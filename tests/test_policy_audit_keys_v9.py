import unittest
from dataclasses import replace
from datetime import datetime,timezone,timedelta
from xyra_logic.issuer_trust import IssuerPolicy
from xyra_logic.policy_attestation import attest_policy,verify_attestations,AttestedIssuerTrustRegistry
from xyra_logic.audit_chain import append_audit,verify_chain
from xyra_logic.key_lifecycle import KeyRecord,KeyRegistry
NOW=datetime(2026,11,8,14,tzinfo=timezone.utc)
K1=b"a"*32;K2=b"b"*32
def policy():
 return IssuerPolicy("issuer",frozenset({"LOGIC"}),NOW-timedelta(days=1),
                     NOW+timedelta(days=1),False,"TEST-NOT-COMMITTEE-APPROVAL")
class TestPolicyAttestation(unittest.TestCase):
 def test_two_keys(self):
  p=policy();a=[attest_policy(p,"a",K1),attest_policy(p,"b",K2)]
  self.assertEqual(verify_attestations(p,a,{"a":K1,"b":K2}),(True,"attestor_key_threshold_met"))
 def test_one_key_insufficient(self):
  p=policy();self.assertFalse(verify_attestations(p,[attest_policy(p,"a",K1)],{"a":K1})[0])
 def test_wrong_key(self):
  p=policy();self.assertFalse(verify_attestations(p,[attest_policy(p,"a",K1)],{"a":K2})[0])
 def test_duplicate_attestor(self):
  p=policy();a=attest_policy(p,"a",K1)
  self.assertFalse(verify_attestations(p,[a,a],{"a":K1})[0])
 def test_policy_tamper(self):
  p=policy();a=[attest_policy(p,"a",K1),attest_policy(p,"b",K2)]
  self.assertFalse(verify_attestations(replace(p,revoked=True),a,{"a":K1,"b":K2})[0])
 def test_scope_tamper(self):
  p=policy();a=[attest_policy(p,"a",K1),attest_policy(p,"b",K2)]
  self.assertFalse(verify_attestations(replace(p,allowed_consumers=frozenset({"AUTOMATION"})),a,{"a":K1,"b":K2})[0])
 def test_attested_registry(self):
  p=policy();a=[attest_policy(p,"a",K1),attest_policy(p,"b",K2)]
  r=AttestedIssuerTrustRegistry([p],{"issuer":a},{"a":K1,"b":K2})
  self.assertTrue(r.authorize("issuer","LOGIC",NOW)[0])
 def test_registry_rejects_one_attestor(self):
  p=policy()
  with self.assertRaises(ValueError):
   AttestedIssuerTrustRegistry([p],{"issuer":[attest_policy(p,"a",K1)]},{"a":K1,"b":K2})
class TestAuditChain(unittest.TestCase):
 def test_empty_chain(self):self.assertTrue(verify_chain([]))
 def test_append(self):
  r=append_audit([],"issued","e1")
  self.assertTrue(verify_chain(r))
 def test_multiple_records(self):
  r=append_audit([],"issued","e1")
  self.assertTrue(verify_chain(append_audit(r,"revoked","e1")))
 def test_tamper_event(self):
  r=append_audit([],"issued","e1")
  self.assertFalse(verify_chain([replace(r[0],event="changed")]))
 def test_tamper_subject(self):
  r=append_audit([],"issued","e1")
  self.assertFalse(verify_chain([replace(r[0],subject="e2")]))
 def test_reorder(self):
  r=append_audit(append_audit([],"issued","e1"),"revoked","e1")
  self.assertFalse(verify_chain(r[::-1]))
 def test_invalid_existing_chain(self):
  r=append_audit([],"issued","e1")
  with self.assertRaises(ValueError):append_audit([replace(r[0],record_hash="0"*64)],"other","e2")
class TestKeyLifecycle(unittest.TestCase):
 def record(self,**kwargs):
  d=dict(issuer="issuer",key_id="v1",secret=K1,valid_from=NOW-timedelta(days=1),
         valid_until=NOW+timedelta(days=1))
  d.update(kwargs);return KeyRecord(**d)
 def test_active(self):
  self.assertEqual(KeyRegistry([self.record()]).resolve("issuer","v1",NOW)[0],K1)
 def test_unknown(self):
  self.assertEqual(KeyRegistry().resolve("issuer","v1",NOW)[1],"unknown_key")
 def test_revoked(self):
  self.assertEqual(KeyRegistry([self.record(revoked=True)]).resolve("issuer","v1",NOW)[1],"revoked_key")
 def test_expired(self):
  self.assertEqual(KeyRegistry([self.record()]).resolve("issuer","v1",NOW+timedelta(days=2))[1],"key_outside_validity")
 def test_rotation(self):
  r=KeyRegistry([self.record(),self.record(key_id="v2",secret=K2)])
  self.assertEqual(r.resolve("issuer","v2",NOW)[0],K2)
 def test_duplicate(self):
  with self.assertRaises(ValueError):KeyRegistry([self.record(),self.record()])
 def test_short_secret(self):
  with self.assertRaises(ValueError):KeyRegistry([self.record(secret=b"x")])
 def test_invalid_window(self):
  with self.assertRaises(ValueError):KeyRegistry([self.record(valid_from=NOW+timedelta(days=2))])
if __name__=="__main__":
 unittest.main()
