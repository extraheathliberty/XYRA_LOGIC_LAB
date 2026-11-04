import json
import unittest
from pathlib import Path

from xyra_logic.learn_validation import validate_learning_packet
from xyra_logic.standard import (
    LogicStandardValidationError,
    assess_standard_conformance,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class TestXyraLogicStandard001(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def executive_result(self, status="PASS", vote_consistency="CONSISTENT"):
        return {
            "status": status,
            "normalized_proposition": {"source_proposition": "bounded test"},
            "criterion_analysis": {"decision_threshold": "current criterion"},
            "evidence_classification": [],
            "expected_vote": "YES",
            "proposed_vote": "YES" if vote_consistency == "CONSISTENT" else "NO",
            "vote_consistency": vote_consistency,
            "authority_ceiling": "DELIBERATIVE_ONLY",
            "institutional_decision": False,
            "authority_expansion": False,
        }

    def test_std_t1_executive_good_passes(self):
        result = assess_standard_conformance(
            profile="EXECUTIVE_DECISION",
            domain_result=self.executive_result(),
        )
        self.assertEqual(result["standard_status"], "PASS")
        self.assertFalse(result["production_admission"])

    def test_std_t2_executive_failure_remains_fail(self):
        result = assess_standard_conformance(
            profile="EXECUTIVE_DECISION",
            domain_result=self.executive_result(
                status="FAIL",
                vote_consistency="INCONSISTENT",
            ),
        )
        self.assertEqual(result["standard_status"], "FAIL")

    def test_std_t3_learning_good_passes(self):
        domain = validate_learning_packet(self.load("logic_learn_001_good.json"))
        result = assess_standard_conformance(
            profile="LEARNING_EVALUATION",
            domain_result=domain,
        )
        self.assertEqual(domain["status"], "PASS")
        self.assertEqual(result["standard_status"], "PASS")

    def test_std_t4_preserved_learning_failure_is_rejected(self):
        domain = validate_learning_packet(
            self.load("logic_learn_001_student001_blind_runtime.json")
        )
        result = assess_standard_conformance(
            profile="LEARNING_EVALUATION",
            domain_result=domain,
        )
        self.assertEqual(domain["status"], "FAIL")
        self.assertEqual(result["standard_status"], "FAIL")

    def test_std_t5_unknown_profile_fails_closed(self):
        with self.assertRaises(LogicStandardValidationError):
            assess_standard_conformance(
                profile="UNKNOWN",
                domain_result=self.executive_result(),
            )

    def test_std_t6_authority_boundary_fails(self):
        domain = self.executive_result()
        domain["institutional_decision"] = True
        result = assess_standard_conformance(
            profile="EXECUTIVE_DECISION",
            domain_result=domain,
        )
        self.assertEqual(result["standard_status"], "FAIL")
        self.assertIn("institutional_decision_not_false", result["findings"])
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])
        self.assertFalse(result["production_admission"])


if __name__ == "__main__":
    unittest.main()
