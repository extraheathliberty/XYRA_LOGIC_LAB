from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class LogicLearnGroundingError(ValueError):
    """Raised when a learning-grounding packet is malformed."""


def verify_source_grounding(
    *,
    source_refs: Sequence[str],
    authorized_sources: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Verify that learner-cited source identifiers resolve to authorized sources.

    This checks identity/admission lineage only. It does not assert that a
    learner's prose accurately paraphrases the underlying source text.
    """
    if not isinstance(source_refs, Sequence) or isinstance(source_refs, (str, bytes)):
        raise LogicLearnGroundingError("source_refs must be a sequence of identifiers.")
    if not isinstance(authorized_sources, Mapping):
        raise LogicLearnGroundingError("authorized_sources must be a mapping.")

    normalized_refs: list[str] = []
    for i, ref in enumerate(source_refs):
        if not isinstance(ref, str) or not ref.strip():
            raise LogicLearnGroundingError(f"source_refs[{i}] must be a non-empty string.")
        normalized_refs.append(ref.strip())

    duplicate_refs = sorted({r for r in normalized_refs if normalized_refs.count(r) > 1})
    unknown_refs = sorted({r for r in normalized_refs if r not in authorized_sources})

    unauthorized_refs: list[str] = []
    resolved: list[dict[str, Any]] = []
    for ref in normalized_refs:
        record = authorized_sources.get(ref)
        if record is None:
            continue
        authorized = bool(record.get("authorized", False))
        if not authorized:
            unauthorized_refs.append(ref)
        resolved.append(
            {
                "source_ref": ref,
                "authorized": authorized,
                "title": record.get("title"),
                "authority_ref": record.get("authority_ref"),
                "artifact_hash": record.get("artifact_hash"),
            }
        )

    grounded = not unknown_refs and not unauthorized_refs and bool(normalized_refs)

    return {
        "grounded": grounded,
        "source_count": len(normalized_refs),
        "resolved_count": len(resolved),
        "unknown_refs": unknown_refs,
        "unauthorized_refs": sorted(set(unauthorized_refs)),
        "duplicate_refs": duplicate_refs,
        "resolved_sources": resolved,
        "content_accuracy_assessed": False,
        "institutional_decision": False,
        "authority_expansion": False,
    }
