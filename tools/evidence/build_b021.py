from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()

FILES: dict[str, str] = {}

FILES["src/mstr_qualify/curriculum/__init__.py"] = '''"""Fixture-only curriculum utilities for MSTR qualification evidence."""

from .frontier import (
    CurriculumRole,
    FixtureSamplingPolicy,
    FrontierCalibrationError,
    FrontierEntry,
    FrontierRefresh,
    FrontierSnapshot,
    StudentIdentity,
    calibrate_fixture_frontier,
    canonical_frontier_json,
    deterministic_sampling_plan,
    refresh_fixture_frontier,
)

__all__ = [
    "CurriculumRole",
    "FixtureSamplingPolicy",
    "FrontierCalibrationError",
    "FrontierEntry",
    "FrontierRefresh",
    "FrontierSnapshot",
    "StudentIdentity",
    "calibrate_fixture_frontier",
    "canonical_frontier_json",
    "deterministic_sampling_plan",
    "refresh_fixture_frontier",
]
'''

FILES["src/mstr_qualify/curriculum/frontier.py"] = '''"""Deterministic fixture-only frontier calibration and sampling for B021.

B021 consumes validated B020 difficulty records. It intentionally does not
infer a universal difficulty class from solve probability: the record's frozen
class remains authoritative for this fixture pilot. The policy here only maps
those already-calibrated classes into explicit curriculum lanes and weights.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, cast

from ..schemas import validate_instance

DifficultyClass = Literal[
    "TOO_EASY",
    "LEARNABLE_FRONTIER",
    "HARD_FRONTIER",
    "CURRENTLY_UNPRODUCTIVE",
    "INVALID",
]
CurriculumRole = Literal[
    "STANDARD",
    "REGRESSION_ANCHOR",
    "CORE_FIM_REPLAY",
    "CORE_DIRECT_CODE_REPLAY",
]
CurriculumLane = Literal[
    "REPLAY_ANCHOR",
    "STABILITY_REPLAY",
    "PRIMARY_FRONTIER",
    "HARD_FRONTIER",
    "DEFERRED",
    "REJECTED_INVALID",
]

_ALLOWED_FIXTURE_SOURCES = {"REPOSITORY_OWNED_FIXTURE", "SYNTHETIC_VERIFIED"}
_ALLOWED_ROLES = {
    "STANDARD",
    "REGRESSION_ANCHOR",
    "CORE_FIM_REPLAY",
    "CORE_DIRECT_CODE_REPLAY",
}
_ANCHOR_ROLES = {"REGRESSION_ANCHOR", "CORE_FIM_REPLAY", "CORE_DIRECT_CODE_REPLAY"}


class FrontierCalibrationError(ValueError):
    """Raised when fixture frontier evidence is ambiguous or unsafe."""


@dataclass(frozen=True)
class StudentIdentity:
    model_id: str
    checkpoint_id: str
    harness_profile_id: str
    sampling_identity: str

    def as_dict(self) -> dict[str, str]:
        return {
            "model_id": self.model_id,
            "checkpoint_id": self.checkpoint_id,
            "harness_profile_id": self.harness_profile_id,
            "sampling_identity": self.sampling_identity,
        }


@dataclass(frozen=True)
class FixtureSamplingPolicy:
    """Explicit fixture policy; no production or universal default is encoded."""

    policy_id: str
    stability_replay_weight: int
    primary_frontier_weight: int
    hard_frontier_weight: int
    anchor_weight: int

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise FrontierCalibrationError("policy_id must be non-empty")
        for name in (
            "stability_replay_weight",
            "primary_frontier_weight",
            "hard_frontier_weight",
            "anchor_weight",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise FrontierCalibrationError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class FrontierEntry:
    task_or_family_id: str
    difficulty_record_identity: str
    difficulty_class: DifficultyClass
    curriculum_role: CurriculumRole
    curriculum_lane: CurriculumLane
    sampling_weight: int
    calibration_time: str

    def as_dict(self) -> dict[str, object]:
        return {
            "task_or_family_id": self.task_or_family_id,
            "difficulty_record_identity": self.difficulty_record_identity,
            "difficulty_class": self.difficulty_class,
            "curriculum_role": self.curriculum_role,
            "curriculum_lane": self.curriculum_lane,
            "sampling_weight": self.sampling_weight,
            "calibration_time": self.calibration_time,
        }


@dataclass(frozen=True)
class FrontierSnapshot:
    policy_id: str
    student_identity: StudentIdentity
    entries: tuple[FrontierEntry, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "snapshot_version": "mstr.fixture-frontier-snapshot.v0",
            "policy_id": self.policy_id,
            "student_identity": self.student_identity.as_dict(),
            "entries": [entry.as_dict() for entry in self.entries],
        }


@dataclass(frozen=True)
class FrontierRefreshChange:
    task_or_family_id: str
    before_record_identity: str
    after_record_identity: str
    before_class: DifficultyClass
    after_class: DifficultyClass
    before_lane: CurriculumLane
    after_lane: CurriculumLane
    before_weight: int
    after_weight: int

    @property
    def changed(self) -> bool:
        return (
            self.before_class != self.after_class
            or self.before_lane != self.after_lane
            or self.before_weight != self.after_weight
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "task_or_family_id": self.task_or_family_id,
            "before_record_identity": self.before_record_identity,
            "after_record_identity": self.after_record_identity,
            "before_class": self.before_class,
            "after_class": self.after_class,
            "before_lane": self.before_lane,
            "after_lane": self.after_lane,
            "before_weight": self.before_weight,
            "after_weight": self.after_weight,
            "changed": self.changed,
        }


@dataclass(frozen=True)
class FrontierRefresh:
    policy_id: str
    model_id: str
    harness_profile_id: str
    sampling_identity: str
    before_checkpoint_id: str
    after_checkpoint_id: str
    recalibration_required: bool
    changes: tuple[FrontierRefreshChange, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "refresh_version": "mstr.fixture-frontier-refresh.v0",
            "policy_id": self.policy_id,
            "model_id": self.model_id,
            "harness_profile_id": self.harness_profile_id,
            "sampling_identity": self.sampling_identity,
            "before_checkpoint_id": self.before_checkpoint_id,
            "after_checkpoint_id": self.after_checkpoint_id,
            "recalibration_required": self.recalibration_required,
            "changes": [change.as_dict() for change in self.changes],
        }


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise FrontierCalibrationError(f"{label} must be an object")
    return cast(dict[str, Any], value)


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise FrontierCalibrationError(f"{label} must be a non-empty string")
    return value


def _student_identity(record: Mapping[str, Any]) -> StudentIdentity:
    student = _object(record["student_model_identity"], "student_model_identity")
    return StudentIdentity(
        model_id=_string(student.get("model_id"), "student_model_identity.model_id"),
        checkpoint_id=_string(
            student.get("checkpoint_id"), "student_model_identity.checkpoint_id"
        ),
        harness_profile_id=_string(
            student.get("harness_profile_id"), "student_model_identity.harness_profile_id"
        ),
        sampling_identity=_string(
            student.get("sampling_identity"), "student_model_identity.sampling_identity"
        ),
    )


def _role_and_source(record: Mapping[str, Any]) -> tuple[CurriculumRole, str]:
    features = _object(record["structural_features"], "structural_features")
    source_class = _string(features.get("source_class"), "structural_features.source_class")
    if source_class not in _ALLOWED_FIXTURE_SOURCES:
        raise FrontierCalibrationError(
            f"B021 is fixture-only; unsupported source_class: {source_class}"
        )
    raw_role = features.get("curriculum_role", "STANDARD")
    role = _string(raw_role, "structural_features.curriculum_role")
    if role not in _ALLOWED_ROLES:
        raise FrontierCalibrationError(f"unsupported curriculum_role: {role}")
    return cast(CurriculumRole, role), source_class


def _lane_and_weight(
    difficulty_class: DifficultyClass,
    role: CurriculumRole,
    policy: FixtureSamplingPolicy,
) -> tuple[CurriculumLane, int]:
    if difficulty_class == "INVALID":
        return "REJECTED_INVALID", 0
    if difficulty_class == "CURRENTLY_UNPRODUCTIVE":
        return "DEFERRED", 0
    if role in _ANCHOR_ROLES:
        return "REPLAY_ANCHOR", policy.anchor_weight
    if difficulty_class == "TOO_EASY":
        return "STABILITY_REPLAY", policy.stability_replay_weight
    if difficulty_class == "LEARNABLE_FRONTIER":
        return "PRIMARY_FRONTIER", policy.primary_frontier_weight
    if difficulty_class == "HARD_FRONTIER":
        return "HARD_FRONTIER", policy.hard_frontier_weight
    raise FrontierCalibrationError(f"unsupported difficulty_class: {difficulty_class}")


def calibrate_fixture_frontier(
    records: Sequence[Mapping[str, Any]], *, policy: FixtureSamplingPolicy
) -> FrontierSnapshot:
    """Map one exact B020 checkpoint calibration into a fixture curriculum snapshot."""

    if not records:
        raise FrontierCalibrationError("frontier calibration requires at least one record")

    identity: StudentIdentity | None = None
    entries: list[FrontierEntry] = []
    task_ids: set[str] = set()
    record_ids: set[str] = set()

    for record in records:
        materialized = dict(record)
        validate_instance("mstr-difficulty-calibration-v0", materialized)
        current_identity = _student_identity(materialized)
        if identity is None:
            identity = current_identity
        elif current_identity != identity:
            raise FrontierCalibrationError(
                "one frontier snapshot must bind one exact student/checkpoint/harness/sampling identity"
            )

        task_id = _string(materialized["task_or_family_id"], "task_or_family_id")
        record_id = _string(
            materialized["difficulty_record_identity"], "difficulty_record_identity"
        )
        if task_id in task_ids:
            raise FrontierCalibrationError(f"duplicate task_or_family_id: {task_id}")
        if record_id in record_ids:
            raise FrontierCalibrationError(f"duplicate difficulty_record_identity: {record_id}")
        task_ids.add(task_id)
        record_ids.add(record_id)

        role, _source_class = _role_and_source(materialized)
        raw_class = _string(materialized["difficulty_class"], "difficulty_class")
        difficulty_class = cast(DifficultyClass, raw_class)
        lane, weight = _lane_and_weight(difficulty_class, role, policy)
        entries.append(
            FrontierEntry(
                task_or_family_id=task_id,
                difficulty_record_identity=record_id,
                difficulty_class=difficulty_class,
                curriculum_role=role,
                curriculum_lane=lane,
                sampling_weight=weight,
                calibration_time=_string(materialized["calibration_time"], "calibration_time"),
            )
        )

    if identity is None:  # pragma: no cover - guarded by the non-empty check above.
        raise FrontierCalibrationError("frontier identity could not be resolved")
    entries.sort(key=lambda entry: entry.task_or_family_id)
    return FrontierSnapshot(policy_id=policy.policy_id, student_identity=identity, entries=tuple(entries))


def deterministic_sampling_plan(snapshot: FrontierSnapshot, *, budget: int) -> tuple[str, ...]:
    """Return a deterministic smooth-weighted fixture schedule for eligible entries."""

    if not isinstance(budget, int) or isinstance(budget, bool) or budget <= 0:
        raise FrontierCalibrationError("budget must be a positive integer")
    eligible = tuple(entry for entry in snapshot.entries if entry.sampling_weight > 0)
    if not eligible:
        raise FrontierCalibrationError("frontier snapshot has no sampleable entries")

    scores = {entry.task_or_family_id: 0 for entry in eligible}
    weights = {entry.task_or_family_id: entry.sampling_weight for entry in eligible}
    total_weight = sum(weights.values())
    plan: list[str] = []

    for _ in range(budget):
        for task_id, weight in weights.items():
            scores[task_id] += weight
        selected = min(scores, key=lambda task_id: (-scores[task_id], task_id))
        plan.append(selected)
        scores[selected] -= total_weight

    return tuple(plan)


def refresh_fixture_frontier(
    before_records: Sequence[Mapping[str, Any]],
    after_records: Sequence[Mapping[str, Any]],
    *,
    policy: FixtureSamplingPolicy,
) -> FrontierRefresh:
    """Compare two fixture checkpoint snapshots and expose refreshable decisions."""

    before = calibrate_fixture_frontier(before_records, policy=policy)
    after = calibrate_fixture_frontier(after_records, policy=policy)
    before_id = before.student_identity
    after_id = after.student_identity

    if before_id.model_id != after_id.model_id:
        raise FrontierCalibrationError("frontier refresh must keep the same student model_id")
    if before_id.harness_profile_id != after_id.harness_profile_id:
        raise FrontierCalibrationError("frontier refresh must keep the harness profile frozen")
    if before_id.sampling_identity != after_id.sampling_identity:
        raise FrontierCalibrationError("frontier refresh must keep the sampling identity frozen")
    if before_id.checkpoint_id == after_id.checkpoint_id:
        raise FrontierCalibrationError("frontier refresh requires a new checkpoint identity")

    before_by_task = {entry.task_or_family_id: entry for entry in before.entries}
    after_by_task = {entry.task_or_family_id: entry for entry in after.entries}
    if before_by_task.keys() != after_by_task.keys():
        raise FrontierCalibrationError("fixture refresh requires the same task/family set")

    changes: list[FrontierRefreshChange] = []
    for task_id in sorted(before_by_task):
        before_entry = before_by_task[task_id]
        after_entry = after_by_task[task_id]
        if after_entry.difficulty_record_identity == before_entry.difficulty_record_identity:
            raise FrontierCalibrationError(
                f"refresh must bind a new difficulty record identity for {task_id}"
            )
        if after_entry.calibration_time <= before_entry.calibration_time:
            raise FrontierCalibrationError(f"refresh calibration_time must advance for {task_id}")
        if after_entry.curriculum_role != before_entry.curriculum_role:
            raise FrontierCalibrationError(f"curriculum_role changed during refresh for {task_id}")
        changes.append(
            FrontierRefreshChange(
                task_or_family_id=task_id,
                before_record_identity=before_entry.difficulty_record_identity,
                after_record_identity=after_entry.difficulty_record_identity,
                before_class=before_entry.difficulty_class,
                after_class=after_entry.difficulty_class,
                before_lane=before_entry.curriculum_lane,
                after_lane=after_entry.curriculum_lane,
                before_weight=before_entry.sampling_weight,
                after_weight=after_entry.sampling_weight,
            )
        )

    return FrontierRefresh(
        policy_id=policy.policy_id,
        model_id=before_id.model_id,
        harness_profile_id=before_id.harness_profile_id,
        sampling_identity=before_id.sampling_identity,
        before_checkpoint_id=before_id.checkpoint_id,
        after_checkpoint_id=after_id.checkpoint_id,
        recalibration_required=True,
        changes=tuple(changes),
    )


def canonical_frontier_json(value: FrontierSnapshot | FrontierRefresh) -> str:
    """Serialize B021 fixture evidence with stable key ordering."""

    return json.dumps(value.as_dict(), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
'''

fixture = {
    "policy": {
        "policy_id": "fixture-frontier-policy-v1",
        "stability_replay_weight": 1,
        "primary_frontier_weight": 5,
        "hard_frontier_weight": 3,
        "anchor_weight": 2,
    },
    "before_records": [],
    "after_records": [],
}


def record(
    *,
    checkpoint: str,
    suffix: str,
    task_id: str,
    difficulty_class: str,
    success_count: int,
    role: str,
    time: str,
) -> dict[str, object]:
    attempt_count = 10
    failed = attempt_count - success_count
    return {
        "schema_version": "mstr.difficulty-calibration.v0",
        "difficulty_record_identity": f"fixture-difficulty-{suffix}",
        "task_or_family_id": task_id,
        "student_model_identity": {
            "model_id": "fixture/student-model",
            "checkpoint_id": checkpoint,
            "harness_profile_id": "fixture-harness-v1",
            "sampling_identity": "fixture-sampling-v1",
        },
        "harness_profile_id": "fixture-harness-v1",
        "sampling_identity": "fixture-sampling-v1",
        "attempt_count": attempt_count,
        "success_count": success_count,
        "estimated_solve_probability": success_count / attempt_count,
        "structural_features": {
            "source_class": "REPOSITORY_OWNED_FIXTURE",
            "curriculum_role": role,
            "complexity_band": "fixture-band",
        },
        "failure_distribution": (
            [] if failed == 0 else [{"failure_class": "FIXTURE_FAILURE", "count": failed}]
        ),
        "difficulty_class": difficulty_class,
        "calibration_time": time,
    }


before_specs = [
    ("regression", "task-regression", "TOO_EASY", 9, "REGRESSION_ANCHOR"),
    ("fim", "task-fim", "TOO_EASY", 8, "CORE_FIM_REPLAY"),
    ("learnable", "task-learnable", "LEARNABLE_FRONTIER", 5, "STANDARD"),
    ("hard", "task-hard", "HARD_FRONTIER", 2, "STANDARD"),
    ("unproductive", "task-unproductive", "CURRENTLY_UNPRODUCTIVE", 0, "STANDARD"),
    ("invalid", "task-invalid", "INVALID", 5, "STANDARD"),
]
after_specs = [
    ("regression", "task-regression", "TOO_EASY", 10, "REGRESSION_ANCHOR"),
    ("fim", "task-fim", "TOO_EASY", 9, "CORE_FIM_REPLAY"),
    ("learnable", "task-learnable", "TOO_EASY", 9, "STANDARD"),
    ("hard", "task-hard", "LEARNABLE_FRONTIER", 5, "STANDARD"),
    ("unproductive", "task-unproductive", "HARD_FRONTIER", 2, "STANDARD"),
    ("invalid", "task-invalid", "INVALID", 5, "STANDARD"),
]
for suffix, task_id, klass, successes, role in before_specs:
    fixture["before_records"].append(
        record(
            checkpoint="fixture-checkpoint-a",
            suffix=f"a-{suffix}",
            task_id=task_id,
            difficulty_class=klass,
            success_count=successes,
            role=role,
            time="2026-08-29T00:00:00Z",
        )
    )
for suffix, task_id, klass, successes, role in after_specs:
    fixture["after_records"].append(
        record(
            checkpoint="fixture-checkpoint-b",
            suffix=f"b-{suffix}",
            task_id=task_id,
            difficulty_class=klass,
            success_count=successes,
            role=role,
            time="2026-08-29T01:00:00Z",
        )
    )
FILES["tests/fixtures/curriculum/b021-frontier-refresh.json"] = json.dumps(
    fixture, indent=2, sort_keys=True
) + "\n"

FILES["tests/unit/test_frontier_curriculum.py"] = '''from __future__ import annotations

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
        records[index]["failure_distribution"] = [
            {"failure_class": "FIXTURE_FAILURE", "count": 5}
        ]
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
        refresh_fixture_frontier(
            payload["before_records"], after, policy=_policy(payload)
        )


def test_refresh_rejects_stale_calibration_time_and_reused_record_identity() -> None:
    payload = _payload()
    after = copy.deepcopy(payload["after_records"])
    after[0]["calibration_time"] = "2026-08-28T23:59:59Z"
    with pytest.raises(FrontierCalibrationError, match="calibration_time must advance"):
        refresh_fixture_frontier(
            payload["before_records"], after, policy=_policy(payload)
        )

    after = copy.deepcopy(payload["after_records"])
    after[0]["difficulty_record_identity"] = payload["before_records"][0][
        "difficulty_record_identity"
    ]
    with pytest.raises(FrontierCalibrationError, match="new difficulty record identity"):
        refresh_fixture_frontier(
            payload["before_records"], after, policy=_policy(payload)
        )


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
    second = calibrate_fixture_frontier(
        list(reversed(payload["before_records"])), policy=policy
    )
    assert canonical_frontier_json(first) == canonical_frontier_json(second)


def test_b021_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B021-frontier-sampler.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B021" in evidence
    assert (
        "ENTRY_GATE_CANONICAL_MAIN = "
        "641e13033b00451ea4b81063640e4066a8c7389d" in evidence
    )
    assert "ENTRY_GATE_RUN = 33235627751" in evidence
    assert "ENTRY_GATE_JOB = 99055993292" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
'''

FILES["evidence/mstr-000b/B021-frontier-sampler.md"] = '''# B021 — Fixture-Only Frontier Sampler/Calibrator Evidence

**Task:** `B021`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `641e13033b00451ea4b81063640e4066a8c7389d`

## Canonical Entry Provenance

```text
ENTRY_GATE_TASK = B021
ENTRY_GATE_CANONICAL_MAIN = 641e13033b00451ea4b81063640e4066a8c7389d
ENTRY_GATE_RUN = 33235627751
ENTRY_GATE_JOB = 99055993292
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

The entry gate proved B020 terminal `COMPLETE_CANONICAL`, B021 `PENDING` and `eligible=true` with no external authority required, canonical drift clean across all 34 MSTR-000B tasks, B011 still blocked, and the canonical baseline quality gates green.

## Fixture Frontier Semantics

B021 consumes records validated against `mstr.difficulty-calibration.v0`. It does not replace the B020 contract and it does not infer a universal difficulty class from solve probability.

The fixture sampler maps the already-calibrated classes into explicit curriculum lanes:

```text
INVALID                 -> REJECTED_INVALID / weight 0
CURRENTLY_UNPRODUCTIVE   -> DEFERRED / weight 0
TOO_EASY                 -> STABILITY_REPLAY
LEARNABLE_FRONTIER       -> PRIMARY_FRONTIER
HARD_FRONTIER            -> HARD_FRONTIER
```

Repository-owned regression, core FIM, and core direct-code anchors remain explicit replay anchors when otherwise sampleable. Sampling weights are provided by an explicit `FixtureSamplingPolicy`; the implementation encodes no default weights and no probability-to-class thresholds.

The deterministic sampler uses smooth weighted scheduling only over entries with positive fixture weights. `INVALID` and deferred currently-unproductive cells cannot enter its plan.

## Checkpoint Refresh Proof

The repository fixture contains the same task/family set at two synthetic checkpoint identities under the same frozen harness and sampling identity. Refresh requires:

- a new checkpoint identity;
- new difficulty-record identities;
- advancing calibration times;
- the same model, harness, sampling identity, task/family set, and curriculum roles.

The fixture demonstrates tasks moving from learnable frontier to replay, hard frontier to learnable frontier, and currently-unproductive to hard frontier after the synthetic checkpoint changes. This is a contract/policy demonstration only; no student model is executed.

A regression test also assigns the same `estimated_solve_probability=0.5` to two records with different frozen B020 classes and proves they route to different lanes. This prevents B021 from silently hard-coding a universal probability threshold that B020 deliberately left unfrozen.

## Fixture Boundary

Accepted source classes are restricted to:

```text
REPOSITORY_OWNED_FIXTURE
SYNTHETIC_VERIFIED
```

The pilot does not read a public repository, external dataset, model artifact, teacher service, production trace, private user data, or network model endpoint.

## Authority

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
REAL_CHECKPOINT_CALIBRATION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B021_AUTHORITY = REPOSITORY_OWNED_FIXTURE_FRONTIER_CALIBRATION_AND_SAMPLING_ONLY
```
'''

for relative, content in FILES.items():
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")

print("B021_MATERIALIZED_FILES=" + str(len(FILES)))
for relative in sorted(FILES):
    print(relative)
