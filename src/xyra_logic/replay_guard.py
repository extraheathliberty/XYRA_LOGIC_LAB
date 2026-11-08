"""Bounded offline anti-replay verification with injected clock.

Caller authentication and trust-root management are out of scope. The
in-memory nonce registry is process-local, non-durable, and not sufficient
for a distributed or restarted production service.
"""
from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
from hashlib import sha256
import hmac
import json

MAX_WINDOW_SECONDS=300

@dataclass(frozen=True)
class SignedRequest:
    issuer: str
    nonce: str
    issued_at: str
    request_digest: str
    signature: str

def _timestamp(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC Z")
    dt=datetime.fromisoformat(value.replace("Z","+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timezone required")
    return dt.astimezone(timezone.utc)

def _payload(issuer,nonce,issued_at,request_digest):
    if any(not isinstance(x,str) or not x or len(x)>256 for x in (issuer,nonce,issued_at)):
        raise ValueError("invalid request metadata")
    if not isinstance(request_digest,str) or len(request_digest)!=64 or any(c not in "0123456789abcdef" for c in request_digest):
        raise ValueError("invalid request digest")
    return json.dumps({"schema":"xyra-signed-request-v1","issuer":issuer,"nonce":nonce,
                       "issued_at":issued_at,"request_digest":request_digest},
                      sort_keys=True,separators=(",",":")).encode()

def sign_request(issuer,nonce,issued_at,request_digest,key):
    if not isinstance(key,bytes) or len(key)<32:
        raise ValueError("weak signing key")
    _timestamp(issued_at)
    data=_payload(issuer,nonce,issued_at,request_digest)
    return SignedRequest(issuer,nonce,issued_at,request_digest,
                         hmac.new(key,data,sha256).hexdigest())

class ReplayGuard:
    def __init__(self,max_entries=10000):
        if not isinstance(max_entries,int) or max_entries<1:
            raise ValueError("invalid replay capacity")
        self._seen={}
        self.max_entries=max_entries

    def verify_once(self,request,keyring,now):
        if not isinstance(request,SignedRequest) or not isinstance(keyring,dict):
            return False,"invalid_request"
        try:
            if not isinstance(now,datetime) or now.tzinfo is None:
                return False,"invalid_clock"
            now=now.astimezone(timezone.utc)
            issued=_timestamp(request.issued_at)
            data=_payload(request.issuer,request.nonce,request.issued_at,request.request_digest)
            key=keyring.get(request.issuer)
            if not isinstance(key,bytes) or len(key)<32:
                return False,"unknown_issuer"
            if not isinstance(request.signature,str) or len(request.signature)!=64:
                return False,"invalid_signature"
            expected=hmac.new(key,data,sha256).hexdigest()
            if not hmac.compare_digest(expected,request.signature):
                return False,"invalid_signature"
            if abs((now-issued).total_seconds())>MAX_WINDOW_SECONDS:
                return False,"outside_time_window"
            identity=(request.issuer,request.nonce)
            if identity in self._seen:
                return False,"replayed_nonce"
            # Fail closed when the capacity is exhausted: do not evict live nonces.
            if len(self._seen)>=self.max_entries:
                return False,"replay_registry_full"
            self._seen[identity]=now
            return True,"accepted_once"
        except (ValueError,TypeError,OverflowError):
            return False,"malformed_request"
