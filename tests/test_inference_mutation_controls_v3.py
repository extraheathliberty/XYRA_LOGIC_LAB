"""Deliberately faulty inference policies as negative controls.

Every mutant is an INVALID inference and must be rejected by the kernel
and/or falsified by a semantic countermodel. This is not a general mutation
testing framework.
"""
import unittest
from xyra_logic.formal_core import Var,Not,Imp,And,ProofStep,valid,countermodels,check_proof,satisfiable
from xyra_logic.bitset_oracle import oracle_entails
P,Q=Var("P"),Var("Q")

class TestInferenceMutationControls(unittest.TestCase):
 def assert_detected(self,premises,conclusion,steps):
  self.assertFalse(check_proof(premises,steps,conclusion))
  self.assertFalse(valid(premises,conclusion))
  self.assertTrue(countermodels(premises,conclusion))
  result,witness=oracle_entails(premises,conclusion)
  self.assertFalse(result)
  self.assertIsNotNone(witness)
 def test_affirming_consequent(self):
  self.assert_detected([Imp(P,Q),Q],P,[ProofStep(Imp(P,Q),"premise"),ProofStep(Q,"premise"),ProofStep(P,"imp_elim",(0,1))])
 def test_denying_antecedent(self):
  self.assert_detected([Imp(P,Q),Not(P)],Not(Q),[ProofStep(Imp(P,Q),"premise"),ProofStep(Not(P),"premise"),ProofStep(Not(Q),"imp_elim",(0,1))])
 def test_and_introduction_without_second_premise(self):
  self.assert_detected([P],And(P,Q),[ProofStep(P,"premise"),ProofStep(And(P,Q),"and_intro",(0,0))])
 def test_and_elimination_to_unrelated_conclusion(self):
  self.assert_detected([And(P,Q)],Not(P),[ProofStep(And(P,Q),"premise"),ProofStep(Not(P),"and_elim_left",(0,))])
 def test_arbitrary_conclusion_from_true_premise(self):
  self.assert_detected([P],Q,[ProofStep(P,"premise"),ProofStep(Q,"premise")])
 def test_production_from_pilot(self):
  pilot=Var("pilot_allowed"); production=Var("production_admitted")
  self.assert_detected([pilot],production,[ProofStep(pilot,"premise"),ProofStep(production,"premise")])
 def test_inversion_of_implication(self):
  self.assert_detected([Imp(P,Q)],Imp(Q,P),[ProofStep(Imp(P,Q),"premise"),ProofStep(Imp(Q,P),"premise")])
 def test_converse_not_equivalent(self):
  self.assertFalse(valid([Imp(P,Q)],Imp(Q,P)))
 def test_excluded_middle_not_premise_of_P(self):
  self.assertFalse(valid([P if False else Imp(P,P)],P))
 def test_contradiction_does_not_imply_premise_consistency(self):
  self.assertTrue(valid([P,Not(P)],Not(Q)))
  self.assertFalse(satisfiable([P,Not(P)]))
if __name__=="__main__":
 unittest.main()
