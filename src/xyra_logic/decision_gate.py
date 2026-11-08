"""A deterministic gate for *proposition* decisions, not Executive authority.

The caller supplies a proposition and premises. No free-form natural language
is parsed and no mandate, appointment or operational action is authorized.
"""
from dataclasses import dataclass
from xyra_logic.reasoning_assessment import assess_reasoning

@dataclass(frozen=True)
class DecisionGate:
    disposition: str
    mathematical_verdict: str
    action_authorized: bool
    rationale: str

def gate_proposition(premises, proposition):
    assessment=assess_reasoning(premises,proposition)
    mapping={
        "SUPPORTED":("MATHEMATICALLY_SUPPORTED","premises_entail_proposition"),
        "REFUTED":("REJECT_PROPOSITION","premises_entail_negation"),
        "UNDETERMINED":("REQUEST_EVIDENCE","multiple_consistent_outcomes"),
        "BLOCKED_CONTRADICTION":("RECONCILE_PREMISES","inconsistent_evidence"),
        "ABSTAIN":("ESCALATE_LIMIT","resource_limit"),
    }
    disposition,reason=mapping[assessment.verdict]
    return DecisionGate(disposition,assessment.verdict,False,reason)
