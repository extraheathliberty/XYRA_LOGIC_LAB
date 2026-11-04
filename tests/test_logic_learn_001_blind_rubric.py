import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUBRIC = ROOT / "fixtures" / "logic_learn_001_student001_blind_rubric.json"


class TestLogicLearn001BlindRubric(unittest.TestCase):
    def load(self):
        return json.loads(RUBRIC.read_text(encoding="utf-8"))

    def test_rubric_is_withheld_and_bounded(self):
        data = self.load()
        self.assertEqual(data["evaluator_visibility"], "WITHHELD_FROM_LEARNER")
        self.assertGreaterEqual(data["minimum_competing_hypotheses"], 3)
        self.assertGreaterEqual(len(data["required_reasoning_features"]), 8)
        self.assertGreaterEqual(len(data["hard_fail_conditions"]), 4)
        self.assertTrue(data["delta_rule"]["baseline_comparison_required"])
        self.assertTrue(data["delta_rule"]["structural_pass_alone_is_not_learning_delta"])
        self.assertFalse(data["authority"]["formal_qualification_granted"])
        self.assertFalse(data["authority"]["sulm_appointment_granted"])
        self.assertFalse(data["authority"]["production_authority"])

    def test_terminal_states_are_bounded(self):
        data = self.load()
        self.assertEqual(
            set(data["acceptable_terminal_states"]),
            {
                "NO SUFFICIENT EVIDENCE OF DECEPTION",
                "UNKNOWN / ACCESS CONSTRAINED",
            },
        )


if __name__ == "__main__":
    unittest.main()
