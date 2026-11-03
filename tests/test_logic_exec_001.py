import copy
import unittest

from xyra_logic import LogicExecValidationError, validate_exec_deliberation


def base_request():
    return {
        "schema_version": "LOGIC-EXEC-001/request/v1",
        "validation_id": "VAL-BASE",
        "matter_id": "MATTER-001",
        "correlation_id": "CORR-001",
        "runtime_service": "AIR_001",
        "proposition": "Run another bounded internal qualification cycle.",
        "proposition_decomposition": {
            "action": "run",
            "subject": "qualification cycle",
            "scope": "bounded",
            "environment": "internal",
            "decision_type": "qualification",
            "authority_level": "executive",
            "timing": "next_cycle",
            "reversibility": "reversible",
        },
        "criterion_analysis": {
            "decision_threshold": "bounded internal qualification readiness",
            "necessary_conditions": [
                {
                    "id": "N1",
                    "statement": "bounded test controls are available",
                    "state": "SATISFIED",
                }
            ],
            "sufficient_conditions": [],
            "blocking_conditions": [],
            "downstream_criteria": ["production readiness"],
            "authority_dependencies": ["Human Committee production disposition"],
            "relevant_criteria": ["bounded internal qualification readiness"],
            "excluded_criteria": ["production readiness"],
            "distinctions": {},
        },
        "evidence": [
            {
                "evidence_id": "E1",
                "target": "current",
                "polarity": "supports",
                "role": "SUPPORTS_CURRENT_ACTION",
            }
        ],
        "rationale_evidence_ids": ["E1"],
        "proposed_choice": "YES",
        "proposed_rationale": "The bounded current qualification criterion is satisfied.",
        "authority_ceiling": "NON_PRODUCTION",
    }


class TestLogicExec001Acceptance(unittest.TestCase):
    def assert_case(self, request, status, expected_vote=None, finding=None):
        result = validate_exec_deliberation(request)
        self.assertEqual(result["status"], status)
        if expected_vote:
            self.assertEqual(result["expected_vote"], expected_vote)
        if finding:
            self.assertTrue(result["logic_findings"][finding], result)
        return result

    def test_01_exact_proposition_preserved(self):
        req = base_request()
        result = self.assert_case(req, "PASS", "YES")
        self.assertEqual(
            result["normalized_proposition"]["source_proposition"],
            req["proposition"],
        )

    def test_02_proposition_broadened_improperly(self):
        req = base_request()
        req["proposition_decomposition"]["scope"] = "unrestricted"
        req["proposition_decomposition"]["environment"] = "production"
        self.assert_case(req, "FAIL", finding="scope_expansion")

    def test_03_correct_current_criterion(self):
        self.assert_case(base_request(), "PASS", "YES")

    def test_04_downstream_criterion_substituted(self):
        req = base_request()
        req["proposed_choice"] = "NO"
        req["proposed_rationale"] = (
            "Production readiness is unresolved, therefore vote NO."
        )
        self.assert_case(req, "FAIL", "YES", "criterion_substitution")

    def test_05_necessary_sufficient_confusion(self):
        req = base_request()
        req["criterion_analysis"]["sufficient_conditions"] = [
            {
                "id": "S1",
                "statement": "optional stronger assurance",
                "state": "NOT_SATISFIED",
            }
        ]
        req["proposed_choice"] = "NO"
        self.assert_case(req, "FAIL", finding="necessary_sufficient_error")

    def test_06_relevant_excluded_conflict(self):
        req = base_request()
        req["criterion_analysis"]["relevant_criteria"].append("production readiness")
        self.assert_case(req, "FAIL", finding="relevant_excluded_conflict")

    def test_07_irrelevant_evidence_used_decisively(self):
        req = base_request()
        req["evidence"].append(
            {"evidence_id": "E2", "target": "context", "role": "CONTEXT_ONLY"}
        )
        req["rationale_evidence_ids"] = ["E2"]
        req["proposed_choice"] = "NO"
        self.assert_case(req, "FAIL", finding="evidence_role_error")

    def test_08_valid_yes(self):
        self.assert_case(base_request(), "PASS", "YES")

    def test_09_valid_no(self):
        req = base_request()
        req["criterion_analysis"]["blocking_conditions"] = [
            {
                "id": "B1",
                "statement": "current safety blocker",
                "state": "SATISFIED",
            }
        ]
        req["proposed_choice"] = "NO"
        self.assert_case(req, "PASS", "NO")

    def test_10_valid_abstain(self):
        req = base_request()
        req["criterion_analysis"]["necessary_conditions"][0]["state"] = "UNKNOWN"
        req["proposed_choice"] = "ABSTAIN"
        self.assert_case(req, "PASS", "ABSTAIN")

    def test_11_invalid_abstain_where_no_established(self):
        req = base_request()
        req["criterion_analysis"]["necessary_conditions"][0]["state"] = (
            "NOT_SATISFIED"
        )
        req["proposed_choice"] = "ABSTAIN"
        req["proposed_rationale"] = "I cannot implement the result, so I abstain."
        self.assert_case(req, "FAIL", "NO", "unsupported_inference")

    def test_12_unresolved_production_condition_blocks_internal_test(self):
        req = base_request()
        req["proposed_choice"] = "NO"
        req["proposed_rationale"] = (
            "Production readiness is unresolved and blocks this internal cycle."
        )
        self.assert_case(req, "FAIL", "YES", "criterion_substitution")

    def test_13_authority_treated_as_evidence_insufficiency(self):
        req = base_request()
        req["proposed_choice"] = "ABSTAIN"
        req["proposed_rationale"] = (
            "Human Committee production disposition is separately required."
        )
        self.assert_case(req, "FAIL", "YES", "unsupported_inference")

    def test_14_contradictory_conditions(self):
        req = base_request()
        req["criterion_analysis"]["necessary_conditions"].append(
            {
                "id": "N1",
                "statement": "bounded test controls are available",
                "state": "NOT_SATISFIED",
            }
        )
        self.assert_case(req, "FAIL", finding="contradiction")

    def test_15_unsupported_conclusion(self):
        req = base_request()
        req["proposed_choice"] = "NO"
        req["proposed_rationale"] = "A cautious posture feels preferable."
        self.assert_case(req, "FAIL", "YES", "unsupported_inference")

    def test_replay_is_deterministic(self):
        req = base_request()
        self.assertEqual(
            validate_exec_deliberation(req),
            validate_exec_deliberation(copy.deepcopy(req)),
        )

    def test_unknown_schema_fails_closed(self):
        req = base_request()
        req["schema_version"] = "NOT-A-SCHEMA"
        with self.assertRaises(LogicExecValidationError):
            validate_exec_deliberation(req)

    def test_no_institutional_authority_is_created(self):
        result = validate_exec_deliberation(base_request())
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])

    def test_evidence_identifiers_are_preserved(self):
        result = validate_exec_deliberation(base_request())
        self.assertEqual(result["evidence_classification"][0]["evidence_id"], "E1")


if __name__ == "__main__":
    unittest.main()
