import unittest
from xyra_logic.formal_core import Var,Not,Imp
from xyra_logic.decision_gate import gate_proposition
P,Q=Var("P"),Var("Q")
class TestDecisionGate(unittest.TestCase):
 def test_supported(self):
  self.assertEqual(gate_proposition([Imp(P,Q),P],Q).disposition,"MATHEMATICALLY_SUPPORTED")
 def test_refuted(self):
  self.assertEqual(gate_proposition([Not(P)],P).disposition,"REJECT_PROPOSITION")
 def test_underdetermined(self):
  self.assertEqual(gate_proposition([P],Q).disposition,"REQUEST_EVIDENCE")
 def test_contradictory(self):
  self.assertEqual(gate_proposition([P,Not(P)],Q).disposition,"RECONCILE_PREMISES")
 def test_limit(self):
  self.assertEqual(gate_proposition([Var(f"X{i}") for i in range(11)],P).disposition,"ESCALATE_LIMIT")
 def test_no_action_authority_for_all_verdicts(self):
  cases=[([P],P),([Not(P)],P),([P],Q),([P,Not(P)],Q),([Var(f"X{i}") for i in range(11)],P)]
  for premises,conclusion in cases:
   with self.subTest(premises=premises):
    self.assertFalse(gate_proposition(premises,conclusion).action_authorized)
if __name__=="__main__":
 unittest.main()
