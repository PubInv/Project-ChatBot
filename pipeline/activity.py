"""Activity status policy for project links."""
from datetime import datetime, timezone

# A project is considered active if its last commit is within about 6 months.
ACTIVE_DAYS = 182

# A project is considered stale from 6-12 months, then dormant after 12 months.
STALE_DAYS = 365


def classify_activity(timestamp: str) -> str:
    """Convert a GitHub timestamp into Active/Stale/Dormant/Unknown."""
    # No timestamp means the script could not determine activity.
    if not timestamp:
        return "Unknown"

    # GitHub API timestamps use UTC ISO format like 2026-05-27T00:39:03Z.
    try:
        last_commit = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return "Unknown"

    # Compare the commit date to now in UTC so timezone differences do not matter.
    age_days = (datetime.now(timezone.utc) - last_commit).days

    # Fresh projects are actively maintained.
    if age_days <= ACTIVE_DAYS:
        return "Active"

    # Older-but-not-abandoned projects are stale.
    if age_days <= STALE_DAYS:
        return "Stale"

    # Anything older than one year is dormant.
    return "Dormant"


def format_commit_month(timestamp: str) -> str:
    """Convert a GitHub timestamp into a workbook-friendly Month Year label."""
    if not timestamp:
        return ""

    try:
        last_commit = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return ""

    return last_commit.strftime("%B %Y")
