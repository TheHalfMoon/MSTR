from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.curriculum.frontier import (
    FixtureSamplingPolicy,
    FrontierCalibrationError,
    calibrate_fixture_frontier,
    canonical_frontier_json,
    deterministic_sampling_plan,
    refresh_fixture_frontier,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "curriculum" / "b021-frontier-refresh.json"


def _payload() -> dict[str, Any]:
    decoded = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def _policy(payload: dict[str, Any]) -> FixtureSamplingPolicy:
    raw = payload["policy"]
    assert isinstance(raw, dict)
    return FixtureSamplingPolicy(**raw)


def _entry(snapshot: Any, task_id: str) -> Any:
    return next(entry for entry in snapshot.entries if entry.task_or_family_id == task_id)


def test_fixture_frontier_maps_classes_and_preserves_replay_anchors() -> None:
    payload = _payload()
    snapshot = calibrate_fixture_frontier(payload["before_records"], policy=_policy(payload))

    assert snapshot.student_identity.checkpoint_id == "fixture-checkpoint-a"
    assert _entry(snapshot, "task-regression").curriculum_lane == "REPLAY_ANCHOR"
    assert _entry(snapshot, "task-regression").sampling_weight == 2
    assert _entry(snapshot, "task-fim").curriculum_lane == "REPLAY_ANCHOR"
    assert _entry(snapshot, "task-learnable").curriculum_lane == "PRIMARY_FRONTIER"
    assert _entry(snapshot, "task-learnable").sampling_weight == 5
    assert _entry(snapshot, "task-hard").curriculum_lane == "HARD_FRONTIER"
    assert _entry(snapshot, "task-hard").sampling_weight == 3
    assert _entry(snapshot, "task-unproductive").curriculum_lane == "DEFERRED"
    assert _entry(snapshot, "task-unproductive").sampling_weight == 0
    assert _entry(snapshot, "task-invalid").curriculum_lane == "REJECTED_INVALID"
    assert _entry(snapshot, "task-invalid").sampling_weight == 0


def test_sampling_plan_is_deterministic_weighted_and_excludes_rejected_cells() -> None:
    payload = _payload()
    snapshot = calibrate_fixture_frontier(payload["before_records"], policy=_policy(payload))

    first = deterministic_sampling_plan(snapshot, budget=24)
    second = deterministic_sampling_plan(snapshot, budget=24)
    assert first == second
    assert "task-unproductive" not in first
    assert "task-invalid" not in first

    counts = Counter(first)
    assert counts["task-learnable"] > counts["task-hard"]
    assert counts["task-hard"] > counts["task-regression"]
    assert counts["task-regression"] == counts["task-fim"]


def test_refresh_recalibrates_sampling_decisions_for_new_checkpoint() -> None:
    payload = _payload()
    refresh = refresh_fixture_frontier(
        payload["before_records"], payload["after_records"], policy=_policy(payload)
    )

    assert refresh.recalibration_required is True
    assert refresh.before_checkpoint_id == "fixture-checkpoint-a"
    assert refresh.after_checkpoint_id == "fixture-checkpoint-b"
    changes = {change.task_or_family_id: change for change in refresh.changes}
    assert changes["task-learnable"].before_lane == "PRIMARY_FRONTIER"
    assert changes["task-learnable"].after_lane == "STABILITY_REPLAY"
    assert changes["task-hard"].before_lane == "HARD_FRONTIER"
    assert changes["task-hard"].after_lane == "PRIMARY_FRONTIER"
    assert changes["task-unproductive"].before_lane == "DEFERRED"
    assert changes["task-unproductive"].after_lane == "HARD_FRONTIER"
    assert changes["task-invalid"].changed is False


def test_same_probability_can_route_by_frozen_class_without_threshold_encoding() -> None:
    payload = _payload()
    records = copy.deepcopy(payload["before_records"][:2])
    for index, (klass, task_id) in enumerate(
        (("LEARNABLE_FRONTIER", "same-p-learnable"), ("HARD_FRONTIER", "same-p-hard"))
    ):
        records[index]["task_or_family_id"] = task_id
        records[index]["difficulty_record_identity"] = f"same-p-{index}"
        records[index]["difficulty_class"] = klass
        records[index]["success_count"] = 5
        records[index]["estimated_solve_probability"] = 0.5
        records[index]["failure_distribution"] = [{"failure_class": "FIXTURE_FAILURE", "count": 5}]
        records[index]["structural_features"]["curriculum_role"] = "STANDARD"

    snapshot = calibrate_fixture_frontier(records, policy=_policy(payload))
    assert _entry(snapshot, "same-p-learnable").curriculum_lane == "PRIMARY_FRONTIER"
    assert _entry(snapshot, "same-p-hard").curriculum_lane == "HARD_FRONTIER"


def test_snapshot_rejects_mixed_checkpoint_identity() -> None:
    payload = _payload()
    records = copy.deepcopy(payload["before_records"][:2])
    records[1]["student_model_identity"]["checkpoint_id"] = "fixture-checkpoint-other"

    with pytest.raises(FrontierCalibrationError, match="one exact student/checkpoint"):
        calibrate_fixture_frontier(records, policy=_policy(payload))


def test_snapshot_rejects_non_fixture_source_class() -> None:
    payload = _payload()
    records = copy.deepcopy(payload["before_records"][:1])
    records[0]["structural_features"]["source_class"] = "PUBLIC_OPEN_SOURCE_REPOSITORY"

    with pytest.raises(FrontierCalibrationError, match="fixture-only"):
        calibrate_fixture_frontier(records, policy=_policy(payload))


def test_snapshot_rejects_unknown_curriculum_role() -> None:
    payload = _payload()
    records = copy.deepcopy(payload["before_records"][:1])
    records[0]["structural_features"]["curriculum_role"] = "MAGIC_ROLE"

    with pytest.raises(FrontierCalibrationError, match="unsupported curriculum_role"):
        calibrate_fixture_frontier(records, policy=_policy(payload))


def test_snapshot_rejects_duplicate_task_identity() -> None:
    payload = _payload()
    records = copy.deepcopy(payload["before_records"][:2])
    records[1]["task_or_family_id"] = records[0]["task_or_family_id"]

    with pytest.raises(FrontierCalibrationError, match="duplicate task_or_family_id"):
        calibrate_fixture_frontier(records, policy=_policy(payload))


def test_refresh_rejects_harness_or_sampling_change() -> None:
    payload = _payload()
    after = copy.deepcopy(payload["after_records"])
    for record in after:
        record["harness_profile_id"] = "fixture-harness-v2"
        record["student_model_identity"]["harness_profile_id"] = "fixture-harness-v2"

    with pytest.raises(FrontierCalibrationError, match="harness profile frozen"):
        refresh_fixture_frontier(payload["before_records"], after, policy=_policy(payload))


def test_refresh_rejects_stale_calibration_time_and_reused_record_identity() -> None:
    payload = _payload()
    after = copy.deepcopy(payload["after_records"])
    after[0]["calibration_time"] = "2026-08-28T23:59:59Z"
    with pytest.raises(FrontierCalibrationError, match="calibration_time must advance"):
        refresh_fixture_frontier(payload["before_records"], after, policy=_policy(payload))

    after = copy.deepcopy(payload["after_records"])
    after[0]["difficulty_record_identity"] = payload["before_records"][0][
        "difficulty_record_identity"
    ]
    with pytest.raises(FrontierCalibrationError, match="new difficulty record identity"):
        refresh_fixture_frontier(payload["before_records"], after, policy=_policy(payload))


def test_fixture_policy_has_no_implicit_defaults_and_fails_closed() -> None:
    with pytest.raises(FrontierCalibrationError, match="positive integer"):
        FixtureSamplingPolicy(
            policy_id="fixture-policy",
            stability_replay_weight=1,
            primary_frontier_weight=0,
            hard_frontier_weight=3,
            anchor_weight=2,
        )


def test_canonical_frontier_serialization_is_stable() -> None:
    payload = _payload()
    policy = _policy(payload)
    first = calibrate_fixture_frontier(payload["before_records"], policy=policy)
    second = calibrate_fixture_frontier(list(reversed(payload["before_records"])), policy=policy)
    assert canonical_frontier_json(first) == canonical_frontier_json(second)


def test_b021_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B021-frontier-sampler.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B021" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 641e13033b00451ea4b81063640e4066a8c7389d" in evidence
    assert "ENTRY_GATE_RUN = 33235627751" in evidence
    assert "ENTRY_GATE_JOB = 99055993292" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
