"""A004 tests for deterministic AgentState projection and bounded compaction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.harness.event_log import EventLogError, create_event
from mstr_qualify.state import (
    CompactionPolicy,
    StateProjectionError,
    compact_agent_state,
    project_agent_state,
    state_to_dict,
)

FIXTURE = Path("tests/fixtures/harness/a004-adversarial-state.json")


def _events_from_specs(run_id: str, specs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    previous: str | None = None
    for seq, spec in enumerate(specs):
        event_type = spec["event_type"]
        source = "harness"
        if event_type == "verifier.result":
            source = "verifier"
        elif event_type.startswith("tool."):
            source = "tool"
        event = create_event(
            run_id,
            seq,
            event_type,
            seq,
            spec["payload"],
            source=source,
            prev_sha256=previous,
        )
        events.append(event)
        previous = event["sha256"]
    return events


def _fixture_events() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return _events_from_specs(payload["run_id"], payload["events"]), payload


def _simple_events(*specs: dict[str, Any]) -> list[dict[str, Any]]:
    return _events_from_specs("a004-test", list(specs))


def test_projection_derives_required_working_state() -> None:
    events, fixture = _fixture_events()
    state = project_agent_state(events)

    assert state.run_id == fixture["run_id"]
    assert state.goal is not None
    assert state.goal.value == "Implement the bounded cache fix"
    assert [item.value for item in state.acceptance_criteria] == [
        "tests pass",
        "cache invalidates stale entries",
    ]
    assert [item.value for item in state.changed_files] == fixture["must_preserve"][
        "changed_files"
    ]
    assert [item.value for item in state.remaining_work] == ["run full regression"]
    assert state.next_action is not None
    assert state.next_action.value == "run full regression"
    assert state.derived_through_seq == len(events) - 1


def test_hypotheses_never_become_facts_or_verifier_passes() -> None:
    events, _ = _fixture_events()
    state = project_agent_state(events)

    assert state.working_hypotheses
    assert all(item.epistemic_status == "UNCERTAIN" for item in state.working_hypotheses)
    hypothesis_text = " ".join(item.value for item in state.working_hypotheses)
    assert "expected to pass" in hypothesis_text
    assert not any(result.detail == hypothesis_text for result in state.verifier_results)


def test_compaction_preserves_failures_changes_uncertainty_and_remaining_work() -> None:
    events, fixture = _fixture_events()
    state = project_agent_state(events)
    compacted = compact_agent_state(
        state,
        CompactionPolicy(
            max_context_items=2,
            max_command_items=1,
            max_pass_verifier_results=1,
            max_critical_items=64,
        ),
    )

    assert [item.value for item in compacted.changed_files] == fixture["must_preserve"][
        "changed_files"
    ]
    assert any(result.status == "FAIL" for result in compacted.verifier_results)
    assert sum(result.status == "PASS" for result in compacted.verifier_results) == 1
    failure_text = " ".join(item.detail for item in compacted.known_failures)
    for expected in fixture["must_preserve"]["failure_substrings"]:
        assert expected in failure_text
    hypothesis_text = " ".join(item.value for item in compacted.working_hypotheses)
    for expected in fixture["must_preserve"]["uncertain_substrings"]:
        assert expected in hypothesis_text
    assert [item.value for item in compacted.remaining_work] == fixture["must_preserve"][
        "remaining_work"
    ]


def test_compaction_records_auditable_digests_for_omitted_noncritical_history() -> None:
    events, _ = _fixture_events()
    state = project_agent_state(events)
    policy = CompactionPolicy(
        max_context_items=2,
        max_command_items=0,
        max_pass_verifier_results=1,
        max_critical_items=64,
    )

    first = compact_agent_state(state, policy)
    second = compact_agent_state(state, policy)

    assert state_to_dict(first) == state_to_dict(second)
    records = {record.field: record for record in first.compaction_records}
    assert records["repo_map"].omitted_count > 0
    assert records["files_inspected"].omitted_count > 0
    assert records["commands_run"].omitted_count > 0
    assert records["verifier_results.pass"].omitted_count == 2
    assert all(len(record.omitted_sha256) == 64 for record in records.values())


def test_compaction_fails_closed_when_critical_state_exceeds_budget() -> None:
    events, _ = _fixture_events()
    state = project_agent_state(events)

    with pytest.raises(StateProjectionError) as exc:
        compact_agent_state(state, CompactionPolicy(max_critical_items=1))

    assert exc.value.code == "state.critical_overflow"


def test_projection_rejects_conflicting_goal() -> None:
    events = _simple_events(
        {"event_type": "run.started", "payload": {}},
        {"event_type": "run.goal_admitted", "payload": {"goal": "first"}},
        {"event_type": "run.goal_admitted", "payload": {"goal": "second"}},
    )

    with pytest.raises(StateProjectionError) as exc:
        project_agent_state(events)

    assert exc.value.code == "state.goal_conflict"


def test_projection_rejects_plan_event_without_plan() -> None:
    events = _simple_events(
        {"event_type": "run.started", "payload": {}},
        {"event_type": "plan.updated", "payload": {"remaining_work": ["work"]}},
    )

    with pytest.raises(StateProjectionError) as exc:
        project_agent_state(events)

    assert exc.value.code == "state.plan_missing"


def test_projection_rejects_malformed_known_projection_field() -> None:
    events = _simple_events(
        {"event_type": "run.started", "payload": {}},
        {"event_type": "context.observed", "payload": {"files_inspected": ["ok", 7]}},
    )

    with pytest.raises(StateProjectionError) as exc:
        project_agent_state(events)

    assert exc.value.code == "state.payload_type_error"


def test_projection_replays_and_rejects_tampered_event_chain() -> None:
    events, _ = _fixture_events()
    events[4]["payload"]["command"] = "tampered-command"

    with pytest.raises(EventLogError, match="hash mismatch"):
        project_agent_state(events)


def test_verifier_failure_survives_later_pass_from_same_verifier() -> None:
    events = _simple_events(
        {"event_type": "run.started", "payload": {}},
        {
            "event_type": "verifier.result",
            "payload": {"verifier_id": "tests", "status": "FAIL", "detail": "regression"},
        },
        {
            "event_type": "verifier.result",
            "payload": {"verifier_id": "tests", "status": "PASS", "detail": "repaired"},
        },
    )
    state = compact_agent_state(
        project_agent_state(events),
        CompactionPolicy(max_pass_verifier_results=0, max_critical_items=16),
    )

    assert [result.status for result in state.verifier_results] == ["FAIL"]
    assert any("regression" in failure.detail for failure in state.known_failures)


def test_edit_rejection_and_tool_failure_are_known_failures() -> None:
    events = _simple_events(
        {"event_type": "run.started", "payload": {}},
        {"event_type": "edit.rejected", "payload": {"reason": "stale file"}},
        {
            "event_type": "tool.result",
            "payload": {"command": "pytest", "success": false, "error": "test failed"},
        },
    )
    state = project_agent_state(events)

    categories = [failure.category for failure in state.known_failures]
    assert categories == ["BAD_PATCH", "TOOL_ERROR"]


def test_empty_event_sequence_fails_closed() -> None:
    with pytest.raises(StateProjectionError) as exc:
        project_agent_state([])

    assert exc.value.code == "state.empty_log"
