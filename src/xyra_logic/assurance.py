from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .derivation import DerivationStep, replay_derivation_step
from .expressions import (
    And,
    Atom,
    Biconditional,
    Expression,
    Implies,
    Not,
    Or,
)


REQUEST_SCHEMA_ID = "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1"
RESULT_SCHEMA_ID = "XYRA_LOGIC_REASONING_ASSURANCE_RESULT_V1"


class ReasoningAssurancePacketError(ValueError):
    """Raised when a reasoning-assurance transport packet fails closed."""


def expression_to_wire(expression: Expression) -> dict[str, Any]:
    """Serialize one supported formal expression to a transport-safe mapping."""
    if isinstance(expression, Atom):
        return {
            "type": "ATOM",
            "name": expression.name,
        }

    if isinstance(expression, Not):
        return {
            "type": "NOT",
            "operand": expression_to_wire(expression.operand),
        }

    if isinstance(expression, And):
        return {
            "type": "AND",
            "left": expression_to_wire(expression.left),
            "right": expression_to_wire(expression.right),
        }

    if isinstance(expression, Or):
        return {
            "type": "OR",
            "left": expression_to_wire(expression.left),
            "right": expression_to_wire(expression.right),
        }

    if isinstance(expression, Implies):
        return {
            "type": "IMPLIES",
            "left": expression_to_wire(expression.left),
            "right": expression_to_wire(expression.right),
        }

    if isinstance(expression, Biconditional):
        return {
            "type": "BICONDITIONAL",
            "left": expression_to_wire(expression.left),
            "right": expression_to_wire(expression.right),
        }

    raise ReasoningAssurancePacketError(
        f"Unsupported expression type: {type(expression).__name__}"
    )


def expression_from_wire(payload: Mapping[str, Any]) -> Expression:
    """Decode one supported transport-safe expression."""
    if not isinstance(payload, Mapping):
        raise ReasoningAssurancePacketError(
            "Expression payload must be a mapping."
        )

    expression_type = payload.get("type")

    if expression_type == "ATOM":
        _require_exact_keys(payload, {"type", "name"})
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ReasoningAssurancePacketError(
                "ATOM name must be a non-empty string."
            )
        return Atom(name)

    if expression_type == "NOT":
        _require_exact_keys(payload, {"type", "operand"})
        return Not(expression_from_wire(payload["operand"]))

    if expression_type in {
        "AND",
        "OR",
        "IMPLIES",
        "BICONDITIONAL",
    }:
        _require_exact_keys(payload, {"type", "left", "right"})
        left = expression_from_wire(payload["left"])
        right = expression_from_wire(payload["right"])

        if expression_type == "AND":
            return And(left, right)
        if expression_type == "OR":
            return Or(left, right)
        if expression_type == "IMPLIES":
            return Implies(left, right)
        return Biconditional(left, right)

    raise ReasoningAssurancePacketError(
        f"Unsupported expression type: {expression_type!r}"
    )


def replay_reasoning_assurance_packet(
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Decode, replay, and serialize one reasoning-assurance request."""
    if not isinstance(packet, Mapping):
        raise ReasoningAssurancePacketError(
            "Reasoning assurance packet must be a mapping."
        )

    _require_exact_keys(
        packet,
        {
            "schema_id",
            "correlation_id",
            "object_registry",
            "step",
        },
    )

    if packet["schema_id"] != REQUEST_SCHEMA_ID:
        raise ReasoningAssurancePacketError(
            f"Unknown reasoning assurance schema: {packet['schema_id']!r}"
        )

    correlation_id = packet["correlation_id"]
    if not isinstance(correlation_id, str) or not correlation_id.strip():
        raise ReasoningAssurancePacketError(
            "correlation_id must be a non-empty string."
        )

    raw_registry = packet["object_registry"]
    if not isinstance(raw_registry, Mapping):
        raise ReasoningAssurancePacketError(
            "object_registry must be a mapping."
        )

    object_registry: dict[str, Expression] = {}
    for object_id, expression_payload in raw_registry.items():
        if not isinstance(object_id, str) or not object_id.strip():
            raise ReasoningAssurancePacketError(
                "Formal object identifiers must be non-empty strings."
            )
        object_registry[object_id] = expression_from_wire(expression_payload)

    raw_step = packet["step"]
    if not isinstance(raw_step, Mapping):
        raise ReasoningAssurancePacketError(
            "step must be a mapping."
        )

    _require_exact_keys(
        raw_step,
        {
            "step_id",
            "input_object_ids",
            "rule_id",
            "proposed_output",
        },
    )

    step_id = raw_step["step_id"]
    rule_id = raw_step["rule_id"]
    raw_input_ids = raw_step["input_object_ids"]

    if not isinstance(step_id, str) or not step_id.strip():
        raise ReasoningAssurancePacketError(
            "step_id must be a non-empty string."
        )

    if not isinstance(rule_id, str) or not rule_id.strip():
        raise ReasoningAssurancePacketError(
            "rule_id must be a non-empty string."
        )

    if not isinstance(raw_input_ids, list):
        raise ReasoningAssurancePacketError(
            "input_object_ids must be a list."
        )

    input_object_ids: list[str] = []
    for object_id in raw_input_ids:
        if not isinstance(object_id, str) or not object_id.strip():
            raise ReasoningAssurancePacketError(
                "input_object_ids must contain non-empty strings."
            )
        input_object_ids.append(object_id)

    proposed_output = expression_from_wire(
        raw_step["proposed_output"]
    )

    step = DerivationStep(
        step_id=step_id,
        input_object_ids=tuple(input_object_ids),
        rule_id=rule_id,
        proposed_output=proposed_output,
    )

    result = replay_derivation_step(
        step,
        object_registry,
    )

    return {
        "schema_id": RESULT_SCHEMA_ID,
        "correlation_id": correlation_id,
        "step_id": result.step_id,
        "input_object_ids": list(result.input_object_ids),
        "rule_id": result.rule_id,
        "proposed_output": expression_to_wire(result.proposed_output),
        "status": result.status,
        "derived_output": (
            None
            if result.derived_output is None
            else expression_to_wire(result.derived_output)
        ),
        "failure_reason": result.failure_reason,
    }


def _require_exact_keys(
    payload: Mapping[str, Any],
    expected: set[str],
) -> None:
    actual = set(payload.keys())
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)

        details = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if unexpected:
            details.append("unexpected=" + ",".join(unexpected))

        raise ReasoningAssurancePacketError(
            "Malformed packet shape: " + "; ".join(details)
        )
