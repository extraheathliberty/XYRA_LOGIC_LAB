import json
import unittest
from pathlib import Path

from xyra_logic.learn_grounding import verify_source_grounding

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class TestLogicLearn001Grounding(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_student001_four_book_refs_are_grounded(self):
        packet = self.load("logic_learn_001_student001_four_book.json")
        registry = self.load("logic_learn_001_authorized_sources.json")
        result = verify_source_grounding(
            source_refs=packet["source_refs"],
            authorized_sources=registry,
        )
        self.assertTrue(result["grounded"])
        self.assertEqual(result["source_count"], 4)
        self.assertEqual(result["resolved_count"], 4)
        self.assertEqual(result["unknown_refs"], [])
        self.assertEqual(result["unauthorized_refs"], [])
        self.assertFalse(result["content_accuracy_assessed"])
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])

    def test_unknown_source_fails_grounding(self):
        registry = self.load("logic_learn_001_authorized_sources.json")
        result = verify_source_grounding(
            source_refs=["EII-CC-0006", "EII-CC-9999"],
            authorized_sources=registry,
        )
        self.assertFalse(result["grounded"])
        self.assertEqual(result["unknown_refs"], ["EII-CC-9999"])

    def test_unauthorized_source_fails_grounding(self):
        registry = self.load("logic_learn_001_authorized_sources.json")
        registry["EII-CC-0005"] = {
            "title": "Kim",
            "authorized": False,
            "authority_ref": "NOT_AUTHORIZED_FOR_THIS_FIXTURE",
            "artifact_hash": None,
        }
        result = verify_source_grounding(
            source_refs=["EII-CC-0005"],
            authorized_sources=registry,
        )
        self.assertFalse(result["grounded"])
        self.assertEqual(result["unauthorized_refs"], ["EII-CC-0005"])


if __name__ == "__main__":
    unittest.main()
