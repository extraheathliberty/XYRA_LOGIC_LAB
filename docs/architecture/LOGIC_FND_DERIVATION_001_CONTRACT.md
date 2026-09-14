# LOGIC-FND-DERIVATION-001
## Replayable Derivation Step Contract

Status: DESIGN CONTRACT
Scope: Single-step deterministic derivation replay
Parent capability: LOGIC-FND-RULES-001

## 1. Purpose

LOGIC-FND-DERIVATION-001 introduces the first replayable derivation
object above executable inference-rule validation.

The node records a declared reasoning step using stable object references,
resolves those references to formal expressions, and delegates formal
validation to the existing LOGIC-FND-RULES-001 rule validator.

This node does not perform proof search.

## 2. Boundary

A DerivationStep records a proposed formal transformation.

It does not determine:

- whether premises are factually supported;
- whether a natural-language formalization is correct;
- whether a rule should be selected automatically;
- whether a proof exists;
- whether an action should be taken.

Models may propose DerivationSteps.

Only deterministic Logic validates them.

## 3. DerivationStep

The initial immutable DerivationStep shall expose:

- step_id
- input_object_ids
- rule_id
- proposed_output

Conceptual form:

STEP_ID:
D3

INPUT_OBJECT_IDS:
D1
D2

RULE_ID:
PROP-MP-001

PROPOSED_OUTPUT:
Q

## 4. DerivationStepResult

Replay shall return an immutable DerivationStepResult exposing:

- step_id
- input_object_ids
- rule_id
- proposed_output
- status
- derived_output
- failure_reason

For a valid step:

STATUS:
VALID_STEP

DERIVED_OUTPUT:
licensed formal expression

FAILURE_REASON:
None

For an invalid step:

STATUS:
INVALID_STEP

DERIVED_OUTPUT:
None

FAILURE_REASON:
deterministic machine-readable reason

## 5. Replay Interface

Initial public interface:

replay_derivation_step(step, object_registry) -> DerivationStepResult

The object_registry maps stable object IDs to formal Expression objects.

Example:

D1 -> P
D2 -> P IMPLIES Q

The replay function shall:

1. read input_object_ids in declared order;
2. resolve every referenced object;
3. fail closed if any dependency is missing;
4. pass the resolved formal expressions, rule_id, and proposed_output
   to validate_rule_application(...);
5. preserve the rule validator's deterministic result;
6. return DerivationStepResult.

## 6. Dependency Resolution

Every declared input dependency must resolve.

If any input_object_id is absent from object_registry:

STATUS:
INVALID_STEP

FAILURE_REASON:
MISSING_DEPENDENCY

No guessed, repaired, reordered, or substituted dependency is permitted.

## 7. Input Order

input_object_ids are ordered.

Replay must preserve declared order exactly.

For example:

D1 -> P
D2 -> P IMPLIES Q

is not interchangeable with:

D1 -> P IMPLIES Q
D2 -> P

when applying PROP-MP-001.

## 8. Delegation to RULES-001

DERIVATION-001 shall not duplicate inference-rule semantics.

Once dependencies resolve, validation must use:

validate_rule_application(...)

LOGIC-FND-RULES-001 remains authoritative for:

- rule existence;
- arity;
- formal expression validation;
- rule-pattern matching;
- licensed output derivation;
- output comparison.

## 9. Determinism

Repeated replay of the same:

- DerivationStep;
- object_registry content;
- executable rule implementation

must produce an identical DerivationStepResult.

Replay must not depend on:

- model memory;
- conversational context;
- hidden chain of thought;
- unstated assumptions;
- external network state.

## 10. Example — Valid Replay

Registry:

D1 = P
D2 = P IMPLIES Q

Step:

STEP_ID:
D3

INPUTS:
D1
D2

RULE:
PROP-MP-001

PROPOSED_OUTPUT:
Q

Expected:

STATUS:
VALID_STEP

DERIVED_OUTPUT:
Q

FAILURE_REASON:
None

## 11. Example — Invalid Rule Application

Registry:

D1 = P IMPLIES Q
D2 = Q

Step:

STEP_ID:
D3

INPUTS:
D1
D2

RULE:
PROP-MP-001

PROPOSED_OUTPUT:
P

Expected:

STATUS:
INVALID_STEP

DERIVED_OUTPUT:
None

FAILURE_REASON:
RULE_INPUT_MISMATCH

## 12. Example — Missing Dependency

Registry:

D1 = P

Step:

STEP_ID:
D3

INPUTS:
D1
D2

RULE:
PROP-MP-001

PROPOSED_OUTPUT:
Q

Expected:

STATUS:
INVALID_STEP

DERIVED_OUTPUT:
None

FAILURE_REASON:
MISSING_DEPENDENCY

## 13. Explicit Non-Goals

This node does not implement:

- multi-step Derivation objects;
- dependency graphs;
- derived-step-to-derived-step chaining;
- assumption introduction or discharge;
- formal-system registries;
- proof search;
- automatic rule selection;
- theorem objects;
- causal reasoning;
- temporal reasoning;
- probabilistic reasoning;
- evidence evaluation;
- natural-language formalization;
- LLM calls;
- autonomous repair.

## 14. Deferred Foundation Fields

The foundational architecture also anticipates:

- FORMAL_SYSTEM_ID;
- ASSUMPTIONS_IN_SCOPE;
- METADATA.

These remain valid future requirements but are deliberately deferred from
DERIVATION-001 until corresponding formal-system and assumption machinery
exists.

Their absence from this initial runtime must not be interpreted as removal
from the foundational architecture.

## 15. Acceptance Principle

LOGIC-FND-DERIVATION-001 is qualified only when a DerivationStep can be
serialized conceptually through stable references, replayed deterministically,
and accepted or rejected without hidden context.

The implementation must fail closed on unresolved dependencies.

Models propose.

Logic replays and validates.

Humans retain authority.

## 16. Reasoning Assurance Integration Boundary

DERIVATION-001 is intended to become a reusable formal-verification primitive
for governed AI reasoning paths across the XYRA estate.

A future AIR / Logic adapter may submit declared DerivationSteps for replay.

The integration boundary is:

AI proposes reasoning.

Logic validates formal consequence.

Evidence systems determine premise standing.

Governance determines authority.

Humans retain final decision authority.

A caller must not reinterpret an INVALID_STEP as formally valid.

A VALID_STEP establishes only that the declared rule licenses the declared
output from the declared formal inputs.

VALID_STEP does not establish:

- factual truth of the premises;
- evidentiary support;
- correct natural-language formalization;
- causal truth;
- probabilistic confidence;
- operational authority;
- permission to act.

Logic validation therefore supplies formal reasoning assurance without
absorbing evidence, governance, causal, temporal, or decision authority.

Future estate integration may additionally expose states such as
OUTSIDE_CURRENT_FORMAL_CAPABILITY or UNRESOLVED.

Those states are not implemented by DERIVATION-001 and must not be fabricated
by this node.

## 17. Estate Safety Principle

Where an AI-generated reasoning path can be expressed through supported formal
objects and rules, deterministic replay should be available before that
reasoning is treated as formally validated.

Model capability does not override deterministic formal validation.

A model substitution must not change the result of replaying the same formal
step against the same Logic version.
