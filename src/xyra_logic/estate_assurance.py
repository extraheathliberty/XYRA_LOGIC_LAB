"""Read-only, versioned estate assurance contract.

Caller labels are descriptive, never authentication. The adapter returns
advisory mathematical assessments only, with no side effects or authority.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from xyra_logic.proof_certificate import encode_formula
from xyra_logic.reasoning_assessment import assess_reasoning
from xyra_logic.decision_gate import gate_proposition

SCHEMA="xyra-logic-assurance-v1"
CONSUMERS=frozenset({"AI_SULM","AUTOMATION","SANDBOX_FOUNDARY","PIPINGS","LOGIC","SUBSYSTEM"})
MAX_EVIDENCE_IDS=64

@dataclass(frozen=True)
class AssuranceResponse:
    schema: str
    request_digest: str
    consumer: str
    verdict: str
    disposition: str
    premise_consistency: str
    countermodel: dict | None
    evidence_ids: tuple[str,...]
    action_authorized: bool
    authenticated: bool
    limitations: tuple[str,...]

def assess_estate_request(consumer, premises, proposition, evidence_ids=()):
    if consumer not in CONSUMERS:
        raise ValueError("unknown consumer category")
    premises=tuple(premises)
    evidence_ids=tuple(evidence_ids)
    if len(evidence_ids)>MAX_EVIDENCE_IDS or any(
        not isinstance(x,str) or not x or len(x)>256 for x in evidence_ids
    ):
        raise ValueError("invalid evidence identifiers")
    if len(set(evidence_ids))!=len(evidence_ids):
        raise ValueError("duplicate evidence identifiers")
    payload={"schema":SCHEMA,"consumer":consumer,
             "premises":[encode_formula(p) for p in premises],
             "proposition":encode_formula(proposition),"evidence_ids":list(evidence_ids)}
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    digest=sha256(canonical).hexdigest()
    assessment=assess_reasoning(premises,proposition)
    gate=gate_proposition(premises,proposition)
    return AssuranceResponse(SCHEMA,digest,consumer,assessment.verdict,
        gate.disposition,assessment.premise_consistency,assessment.countermodel,
        evidence_ids,False,False,
        ("evidence_identifiers_not_verified","premise_truth_not_verified",
         "consumer_label_not_authenticated","no_command_or_deployment_authority"))
