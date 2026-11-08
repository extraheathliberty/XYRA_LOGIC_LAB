"""Structural formula validation independent of truth-value short circuiting."""
from xyra_logic.formal_core import Var,Not,And,Or,Imp,Iff

class FormulaStructureError(ValueError):
    pass

def inspect_formula(expr, *, max_nodes=10000, max_depth=128):
    stack=[(expr,0)]
    seen=set()
    count=0
    names=set()
    while stack:
        node,depth=stack.pop()
        count+=1
        if count>max_nodes or depth>max_depth:
            raise FormulaStructureError("formula size/depth limit exceeded")
        if isinstance(node,Var):
            if not isinstance(node.name,str) or not node.name:
                raise FormulaStructureError("invalid variable name")
            names.add(node.name)
        elif isinstance(node,Not):
            stack.append((node.value,depth+1))
        elif isinstance(node,(And,Or,Imp,Iff)):
            stack.extend([(node.left,depth+1),(node.right,depth+1)])
        else:
            raise FormulaStructureError("unsupported formula node")
    return frozenset(names)
