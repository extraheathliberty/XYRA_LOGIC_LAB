# LOGIC-MTA-001 — MINI TASK ASSISTANT PILOT

Project: XYRA_LOGIC_LAB
Branch: logic-mta-countermodel-001
Authority: Human Committee
Status: CANDIDATE_ONLY

## Mission

Implement structured argument-validity results with explicit countermodels.

Do not change existing propositional semantics.

## Existing Required Capabilities

- evaluate
- truth_table
- is_tautology
- is_contradiction
- is_valid_argument

All existing tests must continue to pass.

## Required Result

For:

P -> Q
Q
Therefore P

return:

STATUS: INVALID_ARGUMENT

COUNTERMODEL:
P = False
Q = True

The countermodel must independently verify that:

P -> Q = True
Q = True
P = False

## Valid Argument Requirement

For a valid argument such as:

P
P -> Q
Therefore Q

return:

STATUS: VALID_ARGUMENT
COUNTERMODEL: NONE

## Restrictions

The assistant may edit only:

- src/xyra_logic/
- tests/
- scripts/

The assistant may read:

- docs/architecture/
- docs/foundation/

Foundation documents are READ ONLY.

The assistant shall not:

- commit
- push
- merge
- alter Git history
- add Hugging Face dependencies or authentication
- add cloud API credentials
- use an LLM to decide formal validity
- silently repair invalid arguments
- expand architecture beyond this task

## Acceptance

1. Existing tests remain green.
2. New countermodel tests pass.
3. Invalid arguments return a real defeating assignment.
4. Valid arguments return no countermodel.
5. Results are deterministic.
6. Countermodels can be re-evaluated by LOGIC-L0.
7. A small terminal screen demo is included.

## Required Screen Demo

The repo should be able to display approximately:

=== XYRA LOGIC COUNTERMODEL DEMO ===

Premise 1: P -> Q
Premise 2: Q
Conclusion: P

Result: INVALID_ARGUMENT

Countermodel:
P = False
Q = True

Verification:
Premise 1 = True
Premise 2 = True
Conclusion = False

COUNTERMODEL VERIFIED

The assistant's work remains CANDIDATE_ONLY until human review.
