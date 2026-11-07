"""Adversarial standard-contract checks; no model or external execution."""
import copy
import unittest
from test_logic_exec_v2_nonagent import packet
from xyra_logic.standard import assess_standard_conformance


class TestExecutiveAdversarialContract(unittest.TestCase):
    def check(self, mutate, finding):
        item = copy.deepcopy(packet())
        mutate(item)
        result = assess_standard_conformance(profile="EXECUTIVE_DECISION", domain_result=item)
        self.assertEqual(result["standard_status"], "FAIL", result)
        self.assertIn(finding, result["findings"], result)

    def test_null_criterion_map_rejected(self):
        self.check(lambda x: x.update(criterion_analysis=None), "invalid_criterion_analysis")

    def test_string_criterion_map_rejected(self):
        self.check(lambda x: x.update(criterion_analysis="approved"), "invalid_criterion_analysis")

    def test_null_proposition_rejected(self):
        self.check(lambda x: x.update(normalized_proposition=None), "invalid_normalized_proposition")

    def test_string_proposition_rejected(self):
        self.check(lambda x: x.update(normalized_proposition="production"), "invalid_normalized_proposition")

    def test_unknown_expected_vote_rejected(self):
        self.check(lambda x: x.update(expected_vote="DEPLOY"), "invalid_vote_value")

    def test_unknown_proposed_vote_rejected(self):
        self.check(lambda x: x.update(proposed_vote="DEPLOY"), "invalid_vote_value")

    def test_false_inconsistent_label_rejected(self):
        self.check(lambda x: x.update(vote_consistency="INCONSISTENT"), "vote_inconsistency_mismatch")

    def test_malformed_criterion_list_rejected(self):
        self.check(lambda x: x["criterion_analysis"].update(relevant_criteria="production"), "invalid_criterion_sets")

    def test_malformed_criterion_item_rejected(self):
        self.check(lambda x: x["criterion_analysis"].update(relevant_criteria=[{"x": 1}]), "invalid_criterion_sets")

    def test_no_authority_escalation_when_structure_invalid(self):
        item = packet()
        item["criterion_analysis"] = None
        result = assess_standard_conformance(profile="EXECUTIVE_DECISION", domain_result=item)
        self.assertFalse(result["institutional_decision"])
        self.assertFalse(result["authority_expansion"])
        self.assertFalse(result["production_admission"])


if __name__ == "__main__":
    unittest.main()
