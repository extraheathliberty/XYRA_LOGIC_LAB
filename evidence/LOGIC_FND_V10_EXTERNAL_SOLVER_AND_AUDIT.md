# LOGIC-FND-V10 — Independent solver execution and durable audit checkpoint

Date: 2026-11-08 UTC
Status: DRAFT / UNMERGED / NOT DEPLOYED. Executive AI trials remain held.

## Verified engineering results

- Standard workflow: 421 discovered tests, successful, run 42489713856, head 2ee5fda0. Six Z3-specific tests are skipped in the standard environment when Z3 is not installed.
- Separate independent-solver workflow: run 42489709020 SUCCESS, Z3 version 4.13.4, six tests PASS with logged SAT/UNSAT decisions and SHA-256 of exported DIMACS inputs. The independent solver is actually executed in GitHub Actions with pinned z3-solver==4.13.4.0. This is *bounded external solver execution*, not a proof of universal soundness or completeness.
- `durable_audit.py`: transactional SQLite append, history verification, concurrent append tests, and exportable head checkpoint. Ten tests.
- `z3_verifier.py`: parses generated DIMACS, checks artifact digest, independently evaluates CNF with Z3.
- `.github/workflows/logic-external-z3.yml`: separate Z3 CI and log artifact.

## Critical limitations

- No independent external anchoring of the audit checkpoint has occurred. The checkpoint is only exportable; an authorized independent repository/service or Committee-approved archive must retain its hash and count.
- SQLite storage can be rewritten by an administrator; audit is tamper-evident only relative to a separately retained trusted checkpoint.
- Issuer attestor keys remain test-configured. No actual Human Committee attestor appointment, trust-root approval, signed roster or custody process is established.
- The Z3 test checks the generated CNF with an external solver, but the CNF generator still relies on the local evaluator. This does not independently prove the correctness of translation from real-world claims to propositions, nor the proof calculus universally.
- No live runtime admission, command authority, AGCOM transport authority, or Executive AI trial is granted.

## Committee decision required before issuer trust-root activation

Proposed, not adopted:
1. Identify two or more separately controlled authorized attestor roles, with scope limited to Logic assurance issuer admission.
2. Establish a Committee-approved roster and explicit revocation/rotation process, without transferring final Committee authority.
3. Select an independent audit checkpoint archive, access controls, retention period and integrity validation procedure.
4. Require proof of key custody separation and signed appointment evidence before accepting policy attestations as institutional authorization.

## Next gates

Committee trust-root decision; external audit checkpoint anchoring; end-to-end issuer key rotation and revocation propagation; independent source provenance; additional external solver coverage and formal soundness review.
