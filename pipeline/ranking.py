"""Public Invention's recommendation rules, enforced in code instead of a prompt.

The same rules live in chatbot/recommend.js for the browser; tests/ranking_cases.json
keeps the two in step.
"""

# Projects Robert asked never to recommend through the chatbot.
EXCLUDED_TITLES = ("Moonrat", "Oxygen Concentrator", "PolyVent", "ADaM", "Librecorder")

# Lower is shown first; anything unlisted (or blank) goes last.
STATUS_ORDER = {"Highly Active": 1, "Progress but Inactive": 2, "Ready-to-start": 3}
HIDDEN_STATUSES = {"Preliminary"}
MIN_README_MATCHES = 2


def is_eligible(project: dict) -> bool:
    """Whether a project may be recommended at all."""
    title = project.get("project", "").lower()
    if any(name.lower() in title for name in EXCLUDED_TITLES):
        return False
    if project.get("status", "") in HIDDEN_STATUSES:
        return False
    return project.get("seeking_volunteers") != "no"


def status_rank(status: str) -> int:
    return STATUS_ORDER.get(status, len(STATUS_ORDER) + 1)


def recommend(projects: list[dict], have=(), want=(), category: str = "", limit: int = 5) -> list[dict]:
    """Rank eligible projects: status first, then skill matches, then the sheet's Order priority."""
    have = {s.lower() for s in have}
    want = {s.lower() for s in want}
    ranked = []
    for project in projects:
        if not project.get("eligible", is_eligible(project)):
            continue
        if category and project.get("category", "").lower() != category.lower():
            continue
        # Sheet skills decide relevance. README keywords are noisy, so a project with no
        # sheet skills needs two README matches to count.
        sheet = {s.lower() for s in project.get("skills", [])}
        skills = sheet or {s.lower() for s in project.get("readme_skills", [])}
        matches = len(skills & have) + len(skills & want)
        if (have or want) and matches < (1 if sheet else MIN_README_MATCHES):
            continue
        ranked.append((status_rank(project.get("status", "")), -matches, -(project.get("priority") or 0),
                       project["project"], project))
    ranked.sort(key=lambda item: item[:4])
    return [item[-1] for item in ranked[:limit]]
