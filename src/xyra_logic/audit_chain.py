"""Offline tamper-evident audit hash chain, not tamper-proof storage.

External anchoring and access-controlled append-only storage are required to
detect truncation or complete chain replacement.
"""
import hashlib,json
from dataclasses import dataclass

GENESIS="0"*64
@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    event: str
    subject: str
    previous_hash: str
    record_hash: str

def record_hash(sequence,event,subject,previous_hash):
    data=json.dumps({"sequence":sequence,"event":event,"subject":subject,
                     "previous_hash":previous_hash},sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(data).hexdigest()

def append_audit(records,event,subject):
    records=tuple(records)
    if not verify_chain(records):
        raise ValueError("invalid audit chain")
    if not isinstance(event,str) or not event or not isinstance(subject,str) or not subject:
        raise ValueError("invalid audit event")
    seq=len(records)+1
    previous=records[-1].record_hash if records else GENESIS
    return (*records,AuditRecord(seq,event,subject,previous,record_hash(seq,event,subject,previous)))

def verify_chain(records):
    previous=GENESIS
    for index,r in enumerate(records,1):
        if not isinstance(r,AuditRecord) or r.sequence!=index or r.previous_hash!=previous:
            return False
        if not isinstance(r.event,str) or not r.event or not isinstance(r.subject,str) or not r.subject:
            return False
        expected=record_hash(r.sequence,r.event,r.subject,r.previous_hash)
        if r.record_hash!=expected:
            return False
        previous=r.record_hash
    return True
