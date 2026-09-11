import unittest

from xyra_logic import (
    And,
    Atom,
    Implies,
    RuleApplicationResult,
    validate_rule_application,
)


class LogicFndRules001Tests(unittest.TestCase):

    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")
        self.R = Atom("R")

    def test_modus_ponens_valid(self):
        result = validate_rule_application(
            "PROP-MP-001",
            [self.P, Implies(self.P, self.Q)],
            self.Q,
        )

        self.assertIsInstance(result, RuleApplicationResult)
        self.assertEqual(result.status, "VALID_STEP")
        self.assertEqual(result.rule_id, "PROP-MP-001")
        self.assertEqual(result.rule_name, "MODUS_PONENS")
        self.assertEqual(result.derived_output, self.Q)
        self.assertIsNone(result.failure_reason)

    def test_modus_ponens_affirming_consequent_rejected(self):
        result = validate_rule_application(
            "PROP-MP-001",
            [Implies(self.P, self.Q), self.Q],
            self.P,
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "RULE_INPUT_MISMATCH")

    def test_modus_ponens_wrong_output_rejected(self):
        result = validate_rule_application(
            "PROP-MP-001",
            [self.P, Implies(self.P, self.Q)],
            self.R,
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "OUTPUT_PATTERN_MISMATCH")

    def test_modus_ponens_missing_input_rejected(self):
        result = validate_rule_application(
            "PROP-MP-001",
            [self.P],
            self.Q,
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "MISSING_REQUIRED_INPUT")

    def test_conjunction_introduction_valid(self):
        expected = And(self.P, self.Q)

        result = validate_rule_application(
            "PROP-AND-I-001",
            [self.P, self.Q],
            expected,
        )

        self.assertEqual(result.status, "VALID_STEP")
        self.assertEqual(result.rule_id, "PROP-AND-I-001")
        self.assertEqual(result.rule_name, "CONJUNCTION_INTRODUCTION")
        self.assertEqual(result.derived_output, expected)
        self.assertIsNone(result.failure_reason)

    def test_conjunction_introduction_reordered_output_rejected(self):
        result = validate_rule_application(
            "PROP-AND-I-001",
            [self.P, self.Q],
            And(self.Q, self.P),
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "OUTPUT_PATTERN_MISMATCH")

    def test_conjunction_elimination_left_valid(self):
        result = validate_rule_application(
            "PROP-AND-E-L-001",
            [And(self.P, self.Q)],
            self.P,
        )

        self.assertEqual(result.status, "VALID_STEP")
        self.assertEqual(result.rule_name, "CONJUNCTION_ELIMINATION_LEFT")
        self.assertEqual(result.derived_output, self.P)

    def test_conjunction_elimination_right_valid(self):
        result = validate_rule_application(
            "PROP-AND-E-R-001",
            [And(self.P, self.Q)],
            self.Q,
        )

        self.assertEqual(result.status, "VALID_STEP")
        self.assertEqual(result.rule_name, "CONJUNCTION_ELIMINATION_RIGHT")
        self.assertEqual(result.derived_output, self.Q)

    def test_unknown_rule_rejected(self):
        result = validate_rule_application(
            "PROP-NOT-A-RULE",
            [self.P],
            self.P,
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertIsNone(result.derived_output)
        self.assertEqual(result.failure_reason, "UNKNOWN_RULE")

    def test_extra_inputs_rejected(self):
        result = validate_rule_application(
            "PROP-AND-E-L-001",
            [And(self.P, self.Q), self.R],
            self.P,
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "INPUT_ARITY_MISMATCH")

    def test_malformed_expression_rejected(self):
        result = validate_rule_application(
            "PROP-AND-I-001",
            [self.P, "not-an-expression"],
            And(self.P, self.Q),
        )

        self.assertEqual(result.status, "INVALID_STEP")
        self.assertEqual(result.failure_reason, "MALFORMED_EXPRESSION")

    def test_repeated_application_is_identical(self):
        args = (
            "PROP-MP-001",
            [self.P, Implies(self.P, self.Q)],
            self.Q,
        )

        first = validate_rule_application(*args)
        second = validate_rule_application(*args)
        third = validate_rule_application(*args)

        self.assertEqual(first, second)
        self.assertEqual(second, third)


if __name__ == "__main__":
    unittest.main(verbosity=2)
