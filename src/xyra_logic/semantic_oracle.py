"""Independent bounded semantic oracle for propositional proof certificates.

This oracle deliberately implements truth semantics separately from
xyra_logic.formal.evaluate, reducing shared implementation risk.
It does not constitute independent institutional assurance.
"""
from itertools import product
from .formal import Atom, Not, And, Or, Implies, Iff
from .proof import verify_proof


def oracle_evaluate(formula, assignment):
    if isinstance(formula, Atom):
        return assignment[formula.name] is True
    if isinstance(formula, Not):
        return oracle_evaluate(formula.operand, assignment) is False
    if isinstance(formula, And):
        return all((oracle_evaluate(formula.left, assignment),
                    oracle_evaluate(formula.right, assignment)))
    if isinstance(formula, Or):
        return any((oracle_evaluate(formula.left, assignment),
                    oracle_evaluate(formula.right, assignment)))
    if isinstance(formula, Implies):
        return not (oracle_evaluate(formula.left, assignment) and
                    not oracle_evaluate(formula.right, assignment))
    if isinstance(formula, Iff):
        left = oracle_evaluate(formula.left, assignment)
        right = oracle_evaluate(formula.right, assignment)
        return (left and right) or (not left and not right)
    raise TypeError("Unknown formula")


def oracle_atoms(formula):
    if isinstance(formula, Atom):
        return {formula.name}
    if isinstance(formula, Not):
        return oracle_atoms(formula.operand)
    if isinstance(formula, (And, Or, Implies, Iff)):
        return oracle_atoms(formula.left) | oracle_atoms(formula.right)
    raise TypeError("Unknown formula")


def oracle_countermodels(premises, conclusion, max_atoms=12):
    premises = tuple(premises)
    names = sorted(set().union(*(oracle_atoms(f) for f in premises + (conclusion,))))
    if len(names) > max_atoms:
        raise ValueError("Oracle atom limit exceeded")
    witnesses = []
    for values in product((False, True), repeat=len(names)):
        assignment = dict(zip(names, values))
        if all(oracle_evaluate(p, assignment) for p in premises) and not oracle_evaluate(conclusion, assignment):
            witnesses.append(assignment)
    return witnesses


def check_certificate(premises, steps, conclusion, max_atoms=12):
    """Reject unsound certificates, retaining an explicit counterexample."""
    verify_proof(premises, steps, conclusion)
    counterexamples = oracle_countermodels(premises, conclusion, max_atoms)
    return {
        "proof_valid": True,
        "bounded_semantically_sound": not bool(counterexamples),
        "countermodels": counterexamples,
        "interpretations_exhausted": True,
        "atom_bound": max_atoms,
    }
