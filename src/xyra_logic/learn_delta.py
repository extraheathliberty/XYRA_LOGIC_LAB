from __future__ import annotations

from collections.abc import Sequence


def assess_learning_delta_evidence(
    *,
    baseline_frozen_before_exposure: bool,
    baseline_executed_before_exposure: bool,
    learning_exposure_occurred: bool,
    post_learning_blind_executed: bool,
    scoring_dimensions_comparable: bool,
    hard_failures: Sequence[str] = (),
) -> dict[str, object]:
    """
    Distinguish present capability evidence from causal learning-delta evidence.

    A frozen-but-unexecuted baseline cannot be reconstructed after learning
    exposure and therefore cannot support a causal pre/post delta claim.
    """
    failures = [str(x) for x in hard_failures if str(x).strip()]

    if (
        baseline_frozen_before_exposure
        and not baseline_executed_before_exposure
        and learning_exposure_occurred
    ):
        delta_status = "NOT_ESTABLISHABLE_RETROACTIVELY"
        delta_blockers = ["pre_learning_baseline_not_executed"]
    elif not baseline_executed_before_exposure:
        delta_status = "PENDING_BASELINE"
        delta_blockers = ["pre_learning_baseline_not_executed"]
    elif not post_learning_blind_executed:
        delta_status = "PENDING_POST_LEARNING_BLIND"
        delta_blockers = ["post_learning_blind_not_executed"]
    elif not scoring_dimensions_comparable:
        delta_status = "NOT_COMPARABLE"
        delta_blockers = ["scoring_dimensions_not_comparable"]
    elif failures:
        delta_status = "FAIL"
        delta_blockers = failures
    else:
        delta_status = "ELIGIBLE_FOR_DELTA_SCORING"
        delta_blockers = []

    capability_status = (
        "PENDING_BLIND_CAPABILITY_TEST"
        if not post_learning_blind_executed
        else "BLIND_CAPABILITY_EVIDENCE_AVAILABLE"
    )

    return {
        "learning_delta_status": delta_status,
        "learning_delta_blockers": delta_blockers,
        "current_capability_status": capability_status,
        "baseline_frozen_before_exposure": baseline_frozen_before_exposure,
        "baseline_executed_before_exposure": baseline_executed_before_exposure,
        "post_learning_blind_executed": post_learning_blind_executed,
        "formal_qualification_granted": False,
        "institutional_decision": False,
        "authority_expansion": False,
    }
