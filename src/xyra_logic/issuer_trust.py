"""Explicit issuer trust policy with deny-by-default scope and revocation.

Trust records are supplied by an external authorized governance process.
This code cannot appoint issuers, infer Committee approval or grant commands.
"""
from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass(frozen=True)
class IssuerPolicy:
    issuer: str
    allowed_consumers: frozenset[str]
    not_before: datetime
    expires_at: datetime
    revoked: bool=False
    authority_reference: str=""

class IssuerTrustRegistry:
    def __init__(self,policies=()):
        policies=tuple(policies)
        if any(not isinstance(p,IssuerPolicy) for p in policies):
            raise ValueError("invalid issuer policy")
        if len({p.issuer for p in policies})!=len(policies):
            raise ValueError("duplicate issuer")
        self._policies={p.issuer:p for p in policies}
    def authorize(self,issuer,consumer,now):
        p=self._policies.get(issuer)
        if p is None:
            return False,"issuer_not_registered"
        if p.revoked:
            return False,"issuer_revoked"
        if not p.authority_reference:
            return False,"missing_governance_reference"
        if not isinstance(now,datetime) or now.tzinfo is None:
            return False,"invalid_clock"
        if p.not_before.tzinfo is None or p.expires_at.tzinfo is None or p.not_before>=p.expires_at:
            return False,"invalid_policy_window"
        now=now.astimezone(timezone.utc)
        if now<p.not_before.astimezone(timezone.utc) or now>=p.expires_at.astimezone(timezone.utc):
            return False,"issuer_outside_policy_window"
        if consumer not in p.allowed_consumers:
            return False,"consumer_scope_denied"
        return True,"policy_permits_advisory_assessment"
