# LOGIC-FND-V2 — mathematical assurance specification

Status: DRAFT / CI-VERIFIED ENGINEERING, NOT INDEPENDENTLY ASSURED
Executive trials: HUMAN COMMITTEE HOLD. No AIR or model execution.

## Separation of claims

1. **Syntax well-formedness**: a formula is admitted to the defined language.
2. **Semantics**: a truth assignment or finite interpretation determines a formula's truth.
3. **Satisfiability**: at least one assignment/interpretation satisfies a formula.
4. **Entailment**: no admissible interpretation makes premises true and conclusion false.
5. **Proof derivability**: a derivation consists only of authorized inference rules with valid earlier references.
6. **Soundness**: every accepted derivation preserves semantic consequence.
7. **Completeness**: every semantic consequence is derivable in a specified calculus; **not claimed** here.
8. **Consistency**: premises have a model; not equivalent to validity, since inconsistent premises classically entail anything.

## Implemented scope

- `formal_core.py`: propositional Boolean semantics, exhaustive truth assignments, countermodels, a restricted positive-rule natural-deduction checker.
- `finite_predicate.py`: fixed finite nonempty models, named relations, constants, equality, universal/existential quantifiers, variable environments, bounded assignment enumeration.
- Explicit limits: at most eight domain members, 100,000 free-variable assignments, formula recursion depth 64. These are engineering limits, not mathematical theorems.
- All model-dependent results must be labeled **fixed finite-model**, never unrestricted first-order validity.
- No function symbols, arithmetic, infinite structures, complete first-order prover, SMT/SAT external solver, or proof certificates are implemented.
- The propositional proof checker implements a **subset** of natural deduction. Rejection of a valid argument may mean the necessary rule is not supported, not that the argument is semantically invalid.

## Required next assurance

- Differential tests against a separate trusted solver or independently written semantic oracle.
- Exhaustive small-formula proof-rule soundness checks and mutation tests for false positives.
- Structural validation independent of evaluation short-circuiting; explicit malformed AST rejection.
- Complexity/resource-exhaustion limits for truth tables and proof lengths.
- Capture deterministic versions, code hashes, CI logs and independent reviewer signature.
- Review quantifier binding, variable shadowing, substitution capture, equality semantics and countermodel minimality.
- Maintain strict separation from Executive cognition, AI eligibility, runtime authority and institutional decisions.

## Evidence and deployment boundary

CI passing is necessary but not sufficient for independent mathematical assurance. The development branch and draft PR are not merged into the canonical main branch. No live AI trials or security-hold changes are authorized.
