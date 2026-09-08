# LOGIC-L0-RESULT-001
## Structured Argument Result and Deterministic Countermodel Contract

### Status

DESIGN CONTRACT

### Purpose

Extend LOGIC-L0 argument validity with deterministic, machine-readable
result evidence while preserving the existing Boolean validity API.

The new capability does not determine factual truth, evidence quality,
source credibility, or real-world correctness.

### Existing API

The existing public API remains unchanged:

    is_valid_argument(premises, conclusion) -> bool

Its semantics remain:

An argument is valid iff no truth assignment makes every premise true
while making the conclusion false.

### New Public API

    analyze_argument(premises, conclusion) -> ArgumentResult

### ArgumentResult

ArgumentResult is an immutable result object with these fields:

    status
    countermodel
    premise_values
    conclusion_value

Permitted status values are:

    VALID_ARGUMENT
    INVALID_ARGUMENT

### Valid Argument Result

For a valid argument:

    status = VALID_ARGUMENT
    countermodel = None
    premise_values = None
    conclusion_value = None

No arbitrary satisfying assignment is returned for a valid argument.

### Invalid Argument Result

For an invalid argument:

    status = INVALID_ARGUMENT

A deterministic countermodel must be returned.

The countermodel is an immutable ordered sequence of:

    (atom_name, bool)

pairs.

Atom names must appear in deterministic sorted order.

The result must also contain:

    premise_values = tuple[bool, ...]

in the same order as the supplied premises, and:

    conclusion_value = False

### Countermodel Witness Requirement

Every returned countermodel must independently replay such that:

1. every supplied premise evaluates to True;
2. the conclusion evaluates to False;
3. premise_values exactly matches those premise evaluations;
4. conclusion_value exactly matches conclusion evaluation.

A proposed assignment that does not satisfy these conditions is not a
countermodel.

### Determinism

When multiple countermodels exist, analyze_argument must return the first
countermodel produced by the existing deterministic assignment enumeration.

Repeated calls with identical formal inputs must return identical results.

### Compatibility

The existing Boolean API must retain its current public behavior.

For every argument:

    is_valid_argument(premises, conclusion) is True

iff:

    analyze_argument(premises, conclusion).status == VALID_ARGUMENT

### Non-Goals

LOGIC-L0-RESULT-001 does not add:

- new logical connectives;
- inference-rule execution;
- proof derivations;
- natural-language explanations;
- LLM calls;
- evidence evaluation;
- factual truth judgments;
- source credibility judgments;
- probabilistic reasoning;
- autonomous repair of invalid arguments.

### Governing Boundary

LLMs or other systems may propose arguments or candidate countermodels.

LOGIC-L0 remains the deterministic authority for whether a supplied
assignment is a valid defeating witness.

VALID_ARGUMENT does not mean TRUE_PREMISES.
INVALID_ARGUMENT does not mean FALSE_CLAIMS.
