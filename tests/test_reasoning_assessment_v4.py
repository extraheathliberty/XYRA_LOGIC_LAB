import unittest
from xyra_logic.formal_core import Var,Not,And,Or,Imp
from xyra_logic.reasoning_assessment import assess_reasoning
P,Q=Var("P"),Var("Q")

class TestReasoningAssessment(unittest.TestCase):
 def test_modus_ponens_supported(self):
  a=assess_reasoning([Imp(P,Q),P],Q)
  self.assertEqual((a.verdict,a.entailment,a.premise_consistency),("SUPPORTED","VALID","CONSISTENT"))
 def test_conclusion_refuted(self):
  a=assess_reasoning([P,Imp(P,Not(Q))],Q)
  self.assertEqual(a.verdict,"REFUTED")
  self.assertEqual(a.conclusion_possible,"NO")
  self.assertTrue(a.countermodel["P"])
  self.assertFalse(a.countermodel["Q"])
 def test_underdetermined(self):
  a=assess_reasoning([P],Q)
  self.assertEqual(a.verdict,"UNDETERMINED")
  self.assertEqual(a.conclusion_possible,"YES")
  self.assertFalse(a.countermodel["Q"])
 def test_contradictory_premises_block(self):
  a=assess_reasoning([P,Not(P)],Q)
  self.assertEqual(a.verdict,"BLOCKED_CONTRADICTION")
  self.assertEqual(a.entailment,"VACUOUSLY_VALID")
  self.assertEqual(a.premise_consistency,"INCONSISTENT")
 def test_contradictory_premises_do_not_support_conclusion(self):
  self.assertNotEqual(assess_reasoning([P,Not(P)],Q).verdict,"SUPPORTED")
 def test_unsupported_converse(self):
  self.assertEqual(assess_reasoning([Imp(P,Q),Q],P).verdict,"UNDETERMINED")
 def test_denied_antecedent_underdetermined(self):
  self.assertEqual(assess_reasoning([Imp(P,Q),Not(P)],Not(Q)).verdict,"UNDETERMINED")
 def test_empty_premises_tautology(self):
  self.assertEqual(assess_reasoning([],Or(P,Not(P))).verdict,"SUPPORTED")
 def test_empty_premises_atom_undetermined(self):
  self.assertEqual(assess_reasoning([],P).verdict,"UNDETERMINED")
 def test_empty_premises_contradiction_refuted(self):
  self.assertEqual(assess_reasoning([],And(P,Not(P))).verdict,"REFUTED")
 def test_consistent_premise_entails_negative(self):
  self.assertEqual(assess_reasoning([Not(P)],P).verdict,"REFUTED")
 def test_consistent_premise_supports_itself(self):
  self.assertEqual(assess_reasoning([P],P).verdict,"SUPPORTED")
 def test_budget_abstains(self):
  a=assess_reasoning([Var(f"X{i}") for i in range(11)],P)
  self.assertEqual(a.verdict,"ABSTAIN")
  self.assertEqual(a.entailment,"UNKNOWN")
  self.assertEqual(a.reason,"resource_budget_exceeded")
 def test_budget_never_claims_consistency(self):
  self.assertEqual(assess_reasoning([Var(f"X{i}") for i in range(11)],P).premise_consistency,"UNKNOWN")
 def test_countermodel_is_genuine(self):
  a=assess_reasoning([Imp(P,Q),Q],P)
  self.assertEqual(a.countermodel,{"P":False,"Q":True})
 def test_no_countermodel_when_supported(self):
  self.assertIsNone(assess_reasoning([P],P).countermodel)
 def test_no_countermodel_when_inconsistent(self):
  self.assertIsNone(assess_reasoning([P,Not(P)],Q).countermodel)
 def test_pilot_does_not_imply_production(self):
  pilot=Var("pilot"); production=Var("production")
  self.assertEqual(assess_reasoning([pilot],production).verdict,"UNDETERMINED")
 def test_approval_not_technical_execution(self):
  approved=Var("approved"); executed=Var("executed")
  self.assertEqual(assess_reasoning([approved],executed).verdict,"UNDETERMINED")
 def test_observation_not_command_authority(self):
  observed=Var("observed"); commanded=Var("commanded")
  self.assertEqual(assess_reasoning([observed],commanded).verdict,"UNDETERMINED")
if __name__=="__main__":
 unittest.main()
