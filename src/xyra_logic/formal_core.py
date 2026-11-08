"""XYRA Formal Logic Foundations V2.

A finite propositional calculus with explicit syntax, truth evaluation,
countermodels and natural-deduction proof checking. No AI/runtime dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from typing import Iterable

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Not:
    value: object

@dataclass(frozen=True)
class And:
    left: object
    right: object

@dataclass(frozen=True)
class Or:
    left: object
    right: object

@dataclass(frozen=True)
class Imp:
    left: object
    right: object

@dataclass(frozen=True)
class Iff:
    left: object
    right: object

def variables(expr):
    if isinstance(expr, Var):
        if not expr.name:
            raise ValueError("variable name must be nonempty")
        return frozenset([expr.name])
    if isinstance(expr, Not):
        return variables(expr.value)
    if isinstance(expr, (And, Or, Imp, Iff)):
        return variables(expr.left) | variables(expr.right)
    raise TypeError(f"not a formula: {type(expr).__name__}")

def evaluate(expr, assignment):
    if isinstance(expr, Var):
        value = assignment[expr.name]
        if type(value) is not bool:
            raise TypeError("truth assignments must be bool")
        return value
    if isinstance(expr, Not):
        return not evaluate(expr.value, assignment)
    if isinstance(expr, And):
        return evaluate(expr.left, assignment) and evaluate(expr.right, assignment)
    if isinstance(expr, Or):
        return evaluate(expr.left, assignment) or evaluate(expr.right, assignment)
    if isinstance(expr, Imp):
        return not evaluate(expr.left, assignment) or evaluate(expr.right, assignment)
    if isinstance(expr, Iff):
        return evaluate(expr.left, assignment) == evaluate(expr.right, assignment)
    raise TypeError(f"not a formula: {type(expr).__name__}")

def valuations(formulas: Iterable):
    names = sorted(set().union(*(variables(f) for f in formulas)))
    for values in product((False, True), repeat=len(names)):
        yield dict(zip(names, values))

def countermodels(premises, conclusion):
    premises = tuple(premises)
    return [a for a in valuations((*premises, conclusion))
            if all(evaluate(p, a) for p in premises) and not evaluate(conclusion, a)]

def valid(premises, conclusion):
    return not countermodels(premises, conclusion)

def satisfiable(formulas):
    formulas = tuple(formulas)
    return any(all(evaluate(f, a) for f in formulas) for a in valuations(formulas))

@dataclass(frozen=True)
class ProofStep:
    formula: object
    rule: str
    refs: tuple[int, ...] = ()

def check_proof(premises, steps, conclusion):
    """Line references are zero-based and must precede the current step.

    Rules: premise, and_intro, and_elim_left/right, imp_elim,
    double_neg_elim, or_intro_left/right. All steps checked structurally.
    """
    premises = tuple(premises)
    derived = []
    for step in steps:
        variables(step.formula)
        if not isinstance(step.refs, tuple) or any(type(i) is not int or i < 0 or i >= len(derived) for i in step.refs):
            return False
        r = [derived[i] for i in step.refs]
        f = step.formula
        rule = step.rule
        ok = False
        if rule == "premise":
            ok = not r and f in premises
        elif rule == "and_intro":
            ok = len(r) == 2 and f == And(r[0], r[1])
        elif rule == "and_elim_left":
            ok = len(r) == 1 and isinstance(r[0], And) and f == r[0].left
        elif rule == "and_elim_right":
            ok = len(r) == 1 and isinstance(r[0], And) and f == r[0].right
        elif rule == "imp_elim":
            ok = len(r) == 2 and isinstance(r[0], Imp) and r[0].left == r[1] and f == r[0].right
        elif rule == "double_neg_elim":
            ok = len(r) == 1 and isinstance(r[0], Not) and isinstance(r[0].value, Not) and f == r[0].value.value
        elif rule == "or_intro_left":
            ok = len(r) == 1 and isinstance(f, Or) and f.left == r[0]
        elif rule == "or_intro_right":
            ok = len(r) == 1 and isinstance(f, Or) and f.right == r[0]
        if not ok:
            return False
        derived.append(f)
    return bool(derived) and derived[-1] == conclusion
