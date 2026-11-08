"""Independent bounded semantic audit of proof certificates.

The audit enumerates every Boolean valuation for small proof contexts,
checks each line's truth preservation, and reports the first countermodel.
This is an assurance tool, not a complete theorem prover.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from xyra_logic.formal_core import variables, evaluate, check_proof

MAX_VARIABLES = 12
MAX_PROOF_STEPS = 2000

@dataclass(frozen=True)
class ProofAudit:
    accepted: bool
    semantically_sound: bool
    countermodel: dict | None
    reason: str

def audit_proof(premises, steps, conclusion):
    premises, steps = tuple(premises), tuple(steps)
    if len(steps) > MAX_PROOF_STEPS:
        return ProofAudit(False, False, None, "proof_step_budget_exceeded")
    formulas = list(premises) + [conclusion] + [s.formula for s in steps]
    names = sorted(set().union(*(variables(f) for f in formulas)))
    if len(names) > MAX_VARIABLES:
        return ProofAudit(False, False, None, "truth_assignment_budget_exceeded")
    accepted = check_proof(premises, steps, conclusion)
    for values in product((False,True),repeat=len(names)):
        env = dict(zip(names,values))
        if all(evaluate(p,env) for p in premises):
            if accepted and any(not evaluate(s.formula,env) for s in steps):
                return ProofAudit(True,False,env,"accepted_proof_contains_false_line")
            if not evaluate(conclusion,env):
                return ProofAudit(accepted,False,env,"conclusion_has_countermodel")
    return ProofAudit(accepted,True,None,"accepted_and_semantically_sound" if accepted else "not_accepted_by_restricted_calculus")
