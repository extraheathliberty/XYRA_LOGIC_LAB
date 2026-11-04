import unittest

from xyra_logic import (
    LogicExecValidationError,
    build_runtime_validation_request,
    validate_runtime_deliberation,
)


PROPOSITION = (
    "Should XYRA continue one additional bounded internal qualification cycle "
    "for the current Executive-table system under the existing non-production restrictions?"
)

EVIDENCE = [
    {
        "evidence_id": "FID-4",
        "text": "A containment finding remains unresolved.",
        "target": "downstream",
        "polarity": "blocks",
        "role": "BLOCKS_DOWNSTREAM_ACTION",
    },
    {
        "evidence_id": "FID-5",
        "text": (
            "The current qualification dataset is adequate for another bounded "
            "internal test but insufficient for broad production generalization."
        ),
        "target": "downstream",
        "polarity": "blocks",
        "role": "BLOCKS_DOWNSTREAM_ACTION",
    },
]


class TestLogicExec002RuntimeHandoff(unittest.TestCase):
    def air001_failed_artifact(self):
        return {
            "matter_id": "HOST-FIDELITY-INTERNAL_CYCLE-AIR001",
            "runtime_service": "AIR_001",
            "choice": "NO",
            "rationale": (
                "The proposition requires an internal qualification cycle, but "
                "FID-4 states a containment finding remains unresolved and FID-5 "
                "states the current qualification dataset is insufficient for "
                "broad production generalization. These evidence points indicate "
                "that the system is not production-ready, and the internal cycle "
                "does not resolve the unresolved containment issue. Therefore, "
                "continuing the cycle does not meet the decision threshold for "
                "production-readiness."
            ),
            "evidence_refs": ["FID-4", "FID-5"],
            "proposition_decomposition": {
                "proposition_summary": PROPOSITION,
                "decision_threshold": (
                    "The current evidence does not establish production-readiness "
                    "for the Executive-table system"
                ),
                "relevant_criteria": [
                    "Containment finding unresolved",
                    "Insufficient qualification dataset for production generalization",
                ],
                "excluded_stricter_criteria": [
                    "Production-readiness",
                    "Institutional adoption",
                    "External deployment",
                ],
            },
        }

    def test_actual_failure_pattern_is_rejected_without_inventing_states(self):
        result = validate_runtime_deliberation(
            runtime_artifact=self.air001_failed_artifact(),
            proposition=PROPOSITION,
            evidence=EVIDENCE,
            validation_id="LOGIC-EXEC-002-AIR001-FAIL",
            authority_ceiling="DELIBERATIVE_VOTE_ONLY",
            correlation_id="LOGIC-EXEC-002-CORR-001",
        )
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["proposed_vote"], "NO")
        self.assertEqual(result["expected_vote"], "ABSTAIN")
        self.assertTrue(result["logic_findings"]["unsupported_inference"])
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])

    def test_valid_runtime_packet_passes_with_explicit_current_condition(self):
        artifact = {
            "matter_id": "HOST-FIDELITY-INTERNAL_CYCLE-AIR001-VALID",
            "runtime_service": "AIR_001",
            "choice": "YES",
            "rationale": (
                "The bounded internal cycle remains inside existing non-production "
                "controls and the evidence supports another qualification cycle."
            ),
            "evidence_refs": ["FID-5"],
            "proposition_decomposition": {
                "proposition_summary": PROPOSITION,
                "decision_threshold": (
                    "Evidence supports one additional bounded internal qualification cycle."
                ),
                "relevant_criteria": [
                    "Evidence is adequate for another bounded internal test."
                ],
                "excluded_stricter_criteria": [
                    "Production-readiness",
                    "Institutional adoption",
                ],
            },
        }
        criterion = {
            "decision_threshold": (
                "Evidence supports one additional bounded internal qualification cycle."
            ),
            "necessary_conditions": [
                {
                    "id": "CURRENT-1",
                    "statement": (
                        "The evidence is adequate for another bounded internal test."
                    ),
                    "state": "SATISFIED",
                }
            ],
            "sufficient_conditions": [],
            "blocking_conditions": [],
            "downstream_criteria": ["Production-readiness", "Institutional adoption"],
            "authority_dependencies": [],
            "relevant_criteria": [
                "Evidence is adequate for another bounded internal test."
            ],
            "excluded_criteria": ["Production-readiness", "Institutional adoption"],
            "distinctions": {},
        }
        result = validate_runtime_deliberation(
            runtime_artifact=artifact,
            proposition=PROPOSITION,
            evidence=EVIDENCE,
            criterion_analysis=criterion,
            validation_id="LOGIC-EXEC-002-AIR001-VALID",
            authority_ceiling="DELIBERATIVE_VOTE_ONLY",
        )
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["expected_vote"], "YES")
        self.assertEqual(result["vote_consistency"], "CONSISTENT")

    def test_runtime_evidence_provenance_fails_closed(self):
        artifact = self.air001_failed_artifact()
        artifact["evidence_refs"] = ["FID-4", "MISSING-EVIDENCE"]
        with self.assertRaisesRegex(
            LogicExecValidationError,
            "cites evidence absent from supplied context",
        ):
            build_runtime_validation_request(
                runtime_artifact=artifact,
                proposition=PROPOSITION,
                evidence=EVIDENCE,
                validation_id="LOGIC-EXEC-002-BAD-PROVENANCE",
                authority_ceiling="DELIBERATIVE_VOTE_ONLY",
            )


if __name__ == "__main__":
    unittest.main()
