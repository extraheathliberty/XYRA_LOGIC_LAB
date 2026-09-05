# Formal System Boundaries

**Project:** XYRA_LOGIC_LAB
**Program Node:** LOGIC-FND-001
**Authority:** Human Committee / CBA
**Status:** GOVERNING BOUNDARY

## 1. Purpose

This document defines the architectural boundaries between formal reasoning,
evidence handling, representation verification, application interpretation,
assurance, and Human decision authority.

Its purpose is to prevent these functions from being merged merely because
they all involve evaluation or checking.

## 2. Primary Architecture

MPal / Evidence Layer
        |
        v
Formalization Boundary
        |
        v
Logic Backbone
        |
        v
Verification / Assurance
        |
        v
Coach / Application
        |
        v
Human

Each layer answers a different class of question.

## 3. MPal / Evidence Layer

Primary question:

Is premise P supported, available, structured, traceable, and admitted?

Responsibilities may include:

- evidence acquisition;
- source identity;
- provenance;
- normalization;
- schema validation;
- availability state;
- evidence support;
- governed admission;
- retrieval;
- evidence conflict preservation;
- logging;
- telemetry.

Logic shall not silently perform these functions.

Evidence support does not establish formal validity.

## 4. Formalization Boundary

The transition from governed information into formal reasoning requires an
explicit transformation.

Conceptually:

ADMITTED EVIDENCE
        |
        v
STRUCTURED CLAIM
        |
        v
FORMALIZATION
        |
        v
FORMAL PREMISE

The mechanism responsible for formalization is not yet fixed.

Possible future mechanisms may include:

- deterministic adapters;
- governed claim contracts;
- AIR-generated candidate formalizations;
- application-specific formalizers;
- Human-reviewed transformations.

The Logic kernel must not invent factual premises merely to complete a proof.

A formal premise should remain traceable, where applicable, to the evidence or
assumption from which it was created.

## 5. Logic Backbone

Primary question:

Given P and Q under formal system S, does R follow?

Responsibilities include or may later include:

- formal syntax;
- formal semantics;
- logical operators;
- assignment evaluation;
- truth tables;
- contradiction;
- validity;
- derivability;
- proof checking;
- countermodels;
- type checking;
- formal consistency analysis.

Logic produces formal results.

Logic does not establish empirical truth by itself.

The statement:

R follows from P and Q.

must remain distinguishable from:

P and Q are factually true.

## 6. Verification

Primary question:

Does output O faithfully correspond to what it claims to represent?

Examples include:

REQUEST <-> ANSWER
DATASET <-> SUMMARY
MODEL <-> VIEW
MAP DATA <-> RENDERED MAP
CONFIGURATION <-> DISPLAYED STATE
SORT RULE <-> DISPLAYED ORDER
FORMAL RESULT <-> REPORTED RESULT

These are correspondence questions.

They are not automatically formal-logic questions.

Logic may contribute to a verification process without owning the entire
verification function.

## 7. Assurance and Audit

Verification asks:

Does X correspond to Y?

Assurance asks:

Was the required verification performed correctly under the required controls?

Audit asks:

Can an independent inspection establish what occurred, what evidence exists,
and whether required procedures and controls were satisfied?

Verification, assurance, and audit may share artifacts.

They remain distinguishable functions.

## 8. Coach / Application

Primary question:

How should a result be framed, explained, communicated, or used?

Applications may:

- request reasoning;
- propose candidate claims;
- request formalization;
- present evidence;
- explain derivations;
- surface uncertainty;
- display verification results;
- present alternatives;
- route results to Humans.

Applications do not acquire formal authority merely because they display a
formal result.

## 9. Human Authority

Primary question:

What should be decided or done?

Human authority remains distinct from:

- evidence support;
- formal validity;
- derivability;
- model confidence;
- representation verification;
- recommendation strength.

A formally valid result may inform a decision.

It does not constitute the decision.

## 10. Required Status Separation

Future systems should avoid ambiguous status terms such as simply:

VALID

Where practical, status vocabulary should identify the domain being evaluated.

Candidate examples include:

FORMALLY_VALID
FORMALLY_INVALID
FORMALLY_UNDETERMINED

EVIDENCE_SUPPORTED
EVIDENCE_DISPUTED
EVIDENCE_UNKNOWN
EVIDENCE_UNAVAILABLE

REPRESENTATION_VERIFIED
REPRESENTATION_MISMATCH
REPRESENTATION_UNVERIFIED

ASSURANCE_PASS
ASSURANCE_FAIL
ASSURANCE_UNRESOLVED

These terms are architectural candidates.

They are not yet an implemented runtime contract.

## 11. Contradiction Boundary

Formal contradiction and evidentiary conflict must remain distinguishable.

Formal contradiction may include a structure such as:

P AND NOT P

Evidence conflict may include:

SOURCE_A supports P
SOURCE_B supports NOT P

The second condition does not automatically mean the formal system itself is
inconsistent.

It may instead indicate disputed or conflicting evidence.

The evidence layer should preserve that distinction before formalization.

## 12. Uncertainty Boundary

Different forms of uncertainty belong to different layers.

Examples:

EVIDENCE UNCERTAINTY
- incomplete sources;
- disputed sources;
- missing provenance;
- unavailable information.

FORMAL UNCERTAINTY
- insufficient premises;
- underdetermined derivation;
- unresolved formal branch.

MODEL UNCERTAINTY
- probability or confidence associated with a learned model.

DECISION UNCERTAINTY
- uncertainty about consequences, preferences, or Human choices.

These forms of uncertainty shall not be collapsed into a single confidence
number without an explicit authorized model.

## 13. Governing Distinction

Evidence support is not logical validity.

Logical validity is not factual truth.

Representation fidelity is not evidence support or logical validity.

Model confidence is not formal proof.

Recommendation is not decision.

Decision authority remains Human.
