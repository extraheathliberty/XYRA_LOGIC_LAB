from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
import re
from typing import Any

REQUEST_SCHEMA_VERSION = "LOGIC-EXEC-001/request/v1"
RESPONSE_SCHEMA_VERSION = "LOGIC-EXEC-001/response/v1"

CHOICES = {"YES", "NO", "ABSTAIN"}
CONDITION_STATES = {"SATISFIED", "NOT_SATISFIED", "UNKNOWN"}
EVIDENCE_ROLES = {
    "SUPPORTS_CURRENT_ACTION",
    "BLOCKS_CURRENT_ACTION",
    "SUPPORTS_DOWNSTREAM_ACTION",
    "BLOCKS_DOWNSTREAM_ACTION",
    "AUTHORITY_CONSTRAINT",
    "CONTEXT_ONLY",
    "IRRELEVANT_TO_CURRENT_PROPOSITION",
    "INSUFFICIENT_TO_CLASSIFY",
}

_NORMALIZED_FIELDS = (
    "action",
    "subject",
    "scope",
    "environment",
    "decision_type",
    "authority_level",
    "timing",
    "reversibility",
)

_SCOPE_MARKERS = {
    "bounded": {"bounded"},
    "unrestricted": {"unrestricted"},
    "internal": {"internal", "non-production", "nonproduction"},
    "production": {"production"},
    "qualification": {"qualification", "qualify"},
    "deployment": {"deployment", "deploy"},
}


class LogicExecValidationError(ValueError):
    """Fail-closed error for malformed LOGIC-EXEC-001 requests."""


def _norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LogicExecValidationError(f"{field} must be a non-empty string.")
    return value


def _string_or_empty(value: Any, field: str) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise LogicExecValidationError(f"{field} must be a string.")
    return value


def _marker_set(text: str) -> set[str]:
    lowered = _norm(text)
    found: set[str] = set()
    for marker, words in _SCOPE_MARKERS.items():
        if any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in words):
            found.add(marker)
    if "non-production" in lowered or "nonproduction" in lowered:
        found.discard("production")
        found.add("internal")
    return found


def normalize_proposition(
    proposition: str,
    decomposition: Mapping[str, Any] | None = None,
) -> tuple[dict[str, str], bool]:
    """
    Produce a conservative deterministic proposition representation.

    The source proposition is always preserved exactly. Supplied decomposition
    fields may refine the representation but may not silently replace the source.
    """
    proposition = _nonempty_string(proposition, "proposition")
    if decomposition is None:
        decomposition = {}
    if not isinstance(decomposition, Mapping):
        raise LogicExecValidationError("proposition_decomposition must be a mapping.")

    words = re.findall(r"[A-Za-z0-9_-]+", proposition)
    derived = {
        "action": words[0].lower() if words else "",
        "subject": " ".join(words[1:]) if len(words) > 1 else "",
        "scope": "",
        "environment": "",
        "decision_type": "",
        "authority_level": "",
        "timing": "",
        "reversibility": "",
    }

    markers = _marker_set(proposition)
    if "bounded" in markers:
        derived["scope"] = "bounded"
    elif "unrestricted" in markers:
        derived["scope"] = "unrestricted"

    if "internal" in markers:
        derived["environment"] = "internal"
    elif "production" in markers:
        derived["environment"] = "production"

    if "qualification" in markers:
        derived["decision_type"] = "qualification"
    elif "deployment" in markers:
        derived["decision_type"] = "deployment"

    lowered = _norm(proposition)
    if "human committee" in lowered:
        derived["authority_level"] = "human_committee"
    elif "executive" in lowered:
        derived["authority_level"] = "executive"

    if re.search(r"\b(next|another)\b", lowered):
        derived["timing"] = "next_cycle"
    elif re.search(r"\b(current|now)\b", lowered):
        derived["timing"] = "current"

    if "irreversible" in lowered:
        derived["reversibility"] = "irreversible"
    elif "reversible" in lowered:
        derived["reversibility"] = "reversible"

    normalized: dict[str, str] = {"source_proposition": proposition}
    for field in _NORMALIZED_FIELDS:
        if field in decomposition:
            normalized[field] = _string_or_empty(
                decomposition[field],
                f"proposition_decomposition.{field}",
            )
        else:
            normalized[field] = derived[field]

    normalized_markers = _marker_set(" ".join(normalized[f] for f in _NORMALIZED_FIELDS))
    source_markers = markers

    scope_expansion = False
    incompatible_pairs = (
        ("bounded", "unrestricted"),
        ("internal", "production"),
        ("qualification", "deployment"),
    )
    for source_marker, normalized_marker in incompatible_pairs:
        if source_marker in source_markers and normalized_marker in normalized_markers:
            scope_expansion = True

    return normalized, scope_expansion


def _normalize_state(value: Any, field: str) -> str:
    if value is None:
        return "UNKNOWN"
    if not isinstance(value, str):
        raise LogicExecValidationError(f"{field}.state must be a string.")
    state = value.strip().upper()
    aliases = {
        "TRUE": "SATISFIED",
        "PASS": "SATISFIED",
        "FALSE": "NOT_SATISFIED",
        "FAIL": "NOT_SATISFIED",
        "UNRESOLVED": "UNKNOWN",
        "INDETERMINATE": "UNKNOWN",
    }
    state = aliases.get(state, state)
    if state not in CONDITION_STATES:
        raise LogicExecValidationError(
            f"{field}.state must be one of {sorted(CONDITION_STATES)}."
        )
    return state


def _normalize_conditions(items: Any, field: str) -> list[dict[str, str]]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise LogicExecValidationError(f"{field} must be a list.")

    result: list[dict[str, str]] = []
    for index, item in enumerate(items):
        item_field = f"{field}[{index}]"
        if isinstance(item, str):
            statement = _nonempty_string(item, item_field)
            result.append(
                {
                    "id": f"{field.upper()}-{index + 1}",
                    "statement": statement,
                    "state": "UNKNOWN",
                }
            )
            continue

        if not isinstance(item, Mapping):
            raise LogicExecValidationError(
                f"{item_field} must be a string or mapping."
            )

        statement = _nonempty_string(item.get("statement"), f"{item_field}.statement")
        condition_id = item.get("id", statement)
        condition_id = _nonempty_string(condition_id, f"{item_field}.id")
        state = _normalize_state(item.get("state"), item_field)
        result.append(
            {
                "id": condition_id,
                "statement": statement,
                "state": state,
            }
        )
    return result


def _normalize_string_list(items: Any, field: str) -> list[str]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise LogicExecValidationError(f"{field} must be a list.")
    out = []
    for index, item in enumerate(items):
        out.append(_nonempty_string(item, f"{field}[{index}]"))
    return out


def derive_criterion_analysis(request: Mapping[str, Any]) -> dict[str, Any]:
    raw = request.get("criterion_analysis") or {}
    if not isinstance(raw, Mapping):
        raise LogicExecValidationError("criterion_analysis must be a mapping.")

    decomposition = request.get("proposition_decomposition") or {}
    fallback_threshold = ""
    if isinstance(decomposition, Mapping):
        fallback_threshold = decomposition.get("decision_threshold", "") or ""

    decision_threshold = _string_or_empty(
        raw.get("decision_threshold", fallback_threshold),
        "criterion_analysis.decision_threshold",
    )

    necessary = _normalize_conditions(
        raw.get("necessary_conditions"),
        "criterion_analysis.necessary_conditions",
    )
    sufficient = _normalize_conditions(
        raw.get("sufficient_conditions"),
        "criterion_analysis.sufficient_conditions",
    )
    blockers = _normalize_conditions(
        raw.get("blocking_conditions"),
        "criterion_analysis.blocking_conditions",
    )

    downstream = _normalize_string_list(
        raw.get("downstream_criteria"),
        "criterion_analysis.downstream_criteria",
    )
    authority = _normalize_string_list(
        raw.get("authority_dependencies"),
        "criterion_analysis.authority_dependencies",
    )
    relevant = _normalize_string_list(
        raw.get("relevant_criteria"),
        "criterion_analysis.relevant_criteria",
    )
    excluded = _normalize_string_list(
        raw.get("excluded_criteria"),
        "criterion_analysis.excluded_criteria",
    )

    distinctions = raw.get("distinctions") or {}
    if not isinstance(distinctions, Mapping):
        raise LogicExecValidationError(
            "criterion_analysis.distinctions must be a mapping."
        )
    clean_distinctions: dict[str, str] = {}
    for key, value in distinctions.items():
        clean_distinctions[
            _nonempty_string(key, "criterion_analysis.distinctions key")
        ] = _nonempty_string(value, f"criterion_analysis.distinctions[{key!r}]")

    if not decision_threshold and relevant:
        decision_threshold = relevant[0]

    return {
        "decision_threshold": decision_threshold,
        "necessary_conditions": necessary,
        "sufficient_conditions": sufficient,
        "blocking_conditions": blockers,
        "downstream_criteria": downstream,
        "authority_dependencies": authority,
        "relevant_criteria": relevant,
        "excluded_criteria": excluded,
        "distinctions": clean_distinctions,
    }


def _derived_role(target: Any, polarity: Any) -> str | None:
    target_norm = _norm(target) if isinstance(target, str) else ""
    polarity_norm = _norm(polarity) if isinstance(polarity, str) else ""

    if target_norm in {"current", "current_action"}:
        if polarity_norm == "supports":
            return "SUPPORTS_CURRENT_ACTION"
        if polarity_norm == "blocks":
            return "BLOCKS_CURRENT_ACTION"
    if target_norm in {"downstream", "downstream_action"}:
        if polarity_norm == "supports":
            return "SUPPORTS_DOWNSTREAM_ACTION"
        if polarity_norm == "blocks":
            return "BLOCKS_DOWNSTREAM_ACTION"
    if target_norm in {"authority", "authority_constraint"}:
        return "AUTHORITY_CONSTRAINT"
    if target_norm in {"context", "context_only"}:
        return "CONTEXT_ONLY"
    if target_norm in {"irrelevant", "irrelevant_to_current"}:
        return "IRRELEVANT_TO_CURRENT_PROPOSITION"
    return None


def classify_evidence(items: Any) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(items, list):
        raise LogicExecValidationError("evidence must be a list.")

    out: list[dict[str, Any]] = []
    role_error = False

    for index, item in enumerate(items):
        field = f"evidence[{index}]"
        if not isinstance(item, Mapping):
            raise LogicExecValidationError(f"{field} must be a mapping.")

        identifier = item.get("evidence_id", item.get("source_id"))
        identifier = _nonempty_string(identifier, f"{field}.evidence_id")

        explicit = item.get("role")
        derived = _derived_role(item.get("target"), item.get("polarity"))

        if explicit is None:
            role = derived or "INSUFFICIENT_TO_CLASSIFY"
        else:
            if not isinstance(explicit, str):
                raise LogicExecValidationError(f"{field}.role must be a string.")
            role = explicit.strip().upper()
            if role not in EVIDENCE_ROLES:
                raise LogicExecValidationError(
                    f"{field}.role must be one of {sorted(EVIDENCE_ROLES)}."
                )
            if derived and role != derived:
                role_error = True

        out.append(
            {
                "evidence_id": identifier,
                "role": role,
            }
        )

    return out, role_error


def _condition_conflict(analysis: Mapping[str, Any]) -> bool:
    states_by_key: dict[str, set[str]] = defaultdict(set)
    for field in (
        "necessary_conditions",
        "sufficient_conditions",
        "blocking_conditions",
    ):
        for condition in analysis[field]:
            key = _norm(condition["id"] or condition["statement"])
            states_by_key[key].add(condition["state"])
    return any(
        "SATISFIED" in states and "NOT_SATISFIED" in states
        for states in states_by_key.values()
    )


def derive_expected_vote(analysis: Mapping[str, Any]) -> str:
    blockers = analysis["blocking_conditions"]
    necessary = analysis["necessary_conditions"]
    sufficient = analysis["sufficient_conditions"]

    if any(c["state"] == "SATISFIED" for c in blockers):
        return "NO"
    if any(c["state"] == "NOT_SATISFIED" for c in necessary):
        return "NO"
    if any(c["state"] == "SATISFIED" for c in sufficient):
        return "YES"
    if necessary:
        if all(c["state"] == "SATISFIED" for c in necessary):
            return "YES"
        if any(c["state"] == "UNKNOWN" for c in necessary):
            return "ABSTAIN"
    return "ABSTAIN"


def _phrase_present(text: str, phrase: str) -> bool:
    phrase_norm = _norm(phrase)
    if not phrase_norm:
        return False
    return phrase_norm in _norm(text)


def validate_exec_deliberation(request: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one LOGIC-EXEC-001 Executive deliberation request."""
    if not isinstance(request, Mapping):
        raise LogicExecValidationError("request must be a mapping.")

    if request.get("schema_version") != REQUEST_SCHEMA_VERSION:
        raise LogicExecValidationError(
            f"Unknown schema_version: {request.get('schema_version')!r}"
        )

    validation_id = _nonempty_string(request.get("validation_id"), "validation_id")
    matter_id = _nonempty_string(request.get("matter_id"), "matter_id")
    runtime_service = _nonempty_string(
        request.get("runtime_service"), "runtime_service"
    )
    proposition = _nonempty_string(request.get("proposition"), "proposition")
    proposed_choice = _nonempty_string(
        request.get("proposed_choice"), "proposed_choice"
    ).upper()
    if proposed_choice not in CHOICES:
        raise LogicExecValidationError(
            f"proposed_choice must be one of {sorted(CHOICES)}."
        )
    proposed_rationale = _string_or_empty(
        request.get("proposed_rationale", ""), "proposed_rationale"
    )
    authority_ceiling = _string_or_empty(
        request.get("authority_ceiling", ""), "authority_ceiling"
    )
    correlation_id = request.get("correlation_id")
    if correlation_id is not None:
        correlation_id = _nonempty_string(correlation_id, "correlation_id")

    normalized, scope_expansion = normalize_proposition(
        proposition,
        request.get("proposition_decomposition"),
    )
    analysis = derive_criterion_analysis(request)
    evidence_classification, evidence_role_error = classify_evidence(
        request.get("evidence", [])
    )

    current_threshold = _norm(analysis["decision_threshold"])
    downstream_norm = {_norm(x) for x in analysis["downstream_criteria"]}
    excluded_norm = {_norm(x) for x in analysis["excluded_criteria"]}
    relevant_norm = {_norm(x) for x in analysis["relevant_criteria"]}

    threshold_conflict = bool(
        current_threshold
        and (current_threshold in downstream_norm or current_threshold in excluded_norm)
    )

    criterion_substitution = threshold_conflict

    expected_vote = derive_expected_vote(analysis)

    rationale_downstream = any(
        _phrase_present(proposed_rationale, criterion)
        for criterion in analysis["downstream_criteria"] + analysis["excluded_criteria"]
    )
    if proposed_choice != expected_vote and rationale_downstream:
        criterion_substitution = True

    overlap = relevant_norm & excluded_norm
    distinction_keys = {_norm(k) for k in analysis["distinctions"]}
    relevant_excluded_conflict = any(key not in distinction_keys for key in overlap)

    contradiction = _condition_conflict(analysis) or relevant_excluded_conflict

    necessary_states = [c["state"] for c in analysis["necessary_conditions"]]
    sufficient_states = [c["state"] for c in analysis["sufficient_conditions"]]
    necessary_sufficient_error = False
    if proposed_choice == "YES" and "NOT_SATISFIED" in necessary_states:
        necessary_sufficient_error = True
    if (
        proposed_choice == "NO"
        and necessary_states
        and all(state == "SATISFIED" for state in necessary_states)
        and "NOT_SATISFIED" in sufficient_states
        and not any(c["state"] == "SATISFIED" for c in analysis["blocking_conditions"])
    ):
        necessary_sufficient_error = True

    supplied_ids = {item["evidence_id"] for item in evidence_classification}
    rationale_ids = request.get("rationale_evidence_ids", [])
    if not isinstance(rationale_ids, list):
        raise LogicExecValidationError("rationale_evidence_ids must be a list.")
    rationale_ids_clean = [
        _nonempty_string(item, f"rationale_evidence_ids[{i}]")
        for i, item in enumerate(rationale_ids)
    ]
    unsupported_inference = any(
        evidence_id not in supplied_ids for evidence_id in rationale_ids_clean
    )

    role_by_id = {
        item["evidence_id"]: item["role"] for item in evidence_classification
    }
    decisively_ineligible_roles = {
        "CONTEXT_ONLY",
        "IRRELEVANT_TO_CURRENT_PROPOSITION",
        "SUPPORTS_DOWNSTREAM_ACTION",
        "BLOCKS_DOWNSTREAM_ACTION",
        "AUTHORITY_CONSTRAINT",
        "INSUFFICIENT_TO_CLASSIFY",
    }
    if any(
        role_by_id.get(evidence_id) in decisively_ineligible_roles
        for evidence_id in rationale_ids_clean
    ) and proposed_choice != expected_vote:
        evidence_role_error = True

    vote_consistency = (
        "CONSISTENT" if proposed_choice == expected_vote else "INCONSISTENT"
    )
    if (
        vote_consistency == "INCONSISTENT"
        and not criterion_substitution
        and not necessary_sufficient_error
        and not contradiction
        and not evidence_role_error
    ):
        unsupported_inference = True

    findings = {
        "criterion_substitution": criterion_substitution,
        "threshold_conflict": threshold_conflict,
        "scope_expansion": scope_expansion,
        "relevant_excluded_conflict": relevant_excluded_conflict,
        "unsupported_inference": unsupported_inference,
        "necessary_sufficient_error": necessary_sufficient_error,
        "contradiction": contradiction,
        "evidence_role_error": evidence_role_error,
    }

    critical_failure = any(findings.values()) or vote_consistency == "INCONSISTENT"
    criterion_information_present = bool(
        analysis["decision_threshold"]
        and (
            analysis["necessary_conditions"]
            or analysis["sufficient_conditions"]
            or analysis["blocking_conditions"]
        )
    )

    if critical_failure:
        status = "FAIL"
    elif not criterion_information_present:
        status = "INDETERMINATE"
    elif any(
        item["role"] == "INSUFFICIENT_TO_CLASSIFY"
        for item in evidence_classification
    ):
        status = "PASS_WITH_FINDINGS"
    else:
        status = "PASS"

    if status == "PASS":
        explanation = (
            f"Reasoning structure is internally consistent; proposed vote "
            f"{proposed_choice} matches the current-action criterion."
        )
    elif status == "PASS_WITH_FINDINGS":
        explanation = (
            "Reasoning structure is consistent, but one or more evidence items "
            "could not be deterministically classified."
        )
    elif status == "INDETERMINATE":
        explanation = (
            "The request does not contain enough structured current-criterion "
            "information to determine vote consistency."
        )
    else:
        active = [name for name, value in findings.items() if value]
        if vote_consistency == "INCONSISTENT":
            active.append("vote_inconsistent")
        explanation = "Logical inconsistency detected: " + ", ".join(active) + "."

    return {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "validation_id": validation_id,
        "matter_id": matter_id,
        "correlation_id": correlation_id,
        "runtime_service": runtime_service,
        "status": status,
        "normalized_proposition": normalized,
        "criterion_analysis": analysis,
        "evidence_classification": evidence_classification,
        "logic_findings": findings,
        "expected_vote": expected_vote,
        "proposed_vote": proposed_choice,
        "vote_consistency": vote_consistency,
        "explanation": explanation,
        "authority_ceiling": authority_ceiling,
        "institutional_decision": False,
        "authority_expansion": False,
    }
