import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "fixtures" / "logic_learn_001_coverage.json"


class TestLogicLearn001Coverage(unittest.TestCase):
    def load(self):
        return json.loads(PATH.read_text(encoding="utf-8"))

    def test_four_distinct_learning_cases_are_preserved(self):
        data = self.load()
        self.assertEqual(len(data["cases"]), 4)
        refs = [case["source_ref"] for case in data["cases"]]
        self.assertEqual(len(set(refs)), 4)
        self.assertTrue(all(case["result"].startswith("PASS") for case in data["cases"]))

    def test_coverage_does_not_claim_blind_or_formal_qualification(self):
        data = self.load()
        self.assertTrue(all(case["formal_blind"] is False for case in data["cases"]))
        self.assertTrue(all(case["formal_qualification"] is False for case in data["cases"]))
        self.assertEqual(data["formal_blind_delta"], "NOT_RUN")
        self.assertEqual(data["learning_delta_status"], "NOT_ESTABLISHABLE_RETROACTIVELY")
        self.assertEqual(data["current_blind_capability_status"], "PENDING_RUNTIME_EXECUTION")
        self.assertEqual(data["formal_qualification"], "NOT_GRANTED")
        self.assertEqual(data["sulm_appointment"], "NOT_AUTHORIZED")


if __name__ == "__main__":
    unittest.main()
