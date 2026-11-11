# LOGIC-TRUST-ROOT-001 — Proposed Committee-controlled trust-root design

Status: ENGINEERING DESIGN ONLY / NOT COMMITTEE ADOPTED
Date: 2026-11-08

## Institutional separation

The Human Committee retains final and supreme authority. Central Control may coordinate within delegated scope but cannot create or approve new issuer authorities by software configuration. Logic is an advisory assurance service, not a command plane. AGCOM may transport authenticated evidence without granting authority.

## Proposed approval workflow

1. Human Committee adopts a named attestor roster with independently controlled identities, explicit scope, effective date, expiry and revocation rules. No names or appointments are inferred here.
2. Committee authorizes a policy-signing key custodian and an independent audit-anchor custodian, with documented custody separation.
3. Proposed issuer policies include immutable issuer ID, consumer scopes, validity, revocation, version and Committee decision reference. Attestors verify the decision source before signing the canonical policy digest.
4. At least two authorized distinct attestors sign the exact policy digest. A trusted, separately authenticated Committee roster determines which keys count; possession of two keys alone is insufficient.
5. A policy registrar validates the roster and signatures, records an append-only admission event and publishes an independently retained checkpoint. Unknown issuers fail closed.
6. Key rotation and revocation require a new authorized policy version; previously issued evidence remains subject to explicit historical validation rules.
7. Every authorization decision is auditable. The Human Committee may suspend admission immediately; runtime authorization and Executive AI trials remain separately gated.

## Explicitly unresolved

No Committee-appointed attestors, institutional root key, independent archive, signed roster, key custody, key revocation distribution or live consumer admission is established by this design. The V9 dual-key verifier is a technical component only.

## Admission criteria

Committee decision evidence, verified independent attestor identity/custody, policy-to-decision provenance, durable externally anchored audit, fail-closed negative tests, independent security review, and separate runtime admission authorization.
