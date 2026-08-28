"""Deterministic fixture-only projections for MSTR software-evolution records.

B017 deliberately operates only on synthetic or repository-owned fixtures. It
consumes the B016 record contract without widening it and fails closed when a
forward-step record could expose future history or has inconsistent lineage.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from .schemas import validate_instance

ProjectionKind = Literal["LOCALIZATION", "EDIT", "REVIEW_REPAIR"]

_ALLOWED_FIXTURE_SOURCE_CLASSES = {"REPOSITORY_OWNED_FIXTURE", "SYNTHETIC_VERIFIED"}
_EVENT_COLLECTIONS = (
    ("change_events", "CHANGE"),
    ("test_ci_events", "TEST_CI"),
    ("review_events", "REVIEW"),
    ("recovery_events", "RECOVERY"),
)


class SoftwareEvolutionProjectionError(ValueError):
    """Raised when a B017 fixture cannot be projected without ambiguity/leakage."""


@dataclass(frozen=True)
class _Event:
    event_id: str
    sequence: int
    event_kind: str
    model_visibility: str
    payload: dict[str, Any]


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SoftwareEvolutionProjectionError(f"{label} must be an object")
    return cast(dict[str, Any], value)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise SoftwareEvolutionProjectionError(f"{label} must be a string")
    return value


def _integer(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SoftwareEvolutionProjectionError(f"{label} must be an integer")
    return value


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SoftwareEvolutionProjectionError(f"{label} must be a string array")
    return cast(list[str], value)


def _collect_events(record: Mapping[str, Any]) -> tuple[_Event, ...]:
    events: list[_Event] = []
    seen_ids: set[str] = set()
    seen_sequences: set[int] = set()

    for collection_name, event_kind in _EVENT_COLLECTIONS:
        raw_collection = record[collection_name]
        if not isinstance(raw_collection, list):
            raise SoftwareEvolutionProjectionError(f"{collection_name} must be an array")
        for raw_event in raw_collection:
            payload = _object(raw_event, f"{collection_name} item")
            event_id = _string(payload.get("event_id"), f"{collection_name}.event_id")
            sequence = _integer(payload.get("sequence"), f"{collection_name}.sequence")
            visibility = _string(
                payload.get("model_visibility"), f"{collection_name}.model_visibility"
            )
            if event_id in seen_ids:
                raise SoftwareEvolutionProjectionError(f"duplicate event_id: {event_id}")
            if sequence in seen_sequences:
                raise SoftwareEvolutionProjectionError(f"duplicate event sequence: {sequence}")
            seen_ids.add(event_id)
            seen_sequences.add(sequence)
            events.append(
                _Event(
                    event_id=event_id,
                    sequence=sequence,
                    event_kind=event_kind,
                    model_visibility=visibility,
                    payload=payload,
                )
            )

    return tuple(sorted(events, key=lambda event: (event.sequence, event.event_id)))


def _validate_lineage(record: Mapping[str, Any], events: tuple[_Event, ...]) -> None:
    current_revision = _string(record["base_revision"], "base_revision")
    by_id = {event.event_id: event for event in events}

    for event in events:
        payload = event.payload
        if event.event_kind == "CHANGE":
            before = _string(payload.get("before_revision"), "change.before_revision")
            after = _string(payload.get("after_revision"), "change.after_revision")
            if before != current_revision:
                raise SoftwareEvolutionProjectionError(
                    f"change {event.event_id} does not extend current revision: "
                    f"expected {current_revision}, got {before}"
                )
            if after == before:
                raise SoftwareEvolutionProjectionError(
                    f"change {event.event_id} must advance the revision"
                )
            current_revision = after
        elif event.event_kind in {"TEST_CI", "REVIEW"}:
            revision = _string(payload.get("revision"), f"{event.event_kind}.revision")
            if revision != current_revision:
                raise SoftwareEvolutionProjectionError(
                    f"{event.event_id} does not reference current revision: "
                    f"expected {current_revision}, got {revision}"
                )
        else:
            trigger_id = _string(payload.get("trigger_event_id"), "recovery.trigger_event_id")
            trigger = by_id.get(trigger_id)
            if trigger is None or trigger.sequence >= event.sequence:
                raise SoftwareEvolutionProjectionError(
                    f"recovery {event.event_id} requires a prior trigger event"
                )
            current_revision = _string(
                payload.get("resulting_revision"), "recovery.resulting_revision"
            )

    final_revision = _string(record["final_revision"], "final_revision")
    if final_revision != current_revision:
        raise SoftwareEvolutionProjectionError(
            "final_revision must equal the terminal fixture revision: "
            f"expected {current_revision}, got {final_revision}"
        )


def _future_artifact_ids(events: tuple[_Event, ...], cutoff: int) -> set[str]:
    artifact_ids: set[str] = set()
    for event in events:
        if event.sequence <= cutoff:
            continue
        payload = event.payload
        if event.event_kind == "CHANGE":
            artifact_ids.add(
                _string(payload.get("change_artifact_identity"), "change.change_artifact_identity")
            )
        elif event.event_kind == "TEST_CI":
            artifact_ids.add(_string(payload.get("evidence_identity"), "test_ci.evidence_identity"))
        elif event.event_kind == "REVIEW":
            artifact_ids.add(_string(payload.get("feedback_identity"), "review.feedback_identity"))
    return artifact_ids


def _validate_forward_boundary(
    record: Mapping[str, Any], events: tuple[_Event, ...]
) -> tuple[dict[str, Any], dict[str, Any], _Event]:
    manifest = _object(record["visible_context_manifest"], "visible_context_manifest")
    boundary = _object(record["future_history_boundary"], "future_history_boundary")

    if boundary.get("projection_mode") != "FORWARD_STEP":
        raise SoftwareEvolutionProjectionError("B017 fixture proof accepts FORWARD_STEP only")

    target_id = _string(boundary.get("target_event_id"), "future_history_boundary.target_event_id")
    cutoff = _integer(boundary.get("cutoff_sequence"), "future_history_boundary.cutoff_sequence")
    if manifest.get("target_event_id") != target_id or manifest.get("cutoff_sequence") != cutoff:
        raise SoftwareEvolutionProjectionError("visible context and future-history boundary disagree")

    by_id = {event.event_id: event for event in events}
    target = by_id.get(target_id)
    if target is None:
        raise SoftwareEvolutionProjectionError(f"target event does not exist: {target_id}")

    future = tuple(event for event in events if event.sequence > cutoff)
    if not future or future[0].event_id != target_id:
        raise SoftwareEvolutionProjectionError(
            "target event must be the first chronological event after the cutoff"
        )
    if target.model_visibility != "FUTURE_HIDDEN":
        raise SoftwareEvolutionProjectionError("target event must remain future-hidden")

    for event in events:
        if event.sequence > cutoff and event.model_visibility != "FUTURE_HIDDEN":
            raise SoftwareEvolutionProjectionError(
                f"future event is not hidden: {event.event_id}"
            )
        if (
            event.sequence <= cutoff
            and event.event_kind in {"CHANGE", "RECOVERY"}
            and event.model_visibility != "MODEL_VISIBLE"
        ):
            raise SoftwareEvolutionProjectionError(
                f"prior revision-changing event must be model-visible: {event.event_id}"
            )

    expected_visible = {
        event.event_id
        for event in events
        if event.sequence <= cutoff and event.model_visibility == "MODEL_VISIBLE"
    }
    declared_visible = set(_string_list(manifest.get("visible_event_ids"), "visible_event_ids"))
    if declared_visible != expected_visible:
        raise SoftwareEvolutionProjectionError(
            "visible_event_ids do not match the model-visible pre-cutoff event set"
        )

    expected_excluded = {event.event_id for event in future}
    declared_excluded = set(
        _string_list(manifest.get("excluded_future_event_ids"), "excluded_future_event_ids")
    )
    if declared_excluded != expected_excluded:
        raise SoftwareEvolutionProjectionError(
            "excluded_future_event_ids do not match the post-cutoff event set"
        )

    visible_artifacts = set(
        _string_list(manifest.get("visible_artifact_ids"), "visible_artifact_ids")
    )
    leaked_artifacts = visible_artifacts & _future_artifact_ids(events, cutoff)
    if leaked_artifacts:
        leaked = ", ".join(sorted(leaked_artifacts))
        raise SoftwareEvolutionProjectionError(
            f"visible_artifact_ids expose future event artifacts: {leaked}"
        )

    return manifest, boundary, target


def _current_revision(record: Mapping[str, Any], events: tuple[_Event, ...], cutoff: int) -> str:
    revision = _string(record["base_revision"], "base_revision")
    for event in events:
        if event.sequence > cutoff:
            break
        if event.event_kind == "CHANGE":
            revision = _string(event.payload.get("after_revision"), "change.after_revision")
        elif event.event_kind == "RECOVERY":
            revision = _string(
                event.payload.get("resulting_revision"), "recovery.resulting_revision"
            )
    return revision


def _supervision_target(kind: ProjectionKind, target: _Event, visible_ids: set[str]) -> dict[str, Any]:
    payload = target.payload
    if kind in {"LOCALIZATION", "EDIT"}:
        if target.event_kind != "CHANGE":
            raise SoftwareEvolutionProjectionError(f"{kind} requires a CHANGE target event")
        result: dict[str, Any] = {
            "event_id": target.event_id,
            "event_kind": target.event_kind,
            "change_artifact_identity": _string(
                payload.get("change_artifact_identity"), "change.change_artifact_identity"
            ),
        }
        if kind == "EDIT":
            result["before_revision"] = _string(
                payload.get("before_revision"), "change.before_revision"
            )
            result["after_revision"] = _string(
                payload.get("after_revision"), "change.after_revision"
            )
        return result

    if target.event_kind != "RECOVERY":
        raise SoftwareEvolutionProjectionError("REVIEW_REPAIR requires a RECOVERY target event")
    trigger_id = _string(payload.get("trigger_event_id"), "recovery.trigger_event_id")
    if trigger_id not in visible_ids:
        raise SoftwareEvolutionProjectionError(
            "REVIEW_REPAIR requires its trigger event to be model-visible"
        )
    return {
        "event_id": target.event_id,
        "event_kind": target.event_kind,
        "trigger_event_id": trigger_id,
        "action": _string(payload.get("action"), "recovery.action"),
        "resulting_revision": _string(
            payload.get("resulting_revision"), "recovery.resulting_revision"
        ),
    }


def project_software_evolution(
    record: dict[str, Any], *, kind: ProjectionKind
) -> dict[str, Any]:
    """Project one B016 record into a deterministic B017 forward-step example."""

    validate_instance("mstr-software-evolution-record-v0", record)

    repository_identity = _object(record["repository_identity"], "repository_identity")
    source_class = _string(repository_identity.get("source_class"), "repository_identity.source_class")
    if source_class not in _ALLOWED_FIXTURE_SOURCE_CLASSES:
        raise SoftwareEvolutionProjectionError(
            f"B017 is fixture-only; unsupported source_class: {source_class}"
        )

    if record.get("contamination_status") != "CLEAR":
        raise SoftwareEvolutionProjectionError("B017 requires CLEAR fixture contamination status")
    rights = _object(record["rights"], "rights")
    provenance = _object(record["provenance"], "provenance")
    if rights.get("decision") != "COMPATIBLE":
        raise SoftwareEvolutionProjectionError("B017 requires compatible fixture rights")
    if provenance.get("lineage_status") != "COMPLETE":
        raise SoftwareEvolutionProjectionError("B017 requires complete fixture lineage")

    events = _collect_events(record)
    _validate_lineage(record, events)
    manifest, boundary, target = _validate_forward_boundary(record, events)
    cutoff = _integer(boundary["cutoff_sequence"], "future_history_boundary.cutoff_sequence")

    visible_events = tuple(
        event
        for event in events
        if event.sequence <= cutoff and event.model_visibility == "MODEL_VISIBLE"
    )
    visible_ids = {event.event_id for event in visible_events}
    future_events = tuple(event for event in events if event.sequence > cutoff)

    model_input: dict[str, Any] = {
        "record_id": _string(record["record_id"], "record_id"),
        "repository_identity": copy.deepcopy(repository_identity),
        "base_revision": _string(record["base_revision"], "base_revision"),
        "current_revision": _current_revision(record, events, cutoff),
        "direction_identity": copy.deepcopy(
            _object(record["direction_identity"], "direction_identity")
        ),
        "visible_artifact_ids": sorted(
            _string_list(manifest["visible_artifact_ids"], "visible_artifact_ids")
        ),
        "visible_events": [
            {**copy.deepcopy(event.payload), "evolution_event_type": event.event_kind}
            for event in visible_events
        ],
    }
    if "issue_pr_identity" in record:
        model_input["issue_pr_identity"] = _string(
            record["issue_pr_identity"], "issue_pr_identity"
        )

    return {
        "projection_version": "mstr.software-evolution-projection.v0",
        "projection_kind": kind,
        "model_input": model_input,
        "supervision_target": _supervision_target(kind, target, visible_ids),
        "audit": {
            "manifest_id": _string(manifest["manifest_id"], "visible_context_manifest.manifest_id"),
            "boundary_id": _string(boundary["boundary_id"], "future_history_boundary.boundary_id"),
            "projection_mode": "FORWARD_STEP",
            "target_event_id": target.event_id,
            "cutoff_sequence": cutoff,
            "excluded_future_event_ids": [event.event_id for event in future_events],
            "future_history_hidden": True,
        },
    }


def canonical_projection_json(projection: Mapping[str, Any]) -> str:
    """Serialize a projection with a stable ordering for fixture/evidence comparison."""

    return json.dumps(projection, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
