import json
import unittest
from pathlib import Path

from xyra_logic.learn_validation import (
    LogicLearnValidationError,
    validate_learning_packet,
)

ROOT = Path(__file__).resolve().parents[1]


class TestLogicLearn001(unittest.TestCase):
    def load_fixture(self):
        return json.loads(
            (ROOT / "fixtures" / "logic_learn_001_student001_four_book.json")
            .read_text(encoding="utf-8")
        )

    def test_historical_four_book_case_passes_with_findings(self):
        result = validate_learning_packet(self.load_fixture())
        self.assertEqual(result["status"], "PASS_WITH_FINDINGS")
        self.assertTrue(result["logic_findings"]["missing_explicit_premises"])
        self.assertTrue(result["logic_findings"]["missing_disconfirming_evidence"])
        self.assertFalse(result["logic_findings"]["fact_inference_contradiction"])
        self.assertFalse(result["formal_qualification"])
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])

    def test_fact_inference_collapse_fails(self):
        req = self.load_fixture()
        req["not_established"].append("infrastructure work exists")
        result = validate_learning_packet(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["fact_inference_contradiction"])

    def test_single_hypothesis_fails(self):
        req = self.load_fixture()
        req["competing_hypotheses"] = ["deliberate concealed capability preparation"]
        self.assertEqual(validate_learning_packet(req)["status"], "FAIL")

    def test_unknown_schema_fails_closed(self):
        req = self.load_fixture()
        req["schema_version"] = "UNKNOWN"
        with self.assertRaises(LogicLearnValidationError):
            validate_learning_packet(req)


if __name__ == "__main__":
    unittest.main()
