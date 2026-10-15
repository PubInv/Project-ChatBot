"""Turn workbook rows plus README text into the UI-facing project records.

Pure functions with no network calls, so they can be unit-tested directly.
"""
import json
import re
from pathlib import Path

from skill_rules import ALL_CANONICAL, SKILL_KEYWORDS

REPO_ROOT = Path(__file__).resolve().parent.parent
ALIASES_JSON = REPO_ROOT / "data" / "skill_aliases.json"

# Fragments of prose that the skills column sometimes contains.
BAD_FRAGMENTS = {
    "a fun", "a challenging", "or poetry", "pretty well developed idea",
    "very preliminary set of ideas", "currently underway", "self-contained",
}


def parse_num(value: str, fallback: float) -> float:
    """Read the first number in a cell like '2 (needs mentor)'."""
    match = re.search(r"\d+(\.\d+)?", value or "")
    return float(match.group(0)) if match else fallback


def parse_seeking(value: str) -> str:
    """Normalize Seeking cells to yes / maybe / no / unknown; never flatten maybe to no."""
    normalized = (value or "").strip().upper()
    if normalized == "TRUE":
        return "yes"
    if normalized.startswith("MAYBE"):
        return "maybe"
    if normalized == "FALSE":
        return "no"
    return "unknown"


def canonical_spelling(skill: str) -> str:
    """Fix common spelling variants before alias lookup."""
    s = re.sub(r"\s+", " ", skill.strip())
    fixes = {"3d": "3D", "js": "JavaScript", "ux": "UX", "ui": "UI",
             "micro-electronics": "Microelectronics", "microelctronics": "Microelectronics"}
    if s.lower() in fixes:
        return fixes[s.lower()]
    for wrong, right in (("3d ", "3D "), (" 3d", " 3D"), ("Javascript", "JavaScript"),
                         ("Javscript", "JavaScript"), ("micro-electronics", "Microelectronics")):
        s = s.replace(wrong, right)
    return s.strip(" .")


def split_skills(text: str) -> list[str]:
    """Split the free-text skills cell into short skill phrases."""
    if not text:
        return []
    protected = re.sub(r"\(([^)]*)\)", lambda m: f"({m.group(1).replace('/', ' / ')})", text)
    parts = re.split(r"\s*,\s*|\s*;\s*|\s*\|\s*|\s+and\s+|\s*&\s*", protected, flags=re.I)
    skills = set()
    for part in parts:
        part = canonical_spelling(re.sub(r"^[\-•\.\s]+", "", part))
        low = part.lower()
        if not part or low in BAD_FRAGMENTS:
            continue
        # Drop half-split parentheticals, sentences and long prose.
        if re.match(r"^[A-Za-z]\)$", part) or re.match(r"^.*\([A-Za-z]$", part):
            continue
        if re.search(r"[.!?]", part) or len(part.split()) > 5:
            continue
        if any(x in low for x in ("you ", "project", "self-contained", "currently underway")):
            continue
        skills.add(part)
    return sorted(skills)


def load_aliases(path: Path = ALIASES_JSON) -> dict[str, list[str]]:
    """Raw lowercase skill string -> canonical skills; [] means drop it."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    return {k.lower(): v for k, v in raw.items() if not k.startswith("_")}


def to_canonical(raw_skill: str, aliases: dict) -> list[str]:
    """Map one raw skill to canonical skills: alias, exact match, then containment."""
    key = raw_skill.lower().strip()
    if key in aliases:
        return aliases[key]
    for canonical in sorted(ALL_CANONICAL):
        if key == canonical.lower():
            return [canonical]
    for canonical in sorted(ALL_CANONICAL):
        if canonical.lower() in key or key in canonical.lower():
            return [canonical]
    return []


def readme_skills(text: str) -> list[str]:
    """Canonical skills whose keywords appear in README or idea-file text."""
    low = (text or "").lower()
    return sorted(skill for skill, keywords in SKILL_KEYWORDS.items() if any(k in low for k in keywords))


def summarize(text: str, max_sentences: int = 3, min_len: int = 40) -> str:
    """First few real sentences of a markdown document."""
    if not text:
        return ""
    for pattern, repl in ((r"```.*?```", " "), (r"`[^`]*`", " "), (r"!\[[^\]]*\]\([^)]+\)", " "),
                          (r"\[([^\]]+)\]\([^)]+\)", r"\1"), (r"<[^>]+>", " "), (r"https?://\S+", "")):
        text = re.sub(pattern, repl, text, flags=re.DOTALL)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*+|_{1,2}", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    good = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        sentence = sentence.strip()
        if len(sentence) < min_len:
            continue
        if re.match(r"^(TODO|Note|See also|References|License|Usage|Install)", sentence, re.I):
            continue
        if re.match(r"^[A-Z][a-z]+:", sentence):  # "Status: active" style lines
            continue
        good.append(sentence)
        if len(good) >= max_sentences:
            break
    return " ".join(good)


def enrich_row(row: dict, readme_text: str, aliases: dict) -> dict:
    """Build one projects.json record from a workbook row and its README text."""
    # Sheet skills are human-entered; README keywords are noisier, so they are kept apart.
    canonical = sorted({c for skill in split_skills(row.get("skills_raw", "")) for c in to_canonical(skill, aliases)})
    inferred = [c for c in readme_skills(readme_text) if c in ALL_CANONICAL and c not in canonical]

    return {
        "project": row["project"],
        "status": row.get("status", ""),
        "synopsis": row.get("synopsis", ""),
        "summary": summarize(readme_text) or row.get("synopsis", ""),
        "link": row.get("link", ""),
        "category": row.get("category", ""),
        "priority": parse_num(row.get("priority", ""), 0.0) or None,
        "joinability": parse_num(row.get("joinability", ""), 2.0),
        "difficulty": parse_num(row.get("difficulty", ""), 5.0),
        "seeking_volunteers": parse_seeking(row.get("seeking_volunteers", "")),
        "seeking_mentors": parse_seeking(row.get("seeking_mentors", "")),
        "skills_raw": row.get("skills_raw", ""),
        "skills": canonical,
        "readme_skills": inferred,
        "activity_status": row.get("activity_status", "Unknown"),
        "last_commit": row.get("last_commit", ""),
        "description_source": row.get("description_source", "none"),
    }
