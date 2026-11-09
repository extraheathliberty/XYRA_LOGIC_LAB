"""Finite propositional logic with explicit consistency and countermodels.

This module is deterministic, dependency-free, and does not invoke AI models,
Executive ballots, runtime admission, or institutional authority.
"""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Atom:
    name: str

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Atom name must be a nonempty string")


@dataclass(frozen=True)
class Not:
    operand: object


@dataclass(frozen=True)
class And:
    left: object
    right: object


@dataclass(frozen=True)
class Or:
    left: object
    right: object


@dataclass(frozen=True)
class Implies:
    left: object
    right: object


@dataclass(frozen=True)
class Iff:
    left: object
    right: object


def variables(formula):
    if isinstance(formula, Atom):
        return frozenset((formula.name,))
    if isinstance(formula, Not):
        return variables(formula.operand)
    if isinstance(formula, (And, Or, Implies, Iff)):
        return variables(formula.left) | variables(formula.right)
    raise TypeError("Unsupported formula type: " + type(formula).__name__)


def evaluate(formula, assignment):
    if isinstance(formula, Atom):
        return bool(assignment[formula.name])
    if isinstance(formula, Not):
        return not evaluate(formula.operand, assignment)
    if isinstance(formula, And):
        return evaluate(formula.left, assignment) and evaluate(formula.right, assignment)
    if isinstance(formula, Or):
        return evaluate(formula.left, assignment) or evaluate(formula.right, assignment)
    if isinstance(formula, Implies):
        return not evaluate(formula.left, assignment) or evaluate(formula.right, assignment)
    if isinstance(formula, Iff):
        return evaluate(formula.left, assignment) == evaluate(formula.right, assignment)
    raise TypeError("Unsupported formula type: " + type(formula).__name__)


def assignments(formulas, max_atoms=16):
    """Enumerate assignments in stable alphabetical order; cap exponential work."""
    names = sorted(set().union(*(variables(f) for f in formulas)))
    if len(names) > max_atoms:
        raise ValueError("Atom limit exceeded; exhaustive evaluation refused")
    for values in product((False, True), repeat=len(names)):
        yield dict(zip(names, values))


def models(formulas, max_atoms=16):
    """All satisfying assignments for a conjunction of formulas."""
    formulas = tuple(formulas)
    return [a for a in assignments(formulas, max_atoms) if all(evaluate(f, a) for f in formulas)]


def satisfiable(formulas, max_atoms=16):
    return bool(models(formulas, max_atoms))


def countermodels(premises, conclusion, max_atoms=16):
    """Models satisfying premises while falsifying conclusion."""
    premises = tuple(premises)
    return [a for a in assignments(premises + (conclusion,), max_atoms)
            if all(evaluate(p, a) for p in premises) and not evaluate(conclusion, a)]


def analyze(premises, conclusion, max_atoms=16):
    """Separate logical entailment from premise consistency.

    In classical logic, inconsistent premises entail every conclusion
    vacuously. Such a result is marked explicitly and must not be
    interpreted as substantive proof.
    """
    premises = tuple(premises)
    premise_models = models(premises, max_atoms)
    counterexamples = countermodels(premises, conclusion, max_atoms)
    return {
        "premises_consistent": bool(premise_models),
        "entails": not bool(counterexamples),
        "vacuous": not bool(premise_models),
        "countermodels": counterexamples,
        "premise_model_count": len(premise_models),
    }


def minimal_inconsistent_subset(premises, max_atoms=16):
    """Return a deletion-minimal inconsistent subset, or empty tuple.

    This is subset-minimal, not guaranteed minimum-cardinality. Original
    premise order is preserved. The same atom cap applies to every check.
    """
    remaining = list(premises)
    if satisfiable(remaining, max_atoms):
        return ()
    index = 0
    while index < len(remaining):
        candidate = remaining[:index] + remaining[index + 1:]
        if not satisfiable(candidate, max_atoms):
            remaining = candidate
        else:
            index += 1
    return tuple(remaining)


def diagnose(premises, conclusion, max_atoms=16):
    """Return entailment analysis with an explicit inconsistency witness."""
    premises = tuple(premises)
    result = analyze(premises, conclusion, max_atoms)
    result["inconsistent_subset"] = minimal_inconsistent_subset(premises, max_atoms)
    return result
