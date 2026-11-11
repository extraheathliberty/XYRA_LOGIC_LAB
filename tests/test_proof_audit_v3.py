import unittest
from xyra_logic.formal_core import Var,Not,And,Or,Imp,ProofStep
from xyra_logic.proof_audit import audit_proof, MAX_VARIABLES, MAX_PROOF_STEPS
P,Q,R=Var("P"),Var("Q"),Var("R")

class TestProofAudit(unittest.TestCase):
 def test_modus_ponens_certificate_sound(self):
  steps=[ProofStep(Imp(P,Q),"premise"),ProofStep(P,"premise"),ProofStep(Q,"imp_elim",(0,1))]
  result=audit_proof([Imp(P,Q),P],steps,Q)
  self.assertTrue(result.accepted)
  self.assertTrue(result.semantically_sound)
  self.assertIsNone(result.countermodel)
 def test_affirming_consequent_rejected_with_countermodel(self):
  steps=[ProofStep(Imp(P,Q),"premise"),ProofStep(Q,"premise"),ProofStep(P,"imp_elim",(0,1))]
  result=audit_proof([Imp(P,Q),Q],steps,P)
  self.assertFalse(result.accepted)
  self.assertFalse(result.semantically_sound)
  self.assertEqual(result.countermodel,{"P":False,"Q":True})
 def test_invalid_proof_of_valid_theorem_not_accepted(self):
  result=audit_proof([], [ProofStep(Or(P,Not(P)),"premise")],Or(P,Not(P)))
  self.assertFalse(result.accepted)
  self.assertTrue(result.semantically_sound)
  self.assertEqual(result.reason,"not_accepted_by_restricted_calculus")
 def test_contradictory_premises_vacuous(self):
  steps=[ProofStep(P,"premise"),ProofStep(Not(P),"premise")]
  result=audit_proof([P,Not(P)],steps,Not(P))
  self.assertTrue(result.accepted)
  self.assertTrue(result.semantically_sound)
 def test_missing_proof_with_false_conclusion(self):
  result=audit_proof([P],[],Q)
  self.assertFalse(result.accepted)
  self.assertEqual(result.countermodel,{"P":True,"Q":False})
 def test_and_intro_sound(self):
  steps=[ProofStep(P,"premise"),ProofStep(Q,"premise"),ProofStep(And(P,Q),"and_intro",(0,1))]
  self.assertTrue(audit_proof([P,Q],steps,And(P,Q)).semantically_sound)
 def test_and_elim_sound(self):
  steps=[ProofStep(And(P,Q),"premise"),ProofStep(P,"and_elim_left",(0,))]
  self.assertTrue(audit_proof([And(P,Q)],steps,P).semantically_sound)
 def test_double_neg_sound(self):
  steps=[ProofStep(Not(Not(P)),"premise"),ProofStep(P,"double_neg_elim",(0,))]
  self.assertTrue(audit_proof([Not(Not(P))],steps,P).semantically_sound)
 def test_imp_chain_sound(self):
  steps=[ProofStep(Imp(P,Q),"premise"),ProofStep(Imp(Q,R),"premise"),
         ProofStep(P,"premise"),ProofStep(Q,"imp_elim",(0,2)),
         ProofStep(R,"imp_elim",(1,3))]
  self.assertTrue(audit_proof([Imp(P,Q),Imp(Q,R),P],steps,R).semantically_sound)
 def test_variable_budget(self):
  ps=[Var(f"P{i}") for i in range(MAX_VARIABLES+1)]
  result=audit_proof(ps,[],ps[0])
  self.assertEqual(result.reason,"truth_assignment_budget_exceeded")
 def test_step_budget(self):
  result=audit_proof([P],[ProofStep(P,"premise")]*(MAX_PROOF_STEPS+1),P)
  self.assertEqual(result.reason,"proof_step_budget_exceeded")
 def test_unsupported_rule_rejected(self):
  result=audit_proof([P],[ProofStep(P,"invented")],P)
  self.assertFalse(result.accepted)
 def test_wrong_conclusion_countermodel(self):
  steps=[ProofStep(P,"premise")]
  result=audit_proof([P],steps,Q)
  self.assertEqual(result.countermodel,{"P":True,"Q":False})
 def test_or_intro_sound(self):
  steps=[ProofStep(P,"premise"),ProofStep(Or(P,Q),"or_intro_left",(0,))]
  self.assertTrue(audit_proof([P],steps,Or(P,Q)).semantically_sound)
 def test_proof_with_unneeded_premise(self):
  steps=[ProofStep(P,"premise")]
  self.assertTrue(audit_proof([P,Q],steps,P).accepted)
if __name__=="__main__":
 unittest.main()
