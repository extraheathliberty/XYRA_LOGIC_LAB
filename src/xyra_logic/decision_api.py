"""Bounded semantic decision interface with explicit inconclusive status.

No resource-exhaustion condition may be interpreted as VALID or INVALID.
"""
from dataclasses import dataclass
from xyra_logic.structural_audit import inspect_formula
from xyra_logic.bitset_oracle import oracle_entails,MAX_ORACLE_VARIABLES

@dataclass(frozen=True)
class Decision:
    status: str
    witness: dict | None
    variables: int
    method: str
    reason: str

def decide_entailment(premises, conclusion):
    premises=tuple(premises)
    names=set()
    for formula in (*premises,conclusion):
        names.update(inspect_formula(formula))
    if len(names)>MAX_ORACLE_VARIABLES:
        return Decision("INCONCLUSIVE",None,len(names),"bitset-exhaustive","variable_budget_exceeded")
    result,witness=oracle_entails(premises,conclusion)
    return Decision("VALID" if result else "INVALID",witness,len(names),"bitset-exhaustive",
                    "no_countermodel" if result else "countermodel_found")
