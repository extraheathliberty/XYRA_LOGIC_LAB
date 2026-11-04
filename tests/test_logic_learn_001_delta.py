import unittest

from xyra_logic.learn_delta import assess_learning_delta_evidence


class TestLogicLearn001Delta(unittest.TestCase):
    def test_student001_frozen_but_unrun_baseline_is_not_retroactively_recoverable(self):
        result = assess_learning_delta_evidence(
            baseline_frozen_before_exposure=True,
            baseline_executed_before_exposure=False,
            learning_exposure_occurred=True,
            post_learning_blind_executed=False,
            scoring_dimensions_comparable=True,
        )
        self.assertEqual(
            result["learning_delta_status"],
            "NOT_ESTABLISHABLE_RETROACTIVELY",
        )
        self.assertIn(
            "pre_learning_baseline_not_executed",
            result["learning_delta_blockers"],
        )
        self.assertEqual(
            result["current_capability_status"],
            "PENDING_BLIND_CAPABILITY_TEST",
        )

    def test_future_program_with_real_pre_and_post_runs_can_enter_delta_scoring(self):
        result = assess_learning_delta_evidence(
            baseline_frozen_before_exposure=True,
            baseline_executed_before_exposure=True,
            learning_exposure_occurred=True,
            post_learning_blind_executed=True,
            scoring_dimensions_comparable=True,
        )
        self.assertEqual(
            result["learning_delta_status"],
            "ELIGIBLE_FOR_DELTA_SCORING",
        )
        self.assertEqual(result["learning_delta_blockers"], [])
        self.assertFalse(result["formal_qualification_granted"])


if __name__ == "__main__":
    unittest.main()
