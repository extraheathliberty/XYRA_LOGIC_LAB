import unittest

from xyra_logic import (
    And,
    Atom,
    Biconditional,
    Implies,
    Not,
    Or,
    is_tautology,
    is_valid_argument,
    truth_table,
)


class LogicL0RegressionTests(unittest.TestCase):

    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")
        self.R = Atom("R")

    def test_modus_tollens_valid(self):
        premises = [
            Implies(self.P, self.Q),
            Not(self.Q),
        ]
        self.assertTrue(
            is_valid_argument(premises, Not(self.P))
        )

    def test_denying_antecedent_invalid(self):
        premises = [
            Implies(self.P, self.Q),
            Not(self.P),
        ]
        self.assertFalse(
            is_valid_argument(premises, Not(self.Q))
        )

    def test_chained_inference_valid(self):
        premises = [
            Implies(self.P, self.Q),
            Implies(self.Q, self.R),
            self.P,
        ]
        self.assertTrue(
            is_valid_argument(premises, self.R)
        )

    def test_contradictory_premises_classically_valid(self):
        premises = [
            self.P,
            Not(self.P),
        ]
        self.assertTrue(
            is_valid_argument(premises, self.Q)
        )

    def test_disjunctive_syllogism_valid(self):
        premises = [
            Or(self.P, self.Q),
            Not(self.P),
        ]
        self.assertTrue(
            is_valid_argument(premises, self.Q)
        )

    def test_inclusive_or_does_not_imply_not_q(self):
        premises = [
            Or(self.P, self.Q),
            self.P,
        ]
        self.assertFalse(
            is_valid_argument(premises, Not(self.Q))
        )

    def test_conjunction_elimination_valid(self):
        premises = [
            And(self.P, self.Q),
        ]
        self.assertTrue(
            is_valid_argument(premises, self.P)
        )

    def test_biconditional_elimination_valid(self):
        premises = [
            Biconditional(self.P, self.Q),
            self.P,
        ]
        self.assertTrue(
            is_valid_argument(premises, self.Q)
        )

    def test_truth_table_is_repeatable_and_ordered(self):
        expression = Implies(self.P, self.Q)

        expected = [
            {"assignment": {"P": True, "Q": True}, "result": True},
            {"assignment": {"P": True, "Q": False}, "result": False},
            {"assignment": {"P": False, "Q": True}, "result": True},
            {"assignment": {"P": False, "Q": False}, "result": True},
        ]

        first = truth_table(expression)
        second = truth_table(expression)
        third = truth_table(expression)

        self.assertEqual(first, expected)
        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_argument_validity_agrees_with_tautology_encoding(self):
        premise1 = Implies(self.P, self.Q)
        premise2 = self.P
        conclusion = self.Q

        argument_valid = is_valid_argument(
            [premise1, premise2],
            conclusion,
        )

        encoded_argument = Implies(
            And(premise1, premise2),
            conclusion,
        )

        self.assertTrue(argument_valid)
        self.assertTrue(is_tautology(encoded_argument))


if __name__ == "__main__":
    unittest.main(verbosity=2)
