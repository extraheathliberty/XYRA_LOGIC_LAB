from __future__ import annotations

from itertools import product
from typing import Mapping, Sequence

from .expressions import (
    And,
    Atom,
    Biconditional,
    Expression,
    Implies,
    Not,
    Or,
)


Assignment = Mapping[str, bool]


def evaluate(expression: Expression, assignment: Assignment) -> bool:
    """Evaluate a propositional expression under a supplied truth assignment."""

    if isinstance(expression, Atom):
        if expression.name not in assignment:
            raise KeyError(f"Missing truth assignment for atom: {expression.name}")
        value = assignment[expression.name]
        if not isinstance(value, bool):
            raise TypeError(
                f"Truth assignment for {expression.name} must be bool, "
                f"got {type(value).__name__}."
            )
        return value

    if isinstance(expression, Not):
        return not evaluate(expression.operand, assignment)

    if isinstance(expression, And):
        return evaluate(expression.left, assignment) and evaluate(
            expression.right, assignment
        )

    if isinstance(expression, Or):
        return evaluate(expression.left, assignment) or evaluate(
            expression.right, assignment
        )

    if isinstance(expression, Implies):
        return (not evaluate(expression.left, assignment)) or evaluate(
            expression.right, assignment
        )

    if isinstance(expression, Biconditional):
        return evaluate(expression.left, assignment) == evaluate(
            expression.right, assignment
        )

    raise TypeError(f"Unsupported expression type: {type(expression).__name__}")


def symbols(expression: Expression) -> tuple[str, ...]:
    """Return the expression's atom names in deterministic sorted order."""

    found: set[str] = set()

    def visit(node: Expression) -> None:
        if isinstance(node, Atom):
            found.add(node.name)
        elif isinstance(node, Not):
            visit(node.operand)
        elif isinstance(node, (And, Or, Implies, Biconditional)):
            visit(node.left)
            visit(node.right)
        else:
            raise TypeError(
                f"Unsupported expression type: {type(node).__name__}"
            )

    visit(expression)
    return tuple(sorted(found))


def _all_assignments(names: Sequence[str]):
    for values in product((True, False), repeat=len(names)):
        yield dict(zip(names, values))


def truth_table(expression: Expression) -> list[dict[str, object]]:
    """Generate a deterministic complete truth table."""

    names = symbols(expression)
    rows: list[dict[str, object]] = []

    for assignment in _all_assignments(names):
        rows.append(
            {
                "assignment": assignment,
                "result": evaluate(expression, assignment),
            }
        )

    return rows


def is_tautology(expression: Expression) -> bool:
    return all(bool(row["result"]) for row in truth_table(expression))


def is_contradiction(expression: Expression) -> bool:
    return all(not bool(row["result"]) for row in truth_table(expression))


def is_valid_argument(
    premises: Sequence[Expression],
    conclusion: Expression,
) -> bool:
    """
    Return True iff no assignment makes every premise true
    while making the conclusion false.
    """

    all_names: set[str] = set(symbols(conclusion))
    for premise in premises:
        all_names.update(symbols(premise))

    names = tuple(sorted(all_names))

    for assignment in _all_assignments(names):
        premises_true = all(evaluate(p, assignment) for p in premises)
        conclusion_true = evaluate(conclusion, assignment)

        if premises_true and not conclusion_true:
            return False

    return True
