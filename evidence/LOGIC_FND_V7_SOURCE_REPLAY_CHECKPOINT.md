# LOGIC-FND-V7 — Source integrity and offline replay protection

Date: 2026-11-08 UTC
Status: draft, not merged, deployed or admitted. Executive trials remain held.

## Implemented
- `source_verification.py`: checks actual caller-supplied source bytes against SHA-256 digest in a verified HMAC evidence envelope, capped at 4 MiB.
- `replay_guard.py`: signed request payload binds issuer, nonce, UTC timestamp and request digest; rejects invalid signature, outside +/-300 second clock window, duplicate issuer/nonce and full replay registry. Clock is injected for deterministic testing.
- `verified_adapter.py`: offline fail-closed chain: evidence source bytes -> envelope HMAC -> proposition matching -> unique evidence IDs -> request digest bound to exact envelope signatures and source digests -> request HMAC -> replay guard -> advisory-only verdict.
- `test_source_replay_v7.py`: 27 source/replay tests.
- `test_verified_adapter_v7.py`: 15 combined-gate tests including evidence substitution under identical IDs.

## Important unresolved threats
1. ReplayGuard is process-local, non-durable and not synchronized across processes. Restart or multi-worker execution permits replay. It intentionally fails closed on capacity exhaustion. No production deployment.
2. No cryptographic key rotation, revocation, HSM, trusted issuer registry or Committee-validated delegation. HMAC possession is not institutional authorization.
3. Source bytes are supplied by caller; matching a digest establishes content integrity relative to a signed claim, NOT independent source origin, factual truth, completeness or freshness.
4. Request digest is bound to signed envelope identities and digests, but not an externally validated source chain or authorization grant.
5. The mathematical oracle is algorithmically separate, not independently reviewed or formally proven sound.
6. No network endpoint, AGCOM integration, autonomous command, runtime admission or Executive trial is implemented.

## Next engineering gates
- Durable transactional nonce store and multi-worker replay tests.
- Signed key lifecycle, issuer authorization registry and revocation.
- Independent source retrieval/provenance chain and source-to-proposition extraction assurance.
- External solver and reviewer; formal soundness arguments.
- Separate Human Committee decision for live estate admission and Executive trials.
