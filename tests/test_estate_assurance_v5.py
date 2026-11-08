import unittest
from xyra_logic.formal_core import Var,Not,Imp
from xyra_logic.estate_assurance import assess_estate_request,CONSUMERS,SCHEMA
P,Q=Var("P"),Var("Q")
class TestEstateAssurance(unittest.TestCase):
 def test_all_six_consumers(self):
  self.assertEqual(len(CONSUMERS),6)
  for consumer in CONSUMERS:
   with self.subTest(consumer=consumer):
    r=assess_estate_request(consumer,[Imp(P,Q),P],Q,("evidence:001",))
    self.assertEqual(r.verdict,"SUPPORTED")
    self.assertFalse(r.action_authorized)
    self.assertFalse(r.authenticated)
    self.assertEqual(r.schema,SCHEMA)
 def test_underdetermined_automation(self):
  r=assess_estate_request("AUTOMATION",[P],Q)
  self.assertEqual(r.disposition,"REQUEST_EVIDENCE")
 def test_contradiction_foundary(self):
  r=assess_estate_request("SANDBOX_FOUNDARY",[P,Not(P)],Q)
  self.assertEqual(r.disposition,"RECONCILE_PREMISES")
 def test_rejected_proposition(self):
  r=assess_estate_request("AI_SULM",[Not(P)],P)
  self.assertEqual(r.disposition,"REJECT_PROPOSITION")
 def test_budget_limit_no_authority(self):
  r=assess_estate_request("SUBSYSTEM",[Var(f"X{i}") for i in range(11)],P)
  self.assertEqual(r.verdict,"ABSTAIN")
  self.assertFalse(r.action_authorized)
 def test_digest_deterministic(self):
  a=assess_estate_request("LOGIC",[P],P,("e1",))
  b=assess_estate_request("LOGIC",[P],P,("e1",))
  self.assertEqual(a.request_digest,b.request_digest)
 def test_digest_binds_evidence_ids(self):
  a=assess_estate_request("LOGIC",[P],P,("e1",))
  b=assess_estate_request("LOGIC",[P],P,("e2",))
  self.assertNotEqual(a.request_digest,b.request_digest)
 def test_digest_binds_consumer(self):
  a=assess_estate_request("LOGIC",[P],P)
  b=assess_estate_request("PIPINGS",[P],P)
  self.assertNotEqual(a.request_digest,b.request_digest)
 def test_digest_binds_proposition(self):
  a=assess_estate_request("LOGIC",[P],P)
  b=assess_estate_request("LOGIC",[P],Q)
  self.assertNotEqual(a.request_digest,b.request_digest)
 def test_reject_unknown_consumer(self):
  with self.assertRaises(ValueError):
   assess_estate_request("CENTRAL_COMMAND",[P],P)
 def test_reject_duplicate_evidence(self):
  with self.assertRaises(ValueError):
   assess_estate_request("LOGIC",[P],P,("e1","e1"))
 def test_reject_empty_evidence(self):
  with self.assertRaises(ValueError):
   assess_estate_request("LOGIC",[P],P,("",))
 def test_reject_long_evidence(self):
  with self.assertRaises(ValueError):
   assess_estate_request("LOGIC",[P],P,("x"*257,))
 def test_reject_many_evidence(self):
  with self.assertRaises(ValueError):
   assess_estate_request("LOGIC",[P],P,tuple(str(i) for i in range(65)))
 def test_evidence_not_authenticated(self):
  r=assess_estate_request("PIPINGS",[P],P,("signed:claimed",))
  self.assertIn("evidence_identifiers_not_verified",r.limitations)
  self.assertFalse(r.authenticated)
 def test_caller_not_authenticated(self):
  r=assess_estate_request("AI_SULM",[P],P)
  self.assertIn("consumer_label_not_authenticated",r.limitations)
 def test_observation_not_command(self):
  r=assess_estate_request("PIPINGS",[Var("observed")],Var("command"))
  self.assertEqual(r.verdict,"UNDETERMINED")
  self.assertFalse(r.action_authorized)
 def test_approval_not_execution(self):
  r=assess_estate_request("AUTOMATION",[Var("approved")],Var("executed"))
  self.assertEqual(r.verdict,"UNDETERMINED")
 def test_pilot_not_production(self):
  r=assess_estate_request("SANDBOX_FOUNDARY",[Var("pilot")],Var("production"))
  self.assertEqual(r.verdict,"UNDETERMINED")
 def test_all_responses_noncommanding(self):
  for premise,conclusion in (([P],P),([P],Q),([Not(P)],P),([P,Not(P)],Q)):
   self.assertFalse(assess_estate_request("LOGIC",premise,conclusion).action_authorized)
if __name__=="__main__":
 unittest.main()
