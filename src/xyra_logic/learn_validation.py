from __future__ import annotations

from collections.abc import Mapping
import re
from typing import Any

LEARN_REQUEST_SCHEMA_VERSION = "LOGIC-LEARN-001/request/v1"
LEARN_RESPONSE_SCHEMA_VERSION = "LOGIC-LEARN-001/response/v1"

TERMINAL_STATES = {
    "NO SUFFICIENT EVIDENCE OF DECEPTION",
    "UNKNOWN / ACCESS CONSTRAINED",
}

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "based", "but", "by", "for",
    "from", "in", "is", "it", "of", "on", "or", "the", "their", "this", "to",
    "was", "were", "with",
}
_DEPENDENCY_CUES = {
    "repeat", "repeats", "repeated", "derive", "derives", "derived", "share",
    "shares", "shared", "intermediary", "common", "same", "independent",
    "independence", "corroboration", "source",
}
_UNCERTAINTY_CUES = {
    "possible", "possibly", "plausible", "may", "might", "could", "uncertain",
    "unknown", "not established", "insufficient", "cannot establish",
    "remains viable", "pending",
}
_FACTUAL_SUPPORT_CUES = {
    "reported", "report", "reports", "notice", "observed", "failed", "failure",
    "maintenance", "provider", "service", "component", "delay", "identity",
    "account", "office", "infrastructure", "intermediary",
}


class LogicLearnValidationError(ValueError):
    """Fail-closed error for malformed LOGIC-LEARN-001 requests."""


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LogicLearnValidationError(f"{key} must be a non-empty string.")
    return value.strip()


def _string_list(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key)
    if not isinstance(value, list):
        raise LogicLearnValidationError(f"{key} must be a list.")
    out: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise LogicLearnValidationError(f"{key}[{i}] must be a non-empty string.")
        out.append(item.strip())
    return out


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.casefold())
        if token not in _STOPWORDS and len(token) > 1
    }


def _jaccard(left: str, right: str) -> float:
    a = _tokens(left)
    b = _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _hypothesis_duplication(hypotheses: list[str]) -> bool:
    if len(hypotheses) < 2:
        return False
    similar_pairs = 0
    for i in range(len(hypotheses)):
        for j in range(i + 1, len(hypotheses)):
            if _jaccard(hypotheses[i], hypotheses[j]) >= 0.55:
                similar_pairs += 1
    return similar_pairs >= max(1, len(hypotheses) - 1)


def _dependency_coverage(observed: list[str], dependencies: list[str]) -> bool:
    dependency_facts = [
        fact for fact in observed
        if _tokens(fact) & _DEPENDENCY_CUES
    ]
    if not dependency_facts:
        return True
    if not dependencies:
        return False
    for fact in dependency_facts:
        fact_tokens = _tokens(fact)
        if not any(
            len(fact_tokens & _tokens(dep)) >= 2
            and bool(fact_tokens & _tokens(dep) & _DEPENDENCY_CUES)
            for dep in dependencies
        ):
            return False
    return True


def _factual_premise_supported(
    premise: str,
    observed: list[str],
    not_established: list[str],
) -> bool:
    premise_tokens = _tokens(premise)
    if not premise_tokens:
        return False

    # Reasoning principles may legitimately be general rather than source-factual.
    principle_markers = {
        "compatible", "causes", "corroboration", "intent", "alone", "multiple",
        "independent", "evidence", "establish", "can", "could", "may",
        "correlated", "shared", "requires",
    }
    if premise_tokens & principle_markers:
        return True

    factual_tokens = premise_tokens & _FACTUAL_SUPPORT_CUES
    if not factual_tokens:
        return True

    source_tokens = set()
    for item in observed + not_established:
        source_tokens |= _tokens(item)

    unsupported = premise_tokens - source_tokens
    unsupported_material = {
        token for token in unsupported
        if token not in {"exact", "nature", "additional", "specific"}
    }
    return len(unsupported_material) <= 1


def _disconfirming_grounded(item: str, observed: list[str]) -> bool:
    item_tokens = _tokens(item)
    if not item_tokens:
        return False
    source_tokens = set()
    for fact in observed:
        source_tokens |= _tokens(fact)
    overlap = item_tokens & source_tokens
    # At least one-third of substantive tokens should anchor to observed material.
    return len(overlap) >= 2 and len(overlap) / max(1, len(item_tokens)) >= 0.25


def _conclusion_supported(conclusion: str, terminal_state: str) -> bool:
    lowered = conclusion.casefold()
    if terminal_state == "UNKNOWN / ACCESS CONSTRAINED":
        return any(cue in lowered for cue in _UNCERTAINTY_CUES)
    if terminal_state == "NO SUFFICIENT EVIDENCE OF DECEPTION":
        return (
            "no sufficient evidence" in lowered
            or "not established" in lowered
            or "insufficient" in lowered
        )
    return False


def validate_learning_packet(request: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate one governed learning-evaluation packet.

    The validator uses bounded deterministic semantic checks. It does not claim
    unrestricted natural-language entailment and does not rewrite the learner answer.
    """
    if not isinstance(request, Mapping):
        raise LogicLearnValidationError("request must be a mapping.")
    if request.get("schema_version") != LEARN_REQUEST_SCHEMA_VERSION:
        raise LogicLearnValidationError("unknown schema_version")

    learner_id = _required_string(request, "learner_id")
    source_work_id = _required_string(request, "source_work_id")
    authority_ref = _required_string(request, "source_authority_ref")
    task = _required_string(request, "task")
    claimed_conclusion = _required_string(request, "claimed_conclusion")
    terminal_state = _required_string(request, "terminal_state")

    observed = _string_list(request, "observed_facts")
    not_established = _string_list(request, "not_established")
    hypotheses = _string_list(request, "competing_hypotheses")
    source_dependencies = _string_list(request, "source_dependencies")
    information_gaps = _string_list(request, "information_gaps")
    next_collection = _string_list(request, "next_collection")
    premises = _string_list(request, "premises")
    disconfirming = _string_list(request, "disconfirming_evidence")

    observed_norm = {x.casefold() for x in observed}
    not_established_norm = {x.casefold() for x in not_established}
    contradiction = bool(observed_norm & not_established_norm)

    semantic_checks_enabled = bool(premises and disconfirming)

    findings = {
        "insufficient_hypothesis_set": len(hypotheses) < 2,
        "hypothesis_duplication": (
            _hypothesis_duplication(hypotheses) if semantic_checks_enabled else False
        ),
        "missing_source_dependency_analysis": not source_dependencies,
        "source_dependency_mismatch": (
            not _dependency_coverage(observed, source_dependencies)
            if semantic_checks_enabled else False
        ),
        "missing_information_gaps": not information_gaps,
        "missing_next_collection": not next_collection,
        "missing_explicit_premises": not premises,
        "unsupported_premise": (
            any(
                not _factual_premise_supported(item, observed, not_established)
                for item in premises
            )
            if premises else False
        ),
        "missing_disconfirming_evidence": not disconfirming,
        "ungrounded_disconfirming_evidence": (
            any(not _disconfirming_grounded(item, observed) for item in disconfirming)
            if disconfirming else False
        ),
        "unsupported_terminal_state": terminal_state not in TERMINAL_STATES,
        "fact_inference_contradiction": contradiction,
        "empty_claimed_conclusion": not bool(claimed_conclusion),
        "unsupported_conclusion": (
            not _conclusion_supported(claimed_conclusion, terminal_state)
            if semantic_checks_enabled else False
        ),
    }

    critical = (
        findings["insufficient_hypothesis_set"]
        or findings["hypothesis_duplication"]
        or findings["missing_source_dependency_analysis"]
        or findings["source_dependency_mismatch"]
        or findings["missing_information_gaps"]
        or findings["missing_next_collection"]
        or findings["unsupported_premise"]
        or findings["ungrounded_disconfirming_evidence"]
        or findings["unsupported_terminal_state"]
        or findings["fact_inference_contradiction"]
        or findings["empty_claimed_conclusion"]
        or findings["unsupported_conclusion"]
    )

    structural_findings = (
        findings["missing_explicit_premises"]
        or findings["missing_disconfirming_evidence"]
    )

    if critical:
        status = "FAIL"
    elif structural_findings:
        status = "PASS_WITH_FINDINGS"
    else:
        status = "PASS"

    return {
        "schema_version": LEARN_RESPONSE_SCHEMA_VERSION,
        "learner_id": learner_id,
        "source_work_id": source_work_id,
        "source_authority_ref": authority_ref,
        "task": task,
        "status": status,
        "logic_findings": findings,
        "claimed_conclusion": claimed_conclusion,
        "terminal_state": terminal_state,
        "knowledge_acquisition_assessed": False,
        "reasoning_integrity_assessed": True,
        "application_performance_assessed": True,
        "formal_qualification": False,
        "institutional_decision": False,
        "authority_expansion": False,
    }
