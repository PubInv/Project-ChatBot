"""Parse project link fields and enrich rows with GitHub metadata."""
import re
from urllib.parse import unquote

from activity import classify_activity, format_commit_month
from github_client import GitHubClient


def enrich_project_row(row: dict, github: GitHubClient, cache: dict) -> dict:
    """Add computed GitHub fields to one workbook row."""
    # Normalize the link cell once so later checks are simple.
    link = (row.get("link") or "").strip()

    # Blank link cells are expected for some projects.
    if not link:
        return with_computed(row, "Unknown", "", "none")

    # Non-GitHub links cannot be checked by this pipeline.
    parsed = parse_github_link(link)
    if not parsed:
        return with_computed(row, "Unknown", "", "non_github")

    # Fetch the latest commit and compute where description text lives.
    last_commit = cached_latest_commit(github, cache, parsed)
    return with_computed(
        row,
        classify_activity(last_commit),
        format_commit_month(last_commit),
        description_source(parsed),
    )


def parse_github_link(link: str) -> dict | None:
    """Parse GitHub repo links and GitHub blob/file links."""
    # Supported shapes:
    #   https://github.com/OWNER/REPO
    #   https://github.com/OWNER/REPO/blob/BRANCH/path/to/file.md
    match = re.search(r"github\.com/([^/]+)/([^/#?]+)(?:/blob/([^/]+)/([^#?]+))?", link)
    if not match:
        return None

    # The branch is not needed because the GitHub commits API path filter works
    # at the repository level; the path is enough for latest file activity.
    return {
        "owner": match.group(1),
        "repo": match.group(2).removesuffix(".git"),
        "ref": match.group(3) or "",
        "path": unquote(match.group(4) or ""),
    }


def cached_latest_commit(github: GitHubClient, cache: dict, parsed: dict) -> str:
    """Use a shared cache so duplicate links do not repeat API calls."""
    key = ("commit", parsed["owner"], parsed["repo"], parsed["ref"], parsed["path"])
    if key not in cache:
        cache[key] = github.latest_commit(
            parsed["owner"],
            parsed["repo"],
            parsed["path"],
            parsed["ref"],
        )
    return cache[key]


def description_source(parsed: dict) -> str:
    """Return the source type for project description text."""
    # A GitHub markdown blob is treated as a project idea file.
    if parsed["path"].lower().endswith(".md"):
        return "idea_file"

    # Plain GitHub repo links conventionally use their README as the description.
    return "readme"


def with_computed(row: dict, activity_status: str, last_commit: str, source: str) -> dict:
    """Return a copy of the row with the three computed workbook fields."""
    return {
        **row,
        "activity_status": activity_status,
        "last_commit": last_commit,
        "description_source": source,
    }
