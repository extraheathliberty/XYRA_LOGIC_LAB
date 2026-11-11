"""Offline source-byte verification for signed evidence envelopes.

The source is caller-supplied bytes, not fetched. Hash agreement and keyed
integrity do not establish factual truth or institutional authority.
"""
import hashlib
from dataclasses import dataclass
from xyra_logic.evidence_envelope import verify_evidence

MAX_SOURCE_BYTES=4*1024*1024

@dataclass(frozen=True)
class SourceVerification:
    verified: bool
    reason: str
    source_sha256: str | None

def verify_source_bytes(envelope,source,keyring):
    if not isinstance(source,bytes):
        return SourceVerification(False,"source_not_bytes",None)
    if len(source)>MAX_SOURCE_BYTES:
        return SourceVerification(False,"source_budget_exceeded",None)
    digest=hashlib.sha256(source).hexdigest()
    if not verify_evidence(envelope,keyring):
        return SourceVerification(False,"envelope_authentication_failed",digest)
    if digest!=envelope.source_digest:
        return SourceVerification(False,"source_digest_mismatch",digest)
    return SourceVerification(True,"signed_digest_matches_source_bytes",digest)
