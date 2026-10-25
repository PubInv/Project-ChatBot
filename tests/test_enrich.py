import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from build_json import unique_rows  # noqa: E402
from enrich import enrich_row, load_aliases, parse_seeking, split_skills, summarize, to_canonical  # noqa: E402


class SeekingTests(unittest.TestCase):
    def test_maybe_is_not_flattened_to_no(self):
        self.assertEqual(parse_seeking("TRUE"), "yes")
        self.assertEqual(parse_seeking("Maybe, ask Rob"), "maybe")
        self.assertEqual(parse_seeking("FALSE"), "no")
        self.assertEqual(parse_seeking(""), "unknown")


class SkillTests(unittest.TestCase):
    def test_split_drops_prose_and_fixes_spelling(self):
        skills = split_skills("Mechanical engineering, javascript; a fun project. And soldering")
        self.assertIn("Mechanical engineering", skills)
        self.assertIn("soldering", skills)
        self.assertNotIn("a fun project.", skills)

    def test_alias_beats_containment(self):
        aliases = {"computer programming": ["Programming"], "pointless": []}
        self.assertEqual(to_canonical("Computer programming", aliases), ["Programming"])
        self.assertEqual(to_canonical("pointless", aliases), [])

    def test_shipped_aliases_load(self):
        self.assertIn("javascript", load_aliases())


class SummaryTests(unittest.TestCase):
    def test_skips_headings_code_and_short_lines(self):
        text = "# Title\n\n```py\nx = 1\n```\nShort.\nThis project builds a low-cost ventilator for clinics that lack one."
        self.assertEqual(summarize(text), "This project builds a low-cost ventilator for clinics that lack one.")


class RecordTests(unittest.TestCase):
    def test_readme_skills_merge_with_sheet_skills(self):
        row = {"project": "Mower", "skills_raw": "machining", "seeking_volunteers": "TRUE",
               "joinability": "1", "difficulty": "6", "priority": "2"}
        record = enrich_row(row, "Use an arduino to slow the motor.", {})
        self.assertEqual(record["skills"], ["Machining"])
        self.assertIn("Arduino", record["readme_skills"])
        self.assertEqual(record["seeking_volunteers"], "yes")
        self.assertEqual((record["joinability"], record["difficulty"], record["priority"]), (1.0, 6.0, 2.0))

    def test_same_link_under_two_names_is_one_project(self):
        rows = [{"_sheet": "Projects", "_row": 3, "project": "Krake", "link": "https://x/60.md"},
                {"_sheet": "Projects", "_row": 4, "project": "Alarm Device", "link": "https://x/60.md"}]
        self.assertEqual([r["project"] for r in unique_rows(rows)], ["Krake"])

    def test_projects_tab_wins_duplicates(self):
        rows = [{"_sheet": "Shortlist", "_row": 2, "project": "A"},
                {"_sheet": "Projects", "_row": 9, "project": "a "}]
        self.assertEqual([r["_sheet"] for r in unique_rows(rows)], ["Projects"])


if __name__ == "__main__":
    unittest.main()
