import json
import unittest
from pathlib import Path

from xyra_logic.learn_validation import validate_learning_packet

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class TestLogicLearn001Benchmarks(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_known_good_passes(self):
        result = validate_learning_packet(self.load("logic_learn_001_good.json"))
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(any(result["logic_findings"].values()))

    def test_known_bad_fails(self):
        result = validate_learning_packet(self.load("logic_learn_001_bad.json"))
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["insufficient_hypothesis_set"])
        self.assertTrue(result["logic_findings"]["missing_source_dependency_analysis"])
        self.assertTrue(result["logic_findings"]["missing_information_gaps"])
        self.assertTrue(result["logic_findings"]["missing_next_collection"])
        self.assertTrue(result["logic_findings"]["missing_explicit_premises"])
        self.assertTrue(result["logic_findings"]["missing_disconfirming_evidence"])
        self.assertTrue(result["logic_findings"]["fact_inference_contradiction"])

    def test_blind_heldout_case_passes(self):
        result = validate_learning_packet(self.load("logic_learn_001_blind.json"))
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(any(result["logic_findings"].values()))
        self.assertFalse(result["formal_qualification"])
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])


if __name__ == "__main__":
    unittest.main()
