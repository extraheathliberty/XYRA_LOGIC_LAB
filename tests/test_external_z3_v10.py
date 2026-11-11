"""Runs only in optional external Z3 verification workflow."""
import json
import unittest
import importlib.util
from xyra_logic.formal_core import Var,Not,Imp,And,Or,Iff
from xyra_logic.z3_verifier import verify_with_z3
P,Q=Var("P"),Var("Q")
@unittest.skipUnless(importlib.util.find_spec("z3") is not None,"z3-solver not installed in standard test environment")
class TestExternalZ3(unittest.TestCase):
 def check(self,premises,conclusion,expected):
  result=verify_with_z3(premises,conclusion)
  self.assertEqual(result["status"],expected)
  self.assertEqual(len(result["handoff_sha256"]),64)
  print("Z3_VERIFIED",json.dumps(result,sort_keys=True))
 def test_modus_ponens(self):self.check([Imp(P,Q),P],Q,"UNSAT")
 def test_affirming_consequent(self):self.check([Imp(P,Q),Q],P,"SAT")
 def test_denial_antecedent(self):self.check([Imp(P,Q),Not(P)],Not(Q),"SAT")
 def test_contradiction(self):self.check([P,Not(P)],Q,"UNSAT")
 def test_tautology(self):self.check([],Or(P,Not(P)),"UNSAT")
 def test_conjunction(self):self.check([And(P,Q)],P,"UNSAT")
 def test_biconditional_forward(self):self.check([Iff(P,Q),P],Q,"UNSAT")
 def test_biconditional_reverse(self):self.check([Iff(P,Q),Q],P,"UNSAT")
 def test_disjunction_elimination(self):self.check([Or(P,Q),Not(P)],Q,"UNSAT")
 def test_disjunction_no_entailment(self):self.check([Or(P,Q)],P,"SAT")
 def test_double_negation(self):self.check([Not(Not(P))],P,"UNSAT")
 def test_contraposition(self):self.check([Imp(P,Q),Not(Q)],Not(P),"UNSAT")
 def test_no_converse(self):self.check([Imp(P,Q)],Imp(Q,P),"SAT")
 def test_and_intro(self):self.check([P,Q],And(P,Q),"UNSAT")
 def test_or_intro(self):self.check([P],Or(P,Q),"UNSAT")
 def test_inconsistent_does_not_authorize(self):
  self.check([P,Not(P)],Q,"UNSAT")
  # Classical UNSAT under inconsistent premises is not an action authorization.
if __name__=="__main__":unittest.main()
