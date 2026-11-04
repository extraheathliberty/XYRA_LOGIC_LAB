from __future__ import annotations

from collections.abc import Mapping
from typing import Any

STANDARD_VERSION = "XYRA_LOGIC_STANDARD-001/v1"
PROFILES = {"EXECUTIVE_DECISION", "LEARNING_EVALUATION"}
DOMAIN_STATUSES = {"PASS", "PASS_WITH_FINDINGS", "FAIL", "INDETERMINATE"}


class LogicStandardValidationError(ValueError):
    """Fail-closed error for malformed standard-conformance records."""


def assess_standard_conformance(
    *,
    profile: str,
    domain_result: Mapping[str, Any],
) -> dict[str, Any]:
    if profile not in PROFILES:
        raise LogicStandardValidationError(f"unknown profile: {profile}")
    if not isinstance(domain_result, Mapping):
        raise LogicStandardValidationError("domain_result must be a mapping")

    domain_status = domain_result.get("status")
    if domain_status not in DOMAIN_STATUSES:
        raise LogicStandardValidationError("invalid domain status")

    findings: list[str] = []

    if domain_result.get("institutional_decision") is not False:
        findings.append("institutional_decision_not_false")
    if domain_result.get("authority_expansion") is not False:
        findings.append("authority_expansion_not_false")

    if profile == "EXECUTIVE_DECISION":
        for key in (
            "normalized_proposition",
            "criterion_analysis",
            "evidence_classification",
            "expected_vote",
            "proposed_vote",
            "vote_consistency",
            "authority_ceiling",
        ):
            if key not in domain_result:
                findings.append(f"missing_{key}")
        if domain_result.get("vote_consistency") not in {
            "CONSISTENT",
            "INCONSISTENT",
        }:
            findings.append("invalid_vote_consistency")

    if profile == "LEARNING_EVALUATION":
        for key in (
            "learner_id",
            "source_work_id",
            "source_authority_ref",
            "task",
            "claimed_conclusion",
            "terminal_state",
            "reasoning_integrity_assessed",
            "application_performance_assessed",
            "formal_qualification",
        ):
            if key not in domain_result:
                findings.append(f"missing_{key}")
        if domain_result.get("formal_qualification") is not False:
            findings.append("formal_qualification_not_false")

    if findings:
        standard_status = "FAIL"
    else:
        standard_status = domain_status

    return {
        "logic_standard_version": STANDARD_VERSION,
        "logic_profile": profile,
        "domain_status": domain_status,
        "standard_status": standard_status,
        "findings": findings,
        "institutional_decision": False,
        "authority_expansion": False,
        "production_admission": False,
    }
