from __future__ import annotations

import pytest

from mstr_qualify.harness.event_log import create_event
from mstr_qualify.verifier.finalizer import FinalizerError, finalize_run


def _append(
    events: list[dict[str, object]],
    event_type: str,
    payload: dict[str, object],
    *,
    source: str,
) -> None:
    events.append(
        create_event(
            run_id="identity-boundary-run",
            seq=len(events),
            event_type=event_type,
            logical_time=len(events),
            payload=payload,
            model_visible=False,
            source=source,
            prev_sha256=str(events[-1]["sha256"]) if events else None,
        )
    )


def _base() -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(events, "run.stop_proposed", {"reason": "done"}, source="model")
    return events


def test_required_verifier_id_with_surrounding_whitespace_is_rejected() -> None:
    events = _base()

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=[" tests"])

    assert excinfo.value.code == "finalizer.required_verifier_id_invalid"


def test_verifier_event_id_with_surrounding_whitespace_is_rejected() -> None:
    events = _base()
    _append(
        events,
        "verifier.result",
        {
            "verifier_id": "tests ",
            "status": "PASS",
            "result_identity": "exact-result",
        },
        source="verifier",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.verifier_id_invalid"


def test_result_identity_with_surrounding_whitespace_is_rejected_not_rewritten() -> None:
    events = _base()
    _append(
        events,
        "verifier.result",
        {
            "verifier_id": "tests",
            "status": "PASS",
            "result_identity": " exact-result ",
        },
        source="verifier",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.verifier_result_identity_invalid"
