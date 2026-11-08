import json
import unittest
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff,ProofStep
from xyra_logic.proof_certificate import (
 encode_formula,decode_formula,canonical_bytes,certificate_digest,replay_certificate
)
P,Q=Var("P"),Var("Q")
PREMISES=[Imp(P,Q),P]
STEPS=[ProofStep(Imp(P,Q),"premise"),ProofStep(P,"premise"),ProofStep(Q,"imp_elim",(0,1))]

class TestProofCertificate(unittest.TestCase):
 def test_round_trip(self):
  data=canonical_bytes(PREMISES,STEPS,Q)
  self.assertTrue(replay_certificate(data,certificate_digest(data)))
 def test_deterministic_encoding(self):
  self.assertEqual(canonical_bytes(PREMISES,STEPS,Q),canonical_bytes(PREMISES,STEPS,Q))
 def test_tamper_detected(self):
  data=canonical_bytes(PREMISES,STEPS,Q)
  with self.assertRaises(ValueError):
   replay_certificate(data+b" ",certificate_digest(data))
 def test_wrong_digest_detected(self):
  data=canonical_bytes(PREMISES,STEPS,Q)
  with self.assertRaises(ValueError):
   replay_certificate(data,"0"*64)
 def test_wrong_rule_rejected(self):
  bad=[*STEPS[:2],ProofStep(Q,"magic",(0,1))]
  data=canonical_bytes(PREMISES,bad,Q)
  self.assertFalse(replay_certificate(data,certificate_digest(data)))
 def test_wrong_conclusion_rejected(self):
  data=canonical_bytes(PREMISES,STEPS,P)
  self.assertFalse(replay_certificate(data,certificate_digest(data)))
 def test_reject_noncanonical_whitespace(self):
  data=canonical_bytes(PREMISES,STEPS,Q)
  obj=json.loads(data)
  changed=json.dumps(obj,indent=2).encode()
  with self.assertRaises(ValueError):
   replay_certificate(changed,certificate_digest(changed))
 def test_reject_unsupported_version(self):
  data=canonical_bytes(PREMISES,STEPS,Q)
  obj=json.loads(data)
  obj["version"]="v999"
  changed=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
  with self.assertRaises(ValueError):
   replay_certificate(changed,certificate_digest(changed))
 def test_reject_extra_field(self):
  obj=json.loads(canonical_bytes(PREMISES,STEPS,Q))
  obj["authority"]="executive"
  changed=json.dumps(obj,sort_keys=True,separators=(",",":")).encode()
  with self.assertRaises(ValueError):
   replay_certificate(changed,certificate_digest(changed))
 def test_formula_round_trip_all_connectives(self):
  f=Iff(Imp(P,Q),Or(Not(P),And(P,Q)))
  self.assertEqual(decode_formula(encode_formula(f)),f)
 def test_invalid_formula_tag(self):
  with self.assertRaises(ValueError): decode_formula(["magic","P"])
 def test_invalid_formula_arity(self):
  with self.assertRaises(ValueError): decode_formula(["imp",["var","P"]])
 def test_invalid_var_name(self):
  with self.assertRaises(ValueError): decode_formula(["var",""])
 def test_invalid_certificate_bytes(self):
  with self.assertRaises(ValueError): replay_certificate("notbytes","0"*64)
 def test_empty_proof_rejected(self):
  data=canonical_bytes([P],[],P)
  self.assertFalse(replay_certificate(data,certificate_digest(data)))
if __name__=="__main__":
 unittest.main()
