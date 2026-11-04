import json
import unittest
from pathlib import Path

from xyra_logic.learn_validation import validate_learning_packet

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class TestLogicStandard001LearningRemediation(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_preserved_student001_blind_failure_is_rejected_generically(self):
        result = validate_learning_packet(
            self.load("logic_learn_001_student001_blind_runtime.json")
        )
        self.assertEqual(result["status"], "FAIL")
        findings = result["logic_findings"]
        self.assertTrue(
            findings["hypothesis_duplication"]
            or findings["unsupported_premise"]
            or findings["ungrounded_disconfirming_evidence"]
            or findings["unsupported_conclusion"]
        )

    def test_known_good_benchmark_still_passes(self):
        result = validate_learning_packet(self.load("logic_learn_001_good.json"))
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(any(result["logic_findings"].values()))

    def test_historical_four_book_record_stays_pass_with_findings(self):
        result = validate_learning_packet(
            self.load("logic_learn_001_student001_four_book.json")
        )
        self.assertEqual(result["status"], "PASS_WITH_FINDINGS")
        self.assertTrue(result["logic_findings"]["missing_explicit_premises"])
        self.assertTrue(result["logic_findings"]["missing_disconfirming_evidence"])
        self.assertFalse(result["logic_findings"]["unsupported_conclusion"])


if __name__ == "__main__":
    unittest.main()
