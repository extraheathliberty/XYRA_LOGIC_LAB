import unittest
from itertools import product

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


BOOLS = (True, False)


def reference_evaluate(expression, assignment):
    """Independent propositional evaluator used only as test oracle."""

    if isinstance(expression, Atom):
        return assignment[expression.name]

    if isinstance(expression, Not):
        return not reference_evaluate(expression.operand, assignment)

    if isinstance(expression, And):
        values = (
            reference_evaluate(expression.left, assignment),
            reference_evaluate(expression.right, assignment),
        )
        return {
            (True, True): True,
            (True, False): False,
            (False, True): False,
            (False, False): False,
        }[values]

    if isinstance(expression, Or):
        values = (
            reference_evaluate(expression.left, assignment),
            reference_evaluate(expression.right, assignment),
        )
        return {
            (True, True): True,
            (True, False): True,
            (False, True): True,
            (False, False): False,
        }[values]

    if isinstance(expression, Implies):
        values = (
            reference_evaluate(expression.left, assignment),
            reference_evaluate(expression.right, assignment),
        )
        return {
            (True, True): True,
            (True, False): False,
            (False, True): True,
            (False, False): True,
        }[values]

    if isinstance(expression, Biconditional):
        values = (
            reference_evaluate(expression.left, assignment),
            reference_evaluate(expression.right, assignment),
        )
        return {
            (True, True): True,
            (True, False): False,
            (False, True): False,
            (False, False): True,
        }[values]

    raise TypeError(type(expression).__name__)


def reference_symbols(expression):
    if isinstance(expression, Atom):
        return {expression.name}

    if isinstance(expression, Not):
        return reference_symbols(expression.operand)

    if isinstance(expression, (And, Or, Implies, Biconditional)):
        return (
            reference_symbols(expression.left)
            | reference_symbols(expression.right)
        )

    raise TypeError(type(expression).__name__)


def reference_assignments(names):
    ordered = tuple(sorted(names))

    for values in product(BOOLS, repeat=len(ordered)):
        yield dict(zip(ordered, values))


def reference_truth_table(expression):
    return [
        {
            "assignment": assignment,
            "result": reference_evaluate(expression, assignment),
        }
        for assignment in reference_assignments(
            reference_symbols(expression)
        )
    ]


def reference_valid_argument(premises, conclusion):
    names = set(reference_symbols(conclusion))

    for premise in premises:
        names.update(reference_symbols(premise))

    for assignment in reference_assignments(names):
        premises_true = all(
            reference_evaluate(premise, assignment)
            for premise in premises
        )
        conclusion_true = reference_evaluate(
            conclusion,
            assignment,
        )

        if premises_true and not conclusion_true:
            return False

    return True


def generated_formulas(max_depth):
    """Generate a deterministic, duplicate-free bounded formula corpus."""

    P = Atom("P")
    Q = Atom("Q")

    formulas = []
    seen = set()

    def add(expression):
        if expression not in seen:
            seen.add(expression)
            formulas.append(expression)

    add(P)
    add(Q)

    for _ in range(max_depth):
        base = list(formulas)

        for expression in base:
            add(Not(expression))

        for left in base:
            for right in base:
                add(And(left, right))
                add(Or(left, right))
                add(Implies(left, right))
                add(Biconditional(left, right))

    return formulas


class LogicL0GeneratedQualificationTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.depth1 = generated_formulas(1)
        cls.depth2 = generated_formulas(2)

        if len(cls.depth1) != 20:
            raise AssertionError(
                f"Expected 20 depth-1 formulas, got {len(cls.depth1)}"
            )

        if len(cls.depth2) != 1622:
            raise AssertionError(
                f"Expected 1622 depth-2 formulas, got {len(cls.depth2)}"
            )

    def test_generated_evaluation_matches_reference(self):
        for expression in self.depth2:
            for assignment in reference_assignments(
                reference_symbols(expression)
            ):
                with self.subTest(
                    expression=expression,
                    assignment=assignment,
                ):
                    self.assertEqual(
                        evaluate(expression, assignment),
                        reference_evaluate(
                            expression,
                            assignment,
                        ),
                    )

    def test_generated_truth_tables_match_reference(self):
        for expression in self.depth2:
            with self.subTest(expression=expression):
                self.assertEqual(
                    truth_table(expression),
                    reference_truth_table(expression),
                )

    def test_generated_tautology_classification_matches_reference(self):
        for expression in self.depth2:
            results = [
                row["result"]
                for row in reference_truth_table(expression)
            ]

            with self.subTest(expression=expression):
                self.assertEqual(
                    is_tautology(expression),
                    all(results),
                )

    def test_generated_contradiction_classification_matches_reference(self):
        for expression in self.depth2:
            results = [
                row["result"]
                for row in reference_truth_table(expression)
            ]

            with self.subTest(expression=expression):
                self.assertEqual(
                    is_contradiction(expression),
                    not any(results),
                )

    def test_zero_premise_validity_matches_tautology(self):
        for expression in self.depth2:
            with self.subTest(expression=expression):
                self.assertEqual(
                    is_valid_argument([], expression),
                    is_tautology(expression),
                )

    def test_all_depth1_single_premise_arguments_match_reference(self):
        for premise in self.depth1:
            for conclusion in self.depth1:
                with self.subTest(
                    premise=premise,
                    conclusion=conclusion,
                ):
                    self.assertEqual(
                        is_valid_argument(
                            [premise],
                            conclusion,
                        ),
                        reference_valid_argument(
                            [premise],
                            conclusion,
                        ),
                    )

    def test_all_depth1_two_premise_arguments_match_reference(self):
        for premise1 in self.depth1:
            for premise2 in self.depth1:
                for conclusion in self.depth1:
                    with self.subTest(
                        premise1=premise1,
                        premise2=premise2,
                        conclusion=conclusion,
                    ):
                        self.assertEqual(
                            is_valid_argument(
                                [premise1, premise2],
                                conclusion,
                            ),
                            reference_valid_argument(
                                [premise1, premise2],
                                conclusion,
                            ),
                        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
