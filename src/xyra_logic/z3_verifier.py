"""Independent Z3 execution of exported DIMACS, opt-in external CI job.

Requires z3-solver installed in the external verification workflow.
No local evaluator is used to decide SAT/UNSAT in this module.
"""
import hashlib
from xyra_logic.external_solver_handoff import build_entailment_sat_handoff

def verify_with_z3(premises,conclusion):
    import z3
    artifact=build_entailment_sat_handoff(premises,conclusion)
    if hashlib.sha256(artifact.dimacs.encode()).hexdigest()!=artifact.sha256:
        raise ValueError("handoff digest mismatch")
    lines=[line for line in artifact.dimacs.splitlines() if line and not line.startswith("c")]
    header=lines.pop(0).split()
    if len(header)!=4 or header[:2]!=["p","cnf"]:
        raise ValueError("invalid DIMACS header")
    n=int(header[2]);m=int(header[3])
    if len(lines)!=m or n!=len(artifact.variable_names):
        raise ValueError("DIMACS count mismatch")
    variables=[z3.Bool(f"v{i}") for i in range(1,n+1)]
    solver=z3.Solver()
    for line in lines:
        tokens=[int(v) for v in line.split()]
        if not tokens or tokens[-1]!=0 or any(v==0 or abs(v)>n for v in tokens[:-1]):
            raise ValueError("invalid DIMACS clause")
        solver.add(z3.Or(*[(variables[abs(v)-1] if v>0 else z3.Not(variables[abs(v)-1])) for v in tokens[:-1]]))
    result=solver.check()
    if result==z3.unknown:
        raise RuntimeError("external solver inconclusive")
    return {"solver":"z3","version":z3.get_version_string(),"status":"SAT" if result==z3.sat else "UNSAT",
            "handoff_sha256":artifact.sha256,"variable_names":artifact.variable_names}
