"""A004: deterministic AgentState projection and bounded compaction.

The append-oriented A003 event log remains authoritative. AgentState is a
reproducible working projection only: every retained item records the source
event sequence, uncertain hypotheses stay explicitly uncertain, and bounded
compaction fails closed instead of dropping safety-critical evidence.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass, replace
from typing import Any, Literal, cast

from mstr_qualify.harness.event_log import EventEntry, replay

EpistemicStatus = Literal["FACT", "UNCERTAIN"]
VerifierStatus = Literal["PASS", "FAIL", "ERROR", "UNKNOWN"]


class StateProjectionError(ValueError):
    """Fail-closed AgentState projection/compaction error."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class StateItem:
    """One event-derived state item with explicit epistemic status."""

    value: str
    source_seq: int
    epistemic_status: EpistemicStatus = "FACT"


@dataclass(frozen=True)
class VerifierResult:
    """Verifier observation retained separately from model hypotheses."""

    verifier_id: str
    status: VerifierStatus
    detail: str
    source_seq: int


@dataclass(frozen=True)
class FailureRecord:
    """Observed failure that compaction is never allowed to silently erase."""

    category: str
    detail: str
    source_seq: int


@dataclass(frozen=True)
class CompactionRecord:
    """Bounded audit summary for entries omitted from one state field."""

    field: str
    omitted_count: int
    omitted_sha256: str


@dataclass(frozen=True)
class CompactionPolicy:
    """Explicit bounded-state policy.

    Critical state is never truncated. If it exceeds ``max_critical_items``,
    compaction rejects the state rather than manufacturing a lossy summary.
    """

    max_context_items: int = 12
    max_command_items: int = 12
    max_pass_verifier_results: int = 6
    max_critical_items: int = 128

    def __post_init__(self) -> None:
        fields = (
            ("max_context_items", self.max_context_items),
            ("max_command_items", self.max_command_items),
            ("max_pass_verifier_results", self.max_pass_verifier_results),
            ("max_critical_items", self.max_critical_items),
        )
        for name, value in fields:
            if value < 0:
                raise StateProjectionError(
                    f"{name} must be non-negative",
                    code="state.invalid_compaction_policy",
                )


@dataclass(frozen=True)
class AgentState:
    """Derived working state through one exact event sequence."""

    run_id: str
    goal: StateItem | None
    acceptance_criteria: tuple[StateItem, ...]
    non_goals: tuple[StateItem, ...]
    constraints: tuple[StateItem, ...]
    current_plan: tuple[StateItem, ...]
    repo_map: tuple[StateItem, ...]
    files_inspected: tuple[StateItem, ...]
    changed_files: tuple[StateItem, ...]
    commands_run: tuple[StateItem, ...]
    verifier_results: tuple[VerifierResult, ...]
    known_failures: tuple[FailureRecord, ...]
    working_hypotheses: tuple[StateItem, ...]
    remaining_work: tuple[StateItem, ...]
    next_action: StateItem | None
    derived_through_seq: int
    compaction_records: tuple[CompactionRecord, ...] = ()


@dataclass
class _Builder:
    run_id: str
    goal: StateItem | None = None
    acceptance_criteria: list[StateItem] | None = None
    non_goals: list[StateItem] | None = None
    constraints: list[StateItem] | None = None
    current_plan: list[StateItem] | None = None
    repo_map: list[StateItem] | None = None
    files_inspected: list[StateItem] | None = None
    changed_files: list[StateItem] | None = None
    commands_run: list[StateItem] | None = None
    verifier_results: list[VerifierResult] | None = None
    known_failures: list[FailureRecord] | None = None
    working_hypotheses: list[StateItem] | None = None
    remaining_work: list[StateItem] | None = None
    next_action: StateItem | None = None

    def __post_init__(self) -> None:
        self.acceptance_criteria = []
        self.non_goals = []
        self.constraints = []
        self.current_plan = []
        self.repo_map = []
        self.files_inspected = []
        self.changed_files = []
        self.commands_run = []
        self.verifier_results = []
        self.known_failures = []
        self.working_hypotheses = []
        self.remaining_work = []


_SOURCE_POLICY: dict[str, frozenset[str]] = {
    "run.goal_admitted": frozenset({"user", "harness", "system"}),
    "context.observed": frozenset(
        {"user", "harness", "tool", "environment", "system"}
    ),
    "plan.updated": frozenset({"model", "harness", "system"}),
    "tool.result": frozenset({"tool", "harness", "environment", "system"}),
    "edit.applied": frozenset({"tool", "harness", "environment", "system"}),
    "edit.rejected": frozenset({"tool", "harness", "environment", "system"}),
    "verifier.result": frozenset({"verifier"}),
    "recovery.result": frozenset({"harness", "tool", "verifier", "system"}),
    "run.failed": frozenset({"harness", "verifier", "system"}),
    "run.escalated": frozenset({"harness", "verifier", "system"}),
}

_COMPACTABLE_FIELDS = frozenset(
    {"repo_map", "files_inspected", "commands_run", "verifier_results.pass"}
)


def _items(
    values: Sequence[str],
    seq: int,
    *,
    uncertain: bool = False,
) -> list[StateItem]:
    status: EpistemicStatus = "UNCERTAIN" if uncertain else "FACT"
    return [
        StateItem(value=value, source_seq=seq, epistemic_status=status)
        for value in values
    ]


def _string(payload: dict[str, Any], key: str, seq: int) -> str | None:
    if key not in payload or payload[key] is None:
        return None
    value = payload[key]
    if not isinstance(value, str) or not value.strip():
        raise StateProjectionError(
            f"event seq={seq} field {key!r} must be a non-empty string",
            code="state.payload_type_error",
        )
    return value


def _strings(payload: dict[str, Any], key: str, seq: int) -> list[str]:
    if key not in payload or payload[key] is None:
        return []
    value = payload[key]
    if isinstance(value, str):
        if not value.strip():
            raise StateProjectionError(
                f"event seq={seq} field {key!r} must not be empty",
                code="state.payload_type_error",
            )
        return [value]
    if not isinstance(value, list):
        raise StateProjectionError(
            f"event seq={seq} field {key!r} must be string or string list",
            code="state.payload_type_error",
        )
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise StateProjectionError(
            f"event seq={seq} field {key!r} contains an invalid item",
            code="state.payload_type_error",
        )
    return list(value)


def _bool(payload: dict[str, Any], key: str, seq: int) -> bool | None:
    if key not in payload:
        return None
    value = payload[key]
    if not isinstance(value, bool):
        raise StateProjectionError(
            f"event seq={seq} field {key!r} must be boolean",
            code="state.payload_type_error",
        )
    return value


def _require_source(raw: dict[str, Any]) -> None:
    event_type = raw["event_type"]
    allowed = _SOURCE_POLICY.get(event_type)
    if allowed is None:
        return
    source = raw["source"]
    if source not in allowed:
        raise StateProjectionError(
            f"event {event_type!r} from source {source!r} cannot author AgentState facts",
            code="state.source_not_authoritative",
        )


def _append_unique(target: list[StateItem], values: Sequence[StateItem]) -> None:
    existing = {item.value for item in target}
    for item in values:
        if item.value not in existing:
            target.append(item)
            existing.add(item.value)


def _required_list(builder: _Builder, name: str) -> list[Any]:
    value = getattr(builder, name)
    if value is None:
        raise AssertionError(f"internal builder list {name} was not initialized")
    return cast(list[Any], value)


def _record_failure(
    builder: _Builder,
    category: str,
    detail: str,
    seq: int,
) -> None:
    failures = _required_list(builder, "known_failures")
    failures.append(FailureRecord(category=category, detail=detail, source_seq=seq))


def _apply_goal(builder: _Builder, payload: dict[str, Any], seq: int) -> None:
    goal = _string(payload, "goal", seq)
    if goal is None:
        raise StateProjectionError(
            f"run.goal_admitted at seq={seq} requires goal",
            code="state.goal_missing",
        )
    candidate = StateItem(goal, seq)
    if builder.goal is not None and builder.goal.value != goal:
        raise StateProjectionError(
            "a run may not silently replace an admitted goal",
            code="state.goal_conflict",
        )
    builder.goal = candidate
    for field in ("acceptance_criteria", "non_goals", "constraints"):
        target = _required_list(builder, field)
        _append_unique(target, _items(_strings(payload, field, seq), seq))


def _apply_context(builder: _Builder, payload: dict[str, Any], seq: int) -> None:
    repo_values = _strings(payload, "repo_map", seq)
    repo_values.extend(_strings(payload, "repo_entries", seq))
    _append_unique(_required_list(builder, "repo_map"), _items(repo_values, seq))
    _append_unique(
        _required_list(builder, "files_inspected"),
        _items(_strings(payload, "files_inspected", seq), seq),
    )
    _append_unique(
        _required_list(builder, "working_hypotheses"),
        _items(_strings(payload, "hypotheses", seq), seq, uncertain=True),
    )


def _apply_plan(builder: _Builder, payload: dict[str, Any], seq: int) -> None:
    plan = _strings(payload, "plan", seq)
    if not plan:
        raise StateProjectionError(
            f"plan.updated at seq={seq} requires plan",
            code="state.plan_missing",
        )
    builder.current_plan = _items(plan, seq)
    if "remaining_work" in payload:
        builder.remaining_work = _items(
            _strings(payload, "remaining_work", seq),
            seq,
        )
    if "next_action" in payload:
        next_action = _string(payload, "next_action", seq)
        if next_action is None:
            builder.next_action = None
        else:
            builder.next_action = StateItem(next_action, seq)
    _append_unique(
        _required_list(builder, "working_hypotheses"),
        _items(_strings(payload, "hypotheses", seq), seq, uncertain=True),
    )


def _apply_tool_result(builder: _Builder, payload: dict[str, Any], seq: int) -> None:
    command = _string(payload, "command", seq)
    if command is not None:
        _required_list(builder, "commands_run").append(StateItem(command, seq))
    success = _bool(payload, "success", seq)
    if success is False:
        detail = (
            _string(payload, "error", seq)
            or _string(payload, "detail", seq)
            or "tool failed"
        )
        _record_failure(builder, "TOOL_ERROR", detail, seq)


def _apply_edit(
    builder: _Builder,
    event_type: str,
    payload: dict[str, Any],
    seq: int,
) -> None:
    if event_type == "edit.applied":
        paths = _strings(payload, "changed_files", seq)
        path = _string(payload, "path", seq)
        if path is not None:
            paths.append(path)
        if not paths:
            raise StateProjectionError(
                f"edit.applied at seq={seq} requires path or changed_files",
                code="state.changed_file_missing",
            )
        _append_unique(
            _required_list(builder, "changed_files"),
            _items(paths, seq),
        )
        return
    detail = (
        _string(payload, "reason", seq)
        or _string(payload, "error", seq)
        or "edit rejected"
    )
    _record_failure(builder, "BAD_PATCH", detail, seq)


def _apply_verifier(builder: _Builder, payload: dict[str, Any], seq: int) -> None:
    verifier_id = _string(payload, "verifier_id", seq)
    status_raw = _string(payload, "status", seq)
    if verifier_id is None or status_raw is None:
        raise StateProjectionError(
            f"verifier.result at seq={seq} requires verifier_id and status",
            code="state.verifier_result_incomplete",
        )
    if status_raw not in {"PASS", "FAIL", "ERROR", "UNKNOWN"}:
        raise StateProjectionError(
            f"verifier.result at seq={seq} has invalid status {status_raw!r}",
            code="state.verifier_status_invalid",
        )
    status = cast(VerifierStatus, status_raw)
    detail = _string(payload, "detail", seq) or ""
    results = _required_list(builder, "verifier_results")
    results.append(VerifierResult(verifier_id, status, detail, seq))
    if status != "PASS":
        suffix = f": {detail}" if detail else ""
        _record_failure(
            builder,
            "VERIFIER_FAILURE",
            f"{verifier_id}: {status}{suffix}",
            seq,
        )


def _apply_terminal_failure(
    builder: _Builder,
    event_type: str,
    payload: dict[str, Any],
    seq: int,
) -> None:
    detail = (
        _string(payload, "failure", seq)
        or _string(payload, "reason", seq)
        or _string(payload, "detail", seq)
        or event_type
    )
    if "authority" in detail.lower():
        category = "AUTHORITY_VIOLATION"
    else:
        category = "INCOMPLETE_IMPLEMENTATION"
    _record_failure(builder, category, detail, seq)


def _project_entries(log: Sequence[EventEntry]) -> AgentState:
    if not log:
        raise StateProjectionError(
            "AgentState requires at least one event",
            code="state.empty_log",
        )
    run_id = log[0].raw["run_id"]
    builder = _Builder(run_id=run_id)

    for entry in log:
        raw = entry.raw
        seq = raw["seq"]
        if raw["run_id"] != run_id:
            raise StateProjectionError(
                "mixed run ids are not projectable",
                code="state.mixed_run_ids",
            )
        payload = raw["payload"]
        if not isinstance(payload, dict):
            raise StateProjectionError(
                f"event seq={seq} payload must be an object",
                code="state.payload_type_error",
            )
        event_type = raw["event_type"]

        # A compaction event describes a model-visible summary. Reprojecting
        # facts from that summary would create a second, circular authority
        # surface. The original events remain sufficient to reconstruct state.
        if event_type == "context.compacted":
            continue

        _require_source(raw)
        if event_type == "run.goal_admitted":
            _apply_goal(builder, payload, seq)
        elif event_type == "context.observed":
            _apply_context(builder, payload, seq)
        elif event_type == "plan.updated":
            _apply_plan(builder, payload, seq)
        elif event_type == "tool.result":
            _apply_tool_result(builder, payload, seq)
        elif event_type in {"edit.applied", "edit.rejected"}:
            _apply_edit(builder, event_type, payload, seq)
        elif event_type == "verifier.result":
            _apply_verifier(builder, payload, seq)
        elif event_type in {"run.failed", "run.escalated"}:
            _apply_terminal_failure(builder, event_type, payload, seq)
        elif event_type == "recovery.result":
            if _bool(payload, "success", seq) is False:
                detail = _string(payload, "detail", seq) or "recovery failed"
                _record_failure(
                    builder,
                    "INCOMPLETE_IMPLEMENTATION",
                    detail,
                    seq,
                )

    return AgentState(
        run_id=run_id,
        goal=builder.goal,
        acceptance_criteria=tuple(_required_list(builder, "acceptance_criteria")),
        non_goals=tuple(_required_list(builder, "non_goals")),
        constraints=tuple(_required_list(builder, "constraints")),
        current_plan=tuple(_required_list(builder, "current_plan")),
        repo_map=tuple(_required_list(builder, "repo_map")),
        files_inspected=tuple(_required_list(builder, "files_inspected")),
        changed_files=tuple(_required_list(builder, "changed_files")),
        commands_run=tuple(_required_list(builder, "commands_run")),
        verifier_results=tuple(_required_list(builder, "verifier_results")),
        known_failures=tuple(_required_list(builder, "known_failures")),
        working_hypotheses=tuple(
            _required_list(builder, "working_hypotheses")
        ),
        remaining_work=tuple(_required_list(builder, "remaining_work")),
        next_action=builder.next_action,
        derived_through_seq=log[-1].raw["seq"],
    )


def project_agent_state(events: Sequence[dict[str, Any]]) -> AgentState:
    """Validate/replay ``events`` and deterministically derive AgentState."""
    return _project_entries(replay(list(events)))


def _canonical_digest(values: Sequence[Any]) -> str:
    serializable = [
        asdict(value) if hasattr(value, "__dataclass_fields__") else value
        for value in values
    ]
    payload = json.dumps(
        serializable,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _chain_digest(previous_sha256: str, next_sha256: str) -> str:
    """Deterministically bind one prior omission digest to a new omission digest."""
    payload = json.dumps(
        {"previous_sha256": previous_sha256, "next_sha256": next_sha256},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _merge_compaction_record(
    records: dict[str, CompactionRecord],
    record: CompactionRecord,
) -> None:
    """Keep exactly one cumulative audit record per compactable state field."""
    if record.field not in _COMPACTABLE_FIELDS:
        raise StateProjectionError(
            f"unsupported compaction record field {record.field!r}",
            code="state.invalid_compaction_record",
        )
    if record.omitted_count <= 0 or len(record.omitted_sha256) != 64:
        raise StateProjectionError(
            f"invalid compaction record for field {record.field!r}",
            code="state.invalid_compaction_record",
        )
    previous = records.get(record.field)
    if previous is None:
        records[record.field] = record
        return
    records[record.field] = CompactionRecord(
        field=record.field,
        omitted_count=previous.omitted_count + record.omitted_count,
        omitted_sha256=_chain_digest(
            previous.omitted_sha256,
            record.omitted_sha256,
        ),
    )


def _normalize_compaction_records(
    values: Sequence[CompactionRecord],
) -> dict[str, CompactionRecord]:
    """Validate and collapse historical records to the fixed field vocabulary."""
    records: dict[str, CompactionRecord] = {}
    for record in values:
        _merge_compaction_record(records, record)
    return records


def _compact_sequence(
    field: str,
    values: tuple[Any, ...],
    limit: int,
) -> tuple[tuple[Any, ...], CompactionRecord | None]:
    if len(values) <= limit:
        return values, None
    omitted = values[: len(values) - limit] if limit else values
    kept = values[-limit:] if limit else ()
    record = CompactionRecord(
        field=field,
        omitted_count=len(omitted),
        omitted_sha256=_canonical_digest(omitted),
    )
    return kept, record


def _critical_count(state: AgentState) -> int:
    nonpass_verifiers = sum(
        result.status != "PASS" for result in state.verifier_results
    )
    scalar_count = int(state.goal is not None) + int(state.next_action is not None)
    groups = (
        len(state.acceptance_criteria),
        len(state.non_goals),
        len(state.constraints),
        len(state.current_plan),
        len(state.changed_files),
        nonpass_verifiers,
        len(state.known_failures),
        len(state.working_hypotheses),
        len(state.remaining_work),
    )
    return scalar_count + sum(groups)


def compact_agent_state(
    state: AgentState,
    policy: CompactionPolicy | None = None,
) -> AgentState:
    """Bound non-critical history without erasing decision-critical evidence.

    Goal/acceptance/constraints/current plan/changed files/all verifier failures,
    known failures, uncertain hypotheses, remaining work and next action are
    critical. If those cannot fit the declared critical budget, compaction
    fails closed instead of truncating them.

    Compaction metadata is itself bounded: at most one cumulative audit record
    exists for each compactable field, regardless of repeated compaction.
    """
    active_policy = policy or CompactionPolicy()
    critical_count = _critical_count(state)
    if critical_count > active_policy.max_critical_items:
        raise StateProjectionError(
            "critical AgentState exceeds compaction budget; refusing lossy compaction",
            code="state.critical_overflow",
        )

    records = _normalize_compaction_records(state.compaction_records)
    repo_map, record = _compact_sequence(
        "repo_map",
        state.repo_map,
        active_policy.max_context_items,
    )
    if record is not None:
        _merge_compaction_record(records, record)
    files_inspected, record = _compact_sequence(
        "files_inspected",
        state.files_inspected,
        active_policy.max_context_items,
    )
    if record is not None:
        _merge_compaction_record(records, record)
    commands_run, record = _compact_sequence(
        "commands_run",
        state.commands_run,
        active_policy.max_command_items,
    )
    if record is not None:
        _merge_compaction_record(records, record)

    pass_results = [
        result for result in state.verifier_results if result.status == "PASS"
    ]
    limit = active_policy.max_pass_verifier_results
    kept_passes = pass_results[-limit:] if limit else []
    omitted_passes = pass_results[: len(pass_results) - len(kept_passes)]
    if omitted_passes:
        _merge_compaction_record(
            records,
            CompactionRecord(
                field="verifier_results.pass",
                omitted_count=len(omitted_passes),
                omitted_sha256=_canonical_digest(omitted_passes),
            ),
        )
    nonpass = [
        result for result in state.verifier_results if result.status != "PASS"
    ]
    verifier_results = tuple(
        sorted((*nonpass, *kept_passes), key=lambda result: result.source_seq)
    )

    return replace(
        state,
        repo_map=repo_map,
        files_inspected=files_inspected,
        commands_run=commands_run,
        verifier_results=verifier_results,
        compaction_records=tuple(records[field] for field in sorted(records)),
    )


def state_to_dict(state: AgentState) -> dict[str, Any]:
    """Return deterministic JSON-compatible state data for model/harness use."""
    return asdict(state)
