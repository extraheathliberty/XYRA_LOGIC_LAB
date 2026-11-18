"""Experimental BUSINESS_CLASSIFICATION profile, no production admission.
Pure deterministic validation of a supplied classification argument.
"""
from collections.abc import Mapping

SCHEMA = "LOGIC-BUSINESS-CLASSIFICATION-001/v1"
LEVELS = ("sector", "industry_group", "industry", "sub_industry", "code")

def validate_business_classification(packet: Mapping) -> dict:
    if not isinstance(packet, Mapping):
        raise ValueError("packet must be mapping")
    findings = []
    for key in ("record_id", "business_name", "entity_scope", "activity"):
        if not isinstance(packet.get(key), str) or not packet[key].strip():
            findings.append(f"missing_{key}")
    evidence = packet.get("evidence")
    supported = isinstance(evidence, list) and any(
        isinstance(e, Mapping) and isinstance(e.get("url"), str)
        and e["url"].startswith(("https://", "http://"))
        and e.get("supports_activity") is True for e in evidence
    )
    if not supported:
        findings.append("missing_activity_evidence")
    gics = packet.get("gics")
    complete = isinstance(gics, Mapping) and all(
        isinstance(gics.get(k), str) and gics[k].strip() for k in LEVELS
    )
    if not complete:
        findings.append("incomplete_gics_hierarchy")
    taxonomy = packet.get("taxonomy")
    if not isinstance(taxonomy, list) or not taxonomy:
        findings.append("missing_taxonomy")
    elif complete and not any(
        isinstance(row, Mapping) and all(row.get(k) == gics.get(k) for k in LEVELS)
        for row in taxonomy
    ):
        findings.append("invalid_gics_hierarchy")
    if not packet.get("taxonomy_version"):
        findings.append("missing_taxonomy_version")
    if packet.get("contradictory_evidence"):
        findings.append("unresolved_contradiction")
    # A structurally consistent packet is not proof that the source is true
    # or that the company's principal activity belongs to this sub-industry.
    return {
        "schema_version": SCHEMA,
        "profile": "BUSINESS_CLASSIFICATION",
        "record_id": packet.get("record_id"),
        "status": "REVIEW" if not findings else "FAIL",
        "structural_validity": "PASS" if not findings else "FAIL",
        "findings": findings,
        "semantic_classification_verified": False,
        "institutional_decision": False,
        "authority_expansion": False,
        "production_admission": False,
    }
