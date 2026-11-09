"""Finite first-order semantics tests; deterministic, no model execution."""
import unittest
from xyra_logic.first_order import (
    Variable, Constant, Predicate, FNot, FAnd, FOr, FImplies,
    ForAll, Exists, Equals, interpret,
)


class FirstOrderTests(unittest.TestCase):
    def setUp(self):
        self.x = Variable("x")
        self.domain = ("a", "b")
        self.p = Predicate("P", (self.x,))

    def test_universal_true(self):
        self.assertTrue(interpret(ForAll(self.x, self.p), self.domain,
                                  {"P": {("a",), ("b",)}}))

    def test_universal_false(self):
        self.assertFalse(interpret(ForAll(self.x, self.p), self.domain,
                                   {"P": {("a",)}}))

    def test_existential_true(self):
        self.assertTrue(interpret(Exists(self.x, self.p), self.domain,
                                  {"P": {("b",)}}))

    def test_existential_false(self):
        self.assertFalse(interpret(Exists(self.x, self.p), self.domain,
                                   {"P": set()}))

    def test_quantifier_negation_duality(self):
        predicates = {"P": {("a",)}}
        lhs = FNot(ForAll(self.x, self.p))
        rhs = Exists(self.x, FNot(self.p))
        self.assertEqual(interpret(lhs, self.domain, predicates),
                         interpret(rhs, self.domain, predicates))

    def test_nested_quantifiers(self):
        y = Variable("y")
        relation = Predicate("R", (self.x, y))
        formula = ForAll(self.x, Exists(y, relation))
        self.assertTrue(interpret(formula, self.domain,
                                  {"R": {("a", "a"), ("b", "a")}}))

    def test_variable_shadowing(self):
        inner = Exists(self.x, self.p)
        formula = ForAll(self.x, inner)
        self.assertTrue(interpret(formula, self.domain, {"P": {("b",)}}))

    def test_equality(self):
        formula = Exists(self.x, Equals(self.x, Constant("b")))
        self.assertTrue(interpret(formula, self.domain, {}))

    def test_connectives(self):
        predicates = {"P": {("a",)}}
        formula = FImplies(FAnd(self.p, self.p), FOr(self.p, FNot(self.p)))
        self.assertTrue(interpret(ForAll(self.x, formula), self.domain, predicates))

    def test_empty_domain_rejected(self):
        with self.assertRaises(ValueError):
            interpret(ForAll(self.x, self.p), (), {"P": set()})

    def test_undefined_predicate_rejected(self):
        with self.assertRaises(ValueError):
            interpret(self.p, self.domain, {}, {"x": "a"})

    def test_unbound_variable_rejected(self):
        with self.assertRaises(ValueError):
            interpret(self.p, self.domain, {"P": set()})

    def test_constant_outside_domain_rejected(self):
        with self.assertRaises(ValueError):
            interpret(Equals(Constant("z"), Constant("a")), self.domain, {})

    def test_duplicate_domain_rejected(self):
        with self.assertRaises(ValueError):
            interpret(self.p, ("a", "a"), {"P": set()}, {"x": "a"})


if __name__ == "__main__":
    unittest.main()
