"""A003 contract/unit tests for the append-oriented event log + replay."""

from __future__ import annotations

import pytest

from mstr_qualify.harness.event_log import (
    EventLogError,
    append_event,
    compute_event_hash,
    create_event,
    model_visible_history,
    replay,
)
from mstr_qualify.schemas import validate_instance


def make_run() -> tuple[str, list[dict]]:
    """Create a three-event run and return (run_id, raw_events)."""
    rid = "test-run-001"
    e0 = create_event(rid, 0, "run.started", 1, {"goal": "implement feature"})
    log = [e0]
    e1 = create_event(rid, 1, "context.observed", 2, {"repo": "test"},
                      model_visible=True, prev_sha256=e0["sha256"])
    log.append(e1)
    e2 = create_event(rid, 2, "plan.updated", 3, {"plan": "edit file A"},
                      prev_sha256=e1["sha256"])
    log.append(e2)
    return rid, log


class TestCreateAndValidate:
    def test_created_events_pass_schema(self) -> None:
        _, events = make_run()
        for e in events:
            validate_instance("mstr-run-event-v0", e)

    def test_hash_is_deterministic(self) -> None:
        _, events = make_run()
        for e in events:
            assert compute_event_hash(e) == e["sha256"]

    def test_genesis_prev_is_sentinel(self) -> None:
        _, events = make_run()
        assert events[0]["prev_event_sha256"] == "0" * 64

    def test_chain_links(self) -> None:
        _, events = make_run()
        for i in range(1, len(events)):
            assert events[i]["prev_event_sha256"] == events[i - 1]["sha256"]

    def test_model_visible_filter(self) -> None:
        _, events = make_run()
        visible = model_visible_history(replay(events))
        assert len(visible) == 1
        assert visible[0]["event_type"] == "context.observed"


class TestReplayIntegrity:
    def test_clean_replay_succeeds(self) -> None:
        _, events = make_run()
        log = replay(events)
        assert len(log) == 3

    def test_missing_hash_fails(self) -> None:
        _, events = make_run()
        del events[1]["sha256"]
        with pytest.raises(Exception, match="sha256"):
            replay(events)

    def test_substituted_hash_fails(self) -> None:
        _, events = make_run()
        events[1]["sha256"] = "b" * 64
        with pytest.raises(EventLogError, match="hash mismatch"):
            replay(events)

    def test_gap_fails(self) -> None:
        _, events = make_run()
        events = [events[0], events[2]]  # skip seq=1
        with pytest.raises(EventLogError, match="sequence gap"):
            replay(events)

    def test_duplicate_seq_fails(self) -> None:
        _, events = make_run()
        dup = dict(events[1])
        events.insert(2, dup)
        with pytest.raises(EventLogError):
            replay(events)

    def test_reordered_events_fail(self) -> None:
        _, events = make_run()
        reordered = [events[1], events[0], events[2]]
        with pytest.raises(EventLogError):
            replay(reordered)

    def test_broken_predecessor_chain_fails(self) -> None:
        _, events = make_run()
        events[2]["prev_event_sha256"] = "c" * 64
        with pytest.raises(EventLogError, match="predecessor chain broken"):
            replay(events)


class TestAppendEvent:
    def test_append_to_empty_log(self) -> None:
        e = create_event("r-1", 0, "run.started", 1, {})
        log: list = []
        entry = append_event(log, e)
        assert len(log) == 1
        assert entry.sha256 == e["sha256"]

    def test_append_chains(self) -> None:
        e0 = create_event("r-1", 0, "run.started", 1, {})
        log: list = []
        append_event(log, e0)
        e1 = create_event("r-1", 1, "tool.result", 2, {},
                          prev_sha256=e0["sha256"])
        append_event(log, e1)
        assert log[-1].raw["prev_event_sha256"] == e0["sha256"]
