import unittest
from xyra_logic.formal_core import (
    Var, Not, And, Or, Imp, Iff, ProofStep,
    variables, evaluate, valuations, countermodels, valid, satisfiable, check_proof,
)
P, Q, R = Var("P"), Var("Q"), Var("R")

class TestFormalCore(unittest.TestCase):
    def test_truth_table_implication(self):
        self.assertEqual([evaluate(Imp(P,Q), a) for a in valuations([P,Q])],
                         [True, True, False, True])
    def test_iff(self):
        self.assertEqual([evaluate(Iff(P,Q), a) for a in valuations([P,Q])],
                         [True, False, False, True])
    def test_de_morgan(self):
        self.assertTrue(valid([], Iff(Not(And(P,Q)), Or(Not(P), Not(Q)))))
    def test_double_negation(self):
        self.assertTrue(valid([], Iff(Not(Not(P)), P)))
    def test_excluded_middle(self):
        self.assertTrue(valid([], Or(P,Not(P))))
    def test_noncontradiction(self):
        self.assertFalse(satisfiable([And(P,Not(P))]))
    def test_consistent_premises(self):
        self.assertTrue(satisfiable([Imp(P,Q),P,Q]))
    def test_modus_ponens(self):
        self.assertTrue(valid([Imp(P,Q),P],Q))
    def test_modus_tollens(self):
        self.assertTrue(valid([Imp(P,Q),Not(Q)],Not(P)))
    def test_affirming_consequent_countermodel(self):
        self.assertEqual(countermodels([Imp(P,Q),Q],P),[{"P":False,"Q":True}])
    def test_denying_antecedent_countermodel(self):
        self.assertEqual(countermodels([Imp(P,Q),Not(P)],Not(Q)),[{"P":False,"Q":True}])
    def test_pilot_not_production(self):
        self.assertEqual(countermodels([P],Q),[{"P":True,"Q":False}])
    def test_empty_premise_tautology(self):
        self.assertTrue(valid([], Imp(P,P)))
    def test_empty_premise_nontautology(self):
        self.assertFalse(valid([], P))
    def test_empty_formula_set_satisfiable(self):
        self.assertTrue(satisfiable([]))
    def test_variable_rejection(self):
        with self.assertRaises(ValueError):
            variables(Var(""))
    def test_bad_formula_rejection(self):
        with self.assertRaises(TypeError):
            variables("P")
    def test_nonbool_truth_assignment_rejection(self):
        with self.assertRaises(TypeError):
            evaluate(P,{"P":1})
    def test_valid_proof_mp(self):
        proof=[ProofStep(Imp(P,Q),"premise"),ProofStep(P,"premise"),
               ProofStep(Q,"imp_elim",(0,1))]
        self.assertTrue(check_proof([Imp(P,Q),P],proof,Q))
    def test_invalid_proof_affirm_consequent(self):
        proof=[ProofStep(Imp(P,Q),"premise"),ProofStep(Q,"premise"),
               ProofStep(P,"imp_elim",(0,1))]
        self.assertFalse(check_proof([Imp(P,Q),Q],proof,P))
    def test_invalid_forward_reference(self):
        self.assertFalse(check_proof([P],[ProofStep(P,"premise",(1,))],P))
    def test_invalid_negative_reference(self):
        self.assertFalse(check_proof([P],[ProofStep(P,"premise",(-1,))],P))
    def test_invalid_bool_reference(self):
        self.assertFalse(check_proof([P],[ProofStep(P,"premise",(True,))],P))
    def test_and_intro_elim(self):
        proof=[ProofStep(P,"premise"),ProofStep(Q,"premise"),
               ProofStep(And(P,Q),"and_intro",(0,1)),
               ProofStep(Q,"and_elim_right",(2,))]
        self.assertTrue(check_proof([P,Q],proof,Q))
    def test_or_intro(self):
        self.assertTrue(check_proof([P],[ProofStep(P,"premise"),
                        ProofStep(Or(P,Q),"or_intro_left",(0,))],Or(P,Q)))
    def test_double_neg_elim(self):
        self.assertTrue(check_proof([Not(Not(P))],[ProofStep(Not(Not(P)),"premise"),
                        ProofStep(P,"double_neg_elim",(0,))],P))
    def test_unknown_rule_fails(self):
        self.assertFalse(check_proof([P],[ProofStep(P,"magical")],P))
    def test_unjustified_conclusion_fails(self):
        self.assertFalse(check_proof([P],[ProofStep(P,"premise")],Q))
    def test_empty_proof_fails(self):
        self.assertFalse(check_proof([P],[],P))
    def test_implication_chain(self):
        self.assertTrue(valid([Imp(P,Q),Imp(Q,R),P],R))

if __name__=="__main__":
    unittest.main()
