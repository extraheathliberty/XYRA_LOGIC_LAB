import unittest
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff,ProofStep
from xyra_logic.structural_audit import inspect_formula,FormulaStructureError
from xyra_logic.proof_audit import audit_proof
P,Q=Var("P"),Var("Q")

class TestStructuralAudit(unittest.TestCase):
 def test_valid_deep_formula(self):
  self.assertEqual(inspect_formula(Imp(And(P,Not(Q)),Iff(Q,Or(P,Q)))),frozenset({"P","Q"}))
 def test_reject_short_circuited_bad_and_branch(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(And(P,"invalid"))
 def test_reject_short_circuited_bad_or_branch(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Or(P,123))
 def test_reject_short_circuited_bad_imp_branch(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Imp(P,None))
 def test_reject_bad_negation(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Not({}))
 def test_reject_empty_variable(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Var(""))
 def test_reject_nonstring_variable(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Var(1))
 def test_reject_node_limit(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(And(P,Q),max_nodes=2)
 def test_reject_depth_limit(self):
  with self.assertRaises(FormulaStructureError): inspect_formula(Not(Not(P)),max_depth=1)
 def test_audit_checks_unvisited_bad_branch(self):
  # Ordinary Boolean AND can short-circuit when P is false; audit must inspect both sides.
  with self.assertRaises(FormulaStructureError):
   audit_proof([And(P,"bad")],[],Q)
 def test_audit_checks_malformed_conclusion(self):
  with self.assertRaises(FormulaStructureError):
   audit_proof([P],[],Or(P,object()))
 def test_audit_checks_malformed_proof_line(self):
  with self.assertRaises(FormulaStructureError):
   audit_proof([P],[ProofStep(And(P,None),"premise")],P)
if __name__=="__main__":
 unittest.main()
