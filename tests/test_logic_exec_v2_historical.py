"""LOGIC-EXEC-V2: historical Executive failures and adversarial criterion fidelity.

This suite replays preserved LOGAI-1.2 artifacts through the actual runtime
validator. Later LOGAI-1.5 records are run-lineage assertions, not invented
verbatim ballot fixtures. No model calls, votes, or runtime admission.
"""
import copy
import json
import unittest
from pathlib import Path

from xyra_logic import validate_exec_deliberation, validate_runtime_deliberation
from test_logic_exec_001 import base_request
from test_logai_1_2_all8_regression import PROPOSITION, EVIDENCE

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "logai_1_2"

HISTORICAL_RUNS = {
    "42040644537": {"valid_votes": 0, "failed_at": "AIR_001"},
    "42043815104": {"valid_votes": 3, "failed_at": "AIR_004"},
    "6aa44d6": {
        "accepted": ["AIR_002", "AIR_003", "AIR_004", "AIR_005"],
        "rejected": ["AIR_001", "AIR_006", "AIR_007", "AIR_008"],
        "classification": "4B_DIAGNOSTIC_NOT_INSTITUTIONAL_VOTE",
    },
}


class TestExecutiveHistoricalLineage(unittest.TestCase):
    def test_all_eight_preserved_artifacts_still_rejected(self):
        for number in range(1, 9):
            runtime = f"AIR_{number:03d}"
            with self.subTest(runtime=runtime):
                artifact = json.loads(
                    (FIXTURES / f"{runtime.lower()}.json").read_text(encoding="utf-8")
                )
                self.assertEqual(artifact["runtime_service"], runtime)
                self.assertEqual(artifact["source_qualification"], "ALL8-PROPOSITION-FIDELITY-002")
                result = validate_runtime_deliberation(
                    runtime_artifact=artifact,
                    proposition=PROPOSITION,
                    evidence=EVIDENCE,
                    validation_id=f"V2-REPLAY-{runtime}",
                    authority_ceiling="DELIBERATIVE_VOTE_ONLY / NON_PRODUCTION",
                    correlation_id=f"V2-REPLAY-{runtime}",
                )
                self.assertEqual(result["status"], "FAIL")
                self.assertEqual(result["vote_consistency"], "INCONSISTENT")
                self.assertFalse(result["institutional_decision"])
                self.assertFalse(result["authority_expansion"])

    def test_run_lineage_keeps_partial_runs_distinct(self):
        self.assertEqual(HISTORICAL_RUNS["42040644537"]["valid_votes"], 0)
        self.assertEqual(HISTORICAL_RUNS["42043815104"]["valid_votes"], 3)
        self.assertEqual(HISTORICAL_RUNS["42043815104"]["failed_at"], "AIR_004")
        diagnostic = HISTORICAL_RUNS["6aa44d6"]
        self.assertEqual(len(diagnostic["accepted"]), 4)
        self.assertEqual(len(diagnostic["rejected"]), 4)
        self.assertEqual(set(diagnostic["accepted"]) & set(diagnostic["rejected"]), set())
        self.assertEqual(diagnostic["classification"], "4B_DIAGNOSTIC_NOT_INSTITUTIONAL_VOTE")

    def test_production_admission_overlap_fails(self):
        req = base_request()
        req["criterion_analysis"]["relevant_criteria"].append("production readiness")
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["relevant_excluded_conflict"])

    def test_production_threshold_substitution_fails(self):
        req = base_request()
        req["criterion_analysis"]["decision_threshold"] = "production readiness"
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["threshold_conflict"])

    def test_deferred_comparison_overlap_fails(self):
        req = base_request()
        req["criterion_analysis"]["relevant_criteria"].append("8B/14B comparative conclusion")
        req["criterion_analysis"]["excluded_criteria"].append("8B/14B comparative conclusion")
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["relevant_excluded_conflict"])

    def test_deferred_comparison_threshold_fails(self):
        req = base_request()
        req["criterion_analysis"]["downstream_criteria"].append("8B/14B comparative conclusion")
        req["criterion_analysis"]["decision_threshold"] = "8B/14B comparative conclusion"
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["criterion_substitution"])

    def test_proposition_upgrade_fails(self):
        req = base_request()
        req["proposition_decomposition"]["environment"] = "production"
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["scope_expansion"])

    def test_valid_current_criterion_does_not_require_production(self):
        req = base_request()
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["expected_vote"], "YES")
        self.assertFalse(result["institutional_decision"])

    def test_evidence_role_substitution_fails(self):
        req = base_request()
        req["proposed_choice"] = "NO"
        req["proposed_rationale"] = "Production readiness is unresolved."
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["criterion_substitution"])

    def test_contradictory_condition_states_fail(self):
        req = base_request()
        conflict = copy.deepcopy(req["criterion_analysis"]["necessary_conditions"][0])
        conflict["state"] = "NOT_SATISFIED"
        req["criterion_analysis"]["necessary_conditions"].append(conflict)
        result = validate_exec_deliberation(req)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(result["logic_findings"]["contradiction"])


if __name__ == "__main__":
    unittest.main()
