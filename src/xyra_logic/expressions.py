from __future__ import annotations

from dataclasses import dataclass


class Expression:
    """Base type for LOGIC-L0 propositional expressions."""


@dataclass(frozen=True)
class Atom(Expression):
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Atom name must be a non-empty string.")


@dataclass(frozen=True)
class Not(Expression):
    operand: Expression


@dataclass(frozen=True)
class And(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Or(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Implies(Expression):
    left: Expression
    right: Expression


@dataclass(frozen=True)
class Biconditional(Expression):
    left: Expression
    right: Expression
