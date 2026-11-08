import hashlib
import unittest
from dataclasses import replace
from datetime import datetime,timezone,timedelta
from xyra_logic.formal_core import Var
from xyra_logic.evidence_envelope import sign_evidence
from xyra_logic.source_verification import verify_source_bytes,MAX_SOURCE_BYTES
from xyra_logic.replay_guard import sign_request,ReplayGuard
K=b"k"*32
NOW=datetime(2026,11,8,14,0,tzinfo=timezone.utc)
STAMP="2026-11-08T14:00:00Z"
P=Var("P")
def envelope(source):
 return sign_evidence("e1","issuer",P,hashlib.sha256(source).hexdigest(),STAMP,K)
def request(nonce="n1",stamp=STAMP):
 return sign_request("issuer",nonce,stamp,"a"*64,K)
class TestSourceVerification(unittest.TestCase):
 def test_matching_source(self):
  self.assertTrue(verify_source_bytes(envelope(b"document"),b"document",{"issuer":K}).verified)
 def test_tampered_source(self):
  self.assertEqual(verify_source_bytes(envelope(b"document"),b"altered",{"issuer":K}).reason,"source_digest_mismatch")
 def test_wrong_key(self):
  self.assertEqual(verify_source_bytes(envelope(b"x"),b"x",{"issuer":b"x"*32}).reason,"envelope_authentication_failed")
 def test_missing_key(self):
  self.assertFalse(verify_source_bytes(envelope(b"x"),b"x",{}).verified)
 def test_nonbytes_source(self):
  self.assertEqual(verify_source_bytes(envelope(b"x"),"x",{"issuer":K}).reason,"source_not_bytes")
 def test_size_limit(self):
  self.assertEqual(verify_source_bytes(envelope(b"x"),b"x"*(MAX_SOURCE_BYTES+1),{"issuer":K}).reason,"source_budget_exceeded")
 def test_empty_bytes_valid_if_signed(self):
  self.assertTrue(verify_source_bytes(envelope(b""),b"",{"issuer":K}).verified)
 def test_source_digest_returned(self):
  self.assertEqual(verify_source_bytes(envelope(b"x"),b"x",{"issuer":K}).source_sha256,hashlib.sha256(b"x").hexdigest())
class TestReplayGuard(unittest.TestCase):
 def test_accept_once(self):
  g=ReplayGuard()
  self.assertEqual(g.verify_once(request(),{"issuer":K},NOW),(True,"accepted_once"))
 def test_replay_rejected(self):
  g=ReplayGuard()
  self.assertTrue(g.verify_once(request(),{"issuer":K},NOW)[0])
  self.assertEqual(g.verify_once(request(),{"issuer":K},NOW)[1],"replayed_nonce")
 def test_new_nonce(self):
  g=ReplayGuard()
  self.assertTrue(g.verify_once(request("n1"),{"issuer":K},NOW)[0])
  self.assertTrue(g.verify_once(request("n2"),{"issuer":K},NOW)[0])
 def test_wrong_key(self):
  self.assertEqual(ReplayGuard().verify_once(request(),{"issuer":b"x"*32},NOW)[1],"invalid_signature")
 def test_unknown_issuer(self):
  self.assertEqual(ReplayGuard().verify_once(request(),{},NOW)[1],"unknown_issuer")
 def test_expired(self):
  self.assertEqual(ReplayGuard().verify_once(request(),{"issuer":K},NOW+timedelta(seconds=301))[1],"outside_time_window")
 def test_future_dated(self):
  self.assertEqual(ReplayGuard().verify_once(request(),{"issuer":K},NOW-timedelta(seconds=301))[1],"outside_time_window")
 def test_boundary(self):
  self.assertTrue(ReplayGuard().verify_once(request(),{"issuer":K},NOW+timedelta(seconds=300))[0])
 def test_tampered_nonce(self):
  self.assertEqual(ReplayGuard().verify_once(replace(request(),nonce="other"),{"issuer":K},NOW)[1],"invalid_signature")
 def test_tampered_digest(self):
  self.assertEqual(ReplayGuard().verify_once(replace(request(),request_digest="b"*64),{"issuer":K},NOW)[1],"invalid_signature")
 def test_tampered_timestamp(self):
  self.assertEqual(ReplayGuard().verify_once(replace(request(),issued_at="2026-11-08T14:01:00Z"),{"issuer":K},NOW)[1],"invalid_signature")
 def test_capacity_fail_closed(self):
  g=ReplayGuard(max_entries=1)
  self.assertTrue(g.verify_once(request("n1"),{"issuer":K},NOW)[0])
  self.assertEqual(g.verify_once(request("n2"),{"issuer":K},NOW)[1],"replay_registry_full")
 def test_invalid_clock(self):
  self.assertEqual(ReplayGuard().verify_once(request(),{"issuer":K},datetime(2026,11,8))[1],"invalid_clock")
 def test_bad_signature(self):
  self.assertEqual(ReplayGuard().verify_once(replace(request(),signature="0"*64),{"issuer":K},NOW)[1],"invalid_signature")
 def test_short_key_rejected(self):
  with self.assertRaises(ValueError): sign_request("issuer","n",STAMP,"a"*64,b"short")
 def test_bad_timestamp_rejected(self):
  with self.assertRaises(ValueError): sign_request("issuer","n","yesterday","a"*64,K)
 def test_invalid_digest_rejected(self):
  with self.assertRaises(ValueError): sign_request("issuer","n",STAMP,"abc",K)
 def test_invalid_object(self):
  self.assertEqual(ReplayGuard().verify_once({},{"issuer":K},NOW)[1],"invalid_request")
 def test_invalid_capacity(self):
  with self.assertRaises(ValueError): ReplayGuard(max_entries=0)
if __name__=="__main__":
 unittest.main()
