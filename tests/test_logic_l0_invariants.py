import unittest

from xyra_logic import (
    And,
    Atom,
    Implies,
    Not,
    Or,
    is_tautology,
    is_valid_argument,
)


class LogicL0InvariantTests(unittest.TestCase):

    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")
        self.R = Atom("R")

    def test_premise_order_does_not_change_validity(self):
        first = [
            self.P,
            Implies(self.P, self.Q),
        ]
        second = [
            Implies(self.P, self.Q),
            self.P,
        ]

        self.assertTrue(is_valid_argument(first, self.Q))
        self.assertTrue(is_valid_argument(second, self.Q))

    def test_duplicate_premises_do_not_change_validity(self):
        normal = [
            self.P,
            Implies(self.P, self.Q),
        ]
        duplicated = [
            self.P,
            self.P,
            Implies(self.P, self.Q),
            Implies(self.P, self.Q),
        ]

        self.assertEqual(
            is_valid_argument(normal, self.Q),
            is_valid_argument(duplicated, self.Q),
        )

    def test_atom_renaming_preserves_validity(self):
        A = Atom("A")
        B = Atom("B")

        original = is_valid_argument(
            [self.P, Implies(self.P, self.Q)],
            self.Q,
        )

        renamed = is_valid_argument(
            [A, Implies(A, B)],
            B,
        )

        self.assertEqual(original, renamed)

    def test_irrelevant_premise_preserves_validity(self):
        premises = [
            self.P,
            Implies(self.P, self.Q),
        ]

        expanded = [
            self.P,
            Implies(self.P, self.Q),
            self.R,
        ]

        self.assertTrue(is_valid_argument(premises, self.Q))
        self.assertTrue(is_valid_argument(expanded, self.Q))

    def test_double_negation_equivalence(self):
        expression = Implies(
            Not(Not(self.P)),
            self.P,
        )

        reverse = Implies(
            self.P,
            Not(Not(self.P)),
        )

        self.assertTrue(is_tautology(expression))
        self.assertTrue(is_tautology(reverse))

    def test_contraposition_equivalence(self):
        expression = Implies(
            Implies(self.P, self.Q),
            Implies(Not(self.Q), Not(self.P)),
        )

        self.assertTrue(is_tautology(expression))

    def test_de_morgan_not_and(self):
        left_to_right = Implies(
            Not(And(self.P, self.Q)),
            Or(Not(self.P), Not(self.Q)),
        )

        right_to_left = Implies(
            Or(Not(self.P), Not(self.Q)),
            Not(And(self.P, self.Q)),
        )

        self.assertTrue(is_tautology(left_to_right))
        self.assertTrue(is_tautology(right_to_left))

    def test_de_morgan_not_or(self):
        left_to_right = Implies(
            Not(Or(self.P, self.Q)),
            And(Not(self.P), Not(self.Q)),
        )

        right_to_left = Implies(
            And(Not(self.P), Not(self.Q)),
            Not(Or(self.P, self.Q)),
        )

        self.assertTrue(is_tautology(left_to_right))
        self.assertTrue(is_tautology(right_to_left))

    def test_hypothetical_syllogism_valid(self):
        premises = [
            Implies(self.P, self.Q),
            Implies(self.Q, self.R),
        ]

        conclusion = Implies(self.P, self.R)

        self.assertTrue(
            is_valid_argument(premises, conclusion)
        )

    def test_resolution_valid(self):
        premises = [
            Or(self.P, self.Q),
            Or(Not(self.P), self.R),
        ]

        conclusion = Or(self.Q, self.R)

        self.assertTrue(
            is_valid_argument(premises, conclusion)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
