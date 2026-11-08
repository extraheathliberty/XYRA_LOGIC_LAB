"""Cross-check accepted proof certificates with distinct bit-vector semantics.

This is bounded differential assurance, not a universal soundness theorem.
"""
from dataclasses import dataclass
from xyra_logic.formal_core import check_proof
from xyra_logic.bitset_oracle import oracle_entails,MAX_ORACLE_VARIABLES
from xyra_logic.structural_audit import inspect_formula

@dataclass(frozen=True)
class CrossCheck:
    status: str
    certificate_accepted: bool
    countermodel: dict | None
    reason: str

def crosscheck_proof(premises,steps,conclusion):
    premises,steps=tuple(premises),tuple(steps)
    names=set()
    for formula in (*premises,conclusion,*(s.formula for s in steps)):
        names.update(inspect_formula(formula))
    if len(names)>MAX_ORACLE_VARIABLES:
        return CrossCheck("INCONCLUSIVE",False,None,"oracle_budget_exceeded")
    if len(steps)>2000:
        return CrossCheck("INCONCLUSIVE",False,None,"proof_budget_exceeded")
    accepted=check_proof(premises,steps,conclusion)
    entails,witness=oracle_entails(premises,conclusion)
    if accepted and not entails:
        return CrossCheck("SOUNDNESS_VIOLATION",True,witness,"accepted_invalid_inference")
    if not accepted:
        return CrossCheck("NOT_ACCEPTED",False,witness,"certificate_rejected")
    return CrossCheck("BOUNDED_CROSSCHECK_PASS",True,None,"accepted_proof_entails_conclusion")
