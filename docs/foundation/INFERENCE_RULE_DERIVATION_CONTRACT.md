# Inference Rule and Derivation Contract

**Project:** XYRA_LOGIC_LAB
**Program Node:** LOGIC-FND-003
**Track:** LOGIC-OVERALL / SHARED CORE
**Authority:** Human Committee / CBA
**Status:** DESIGN / NOT YET IMPLEMENTED
**Parent Commit:** de4f47d

## 1. Purpose

This document defines how the XYRA Logic Backbone shall represent and validate
an individual inference step.

LOGIC-FND-002 established formal objects and proof architecture.

LOGIC-FND-003 establishes the contract that determines whether a proposed
transition from formal inputs to a derived expression is permitted.

This design does not yet authorize runtime implementation.

## 2. Governing Principle

A derived expression shall not be accepted merely because it resembles a
plausible conclusion.

Every derivation step must identify:

- its formal system;
- its input expressions or prior steps;
- its inference rule;
- assumptions currently in scope;
- required side conditions;
- its proposed output;
- its validation result;
- a failure reason when invalid.

## 3. Inference Rule Contract

Every InferenceRule should eventually expose at least:

RULE_ID
RULE_NAME
FORMAL_SYSTEM_ID
INPUT_ARITY
INPUT_PATTERNS
OUTPUT_PATTERN
SIDE_CONDITIONS
ASSUMPTION_REQUIREMENTS
DESCRIPTION
VERSION

A rule is a formal transformation contract.

It is not an evidentiary judgment.

## 4. Derivation Step Contract

Every DerivationStep should eventually expose at least:

STEP_ID
FORMAL_SYSTEM_ID
INPUT_OBJECT_IDS
RULE_ID
ASSUMPTIONS_IN_SCOPE
PROPOSED_OUTPUT
VALIDATION_STATUS
FAILURE_REASON
METADATA

A step is valid only when the declared rule licenses the proposed output from
the declared inputs under the active formal system.

## 5. Canonical Rule 001 — Modus Ponens

Rule ID:

PROP-MP-001

Rule Name:

MODUS_PONENS

Input pattern:

P
P IMPLIES Q

Output pattern:

Q

Canonical form:

P
P -> Q
Therefore Q

Example valid step:

INPUT 1:
P

INPUT 2:
P -> Q

RULE:
MODUS_PONENS

PROPOSED OUTPUT:
Q

RESULT:
VALID_STEP

## 6. Invalid Modus Ponens Cases

The following must fail.

### Missing antecedent

Input:

P -> Q

Proposed output:

Q

Result:

INVALID_STEP

Reason:

MISSING_REQUIRED_INPUT

### Consequent mismatch

Input:

P
P -> Q

Proposed output:

R

Result:

INVALID_STEP

Reason:

OUTPUT_PATTERN_MISMATCH

### Affirming the consequent

Input:

P -> Q
Q

Proposed output:

P

Result:

INVALID_STEP

Reason:

RULE_INPUT_MISMATCH

The system must not reinterpret an invalid argument into a valid one merely to
produce a result.

## 7. Canonical Rule 002 — Conjunction Introduction

Rule ID:

PROP-AND-I-001

Rule Name:

CONJUNCTION_INTRODUCTION

Input pattern:

P
Q

Output pattern:

P AND Q

Example:

P
Q

Therefore:

P AND Q

## 8. Canonical Rule 003 — Conjunction Elimination Left

Rule ID:

PROP-AND-E-L-001

Rule Name:

CONJUNCTION_ELIMINATION_LEFT

Input pattern:

P AND Q

Output pattern:

P

## 9. Canonical Rule 004 — Conjunction Elimination Right

Rule ID:

PROP-AND-E-R-001

Rule Name:

CONJUNCTION_ELIMINATION_RIGHT

Input pattern:

P AND Q

Output pattern:

Q

## 10. Rule Matching

Rule validation should conceptually perform:

1. resolve the active FormalSystem;
2. resolve the declared rule;
3. resolve the referenced input objects;
4. verify input arity;
5. match inputs against rule patterns;
6. evaluate side conditions;
7. verify assumptions in scope;
8. derive the permitted output pattern;
9. compare permitted output with proposed output;
10. return VALID_STEP or INVALID_STEP.

Validation shall be deterministic.

## 11. Side Conditions

Some future rules may require conditions beyond structural input matching.

Examples may include:

- variable not free in a specified expression;
- assumption remains in scope;
- required type compatibility;
- no prohibited self-reference;
- formal-system compatibility.

LOGIC-FND-003 does not yet implement these conditions.

The architecture must nevertheless permit them.

## 12. Assumption Scope

A derivation step must not use an assumption that is outside its declared
scope.

Future proof systems may introduce and discharge assumptions.

For the current propositional shared core, assumption handling should remain
minimal and explicit.

No hidden assumptions are permitted.

## 13. Validation Result

Candidate step statuses:

VALID_STEP
INVALID_STEP
UNDETERMINED_STEP

A failure should include a specific reason where possible.

Candidate failure reasons:

UNKNOWN_RULE
FORMAL_SYSTEM_MISMATCH
INPUT_ARITY_MISMATCH
MISSING_REQUIRED_INPUT
RULE_INPUT_MISMATCH
OUTPUT_PATTERN_MISMATCH
SIDE_CONDITION_FAILED
ASSUMPTION_OUT_OF_SCOPE
MALFORMED_EXPRESSION
MISSING_DEPENDENCY

These names are provisional until implementation design is approved.

## 14. Derivation Contract

A Derivation contains one or more DerivationSteps.

A derivation is formally valid only if:

- every required dependency resolves;
- every required step is valid;
- assumption scope is respected;
- the final conclusion corresponds to the final authorized derivation result.

Conceptually:

D1: P
D2: P -> Q
D3: MODUS_PONENS(D1,D2) => Q

DERIVATION STATUS:
VALID

CONCLUSION:
Q

## 15. Replay Requirement

A derivation should eventually be replayable from its serialized formal inputs.

Replay must not depend on:

- model memory;
- conversational context;
- hidden chain of thought;
- external unstated assumptions.

The same formal inputs, rules, and system version should produce the same
validation result.

## 16. Evidence Boundary

Inference rules operate over formal expressions.

They do not determine whether a premise is factually supported.

Conceptually:

MPal / Evidence
      |
      v
Admitted Claim
      |
      v
Formal Premise
      |
      v
Inference Rule
      |
      v
Derived Expression

An evidence reference may remain attached to a Premise.

The inference engine shall not alter that reference into a credibility judgment.

## 17. Toronto EHM Relevance

The EHM Track will consume the shared rule engine rather than create a separate
Toronto-specific logic engine.

Example future EHM structure:

P:
M5V permit activity increased during period T.

Q:
M5V dwelling activity increased during period T.

R:
Residential-development activity strengthened under analytical rule A.

Formal structure:

P
Q
P AND Q
(P AND Q) -> R
Therefore R

Possible rule sequence:

CONJUNCTION_INTRODUCTION
MODUS_PONENS

The Logic Backbone determines whether R follows from the formal premises and
rule.

It does not determine whether the Toronto evidence supporting P or Q is true or
reliable.

## 18. EHM Context Guard

Two claims must not be treated as equivalent merely because their natural
language is similar.

Future EHM formalization must preserve relevant context such as:

- geography;
- time;
- measure;
- subject;
- claim type.

For example:

M5V permits increased in 2025.

and:

Toronto completions increased in 2025.

must not silently become the same proposition.

Context typing belongs at the formalization boundary and shall later integrate
with Logic without introducing Toronto-specific semantics into the kernel.

## 19. Machine Learning Boundary

A future model may propose:

- a rule to consider;
- a candidate derivation;
- a candidate output.

The formal checker determines whether the proposed step is licensed.

A machine-generated derivation receives no privileged validation status.

## 20. Failure Transparency

The checker shall reject invalid steps rather than silently repair them.

A useful formal failure result should identify:

STEP
RULE
INPUTS
PROPOSED OUTPUT
STATUS
FAILURE REASON

Example:

STEP:
D4

RULE:
MODUS_PONENS

INPUTS:
P -> Q
Q

PROPOSED OUTPUT:
P

STATUS:
INVALID_STEP

FAILURE REASON:
RULE_INPUT_MISMATCH

## 21. Initial Shared-Core Rule Set

The first implementation candidate set should remain deliberately small:

PROP-MP-001
MODUS_PONENS

PROP-AND-I-001
CONJUNCTION_INTRODUCTION

PROP-AND-E-L-001
CONJUNCTION_ELIMINATION_LEFT

PROP-AND-E-R-001
CONJUNCTION_ELIMINATION_RIGHT

Additional rules require separate design or explicit extension of this
contract.

## 22. Implementation Stop Condition

Before runtime implementation begins, LOGIC-FND-003 must answer:

- What uniquely identifies a rule?
- How are input patterns represented?
- How is output authorization determined?
- How are side conditions represented?
- How is assumption scope enforced?
- What constitutes a valid step?
- What constitutes an invalid step?
- How is failure reported?
- Can a derivation be deterministically replayed?
- Can the EHM Track consume the rule engine without adding Toronto semantics to
  the formal kernel?

## 23. Governing Outcome

The formal system should be able to move from:

P
P -> Q

to:

Q

only because a declared and machine-checkable inference rule licenses that
transition.

The target output is not merely:

TRUE

It is:

STEP:
D3

RULE:
PROP-MP-001 / MODUS_PONENS

INPUTS:
D1, D2

DERIVED:
Q

STATUS:
VALID_STEP

REPLAYABLE:
YES

This is the minimum discipline required before future AI systems are permitted
to propose more complicated reasoning.
