"""Deterministic proof-checking acceptance and rejection tests."""
import unittest
from xyra_logic.formal import Atom, And, Implies, Not
from xyra_logic.proof import ProofStep as S, ProofError, verify_proof


class ProofTests(unittest.TestCase):
    def setUp(self):
        self.p, self.q = Atom("P"), Atom("Q")

    def test_modus_ponens(self):
        implication = Implies(self.p, self.q)
        steps = [S(implication, "premise"), S(self.p, "premise"),
                 S(self.q, "modus_ponens", (0, 1))]
        self.assertTrue(verify_proof([implication, self.p], steps, self.q))

    def test_and_introduction(self):
        conjunction = And(self.p, self.q)
        steps = [S(self.p, "premise"), S(self.q, "premise"),
                 S(conjunction, "and_intro", (0, 1))]
        self.assertTrue(verify_proof([self.p, self.q], steps, conjunction))

    def test_and_elimination(self):
        pair = And(self.p, self.q)
        steps = [S(pair, "premise"), S(self.q, "and_right", (0,))]
        self.assertTrue(verify_proof([pair], steps, self.q))

    def test_double_negation(self):
        nn = Not(Not(self.p))
        self.assertTrue(verify_proof([nn], [S(nn, "premise"), S(self.p, "double_negation", (0,))], self.p))

    def test_identity_implication_discharge(self):
        conclusion = Implies(self.p, self.p)
        steps = [S(self.p, "assume"), S(conclusion, "implies_intro", (0,), assumption=0)]
        self.assertTrue(verify_proof([], steps, conclusion))

    def test_nested_discharge(self):
        inner = Implies(self.q, self.p)
        outer = Implies(self.p, inner)
        steps = [S(self.p, "assume"), S(self.q, "assume"),
                 S(inner, "implies_intro", (0,), assumption=1),
                 S(outer, "implies_intro", (2,), assumption=0)]
        self.assertTrue(verify_proof([], steps, outer))

    def test_undischarged_assumption_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([], [S(self.p, "assume")], self.p)

    def test_invalid_modus_ponens_rejected(self):
        implication = Implies(self.p, self.q)
        steps = [S(implication, "premise"), S(self.q, "premise"),
                 S(self.p, "modus_ponens", (0, 1))]
        with self.assertRaises(ProofError):
            verify_proof([implication, self.q], steps, self.p)

    def test_forward_reference_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([self.p], [S(self.p, "premise", (1,))], self.p)

    def test_unlisted_premise_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([], [S(self.p, "premise")], self.p)

    def test_unknown_rule_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([], [S(self.p, "magic")], self.p)

    def test_discharge_unrelated_assumption_rejected(self):
        implication = Implies(self.p, self.q)
        steps = [S(self.p, "assume"), S(self.q, "premise"),
                 S(implication, "implies_intro", (1,), assumption=0)]
        with self.assertRaises(ProofError):
            verify_proof([self.q], steps, implication)

    def test_conclusion_mismatch_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([self.p], [S(self.p, "premise")], self.q)

    def test_empty_proof_rejected(self):
        with self.assertRaises(ProofError):
            verify_proof([], [], self.p)


if __name__ == "__main__":
    unittest.main()
