# LOGIC-L0 DESIGN

## Purpose

LOGIC-L0 provides a small deterministic propositional-logic kernel for XYRA_LOGIC_LAB.

It evaluates formal logical structure only.

It does not determine whether propositions are factually true.

## Supported Constructs

Atomic propositions:
- P
- Q
- arbitrary symbolic proposition identifiers

Operators:
- NOT: ¬
- AND: ∧
- OR: ∨
- IMPLIES: →
- BICONDITIONAL: ↔

## Required Capabilities

1. Evaluate an expression under a supplied truth assignment.
2. Generate a complete truth table for an expression.
3. Determine whether an expression is a tautology.
4. Determine whether an expression is a contradiction.
5. Determine whether an argument is formally valid.

## Argument Validity

An argument is valid when there is no truth assignment under which:

- every premise is true; and
- the conclusion is false.

Validity does not establish factual truth.

## Explicit Non-Goals

LOGIC-L0 does not include:

- evidence evaluation
- source credibility
- typed claims
- temporal reasoning
- probabilistic reasoning
- defeasible reasoning
- natural-language interpretation
- Toronto or M5V domain logic
- autonomous factual truth determination

## Candidate Public Interface

evaluate(expression, assignment) -> bool

truth_table(expression) -> rows

is_tautology(expression) -> bool

is_contradiction(expression) -> bool

is_valid_argument(premises, conclusion) -> bool

## Determinism

For identical inputs, LOGIC-L0 must return identical outputs.

No LLM or stochastic model is permitted inside the kernel.

## Governing Principle

VALID_ARGUMENT != TRUE_PREMISES

Formal derivability and evidential support remain separate system responsibilities.
