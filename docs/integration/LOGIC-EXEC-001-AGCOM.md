# LOGIC-EXEC-001 AGCOM Integration Specification

**Status:** IMPLEMENTED SPECIFICATION / TRANSPORT ADMISSION NOT CLAIMED

AGCOM carries validation packets and returns Logic Lab results. It does not modify reasoning or convert findings into commands.

## Message flow

1. Executive/Runtime creates a request conforming to `schemas/logic_validation_request.schema.json`.
2. AGCOM assigns/preserves `correlation_id` and transports the packet to Logic Lab.
3. Logic Lab calls `validate_exec_deliberation`.
4. AGCOM transports the unchanged response to Runtime Lab / the Executive.
5. Runtime records the Logic result beside the final Executive deliberation.

Required lineage fields, where supplied: `validation_id`, `matter_id`, `correlation_id`, `runtime_service`.

## Fail-closed integration rule

A Logic response with `status=FAIL` means the deliberation is rejected for logical inconsistency. It does **not** mean Logic Lab changed the vote.

`INDETERMINATE` means the structured packet was insufficient for a consistency decision and must not be converted to PASS by transport.

## Authority

AGCOM transport has no command authority. No external communications, credentials, persistent runtime expansion, or production admission are created by this specification.

## Initial integration

The first live integration target is AIR_001 only. A live run requires the actual AIR_001 proposed deliberation and Runtime-owned qualification context. Those artifacts are not fabricated by Logic Lab.
