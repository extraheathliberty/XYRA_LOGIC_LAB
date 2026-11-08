"""Offline evidence integrity and issuer authentication using keyed HMAC.

This verifies possession of an explicitly provisioned shared key, NOT the
truth of a claim, institutional authority, or independent source provenance.
No keys are stored in records; no network or command execution.
"""
from dataclasses import dataclass
import hashlib
import hmac
import json
from xyra_logic.proof_certificate import encode_formula

SCHEMA="xyra-evidence-envelope-v1"
MAX_PAYLOAD_BYTES=65536

@dataclass(frozen=True)
class EvidenceEnvelope:
    evidence_id: str
    issuer: str
    proposition: object
    source_digest: str
    issued_at: str
    signature: str

def _payload(evidence_id,issuer,proposition,source_digest,issued_at):
    if any(not isinstance(x,str) or not x or len(x)>256 for x in (evidence_id,issuer,issued_at)):
        raise ValueError("invalid evidence metadata")
    if not isinstance(source_digest,str) or len(source_digest)!=64 or any(c not in "0123456789abcdef" for c in source_digest):
        raise ValueError("invalid source digest")
    data=json.dumps({"schema":SCHEMA,"evidence_id":evidence_id,"issuer":issuer,
        "proposition":encode_formula(proposition),"source_digest":source_digest,
        "issued_at":issued_at},sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()
    if len(data)>MAX_PAYLOAD_BYTES:
        raise ValueError("evidence payload too large")
    return data

def sign_evidence(evidence_id,issuer,proposition,source_digest,issued_at,key):
    if not isinstance(key,bytes) or len(key)<32:
        raise ValueError("key must be at least 32 bytes")
    data=_payload(evidence_id,issuer,proposition,source_digest,issued_at)
    signature=hmac.new(key,data,hashlib.sha256).hexdigest()
    return EvidenceEnvelope(evidence_id,issuer,proposition,source_digest,issued_at,signature)

def verify_evidence(envelope,keyring):
    if not isinstance(envelope,EvidenceEnvelope) or not isinstance(keyring,dict):
        return False
    try:
        key=keyring.get(envelope.issuer)
        if not isinstance(key,bytes) or len(key)<32:
            return False
        data=_payload(envelope.evidence_id,envelope.issuer,envelope.proposition,
                      envelope.source_digest,envelope.issued_at)
        if not isinstance(envelope.signature,str) or len(envelope.signature)!=64:
            return False
        expected=hmac.new(key,data,hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected,envelope.signature)
    except (ValueError,TypeError,AttributeError):
        return False
