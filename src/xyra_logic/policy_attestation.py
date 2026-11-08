"""Offline dual-attestor policy integrity, not Committee authority verification.

Attestor keys and approved identities MUST originate from an independent
governance process. Two HMACs prove two key possessions, not two humans.
"""
from dataclasses import dataclass
from datetime import timezone
import hashlib,hmac,json
from xyra_logic.issuer_trust import IssuerPolicy,IssuerTrustRegistry

@dataclass(frozen=True)
class PolicyAttestation:
    attestor: str
    policy_digest: str
    signature: str

def policy_digest(policy):
    if not isinstance(policy,IssuerPolicy):
        raise ValueError("invalid policy")
    payload={"issuer":policy.issuer,"consumers":sorted(policy.allowed_consumers),
             "not_before":policy.not_before.astimezone(timezone.utc).isoformat(),
             "expires_at":policy.expires_at.astimezone(timezone.utc).isoformat(),
             "revoked":policy.revoked,"authority_reference":policy.authority_reference}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def attest_policy(policy,attestor,key):
    if not isinstance(attestor,str) or not attestor or not isinstance(key,bytes) or len(key)<32:
        raise ValueError("invalid attestor")
    digest=policy_digest(policy)
    signature=hmac.new(key,("xyra-policy-v1:"+digest).encode(),hashlib.sha256).hexdigest()
    return PolicyAttestation(attestor,digest,signature)

def verify_attestations(policy,attestations,attestor_keys,required=2):
    if not isinstance(attestor_keys,dict) or not isinstance(required,int) or required<2:
        return False,"invalid_attestation_configuration"
    try:
        digest=policy_digest(policy)
        valid=set()
        for a in attestations:
            if not isinstance(a,PolicyAttestation) or a.attestor in valid or a.policy_digest!=digest:
                return False,"invalid_or_duplicate_attestation"
            key=attestor_keys.get(a.attestor)
            if not isinstance(key,bytes) or len(key)<32 or not isinstance(a.signature,str):
                return False,"unknown_attestor"
            expected=hmac.new(key,("xyra-policy-v1:"+digest).encode(),hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected,a.signature):
                return False,"invalid_attestation_signature"
            valid.add(a.attestor)
        return (True,"attestor_key_threshold_met") if len(valid)>=required else (False,"insufficient_attestations")
    except (ValueError,TypeError,AttributeError):
        return False,"malformed_attestation"

class AttestedIssuerTrustRegistry(IssuerTrustRegistry):
    def __init__(self,policies,attestations_by_issuer,attestor_keys,required=2):
        policies=tuple(policies)
        for policy in policies:
            ok,reason=verify_attestations(policy,attestations_by_issuer.get(policy.issuer,()),
                                          attestor_keys,required)
            if not ok:
                raise ValueError("policy not attested: "+reason)
        super().__init__(policies)
