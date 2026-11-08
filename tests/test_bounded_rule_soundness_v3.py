"""Exhaustive bounded proof-rule soundness over small formulas.

These are exhaustive within the explicitly enumerated fragment, not a
mathematical proof of soundness for every possible formula.
"""
import unittest
from itertools import product
from xyra_logic.formal_core import Var,Not,And,Or,Imp,ProofStep
from xyra_logic.proof_audit import audit_proof
P,Q=Var("P"),Var("Q")
FORMULAS=(P,Q,Not(P),Not(Q),And(P,Q),Or(P,Q),Imp(P,Q))

class TestBoundedRuleSoundness(unittest.TestCase):
 def test_and_introduction_all_pairs(self):
  for a,b in product(FORMULAS,repeat=2):
   with self.subTest(a=a,b=b):
    steps=[ProofStep(a,"premise"),ProofStep(b,"premise"),ProofStep(And(a,b),"and_intro",(0,1))]
    audit=audit_proof([a,b],steps,And(a,b))
    self.assertTrue(audit.accepted and audit.semantically_sound,audit)
 def test_and_elimination_all_pairs(self):
  for a,b in product(FORMULAS,repeat=2):
   with self.subTest(a=a,b=b):
    steps=[ProofStep(And(a,b),"premise"),ProofStep(a,"and_elim_left",(0,))]
    audit=audit_proof([And(a,b)],steps,a)
    self.assertTrue(audit.accepted and audit.semantically_sound,audit)
 def test_imp_elimination_all_pairs(self):
  for a,b in product(FORMULAS,repeat=2):
   with self.subTest(a=a,b=b):
    steps=[ProofStep(Imp(a,b),"premise"),ProofStep(a,"premise"),ProofStep(b,"imp_elim",(0,1))]
    audit=audit_proof([Imp(a,b),a],steps,b)
    self.assertTrue(audit.accepted and audit.semantically_sound,audit)
 def test_or_introduction_all_pairs(self):
  for a,b in product(FORMULAS,repeat=2):
   with self.subTest(a=a,b=b):
    steps=[ProofStep(a,"premise"),ProofStep(Or(a,b),"or_intro_left",(0,))]
    audit=audit_proof([a],steps,Or(a,b))
    self.assertTrue(audit.accepted and audit.semantically_sound,audit)
 def test_double_negation_all_formulas(self):
  for a in FORMULAS:
   with self.subTest(a=a):
    steps=[ProofStep(Not(Not(a)),"premise"),ProofStep(a,"double_neg_elim",(0,))]
    audit=audit_proof([Not(Not(a))],steps,a)
    self.assertTrue(audit.accepted and audit.semantically_sound,audit)
 def test_invalid_affirm_consequent_countermodel(self):
  result=audit_proof([Imp(P,Q),Q],[ProofStep(Imp(P,Q),"premise"),ProofStep(Q,"premise"),ProofStep(P,"imp_elim",(0,1))],P)
  self.assertFalse(result.accepted)
  self.assertEqual(result.countermodel,{"P":False,"Q":True})
if __name__=="__main__":
 unittest.main()
