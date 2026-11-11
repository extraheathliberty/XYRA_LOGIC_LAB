"""Versioned offline issuer key lifecycle. Keys never embedded in records.

Key enrollment and rotation require external approved trust governance.
"""
from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass(frozen=True)
class KeyRecord:
    issuer: str
    key_id: str
    secret: bytes
    valid_from: datetime
    valid_until: datetime
    revoked: bool=False

class KeyRegistry:
    def __init__(self,records=()):
        records=tuple(records)
        if len({(r.issuer,r.key_id) for r in records})!=len(records):
            raise ValueError("duplicate key identifier")
        for r in records:
            if not isinstance(r,KeyRecord) or not isinstance(r.secret,bytes) or len(r.secret)<32:
                raise ValueError("invalid key record")
            if r.valid_from.tzinfo is None or r.valid_until.tzinfo is None or r.valid_from>=r.valid_until:
                raise ValueError("invalid key window")
        self._records={(r.issuer,r.key_id):r for r in records}
    def resolve(self,issuer,key_id,now):
        r=self._records.get((issuer,key_id))
        if r is None:return None,"unknown_key"
        if r.revoked:return None,"revoked_key"
        if not isinstance(now,datetime) or now.tzinfo is None:return None,"invalid_clock"
        now=now.astimezone(timezone.utc)
        if not (r.valid_from.astimezone(timezone.utc)<=now<r.valid_until.astimezone(timezone.utc)):
            return None,"key_outside_validity"
        return r.secret,"key_valid"
