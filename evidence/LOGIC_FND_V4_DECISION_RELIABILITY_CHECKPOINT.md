# LOGIC-FND-V4 — Reasoning reliability and decision-readiness checkpoint

Date: 2026-11-08 UTC
Authority: Human Committee direction to make logic a central estate capability. Existing hold on Executive trials remains unchanged. No institutional authority transfers.

## Problem definition

A logical Executive must not (1) accept an invalid inference, (2) refuse to decide when a conclusion follows from adequate premises, or (3) manufacture a conclusion where premises are insufficient.

## Engineering implementation

- `reasoning_assessment.py` separately determines premise consistency and entailment in bounded classical propositional semantics. Outputs:
  - SUPPORTED: every premise-satisfying assignment supports conclusion.
  - REFUTED: every premise-satisfying assignment falsifies conclusion.
  - UNDETERMINED: both conclusion and its negation remain possible.
  - BLOCKED_CONTRADICTION: premises have no joint model; classical vacuous entailment must not be treated as decision readiness.
  - ABSTAIN: variable budget exceeded, no inference asserted.
- `decision_gate.py` maps these mathematical states to bounded advisory dispositions and always returns `action_authorized=False`.
- Tests include governance counterexamples: pilot admission does not imply production admission; institutional approval does not prove execution; observation does not confer command authority.

## Strict limits

These functions reason only over supplied formal Boolean propositions. They do NOT validate that premises are factually true, correctly sourced, current, complete or authorized. They do NOT parse natural language, measure AIR Executive competence, resolve normative conflicts, confer decisions or initiate actions. No confidence scores are invented.

## Required next gates

1. Evidence provenance and source-to-proposition traceability with signed records.
2. Epistemic status distinct from logical entailment; conflicts and missing evidence.
3. External independent oracle and rule soundness proof.
4. Executive competency benchmark design under hold, not execution.
5. Explicit Committee decision before any AIR trials, deployment or institutional integration.
