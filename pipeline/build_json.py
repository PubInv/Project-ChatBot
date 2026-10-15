#!/usr/bin/env python3
"""Generate data/projects.json and data/skills.json for the chatbot.

Reads the project workbook, checks each GitHub link's activity, pulls the
README or idea file, and writes enriched JSON. Runs in GitHub Actions.
"""
import json

from enrich import enrich_row, load_aliases
from github_client import GitHubClient
from project_links import enrich_project_row, parse_github_link
from ranking import is_eligible, status_rank
from workbook_reader import DEFAULT_SHEETS, DEFAULT_XLSX, REPO_ROOT, read_project_rows

PROJECTS_OUT = REPO_ROOT / "data" / "projects.json"
SKILLS_OUT = REPO_ROOT / "data" / "skills.json"
SITE_PAGES = REPO_ROOT / "data" / "site_pages.json"


def unique_rows(rows: list[dict]) -> list[dict]:
    """Keep one row per project (same name or same link); the Projects tab wins over Shortlist."""
    rows = sorted(rows, key=lambda r: (r["_sheet"] != "Projects", r["_row"]))
    seen, unique = set(), []
    for row in rows:
        keys = {row["project"].strip().lower()}
        if row.get("link"):
            keys.add(row["link"].strip().lower())
        if not keys & seen:
            unique.append(row)
        seen |= keys
    return unique


def main() -> None:
    rows = unique_rows(read_project_rows(DEFAULT_XLSX, sheets=DEFAULT_SHEETS))
    print(f"Read {len(rows)} unique projects from {DEFAULT_XLSX.name}.")

    github = GitHubClient()
    aliases = load_aliases()
    pages = {k: v for k, v in json.loads(SITE_PAGES.read_text()).items() if not k.startswith("_")}
    cache = {}
    projects = []
    for idx, row in enumerate(rows, 1):
        row = enrich_project_row(row, github, cache)
        parsed = parse_github_link(row.get("link") or "")
        text = github.description_text(parsed["owner"], parsed["repo"], parsed["path"], parsed["ref"]) if parsed else ""
        record = enrich_row(row, text, aliases)
        record["eligible"] = is_eligible(record)
        record["status_rank"] = status_rank(record["status"])
        record["page"] = pages.get(record["project"], "")
        projects.append(record)
        print(f"[{idx}/{len(rows)}] {row['project'][:58]:58} {row['activity_status']:8} "
              f"{len(projects[-1]['skills'])} skills")

    # Same guard as the workbook refresh: an all-Unknown run means GitHub failed.
    linked = [p for p in projects if "github.com" in p["link"]]
    if linked and all(p["activity_status"] == "Unknown" for p in linked):
        raise SystemExit(f"ERROR: all {len(linked)} GitHub-linked projects are Unknown. Refusing to overwrite JSON.")

    PROJECTS_OUT.parent.mkdir(exist_ok=True)
    PROJECTS_OUT.write_text(json.dumps(projects, indent=2, ensure_ascii=False) + "\n")
    skills = sorted({s for p in projects for s in p["skills"] + p["readme_skills"]})
    SKILLS_OUT.write_text(json.dumps({"skills": skills}, indent=2) + "\n")

    with_skills = sum(1 for p in projects if p["skills"] or p["readme_skills"])
    eligible = sum(1 for p in projects if p["eligible"])
    seeking = sum(1 for p in projects if p["seeking_volunteers"] != "unknown")
    print(f"Wrote {len(projects)} projects ({with_skills} with skills, {eligible} recommendable) and {len(skills)} skills.")
    missing = sorted(set(pages) - {p["project"] for p in projects})
    if missing:
        print(f"WARNING: data/site_pages.json names projects not in the workbook: {missing}")
    print(f"Seeking Volunteers is filled in for {seeking} of {len(projects)} projects (issue #4).")


if __name__ == "__main__":
    main()
