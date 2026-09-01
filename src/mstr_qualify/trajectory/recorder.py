"""A018: deterministic trajectory recording, replay, and storage boundaries."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast

from mstr_qualify.harness.event_log import EventLogError, replay
from mstr_qualify.schemas import validate_instance
from mstr_qualify.trajectory.admission import (
    ContaminationStatus,
    RequestedLane,
    TerminalClass,
    TrajectoryAdmissionError,
    bind_verifier_health,
    decide_training_admission,
)

_PRIVATE_SOURCES = frozenset({"PRIVATE_USER_REPOSITORY", "PRODUCTION_TRACE"})
_SUCCESS_TERMINALS = frozenset({"VERIFIED_SUCCESS", "RECOVERED_SUCCESS"})


class TrajectoryReplayError(ValueError):
    """Fail-closed trajectory replay/recording error with a stable machine code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


def _canonical_event_log_bytes(events: Sequence[Mapping[str, Any]]) -> bytes:
    return json.dumps(
        list(events),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def event_log_sha256(events: Sequence[Mapping[str, Any]]) -> str:
    """Digest the complete integrity-checked event sequence deterministically."""

    return hashlib.sha256(_canonical_event_log_bytes(events)).hexdigest()


def _replayed_raw(events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not events:
        raise TrajectoryReplayError(
            "trajectory requires at least one event",
            code="trajectory.events_empty",
        )
    copied = [dict(event) for event in events]
    try:
        entries = replay(copied)
    except (EventLogError, ValueError) as exc:
        raise TrajectoryReplayError(
            "trajectory event log failed deterministic replay",
            code="trajectory.event_log_invalid",
        ) from exc
    return [entry.raw for entry in entries]


def _recovery_count(events: Sequence[Mapping[str, Any]]) -> int:
    explicit = sum(event.get("event_type") == "recovery.started" for event in events)

    verifier_history: dict[str, list[str]] = {}
    for event in events:
        if event.get("event_type") != "verifier.result":
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        verifier_id = payload.get("verifier_id")
        status = payload.get("status")
        if isinstance(verifier_id, str) and isinstance(status, str):
            verifier_history.setdefault(verifier_id, []).append(status)

    recovered_verifiers = sum(
        any(status != "PASS" for status in statuses[:-1]) and statuses[-1] == "PASS"
        for statuses in verifier_history.values()
        if statuses
    )
    return max(explicit, recovered_verifiers)


def _terminal_from_events(
    events: Sequence[Mapping[str, Any]],
    *,
    failure_terminal_class: TerminalClass | None,
) -> tuple[TerminalClass, str | None, bool]:
    terminal = events[-1]
    event_type = terminal.get("event_type")

    if event_type == "run.completed":
        if failure_terminal_class is not None:
            raise TrajectoryReplayError(
                "caller cannot override a protected successful terminal event",
                code="trajectory.success_terminal_override",
            )
        if terminal.get("source") != "verifier":
            raise TrajectoryReplayError(
                "successful trajectory requires verifier-authored completion",
                code="trajectory.success_source_untrusted",
            )
        payload = terminal.get("payload")
        if not isinstance(payload, dict):
            raise TrajectoryReplayError(
                "successful terminal payload is missing",
                code="trajectory.success_payload_missing",
            )
        raw_class = payload.get("terminal_class")
        raw_identity = payload.get("verifier_result_identity")
        if raw_class not in _SUCCESS_TERMINALS:
            raise TrajectoryReplayError(
                "successful terminal class is invalid",
                code="trajectory.success_class_invalid",
            )
        if not isinstance(raw_identity, str) or not raw_identity.strip():
            raise TrajectoryReplayError(
                "successful trajectory requires verifier result identity",
                code="trajectory.verifier_proof_missing",
            )
        return cast(TerminalClass, raw_class), raw_identity, True

    if event_type not in {"run.failed", "run.escalated"}:
        raise TrajectoryReplayError(
            "trajectory must end in run.completed, run.failed, or run.escalated",
            code="trajectory.terminal_event_missing",
        )
    if failure_terminal_class is None or failure_terminal_class in _SUCCESS_TERMINALS:
        raise TrajectoryReplayError(
            "failed/escalated trajectory requires an explicit non-success terminal class",
            code="trajectory.failure_class_missing",
        )
    return failure_terminal_class, None, False


def _assert_run_identity(
    events: Sequence[Mapping[str, Any]],
    run_identity: Mapping[str, Any],
) -> None:
    run_id = run_identity.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise TrajectoryReplayError(
            "run identity requires a non-empty run_id",
            code="trajectory.run_id_missing",
        )
    event_run_ids = {event.get("run_id") for event in events}
    if event_run_ids != {run_id}:
        raise TrajectoryReplayError(
            "event log run identity does not match the trajectory run identity",
            code="trajectory.run_id_mismatch",
        )


def build_trajectory_manifest(
    *,
    trajectory_id: str,
    events: Sequence[Mapping[str, Any]],
    run_identity: Mapping[str, Any],
    provenance: Mapping[str, Any],
    requested_lane: RequestedLane = "EVAL_ONLY",
    failure_terminal_class: TerminalClass | None = None,
    failure_classes: Sequence[str] = (),
    authority_violations: Sequence[str] = (),
    contamination_status: ContaminationStatus = "CLEAR",
    verifier_health_record: Mapping[str, Any] | None = None,
    verifier_health_stage_id: str | None = None,
) -> dict[str, Any]:
    """Build one validated trajectory manifest from exact replayable evidence."""

    if not trajectory_id.strip():
        raise TrajectoryReplayError(
            "trajectory_id must be non-empty",
            code="trajectory.id_missing",
        )

    raw_events = _replayed_raw(events)
    _assert_run_identity(raw_events, run_identity)
    terminal_class, verifier_result_identity, verifier_proof_present = _terminal_from_events(
        raw_events,
        failure_terminal_class=failure_terminal_class,
    )
    recovery_count = _recovery_count(raw_events)

    health_binding = None
    if (verifier_health_record is None) != (verifier_health_stage_id is None):
        raise TrajectoryAdmissionError(
            "verifier health record and stage id must be provided together",
            code="trajectory.health_binding_incomplete",
        )
    if verifier_health_record is not None and verifier_health_stage_id is not None:
        task_manifest_id = run_identity.get("task_manifest_id")
        verifier_manifest_id = run_identity.get("verifier_manifest_id")
        if not isinstance(task_manifest_id, str) or not isinstance(verifier_manifest_id, str):
            raise TrajectoryAdmissionError(
                "run identity requires task/verifier manifest ids before health binding",
                code="trajectory.run_health_identity_missing",
            )
        health_binding = bind_verifier_health(
            verifier_health_record,
            task_manifest_id=task_manifest_id,
            verifier_manifest_id=verifier_manifest_id,
            stage_id=verifier_health_stage_id,
        )

    authority_tuple = tuple(authority_violations)
    decision = decide_training_admission(
        terminal_class=terminal_class,
        requested_lane=requested_lane,
        provenance=provenance,
        contamination_status=contamination_status,
        authority_violations=authority_tuple,
        verifier_health_binding=health_binding,
        verifier_proof_present=verifier_proof_present,
    )

    manifest: dict[str, Any] = {
        "schema_version": "mstr.trajectory-manifest.v0",
        "trajectory_id": trajectory_id,
        "run_identity": dict(run_identity),
        "event_log_schema_version": "mstr.run-event.v0",
        "event_log_sha256": event_log_sha256(raw_events),
        "event_count": len(raw_events),
        "failure_taxonomy_version": "mstr.failure-taxonomy.v0",
        "terminal_class": terminal_class,
        "verifier_result_identity": verifier_result_identity,
        "verifier_health_binding": (
            health_binding.as_mapping() if health_binding is not None else None
        ),
        "failure_classes": list(failure_classes),
        "recovery_count": recovery_count,
        "authority_violations": list(authority_tuple),
        "contamination_status": contamination_status,
        "training_admission": decision.training_admission,
        "admission_policy_version": "mstr.trajectory-admission.v0",
        "admission_reasons": list(decision.admission_reasons),
        "provenance": dict(provenance),
    }
    if decision.training_labels:
        manifest["training_labels"] = dict(decision.training_labels)

    try:
        validate_instance("mstr-trajectory-manifest-v0", manifest)
    except ValueError as exc:
        raise TrajectoryReplayError(
            "constructed trajectory manifest violates the canonical A017 contract",
            code="trajectory.manifest_invalid",
        ) from exc

    replay_trajectory(manifest, raw_events)
    return manifest


def replay_trajectory(
    manifest: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Replay exact events and verify every trajectory-manifest binding."""

    candidate = dict(manifest)
    try:
        validate_instance("mstr-trajectory-manifest-v0", candidate)
    except ValueError as exc:
        raise TrajectoryReplayError(
            "trajectory manifest failed canonical validation",
            code="trajectory.manifest_invalid",
        ) from exc

    raw_events = _replayed_raw(events)
    run_identity = candidate.get("run_identity")
    if not isinstance(run_identity, dict):
        raise TrajectoryReplayError(
            "trajectory run identity is missing",
            code="trajectory.run_identity_missing",
        )
    _assert_run_identity(raw_events, run_identity)

    if candidate.get("event_count") != len(raw_events):
        raise TrajectoryReplayError(
            "trajectory event count does not match replayed events",
            code="trajectory.event_count_mismatch",
        )
    if candidate.get("event_log_sha256") != event_log_sha256(raw_events):
        raise TrajectoryReplayError(
            "trajectory event-log digest does not match replayed events",
            code="trajectory.event_digest_mismatch",
        )

    failure_terminal = candidate.get("terminal_class")
    inferred_failure = (
        cast(TerminalClass, failure_terminal)
        if failure_terminal not in _SUCCESS_TERMINALS
        else None
    )
    terminal_class, verifier_identity, _ = _terminal_from_events(
        raw_events,
        failure_terminal_class=inferred_failure,
    )
    if candidate.get("terminal_class") != terminal_class:
        raise TrajectoryReplayError(
            "trajectory terminal class does not match terminal event",
            code="trajectory.terminal_class_mismatch",
        )
    if candidate.get("verifier_result_identity") != verifier_identity:
        raise TrajectoryReplayError(
            "trajectory verifier result identity does not match terminal event",
            code="trajectory.verifier_identity_mismatch",
        )
    if candidate.get("recovery_count") != _recovery_count(raw_events):
        raise TrajectoryReplayError(
            "trajectory recovery count does not match replay evidence",
            code="trajectory.recovery_count_mismatch",
        )
    return raw_events


def record_trajectory_bundle(
    path: Path,
    *,
    manifest: Mapping[str, Any],
    events: Sequence[Mapping[str, Any]],
) -> None:
    """Persist a deterministic bundle only when the source is ingestible in v0."""

    replayed = replay_trajectory(manifest, events)
    provenance = manifest.get("provenance")
    source_class = provenance.get("source_class") if isinstance(provenance, dict) else None
    if source_class in _PRIVATE_SOURCES:
        raise TrajectoryReplayError(
            "private user and production traces are not ingested by trajectory v0",
            code="trajectory.private_source_not_ingested",
        )

    payload = {
        "events": replayed,
        "manifest": dict(manifest),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def load_trajectory_bundle(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load a stored bundle and re-run canonical replay/binding validation."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TrajectoryReplayError(
            "trajectory bundle cannot be decoded",
            code="trajectory.bundle_decode",
        ) from exc
    if not isinstance(payload, dict):
        raise TrajectoryReplayError(
            "trajectory bundle must be an object",
            code="trajectory.bundle_root",
        )
    manifest = payload.get("manifest")
    events = payload.get("events")
    if not isinstance(manifest, dict) or not isinstance(events, list):
        raise TrajectoryReplayError(
            "trajectory bundle requires manifest and event-list fields",
            code="trajectory.bundle_shape",
        )
    raw_events = [dict(event) for event in events if isinstance(event, dict)]
    if len(raw_events) != len(events):
        raise TrajectoryReplayError(
            "trajectory bundle events must all be objects",
            code="trajectory.bundle_event_shape",
        )
    replay_trajectory(manifest, raw_events)
    return manifest, raw_events
