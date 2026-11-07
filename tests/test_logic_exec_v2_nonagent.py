"""Non-agent Executive logic regression: real XYRA_LOGIC_STANDARD-001/v1 API.

No LLM, runtime, credentials, network, institutional vote or admission.
Known missing semantic checks are recorded as expected failures, NOT passes.
Run: PYTHONPATH=src python -m unittest tests.test_logic_exec_v2_nonagent -v
"""
import copy
import unittest

from xyra_logic.standard import assess_standard_conformance


def packet():
    return {
        "status": "PASS",
        "normalized_proposition": {
            "source_proposition": "Evaluate bounded internal pilot now",
            "scope": "bounded", "environment": "internal",
        },
        "criterion_analysis": {
            "decision_threshold": "bounded internal pilot",
            "relevant_criteria": ["pilot evidence"],
            "excluded_criteria": ["production admission"],
            "downstream_criteria": ["production admission"],
        },
        "evidence_classification": [],
        "expected_vote": "YES",
        "proposed_vote": "YES",
        "vote_consistency": "CONSISTENT",
        "authority_ceiling": "DELIBERATIVE_ONLY",
        "institutional_decision": False,
        "authority_expansion": False,
        "production_admission": False,
    }


class ExecutiveLogicNonAgentRegression(unittest.TestCase):
    def assess(self, value):
        return assess_standard_conformance(
            profile="EXECUTIVE_DECISION", domain_result=value
        )

    def test_valid_bounded_packet_passes_standard(self):
        result = self.assess(packet())
        self.assertEqual(result["standard_status"], "PASS")
        self.assertIs(result["institutional_decision"], False)
        self.assertIs(result["authority_expansion"], False)
        self.assertIs(result["production_admission"], False)

    def test_institutional_decision_true_rejected(self):
        value = packet()
        value["institutional_decision"] = True
        result = self.assess(value)
        self.assertEqual(result["standard_status"], "FAIL")
        self.assertIn("institutional_decision_not_false", result["findings"])

    def test_authority_expansion_true_rejected(self):
        value = packet()
        value["authority_expansion"] = True
        result = self.assess(value)
        self.assertEqual(result["standard_status"], "FAIL")
        self.assertIn("authority_expansion_not_false", result["findings"])

    def test_inconsistent_domain_failure_preserved(self):
        value = packet()
        value["status"] = "FAIL"
        value["vote_consistency"] = "INCONSISTENT"
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")

    def test_missing_structure_rejected(self):
        value = packet()
        del value["criterion_analysis"]
        result = self.assess(value)
        self.assertEqual(result["standard_status"], "FAIL")
        self.assertIn("missing_criterion_analysis", result["findings"])

    @unittest.expectedFailure
    def test_production_admission_true_must_be_rejected(self):
        # Current v1 returns output production_admission=False but does not
        # inspect input production_admission=True; masking is not validation.
        value = packet()
        value["production_admission"] = True
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")

    @unittest.expectedFailure
    def test_relevant_excluded_overlap_must_be_rejected(self):
        value = packet()
        value["criterion_analysis"]["relevant_criteria"].append(
            "production admission"
        )
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")

    @unittest.expectedFailure
    def test_deferred_production_threshold_must_be_rejected(self):
        value = packet()
        value["criterion_analysis"]["decision_threshold"] = (
            "production admission"
        )
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")

    @unittest.expectedFailure
    def test_bounded_source_upgraded_to_production_must_be_rejected(self):
        value = packet()
        value["normalized_proposition"]["environment"] = "production"
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")

    @unittest.expectedFailure
    def test_vote_mismatch_must_be_rejected_despite_consistency_claim(self):
        value = packet()
        value["proposed_vote"] = "NO"
        self.assertEqual(self.assess(value)["standard_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
