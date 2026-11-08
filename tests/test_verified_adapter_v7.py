import hashlib
import unittest
from datetime import datetime,timezone
from xyra_logic.formal_core import Var,Not
from xyra_logic.evidence_envelope import sign_evidence
from xyra_logic.estate_assurance import assess_estate_request
from xyra_logic.replay_guard import sign_request,ReplayGuard
from xyra_logic.verified_adapter import assess_verified_request
P,Q=Var("P"),Var("Q")
K=b"k"*32
NOW=datetime(2026,11,8,14,tzinfo=timezone.utc)
STAMP="2026-11-08T14:00:00Z"
def fixture(consumer="LOGIC",p=P,conclusion=P,source=b"source",nonce="n1"):
 e=sign_evidence("e1","issuer",p,hashlib.sha256(source).hexdigest(),STAMP,K)
 digest=assess_estate_request(consumer,[p],conclusion,("e1",)).request_digest
 req=sign_request("issuer",nonce,STAMP,digest,K)
 return e,req
class TestVerifiedAdapter(unittest.TestCase):
 def setUp(self):
  self.e,self.req=fixture()
  self.guard=ReplayGuard()
 def call(self,envelopes=None,sources=None,request=None,consumer="LOGIC",premises=None,conclusion=P):
  return assess_verified_request(consumer,[P] if premises is None else premises,conclusion,
    [self.e] if envelopes is None else envelopes,[b"source"] if sources is None else sources,
    self.req if request is None else request,{"issuer":K},self.guard,NOW)
 def test_success_advisory_only(self):
  r=self.call()
  self.assertEqual(r.status,"ADVISORY_ONLY")
  self.assertEqual(r.assurance.verdict,"SUPPORTED")
  self.assertFalse(r.action_authorized)
 def test_replay_rejected(self):
  self.assertEqual(self.call().status,"ADVISORY_ONLY")
  self.assertEqual(self.call().reason,"replayed_nonce")
 def test_source_tamper(self):
  self.assertEqual(self.call(sources=[b"changed"]).reason,"source_digest_mismatch")
 def test_missing_source(self):
  self.assertEqual(self.call(sources=[]).reason,"evidence_cardinality")
 def test_missing_envelope(self):
  self.assertEqual(self.call(envelopes=[]).reason,"evidence_cardinality")
 def test_wrong_premise(self):
  self.assertEqual(self.call(premises=[Q]).reason,"proposition_mismatch")
 def test_wrong_conclusion_digest(self):
  self.assertEqual(self.call(conclusion=Q).reason,"request_digest_mismatch")
 def test_wrong_consumer(self):
  self.assertEqual(self.call(consumer="AUTOMATION").reason,"request_digest_mismatch")
 def test_unknown_consumer(self):
  self.assertEqual(self.call(consumer="COMMAND").reason,"unknown_consumer")
 def test_duplicate_evidence(self):
  self.assertEqual(self.call(premises=[P,P],envelopes=[self.e,self.e],sources=[b"source",b"source"]).reason,"duplicate_evidence")
 def test_no_authority_after_success(self):
  self.assertFalse(self.call().assurance.action_authorized)
 def test_bad_source_does_not_consume_nonce(self):
  self.assertEqual(self.call(sources=[b"changed"]).status,"REJECT")
  self.assertEqual(self.call().status,"ADVISORY_ONLY")
 def test_invalid_replay_guard(self):
  result=assess_verified_request("LOGIC",[P],P,[self.e],[b"source"],self.req,{"issuer":K},None,NOW)
  self.assertEqual(result.reason,"invalid_replay_guard")
 def test_unverified_truth_limitation(self):
  self.assertIn("premise_truth_not_verified",self.call().assurance.limitations)
if __name__=="__main__":
 unittest.main()
