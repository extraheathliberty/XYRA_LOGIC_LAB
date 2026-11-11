"""Differential oracle checks on exhaustively enumerated small formulas."""
import unittest
from itertools import product
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff,evaluate,valid,countermodels,valuations
from xyra_logic.bitset_oracle import oracle_mask,oracle_entails

P,Q=Var("P"),Var("Q")
BASE=(P,Q,Not(P),Not(Q))
FORMULAS=BASE+tuple(op(a,b) for op in (And,Or,Imp,Iff) for a,b in product(BASE,repeat=2))

class TestBitsetOracle(unittest.TestCase):
 def test_formula_truth_vectors_differential(self):
  names=("P","Q")
  for f in FORMULAS:
   with self.subTest(formula=f):
    mask=oracle_mask(f,names)
    expected=[bool((mask>>i)&1) for i in range(4)]
    observed=[evaluate(f,env) for env in valuations((P,Q))]
    self.assertEqual(expected,observed)
 def test_entailment_pairwise_differential(self):
  for premise in FORMULAS:
   for conclusion in FORMULAS:
    with self.subTest(p=premise,c=conclusion):
     result,witness=oracle_entails([premise],conclusion)
     self.assertEqual(result,valid([premise],conclusion))
     if witness is not None:
      self.assertTrue(evaluate(premise,witness))
      self.assertFalse(evaluate(conclusion,witness))
 def test_two_premise_differential_sample(self):
  for p in BASE:
   for q in BASE:
    for c in FORMULAS:
     result,witness=oracle_entails([p,q],c)
     self.assertEqual(result,valid([p,q],c))
 def test_tautology_empty_premises(self):
  self.assertEqual(oracle_entails([],Or(P,Not(P))),(True,None))
 def test_non_tautology_witness(self):
  result,witness=oracle_entails([],P)
  self.assertFalse(result)
  self.assertFalse(witness["P"])
 def test_invalid_affirm_consequent(self):
  result,witness=oracle_entails([Imp(P,Q),Q],P)
  self.assertFalse(result)
  self.assertEqual(witness,{"P":False,"Q":True})
 def test_inconsistent_premises(self):
  self.assertEqual(oracle_entails([P,Not(P)],Q),(True,None))
 def test_reject_duplicate_names(self):
  with self.assertRaises(ValueError): oracle_mask(P,("P","P"))
 def test_reject_undeclared_name(self):
  with self.assertRaises(ValueError): oracle_mask(Q,("P",))
 def test_reject_budget(self):
  with self.assertRaises(ValueError): oracle_mask(P,tuple(f"X{i}" for i in range(11)))
if __name__=="__main__":
 unittest.main()
