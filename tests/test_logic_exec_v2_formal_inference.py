"""Formal inference countermodels for Executive development.

Pure Boolean countermodels are deliberately separate from the current
Executive validator: a validator passing its own schema is not a proof
that an Executive can reason soundly. No model or runtime invocation.
"""
import itertools
import unittest


def implies(p, q):
    return not p or q


def valid_inference(premises, conclusion):
    """Validity: no valuation makes all premises true and conclusion false."""
    for p, q in itertools.product((False, True), repeat=2):
        if all(f(p, q) for f in premises) and not conclusion(p, q):
            return False
    return True


def countermodels(premises, conclusion):
    return [
        {"P": p, "Q": q}
        for p, q in itertools.product((False, True), repeat=2)
        if all(f(p, q) for f in premises) and not conclusion(p, q)
    ]


class TestExecutiveFormalInference(unittest.TestCase):
    def test_modus_ponens_valid(self):
        self.assertTrue(valid_inference(
            [lambda p, q: implies(p, q), lambda p, q: p],
            lambda p, q: q,
        ))

    def test_modus_tollens_valid(self):
        self.assertTrue(valid_inference(
            [lambda p, q: implies(p, q), lambda p, q: not q],
            lambda p, q: not p,
        ))

    def test_affirming_consequent_invalid(self):
        premises = [lambda p, q: implies(p, q), lambda p, q: q]
        self.assertFalse(valid_inference(premises, lambda p, q: p))
        self.assertIn({"P": False, "Q": True}, countermodels(premises, lambda p, q: p))

    def test_denying_antecedent_invalid(self):
        premises = [lambda p, q: implies(p, q), lambda p, q: not p]
        self.assertFalse(valid_inference(premises, lambda p, q: not q))
        self.assertIn({"P": False, "Q": True}, countermodels(premises, lambda p, q: not q))

    def test_contradictory_premises_no_countermodel(self):
        premises = [lambda p, q: p, lambda p, q: not p]
        self.assertEqual(countermodels(premises, lambda p, q: q), [])
        # Classical validity here is vacuous; consistency must be checked separately.
        self.assertTrue(valid_inference(premises, lambda p, q: q))

    def test_unsupported_production_inference_invalid(self):
        # P = bounded internal pilot permitted; Q = production admitted.
        premises = [lambda p, q: p]
        self.assertFalse(valid_inference(premises, lambda p, q: q))
        self.assertIn({"P": True, "Q": False}, countermodels(premises, lambda p, q: q))

    def test_downstream_condition_not_required_for_pilot(self):
        # P = internal pilot allowed; Q = production ready.
        premises = [lambda p, q: p, lambda p, q: not q]
        self.assertFalse(valid_inference(premises, lambda p, q: not p))
        self.assertIn({"P": True, "Q": False}, countermodels(premises, lambda p, q: not p))

    def test_indeterminate_antecedent_does_not_prove_conclusion(self):
        premises = [lambda p, q: implies(p, q)]
        self.assertFalse(valid_inference(premises, lambda p, q: q))


if __name__ == "__main__":
    unittest.main()
