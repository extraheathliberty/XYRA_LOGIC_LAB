from __future__ import annotations

from collections.abc import Mapping
from typing import Any

LEARN_REQUEST_SCHEMA_VERSION = "LOGIC-LEARN-001/request/v1"
LEARN_RESPONSE_SCHEMA_VERSION = "LOGIC-LEARN-001/response/v1"

TERMINAL_STATES = {
    "NO SUFFICIENT EVIDENCE OF DECEPTION",
    "UNKNOWN / ACCESS CONSTRAINED",
}


class LogicLearnValidationError(ValueError):
    """Fail-closed error for malformed LOGIC-LEARN-001 packets."""


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


def validate_learning_packet(request: Mapping[str, Any]) -> dict[str, Any]:
    """
    Validate the structure of one governed learning-evaluation packet.

    This validator checks reasoning discipline and representation quality.
    It does not determine whether source propositions are factually true and
    does not rewrite the learner answer.
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

    findings = {
        "insufficient_hypothesis_set": len(hypotheses) < 2,
        "missing_source_dependency_analysis": not source_dependencies,
        "missing_information_gaps": not information_gaps,
        "missing_next_collection": not next_collection,
        "missing_explicit_premises": not premises,
        "missing_disconfirming_evidence": not disconfirming,
        "unsupported_terminal_state": terminal_state not in TERMINAL_STATES,
        "fact_inference_contradiction": contradiction,
        "empty_claimed_conclusion": not bool(claimed_conclusion),
    }

    critical = (
        findings["insufficient_hypothesis_set"]
        or findings["missing_source_dependency_analysis"]
        or findings["missing_information_gaps"]
        or findings["missing_next_collection"]
        or findings["unsupported_terminal_state"]
        or findings["fact_inference_contradiction"]
        or findings["empty_claimed_conclusion"]
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
