import unittest

from xyra_logic import (
    And,
    Atom,
    Biconditional,
    Implies,
    Not,
    Or,
    evaluate,
    is_contradiction,
    is_tautology,
    is_valid_argument,
    truth_table,
)


class LogicL0Tests(unittest.TestCase):

    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")

    def test_atom(self):
        self.assertTrue(evaluate(self.P, {"P": True}))
        self.assertFalse(evaluate(self.P, {"P": False}))

    def test_not(self):
        self.assertFalse(evaluate(Not(self.P), {"P": True}))
        self.assertTrue(evaluate(Not(self.P), {"P": False}))

    def test_and(self):
        self.assertTrue(
            evaluate(And(self.P, self.Q), {"P": True, "Q": True})
        )
        self.assertFalse(
            evaluate(And(self.P, self.Q), {"P": True, "Q": False})
        )

    def test_or(self):
        self.assertFalse(
            evaluate(Or(self.P, self.Q), {"P": False, "Q": False})
        )
        self.assertTrue(
            evaluate(Or(self.P, self.Q), {"P": False, "Q": True})
        )

    def test_implies(self):
        expression = Implies(self.P, self.Q)

        self.assertTrue(
            evaluate(expression, {"P": True, "Q": True})
        )
        self.assertFalse(
            evaluate(expression, {"P": True, "Q": False})
        )
        self.assertTrue(
            evaluate(expression, {"P": False, "Q": True})
        )
        self.assertTrue(
            evaluate(expression, {"P": False, "Q": False})
        )

    def test_biconditional(self):
        expression = Biconditional(self.P, self.Q)

        self.assertTrue(
            evaluate(expression, {"P": True, "Q": True})
        )
        self.assertFalse(
            evaluate(expression, {"P": True, "Q": False})
        )
        self.assertFalse(
            evaluate(expression, {"P": False, "Q": True})
        )
        self.assertTrue(
            evaluate(expression, {"P": False, "Q": False})
        )

    def test_truth_table(self):
        rows = truth_table(Implies(self.P, self.Q))

        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [row["result"] for row in rows],
            [True, False, True, True],
        )

    def test_tautology(self):
        expression = Or(self.P, Not(self.P))
        self.assertTrue(is_tautology(expression))

    def test_contradiction(self):
        expression = And(self.P, Not(self.P))
        self.assertTrue(is_contradiction(expression))

    def test_modus_ponens_valid(self):
        premises = [
            self.P,
            Implies(self.P, self.Q),
        ]
        self.assertTrue(
            is_valid_argument(premises, self.Q)
        )

    def test_affirming_consequent_invalid(self):
        premises = [
            Implies(self.P, self.Q),
            self.Q,
        ]
        self.assertFalse(
            is_valid_argument(premises, self.P)
        )

    def test_missing_assignment_rejected(self):
        with self.assertRaises(KeyError):
            evaluate(And(self.P, self.Q), {"P": True})

    def test_non_boolean_assignment_rejected(self):
        with self.assertRaises(TypeError):
            evaluate(self.P, {"P": 1})


if __name__ == "__main__":
    unittest.main(verbosity=2)
