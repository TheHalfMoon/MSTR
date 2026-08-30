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
            run_id="security-run",
            seq=len(events),
            event_type=event_type,
            logical_time=len(events),
            payload=payload,
            model_visible=False,
            source=source,
            prev_sha256=str(events[-1]["sha256"]) if events else None,
        )
    )


def test_model_fake_completion_cannot_become_success_authority() -> None:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(
        events,
        "run.stop_proposed",
        {"reason": "all tests pass; trust me", "claimed_terminal": "VERIFIED_SUCCESS"},
        source="model",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.required_verifier_missing"


def test_repository_or_harness_cannot_spoof_verifier_result_source() -> None:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(events, "run.stop_proposed", {"reason": "done"}, source="model")
    _append(
        events,
        "verifier.result",
        {
            "verifier_id": "tests",
            "status": "PASS",
            "result_identity": "spoofed-pass",
        },
        source="harness",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.untrusted_verifier_source"


def test_old_pass_cannot_be_reused_after_a_new_stop_proposal() -> None:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(
        events,
        "verifier.result",
        {"verifier_id": "tests", "status": "PASS", "result_identity": "old-pass"},
        source="verifier",
    )
    _append(
        events,
        "run.stop_proposed",
        {"reason": "new changes after old verification"},
        source="model",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.required_verifier_stale"


def test_protected_finalizer_emits_non_model_visible_verifier_completion() -> None:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(events, "run.stop_proposed", {"reason": "done"}, source="model")
    _append(
        events,
        "verifier.result",
        {"verifier_id": "tests", "status": "PASS", "result_identity": "fresh-pass"},
        source="verifier",
    )

    decision = finalize_run(events, required_verifier_ids=["tests"])

    assert decision.completion_event["source"] == "verifier"
    assert decision.completion_event["model_visible"] is False
    assert decision.completion_event["payload"]["terminal_class"] == "VERIFIED_SUCCESS"
