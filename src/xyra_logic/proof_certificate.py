"""Canonical, versioned proof certificate encoding with digest and replay.

SHA-256 provides content integrity, NOT authenticity or institutional authority.
"""
import hashlib
import json
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff,ProofStep,check_proof
from xyra_logic.structural_audit import inspect_formula

VERSION="xyra-proof-v1"
MAX_CERTIFICATE_BYTES=1048576

def encode_formula(f):
    inspect_formula(f)
    if isinstance(f,Var): return ["var",f.name]
    if isinstance(f,Not): return ["not",encode_formula(f.value)]
    for typ,tag in ((And,"and"),(Or,"or"),(Imp,"imp"),(Iff,"iff")):
        if isinstance(f,typ): return [tag,encode_formula(f.left),encode_formula(f.right)]
    raise ValueError("invalid formula")

def decode_formula(data):
    if not isinstance(data,list) or not data or not isinstance(data[0],str):
        raise ValueError("invalid encoded formula")
    tag=data[0]
    if tag=="var" and len(data)==2 and isinstance(data[1],str) and data[1]:
        return Var(data[1])
    if tag=="not" and len(data)==2:
        return Not(decode_formula(data[1]))
    constructors={"and":And,"or":Or,"imp":Imp,"iff":Iff}
    if tag in constructors and len(data)==3:
        return constructors[tag](decode_formula(data[1]),decode_formula(data[2]))
    raise ValueError("invalid formula tag/arity")

def canonical_bytes(premises,steps,conclusion):
    payload={"version":VERSION,"premises":[encode_formula(f) for f in premises],
             "steps":[{"formula":encode_formula(s.formula),"rule":s.rule,
                       "refs":list(s.refs)} for s in steps],
             "conclusion":encode_formula(conclusion)}
    encoded=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("utf-8")
    if len(encoded)>MAX_CERTIFICATE_BYTES:
        raise ValueError("certificate exceeds size bound")
    return encoded

def certificate_digest(data):
    if len(data)>MAX_CERTIFICATE_BYTES:
        raise ValueError("certificate exceeds size bound")
    return hashlib.sha256(data).hexdigest()

def replay_certificate(data, expected_digest):
    if not isinstance(data,bytes) or len(data)>MAX_CERTIFICATE_BYTES:
        raise ValueError("invalid certificate bytes")
    if not isinstance(expected_digest,str) or certificate_digest(data)!=expected_digest:
        raise ValueError("certificate digest mismatch")
    payload=json.loads(data)
    if not isinstance(payload,dict) or set(payload)!={"version","premises","steps","conclusion"} or payload["version"]!=VERSION:
        raise ValueError("unsupported certificate")
    premises=[decode_formula(f) for f in payload["premises"]]
    conclusion=decode_formula(payload["conclusion"])
    steps=[]
    for item in payload["steps"]:
        if not isinstance(item,dict) or set(item)!={"formula","rule","refs"}:
            raise ValueError("invalid proof step")
        if not isinstance(item["rule"],str) or not isinstance(item["refs"],list):
            raise ValueError("invalid step fields")
        steps.append(ProofStep(decode_formula(item["formula"]),item["rule"],tuple(item["refs"])))
    if canonical_bytes(premises,steps,conclusion)!=data:
        raise ValueError("noncanonical certificate")
    return check_proof(premises,steps,conclusion)
