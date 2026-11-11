"""Finite-model first-order logic, explicit closed-world interpretations.

Scope: finite nonempty domains, relation symbols, variables, constants,
Boolean connectives, equality and quantifiers. No functions, arithmetic,
infinite-domain validity, theorem completeness or authority inference.
"""
from dataclasses import dataclass
from itertools import product

MAX_DOMAIN = 8
MAX_ASSIGNMENTS = 100000

@dataclass(frozen=True)
class Term:
    name: str
    variable: bool = True

@dataclass(frozen=True)
class Atom:
    predicate: str
    terms: tuple[Term, ...]

@dataclass(frozen=True)
class Equal:
    left: Term
    right: Term

@dataclass(frozen=True)
class Neg:
    value: object

@dataclass(frozen=True)
class Conj:
    left: object
    right: object

@dataclass(frozen=True)
class Disj:
    left: object
    right: object

@dataclass(frozen=True)
class Conditional:
    left: object
    right: object

@dataclass(frozen=True)
class ForAll:
    variable: str
    body: object

@dataclass(frozen=True)
class Exists:
    variable: str
    body: object

class ModelError(ValueError):
    pass

@dataclass
class FiniteModel:
    domain: tuple
    relations: dict
    constants: dict

    def __post_init__(self):
        if not 0 < len(self.domain) <= MAX_DOMAIN or len(set(self.domain)) != len(self.domain):
            raise ModelError("domain must be unique, nonempty and bounded")
        universe = set(self.domain)
        if any(v not in universe for v in self.constants.values()):
            raise ModelError("constant outside domain")
        for name, (arity, tuples) in self.relations.items():
            if not isinstance(arity, int) or isinstance(arity, bool) or arity < 0:
                raise ModelError("invalid relation arity")
            if any(len(t) != arity or any(x not in universe for x in t) for t in tuples):
                raise ModelError(f"invalid extension for {name}")

def _term(term, model, env):
    if not isinstance(term, Term) or not term.name:
        raise ModelError("malformed term")
    mapping = env if term.variable else model.constants
    if term.name not in mapping:
        raise ModelError(f"unbound term: {term.name}")
    return mapping[term.name]

def holds(expr, model: FiniteModel, env=None, depth=0):
    if depth > 64:
        raise ModelError("formula nesting exceeds bound")
    env = {} if env is None else dict(env)
    if isinstance(expr, Atom):
        if expr.predicate not in model.relations:
            raise ModelError("undeclared predicate")
        arity, extension = model.relations[expr.predicate]
        if len(expr.terms) != arity:
            raise ModelError("predicate arity mismatch")
        return tuple(_term(t,model,env) for t in expr.terms) in extension
    if isinstance(expr, Equal):
        return _term(expr.left,model,env) == _term(expr.right,model,env)
    if isinstance(expr, Neg):
        return not holds(expr.value,model,env,depth+1)
    if isinstance(expr, Conj):
        return holds(expr.left,model,env,depth+1) and holds(expr.right,model,env,depth+1)
    if isinstance(expr, Disj):
        return holds(expr.left,model,env,depth+1) or holds(expr.right,model,env,depth+1)
    if isinstance(expr, Conditional):
        return not holds(expr.left,model,env,depth+1) or holds(expr.right,model,env,depth+1)
    if isinstance(expr, (ForAll, Exists)):
        if not expr.variable:
            raise ModelError("empty binder")
        results = []
        for member in model.domain:
            local = dict(env)
            local[expr.variable] = member
            results.append(holds(expr.body,model,local,depth+1))
        return all(results) if isinstance(expr,ForAll) else any(results)
    raise ModelError("unsupported formula")

def free_variables(expr, bound=frozenset()):
    if isinstance(expr, Atom):
        return frozenset(t.name for t in expr.terms if t.variable and t.name not in bound)
    if isinstance(expr, Equal):
        return frozenset(t.name for t in (expr.left,expr.right) if t.variable and t.name not in bound)
    if isinstance(expr, Neg):
        return free_variables(expr.value,bound)
    if isinstance(expr,(Conj,Disj,Conditional)):
        return free_variables(expr.left,bound) | free_variables(expr.right,bound)
    if isinstance(expr,(ForAll,Exists)):
        return free_variables(expr.body,bound | frozenset([expr.variable]))
    raise ModelError("unsupported formula")

def finite_entails(model, premises, conclusion):
    """Entailment only in the supplied fixed finite model, over free-variable assignments."""
    premises = tuple(premises)
    names = sorted(set().union(*(free_variables(f) for f in (*premises,conclusion))))
    if len(model.domain) ** len(names) > MAX_ASSIGNMENTS:
        raise ModelError("assignment budget exceeded")
    for values in product(model.domain,repeat=len(names)):
        env = dict(zip(names,values))
        if all(holds(p,model,env) for p in premises) and not holds(conclusion,model,env):
            return False, env
    return True, None
