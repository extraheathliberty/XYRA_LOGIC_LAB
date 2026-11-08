"""Contradiction witness tests for deterministic logic foundations."""
import unittest
from xyra_logic.formal import Atom, Not, And, Or, Implies, diagnose, minimal_inconsistent_subset


class ContradictionDiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.p, self.q, self.r = Atom("P"), Atom("Q"), Atom("R")

    def test_consistent_has_no_core(self):
        self.assertEqual(minimal_inconsistent_subset([self.p, self.q]), ())

    def test_direct_contradiction(self):
        self.assertEqual(minimal_inconsistent_subset([self.p, Not(self.p)]), (self.p, Not(self.p)))

    def test_irrelevant_premises_excluded(self):
        core = minimal_inconsistent_subset([self.r, self.p, Not(self.p)])
        self.assertEqual(core, (self.p, Not(self.p)))

    def test_indirect_contradiction(self):
        premises = [Implies(self.p, self.q), self.p, Not(self.q), self.r]
        self.assertEqual(minimal_inconsistent_subset(premises), tuple(premises[:3]))

    def test_each_core_member_necessary(self):
        core = minimal_inconsistent_subset([Implies(self.p, self.q), self.p, Not(self.q)])
        for i in range(len(core)):
            self.assertEqual(minimal_inconsistent_subset(core[:i] + core[i+1:]), ())

    def test_diagnose_marks_vacuity(self):
        result = diagnose([self.p, Not(self.p)], self.q)
        self.assertTrue(result["vacuous"])
        self.assertTrue(result["entails"])
        self.assertEqual(result["inconsistent_subset"], (self.p, Not(self.p)))

    def test_diagnose_invalid_inference_counterexample(self):
        result = diagnose([Implies(self.p, self.q), self.q], self.p)
        self.assertFalse(result["entails"])
        self.assertEqual(result["inconsistent_subset"], ())
        self.assertIn({"P": False, "Q": True}, result["countermodels"])

    def test_atom_limit_is_enforced(self):
        with self.assertRaises(ValueError):
            minimal_inconsistent_subset([Atom("X" + str(i)) for i in range(17)])

    def test_single_false_formula_is_core(self):
        impossible = And(self.p, Not(self.p))
        self.assertEqual(minimal_inconsistent_subset([self.q, impossible]), (impossible,))


if __name__ == "__main__":
    unittest.main()
