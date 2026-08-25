"""Unit tests for MSTR-MEASURE-v0 monotonic event logic (T026)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from mstr_qualify.measurement.protocol import (
    AcceptedActionKind,
    FinalResultKind,
    MeasurementRecord,
    RunFailureKind,
    TaskMeasurementSession,
)


@dataclass
class MutableClock:
    """Test clock whose value the test advances explicitly."""

    value_ns: int = 1_000_000_000

    def now_ns(self) -> int:
        return self.value_ns


def _session(clock: MutableClock, *, edit: bool = True) -> TaskMeasurementSession:
    return TaskMeasurementSession(
        required_verifiers=("v_static", "v_tests"),
        requires_edit=edit,
        clock=clock,
        timeout_ns=60_000_000_000,
        wall_clock_metadata={"wall_start_utc": "2026-08-25T12:00:00Z"},
    )


MS = 1_000_000


def _happy_path(clock: MutableClock, session: TaskMeasurementSession) -> None:
    session.start_task()
    clock.value_ns += 5 * MS
    session.record_first_local_interaction()
    clock.value_ns += 40 * MS
    session.record_accepted_action(AcceptedActionKind.REPOSITORY_SEARCH)
    clock.value_ns += 200 * MS
    session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
    clock.value_ns += 100 * MS
    session.record_verifier_result("v_static", passed=True)
    clock.value_ns += 150 * MS
    session.record_verifier_result("v_tests", passed=True)
    clock.value_ns += 10 * MS
    session.complete_task()


class TestHappyPath:
    def test_ttvc_is_max_of_last_pass_and_completion(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        _happy_path(clock, session)
        record = session.finalize()
        assert record.censored is False
        assert record.final_result is FinalResultKind.VERIFIED_PASS
        # last pass at start + 495ms; completion at +505ms → TTVC = 505ms.
        assert record.ttvc_ms == pytest.approx(505.0)

    def test_ttfa_and_ttfce_measured_from_submission(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        _happy_path(clock, session)
        record = session.finalize()
        assert record.ttfa_ms == pytest.approx(45.0)
        assert record.ttfce_ms == pytest.approx(245.0)
        assert record.ttfi_ms == pytest.approx(5.0)

    def test_wall_clock_metadata_present_but_never_in_durations(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        _happy_path(clock, session)
        record = session.finalize()
        assert isinstance(record, MeasurementRecord)
        assert record.wall_clock_metadata["wall_start_utc"] == "2026-08-25T12:00:00Z"
        # All durations derive from monotonic values only; wall metadata has
        # no influence — verified implicitly by exact ms assertions above.


class TestTTFA:
    def test_rejected_tool_output_does_not_stop_ttfa(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        clock.value_ns += 30 * MS
        session.record_rejected_tool_output("malformed JSON tool call")
        clock.value_ns += 20 * MS
        session.record_accepted_action(AcceptedActionKind.FILE_OR_SYMBOL_READ)
        clock.value_ns += 50 * MS
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        for verifier in ("v_static", "v_tests"):
            clock.value_ns += 10 * MS
            session.record_verifier_result(verifier, passed=True)
        session.complete_task()
        record = session.finalize()
        # TTFA stops only at the accepted action (+50ms), not at rejection.
        assert record.ttfa_ms == pytest.approx(50.0)
        assert record.rejected_tool_outputs == 1

    def test_only_first_accepted_action_stops_ttfa(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        clock.value_ns += 10 * MS
        session.record_accepted_action(AcceptedActionKind.SHELL_BUILD_TEST_START)
        clock.value_ns += 90 * MS
        session.record_accepted_action(AcceptedActionKind.FILE_OR_SYMBOL_READ)
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        for verifier in ("v_static", "v_tests"):
            session.record_verifier_result(verifier, passed=True)
        session.complete_task()
        record = session.finalize()
        assert record.ttfa_ms == pytest.approx(10.0)


class TestTTFCE:
    def test_no_edit_task_reports_na_not_zero(self) -> None:
        clock = MutableClock()
        session = _session(clock, edit=False)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.FIRST_USER_VISIBLE_OUTPUT_TOKEN)
        session.record_verifier_result("v_static", passed=True)
        session.record_verifier_result("v_tests", passed=True)
        session.complete_task()
        record = session.finalize()
        assert record.censored is False
        assert record.ttvc_ms is not None and record.ttvc_ms >= 0
        assert record.ttfce_ms is None

    def test_edit_commit_required_for_ttfce_value(self) -> None:
        clock = MutableClock()
        session = _session(clock, edit=True)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.FILE_OR_SYMBOL_READ)
        for verifier in ("v_static", "v_tests"):
            session.record_verifier_result(verifier, passed=True)
        session.complete_task()
        record = session.finalize()
        assert record.ttfce_ms is None


class TestRepairTimeInsideTTVC:
    def test_failing_then_passing_verifier_extends_ttvc(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.EDIT_TRANSACTION_START)
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        clock.value_ns += 100 * MS
        session.record_verifier_result("v_static", passed=True)
        clock.value_ns += 100 * MS
        session.record_verifier_result("v_tests", passed=False)  # repair starts
        clock.value_ns += 500 * MS  # agent repairs work
        session.record_verifier_result("v_tests", passed=True)  # repair done
        session.complete_task()
        record = session.finalize()
        assert record.censored is False
        # All verifier events (including the failed one) are retained as
        # evidence; the last event for v_tests is the post-repair PASS.
        assert len(record.verifier_outcomes) == 3
        assert record.verifier_outcomes[1].passed is False
        assert record.verifier_outcomes[2].passed is True
        # Repair time remains inside TTVC: last required PASS at ~700ms.
        assert record.ttvc_ms == pytest.approx(700.0)

    def test_stale_pass_removed_when_verifier_fails_after_passing(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.EDIT_TRANSACTION_START)
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        clock.value_ns += 100 * MS
        session.record_verifier_result("v_tests", passed=True)  # early pass
        clock.value_ns += 100 * MS
        session.record_verifier_result("v_static", passed=True)
        clock.value_ns += 100 * MS
        session.record_verifier_result("v_tests", passed=False)  # regression!
        session.complete_task()
        record = session.finalize()
        # The stale v_tests pass must NOT yield VERIFIED_PASS.
        assert record.censored is True
        assert record.final_result is FinalResultKind.VERIFIER_FAIL
        assert "v_tests" in (record.censor_reason or "")
        assert record.ttvc_ms is None


class TestCensoring:
    def test_timeout_yields_censored_run_not_successful_sample(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.REPOSITORY_SEARCH)
        session.mark_timed_out()
        record = session.finalize()
        assert record.censored is True
        assert record.final_result is FinalResultKind.TIMEOUT
        assert record.ttvc_ms is None
        assert record.censor_reason is not None

    def test_completed_without_all_required_passes_censored(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_verifier_result("v_static", passed=True)
        session.complete_task()  # v_tests never passed
        record = session.finalize()
        assert record.censored is True
        assert record.final_result is FinalResultKind.VERIFIER_FAIL
        assert record.ttvc_ms is None
        assert "v_tests" in (record.censor_reason or "")

    def test_failed_run_censored_with_detail(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.fail_run("model produced invalid output repeatedly")
        record = session.finalize()
        assert record.censored is True
        assert "invalid output" in (record.censor_reason or "")


class TestFailClosedViolations:
    def test_events_must_not_move_backward(self) -> None:
        clock = MutableClock(value_ns=1_000_000)
        session = _session(clock)
        session.start_task()
        clock.value_ns -= 500_000  # backwards!
        with pytest.raises(Exception, match="backward"):
            session.record_accepted_action(AcceptedActionKind.REPOSITORY_SEARCH)

    def test_duplicate_terminal_state_fails_closed(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.complete_task()
        with pytest.raises(Exception, match="terminal"):
            session.complete_task()

    def test_unknown_verifier_rejected(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        with pytest.raises(Exception, match="required set"):
            session.record_verifier_result("rogue_verifier", passed=True)

    def test_verifier_set_frozen_before_execution(self) -> None:
        # The frozen set is captured at construction; later mutation of the
        # caller's list cannot add verifiers to a running session.
        verifiers = ["v_a"]
        clock = MutableClock()
        session = TaskMeasurementSession(
            required_verifiers=verifiers,
            requires_edit=False,
            clock=clock,
        )
        verifiers.append("v_b")  # mutate after construction
        session.start_task()
        with pytest.raises(Exception, match="required set"):
            session.record_verifier_result("v_b", passed=True)

    def test_finalize_before_terminal_prohibited(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        with pytest.raises(Exception, match="terminal"):
            session.finalize()

    def test_empty_verifier_set_rejected_at_construction(self) -> None:
        with pytest.raises(Exception, match="non-empty"):
            TaskMeasurementSession(
                required_verifiers=(),
                requires_edit=False,
                clock=MutableClock(),
            )

    def test_duplicate_verifier_ids_rejected(self) -> None:
        with pytest.raises(Exception, match="duplicate"):
            TaskMeasurementSession(
                required_verifiers=("v_a", "v_a"),
                requires_edit=False,
                clock=MutableClock(),
            )

    def test_double_start_rejected(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        with pytest.raises(Exception, match="already started"):
            session.start_task()


class TestManualClockDeterminism:
    def test_identical_event_schedules_yield_identical_records(self) -> None:
        records: list[MeasurementRecord] = []
        for _ in range(2):
            clock = MutableClock()
            session = _session(clock)
            _happy_path(clock, session)
            records.append(session.finalize())
        assert records[0] == records[1]


class TestReviewFixRegressions:
    def test_frozen_timeout_budget_enforced_even_if_completion_claimed(self) -> None:
        clock = MutableClock()
        session = TaskMeasurementSession(
            required_verifiers=("v_static",),
            requires_edit=False,
            clock=clock,
            timeout_ns=1_000 * MS,
        )
        session.start_task()
        session.record_verifier_result("v_static", passed=True)
        clock.value_ns += 5_000 * MS  # completion claimed far beyond budget
        session.complete_task()
        record = session.finalize()
        assert record.censored is True
        assert record.final_result is FinalResultKind.TIMEOUT
        assert record.ttvc_ms is None

    def test_ttfi_first_response_only(self) -> None:
        clock = MutableClock()
        session = _session(clock, edit=False)
        session.start_task()
        clock.value_ns += 7 * MS
        session.record_first_local_interaction()
        clock.value_ns += 90 * MS
        session.record_first_local_interaction()  # later smoke response ignored
        for verifier in ("v_static", "v_tests"):
            session.record_verifier_result(verifier, passed=True)
        session.complete_task()
        record = session.finalize()
        assert record.ttfi_ms == pytest.approx(7.0)

    def test_failure_kinds_map_to_distinct_results(self) -> None:
        for kind, expected in [
            (RunFailureKind.MODEL_ERROR, FinalResultKind.MODEL_ERROR),
            (RunFailureKind.TOOL_ERROR, FinalResultKind.TOOL_ERROR),
            (RunFailureKind.VERIFIER_FAIL, FinalResultKind.VERIFIER_FAIL),
        ]:
            clock = MutableClock()
            session = _session(clock)
            session.start_task()
            session.fail_run("operational failure", kind=kind)
            record = session.finalize()
            assert record.final_result is expected

    def test_edit_lineage_required_and_reported(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.EDIT_TRANSACTION_START)
        with pytest.raises(Exception, match="lineage"):
            session.record_edit_committed(file_hash_before="", file_hash_after="")
        with pytest.raises(Exception, match="no-op"):
            session.record_edit_committed(
                file_hash_before="a" * 64, file_hash_after="a" * 64
            )
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        for verifier in ("v_static", "v_tests"):
            session.record_verifier_result(verifier, passed=True)
        session.complete_task()
        record = session.finalize()
        assert len(record.edit_lineage) == 1

    def test_censored_run_does_not_report_numeric_ttfce(self) -> None:
        clock = MutableClock()
        session = _session(clock)
        session.start_task()
        session.record_accepted_action(AcceptedActionKind.EDIT_TRANSACTION_START)
        session.record_edit_committed(file_hash_before="a" * 64, file_hash_after="b" * 64)
        session.mark_timed_out()  # contribution never verified
        record = session.finalize()
        assert record.censored is True
        assert record.ttfce_ms is None
