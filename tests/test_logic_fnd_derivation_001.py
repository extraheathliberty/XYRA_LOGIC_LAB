import unittest

from xyra_logic import (
    Atom,
    Implies,
    DerivationStep,
    DerivationStepResult,
    replay_derivation_step,
)


class TestLogicFndDerivation001(unittest.TestCase):
    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")

    def test_valid_modus_ponens_replay(self):
        registry = {
            "D1": self.P,
            "D2": Implies(self.P, self.Q),
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertIsInstance(result, DerivationStepResult)
        self.assertEqual(result.status, "VALID_STEP")
        self.assertEqual(result.derived_output, self.Q)
        self.assertIsNone(result.failure_reason)

    def test_result_preserves_step_identity(self):
        registry = {
            "D1": self.P,
            "D2": Implies(self.P, self.Q),
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.step_id, "D3")
        self.assertEqual(result.input_object_ids, ("D1", "D2"))
        self.assertEqual(result.rule_id, "PROP-MP-001")
        self.assertEqual(result.proposed_output, self.Q)

    def test_missing_dependency_fails_closed(self):
        registry = {
            "D1": self.P,
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "MISSING_DEPENDENCY")

    def test_invalid_rule_application_is_preserved(self):
        registry = {
            "D1": Implies(self.P, self.Q),
            "D2": self.Q,
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.P,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "RULE_INPUT_MISMATCH")

    def test_unknown_rule_is_preserved(self):
        registry = {
            "D1": self.P,
        }

        step = DerivationStep(
            step_id="D2",
            input_object_ids=("D1",),
            rule_id="PROP-NOT-A-RULE",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "UNKNOWN_RULE")

    def test_input_order_is_preserved(self):
        registry = {
            "D1": self.P,
            "D2": Implies(self.P, self.Q),
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D2", "D1"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "RULE_INPUT_MISMATCH")

    def test_malformed_resolved_object_is_rejected(self):
        registry = {
            "D1": self.P,
            "D2": "not-an-expression",
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        result = replay_derivation_step(step, registry)

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "MALFORMED_EXPRESSION")

    def test_repeated_replay_is_identical(self):
        registry = {
            "D1": self.P,
            "D2": Implies(self.P, self.Q),
        }

        step = DerivationStep(
            step_id="D3",
            input_object_ids=("D1", "D2"),
            rule_id="PROP-MP-001",
            proposed_output=self.Q,
        )

        first = replay_derivation_step(step, registry)
        second = replay_derivation_step(step, registry)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
