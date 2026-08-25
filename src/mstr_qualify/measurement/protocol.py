"""MSTR-MEASURE-v0 monotonic event/TTFI/TTFA/TTFCE/TTVC logic.

Implements the canonical measurement semantics frozen by T001:

- durations come exclusively from a monotonic high-resolution clock;
- wall-clock timestamps are metadata only and never enter latency math;
- TTFA stops on the FIRST accepted externally observable action; malformed
  or rejected tool output never stops it;
- TTFCE requires a durable committed edit and is N/A for no-edit tasks;
- TTVC = max(last REQUIRED verifier PASS, task completed) - submitted,
  with the required verifier set frozen before execution; repair time
  stays inside TTVC; timeout/failure yields a CENSORED run, never a
  successful sample.
"""

from __future__ import annotations

import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

from ..errors import QualificationError


class ProtocolViolationError(QualificationError):
    default_code = "protocol.violation"


class MeasurementProtocolError(QualificationError):
    """Base class for protocol-level fail-closed errors."""

    default_code = "measurement.protocol"


PROTOCOL_ID = "MSTR-MEASURE-v0"


def _fail(message: str, code: str, **details: object) -> ProtocolViolationError:
    return ProtocolViolationError(message, code=code, details=details)


class MonotonicClock(Protocol):
    def now_ns(self) -> int: ...


@dataclass(frozen=True, slots=True)
class SystemMonotonicClock:
    """Production clock backed by time.monotonic_ns."""

    def now_ns(self) -> int:
        return time.monotonic_ns()


@dataclass(frozen=True, slots=True)
class ManualClock:
    """Deterministic test clock."""

    value_ns: int = 0

    def now_ns(self) -> int:
        return self.value_ns


class AcceptedActionKind(Enum):
    REPOSITORY_SEARCH = "repository_search"
    FILE_OR_SYMBOL_READ = "file_or_symbol_read"
    SHELL_BUILD_TEST_START = "shell_build_test_start"
    EDIT_TRANSACTION_START = "edit_transaction_start"
    FIRST_USER_VISIBLE_OUTPUT_TOKEN = "first_user_visible_output_token"


class TerminalState(Enum):
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    FAILED = "failed"


class FinalResultKind(Enum):
    VERIFIED_PASS = "verified_pass"
    TIMEOUT = "timeout"
    VERIFIER_FAIL = "verifier_fail"
    MODEL_ERROR = "model_error"
    TOOL_ERROR = "tool_error"


@dataclass(frozen=True, slots=True)
class VerifierOutcome:
    verifier_id: str
    passed: bool
    at_ns: int


@dataclass(frozen=True, slots=True)
class MeasurementRecord:
    """Immutable outcome of one measured run."""

    censored: bool
    final_result: FinalResultKind
    ttfi_ms: float | None
    ttfa_ms: float | None
    ttfce_ms: float | None
    ttvc_ms: float | None
    verifier_outcomes: tuple[VerifierOutcome, ...]
    rejected_tool_outputs: int
    wall_clock_metadata: dict[str, str] = field(default_factory=dict)
    censor_reason: str | None = None


_NS_PER_MS = 1_000_000


def _to_ms(delta_ns: int) -> float:
    return delta_ns / _NS_PER_MS


class TaskMeasurementSession:
    """One run's event ledger with monotonic validation and frozen verifiers."""

    def __init__(
        self,
        *,
        required_verifiers: Sequence[str],
        requires_edit: bool,
        clock: MonotonicClock,
        timeout_ns: int | None = None,
        wall_clock_metadata: Mapping[str, str] | None = None,
    ) -> None:
        if not required_verifiers:
            raise _fail(
                "required verifier set must be non-empty",
                code="measurement.empty_verifier_set",
            )
        deduped = list(dict.fromkeys(required_verifiers))
        if len(deduped) != len(required_verifiers):
            raise _fail(
                "duplicate verifier ids in required set are prohibited",
                code="measurement.duplicate_verifier",
            )
        self._required: frozenset[str] = frozenset(required_verifiers)
        self._ordered_required: tuple[str, ...] = tuple(required_verifiers)
        self._requires_edit = requires_edit
        self._clock = clock
        self._timeout_ns = timeout_ns
        self._wall_clock_metadata = dict(wall_clock_metadata or {})

        self._started_ns: int | None = None
        self._last_event_ns: int | None = None
        self._ttfi_end_ns: int | None = None
        self._ttfa_end_ns: int | None = None
        self._ttfce_commit_ns: int | None = None
        self._verifier_passes: dict[str, int] = {}
        self._verifier_fails: dict[str, int] = {}
        self._terminal: TerminalState | None = None
        self._terminal_ns: int | None = None
        self._terminal_detail: str | None = None
        self._rejected_tool_outputs = 0

    # -- lifecycle ---------------------------------------------------------

    @property
    def started(self) -> bool:
        return self._started_ns is not None

    @property
    def terminal_state(self) -> TerminalState | None:
        return self._terminal

    def start_task(self) -> None:
        if self.started:
            raise _fail("task already started", code="measurement.double_start")
        now = self._clock.now_ns()
        self._started_ns = now
        self._last_event_ns = now

    def _require_started(self) -> None:
        if not self.started or self._started_ns is None:
            raise _fail(
                "event recorded before start_task",
                code="measurement.not_started",
            )

    def _advance(self) -> int:
        """Validate monotonicity and return the current timestamp."""
        self._require_started()
        now = self._clock.now_ns()
        assert self._last_event_ns is not None
        if now < self._last_event_ns:
            raise _fail(
                "monotonic violation: events must never move backward",
                code="measurement.event_backwards",
                details={
                    "previous_ns": self._last_event_ns,
                    "attempted_ns": now,
                },
            )
        self._last_event_ns = now
        return now

    def _reject_if_terminal(self) -> None:
        if self._terminal is not None:
            raise _fail(
                f"run already reached terminal state {self._terminal.value}",
                code="measurement.after_terminal",
                details={"state": self._terminal.value},
            )

    # -- TTFI --------------------------------------------------------------

    def record_first_local_interaction(self) -> None:
        """Stop TTFI on the first complete locally generated smoke response."""
        now = self._advance()
        self._reject_if_terminal()
        self._ttfi_end_ns = now

    # -- TTFA --------------------------------------------------------------

    def record_accepted_action(self, kind: AcceptedActionKind) -> None:
        """Stop TTFA on the first ACCEPTED externally observable action."""
        del kind
        now = self._advance()
        self._reject_if_terminal()
        if self._ttfa_end_ns is None:
            self._ttfa_end_ns = now

    def record_rejected_tool_output(self, reason: str) -> None:
        """Malformed/rejected tool output NEVER stops TTFA; counted only."""
        del reason
        self._advance()
        self._reject_if_terminal()
        self._rejected_tool_outputs += 1

    # -- TTFCE ---------------------------------------------------------------

    def record_edit_committed(self) -> None:
        """A durable edit transaction successfully COMMITS to the workspace."""
        now = self._advance()
        self._reject_if_terminal()
        if not self._requires_edit:
            raise _fail(
                "edit commit recorded for a no-edit task",
                code="measurement.edit_on_no_edit_task",
            )
        if self._ttfce_commit_ns is None:
            self._ttfce_commit_ns = now

    # -- verifiers -----------------------------------------------------------

    def record_verifier_result(self, verifier_id: str, *, passed: bool) -> None:
        now = self._advance()
        self._reject_if_terminal()
        if verifier_id not in self._required:
            raise _fail(
                "verifier not in the pre-declared required set",
                code="measurement.unknown_verifier",
                details={"verifier_id": verifier_id},
            )
        if passed:
            self._verifier_passes[verifier_id] = now
        else:
            self._verifier_fails[verifier_id] = self._verifier_fails.get(verifier_id, 0) + 1

    # -- terminals -------------------------------------------------------------

    def complete_task(self) -> None:
        now = self._advance()
        self._set_terminal(TerminalState.COMPLETED, now)

    def mark_timed_out(self) -> None:
        now = self._advance()
        self._set_terminal(TerminalState.TIMED_OUT, now)

    def fail_run(self, detail: str) -> None:
        now = self._advance()
        self._set_terminal(TerminalState.FAILED, now, detail)

    def _set_terminal(
        self,
        state: TerminalState,
        at_ns: int,
        detail: str | None = None,
    ) -> None:
        if self._terminal is not None:
            raise _fail(
                "duplicate/invalid terminal state is prohibited",
                code="measurement.duplicate_terminal",
                details={"existing": self._terminal.value, "attempted": state.value},
            )
        self._terminal = state
        self._terminal_ns = at_ns
        self._terminal_detail = detail

    # -- finalization --------------------------------------------------------

    def finalize(self) -> MeasurementRecord:
        assert self._started_ns is not None
        if self._terminal is None or self._terminal_ns is None:
            raise _fail(
                "finalize before reaching any terminal state is prohibited",
                code="measurement.finalize_before_terminal",
            )

        started_ns = self._started_ns
        ttfi_ms: float | None = (
            None
            if self._ttfi_end_ns is None
            else _to_ms(self._ttfi_end_ns - started_ns)
        )
        ttfa_ms: float | None = (
            None
            if self._ttfa_end_ns is None
            else _to_ms(self._ttfa_end_ns - started_ns)
        )

        outcomes = [
            VerifierOutcome(verifier_id=v, passed=True, at_ns=self._verifier_passes[v])
            for v in self._ordered_required
            if v in self._verifier_passes
        ]
        missing_passes = sorted(set(self._ordered_required) - set(self._verifier_passes))

        ttfce_ms: float | None
        if not self._requires_edit:
            ttfce_ms = None  # N/A rather than zero per T001 section 6
        elif self._ttfce_commit_ns is None:
            ttfce_ms = None
        else:
            ttfce_ms = _to_ms(self._ttfce_commit_ns - started_ns)

        censor_reason: str | None = None
        final_result: FinalResultKind
        ttvc_ms: float | None = None

        if self._terminal is TerminalState.TIMED_OUT:
            final_result = FinalResultKind.TIMEOUT
            censor_reason = "timeout budget exhausted before verified completion"
        elif self._terminal is TerminalState.FAILED:
            final_result = FinalResultKind.VERIFIER_FAIL
            censor_reason = self._terminal_detail or "run failed"
        elif self._terminal is TerminalState.COMPLETED:
            if missing_passes:
                final_result = FinalResultKind.VERIFIER_FAIL
                censor_reason = (
                    "task claimed completed but required verifiers did not pass: "
                    + ",".join(missing_passes)
                )
            else:
                last_pass_ns = max(
                    self._verifier_passes[v] for v in self._ordered_required
                )
                ttvc_ns = max(last_pass_ns, self._terminal_ns) - started_ns
                ttvc_ms = _to_ms(ttvc_ns)
                final_result = FinalResultKind.VERIFIED_PASS

        return MeasurementRecord(
            censored=censor_reason is not None,
            final_result=final_result,
            ttfi_ms=ttfi_ms,
            ttfa_ms=ttfa_ms,
            ttfce_ms=ttfce_ms,
            ttvc_ms=ttvc_ms,
            verifier_outcomes=tuple(outcomes),
            rejected_tool_outputs=self._rejected_tool_outputs,
            wall_clock_metadata=dict(self._wall_clock_metadata),
            censor_reason=censor_reason,
        )


__all__ = [
    "PROTOCOL_ID",
    "AcceptedActionKind",
    "FinalResultKind",
    "ManualClock",
    "MeasurementProtocolError",
    "MeasurementRecord",
    "MonotonicClock",
    "ProtocolViolationError",
    "SystemMonotonicClock",
    "TaskMeasurementSession",
    "TerminalState",
    "VerifierOutcome",
]
