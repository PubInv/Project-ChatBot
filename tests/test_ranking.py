import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))

from ranking import is_eligible, recommend  # noqa: E402

CASES = json.loads((ROOT / "tests" / "ranking_cases.json").read_text())


class RankingTests(unittest.TestCase):
    def test_shared_cases(self):
        for case in CASES["cases"]:
            with self.subTest(case["name"]):
                got = recommend(CASES["projects"], case["have"], case["want"], case["category"])
                self.assertEqual([p["project"] for p in got], case["expected"])

    def test_robert_exclusions(self):
        self.assertFalse(is_eligible({"project": "Project #82: Librecorder", "status": "Highly Active"}))
        self.assertFalse(is_eligible({"project": "Project #9: X", "status": "Preliminary"}))
        self.assertTrue(is_eligible({"project": "Project #9: X", "status": "Ready-to-start"}))

    def test_real_data_respects_the_rules(self):
        projects = json.loads((ROOT / "data" / "projects.json").read_text())
        shown = recommend(projects, limit=len(projects))
        self.assertTrue(shown)
        self.assertFalse([p for p in shown if p["status"] == "Preliminary"])
        ranks = [p["status_rank"] for p in shown]
        self.assertEqual(ranks, sorted(ranks))  # never Ready-to-start before Highly Active


if __name__ == "__main__":
    unittest.main()
