"""Independent *algorithmic* Boolean semantics oracle using bit-vector masks.

No imports from the production evaluator or proof checker. The oracle
shares only AST data classes, so it is not independent mathematical assurance.
"""
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff
from xyra_logic.structural_audit import inspect_formula

MAX_ORACLE_VARIABLES=10

def oracle_mask(formula, names):
    names=tuple(names)
    if len(names)>MAX_ORACLE_VARIABLES or len(set(names))!=len(names):
        raise ValueError("oracle variable budget or duplicate name")
    declared=inspect_formula(formula)
    if not declared.issubset(names):
        raise ValueError("formula has undeclared variables")
    rows=1<<len(names)
    universe=(1<<rows)-1
    masks={}
    for i,name in enumerate(names):
        bit=0
        for row in range(rows):
            if (row>>(len(names)-i-1))&1:
                bit|=1<<row
        masks[name]=bit
    def visit(f):
        if isinstance(f,Var):
            return masks[f.name]
        if isinstance(f,Not):
            return universe^visit(f.value)
        if isinstance(f,And):
            return visit(f.left)&visit(f.right)
        if isinstance(f,Or):
            return visit(f.left)|visit(f.right)
        if isinstance(f,Imp):
            return (universe^visit(f.left))|visit(f.right)
        if isinstance(f,Iff):
            return universe^(visit(f.left)^visit(f.right))
        raise TypeError("unknown AST")
    return visit(formula)

def oracle_entails(premises, conclusion):
    premises=tuple(premises)
    names=tuple(sorted(set().union(*(inspect_formula(f) for f in (*premises,conclusion)))))
    rows=1<<len(names)
    premise_mask=(1<<rows)-1
    for p in premises:
        premise_mask &= oracle_mask(p,names)
    violating=premise_mask & ~oracle_mask(conclusion,names)
    if not violating:
        return True,None
    first=(violating & -violating).bit_length()-1
    return False,{name:bool((first>>(len(names)-i-1))&1) for i,name in enumerate(names)}
