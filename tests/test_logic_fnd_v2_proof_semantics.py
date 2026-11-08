"""Cross-check proof certificates against independent finite truth-table semantics."""
import unittest
from xyra_logic.formal import Atom, And, Implies, Not, analyze, assignments, evaluate
from xyra_logic.proof import ProofStep as S, ProofError, verify_proof


class ProofSemanticCrosscheckTests(unittest.TestCase):
    def setUp(self):
        self.p, self.q, self.r = Atom("P"), Atom("Q"), Atom("R")

    def assert_sound_on_assignments(self, premises, steps, conclusion):
        self.assertTrue(verify_proof(premises, steps, conclusion))
        for assignment in assignments(tuple(premises) + (conclusion,)):
            if all(evaluate(p, assignment) for p in premises):
                self.assertTrue(evaluate(conclusion, assignment), assignment)
        self.assertTrue(analyze(premises, conclusion)["entails"])

    def test_modus_ponens_sound(self):
        pq = Implies(self.p, self.q)
        self.assert_sound_on_assignments([pq, self.p],
            [S(pq, "premise"), S(self.p, "premise"),
             S(self.q, "modus_ponens", (0, 1))], self.q)

    def test_conjunction_sound(self):
        pq = And(self.p, self.q)
        self.assert_sound_on_assignments([self.p, self.q],
            [S(self.p, "premise"), S(self.q, "premise"),
             S(pq, "and_intro", (0, 1))], pq)

    def test_double_negation_sound(self):
        nn = Not(Not(self.p))
        self.assert_sound_on_assignments([nn],
            [S(nn, "premise"), S(self.p, "double_negation", (0,))], self.p)

    def test_identity_implication_sound(self):
        identity = Implies(self.p, self.p)
        self.assert_sound_on_assignments([],
            [S(self.p, "assume"), S(identity, "implies_intro", (0,), assumption=0)],
            identity)

    def test_nested_implication_sound(self):
        inner = Implies(self.q, self.p)
        outer = Implies(self.p, inner)
        pair = And(self.p, self.q)
        self.assert_sound_on_assignments([],
            [S(self.p, "assume"), S(self.q, "assume"),
             S(pair, "and_intro", (0, 1)), S(self.p, "and_left", (2,)),
             S(inner, "implies_intro", (3,), assumption=1),
             S(outer, "implies_intro", (4,), assumption=0)], outer)

    def test_invalid_affirming_consequent_cannot_be_certified(self):
        pq = Implies(self.p, self.q)
        self.assertFalse(analyze([pq, self.q], self.p)["entails"])
        with self.assertRaises(ProofError):
            verify_proof([pq, self.q],
                [S(pq, "premise"), S(self.q, "premise"),
                 S(self.p, "modus_ponens", (0, 1))], self.p)


if __name__ == "__main__":
    unittest.main()
