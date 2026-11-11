"""Offline combined assurance gate: source bytes + signed request + replay guard.

No live transport, no persistent nonce store, no issuer authorization policy,
and no permission to issue commands. Suitable only for bounded development.
"""
from dataclasses import dataclass
import hashlib
import json
from xyra_logic.estate_assurance import assess_estate_request,CONSUMERS
from xyra_logic.source_verification import verify_source_bytes
from xyra_logic.replay_guard import ReplayGuard,SignedRequest
from xyra_logic.durable_replay import DurableReplayGuard

@dataclass(frozen=True)
class VerifiedAdvisory:
    status: str
    reason: str
    assurance: object | None
    action_authorized: bool

def bound_request_digest(assurance_digest,envelopes):
    """Bind request authentication to the exact signed evidence envelopes."""
    payload={"assurance_digest":assurance_digest,
             "envelopes":[{"id":e.evidence_id,"issuer":e.issuer,
                           "source_digest":e.source_digest,"signature":e.signature}
                          for e in envelopes]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def assess_verified_request(consumer,premises,proposition,envelopes,sources,
                            signed_request,keyring,replay_guard,now):
    if consumer not in CONSUMERS:
        return VerifiedAdvisory("REJECT","unknown_consumer",None,False)
    premises=tuple(premises)
    envelopes=tuple(envelopes)
    sources=tuple(sources)
    if len(premises)!=len(envelopes) or len(envelopes)!=len(sources) or len(premises)>64:
        return VerifiedAdvisory("REJECT","evidence_cardinality",None,False)
    ids=set()
    for p,e,source in zip(premises,envelopes,sources):
        verification=verify_source_bytes(e,source,keyring)
        if not verification.verified:
            return VerifiedAdvisory("REJECT",verification.reason,None,False)
        if e.proposition!=p:
            return VerifiedAdvisory("REJECT","proposition_mismatch",None,False)
        if e.evidence_id in ids:
            return VerifiedAdvisory("REJECT","duplicate_evidence",None,False)
        ids.add(e.evidence_id)
    advisory=assess_estate_request(consumer,premises,proposition,
                                  tuple(e.evidence_id for e in envelopes))
    if not isinstance(signed_request,SignedRequest) or signed_request.request_digest!=bound_request_digest(advisory.request_digest,envelopes):
        return VerifiedAdvisory("REJECT","request_digest_mismatch",None,False)
    if not isinstance(replay_guard,(ReplayGuard,DurableReplayGuard)):
        return VerifiedAdvisory("REJECT","invalid_replay_guard",None,False)
    accepted,reason=replay_guard.verify_once(signed_request,keyring,now)
    if not accepted:
        return VerifiedAdvisory("REJECT",reason,None,False)
    return VerifiedAdvisory("ADVISORY_ONLY","integrity_verified_truth_and_authority_unverified",
                            advisory,False)
