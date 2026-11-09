"""Finite-domain first-order semantics, separate from AI/Executive execution.

All quantification is over an explicitly supplied nonempty finite domain.
Predicate interpretations are supplied as finite sets of true tuples.
No unrestricted theorem-proving or infinite-domain completeness is claimed.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    name: str


@dataclass(frozen=True)
class Constant:
    value: object


@dataclass(frozen=True)
class Predicate:
    name: str
    terms: tuple


@dataclass(frozen=True)
class FNot:
    operand: object


@dataclass(frozen=True)
class FAnd:
    left: object
    right: object


@dataclass(frozen=True)
class FOr:
    left: object
    right: object


@dataclass(frozen=True)
class FImplies:
    left: object
    right: object


@dataclass(frozen=True)
class ForAll:
    variable: Variable
    body: object


@dataclass(frozen=True)
class Exists:
    variable: Variable
    body: object


@dataclass(frozen=True)
class Equals:
    left: object
    right: object


def interpret(formula, domain, predicates, environment=None):
    """Evaluate first-order formula under a finite interpretation.

    Predicate mapping: name -> set of tuples. Undefined predicates and
    unbound variables fail closed, rather than silently evaluating false.
    """
    domain = tuple(domain)
    if not domain:
        raise ValueError("Finite domain must be nonempty")
    if len(set(domain)) != len(domain):
        raise ValueError("Finite domain elements must be unique and hashable")
    environment = dict(environment or {})

    def term(t, env):
        if isinstance(t, Variable):
            if t.name not in env:
                raise ValueError("Unbound variable: " + t.name)
            return env[t.name]
        if isinstance(t, Constant):
            if t.value not in domain:
                raise ValueError("Constant outside finite domain")
            return t.value
        raise TypeError("Unsupported term")

    def walk(f, env):
        if isinstance(f, Predicate):
            if f.name not in predicates:
                raise ValueError("Undefined predicate: " + f.name)
            args = tuple(term(t, env) for t in f.terms)
            if any(x not in domain for x in args):
                raise ValueError("Predicate argument outside domain")
            return args in predicates[f.name]
        if isinstance(f, Equals):
            return term(f.left, env) == term(f.right, env)
        if isinstance(f, FNot):
            return not walk(f.operand, env)
        if isinstance(f, FAnd):
            return walk(f.left, env) and walk(f.right, env)
        if isinstance(f, FOr):
            return walk(f.left, env) or walk(f.right, env)
        if isinstance(f, FImplies):
            return not walk(f.left, env) or walk(f.right, env)
        if isinstance(f, (ForAll, Exists)):
            if not isinstance(f.variable, Variable):
                raise TypeError("Quantifier binder must be Variable")
            values = []
            for value in domain:
                scoped = dict(env)
                scoped[f.variable.name] = value
                values.append(walk(f.body, scoped))
            return all(values) if isinstance(f, ForAll) else any(values)
        raise TypeError("Unsupported first-order formula")

    return walk(formula, environment)
