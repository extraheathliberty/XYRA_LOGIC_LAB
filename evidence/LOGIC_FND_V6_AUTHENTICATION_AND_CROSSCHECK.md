# LOGIC-FND-V6 — Offline evidence authentication, consumer adapters and proof cross-check

Date: 2026-11-08 UTC
Status: Draft engineering only; no live endpoint, runtime connection, merge, or admission.
Authority: bounded Human Committee development direction. Executive trial hold unchanged.

## Implemented

- `evidence_envelope.py`: canonical HMAC-SHA256 evidence envelope, keyed issuer verification and tamper detection. Binds evidence ID, issuer label, formal proposition, source digest and issue timestamp. Key must be provisioned by a trusted operator; no secrets are committed.
- `consumer_adapter.py`: offline, read-only, fail-closed adapter for the six strategic consumers. Every supplied premise requires a matching signed envelope; missing, mismatched, duplicate or invalid envelopes reject the request. No command authority.
- `proof_crosscheck.py`: accepted proof certificates are checked for bounded entailment using the separate bit-vector Boolean semantics oracle. Reports SOUNDNESS_VIOLATION if an accepted certificate has a countermodel.
- Tests: evidence envelope 15, consumer adapter 15, proof cross-check 10.

## Explicit limitations and threat model

1. HMAC verifies knowledge of a shared key, NOT independent institutional identity. An issuer name is only as trustworthy as the securely provisioned keyring and key custody.
2. `source_digest` is a claim bound into the signed envelope. The actual source bytes are NOT fetched or compared. Source authenticity, provenance chain, truth and relevance are NOT established.
3. `issued_at` is signed but NOT freshness-validated. No nonce registry, replay cache, key rotation, revocation, expiry, certificate authority, issuer delegation, signature trust root or transport authentication exists. **Replay is possible**. This adapter must not be exposed as a live trusted service.
4. The adapter binds premises to signed evidence but does not prove factual truth, mandate authority or normative decision legitimacy. Its `AssuranceResponse.authenticated` remains false, since the overall request/caller is not authenticated.
5. The proof oracle is a second algorithm, not an independently maintained mathematical implementation. No universal proof of soundness or external reviewer certification.
6. The offline adapter returns `action_authorized=False` regardless of verdict. AGCOM remains communications transport only.
7. Input and resource bounds must be tightened before any untrusted network endpoint is designed.

## Next gates

- Immutable evidence storage, source-byte hashing, provenance chain and signed issuance policy.
- Authenticated caller identity, nonces, expiry, replay rejection, key lifecycle and revocation, separately governed.
- External theorem prover oracle and independent formal proof review.
- Per-consumer contract tests and integration admission; no assumption of institutional deployment.
- Explicit Human Committee approval before AIR Executive trials or live authority-bearing integration.
