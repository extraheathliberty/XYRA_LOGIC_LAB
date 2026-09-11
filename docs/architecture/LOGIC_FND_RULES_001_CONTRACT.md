# LOGIC-FND-RULES-001 Executable Inference Rule Contract

Status: IMPLEMENTATION CONTRACT
Parent authority: docs/foundation/INFERENCE_RULE_DERIVATION_CONTRACT.md
Baseline: LOGIC-L0-RESULT-001 / 47fce98

## 1. Purpose

LOGIC-FND-RULES-001 introduces deterministic execution and validation of the initial shared-core propositional inference rules defined by LOGIC-FND-003.

This node validates a declared rule application. It does not search for rules, plan proofs, repair invalid derivations, evaluate evidence, or use machine learning.

## 2. Public Operation

validate_rule_application(
    rule_id,
    inputs,
    proposed_output,
) -> RuleApplicationResult

Inputs are an ordered sequence of formal Expression objects.

Validation is deterministic.

## 3. Result Contract

RuleApplicationResult is immutable and contains:

- status
- rule_id
- rule_name
- derived_output
- failure_reason

Executable statuses for this node:

- VALID_STEP
- INVALID_STEP

UNDETERMINED_STEP remains reserved for future extensions and is not emitted by the initial deterministic rules.

For VALID_STEP:

- derived_output is the expression licensed by the declared rule.
- failure_reason is None.

For INVALID_STEP:

- derived_output is None.
- failure_reason contains a deterministic machine-readable reason.

The checker must reject invalid applications rather than silently repair them.

## 4. Initial Rule Registry

### PROP-MP-001 / MODUS_PONENS

Required ordered inputs:

1. P
2. P IMPLIES Q

Licensed output:

Q

### PROP-AND-I-001 / CONJUNCTION_INTRODUCTION

Required ordered inputs:

1. P
2. Q

Licensed output:

P AND Q

The licensed output preserves declared input order. P AND Q is not silently rewritten as Q AND P.

### PROP-AND-E-L-001 / CONJUNCTION_ELIMINATION_LEFT

Required input:

1. P AND Q

Licensed output:

P

### PROP-AND-E-R-001 / CONJUNCTION_ELIMINATION_RIGHT

Required input:

1. P AND Q

Licensed output:

Q

## 5. Deterministic Validation Order

Validation proceeds in this order:

1. resolve rule_id;
2. verify required input count;
3. verify all inputs and proposed_output are formal Expression objects;
4. structurally match inputs against the declared rule pattern;
5. derive the uniquely licensed output;
6. structurally compare licensed output with proposed_output;
7. return VALID_STEP or INVALID_STEP.

No natural-language equivalence, semantic guessing, commutative rewriting, or model judgment is permitted.

## 6. Failure Reasons

Initial executable failure reasons:

- UNKNOWN_RULE
- MISSING_REQUIRED_INPUT
- INPUT_ARITY_MISMATCH
- MALFORMED_EXPRESSION
- RULE_INPUT_MISMATCH
- OUTPUT_PATTERN_MISMATCH

For a rule requiring N inputs:

- fewer than N inputs -> MISSING_REQUIRED_INPUT
- more than N inputs -> INPUT_ARITY_MISMATCH

FORMAL_SYSTEM_MISMATCH, SIDE_CONDITION_FAILED, ASSUMPTION_OUT_OF_SCOPE, and MISSING_DEPENDENCY remain reserved for later nodes.

## 7. Required Examples

Valid Modus Ponens:

P
P -> Q
proposed Q
=> VALID_STEP

Affirming the consequent:

P -> Q
Q
proposed P
=> INVALID_STEP / RULE_INPUT_MISMATCH

Conjunction introduction:

P
Q
proposed P AND Q
=> VALID_STEP

Incorrect reordered conjunction output:

P
Q
proposed Q AND P
=> INVALID_STEP / OUTPUT_PATTERN_MISMATCH

Conjunction elimination left:

P AND Q
proposed P
=> VALID_STEP

Conjunction elimination right:

P AND Q
proposed Q
=> VALID_STEP

## 8. Replay Requirement

The same rule_id, ordered formal inputs, proposed output, and implementation version must produce the same result.

Replay must not depend on:

- model memory;
- conversational context;
- hidden chain of thought;
- unstated assumptions;
- external evidence.

## 9. Evidence Boundary

This engine determines only whether a declared formal inference rule licenses a proposed derivation step.

VALID_STEP does not establish that any premise is factually true or evidentially supported.

Evidence admission remains outside the Logic rule engine.

## 10. Machine Learning Boundary

Models and agents may propose:

- rule IDs;
- formal inputs;
- proposed outputs;
- candidate derivation steps.

They possess no validation authority.

The deterministic rule checker accepts or rejects the proposed step.

## 11. Non-Goals

This node does not implement:

- automatic rule selection;
- proof search;
- multi-step derivation objects;
- assumption introduction or discharge;
- side conditions;
- natural-language formalization;
- evidence evaluation;
- probabilistic reasoning;
- autonomous repair;
- LLM calls;
- new logical connectives.

## 12. Acceptance Gate

Implementation may proceed only against tests derived from this contract.

Completion requires:

- all four initial rules executable;
- deterministic failures;
- no silent repair;
- replayable results;
- all prior Logic-L0 tests remain green.
