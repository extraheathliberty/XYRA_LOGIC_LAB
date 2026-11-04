import json
import unittest
from pathlib import Path

from xyra_logic.learn_content import (
    assess_learning_qualification_readiness,
    verify_source_propositions,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"


class TestLogicLearn001Content(unittest.TestCase):
    def registry(self):
        return json.loads(
            (FIXTURES / "logic_learn_001_proposition_registry.json")
            .read_text(encoding="utf-8")
        )

    def test_cross_book_proposition_set_passes(self):
        result = verify_source_propositions(
            claims=[
                {"proposition_id":"B1-P11","modality":"assertive"},
                {"proposition_id":"SUNZI-P02","modality":"assertive"},
                {"proposition_id":"CLAUSEWITZ-P04","modality":"assertive"},
                {"proposition_id":"THUCYDIDES-P01","modality":"assertive"},
            ],
            proposition_registry=self.registry(),
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["resolved_count"], 4)
        self.assertFalse(result["semantic_equivalence_assessed"])

    def test_book1_modality_inflation_is_rejected(self):
        result = verify_source_propositions(
            claims=[
                {"proposition_id":"B1-TENTATIVE-QUAY","modality":"assertive"},
            ],
            proposition_registry=self.registry(),
        )
        self.assertFalse(result["passed"])
        self.assertEqual(
            result["source_modality_inflation"],
            ["B1-TENTATIVE-QUAY"],
        )

    def test_readiness_requires_all_gates(self):
        ready = assess_learning_qualification_readiness(
            source_grounding_pass=True,
            content_fidelity_pass=True,
            validator_blind_benchmark_pass=True,
            learner_blind_delta_pass=True,
            positive_benchmark_pass=True,
            negative_benchmark_rejected=True,
            covered_learning_cases=4,
        )
        self.assertEqual(
            ready["status"],
            "READY_FOR_FORMAL_QUALIFICATION_REVIEW",
        )
        self.assertFalse(ready["formal_qualification_granted"])

    def test_readiness_blocks_missing_coverage(self):
        blocked = assess_learning_qualification_readiness(
            source_grounding_pass=True,
            content_fidelity_pass=True,
            validator_blind_benchmark_pass=True,
            learner_blind_delta_pass=False,
            positive_benchmark_pass=True,
            negative_benchmark_rejected=True,
            covered_learning_cases=4,
        )
        self.assertEqual(blocked["status"], "NOT_READY")
        self.assertIn("learner_blind_delta", blocked["blockers"])


if __name__ == "__main__":
    unittest.main()
