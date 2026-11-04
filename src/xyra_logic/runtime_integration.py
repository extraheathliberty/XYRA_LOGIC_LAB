from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .exec_validation import (
    LogicExecValidationError,
    REQUEST_SCHEMA_VERSION,
    validate_exec_deliberation,
)


def _required_string(mapping: Mapping[str, Any], key: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LogicExecValidationError(f"runtime_artifact.{key} must be a non-empty string.")
    return value.strip()


def build_runtime_validation_request(
    *,
    runtime_artifact: Mapping[str, Any],
    proposition: str,
    evidence: list[Mapping[str, Any]],
    validation_id: str,
    authority_ceiling: str,
    correlation_id: str | None = None,
    criterion_analysis: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convert a preserved Executive runtime deliberation into LOGIC-EXEC-001/v1.

    This adapter is deliberately provenance-preserving. It does not infer
    necessary/sufficient condition states from prose. If Runtime does not
    provide a governed criterion_analysis packet, only the decomposition's
    threshold/relevant/excluded fields are carried forward and the Logic
    validator may return INDETERMINATE or FAIL rather than inventing semantics.
    """
    if not isinstance(runtime_artifact, Mapping):
        raise LogicExecValidationError("runtime_artifact must be a mapping.")
    if not isinstance(evidence, list):
        raise LogicExecValidationError("evidence must be a list.")

    matter_id = _required_string(runtime_artifact, "matter_id")
    runtime_service = _required_string(runtime_artifact, "runtime_service")
    choice = _required_string(runtime_artifact, "choice").upper()
    rationale = _required_string(runtime_artifact, "rationale")

    refs = runtime_artifact.get("evidence_refs", [])
    if not isinstance(refs, list) or any(not isinstance(x, str) or not x.strip() for x in refs):
        raise LogicExecValidationError("runtime_artifact.evidence_refs must be a list of strings.")
    refs = [x.strip() for x in refs]

    available_ids: set[str] = set()
    for index, item in enumerate(evidence):
        if not isinstance(item, Mapping):
            raise LogicExecValidationError(f"evidence[{index}] must be a mapping.")
        identifier = item.get("evidence_id", item.get("source_id"))
        if not isinstance(identifier, str) or not identifier.strip():
            raise LogicExecValidationError(
                f"evidence[{index}] requires evidence_id or source_id."
            )
        available_ids.add(identifier.strip())

    missing = [ref for ref in refs if ref not in available_ids]
    if missing:
        raise LogicExecValidationError(
            "runtime artifact cites evidence absent from supplied context: "
            + ", ".join(missing)
        )

    decomposition = runtime_artifact.get("proposition_decomposition") or {}
    if not isinstance(decomposition, Mapping):
        raise LogicExecValidationError(
            "runtime_artifact.proposition_decomposition must be a mapping."
        )

    if criterion_analysis is None:
        relevant = decomposition.get("relevant_criteria", [])
        excluded = decomposition.get("excluded_stricter_criteria", [])
        if not isinstance(relevant, list) or not isinstance(excluded, list):
            raise LogicExecValidationError(
                "runtime proposition decomposition criteria must be lists."
            )
        criterion_analysis = {
            "decision_threshold": decomposition.get("decision_threshold", ""),
            "necessary_conditions": [],
            "sufficient_conditions": [],
            "blocking_conditions": [],
            "downstream_criteria": list(excluded),
            "authority_dependencies": [],
            "relevant_criteria": list(relevant),
            "excluded_criteria": list(excluded),
            "distinctions": {},
        }
    elif not isinstance(criterion_analysis, Mapping):
        raise LogicExecValidationError("criterion_analysis must be a mapping.")

    request: dict[str, Any] = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "validation_id": validation_id,
        "matter_id": matter_id,
        "runtime_service": runtime_service,
        "proposition": proposition,
        "proposition_decomposition": dict(decomposition),
        "criterion_analysis": dict(criterion_analysis),
        "evidence": [dict(item) for item in evidence],
        "rationale_evidence_ids": refs,
        "proposed_choice": choice,
        "proposed_rationale": rationale,
        "authority_ceiling": authority_ceiling,
    }
    if correlation_id:
        request["correlation_id"] = correlation_id
    return request


def validate_runtime_deliberation(**kwargs: Any) -> dict[str, Any]:
    """Build and validate one preserved Runtime deliberation."""
    return validate_exec_deliberation(build_runtime_validation_request(**kwargs))
