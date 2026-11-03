# LOGIC-EXEC-001 Runtime Lab Integration Specification

**Status:** IMPLEMENTED SPECIFICATION / LIVE AIR_001 RUN PENDING INPUT

Runtime Lab may invoke Logic Lab during Executive qualification and must preserve both the Executive's proposed deliberation and the Logic result.

## Runtime contract

Input: `LOGIC-EXEC-001/request/v1`  
Output: `LOGIC-EXEC-001/response/v1`

Runtime must not substitute Logic's `expected_vote` for the Executive's vote. The correct fail-closed behavior is:

`DELIBERATION REJECTED FOR LOGICAL INCONSISTENCY`

not:

`LOGIC LAB CHANGED THE VOTE`

## Qualification measurements

Runtime should capture:

- proposition-normalization accuracy;
- scope-preservation rate;
- criterion-applicability accuracy;
- criterion-substitution detection rate;
- contradiction-detection rate;
- vote-consistency accuracy;
- false-positive rejection rate;
- false-negative acceptance rate;
- Logic Lab intervention rate;
- final Executive paired-scope fidelity.

## AIR_001 gate

The first live integration is AIR_001 only. Logic Lab requires the actual Runtime-owned AIR_001 proposed deliberation packet before executing a historical/live qualification. Synthetic reconstruction is not a substitute for the Runtime artifact.

Automatic correction/re-deliberation remains deferred.
