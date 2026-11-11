import unittest
from xyra_logic.formal_core import Var,Not,And,Imp,ProofStep
from xyra_logic.proof_crosscheck import crosscheck_proof
P,Q=Var("P"),Var("Q")
class TestProofCrosscheck(unittest.TestCase):
 def test_modus_ponens(self):
  steps=[ProofStep(Imp(P,Q),"premise"),ProofStep(P,"premise"),ProofStep(Q,"imp_elim",(0,1))]
  self.assertEqual(crosscheck_proof([Imp(P,Q),P],steps,Q).status,"BOUNDED_CROSSCHECK_PASS")
 def test_reject_affirming_consequent(self):
  steps=[ProofStep(Imp(P,Q),"premise"),ProofStep(Q,"premise"),ProofStep(P,"imp_elim",(0,1))]
  r=crosscheck_proof([Imp(P,Q),Q],steps,P)
  self.assertEqual(r.status,"NOT_ACCEPTED")
  self.assertEqual(r.countermodel,{"P":False,"Q":True})
 def test_reject_unsupported_rule(self):
  self.assertEqual(crosscheck_proof([P],[ProofStep(P,"invented")],P).status,"NOT_ACCEPTED")
 def test_reject_wrong_conclusion(self):
  self.assertEqual(crosscheck_proof([P],[ProofStep(P,"premise")],Q).status,"NOT_ACCEPTED")
 def test_and_elim(self):
  steps=[ProofStep(And(P,Q),"premise"),ProofStep(P,"and_elim_left",(0,))]
  self.assertEqual(crosscheck_proof([And(P,Q)],steps,P).status,"BOUNDED_CROSSCHECK_PASS")
 def test_double_neg(self):
  steps=[ProofStep(Not(Not(P)),"premise"),ProofStep(P,"double_neg_elim",(0,))]
  self.assertEqual(crosscheck_proof([Not(Not(P))],steps,P).status,"BOUNDED_CROSSCHECK_PASS")
 def test_budget(self):
  r=crosscheck_proof([Var(f"X{i}") for i in range(11)],[],P)
  self.assertEqual(r.status,"INCONCLUSIVE")
 def test_no_proof(self):
  self.assertEqual(crosscheck_proof([P],[],P).status,"NOT_ACCEPTED")
 def test_inconsistent_premises_do_not_authorize(self):
  steps=[ProofStep(P,"premise"),ProofStep(Not(P),"premise")]
  r=crosscheck_proof([P,Not(P)],steps,Not(P))
  self.assertEqual(r.status,"BOUNDED_CROSSCHECK_PASS")
  # Consistency must be separately assessed before any decision.
 def test_conjunction_intro(self):
  steps=[ProofStep(P,"premise"),ProofStep(Q,"premise"),ProofStep(And(P,Q),"and_intro",(0,1))]
  self.assertEqual(crosscheck_proof([P,Q],steps,And(P,Q)).status,"BOUNDED_CROSSCHECK_PASS")
if __name__=="__main__":
 unittest.main()
