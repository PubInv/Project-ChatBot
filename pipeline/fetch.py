#!/usr/bin/env python3
"""Refresh computed GitHub columns in the project workbook.

This script is designed to run in GitHub Actions. It only updates the Excel
workbook; it does not parse skills, generate JSON, run the demo page, or
perform project matching.
"""
from github_client import GitHubClient
from project_links import enrich_project_row
from workbook_reader import DEFAULT_SHEETS, DEFAULT_XLSX, read_project_rows
from workbook_writer import write_computed_columns

COMPUTED_COLUMNS = {
    # Excel header -> field name in the enriched row dictionary.
    "Status": "activity_status",
    "Last Commit": "last_commit",
    "Description Source": "description_source",
}


def main() -> None:
    # The Action always refreshes the repo workbook's standard project tabs.
    workbook = DEFAULT_XLSX
    sheets = DEFAULT_SHEETS

    # Read project rows from the workbook before making any network calls.
    records = read_project_rows(workbook, sheets=sheets)
    print(f"Read {len(records)} project rows from {workbook}.")

    # Build the GitHub API client with the Action-provided token.
    github = GitHubClient()

    # Reuse one cache across rows so repeated PubInv/PubInv idea-file links do
    # not call the same GitHub endpoints more than needed.
    enriched = []
    cache = {}
    for idx, record in enumerate(records, 1):
        # Add activity_status, last_commit, and description_source to the row.
        updated = enrich_project_row(record, github, cache)
        enriched.append(updated)

        # Print one line per row so Actions logs show what was computed.
        print(
            f"[{idx}/{len(records)}] {updated['project'][:58]:58} "
            f"{updated['activity_status']:8} "
            f"{updated['last_commit'] or '-':20} "
            f"{updated['description_source']}"
        )

    # Safety guard: if every GitHub row became Unknown, do not overwrite useful
    # workbook data with a failed refresh.
    github_rows = [row for row in enriched if "github.com" in (row.get("link") or "")]
    resolved = [row for row in github_rows if row["activity_status"] != "Unknown"]
    if github_rows and not resolved:
        raise SystemExit(
            f"ERROR: {len(github_rows)} GitHub-linked rows all resolved to Unknown. "
            "Refusing to overwrite workbook data."
        )

    # Write only the computed columns back into the workbook.
    write_computed_columns(workbook, enriched, COMPUTED_COLUMNS)
    print(f"Updated computed columns in {workbook}.")


if __name__ == "__main__":
    # Standard Python entrypoint.
    main()
