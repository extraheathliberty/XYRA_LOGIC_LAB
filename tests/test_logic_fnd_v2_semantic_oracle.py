"""Independent oracle tests and proof certificate regression checks."""
import unittest
from itertools import product
from xyra_logic.formal import Atom, Not, And, Or, Implies, Iff, evaluate
from xyra_logic.proof import ProofStep as S, ProofError
from xyra_logic.semantic_oracle import (
    oracle_evaluate, oracle_atoms, oracle_countermodels, check_certificate,
)


class SemanticOracleTests(unittest.TestCase):
    def setUp(self):
        self.p, self.q = Atom("P"), Atom("Q")
        self.assignments = [dict(zip(("P", "Q"), values))
                            for values in product((False, True), repeat=2)]

    def test_all_connectives_against_separate_oracle(self):
        formulas = [self.p, Not(self.p), And(self.p, self.q),
                    Or(self.p, self.q), Implies(self.p, self.q),
                    Iff(self.p, self.q), Not(Implies(self.p, self.q))]
        for formula in formulas:
            for assignment in self.assignments:
                self.assertEqual(oracle_evaluate(formula, assignment),
                                 evaluate(formula, assignment))

    def test_nested_formula_oracle(self):
        f = Iff(Implies(self.p, self.q), Or(Not(self.p), self.q))
        self.assertTrue(all(oracle_evaluate(f, a) for a in self.assignments))

    def test_atom_collection(self):
        self.assertEqual(oracle_atoms(And(self.p, Not(self.q))), {"P", "Q"})

    def test_invalid_consequent_has_countermodel(self):
        witnesses = oracle_countermodels([Implies(self.p, self.q), self.q], self.p)
        self.assertIn({"P": False, "Q": True}, witnesses)

    def test_valid_modus_ponens_has_no_countermodel(self):
        self.assertEqual(oracle_countermodels([Implies(self.p, self.q), self.p], self.q), [])

    def test_inconsistent_premises_have_no_countermodel(self):
        self.assertEqual(oracle_countermodels([self.p, Not(self.p)], self.q), [])

    def test_tautology(self):
        self.assertEqual(oracle_countermodels([], Or(self.p, Not(self.p))), [])

    def test_oracle_atom_cap(self):
        with self.assertRaises(ValueError):
            oracle_countermodels([Atom(str(i)) for i in range(13)], self.p)

    def test_certified_modus_ponens(self):
        pq = Implies(self.p, self.q)
        steps = [S(pq, "premise"), S(self.p, "premise"),
                 S(self.q, "modus_ponens", (0, 1))]
        result = check_certificate([pq, self.p], steps, self.q)
        self.assertTrue(result["bounded_semantically_sound"])
        self.assertEqual(result["countermodels"], [])

    def test_certified_identity(self):
        identity = Implies(self.p, self.p)
        steps = [S(self.p, "assume"),
                 S(identity, "implies_intro", (0,), assumption=0)]
        self.assertTrue(check_certificate([], steps, identity)["bounded_semantically_sound"])

    def test_false_certificate_rejected(self):
        pq = Implies(self.p, self.q)
        steps = [S(pq, "premise"), S(self.q, "premise"),
                 S(self.p, "modus_ponens", (0, 1))]
        with self.assertRaises(ProofError):
            check_certificate([pq, self.q], steps, self.p)

    def test_open_assumption_rejected(self):
        with self.assertRaises(ProofError):
            check_certificate([], [S(self.p, "assume")], self.p)


if __name__ == "__main__":
    unittest.main()
