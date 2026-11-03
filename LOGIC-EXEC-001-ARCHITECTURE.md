# LOGIC-EXEC-001 Architecture

**Status:** IMPLEMENTED / LOCAL TESTED FOUNDATION  
**Authority:** Human Committee execution order LOGIC-EXEC-001, 3 November 2026  
**Scope:** bounded reasoning validation; non-production; no institutional decision authority

## Purpose

LOGIC-EXEC-001 adds a deterministic Executive Decision Logic Support layer to XYRA_LOGIC_LAB. It validates the structure of an Executive deliberation without selecting policy, changing a vote, or claiming factual truth.

The service sequence is:

`PROPOSITION -> CURRENT ACTION -> CURRENT THRESHOLD -> EVIDENCE ROLES -> BLOCKERS -> DOWNSTREAM/EXCLUDED CRITERIA -> EXPECTED VOTE -> CONSISTENCY CHECK`

It is intentionally distinct from the propositional L0 kernel. L0 checks formal propositional objects and derivations. LOGIC-EXEC-001 checks a governed structured decision packet for applicability, substitution, contradiction, evidence-role misuse, and vote consistency.

## Boundaries

Logic Lab may return PASS, PASS_WITH_FINDINGS, FAIL, or INDETERMINATE. It may reject a deliberation for logical inconsistency. It may not rewrite the deliberation, cast or alter a vote, authorize production, infer institutional authority, or turn a finding into a disposition.

`institutional_decision` and `authority_expansion` are hard-coded false in the response contract.

## P0 Proposition normalization

The source proposition is preserved exactly in `normalized_proposition.source_proposition`. The implementation derives conservative structural hints and accepts a caller-supplied bounded decomposition. It detects explicit scope inversions such as bounded -> unrestricted, internal -> production, and qualification -> deployment.

This is not unrestricted natural-language semantic parsing. Where a proposition cannot be safely structured, the caller must supply the governed decomposition.

## P1 Criterion applicability

The packet separates:

- decision threshold;
- necessary conditions;
- sufficient conditions;
- current-action blockers;
- downstream criteria;
- authority dependencies;
- relevant criteria;
- excluded criteria.

If the operative threshold equals a downstream or excluded criterion, the validator flags criterion substitution/threshold conflict.

## P2 Evidence roles

Evidence identifiers are preserved. Roles are either explicitly supplied or derived from bounded `target` + `polarity` metadata. Unknown cases become `INSUFFICIENT_TO_CLASSIFY`; no facts are invented.

## P3 Necessary/sufficient validation

The vote engine uses only structured current-action conditions:

- established blocker -> NO;
- failed necessary condition -> NO;
- satisfied sufficient condition -> YES;
- all necessary conditions satisfied -> YES;
- unresolved necessary condition -> ABSTAIN;
- otherwise -> ABSTAIN.

A failure of a merely sufficient condition cannot by itself become a necessary blocker.

## P4 Contradiction / criterion substitution

The service detects:

- downstream/excluded threshold substitution;
- relevant/excluded overlap without an explicit distinction;
- explicit scope expansion;
- conflicting states on the same declared condition;
- decisive use of context, irrelevant, downstream, authority-only, or unclassified evidence where it changes the vote.

## P5 Conclusion entailment

The derived expected vote is compared to the Executive's proposed vote. An unexplained mismatch is an unsupported inference. The validator reports rather than repairs.

## P6 Vote consistency

YES, NO, and ABSTAIN are checked against the Executive's own declared current criterion and evidence state. Authority ceiling and evidence sufficiency remain separate.

## P7 Integration contract

Schema versions:

- request: `LOGIC-EXEC-001/request/v1`
- response: `LOGIC-EXEC-001/response/v1`

Transport identifiers are preserved where supplied. AGCOM is transport only. Runtime Lab remains the execution/qualification owner.

## Fail-closed behavior

Malformed schema versions, choices, evidence identifiers, condition states, or packet types raise `LogicExecValidationError`. Missing structured criterion information produces `INDETERMINATE`, not a guessed conclusion.

## Deferred

Automatic repair, revoting, iterative self-correction, production deployment, and Node 3 blind-scope generalization remain outside this implementation.
