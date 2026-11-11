"""Transactional append-only audit with externally exportable head checkpoints.

SQLite provides atomic appends for cooperating writers. The database owner
can still rewrite or delete history. Independent anchoring is NOT implemented.
"""
import hashlib
import json
import sqlite3
from xyra_logic.audit_chain import GENESIS,record_hash

class DurableAudit:
    def __init__(self,path):
        if not isinstance(path,str) or not path:
            raise ValueError("invalid audit path")
        self.path=path
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS audit (sequence INTEGER PRIMARY KEY, event TEXT NOT NULL, subject TEXT NOT NULL, previous_hash TEXT NOT NULL, record_hash TEXT NOT NULL)")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    def append(self,event,subject):
        if not isinstance(event,str) or not event or not isinstance(subject,str) or not subject:
            raise ValueError("invalid event")
        with self._connect() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                rows=db.execute("SELECT sequence,event,subject,previous_hash,record_hash FROM audit ORDER BY sequence").fetchall()
                self._validate(rows)
                seq=len(rows)+1
                prev=rows[-1][4] if rows else GENESIS
                digest=record_hash(seq,event,subject,prev)
                db.execute("INSERT INTO audit VALUES(?,?,?,?,?)",(seq,event,subject,prev,digest))
                db.execute("COMMIT")
                return seq,digest
            except Exception:
                db.execute("ROLLBACK")
                raise
    @staticmethod
    def _validate(rows):
        prev=GENESIS
        for i,(seq,event,subject,prior,digest) in enumerate(rows,1):
            if seq!=i or prior!=prev or digest!=record_hash(seq,event,subject,prior):
                raise ValueError("audit history invalid")
            prev=digest
    def checkpoint(self):
        with self._connect() as db:
            rows=db.execute("SELECT sequence,event,subject,previous_hash,record_hash FROM audit ORDER BY sequence").fetchall()
        self._validate(rows)
        return {"schema":"xyra-audit-head-v1","count":len(rows),
                "head":rows[-1][4] if rows else GENESIS}
    def verify_checkpoint(self,expected):
        actual=self.checkpoint()
        return isinstance(expected,dict) and actual==expected
