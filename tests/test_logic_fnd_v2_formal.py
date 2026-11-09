"""Deterministic formal-logic foundation tests; no Executive or model execution."""
import unittest

from xyra_logic.formal import (
    Atom, Not, And, Or, Implies, Iff, evaluate, variables,
    assignments, models, satisfiable, countermodels, analyze,
)


class FormalFoundationsTests(unittest.TestCase):
    def setUp(self):
        self.p, self.q = Atom("P"), Atom("Q")

    def test_modus_ponens(self):
        result = analyze([Implies(self.p, self.q), self.p], self.q)
        self.assertTrue(result["entails"])
        self.assertTrue(result["premises_consistent"])
        self.assertFalse(result["vacuous"])

    def test_modus_tollens(self):
        self.assertTrue(analyze([Implies(self.p, self.q), Not(self.q)], Not(self.p))["entails"])

    def test_affirming_consequent_countermodel(self):
        result = analyze([Implies(self.p, self.q), self.q], self.p)
        self.assertFalse(result["entails"])
        self.assertIn({"P": False, "Q": True}, result["countermodels"])

    def test_denying_antecedent_countermodel(self):
        result = analyze([Implies(self.p, self.q), Not(self.p)], Not(self.q))
        self.assertFalse(result["entails"])
        self.assertIn({"P": False, "Q": True}, result["countermodels"])

    def test_inconsistency_is_vacuous_not_substantive(self):
        result = analyze([self.p, Not(self.p)], self.q)
        self.assertTrue(result["entails"])
        self.assertFalse(result["premises_consistent"])
        self.assertTrue(result["vacuous"])
        self.assertEqual(result["countermodels"], [])

    def test_pilot_does_not_imply_production(self):
        result = analyze([self.p], self.q)
        self.assertFalse(result["entails"])
        self.assertIn({"P": True, "Q": False}, result["countermodels"])

    def test_disjunction_and_biconditional(self):
        self.assertTrue(evaluate(Or(self.p, self.q), {"P": False, "Q": True}))
        self.assertTrue(evaluate(Iff(self.p, self.q), {"P": True, "Q": True}))
        self.assertFalse(evaluate(Iff(self.p, self.q), {"P": True, "Q": False}))

    def test_conjunction_and_negation(self):
        f = And(self.p, Not(self.q))
        self.assertEqual(variables(f), frozenset({"P", "Q"}))
        self.assertEqual(models([f]), [{"P": True, "Q": False}])

    def test_tautology_and_empty_premises(self):
        self.assertTrue(analyze([], Or(self.p, Not(self.p)))["entails"])
        self.assertTrue(satisfiable([]))
        self.assertEqual(list(assignments([])), [{}])

    def test_atom_limit_fail_closed(self):
        formulas = [Atom("X" + str(i)) for i in range(17)]
        with self.assertRaises(ValueError):
            models(formulas)

    def test_invalid_formula_rejected(self):
        with self.assertRaises(TypeError):
            variables("P")
        with self.assertRaises(TypeError):
            evaluate("P", {})
        with self.assertRaises(ValueError):
            Atom("  ")

    def test_deterministic_order(self):
        self.assertEqual(list(assignments([self.q, self.p]))[0], {"P": False, "Q": False})
        self.assertEqual(len(countermodels([], self.p)), 1)


if __name__ == "__main__":
    unittest.main()
