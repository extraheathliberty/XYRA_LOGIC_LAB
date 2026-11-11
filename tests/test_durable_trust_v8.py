import hashlib
import os
import tempfile
import threading
import unittest
from datetime import datetime,timezone,timedelta
from xyra_logic.formal_core import Var
from xyra_logic.evidence_envelope import sign_evidence
from xyra_logic.estate_assurance import assess_estate_request
from xyra_logic.verified_adapter import bound_request_digest
from xyra_logic.replay_guard import sign_request
from xyra_logic.durable_replay import DurableReplayGuard
from xyra_logic.issuer_trust import IssuerPolicy,IssuerTrustRegistry
from xyra_logic.governed_adapter import assess_governed_request

P=Var("P")
K=b"k"*32
NOW=datetime(2026,11,8,14,tzinfo=timezone.utc)
STAMP="2026-11-08T14:00:00Z"
def policy(**kwargs):
 d=dict(issuer="issuer",allowed_consumers=frozenset({"LOGIC"}),
        not_before=NOW-timedelta(days=1),expires_at=NOW+timedelta(days=1),
        authority_reference="TEST-POLICY-ONLY")
 d.update(kwargs)
 return IssuerPolicy(**d)
class TestDurableReplay(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.path=os.path.join(self.tmp.name,"replay.sqlite3")
  self.guard=DurableReplayGuard(self.path)
  self.req=sign_request("issuer","n1",STAMP,"a"*64,K)
 def tearDown(self):
  self.tmp.cleanup()
 def test_accept_once(self):
  self.assertTrue(self.guard.verify_once(self.req,{"issuer":K},NOW)[0])
 def test_restart_replay_rejected(self):
  self.assertTrue(self.guard.verify_once(self.req,{"issuer":K},NOW)[0])
  self.assertEqual(DurableReplayGuard(self.path).verify_once(self.req,{"issuer":K},NOW)[1],"replayed_nonce")
 def test_parallel_exactly_one(self):
  outcomes=[]
  def worker():
   outcomes.append(DurableReplayGuard(self.path).verify_once(self.req,{"issuer":K},NOW)[0])
  threads=[threading.Thread(target=worker) for _ in range(8)]
  for t in threads:t.start()
  for t in threads:t.join()
  self.assertEqual(outcomes.count(True),1)
  self.assertEqual(outcomes.count(False),7)
 def test_invalid_signature_does_not_consume(self):
  self.assertFalse(self.guard.verify_once(self.req,{"issuer":b"x"*32},NOW)[0])
  self.assertTrue(self.guard.verify_once(self.req,{"issuer":K},NOW)[0])
 def test_expired_not_consumed(self):
  self.assertFalse(self.guard.verify_once(self.req,{"issuer":K},NOW+timedelta(hours=1))[0])
  self.assertTrue(self.guard.verify_once(self.req,{"issuer":K},NOW)[0])
 def test_capacity(self):
  g=DurableReplayGuard(self.path,max_entries=1)
  self.assertTrue(g.verify_once(self.req,{"issuer":K},NOW)[0])
  req2=sign_request("issuer","n2",STAMP,"a"*64,K)
  self.assertEqual(g.verify_once(req2,{"issuer":K},NOW)[1],"replay_registry_full")
 def test_bad_path(self):
  with self.assertRaises(ValueError): DurableReplayGuard("")
class TestIssuerTrust(unittest.TestCase):
 def test_allowed(self):
  self.assertTrue(IssuerTrustRegistry([policy()]).authorize("issuer","LOGIC",NOW)[0])
 def test_unregistered(self):
  self.assertEqual(IssuerTrustRegistry().authorize("issuer","LOGIC",NOW)[1],"issuer_not_registered")
 def test_revoked(self):
  self.assertEqual(IssuerTrustRegistry([policy(revoked=True)]).authorize("issuer","LOGIC",NOW)[1],"issuer_revoked")
 def test_scope(self):
  self.assertEqual(IssuerTrustRegistry([policy()]).authorize("issuer","AUTOMATION",NOW)[1],"consumer_scope_denied")
 def test_missing_governance_reference(self):
  self.assertEqual(IssuerTrustRegistry([policy(authority_reference="")]).authorize("issuer","LOGIC",NOW)[1],"missing_governance_reference")
 def test_expiry(self):
  self.assertEqual(IssuerTrustRegistry([policy()]).authorize("issuer","LOGIC",NOW+timedelta(days=2))[1],"issuer_outside_policy_window")
 def test_duplicate_policy(self):
  with self.assertRaises(ValueError): IssuerTrustRegistry([policy(),policy()])
class TestGovernedAdapter(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.guard=DurableReplayGuard(os.path.join(self.tmp.name,"db.sqlite3"))
  source=b"evidence"
  self.env=sign_evidence("e1","issuer",P,hashlib.sha256(source).hexdigest(),STAMP,K)
  digest=assess_estate_request("LOGIC",[P],P,("e1",)).request_digest
  self.req=sign_request("issuer","n1",STAMP,bound_request_digest(digest,[self.env]),K)
 def tearDown(self):self.tmp.cleanup()
 def call(self,registry):
  return assess_governed_request("LOGIC",[P],P,[self.env],[b"evidence"],
                                 self.req,{"issuer":K},self.guard,registry,NOW)
 def test_allowed_is_advisory(self):
  r=self.call(IssuerTrustRegistry([policy()]))
  self.assertEqual(r.status,"ADVISORY_ONLY")
  self.assertFalse(r.action_authorized)
 def test_revoked_blocks(self):
  self.assertEqual(self.call(IssuerTrustRegistry([policy(revoked=True)])).reason,"issuer_revoked")
 def test_rejection_does_not_consume_nonce(self):
  self.assertEqual(self.call(IssuerTrustRegistry()).status,"REJECT")
  self.assertEqual(self.call(IssuerTrustRegistry([policy()])).status,"ADVISORY_ONLY")
 def test_replay(self):
  reg=IssuerTrustRegistry([policy()])
  self.assertEqual(self.call(reg).status,"ADVISORY_ONLY")
  self.assertEqual(self.call(reg).reason,"replayed_nonce")
if __name__=="__main__":
 unittest.main()
