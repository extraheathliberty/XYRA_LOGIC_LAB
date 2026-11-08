import os
import tempfile
import threading
import unittest
from xyra_logic.durable_audit import DurableAudit

class TestDurableAudit(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.path=os.path.join(self.tmp.name,"audit.db")
  self.audit=DurableAudit(self.path)
 def tearDown(self):self.tmp.cleanup()
 def test_empty_checkpoint(self):
  self.assertEqual(self.audit.checkpoint()["count"],0)
 def test_append_and_reopen(self):
  self.audit.append("issued","e1")
  self.assertEqual(DurableAudit(self.path).checkpoint()["count"],1)
 def test_checkpoint_matches(self):
  self.audit.append("issued","e1")
  self.assertTrue(self.audit.verify_checkpoint(self.audit.checkpoint()))
 def test_truncation_detected_against_checkpoint(self):
  self.audit.append("issued","e1")
  checkpoint=self.audit.checkpoint()
  with self.audit._connect() as db:db.execute("DELETE FROM audit")
  self.assertFalse(self.audit.verify_checkpoint(checkpoint))
 def test_tampering_detected(self):
  self.audit.append("issued","e1")
  with self.audit._connect() as db:db.execute("UPDATE audit SET event='forged' WHERE sequence=1")
  with self.assertRaises(ValueError):self.audit.checkpoint()
 def test_append_rejects_tampered_chain(self):
  self.audit.append("issued","e1")
  with self.audit._connect() as db:db.execute("UPDATE audit SET subject='fake' WHERE sequence=1")
  with self.assertRaises(ValueError):self.audit.append("revoked","e1")
 def test_parallel_appends(self):
  errors=[]
  def worker(i):
   try:DurableAudit(self.path).append("event",str(i))
   except Exception as e:errors.append(str(e))
  threads=[threading.Thread(target=worker,args=(i,)) for i in range(8)]
  for t in threads:t.start()
  for t in threads:t.join()
  self.assertEqual(errors,[])
  self.assertEqual(self.audit.checkpoint()["count"],8)
 def test_empty_event(self):
  with self.assertRaises(ValueError):self.audit.append("","x")
 def test_wrong_anchor(self):
  self.audit.append("issued","e1")
  self.assertFalse(self.audit.verify_checkpoint({"schema":"xyra-audit-head-v1","count":1,"head":"0"*64}))
 def test_no_external_anchor_claim(self):
  self.assertNotIn("externally_anchored",self.audit.checkpoint())
if __name__=="__main__":unittest.main()
