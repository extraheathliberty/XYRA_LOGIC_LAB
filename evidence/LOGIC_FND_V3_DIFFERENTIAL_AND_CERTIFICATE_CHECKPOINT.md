# LOGIC-FND-V3 — Differential semantics and proof-certificate checkpoint

Date: 2026-11-08 UTC
Authority: Human Committee delegated latitude for bounded Logic Lab development. Prior explicit Executive-trial HOLD remains effective; no AIR trials, ballots or Executive evaluation performed.
Status: draft PR #22, unmerged.

## Engineering additions

1. `bitset_oracle.py`: Boolean bit-vector semantics, implemented separately from the production evaluator; shares formula AST classes and structural audit. Evaluates truth vectors and produces entailment countermodels.
2. `test_bitset_oracle_v3.py`: differential checks over 68 formulas (four atomic/negated, 64 binary combinations), all pairwise single-premise entailments, sampled two-premise entailments and invalid inference witnesses. Test method count is not the number of evaluated cases.
3. `proof_certificate.py`: versioned canonical JSON serialization, SHA-256 content digest, replay against the restricted proof checker, canonical encoding enforcement and tamper detection.
4. `test_proof_certificate_v3.py`: fifteen certificate tests, including corrupted bytes, wrong digest, extra fields, wrong rule, wrong conclusion and malformed syntax.
5. `test_inference_mutation_controls_v3.py`: ten negative controls for common invalid inference patterns, including pilot-to-production authority confusion and contradictory premises.
6. `decision_api.py`: explicit VALID, INVALID and INCONCLUSIVE outcomes. Resource exhaustion cannot silently become a validity claim.
7. `test_decision_api_v3.py`: eight tests of verdicts, witnesses, resource budgets and metadata.

## Assurance interpretation

- The bit-vector oracle is algorithmically distinct, but shares the AST and structural validation implementation. It is NOT an external independently maintained theorem prover.
- SHA-256 certificate hashes detect content changes but DO NOT authenticate authorship, certify truth or convey institutional authority.
- A replayed certificate can be accepted by the restricted checker without proving the checker universally sound.
- VALID refers only to exhaustive propositional Boolean entailment within configured variable limits. Fixed finite-model predicate results remain separate.
- Classical explosion from inconsistent premises is mathematical semantics, not permission to treat contradictory evidence as reliable.
- Passing CI does not establish that any AIR Executive can reason.

## Next independent assurance gates

External reference solver differential tests; proof-rule soundness proof; proof-certificate schema hardening and threat modeling; bounded proof search; predicate substitution and capture-avoidance; performance testing; Committee-controlled release of Executive trials only if explicitly directed.
