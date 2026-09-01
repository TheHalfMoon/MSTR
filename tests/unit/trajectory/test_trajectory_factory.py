"""A018 trajectory recorder/replay/admission tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.harness.event_log import compute_event_hash, create_event
from mstr_qualify.trajectory import (
    TrajectoryAdmissionError,
    TrajectoryReplayError,
    build_trajectory_manifest,
    load_trajectory_bundle,
    record_trajectory_bundle,
    replay_trajectory,
)
from mstr_qualify.verifier.finalizer import finalize_run


def _run_identity(run_id: str = "run-a018-001") -> dict[str, Any]:
    return {
        "run_id": run_id,
        "task_manifest_id": "direction-task-a018-fixture",
        "repository_revision": "f222df1b939fc5db792021d6883d977014502dba",
        "environment_manifest_id": "env-a018-fixture",
        "model_id": "N/A_CONTRACT_FIXTURE",
        "model_revision": "N/A_CONTRACT_FIXTURE",
        "artifact_sha256": "0" * 64,
        "runtime_id": "N/A_CONTRACT_FIXTURE",
        "interaction_contract_id": "mstr.interaction.fixture.v0",
        "loop_contract_id": "mstr.loop-contract.v0",
        "harness_profile_id": "h0-neutral-fixture",
        "verifier_manifest_id": "verifier-a018-fixture",
        "sampling_config": {"temperature": 0},
        "seed": 0,
        "timeout_seconds": 60,
        "cache_state": "EMPTY",
        "hardware_profile_id": "fixture-hardware",
    }


def _provenance(source_class: str = "REPOSITORY_OWNED_FIXTURE") -> dict[str, Any]:
    return {
        "source_class": source_class,
        "source_identity": "tests/unit/trajectory/test_trajectory_factory.py",
        "provenance_status": "COMPLETE",
        "rights_status": "NOT_APPLICABLE",
        "secret_scan_status": "NOT_APPLICABLE",
        "contamination_evidence_identity": "fixture-contamination-clear",
    }


def _health(
    *,
    health_class: str = "HEALTHY",
    stage_class: str = "CLEAN_POSITIVE_ELIGIBLE",
    task_identity: str = "direction-task-a018-fixture",
    verifier_manifest_id: str = "verifier-a018-fixture",
) -> dict[str, Any]:
    return {
        "schema_version": "mstr.verifier-health.v0",
        "verifier_health_id": "vh-a018-fixture",
        "task_identity": task_identity,
        "verifier_manifest_id": verifier_manifest_id,
        "evaluator_hashes": [{"path": "tests/verifier.py", "sha256": "a" * 64}],
        "protected_paths": ["tests/verifier.py"],
        "protected_path_integrity": "PASS",
        "reference_oracle_status": "PASS",
        "noop_fail_status": "PASS",
        "known_bad_fail_status": "PASS",
        "mutation_results": [
            {
                "mutation_id": "delete-tests",
                "shortcut_class": "DELETE_TESTS",
                "expected_rejection": True,
                "observed_rejection": True,
                "evidence_identity": "fixture-mutation",
            }
        ],
        "generated_test_independence": "INDEPENDENT",
        "leakage_checks": [
            {
                "check_id": "future-history",
                "leakage_class": "FUTURE_HISTORY",
                "status": "CLEAR",
                "evidence_identity": "fixture-leakage",
            }
        ],
        "disagreement_signals": [
            {
                "signal_id": "existing-vs-targeted",
                "left_evidence_identity": "fixture-left",
                "right_evidence_identity": "fixture-right",
                "status": "AGREE",
            }
        ],
        "health_class": health_class,
        "training_stage_eligibility": [
            {
                "stage_id": "MSTR-002-SFT",
                "admission_class": stage_class,
                "reason_codes": [] if stage_class == "CLEAN_POSITIVE_ELIGIBLE" else ["DIAGNOSTIC"],
            },
            {
                "stage_id": "MSTR-002-PREFERENCE",
                "admission_class": stage_class,
                "reason_codes": [] if stage_class == "CLEAN_POSITIVE_ELIGIBLE" else ["DIAGNOSTIC"],
            },
        ],
    }


def _successful_events(*, recovered: bool = False) -> list[dict[str, Any]]:
    run_id = "run-a018-001"
    events: list[dict[str, Any]] = []
    first = create_event(run_id, 0, "run.started", 0, {"goal": "fixture"})
    events.append(first)
    prev = first["sha256"]

    seq = 1
    logical_time = 1
    if recovered:
        failed = create_event(
            run_id,
            seq,
            "verifier.result",
            logical_time,
            {
                "verifier_id": "tests",
                "status": "FAIL",
                "result_identity": "fixture-failed-tests",
            },
            source="verifier",
            prev_sha256=prev,
        )
        events.append(failed)
        prev = failed["sha256"]
        seq += 1
        logical_time += 1

    stop = create_event(
        run_id,
        seq,
        "run.stop_proposed",
        logical_time,
        {"reason": "ready"},
        source="harness",
        prev_sha256=prev,
    )
    events.append(stop)
    prev = stop["sha256"]
    seq += 1
    logical_time += 1

    passed = create_event(
        run_id,
        seq,
        "verifier.result",
        logical_time,
        {
            "verifier_id": "tests",
            "status": "PASS",
            "result_identity": "fixture-passed-tests",
        },
        source="verifier",
        prev_sha256=prev,
    )
    events.append(passed)

    decision = finalize_run(events, required_verifier_ids=("tests",))
    events.append(decision.completion_event)
    return events


def _failed_events() -> list[dict[str, Any]]:
    run_id = "run-a018-001"
    started = create_event(run_id, 0, "run.started", 0, {"goal": "fixture"})
    failed = create_event(
        run_id,
        1,
        "run.failed",
        1,
        {"reason": "tests failed"},
        source="harness",
        prev_sha256=started["sha256"],
    )
    return [started, failed]


def test_clean_success_sft_requires_and_binds_verifier_proof() -> None:
    events = _successful_events()
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-clean-success",
        events=events,
        run_identity=_run_identity(),
        provenance=_provenance(),
        requested_lane="SFT",
        verifier_health_record=_health(),
        verifier_health_stage_id="MSTR-002-SFT",
    )

    assert manifest["terminal_class"] == "VERIFIED_SUCCESS"
    assert manifest["training_admission"] == "ADMITTED_SFT"
    assert manifest["training_labels"] == {"label_kind": "CLEAN_POSITIVE"}
    assert manifest["verifier_result_identity"] == events[-1]["payload"]["verifier_result_identity"]
    assert replay_trajectory(manifest, events) == events


def test_success_without_verifier_health_is_rejected_from_training() -> None:
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-no-health",
        events=_successful_events(),
        run_identity=_run_identity(),
        provenance=_provenance(),
        requested_lane="SFT",
    )

    assert manifest["training_admission"] == "REJECTED"
    assert manifest["admission_reasons"] == ["VERIFIER_HEALTH_REQUIRED_FOR_TRAINING"]


def test_success_completion_must_be_verifier_authored() -> None:
    events = _successful_events()
    terminal = dict(events[-1])
    terminal["source"] = "harness"
    terminal["sha256"] = ""
    terminal["sha256"] = compute_event_hash(terminal)
    events[-1] = terminal

    with pytest.raises(TrajectoryReplayError) as exc:
        build_trajectory_manifest(
            trajectory_id="trajectory-a018-untrusted-success",
            events=events,
            run_identity=_run_identity(),
            provenance=_provenance(),
        )
    assert exc.value.code == "trajectory.success_source_untrusted"


def test_valid_failure_remains_preference_evidence() -> None:
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-valid-failure",
        events=_failed_events(),
        run_identity=_run_identity(),
        provenance=_provenance(),
        requested_lane="PREFERENCE",
        failure_terminal_class="FAILED_VALID",
        failure_classes=("TEST_FAILURE",),
        verifier_health_record=_health(),
        verifier_health_stage_id="MSTR-002-PREFERENCE",
    )

    assert manifest["terminal_class"] == "FAILED_VALID"
    assert manifest["verifier_result_identity"] is None
    assert manifest["training_admission"] == "ADMITTED_PREFERENCE"
    assert manifest["training_labels"] == {"label_kind": "FAILURE_PREFERENCE_EVIDENCE"}


def test_private_user_trace_is_rejected_and_not_persisted(tmp_path: Path) -> None:
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-private",
        events=_failed_events(),
        run_identity=_run_identity(),
        provenance=_provenance("PRIVATE_USER_REPOSITORY"),
        requested_lane="PREFERENCE",
        failure_terminal_class="FAILED_VALID",
        failure_classes=("TEST_FAILURE",),
        verifier_health_record=_health(),
        verifier_health_stage_id="MSTR-002-PREFERENCE",
    )
    path = tmp_path / "trajectory.json"

    assert manifest["training_admission"] == "REJECTED"
    assert "PRIVATE_OR_PRODUCTION_TRACE_REJECTED_V0" in manifest["admission_reasons"]
    with pytest.raises(TrajectoryReplayError) as exc:
        record_trajectory_bundle(path, manifest=manifest, events=_failed_events())
    assert exc.value.code == "trajectory.private_source_not_ingested"
    assert not path.exists()


def test_replay_rejects_tampered_event_payload() -> None:
    events = _successful_events()
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-tamper",
        events=events,
        run_identity=_run_identity(),
        provenance=_provenance(),
    )
    events[0]["payload"]["goal"] = "tampered"

    with pytest.raises(TrajectoryReplayError) as exc:
        replay_trajectory(manifest, events)
    assert exc.value.code == "trajectory.event_log_invalid"


def test_replay_rejects_manifest_event_digest_mismatch() -> None:
    events = _successful_events()
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-digest",
        events=events,
        run_identity=_run_identity(),
        provenance=_provenance(),
    )
    manifest["event_log_sha256"] = "f" * 64

    with pytest.raises(TrajectoryReplayError) as exc:
        replay_trajectory(manifest, events)
    assert exc.value.code == "trajectory.event_digest_mismatch"


def test_verifier_health_identity_mismatch_fails_closed() -> None:
    with pytest.raises(TrajectoryAdmissionError) as exc:
        build_trajectory_manifest(
            trajectory_id="trajectory-a018-health-mismatch",
            events=_successful_events(),
            run_identity=_run_identity(),
            provenance=_provenance(),
            requested_lane="SFT",
            verifier_health_record=_health(task_identity="other-task"),
            verifier_health_stage_id="MSTR-002-SFT",
        )
    assert exc.value.code == "trajectory.health_task_mismatch"


def test_recovered_success_replays_failure_and_recovery_evidence() -> None:
    events = _successful_events(recovered=True)
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-recovered",
        events=events,
        run_identity=_run_identity(),
        provenance=_provenance(),
        requested_lane="SFT",
        failure_classes=("TEST_FAILURE",),
        verifier_health_record=_health(),
        verifier_health_stage_id="MSTR-002-SFT",
    )

    assert manifest["terminal_class"] == "RECOVERED_SUCCESS"
    assert manifest["recovery_count"] == 1
    assert manifest["training_admission"] == "ADMITTED_SFT"
    assert replay_trajectory(manifest, events) == events


def test_timeout_requires_timeout_failure_class() -> None:
    with pytest.raises(TrajectoryReplayError) as exc:
        build_trajectory_manifest(
            trajectory_id="trajectory-a018-timeout-invalid",
            events=_failed_events(),
            run_identity=_run_identity(),
            provenance=_provenance(),
            failure_terminal_class="TIMEOUT_VALID",
            failure_classes=("TEST_FAILURE",),
        )
    assert exc.value.code == "trajectory.manifest_invalid"


def test_bundle_round_trip_is_deterministic(tmp_path: Path) -> None:
    events = _failed_events()
    manifest = build_trajectory_manifest(
        trajectory_id="trajectory-a018-round-trip",
        events=events,
        run_identity=_run_identity(),
        provenance=_provenance(),
        failure_terminal_class="FAILED_VALID",
        failure_classes=("TEST_FAILURE",),
    )
    path = tmp_path / "trajectory.json"

    record_trajectory_bundle(path, manifest=manifest, events=events)
    first_bytes = path.read_bytes()
    loaded_manifest, loaded_events = load_trajectory_bundle(path)
    record_trajectory_bundle(path, manifest=loaded_manifest, events=loaded_events)

    assert path.read_bytes() == first_bytes
    assert loaded_manifest == manifest
    assert loaded_events == events
