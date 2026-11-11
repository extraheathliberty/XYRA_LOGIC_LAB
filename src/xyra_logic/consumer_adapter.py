"""Offline consumer adapter with explicit evidence and trust boundaries.

All premises require matching authenticated envelopes. This does not check
source truth, source bytes, issuer authority, freshness, or replay. The
adapter is not an admission or command service.
"""
from dataclasses import dataclass
from xyra_logic.estate_assurance import assess_estate_request,CONSUMERS
from xyra_logic.evidence_envelope import verify_evidence

@dataclass(frozen=True)
class AdapterResult:
    status: str
    assurance: object | None
    authenticated_envelopes: int
    action_authorized: bool
    reason: str

def assess_signed_consumer(consumer,premises,proposition,envelopes,keyring):
    if consumer not in CONSUMERS:
        return AdapterResult("REJECT",None,0,False,"unknown_consumer")
    premises=tuple(premises)
    envelopes=tuple(envelopes)
    if len(envelopes)!=len(premises):
        return AdapterResult("REJECT",None,0,False,"missing_or_extra_evidence")
    if len(envelopes)>64:
        return AdapterResult("REJECT",None,0,False,"evidence_budget_exceeded")
    verified=0
    ids=set()
    for premise,env in zip(premises,envelopes):
        if not verify_evidence(env,keyring):
            return AdapterResult("REJECT",None,verified,False,"evidence_authentication_failed")
        if env.proposition!=premise:
            return AdapterResult("REJECT",None,verified,False,"evidence_proposition_mismatch")
        if env.evidence_id in ids:
            return AdapterResult("REJECT",None,verified,False,"duplicate_evidence")
        ids.add(env.evidence_id)
        verified+=1
    response=assess_estate_request(consumer,premises,proposition,
                                  tuple(env.evidence_id for env in envelopes))
    return AdapterResult("ADVISORY_ONLY",response,verified,False,
                         "issuer_key_verified_source_truth_and_authority_unverified")
