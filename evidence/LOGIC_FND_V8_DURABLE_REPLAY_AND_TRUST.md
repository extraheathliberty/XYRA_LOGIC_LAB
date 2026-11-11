# LOGIC-FND-V8 — Durable replay and issuer trust checkpoint

Date: 2026-11-08 UTC. Status: draft branch only; no live admission.

## Implementation

- `durable_replay.py`: SQLite primary-key uniqueness on issuer and nonce, transactional BEGIN IMMEDIATE insertion, process-restart persistence, concurrent admission test with eight threads and one accepted request, bounded store capacity with fail-closed behavior. Existing nonce checked before capacity denial.
- `issuer_trust.py`: explicit immutable issuer policy records with consumer scope, time window, revocation flag and nonempty governance reference. Unregistered issuers denied.
- `governed_adapter.py`: offline policy gate on signed request issuer and evidence issuers before signed evidence, source verification and durable nonce admission. All successful outcomes remain advisory, never action-authorizing.
- `test_durable_trust_v8.py`: 18 tests of restart replay, concurrency, expiry, capacity, revocation, consumer scope and governance denial.

## Trust limitations

The issuer policies are provided by the caller/operator and the governance reference is an unverified string. A malicious operator could fabricate a policy. This is NOT an independently governed trust root, Committee adoption, or delegated authority. The database assumes all cooperating processes share the same SQLite file on a filesystem with correct locking semantics. No multi-host consensus, tamper-resistant storage, trusted time, key rotation, revocation distribution, issuer enrollment workflow or replay pruning. This code has not been threat-modeled for an exposed network service.

## Required next gates

1. Committee-approved issuer admission process and independent policy attestation.
2. Durable authenticated audit trail, key lifecycle and revocation propagation.
3. Cross-process and multi-host storage acceptance tests; secure permissions and database integrity checks.
4. External proof oracle, evidence source lineage and provenance verification.
5. Consumer-specific integration review and separate Committee authorization before any live runtime admission or Executive trials.
