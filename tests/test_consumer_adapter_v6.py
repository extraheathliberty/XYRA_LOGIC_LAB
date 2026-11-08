import unittest
from dataclasses import replace
from xyra_logic.formal_core import Var,Not,Imp
from xyra_logic.evidence_envelope import sign_evidence
from xyra_logic.consumer_adapter import assess_signed_consumer
P,Q=Var("P"),Var("Q")
KEY=b"k"*32
D="a"*64
def env(eid,p):
 return sign_evidence(eid,"issuer",p,D,"2026-11-08T13:00:00Z",KEY)
class TestConsumerAdapter(unittest.TestCase):
 def call(self,premises,envelopes,consumer="AI_SULM",keyring=None,conclusion=Q):
  return assess_signed_consumer(consumer,premises,conclusion,envelopes,
                                {"issuer":KEY} if keyring is None else keyring)
 def test_supported_but_advisory(self):
  r=self.call([Imp(P,Q),P],[env("e1",Imp(P,Q)),env("e2",P)])
  self.assertEqual(r.status,"ADVISORY_ONLY")
  self.assertEqual(r.assurance.verdict,"SUPPORTED")
  self.assertFalse(r.action_authorized)
  self.assertFalse(r.assurance.authenticated)
 def test_missing_evidence(self):
  self.assertEqual(self.call([P],[]).reason,"missing_or_extra_evidence")
 def test_extra_evidence(self):
  self.assertEqual(self.call([],[env("e1",P)]).status,"REJECT")
 def test_wrong_key(self):
  self.assertEqual(self.call([P],[env("e1",P)],keyring={"issuer":b"x"*32}).reason,"evidence_authentication_failed")
 def test_tamper(self):
  tampered=replace(env("e1",P),proposition=Not(P))
  self.assertEqual(self.call([P],[tampered]).status,"REJECT")
 def test_premise_mismatch(self):
  self.assertEqual(self.call([P],[env("e1",Q)]).reason,"evidence_proposition_mismatch")
 def test_duplicate_evidence(self):
  self.assertEqual(self.call([P,P],[env("e1",P),env("e1",P)]).reason,"duplicate_evidence")
 def test_unknown_consumer(self):
  self.assertEqual(self.call([P],[env("e1",P)],consumer="COMMAND").status,"REJECT")
 def test_all_consumers_no_authority(self):
  for c in ("AI_SULM","AUTOMATION","SANDBOX_FOUNDARY","PIPINGS","LOGIC","SUBSYSTEM"):
   self.assertFalse(self.call([P],[env("e1",P)],consumer=c).action_authorized)
 def test_contradictory_signed_evidence(self):
  r=self.call([P,Not(P)],[env("e1",P),env("e2",Not(P))])
  self.assertEqual(r.assurance.verdict,"BLOCKED_CONTRADICTION")
 def test_underdetermined_signed_evidence(self):
  self.assertEqual(self.call([P],[env("e1",P)]).assurance.verdict,"UNDETERMINED")
 def test_zero_premises_tautology(self):
  from xyra_logic.formal_core import Or
  r=self.call([],[],conclusion=Or(P,Not(P)))
  self.assertEqual(r.assurance.verdict,"SUPPORTED")
 def test_signed_claim_does_not_authenticate_source_truth(self):
  r=self.call([P],[env("e1",P)])
  self.assertIn("premise_truth_not_verified",r.assurance.limitations)
 def test_rejected_has_no_assurance(self):
  self.assertIsNone(self.call([P],[]).assurance)
 def test_verified_envelope_count(self):
  r=self.call([P],[env("e1",P)])
  self.assertEqual(r.authenticated_envelopes,1)
if __name__=="__main__":
 unittest.main()
