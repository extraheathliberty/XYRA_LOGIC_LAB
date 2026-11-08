"""Durable atomic nonce admission using SQLite uniqueness and transactions.

Single SQLite database file shared by cooperating processes. Does not
establish distributed multi-host consistency, clock trust or issuer authority.
"""
import sqlite3
from datetime import datetime,timezone
from xyra_logic.replay_guard import SignedRequest,ReplayGuard,MAX_WINDOW_SECONDS,_timestamp,_payload
import hashlib,hmac

class DurableReplayGuard:
    def __init__(self,path,max_entries=100000):
        if not isinstance(path,str) or not path or not isinstance(max_entries,int) or max_entries<1:
            raise ValueError("invalid replay store configuration")
        self.path=path
        self.max_entries=max_entries
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS admitted_nonce (issuer TEXT NOT NULL, nonce TEXT NOT NULL, admitted_at TEXT NOT NULL, PRIMARY KEY(issuer,nonce))")
    def _connect(self):
        db=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        db.execute("PRAGMA busy_timeout=10000")
        return db
    def verify_once(self,request,keyring,now):
        if not isinstance(request,SignedRequest) or not isinstance(keyring,dict):
            return False,"invalid_request"
        try:
            if not isinstance(now,datetime) or now.tzinfo is None:
                return False,"invalid_clock"
            now=now.astimezone(timezone.utc)
            issued=_timestamp(request.issued_at)
            payload=_payload(request.issuer,request.nonce,request.issued_at,request.request_digest)
            key=keyring.get(request.issuer)
            if not isinstance(key,bytes) or len(key)<32:
                return False,"unknown_issuer"
            if not isinstance(request.signature,str) or len(request.signature)!=64:
                return False,"invalid_signature"
            if not hmac.compare_digest(hmac.new(key,payload,hashlib.sha256).hexdigest(),request.signature):
                return False,"invalid_signature"
            if abs((now-issued).total_seconds())>MAX_WINDOW_SECONDS:
                return False,"outside_time_window"
            with self._connect() as db:
                try:
                    db.execute("BEGIN IMMEDIATE")
                    existing=db.execute("SELECT 1 FROM admitted_nonce WHERE issuer=? AND nonce=?", (request.issuer,request.nonce)).fetchone()
                    if existing:
                        db.execute("ROLLBACK")
                        return False,"replayed_nonce"
                    count=db.execute("SELECT COUNT(*) FROM admitted_nonce").fetchone()[0]
                    if count>=self.max_entries:
                        db.execute("ROLLBACK")
                        return False,"replay_registry_full"
                    db.execute("INSERT INTO admitted_nonce(issuer,nonce,admitted_at) VALUES (?,?,?)",
                               (request.issuer,request.nonce,now.isoformat()))
                    db.execute("COMMIT")
                except sqlite3.IntegrityError:
                    db.execute("ROLLBACK")
                    return False,"replayed_nonce"
                except Exception:
                    db.execute("ROLLBACK")
                    raise
            return True,"accepted_once"
        except (ValueError,TypeError,OverflowError,sqlite3.Error):
            return False,"store_or_request_failure"
