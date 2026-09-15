from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .expressions import Expression
from .rules import validate_rule_application


@dataclass(frozen=True)
class DerivationStep:
    """Immutable declaration of one formal derivation step."""

    step_id: str
    input_object_ids: tuple[str, ...]
    rule_id: str
    proposed_output: Expression


@dataclass(frozen=True)
class DerivationStepResult:
    """Immutable result of deterministically replaying one derivation step."""

    step_id: str
    input_object_ids: tuple[str, ...]
    rule_id: str
    proposed_output: Expression
    status: str
    derived_output: Expression | None
    failure_reason: str | None


def replay_derivation_step(
    step: DerivationStep,
    object_registry: Mapping[str, object],
) -> DerivationStepResult:
    """Replay one declared derivation step from stable object references."""

    resolved_inputs: list[object] = []

    for object_id in step.input_object_ids:
        if object_id not in object_registry:
            return DerivationStepResult(
                step_id=step.step_id,
                input_object_ids=step.input_object_ids,
                rule_id=step.rule_id,
                proposed_output=step.proposed_output,
                status="INVALID_STEP",
                derived_output=None,
                failure_reason="MISSING_DEPENDENCY",
            )

        resolved_inputs.append(object_registry[object_id])

    rule_result = validate_rule_application(
        step.rule_id,
        resolved_inputs,
        step.proposed_output,
    )

    return DerivationStepResult(
        step_id=step.step_id,
        input_object_ids=step.input_object_ids,
        rule_id=step.rule_id,
        proposed_output=step.proposed_output,
        status=rule_result.status,
        derived_output=rule_result.derived_output,
        failure_reason=rule_result.failure_reason,
    )
