# LOGIC-CC-AIR-001A
## Central-Control Routed Reasoning Assurance Packet Contract

Status: DESIGN CONTRACT
Project: XYRA_LOGIC_LAB

## 1. Purpose

LOGIC-CC-AIR-001A defines the first transport-safe reasoning-assurance
boundary between XYRA Logic and the governed Central Control / AI execution
path.

The node does not create a direct AIR-to-Logic authority channel.

Central Control remains responsible for routing, admission, correlation,
authority, escalation, and result delivery.

Logic remains responsible only for deterministic formal validation within
its supported formal capability.

## 2. Controlling Direction

Human Committee direction requires the Logic pathway to be cut into the
Central Control governed execution pipe.

The intended architecture is:

Central Control
    -> AI execution
    -> formal reasoning packet
    -> Logic
    -> assurance result
    -> Central Control

The original Logic assurance result must remain available to Central Control.

A calling AI may react to, explain, or revise after a Logic result, but it
must not replace an INVALID Logic result with its own claim of validity.

## 3. Dependency

This contract builds directly on:

- LOGIC-FND-RULES-001
- LOGIC-FND-DERIVATION-001
- implementation commit e256d1c

LOGIC-FND-DERIVATION-001 operates on native Python Expression objects.

LOGIC-CC-AIR-001A adds only the transport-safe representation required to
move equivalent formal objects across a governed service boundary.

## 4. Expression Wire Representation

Supported expression kinds are exactly those already supported by the
qualified propositional kernel:

ATOM
NOT
AND
OR
IMPLIES
BICONDITIONAL

Examples:

Atom P:

    {
      "type": "ATOM",
      "name": "P"
    }

P -> Q:

    {
      "type": "IMPLIES",
      "left": {
        "type": "ATOM",
        "name": "P"
      },
      "right": {
        "type": "ATOM",
        "name": "Q"
      }
    }

No unsupported expression type may be silently approximated.

## 5. Reasoning Assurance Request

The initial request object contains:

- schema_id
- correlation_id
- object_registry
- step

Initial schema identifier:

    XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1

object_registry maps stable formal-object identifiers to serialized
expressions.

step contains:

- step_id
- input_object_ids
- rule_id
- proposed_output

Example:

    {
      "schema_id": "XYRA_LOGIC_REASONING_ASSURANCE_REQUEST_V1",
      "correlation_id": "CC-TASK-001",
      "object_registry": {
        "D1": {
          "type": "ATOM",
          "name": "P"
        },
        "D2": {
          "type": "IMPLIES",
          "left": {
            "type": "ATOM",
            "name": "P"
          },
          "right": {
            "type": "ATOM",
            "name": "Q"
          }
        }
      },
      "step": {
        "step_id": "D3",
        "input_object_ids": ["D1", "D2"],
        "rule_id": "PROP-MP-001",
        "proposed_output": {
          "type": "ATOM",
          "name": "Q"
        }
      }
    }

## 6. Replay Semantics

The Logic adapter must:

1. validate the packet shape;
2. decode serialized expressions into existing Expression objects;
3. preserve declared object identifiers;
4. preserve declared input order;
5. construct the existing DerivationStep;
6. call replay_derivation_step;
7. preserve the resulting status, derived output, and failure reason;
8. serialize the result without changing its formal meaning.

The adapter must not duplicate inference-rule semantics.

## 7. Reasoning Assurance Result

The initial result contains:

- schema_id
- correlation_id
- step_id
- input_object_ids
- rule_id
- proposed_output
- status
- derived_output
- failure_reason

Initial schema identifier:

    XYRA_LOGIC_REASONING_ASSURANCE_RESULT_V1

Existing executable statuses remain authoritative:

- VALID_STEP
- INVALID_STEP

Existing failure reasons remain preserved.

MISSING_DEPENDENCY remains a fail-closed derivation failure.

## 8. Independence Requirement

The Logic result is an independent assurance artifact.

An AI caller may:

- consume the result;
- explain the result;
- revise reasoning after rejection;
- submit a new reasoning packet.

An AI caller may not:

- alter the original Logic result;
- convert INVALID_STEP into VALID_STEP;
- suppress a failure reason when returning the assurance artifact;
- claim formal validation without successful Logic replay.

Central Control integration must preserve this distinction.

## 9. Authority Boundary

A VALID_STEP means only that the declared formal output follows from the
declared formal inputs under the declared executable rule.

It does not establish:

- truth of premises;
- evidentiary support;
- correctness of natural-language formalization;
- causal truth;
- probabilistic confidence;
- operational authority;
- permission to act.

Human Committee authority remains final.

## 10. Fail-Closed Requirements

The adapter must fail closed for at least:

- unknown schema identifier;
- malformed expression;
- unknown expression type;
- missing required packet field;
- malformed step;
- missing dependency;
- unsupported formal construct;
- invalid rule application.

No malformed packet may be repaired by guessing.

## 11. Determinism

The same supported packet evaluated against the same Logic implementation
must produce the same formal assurance result.

Replay must not depend on:

- model memory;
- conversation history;
- hidden chain of thought;
- external network state;
- unstated assumptions.

## 12. Explicit Non-Goals

LOGIC-CC-AIR-001A does not implement:

- Central Control routing;
- authenticated transport;
- AIR runtime modification;
- AI model calls;
- reasoning generation;
- proof search;
- multi-step derivations;
- assumption discharge;
- causal logic;
- temporal logic;
- probabilistic logic;
- evidence evaluation;
- natural-language formalization;
- autonomous repair;
- execution authority.

Those require later governed nodes.

## 13. Central Control Integration Boundary

The canonical Central Control runtime is not present in the current
Chromebook environment.

Therefore this node defines and qualifies the Logic-side transport contract
only.

No claim is made that the Central Control routing splice is implemented by
LOGIC-CC-AIR-001A.

The later Central Control integration must be performed against the actual
canonical Central Control runtime and must preserve its existing admission,
authority, routing, audit, and result-return controls.

## 14. Exit Criteria

LOGIC-CC-AIR-001A may advance from contract to implementation only after
acceptance tests demonstrate:

- supported expressions round-trip exactly;
- nested expressions round-trip exactly;
- valid Modus Ponens survives serialization and replay;
- invalid rule application remains invalid;
- input order remains preserved;
- missing dependency remains fail-closed;
- unknown expression type fails closed;
- repeated identical packet replay is deterministic.


## 15. Initial Logic-Side Public Interface

The initial implementation exposes:

    expression_to_wire(expression) -> dict

    expression_from_wire(payload) -> Expression

    replay_reasoning_assurance_packet(packet) -> dict

    ReasoningAssurancePacketError

`expression_to_wire` serializes an existing supported Expression without
changing its formal structure.

`expression_from_wire` reconstructs an existing supported Expression from
the transport-safe representation.

`replay_reasoning_assurance_packet` validates and decodes one assurance
request, constructs the existing DerivationStep, delegates formal replay to
replay_derivation_step, and returns a transport-safe assurance result.

`ReasoningAssurancePacketError` is a fail-closed transport-boundary error
for malformed packets, unsupported expression representations, unknown
schema identifiers, and other failures that prevent a valid DerivationStep
from being constructed.

A missing declared derivation dependency is not a transport parsing error.
It remains an executable derivation result:

    status = INVALID_STEP
    failure_reason = MISSING_DEPENDENCY

The transport interface must not introduce or duplicate inference-rule
semantics.
