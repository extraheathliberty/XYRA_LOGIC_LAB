"""Small deterministic natural-deduction proof checker.

Supports premise, conjunction introduction/elimination, implication
elimination (modus ponens), double-negation elimination, and
implication introduction via explicitly discharged assumptions.
All references must point to earlier steps. No AI model is invoked.
"""
from dataclasses import dataclass
from .formal import And, Implies, Not


@dataclass(frozen=True)
class ProofStep:
    formula: object
    rule: str
    references: tuple = ()
    assumption: int = -1


class ProofError(ValueError):
    pass


def verify_proof(premises, steps, conclusion):
    """Verify each inference with tracked open assumptions.

    Step indices are zero-based. Implication introduction requires
    'assumption' to identify an earlier assumption step, and a single
    reference to the consequent derivation. Discharge removes only the
    named assumption from that derivation's dependency set.
    """
    premises = tuple(premises)
    steps = tuple(steps)
    if not steps:
        raise ProofError("Proof must contain steps")
    dependencies = []
    for i, step in enumerate(steps):
        if not isinstance(step, ProofStep):
            raise ProofError("Invalid proof step")
        refs = step.references
        if not isinstance(refs, tuple) or any(type(k) is not int or k < 0 or k >= i for k in refs):
            raise ProofError("References must be earlier nonnegative integer indices")
        if step.rule == "premise":
            if refs or step.formula not in premises:
                raise ProofError("Invalid premise")
            deps = frozenset()
        elif step.rule == "assume":
            if refs:
                raise ProofError("Assumption cannot cite references")
            deps = frozenset((i,))
        elif step.rule == "and_intro":
            if len(refs) != 2 or step.formula != And(steps[refs[0]].formula, steps[refs[1]].formula):
                raise ProofError("Invalid conjunction introduction")
            deps = dependencies[refs[0]] | dependencies[refs[1]]
        elif step.rule in ("and_left", "and_right"):
            if len(refs) != 1 or not isinstance(steps[refs[0]].formula, And):
                raise ProofError("Invalid conjunction elimination")
            pair = steps[refs[0]].formula
            expected = pair.left if step.rule == "and_left" else pair.right
            if step.formula != expected:
                raise ProofError("Conjunction elimination conclusion mismatch")
            deps = dependencies[refs[0]]
        elif step.rule == "modus_ponens":
            if len(refs) != 2:
                raise ProofError("Modus ponens requires implication and antecedent")
            implication = steps[refs[0]].formula
            if not isinstance(implication, Implies) or implication.left != steps[refs[1]].formula or implication.right != step.formula:
                raise ProofError("Invalid modus ponens")
            deps = dependencies[refs[0]] | dependencies[refs[1]]
        elif step.rule == "double_negation":
            if len(refs) != 1 or steps[refs[0]].formula != Not(Not(step.formula)):
                raise ProofError("Invalid double-negation elimination")
            deps = dependencies[refs[0]]
        elif step.rule == "implies_intro":
            if len(refs) != 1 or type(step.assumption) is not int or step.assumption < 0 or step.assumption >= i:
                raise ProofError("Implication introduction needs earlier assumption")
            a = step.assumption
            if steps[a].rule != "assume" or a not in dependencies[refs[0]]:
                raise ProofError("Assumption not open in referenced derivation")
            if step.formula != Implies(steps[a].formula, steps[refs[0]].formula):
                raise ProofError("Implication introduction mismatch")
            deps = dependencies[refs[0]] - {a}
        else:
            raise ProofError("Unknown proof rule: " + str(step.rule))
        dependencies.append(frozenset(deps))
    if steps[-1].formula != conclusion:
        raise ProofError("Final conclusion mismatch")
    if dependencies[-1]:
        raise ProofError("Undischarged assumptions in final conclusion")
    return True
