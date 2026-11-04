from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class LogicLearnContentError(ValueError):
    """Fail-closed error for malformed source-proposition packets."""


_MODALITY_RANK = {
    "tentative": 1,
    "conditional": 2,
    "assertive": 3,
}


def verify_source_propositions(
    *,
    claims: Sequence[Mapping[str, Any]],
    proposition_registry: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(claims, Sequence) or isinstance(claims, (str, bytes)):
        raise LogicLearnContentError("claims must be a sequence")
    if not isinstance(proposition_registry, Mapping):
        raise LogicLearnContentError("proposition_registry must be a mapping")

    unknown_ids: list[str] = []
    unauthorized_ids: list[str] = []
    modality_inflation: list[str] = []
    resolved: list[dict[str, Any]] = []

    for i, claim in enumerate(claims):
        if not isinstance(claim, Mapping):
            raise LogicLearnContentError(f"claims[{i}] must be a mapping")
        prop_id = claim.get("proposition_id")
        modality = claim.get("modality")
        if not isinstance(prop_id, str) or not prop_id.strip():
            raise LogicLearnContentError(f"claims[{i}].proposition_id invalid")
        if modality not in _MODALITY_RANK:
            raise LogicLearnContentError(f"claims[{i}].modality invalid")

        prop_id = prop_id.strip()
        source = proposition_registry.get(prop_id)
        if source is None:
            unknown_ids.append(prop_id)
            continue

        authorized = bool(source.get("authorized", False))
        if not authorized:
            unauthorized_ids.append(prop_id)

        source_modality = source.get("modality", "assertive")
        if source_modality not in _MODALITY_RANK:
            raise LogicLearnContentError(
                f"registry modality invalid for {prop_id}"
            )
        if _MODALITY_RANK[modality] > _MODALITY_RANK[source_modality]:
            modality_inflation.append(prop_id)

        resolved.append(
            {
                "proposition_id": prop_id,
                "source_ref": source.get("source_ref"),
                "authorized": authorized,
                "source_modality": source_modality,
                "claim_modality": modality,
                "statement": source.get("statement"),
            }
        )

    passed = bool(claims) and not unknown_ids and not unauthorized_ids and not modality_inflation

    return {
        "passed": passed,
        "claim_count": len(claims),
        "resolved_count": len(resolved),
        "unknown_proposition_ids": sorted(set(unknown_ids)),
        "unauthorized_proposition_ids": sorted(set(unauthorized_ids)),
        "source_modality_inflation": sorted(set(modality_inflation)),
        "resolved_claims": resolved,
        "semantic_equivalence_assessed": False,
        "institutional_decision": False,
        "authority_expansion": False,
    }


def assess_learning_qualification_readiness(
    *,
    source_grounding_pass: bool,
    content_fidelity_pass: bool,
    validator_blind_benchmark_pass: bool,
    learner_blind_delta_pass: bool,
    positive_benchmark_pass: bool,
    negative_benchmark_rejected: bool,
    covered_learning_cases: int,
    minimum_learning_cases: int = 4,
    critical_findings: Sequence[str] = (),
) -> dict[str, Any]:
    blockers: list[str] = []
    if not source_grounding_pass:
        blockers.append("source_grounding")
    if not content_fidelity_pass:
        blockers.append("content_fidelity")
    if not blind_case_pass:
        blockers.append("blind_case")
    if not positive_benchmark_pass:
        blockers.append("positive_benchmark")
    if not negative_benchmark_rejected:
        blockers.append("negative_benchmark")
    if covered_learning_cases < minimum_learning_cases:
        blockers.append("multi_case_coverage")
    blockers.extend(str(x) for x in critical_findings if str(x).strip())

    return {
        "status": (
            "READY_FOR_FORMAL_QUALIFICATION_REVIEW"
            if not blockers
            else "NOT_READY"
        ),
        "covered_learning_cases": covered_learning_cases,
        "minimum_learning_cases": minimum_learning_cases,
        "blockers": sorted(set(blockers)),
        "formal_qualification_granted": False,
        "sulm_appointment_granted": False,
        "institutional_decision": False,
        "authority_expansion": False,
    }
