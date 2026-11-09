"""Quantifier substitution safety and finite-domain semantic cross-checks."""
import unittest
from xyra_logic.first_order import (
    Variable, Constant, Predicate, Equals, FNot, FAnd, FOr,
    FImplies, ForAll, Exists, interpret,
)
from xyra_logic.quantifier_rules import (
    CaptureError, free_variables, substitute,
    universal_instance, existential_witness,
)


class QuantifierRulesTests(unittest.TestCase):
    def setUp(self):
        self.x, self.y = Variable("x"), Variable("y")
        self.p = Predicate("P", (self.x,))
        self.domain = ("a", "b")

    def test_free_variables(self):
        f = ForAll(self.x, Predicate("R", (self.x, self.y)))
        self.assertEqual(free_variables(f), frozenset({"y"}))

    def test_universal_instance_constant(self):
        f = ForAll(self.x, self.p)
        self.assertEqual(universal_instance(f, Constant("a")),
                         Predicate("P", (Constant("a"),)))

    def test_existential_witness_constant(self):
        f = Exists(self.x, self.p)
        self.assertEqual(existential_witness(f, Constant("b")),
                         Predicate("P", (Constant("b"),)))

    def test_shadowed_binder_unchanged(self):
        f = ForAll(self.x, self.p)
        self.assertEqual(substitute(f, self.x, Constant("a")), f)

    def test_capture_rejected(self):
        f = Exists(self.y, Predicate("R", (self.x, self.y)))
        with self.assertRaises(CaptureError):
            substitute(f, self.x, self.y)

    def test_safe_rename_free_variable(self):
        f = Predicate("R", (self.x, self.y))
        self.assertEqual(substitute(f, self.x, self.y),
                         Predicate("R", (self.y, self.y)))

    def test_nested_binder_preserved(self):
        f = ForAll(self.y, Exists(self.x, self.p))
        self.assertEqual(substitute(f, self.x, Constant("a")), f)

    def test_equality_substitution(self):
        f = Equals(self.x, Constant("a"))
        self.assertEqual(substitute(f, self.x, Constant("b")),
                         Equals(Constant("b"), Constant("a")))

    def test_boolean_connectives_substitution(self):
        f = FImplies(FAnd(self.p, FNot(self.p)), FOr(self.p, self.p))
        replaced = substitute(f, self.x, Constant("a"))
        self.assertNotIn("x", free_variables(replaced))

    def test_universal_soundness_for_each_finite_interpretation(self):
        f = ForAll(self.x, self.p)
        instance = universal_instance(f, Constant("a"))
        for bits in range(4):
            extension = {((name),) for i, name in enumerate(self.domain) if bits & (1 << i)}
            predicates = {"P": extension}
            if interpret(f, self.domain, predicates):
                self.assertTrue(interpret(instance, self.domain, predicates))

    def test_existential_witness_implies_exists(self):
        f = Exists(self.x, self.p)
        witness = existential_witness(f, Constant("b"))
        for bits in range(4):
            extension = {(name,) for i, name in enumerate(self.domain) if bits & (1 << i)}
            predicates = {"P": extension}
            if interpret(witness, self.domain, predicates):
                self.assertTrue(interpret(f, self.domain, predicates))

    def test_invalid_term_rejected(self):
        with self.assertRaises(TypeError):
            substitute(self.p, self.x, "a")

    def test_invalid_quantifier_rejected(self):
        with self.assertRaises(TypeError):
            universal_instance(self.p, Constant("a"))


if __name__ == "__main__":
    unittest.main()
