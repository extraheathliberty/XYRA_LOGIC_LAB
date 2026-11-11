"""Governed offline wrapper. Trust is evaluated before nonce consumption.

Policy references are operator-supplied and not independently checked against
Committee records. This is a simulation adapter, not live admission.
"""
from dataclasses import dataclass
from xyra_logic.issuer_trust import IssuerTrustRegistry
from xyra_logic.durable_replay import DurableReplayGuard
from xyra_logic.verified_adapter import assess_verified_request,VerifiedAdvisory

def assess_governed_request(consumer,premises,proposition,envelopes,sources,
                            signed_request,keyring,guard,registry,now):
    if not isinstance(registry,IssuerTrustRegistry) or not isinstance(guard,DurableReplayGuard):
        return VerifiedAdvisory("REJECT","governance_components_missing",None,False)
    if signed_request is None or not isinstance(getattr(signed_request,"issuer",None),str):
        return VerifiedAdvisory("REJECT","invalid_request_issuer",None,False)
    allowed,reason=registry.authorize(signed_request.issuer,consumer,now)
    if not allowed:
        return VerifiedAdvisory("REJECT",reason,None,False)
    for envelope in envelopes:
        allowed,reason=registry.authorize(getattr(envelope,"issuer",None),consumer,now)
        if not allowed:
            return VerifiedAdvisory("REJECT","evidence_"+reason,None,False)
    # Reuse verified adapter's source and request bindings, and atomic guard.
    # Its guard check is duck-typed here via a narrowly scoped facade.
    return assess_verified_request(consumer,premises,proposition,envelopes,sources,
                                   signed_request,keyring,guard,now)
