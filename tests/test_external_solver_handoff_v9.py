import unittest
from xyra_logic.formal_core import Var,Not,Imp
from xyra_logic.external_solver_handoff import build_entailment_sat_handoff
P,Q=Var("P"),Var("Q")
class TestExternalSolverHandoff(unittest.TestCase):
 def test_valid_entailment_unsat_handoff(self):
  r=build_entailment_sat_handoff([Imp(P,Q),P],Q)
  self.assertIn("p cnf 2 ",r.dimacs)
  self.assertFalse(r.externally_verified)
 def test_invalid_entailment_sat_handoff(self):
  r=build_entailment_sat_handoff([Imp(P,Q),Q],P)
  self.assertIn("p cnf 2 ",r.dimacs)
  self.assertIn("SAT means counterexample",r.expected_semantics)
 def test_deterministic(self):
  a=build_entailment_sat_handoff([P],Q)
  b=build_entailment_sat_handoff([P],Q)
  self.assertEqual(a.sha256,b.sha256)
 def test_order_independent_variable_names(self):
  r=build_entailment_sat_handoff([Q],P)
  self.assertEqual(r.variable_names,("P","Q"))
 def test_budget(self):
  with self.assertRaises(ValueError):
   build_entailment_sat_handoff([Var(f"X{i}") for i in range(9)],P)
 def test_empty_premises(self):
  self.assertTrue(build_entailment_sat_handoff([],P).dimacs.startswith("c XYRA"))
if __name__=="__main__":
 unittest.main()
