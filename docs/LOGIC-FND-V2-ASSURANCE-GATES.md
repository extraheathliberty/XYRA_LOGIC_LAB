# LOGIC-FND-V2 — Qualification and Independent Assurance Gates

Status: DEVELOPMENT / NOT ADMITTED. Authority: Human Committee; Executive trials remain ON HOLD under 2026-11-07 direction.

## Scope and claims

- Propositional truth-table entailment is exhaustive only within the configured atom bound; it is not unrestricted first-order completeness.
- First-order interpretations currently evaluate explicit finite nonempty domains and finite predicate extensions.
- The proof checker supports a limited, enumerated set of propositional rules. It is not a complete natural deduction calculus.
- Quantifier substitution rejects capture; quantifier instantiation is a syntax operation. No unrestricted first-order proof checker is claimed.
- A green GitHub Actions run is implementation regression evidence, **not independent assurance**.
- No Executive AIR-001–008 reasoning qualification has been performed under this development directive.

## Qualification work packages

**FND-01: Formal specification.** Define syntax, semantics, scoping, admissible substitutions, proof judgements, assumptions and discharge, consistency, and theorem statements. Require an explicit supported-fragment manifest.

**FND-02: Soundness.** Independently enumerate bounded interpretations and cross-check every implemented proof rule. Include adversarial substitution/capture, invalid rule, dangling reference, inconsistent premises, and false proof certificate fixtures. Counterexamples must be retained.

**FND-03: Completeness.** Distinguish (a) exhaustive propositional entailment within atom limits, (b) proof-calculus completeness for an explicitly defined fragment, and (c) unrestricted first-order validity. Do not claim (c) from finite enumeration or a bounded checker. Any formal theorem must specify its logic, axioms, inference rules, and metatheory.

**FND-04: Independent assurance.** A separate reviewer or independently implemented oracle must validate specifications, fixtures, proof checker, and countermodels. Preserve reviewer identity, versioned evidence, independent execution logs, commit SHAs, discrepancies, and sign-off. Authors cannot self-certify independence.

**FND-05: Executive competence (BLOCKED).** Prepare but do not execute AIR-001–008 blind tasks, fixed scoring rubrics, proposition fidelity tests, contradiction and abstention cases, and per-Executive reporting. Human Committee release of the Executive-trial hold is a prerequisite. Competence cannot be inferred from deterministic engine CI.

## Release conditions

1. CI green on exact proposed SHA, with archived logs and reproducible test command.
2. Independent assurance findings resolved or explicitly escalated.
3. Formal claims narrowed to independently demonstrated scope.
4. No merge, production promotion, AI admission, or Executive trial solely from this document.
5. Human Committee retains final reserved authority.
