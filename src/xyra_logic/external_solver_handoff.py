"""External solver handoff manifest. Does NOT claim an external solver ran.

Produces deterministic, portable DIMACS CNF for entailment counterexamples
using exhaustive truth-table clauses, bounded to 8 variables. An external
SAT solver can independently inspect the artifact and return SAT/UNSAT.
"""
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from xyra_logic.formal_core import evaluate
from xyra_logic.structural_audit import inspect_formula

@dataclass(frozen=True)
class SolverHandoff:
    dimacs: str
    sha256: str
    variable_names: tuple[str,...]
    expected_semantics: str
    externally_verified: bool

def build_entailment_sat_handoff(premises,conclusion):
    premises=tuple(premises)
    names=tuple(sorted(set().union(*(inspect_formula(f) for f in (*premises,conclusion)))))
    if len(names)>8:
        raise ValueError("external handoff variable budget exceeded")
    clauses=[]
    for bits in product((False,True),repeat=len(names)):
        assignment=dict(zip(names,bits))
        # CNF forbids valuations that do not witness invalid entailment.
        witness=all(evaluate(p,assignment) for p in premises) and not evaluate(conclusion,assignment)
        if not witness:
            clauses.append(" ".join(str(-i if value else i) for i,value in enumerate(bits,1))+" 0")
    lines=[f"c XYRA entailment counterexample handoff; vars={','.join(names)}",
           f"p cnf {len(names)} {len(clauses)}",*clauses]
    dimacs="\n".join(lines)+"\n"
    return SolverHandoff(dimacs,sha256(dimacs.encode()).hexdigest(),names,
                         "SAT means counterexample exists; UNSAT means entailment",False)
