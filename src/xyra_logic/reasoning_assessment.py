"""Bounded decision diagnostics: validity is not decision readiness.

Separate contradictory evidence, unsupported conclusions, incomplete evidence,
and computational limits. This module is advisory mathematics, never authority.
"""
from dataclasses import dataclass
from xyra_logic.structural_audit import inspect_formula
from xyra_logic.bitset_oracle import oracle_mask,oracle_entails,MAX_ORACLE_VARIABLES

@dataclass(frozen=True)
class ReasoningAssessment:
    verdict: str
    entailment: str
    premise_consistency: str
    conclusion_possible: str
    countermodel: dict | None
    variables: int
    reason: str

def assess_reasoning(premises, conclusion):
    premises=tuple(premises)
    names=set()
    for f in (*premises,conclusion):
        names.update(inspect_formula(f))
    names=tuple(sorted(names))
    if len(names)>MAX_ORACLE_VARIABLES:
        return ReasoningAssessment("ABSTAIN","UNKNOWN","UNKNOWN","UNKNOWN",None,len(names),
                                   "resource_budget_exceeded")
    universe=(1<<(1<<len(names)))-1
    satisfying=universe
    for p in premises:
        satisfying &= oracle_mask(p,names)
    conclusion_mask=oracle_mask(conclusion,names)
    if satisfying==0:
        return ReasoningAssessment("BLOCKED_CONTRADICTION","VACUOUSLY_VALID","INCONSISTENT",
                                   "UNKNOWN",None,len(names),"premises_have_no_joint_model")
    possible=bool(satisfying & conclusion_mask)
    counter=satisfying & (universe^conclusion_mask)
    if not counter:
        return ReasoningAssessment("SUPPORTED","VALID","CONSISTENT","YES",None,len(names),
                                   "all_premise_models_support_conclusion")
    if not possible:
        _,witness=oracle_entails(premises,conclusion)
        return ReasoningAssessment("REFUTED","INVALID","CONSISTENT","NO",witness,len(names),
                                   "premises_entail_negation_of_conclusion")
    _,witness=oracle_entails(premises,conclusion)
    return ReasoningAssessment("UNDETERMINED","INVALID","CONSISTENT","YES",witness,len(names),
                               "premises_allow_both_conclusion_and_negation")
