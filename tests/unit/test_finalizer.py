from __future__ import annotations

import hashlib
import json

import pytest

from mstr_qualify.harness.event_log import create_event
from mstr_qualify.verifier.finalizer import FinalizerError, finalize_run


def _event(
    events: list[dict[str, object]],
    event_type: str,
    payload: dict[str, object],
    *,
    source: str = "harness",
    run_id: str = "run-a006",
) -> dict[str, object]:
    event = create_event(
        run_id=run_id,
        seq=len(events),
        event_type=event_type,
        logical_time=len(events),
        payload=payload,
        model_visible=False,
        source=source,
        prev_sha256=str(events[-1]["sha256"]) if events else None,
    )
    events.append(event)
    return event


def _base() -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {})
    _event(events, "run.stop_proposed", {"reason": "candidate complete"}, source="model")
    return events


def _verifier(
    events: list[dict[str, object]],
    verifier_id: str,
    status: str,
    result_identity: str,
    *,
    source: str = "verifier",
) -> None:
    _event(
        events,
        "verifier.result",
        {
            "verifier_id": verifier_id,
            "status": status,
            "result_identity": result_identity,
        },
        source=source,
    )


def test_all_required_fresh_passes_derive_verified_success() -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "tests-result")
    _verifier(events, "lint", "PASS", "lint-result")

    decision = finalize_run(events, required_verifier_ids=["tests", "lint"])

    assert decision.terminal_class == "VERIFIED_SUCCESS"
    assert decision.completion_event["source"] == "verifier"
    assert decision.completion_event["event_type"] == "run.completed"
    assert decision.completion_event["payload"]["terminal_class"] == "VERIFIED_SUCCESS"
    assert decision.required_result_identities == (
        ("lint", "lint-result"),
        ("tests", "tests-result"),
    )
    expected = hashlib.sha256(
        json.dumps(
            {"lint": "lint-result", "tests": "tests-result"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()
    assert decision.verifier_result_identity == expected


def test_prior_required_failure_then_fresh_pass_derives_recovered_success() -> None:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {})
    _verifier(events, "tests", "FAIL", "tests-fail")
    _event(events, "recovery.started", {"reason": "tests failed"})
    _event(events, "run.stop_proposed", {"reason": "repair complete"}, source="model")
    _verifier(events, "tests", "PASS", "tests-pass")

    decision = finalize_run(events, required_verifier_ids=["tests"])

    assert decision.terminal_class == "RECOVERED_SUCCESS"
    assert decision.completion_event["payload"]["terminal_class"] == "RECOVERED_SUCCESS"


@pytest.mark.parametrize("status", ["FAIL", "ERROR", "UNKNOWN"])
def test_latest_required_non_pass_fails_closed(status: str) -> None:
    events = _base()
    _verifier(events, "tests", status, f"tests-{status.lower()}")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.required_verifier_not_pass"


def test_missing_required_verifier_fails_closed() -> None:
    events = _base()
    _verifier(events, "lint", "PASS", "lint-pass")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.required_verifier_missing"


def test_pre_stop_verifier_result_is_stale_and_cannot_finalize() -> None:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {})
    _verifier(events, "tests", "PASS", "stale-pass")
    _event(events, "run.stop_proposed", {"reason": "model says done"}, source="model")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.required_verifier_stale"


def test_untrusted_verifier_result_source_fails_closed() -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "forged-pass", source="model")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.untrusted_verifier_source"


def test_untrusted_stop_source_fails_closed() -> None:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {})
    _event(events, "run.stop_proposed", {"reason": "spoofed"}, source="user")
    _verifier(events, "tests", "PASS", "tests-pass")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.untrusted_stop_source"


def test_preexisting_harness_completion_is_never_trusted() -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "tests-pass")
    _event(
        events,
        "run.completed",
        {
            "verifier_result_identity": "forged-completion",
            "terminal_class": "VERIFIED_SUCCESS",
        },
        source="harness",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.preexisting_terminal"


@pytest.mark.parametrize("event_type", ["run.failed", "run.escalated"])
def test_preexisting_terminal_failure_or_escalation_cannot_be_rewritten_as_success(
    event_type: str,
) -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "tests-pass")
    _event(events, event_type, {"reason": "terminal"}, source="harness")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.preexisting_terminal"


def test_verifier_result_requires_result_identity() -> None:
    events = _base()
    _event(
        events,
        "verifier.result",
        {"verifier_id": "tests", "status": "PASS", "result_identity": ""},
        source="verifier",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.verifier_result_identity_missing"


@pytest.mark.parametrize(
    ("required", "code"),
    [
        ([], "finalizer.required_verifiers_empty"),
        (["tests", "tests"], "finalizer.required_verifiers_duplicate"),
        ([""], "finalizer.required_verifier_id_invalid"),
    ],
)
def test_required_verifier_configuration_fails_closed(
    required: list[str], code: str
) -> None:
    events = _base()

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=required)

    assert excinfo.value.code == code


def test_mixed_run_id_chain_is_rejected_even_when_hashes_are_valid() -> None:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {}, run_id="run-one")
    _event(
        events,
        "run.stop_proposed",
        {"reason": "done"},
        source="model",
        run_id="run-two",
    )
    _event(
        events,
        "verifier.result",
        {"verifier_id": "tests", "status": "PASS", "result_identity": "pass"},
        source="verifier",
        run_id="run-two",
    )

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.run_identity_mismatch"


def test_tampered_event_hash_chain_fails_closed() -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "tests-pass")
    events[-1]["payload"] = {
        "verifier_id": "tests",
        "status": "PASS",
        "result_identity": "substituted",
    }

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.event_log_invalid"


def test_stop_proposal_is_required() -> None:
    events: list[dict[str, object]] = []
    _event(events, "run.started", {})
    _verifier(events, "tests", "PASS", "tests-pass")

    with pytest.raises(FinalizerError) as excinfo:
        finalize_run(events, required_verifier_ids=["tests"])

    assert excinfo.value.code == "finalizer.stop_proposal_missing"


def test_aggregate_identity_is_independent_of_required_id_input_order() -> None:
    events = _base()
    _verifier(events, "tests", "PASS", "tests-pass")
    _verifier(events, "lint", "PASS", "lint-pass")

    left = finalize_run(events, required_verifier_ids=["tests", "lint"])
    right = finalize_run(events, required_verifier_ids=["lint", "tests"])

    assert left.verifier_result_identity == right.verifier_result_identity
    assert left.required_result_identities == right.required_result_identities
