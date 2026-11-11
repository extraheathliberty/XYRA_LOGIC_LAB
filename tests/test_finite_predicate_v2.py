import unittest
from xyra_logic.finite_predicate import (
 Term,Atom,Equal,Neg,Conj,Disj,Conditional,ForAll,Exists,
 FiniteModel,ModelError,holds,free_variables,finite_entails
)
x=Term("x"); y=Term("y"); a=Term("a",False)
H=lambda t: Atom("Human",(t,))
M=lambda t: Atom("Mortal",(t,))
R=lambda s,t: Atom("R",(s,t))
model=FiniteModel(("socrates","plato"),{
 "Human":(1,{("socrates",),("plato",)}),
 "Mortal":(1,{("socrates",)}),
 "R":(2,{("socrates","plato")})
},{"a":"socrates"})

class TestFinitePredicate(unittest.TestCase):
 def test_universal_false(self):
  self.assertFalse(holds(ForAll("x",M(x)),model))
 def test_existential_true(self):
  self.assertTrue(holds(Exists("x",M(x)),model))
 def test_universal_human_true(self):
  self.assertTrue(holds(ForAll("x",H(x)),model))
 def test_existential_nonmortal(self):
  self.assertTrue(holds(Exists("x",Neg(M(x))),model))
 def test_nested_exists_relation(self):
  self.assertTrue(holds(Exists("x",Exists("y",R(x,y))),model))
 def test_nested_forall_relation_false(self):
  self.assertFalse(holds(ForAll("x",ForAll("y",R(x,y))),model))
 def test_shadowed_binder(self):
  self.assertTrue(holds(ForAll("x",Exists("x",M(x))),model))
 def test_constants(self):
  self.assertTrue(holds(M(a),model))
 def test_equality(self):
  self.assertTrue(holds(Equal(x,x),model,{"x":"plato"}))
 def test_inequality(self):
  self.assertFalse(holds(Equal(x,y),model,{"x":"plato","y":"socrates"}))
 def test_implication_counterexample(self):
  self.assertFalse(holds(ForAll("x",Conditional(H(x),M(x))),model))
 def test_conjunction(self):
  self.assertTrue(holds(Conj(H(a),M(a)),model))
 def test_disjunction(self):
  self.assertTrue(holds(Disj(M(a),Neg(M(a))),model))
 def test_free_vars(self):
  self.assertEqual(free_variables(ForAll("x",R(x,y))),frozenset({"y"}))
 def test_closed_formula_free_vars(self):
  self.assertEqual(free_variables(ForAll("x",Exists("y",R(x,y)))),frozenset())
 def test_fixed_model_counterexample(self):
  valid,witness=finite_entails(model,[H(x)],M(x))
  self.assertFalse(valid)
  self.assertEqual(witness,{"x":"plato"})
 def test_fixed_model_valid_entailment(self):
  self.assertEqual(finite_entails(model,[Conj(H(x),M(x))],H(x)),(True,None))
 def test_no_premises_not_valid(self):
  self.assertFalse(finite_entails(model,[],M(x))[0])
 def test_unbound_variable_rejected(self):
  with self.assertRaises(ModelError): holds(H(x),model)
 def test_undeclared_predicate_rejected(self):
  with self.assertRaises(ModelError): holds(Atom("Unknown",(x,)),model,{"x":"plato"})
 def test_arity_mismatch_rejected(self):
  with self.assertRaises(ModelError): holds(Atom("Human",(x,y)),model,{"x":"plato","y":"socrates"})
 def test_empty_domain_rejected(self):
  with self.assertRaises(ModelError): FiniteModel((),{}, {})
 def test_duplicate_domain_rejected(self):
  with self.assertRaises(ModelError): FiniteModel(("a","a"),{}, {})
 def test_outside_constant_rejected(self):
  with self.assertRaises(ModelError): FiniteModel(("a",),{},{"z":"b"})
 def test_invalid_relation_extension_rejected(self):
  with self.assertRaises(ModelError): FiniteModel(("a",),{"P":(1,{("b",)})},{})
 def test_invalid_arity_rejected(self):
  with self.assertRaises(ModelError): FiniteModel(("a",),{"P":(-1,set())},{})
 def test_invalid_formula_rejected(self):
  with self.assertRaises(ModelError): holds("P",model)
 def test_invalid_binder_rejected(self):
  with self.assertRaises(ModelError): holds(Exists("",H(x)),model)
 def test_quantifier_does_not_mutate_environment(self):
  env={"x":"plato"}
  holds(Exists("x",M(x)),model,env)
  self.assertEqual(env,{"x":"plato"})
 def test_finite_model_not_global_validity(self):
  # All humans happen to be in this model, but this does not prove a universal logical law.
  self.assertTrue(holds(ForAll("x",H(x)),model))
  self.assertFalse(holds(ForAll("x",H(x)),FiniteModel(("outsider",),{"Human":(1,set())},{})))
if __name__=="__main__":
 unittest.main()
