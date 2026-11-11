import unittest
from xyra_logic.formal_core import Var,Not,Imp,Or
from xyra_logic.decision_api import decide_entailment
P,Q=Var("P"),Var("Q")
class TestDecisionAPI(unittest.TestCase):
 def test_valid(self):
  d=decide_entailment([Imp(P,Q),P],Q)
  self.assertEqual(d.status,"VALID")
  self.assertIsNone(d.witness)
 def test_invalid(self):
  d=decide_entailment([Imp(P,Q),Q],P)
  self.assertEqual(d.status,"INVALID")
  self.assertEqual(d.witness,{"P":False,"Q":True})
 def test_budget_is_inconclusive_not_valid(self):
  d=decide_entailment([Var(f"X{i}") for i in range(11)],P)
  self.assertEqual(d.status,"INCONCLUSIVE")
  self.assertEqual(d.reason,"variable_budget_exceeded")
 def test_no_premise_tautology(self):
  self.assertEqual(decide_entailment([],Or(P,Not(P))).status,"VALID")
 def test_no_premise_nontautology(self):
  self.assertEqual(decide_entailment([],P).status,"INVALID")
 def test_contradiction_classically_entails(self):
  self.assertEqual(decide_entailment([P,Not(P)],Q).status,"VALID")
 def test_inconclusive_not_witness(self):
  self.assertIsNone(decide_entailment([Var(f"X{i}") for i in range(11)],P).witness)
 def test_method_metadata(self):
  self.assertEqual(decide_entailment([],P).method,"bitset-exhaustive")
if __name__=="__main__":
 unittest.main()
