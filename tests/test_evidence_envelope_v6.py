import unittest
from dataclasses import replace
from xyra_logic.formal_core import Var,Not
from xyra_logic.evidence_envelope import sign_evidence,verify_evidence
P=Var("P")
KEY=b"k"*32
DIGEST="a"*64
class TestEvidenceEnvelope(unittest.TestCase):
 def setUp(self):
  self.env=sign_evidence("e-1","lab",P,DIGEST,"2026-11-08T00:00:00Z",KEY)
 def test_valid_signature(self):
  self.assertTrue(verify_evidence(self.env,{"lab":KEY}))
 def test_wrong_key(self):
  self.assertFalse(verify_evidence(self.env,{"lab":b"x"*32}))
 def test_missing_issuer(self):
  self.assertFalse(verify_evidence(self.env,{}))
 def test_issuer_change(self):
  self.assertFalse(verify_evidence(replace(self.env,issuer="other"),{"other":KEY}))
 def test_evidence_id_change(self):
  self.assertFalse(verify_evidence(replace(self.env,evidence_id="e-2"),{"lab":KEY}))
 def test_proposition_change(self):
  self.assertFalse(verify_evidence(replace(self.env,proposition=Not(P)),{"lab":KEY}))
 def test_source_digest_change(self):
  self.assertFalse(verify_evidence(replace(self.env,source_digest="b"*64),{"lab":KEY}))
 def test_issued_at_change(self):
  self.assertFalse(verify_evidence(replace(self.env,issued_at="2026-11-09"),{"lab":KEY}))
 def test_signature_change(self):
  self.assertFalse(verify_evidence(replace(self.env,signature="0"*64),{"lab":KEY}))
 def test_short_key_rejected(self):
  with self.assertRaises(ValueError):
   sign_evidence("e-1","lab",P,DIGEST,"2026-11-08",b"weak")
 def test_invalid_digest_rejected(self):
  with self.assertRaises(ValueError):
   sign_evidence("e-1","lab",P,"nope","2026-11-08",KEY)
 def test_non_envelope_rejected(self):
  self.assertFalse(verify_evidence({},{"lab":KEY}))
 def test_bad_keyring_rejected(self):
  self.assertFalse(verify_evidence(self.env,None))
 def test_nonstring_signature_rejected(self):
  self.assertFalse(verify_evidence(replace(self.env,signature=None),{"lab":KEY}))
 def test_invalid_metadata_rejected(self):
  with self.assertRaises(ValueError):
   sign_evidence("","lab",P,DIGEST,"2026-11-08",KEY)
if __name__=="__main__":
 unittest.main()
