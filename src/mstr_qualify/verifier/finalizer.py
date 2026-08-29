"""A006: protected finalizer / verifier boundary.

Canonical success is derived only from integrity-checked, verifier-authored
results that satisfy the required verifier set *after* the latest builder stop
proposal.  Model/harness/system completion text is never success authority.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from mstr_qualify.harness.event_log import EventLogError, create_event, replay

VerifierStatus = Literal["PASS", "FAIL", "ERROR", "UNKNOWN"]
TerminalClass = Literal["VERIFIED_SUCCESS", "RECOVERED_SUCCESS"]
_VALID_STATUSES = frozenset({"PASS", "FAIL", "ERROR", "UNKNOWN"})


class FinalizerError(ValueError):
    """Fail-closed finalizer error with a stable machine code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class FinalizationDecision:
    run_id: str
    terminal_class: TerminalClass
    verifier_result_identity: str
    required_result_identities: tuple[tuple[str, str], ...]
    completion_event: dict[str, Any]


@dataclass(frozen=True)
class _VerifierObservation:
    verifier_id: str
    status: VerifierStatus
    result_identity: str
    seq: int


def _required_ids(required_verifier_ids: Iterable[str]) -> tuple[str, ...]:
    values = tuple(required_verifier_ids)
    if not values:
        raise FinalizerError(
            "at least one required verifier is mandatory",
            code="finalizer.required_verifiers_empty",
        )
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise FinalizerError(
            "required verifier ids must be non-empty strings",
            code="finalizer.required_verifier_id_invalid",
        )
    normalized = tuple(value.strip() for value in values)
    if len(set(normalized)) != len(normalized):
        raise FinalizerError(
            "required verifier ids must be unique",
            code="finalizer.required_verifiers_duplicate",
        )
    return tuple(sorted(normalized))


def _observation(event: dict[str, Any]) -> _VerifierObservation:
    if event.get("source") != "verifier":
        raise FinalizerError(
            "verifier.result must be authored by source=verifier",
            code="finalizer.untrusted_verifier_source",
        )
    payload = event.get("payload")
    if not isinstance(payload, dict):
        raise FinalizerError(
            "verifier.result payload must be an object",
            code="finalizer.verifier_payload_invalid",
        )
    verifier_id = payload.get("verifier_id")
    if not isinstance(verifier_id, str) or not verifier_id.strip():
        raise FinalizerError(
            "verifier.result requires a non-empty verifier_id",
            code="finalizer.verifier_id_missing",
        )
    status = payload.get("status")
    if status not in _VALID_STATUSES:
        raise FinalizerError(
            "verifier.result status must be PASS, FAIL, ERROR, or UNKNOWN",
            code="finalizer.verifier_status_invalid",
        )
    result_identity = payload.get("result_identity")
    if not isinstance(result_identity, str) or not result_identity.strip():
        raise FinalizerError(
            "verifier.result requires a non-empty result_identity",
            code="finalizer.verifier_result_identity_missing",
        )
    return _VerifierObservation(
        verifier_id=verifier_id.strip(),
        status=status,
        result_identity=result_identity.strip(),
        seq=int(event["seq"]),
    )


def _aggregate_identity(observations: Sequence[_VerifierObservation]) -> str:
    payload = {
        observation.verifier_id: observation.result_identity
        for observation in sorted(observations, key=lambda item: item.verifier_id)
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def finalize_run(
    events: Sequence[dict[str, Any]],
    *,
    required_verifier_ids: Iterable[str],
) -> FinalizationDecision:
    """Derive one successful terminal event from protected verifier evidence.

    The function intentionally has no path for a caller to pass a desired
    terminal class.  It replays the complete event hash chain, rejects any
    pre-existing completion event, requires a stop proposal, requires fresh
    post-proposal results from every required verifier, and derives success
    solely from the latest verifier-authored results.
    """

    required_ids = _required_ids(required_verifier_ids)
    if not events:
        raise FinalizerError(
            "cannot finalize an empty event log",
            code="finalizer.event_log_empty",
        )

    try:
        log = replay(list(events))
    except (EventLogError, ValueError) as exc:
        raise FinalizerError(
            "event log failed integrity/schema validation",
            code="finalizer.event_log_invalid",
        ) from exc

    raw_events = [entry.raw for entry in log]
    run_ids = {event.get("run_id") for event in raw_events}
    if len(run_ids) != 1 or not isinstance(next(iter(run_ids)), str):
        raise FinalizerError(
            "all events must belong to one non-empty run_id",
            code="finalizer.run_identity_mismatch",
        )
    run_id = next(iter(run_ids))
    assert isinstance(run_id, str)
    if not run_id.strip():
        raise FinalizerError(
            "run_id must be non-empty",
            code="finalizer.run_identity_mismatch",
        )

    if any(event["event_type"] == "run.completed" for event in raw_events):
        raise FinalizerError(
            "pre-existing run.completed is not trusted as finalizer input",
            code="finalizer.preexisting_completion",
        )

    stop_sequences = [
        int(event["seq"])
        for event in raw_events
        if event["event_type"] == "run.stop_proposed"
    ]
    if not stop_sequences:
        raise FinalizerError(
            "builder must propose stop before protected finalization",
            code="finalizer.stop_proposal_missing",
        )
    latest_stop_seq = max(stop_sequences)

    observations: list[_VerifierObservation] = []
    for event in raw_events:
        if event["event_type"] == "verifier.result":
            observations.append(_observation(event))

    by_verifier: dict[str, list[_VerifierObservation]] = {}
    for observation in observations:
        by_verifier.setdefault(observation.verifier_id, []).append(observation)

    final_required: list[_VerifierObservation] = []
    recovered = any(
        event["event_type"] in {"recovery.started", "recovery.result"}
        for event in raw_events
    )
    for verifier_id in required_ids:
        history = sorted(by_verifier.get(verifier_id, []), key=lambda item: item.seq)
        if not history:
            raise FinalizerError(
                f"required verifier {verifier_id!r} has no result",
                code="finalizer.required_verifier_missing",
            )
        latest = history[-1]
        if latest.seq <= latest_stop_seq:
            raise FinalizerError(
                f"required verifier {verifier_id!r} has no fresh post-stop result",
                code="finalizer.required_verifier_stale",
            )
        if latest.status != "PASS":
            raise FinalizerError(
                f"required verifier {verifier_id!r} latest status is {latest.status}",
                code="finalizer.required_verifier_not_pass",
            )
        if any(item.status != "PASS" for item in history[:-1]):
            recovered = True
        final_required.append(latest)

    aggregate_identity = _aggregate_identity(final_required)
    terminal_class: TerminalClass = (
        "RECOVERED_SUCCESS" if recovered else "VERIFIED_SUCCESS"
    )
    last_event = raw_events[-1]
    completion_event = create_event(
        run_id=run_id,
        seq=len(raw_events),
        event_type="run.completed",
        logical_time=int(last_event["logical_time"]) + 1,
        payload={
            "verifier_result_identity": aggregate_identity,
            "terminal_class": terminal_class,
        },
        model_visible=False,
        source="verifier",
        prev_sha256=str(last_event["sha256"]),
    )

    return FinalizationDecision(
        run_id=run_id,
        terminal_class=terminal_class,
        verifier_result_identity=aggregate_identity,
        required_result_identities=tuple(
            (item.verifier_id, item.result_identity)
            for item in sorted(final_required, key=lambda value: value.verifier_id)
        ),
        completion_event=completion_event,
    )
