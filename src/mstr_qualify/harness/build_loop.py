"""A005: bounded MSTR-BUILD-LOOP-v0 state graph.

The build loop is deliberately small and framework-neutral.  It enforces the
frozen loop contract, bounded execution budgets, a trivial-task fast path, and
fail-closed stop semantics.  A builder may propose STOP after verification or
escalate when the contract permits it, but this module never turns a builder
proposal into canonical success; A006 owns the protected finalizer boundary.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from mstr_qualify.schemas import validate_instance


class LoopState(StrEnum):
    ORIENT = "ORIENT"
    GOAL = "GOAL"
    LOCALIZE = "LOCALIZE"
    PLAN = "PLAN"
    ACT = "ACT"
    OBSERVE = "OBSERVE"
    VERIFY = "VERIFY"
    RECOVER = "RECOVER"
    STOP = "STOP"


class LoopControlError(ValueError):
    """Fail-closed loop-control error with a stable machine code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class StopProposal:
    """A non-authoritative builder stop proposal.

    ``canonical_success`` is intentionally fixed to ``False``.  A006 must
    derive terminal success from protected verifier results.
    """

    reason: str
    escalation: bool
    verifier_observed: bool
    canonical_success: bool = False


@dataclass(frozen=True)
class LoopSnapshot:
    state: LoopState
    steps: int
    tool_calls: int
    repairs: int
    stopped: bool
    stop_proposal: StopProposal | None


_ALLOWED_TRANSITIONS: dict[LoopState, frozenset[LoopState]] = {
    LoopState.ORIENT: frozenset({LoopState.GOAL}),
    LoopState.GOAL: frozenset(
        {LoopState.LOCALIZE, LoopState.PLAN, LoopState.ACT, LoopState.VERIFY}
    ),
    LoopState.LOCALIZE: frozenset(
        {LoopState.PLAN, LoopState.ACT, LoopState.OBSERVE, LoopState.VERIFY}
    ),
    LoopState.PLAN: frozenset(
        {LoopState.LOCALIZE, LoopState.ACT, LoopState.OBSERVE, LoopState.VERIFY}
    ),
    LoopState.ACT: frozenset(
        {LoopState.OBSERVE, LoopState.VERIFY, LoopState.RECOVER}
    ),
    LoopState.OBSERVE: frozenset(
        {
            LoopState.LOCALIZE,
            LoopState.PLAN,
            LoopState.ACT,
            LoopState.VERIFY,
            LoopState.RECOVER,
        }
    ),
    LoopState.VERIFY: frozenset(
        {
            LoopState.LOCALIZE,
            LoopState.PLAN,
            LoopState.ACT,
            LoopState.OBSERVE,
            LoopState.RECOVER,
        }
    ),
    LoopState.RECOVER: frozenset(
        {LoopState.LOCALIZE, LoopState.PLAN, LoopState.ACT, LoopState.VERIFY}
    ),
    LoopState.STOP: frozenset(),
}


class BuildLoop:
    """Contract-bound state machine for one bounded MSTR build attempt."""

    def __init__(
        self,
        contract: Mapping[str, Any],
        *,
        clock: Callable[[], float] | None = None,
    ) -> None:
        payload = dict(contract)
        validate_instance("mstr-loop-contract-v0", payload)
        self._contract = payload
        self._clock = clock or time.monotonic
        self._started_at = self._clock()
        self._state = LoopState.ORIENT
        self._steps = 0
        self._tool_calls = 0
        self._repairs = 0
        self._stop_proposal: StopProposal | None = None
        self._failed_action_evidence: dict[str, str] = {}

    @property
    def state(self) -> LoopState:
        return self._state

    @property
    def stopped(self) -> bool:
        return self._state is LoopState.STOP

    @property
    def trivial_task_fast_path_enabled(self) -> bool:
        fast_path = self._contract.get("trivial_task_fast_path")
        return bool(isinstance(fast_path, dict) and fast_path.get("enabled"))

    def snapshot(self) -> LoopSnapshot:
        return LoopSnapshot(
            state=self._state,
            steps=self._steps,
            tool_calls=self._tool_calls,
            repairs=self._repairs,
            stopped=self.stopped,
            stop_proposal=self._stop_proposal,
        )

    def _ensure_active(self) -> None:
        if self.stopped:
            raise LoopControlError(
                "the build loop is already stopped",
                code="loop.already_stopped",
            )
        elapsed = self._clock() - self._started_at
        if elapsed > float(self._contract["timeout_seconds"]):
            raise LoopControlError(
                "the build loop exceeded its timeout budget",
                code="loop.timeout_exceeded",
            )

    def _consume_step(self) -> None:
        if self._steps >= int(self._contract["max_steps"]):
            raise LoopControlError(
                "the build loop exceeded its step budget",
                code="loop.step_budget_exhausted",
            )
        self._steps += 1

    def transition(self, next_state: LoopState | str) -> LoopSnapshot:
        """Advance to one legal conceptual state.

        Direct transition to STOP is forbidden because STOP is a proposal
        boundary, not a builder-authored success verdict.
        """

        self._ensure_active()
        target = LoopState(next_state)
        if target is LoopState.STOP:
            raise LoopControlError(
                "STOP requires propose_stop() or escalate()",
                code="loop.stop_requires_proposal",
            )
        if target not in _ALLOWED_TRANSITIONS[self._state]:
            raise LoopControlError(
                f"illegal transition {self._state.value} -> {target.value}",
                code="loop.illegal_transition",
            )
        self._consume_step()
        self._state = target
        return self.snapshot()

    def record_tool_call(self) -> LoopSnapshot:
        self._ensure_active()
        if self._tool_calls >= int(self._contract["max_tool_calls"]):
            raise LoopControlError(
                "the build loop exceeded its tool-call budget",
                code="loop.tool_budget_exhausted",
            )
        self._tool_calls += 1
        return self.snapshot()

    def record_repair(self) -> LoopSnapshot:
        self._ensure_active()
        if self._repairs >= int(self._contract["max_repairs"]):
            raise LoopControlError(
                "the build loop exceeded its repair budget",
                code="loop.repair_budget_exhausted",
            )
        self._repairs += 1
        return self.snapshot()

    def record_action_result(
        self,
        action_id: str,
        *,
        success: bool,
        evidence_token: str,
    ) -> None:
        """Bind a failed action to the evidence available when it failed."""

        self._ensure_active()
        if not action_id.strip() or not evidence_token.strip():
            raise LoopControlError(
                "action_id and evidence_token must be non-empty",
                code="loop.invalid_action_identity",
            )
        if success:
            self._failed_action_evidence.pop(action_id, None)
        else:
            self._failed_action_evidence[action_id] = evidence_token

    def admit_retry(self, action_id: str, *, evidence_token: str) -> None:
        """Reject retrying the same failed action without new evidence."""

        self._ensure_active()
        prior = self._failed_action_evidence.get(action_id)
        if prior is None:
            return
        recovery_policy = self._contract["recovery_policy"]
        retry_without_evidence = recovery_policy[
            "retry_same_failed_action_without_new_evidence"
        ]
        if retry_without_evidence is False and prior == evidence_token:
            raise LoopControlError(
                "retry of the same failed action requires new evidence",
                code="loop.retry_without_new_evidence",
            )

    def propose_stop(
        self,
        reason: str,
        *,
        verifier_observed: bool,
    ) -> StopProposal:
        """Stop after VERIFY while leaving success authority to A006."""

        self._ensure_active()
        if not reason.strip():
            raise LoopControlError(
                "stop reason must be non-empty",
                code="loop.stop_reason_missing",
            )
        if self._state is not LoopState.VERIFY:
            raise LoopControlError(
                "normal STOP may only be proposed from VERIFY",
                code="loop.stop_before_verify",
            )
        if not verifier_observed:
            raise LoopControlError(
                "normal STOP requires a verifier observation",
                code="loop.stop_without_verifier_observation",
            )
        self._consume_step()
        proposal = StopProposal(
            reason=reason,
            escalation=False,
            verifier_observed=True,
        )
        self._stop_proposal = proposal
        self._state = LoopState.STOP
        return proposal

    def escalate(self, reason: str) -> StopProposal:
        """Stop without claiming success when the contract permits escalation."""

        self._ensure_active()
        if not reason.strip():
            raise LoopControlError(
                "escalation reason must be non-empty",
                code="loop.escalation_reason_missing",
            )
        stop_policy = self._contract["stop_policy"]
        if stop_policy["allow_escalation"] is not True:
            raise LoopControlError(
                "the active loop contract does not permit escalation",
                code="loop.escalation_forbidden",
            )
        self._consume_step()
        proposal = StopProposal(
            reason=reason,
            escalation=True,
            verifier_observed=False,
        )
        self._stop_proposal = proposal
        self._state = LoopState.STOP
        return proposal
