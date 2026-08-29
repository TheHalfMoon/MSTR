"""Deterministic fixture-only frontier calibration and sampling for B021.

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
        checkpoint_id=_string(student.get("checkpoint_id"), "student_model_identity.checkpoint_id"),
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
                "one frontier snapshot must bind one exact "
                "student/checkpoint/harness/sampling identity"
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
    return FrontierSnapshot(
        policy_id=policy.policy_id, student_identity=identity, entries=tuple(entries)
    )


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
