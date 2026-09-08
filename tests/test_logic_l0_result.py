import unittest

from xyra_logic import (
    Atom,
    Implies,
    Not,
    Or,
    analyze_argument,
    is_valid_argument,
)


class LogicL0ResultTests(unittest.TestCase):

    def setUp(self):
        self.P = Atom("P")
        self.Q = Atom("Q")

    def test_valid_argument_has_no_countermodel(self):
        premises = [
            Implies(self.P, self.Q),
            self.P,
        ]

        result = analyze_argument(premises, self.Q)

        self.assertEqual(result.status, "VALID_ARGUMENT")
        self.assertIsNone(result.countermodel)
        self.assertIsNone(result.premise_values)
        self.assertIsNone(result.conclusion_value)

    def test_invalid_argument_returns_countermodel(self):
        premises = [
            Implies(self.P, self.Q),
            self.Q,
        ]

        result = analyze_argument(premises, self.P)

        self.assertEqual(result.status, "INVALID_ARGUMENT")
        self.assertEqual(
            result.countermodel,
            (("P", False), ("Q", True)),
        )
        self.assertEqual(
            result.premise_values,
            (True, True),
        )
        self.assertFalse(result.conclusion_value)

    def test_countermodel_replays_as_defeating_witness(self):
        premises = [
            Implies(self.P, self.Q),
            Not(self.P),
        ]

        result = analyze_argument(
            premises,
            Not(self.Q),
        )

        self.assertEqual(result.status, "INVALID_ARGUMENT")
        self.assertEqual(
            result.countermodel,
            (("P", False), ("Q", True)),
        )
        self.assertTrue(all(result.premise_values))
        self.assertFalse(result.conclusion_value)

    def test_countermodel_atom_order_is_deterministic(self):
        premises = [
            Or(self.Q, self.P),
            self.P,
        ]

        result = analyze_argument(
            premises,
            Not(self.Q),
        )

        self.assertEqual(
            tuple(name for name, _ in result.countermodel),
            ("P", "Q"),
        )

    def test_repeated_analysis_is_identical(self):
        premises = [
            Implies(self.P, self.Q),
            self.Q,
        ]

        first = analyze_argument(premises, self.P)
        second = analyze_argument(premises, self.P)
        third = analyze_argument(premises, self.P)

        self.assertEqual(first, second)
        self.assertEqual(second, third)

    def test_zero_premise_tautology_is_valid(self):
        conclusion = Or(
            self.P,
            Not(self.P),
        )

        result = analyze_argument([], conclusion)

        self.assertEqual(result.status, "VALID_ARGUMENT")
        self.assertIsNone(result.countermodel)

    def test_zero_premise_non_tautology_returns_countermodel(self):
        result = analyze_argument([], self.P)

        self.assertEqual(result.status, "INVALID_ARGUMENT")
        self.assertEqual(
            result.countermodel,
            (("P", False),),
        )
        self.assertEqual(result.premise_values, ())
        self.assertFalse(result.conclusion_value)

    def test_boolean_api_agrees_with_structured_result(self):
        cases = [
            (
                [Implies(self.P, self.Q), self.P],
                self.Q,
            ),
            (
                [Implies(self.P, self.Q), self.Q],
                self.P,
            ),
            (
                [Implies(self.P, self.Q), Not(self.Q)],
                Not(self.P),
            ),
        ]

        for premises, conclusion in cases:
            with self.subTest(
                premises=premises,
                conclusion=conclusion,
            ):
                result = analyze_argument(
                    premises,
                    conclusion,
                )

                self.assertEqual(
                    is_valid_argument(premises, conclusion),
                    result.status == "VALID_ARGUMENT",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
