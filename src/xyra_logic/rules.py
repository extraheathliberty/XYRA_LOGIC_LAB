from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .expressions import And, Expression, Implies


@dataclass(frozen=True)
class RuleApplicationResult:
    """Immutable result of validating an inference rule application."""

    status: str
    rule_id: str
    rule_name: str | None
    derived_output: Expression | None
    failure_reason: str | None


@dataclass(frozen=True)
class _RuleDefinition:
    rule_id: str
    rule_name: str
    input_arity: int
    derive_output: Callable[[Sequence[Expression]], Expression | None]


def _derive_mp(inputs: Sequence[Expression]) -> Expression | None:
    premise, implication = inputs[0], inputs[1]
    if isinstance(implication, Implies) and implication.left == premise:
        return implication.right
    return None


def _derive_and_i(inputs: Sequence[Expression]) -> Expression | None:
    return And(inputs[0], inputs[1])


def _derive_and_e_l(inputs: Sequence[Expression]) -> Expression | None:
    conjunction = inputs[0]
    if isinstance(conjunction, And):
        return conjunction.left
    return None


def _derive_and_e_r(inputs: Sequence[Expression]) -> Expression | None:
    conjunction = inputs[0]
    if isinstance(conjunction, And):
        return conjunction.right
    return None


_RULES: dict[str, _RuleDefinition] = {
    "PROP-MP-001": _RuleDefinition(
        rule_id="PROP-MP-001",
        rule_name="MODUS_PONENS",
        input_arity=2,
        derive_output=_derive_mp,
    ),
    "PROP-AND-I-001": _RuleDefinition(
        rule_id="PROP-AND-I-001",
        rule_name="CONJUNCTION_INTRODUCTION",
        input_arity=2,
        derive_output=_derive_and_i,
    ),
    "PROP-AND-E-L-001": _RuleDefinition(
        rule_id="PROP-AND-E-L-001",
        rule_name="CONJUNCTION_ELIMINATION_LEFT",
        input_arity=1,
        derive_output=_derive_and_e_l,
    ),
    "PROP-AND-E-R-001": _RuleDefinition(
        rule_id="PROP-AND-E-R-001",
        rule_name="CONJUNCTION_ELIMINATION_RIGHT",
        input_arity=1,
        derive_output=_derive_and_e_r,
    ),
}


def validate_rule_application(
    rule_id: str,
    inputs: Sequence[Expression],
    proposed_output: Expression,
) -> RuleApplicationResult:
    """
    Deterministically validate a declared inference rule application step.
    """
    # 1. resolve rule_id
    rule = _RULES.get(rule_id)
    if rule is None:
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=None,
            derived_output=None,
            failure_reason="UNKNOWN_RULE",
        )

    # 2. verify required input count
    try:
        input_count = len(inputs)
    except TypeError:
        input_count = 0

    if input_count < rule.input_arity:
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=rule.rule_name,
            derived_output=None,
            failure_reason="MISSING_REQUIRED_INPUT",
        )
    if input_count > rule.input_arity:
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=rule.rule_name,
            derived_output=None,
            failure_reason="INPUT_ARITY_MISMATCH",
        )

    # 3. verify all inputs and proposed_output are formal Expression objects
    try:
        all_expressions = all(isinstance(x, Expression) for x in inputs)
    except TypeError:
        all_expressions = False

    if not all_expressions or not isinstance(proposed_output, Expression):
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=rule.rule_name,
            derived_output=None,
            failure_reason="MALFORMED_EXPRESSION",
        )

    # 4. structurally match inputs against the declared rule pattern;
    # 5. derive the uniquely licensed output;
    licensed_output = rule.derive_output(inputs)
    if licensed_output is None:
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=rule.rule_name,
            derived_output=None,
            failure_reason="RULE_INPUT_MISMATCH",
        )

    # 6. structurally compare licensed output with proposed_output;
    if licensed_output != proposed_output:
        return RuleApplicationResult(
            status="INVALID_STEP",
            rule_id=rule_id,
            rule_name=rule.rule_name,
            derived_output=None,
            failure_reason="OUTPUT_PATTERN_MISMATCH",
        )

    # 7. return VALID_STEP
    return RuleApplicationResult(
        status="VALID_STEP",
        rule_id=rule_id,
        rule_name=rule.rule_name,
        derived_output=licensed_output,
        failure_reason=None,
    )
