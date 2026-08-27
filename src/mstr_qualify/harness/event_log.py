"""A003: Append-oriented event log + deterministic replay.

Every event carries a mandatory SHA-256 computed over its canonical bytes
(the serialized event object with ``sha256`` and ``prev_event_sha256``
removed, keys sorted, separators compact, ensure_ascii=True).  The
``prev_event_sha256`` field chains events; seq=0 uses the all-zeros sentinel.
Replay MUST reject missing hashes, duplicates, gaps, reordered or substituted
events, and broken predecessor chains.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SENTINEL_PREV = "0" * 64

_EVENT_FIELDS = (
    "schema_version", "run_id", "seq", "event_type",
    "logical_time", "payload", "model_visible", "source",
    "step_id", "sha256", "prev_event_sha256",
)


def canonical_bytes(event: dict[str, Any]) -> str:
    """Produce the canonical UTF-8 serialization used for hash computation."""
    stripped = {k: v for k, v in event.items() if k not in ("sha256", "prev_event_sha256")}
    return json.dumps(stripped, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(event).encode("utf-8")).hexdigest()


class EventLogError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class EventEntry:
    raw: dict[str, Any]
    sha256: str


def validate_event(
    event: dict[str, Any], expected_seq: int, expected_prev: str | None
) -> EventEntry:
    """Validate a single event's structural and integrity properties."""
    from mstr_qualify.schemas import validate_instance

    validate_instance("mstr-run-event-v0", event)

    seq = event["seq"]
    if seq != expected_seq:
        raise EventLogError(
            f"sequence gap or reorder: expected {expected_seq}, got {seq}",
            code="event.seq_mismatch",
        )

    prev = event.get("prev_event_sha256")
    if seq == 0:
        if prev != SENTINEL_PREV:
            raise EventLogError(
                "seq=0 event must use the all-zeros prev sentinel",
                code="event.bad_genesis_prev",
            )
    else:
        if expected_prev is None:
            raise EventLogError(
                "cannot verify predecessor for seq>0 without prior hash",
                code="event.missing_predecessor_context",
            )
        if prev != expected_prev:
            raise EventLogError(
                f"predecessor chain broken at seq={seq}",
                code="event.predecessor_broken",
            )

    actual_hash = compute_event_hash(event)
    declared = event.get("sha256")
    if declared != actual_hash:
        raise EventLogError(
            f"event hash mismatch at seq={seq}: expected {actual_hash}, got {declared}",
            code="event.hash_substituted",
        )
    return EventEntry(raw=event, sha256=actual_hash)


def append_event(log: list[EventEntry], event: dict[str, Any]) -> EventEntry:
    """Append an event to an in-memory log, validating chain continuity."""
    expected_seq = len(log)
    expected_prev = log[-1].sha256 if log else None
    entry = validate_event(event, expected_seq, expected_prev)
    log.append(entry)
    return entry


def create_event(
    run_id: str,
    seq: int,
    event_type: str,
    logical_time: int,
    payload: dict[str, Any],
    *,
    model_visible: bool = False,
    source: str = "harness",
    step_id: str | None = None,
    prev_sha256: str | None = None,
) -> dict[str, Any]:
    """Create a new event with correct sentinel/hash values."""
    event: dict[str, Any] = {
        "schema_version": "mstr.run-event.v0",
        "run_id": run_id,
        "seq": seq,
        "event_type": event_type,
        "logical_time": logical_time,
        "payload": payload,
        "model_visible": model_visible,
        "source": source,
        "step_id": step_id,
    }
    if step_id is None:
        del event["step_id"]
    event["prev_event_sha256"] = prev_sha256 if seq > 0 else SENTINEL_PREV
    # Remove optional field if absent to match schema exactly
    if "step_id" in event and event["step_id"] is None:
        del event["step_id"]
    event["sha256"] = compute_event_hash(event)
    return event


def replay(events: list[dict[str, Any]]) -> list[EventEntry]:
    """Replay a full event sequence, verifying every integrity property."""
    log: list[EventEntry] = []
    for event in events:
        append_event(log, event)
    return log


def save_log(log: list[EventEntry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps([e.raw for e in log], indent=2, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")


def load_log(path: Path) -> list[EventEntry]:
    raw_events = json.loads(path.read_text(encoding="utf-8"))
    return replay(raw_events)


def model_visible_history(log: list[EventEntry]) -> list[dict[str, Any]]:
    """Reconstruct only the model-visible subset of the history."""
    return [e.raw for e in log if e.raw.get("model_visible") is True]
