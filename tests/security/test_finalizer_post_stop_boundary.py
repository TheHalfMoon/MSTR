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
            run_id="post-stop-security",
            seq=len(events),
            event_type=event_type,
            logical_time=len(events),
            payload=payload,
            model_visible=False,
            source=source,
            prev_sha256=str(events[-1]["sha256"]) if events else None,
        )
    )


@pytest.mark.parametrize("mutation_after_pass", [False, True])
def test_state_mutation_after_latest_stop_requires_fresh_stop_proposal(
    mutation_after_pass: bool,
) -> None:
    events: list[dict[str, object]] = []
    _append(events, "run.started", {}, source="harness")
    _append(events, "run.stop_proposed", {"reason": "done"}, source="model")

    if not mutation_after_pass:
        _append(
            events,
            "edit.applied",
            {"path": "src/example.py", "identity": "changed-after-stop"},
            source="harness",
        )

    _append(
        events,
        "verifier.result",
        {
            "verifier_id": "tests",
            "status": "PASS",
            "result_identity": "tests-pass",
        },
        source="verifier",
    )

    if mutation_after_pass:
        _append(
            events,
            "edit.applied",
            {"path": "src/example.py", "identity": "changed-after-pass"},
            source="harness",
        )

    with pytest.raises(FinalizerError) as exc_info:
        finalize_run(events, required_verifier_ids=["tests"])

    assert exc_info.value.code == "finalizer.post_stop_event_invalid"
