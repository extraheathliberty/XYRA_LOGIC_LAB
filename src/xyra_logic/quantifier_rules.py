"""Capture-avoiding substitution for finite first-order formula syntax.

Rejects substitutions that would capture a free variable. This is a
foundational component for sound quantifier inference, not a claim of
complete first-order theorem proving.
"""
from .first_order import (
    Variable, Constant, Predicate, Equals, FNot, FAnd, FOr,
    FImplies, ForAll, Exists,
)


class CaptureError(ValueError):
    pass


def free_variables(formula):
    if isinstance(formula, (Predicate, Equals)):
        terms = formula.terms if isinstance(formula, Predicate) else (formula.left, formula.right)
        return frozenset(t.name for t in terms if isinstance(t, Variable))
    if isinstance(formula, FNot):
        return free_variables(formula.operand)
    if isinstance(formula, (FAnd, FOr, FImplies)):
        return free_variables(formula.left) | free_variables(formula.right)
    if isinstance(formula, (ForAll, Exists)):
        return free_variables(formula.body) - {formula.variable.name}
    raise TypeError("Unsupported first-order formula")


def substitute(formula, variable, replacement):
    """Substitute free occurrences; reject any variable capture."""
    if not isinstance(variable, Variable) or not isinstance(replacement, (Variable, Constant)):
        raise TypeError("Expected Variable binder and Variable/Constant replacement")

    def term(t):
        if not isinstance(t, (Variable, Constant)):
            raise TypeError("Unsupported term")
        return replacement if t == variable else t

    def walk(f):
        if isinstance(f, Predicate):
            return Predicate(f.name, tuple(term(t) for t in f.terms))
        if isinstance(f, Equals):
            return Equals(term(f.left), term(f.right))
        if isinstance(f, FNot):
            return FNot(walk(f.operand))
        if isinstance(f, (FAnd, FOr, FImplies)):
            return type(f)(walk(f.left), walk(f.right))
        if isinstance(f, (ForAll, Exists)):
            if f.variable == variable:
                return f
            if (isinstance(replacement, Variable) and
                    f.variable == replacement and
                    variable.name in free_variables(f.body)):
                raise CaptureError("Substitution would capture free variable")
            return type(f)(f.variable, walk(f.body))
        raise TypeError("Unsupported first-order formula")
    return walk(formula)


def universal_instance(formula, term):
    if not isinstance(formula, ForAll):
        raise TypeError("Universal instantiation requires ForAll")
    return substitute(formula.body, formula.variable, term)


def existential_witness(formula, term):
    if not isinstance(formula, Exists):
        raise TypeError("Existential witness requires Exists")
    return substitute(formula.body, formula.variable, term)
