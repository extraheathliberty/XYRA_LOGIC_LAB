import os
import tempfile
import unittest
from xyra_logic.durable_audit import DurableAudit
from xyra_logic.audit_anchor import export_anchor,verify_anchor

class TestAuditAnchor(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.audit=DurableAudit(os.path.join(self.tmp.name,"db.sqlite3"))
  self.archive=os.path.join(self.tmp.name,"archive")
  os.mkdir(self.archive)
 def tearDown(self):self.tmp.cleanup()
 def test_export_and_verify(self):
  self.audit.append("issue","e1")
  export_anchor(self.audit,self.archive,"anchor1")
  self.assertTrue(verify_anchor(self.audit,self.archive,"anchor1"))
 def test_exclusive_no_overwrite(self):
  export_anchor(self.audit,self.archive,"anchor1")
  with self.assertRaises(FileExistsError):export_anchor(self.audit,self.archive,"anchor1")
 def test_detect_subsequent_append(self):
  export_anchor(self.audit,self.archive,"anchor1")
  self.audit.append("issue","e2")
  self.assertFalse(verify_anchor(self.audit,self.archive,"anchor1"))
 def test_detect_archive_edit(self):
  path=export_anchor(self.audit,self.archive,"anchor1")
  with open(path,"w") as f:f.write('{"anchor_id":"anchor1","checkpoint":{"count":900}}')
  self.assertFalse(verify_anchor(self.audit,self.archive,"anchor1"))
 def test_missing_anchor(self):
  self.assertFalse(verify_anchor(self.audit,self.archive,"missing"))
 def test_reject_path_traversal(self):
  with self.assertRaises(ValueError):export_anchor(self.audit,self.archive,"../escape")
 def test_reject_missing_directory(self):
  with self.assertRaises(ValueError):export_anchor(self.audit,os.path.join(self.tmp.name,"missing"),"id")
 def test_reject_oversized(self):
  path=export_anchor(self.audit,self.archive,"anchor1")
  with open(path,"w") as f:f.write("x"*5000)
  self.assertFalse(verify_anchor(self.audit,self.archive,"anchor1"))
if __name__=="__main__":unittest.main()
