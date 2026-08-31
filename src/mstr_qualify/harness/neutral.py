"""A007: H0 neutral-minimal repository harness.

H0 intentionally provides only the smallest scaffold needed to expose model
capability: bounded repository read/search, argv-based shell execution, one
whole-file deterministic edit path, verifier invocation, and the shared A005 /
A006 state and success boundaries. It does not implement H1 context selection,
stale-safe edit transactions, cache policy, or autonomous recovery cadence.
"""

from __future__ import annotations

import copy
import hashlib
import shlex
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

from mstr_qualify.harness.build_loop import (
    BuildLoop,
    LoopSnapshot,
    LoopState,
    StopProposal,
)
from mstr_qualify.harness.event_log import create_event
from mstr_qualify.state import AgentState, project_agent_state
from mstr_qualify.verifier.finalizer import FinalizationDecision, finalize_run

VerifierStatus = Literal["PASS", "FAIL", "ERROR", "UNKNOWN"]
_VALID_VERIFIER_STATUSES = frozenset({"PASS", "FAIL", "ERROR", "UNKNOWN"})


class NeutralHarnessError(ValueError):
    """Fail-closed H0 error with a stable machine code."""

    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class SearchMatch:
    path: str
    line_number: int
    line: str


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class VerifierOutcome:
    status: VerifierStatus
    result_identity: str
    detail: str = ""


class CommandRunner(Protocol):
    def __call__(
        self,
        argv: tuple[str, ...],
        cwd: Path,
        timeout_seconds: float,
    ) -> CommandResult: ...


Verifier = Callable[[Path], VerifierOutcome]


def _subprocess_runner(
    argv: tuple[str, ...],
    cwd: Path,
    timeout_seconds: float,
) -> CommandResult:
    completed = subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
        shell=False,
    )
    return CommandResult(
        argv=argv,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _canonical_required_verifiers(values: Sequence[str]) -> tuple[str, ...]:
    required = tuple(values)
    if not required:
        raise NeutralHarnessError(
            "at least one required verifier is mandatory",
            code="h0.required_verifiers_empty",
        )
    if any(not isinstance(value, str) or not value.strip() for value in required):
        raise NeutralHarnessError(
            "required verifier ids must be non-empty strings",
            code="h0.required_verifier_id_invalid",
        )
    if any(value.strip() != value for value in required):
        raise NeutralHarnessError(
            "required verifier ids must not contain surrounding whitespace",
            code="h0.required_verifier_id_invalid",
        )
    if len(set(required)) != len(required):
        raise NeutralHarnessError(
            "required verifier ids must be unique",
            code="h0.required_verifiers_duplicate",
        )
    return tuple(sorted(required))


def _validate_verifier_outcome(outcome: VerifierOutcome) -> None:
    if not isinstance(outcome.status, str) or outcome.status not in _VALID_VERIFIER_STATUSES:
        raise NeutralHarnessError(
            "verifier status must be PASS, FAIL, ERROR, or UNKNOWN",
            code="h0.verifier_status_invalid",
        )
    if not isinstance(outcome.result_identity, str) or not outcome.result_identity.strip():
        raise NeutralHarnessError(
            "verifier result identity must be non-empty",
            code="h0.verifier_result_identity_invalid",
        )
    if outcome.result_identity.strip() != outcome.result_identity:
        raise NeutralHarnessError(
            "verifier result identity must not contain surrounding whitespace",
            code="h0.verifier_result_identity_invalid",
        )
    if not isinstance(outcome.detail, str):
        raise NeutralHarnessError(
            "verifier detail must be a string",
            code="h0.verifier_detail_invalid",
        )


class NeutralHarness:
    """Minimal H0 harness over the canonical MSTR loop/event/finalizer spine."""

    def __init__(
        self,
        workspace: Path,
        contract: Mapping[str, Any],
        *,
        run_id: str,
        required_verifier_ids: Sequence[str],
        command_runner: CommandRunner | None = None,
        max_search_matches: int = 100,
    ) -> None:
        root = workspace.resolve()
        if not root.is_dir():
            raise NeutralHarnessError(
                "workspace must be an existing directory",
                code="h0.workspace_invalid",
            )
        if not run_id.strip() or run_id.strip() != run_id:
            raise NeutralHarnessError(
                "run_id must be a non-empty canonical string",
                code="h0.run_id_invalid",
            )
        if max_search_matches < 1:
            raise NeutralHarnessError(
                "max_search_matches must be positive",
                code="h0.search_limit_invalid",
            )

        contract_payload = dict(contract)
        self._workspace = root
        self._loop = BuildLoop(contract_payload)
        self._timeout_seconds = float(contract_payload["timeout_seconds"])
        goal_policy = contract_payload["goal_policy"]
        self._require_acceptance_criteria = bool(
            isinstance(goal_policy, dict)
            and goal_policy.get("require_acceptance_criteria") is True
        )
        self._run_id = run_id
        self._required_verifier_ids = _canonical_required_verifiers(
            required_verifier_ids
        )
        self._command_runner = command_runner or _subprocess_runner
        self._max_search_matches = max_search_matches
        self._events: list[dict[str, Any]] = []
        self._logical_time = 0
        self._observed_verifiers: set[str] = set()
        self._emit("run.started", {}, source="harness", model_visible=True)

    @property
    def workspace(self) -> Path:
        return self._workspace

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(self._events))

    def snapshot(self) -> LoopSnapshot:
        return self._loop.snapshot()

    def project_state(self) -> AgentState:
        return project_agent_state(copy.deepcopy(self._events))

    def _emit(
        self,
        event_type: str,
        payload: dict[str, Any],
        *,
        source: str,
        model_visible: bool,
    ) -> dict[str, Any]:
        previous = str(self._events[-1]["sha256"]) if self._events else None
        event = create_event(
            run_id=self._run_id,
            seq=len(self._events),
            event_type=event_type,
            logical_time=self._logical_time,
            payload=payload,
            source=source,
            model_visible=model_visible,
            prev_sha256=previous,
        )
        self._logical_time += 1
        self._events.append(event)
        return event

    def _resolve_path(self, relative_path: str) -> Path:
        requested = Path(relative_path)
        if requested.is_absolute() or not relative_path.strip():
            raise NeutralHarnessError(
                "repository path must be a non-empty relative path",
                code="h0.path_outside_workspace",
            )
        resolved = (self._workspace / requested).resolve(strict=False)
        try:
            resolved.relative_to(self._workspace)
        except ValueError as exc:
            raise NeutralHarnessError(
                "repository path escapes the workspace",
                code="h0.path_outside_workspace",
            ) from exc
        return resolved

    def _require_state(self, allowed: frozenset[LoopState], operation: str) -> None:
        if self._loop.state not in allowed:
            expected = ", ".join(sorted(state.value for state in allowed))
            raise NeutralHarnessError(
                f"{operation} requires loop state in {{{expected}}}",
                code="h0.operation_state_invalid",
            )

    def admit_goal(
        self,
        goal: str,
        *,
        acceptance_criteria: Sequence[str],
        constraints: Sequence[str] = (),
        non_goals: Sequence[str] = (),
    ) -> LoopSnapshot:
        if not goal.strip():
            raise NeutralHarnessError("goal must be non-empty", code="h0.goal_invalid")
        if self._require_acceptance_criteria and not acceptance_criteria:
            raise NeutralHarnessError(
                "acceptance criteria are required by the active loop contract",
                code="h0.acceptance_criteria_required",
            )
        metadata = (*acceptance_criteria, *constraints, *non_goals)
        if any(not isinstance(item, str) or not item.strip() for item in metadata):
            raise NeutralHarnessError(
                "goal metadata items must be non-empty strings",
                code="h0.goal_metadata_invalid",
            )
        snapshot = self._loop.transition(LoopState.GOAL)
        self._emit(
            "run.goal_admitted",
            {
                "goal": goal,
                "acceptance_criteria": list(acceptance_criteria),
                "constraints": list(constraints),
                "non_goals": list(non_goals),
            },
            source="harness",
            model_visible=True,
        )
        return snapshot

    def transition(self, next_state: LoopState | str) -> LoopSnapshot:
        return self._loop.transition(next_state)

    def read_text(self, relative_path: str) -> str:
        self._require_state(
            frozenset({LoopState.LOCALIZE, LoopState.OBSERVE, LoopState.VERIFY}),
            "repository read",
        )
        path = self._resolve_path(relative_path)
        if not path.is_file() or path.is_symlink():
            raise NeutralHarnessError(
                "repository read target must be a regular non-symlink file",
                code="h0.read_target_invalid",
            )
        self._loop.record_tool_call()
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise NeutralHarnessError(
                "repository read target is not valid UTF-8 text",
                code="h0.read_not_text",
            ) from exc
        self._emit(
            "context.observed",
            {"files_inspected": [relative_path]},
            source="tool",
            model_visible=True,
        )
        return content

    def search_text(
        self,
        needle: str,
        *,
        relative_paths: Sequence[str] | None = None,
    ) -> tuple[SearchMatch, ...]:
        self._require_state(
            frozenset({LoopState.LOCALIZE, LoopState.OBSERVE}),
            "repository search",
        )
        if not needle:
            raise NeutralHarnessError(
                "search needle must be non-empty",
                code="h0.search_needle_invalid",
            )
        self._loop.record_tool_call()

        if relative_paths is None:
            candidates = [
                path
                for path in sorted(self._workspace.rglob("*"))
                if path.is_file() and ".git" not in path.relative_to(self._workspace).parts
            ]
        else:
            candidates = [self._resolve_path(path) for path in relative_paths]

        matches: list[SearchMatch] = []
        inspected: list[str] = []
        for path in candidates:
            if not path.is_file() or path.is_symlink():
                continue
            relative = path.relative_to(self._workspace).as_posix()
            inspected.append(relative)
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for line_number, line in enumerate(lines, start=1):
                if needle in line:
                    matches.append(SearchMatch(relative, line_number, line))
                    if len(matches) >= self._max_search_matches:
                        break
            if len(matches) >= self._max_search_matches:
                break

        self._emit(
            "context.observed",
            {
                "files_inspected": sorted(set(inspected)),
                "repo_entries": [
                    f"{match.path}:{match.line_number}:{match.line}"
                    for match in matches
                ],
            },
            source="tool",
            model_visible=True,
        )
        return tuple(matches)

    def run_shell(self, argv: Sequence[str]) -> CommandResult:
        self._require_state(frozenset({LoopState.ACT}), "shell execution")
        command = tuple(argv)
        if (
            not command
            or not isinstance(command[0], str)
            or not command[0].strip()
            or any(not isinstance(arg, str) or "\x00" in arg for arg in command)
        ):
            raise NeutralHarnessError(
                "shell argv must contain string arguments, a valid executable, and no NUL bytes",
                code="h0.shell_argv_invalid",
            )
        self._loop.record_tool_call()
        rendered = shlex.join(command)
        self._emit(
            "tool.requested",
            {"command": rendered},
            source="harness",
            model_visible=False,
        )
        try:
            result = self._command_runner(
                command,
                self._workspace,
                self._timeout_seconds,
            )
        except Exception as exc:
            self._emit(
                "tool.result",
                {
                    "command": rendered,
                    "success": False,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                source="tool",
                model_visible=True,
            )
            raise NeutralHarnessError(
                "shell runner failed before returning a result",
                code="h0.shell_runner_failed",
            ) from exc
        if result.argv != command:
            raise NeutralHarnessError(
                "shell runner returned evidence for a different argv",
                code="h0.shell_result_identity_mismatch",
            )
        detail = result.stdout if result.returncode == 0 else result.stderr
        payload: dict[str, Any] = {
            "command": rendered,
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "detail": detail,
        }
        if result.returncode != 0:
            payload["error"] = result.stderr or f"process exited {result.returncode}"
        self._emit(
            "tool.result",
            payload,
            source="tool",
            model_visible=True,
        )
        return result

    def apply_file(self, relative_path: str, content: str) -> str:
        self._require_state(frozenset({LoopState.ACT}), "file apply")
        path = self._resolve_path(relative_path)
        if path.exists() and (not path.is_file() or path.is_symlink()):
            raise NeutralHarnessError(
                "edit target must be a regular non-symlink file",
                code="h0.edit_target_invalid",
            )
        self._loop.record_tool_call()
        self._emit(
            "edit.proposed",
            {"path": relative_path},
            source="harness",
            model_visible=False,
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        except OSError as exc:
            self._emit(
                "edit.rejected",
                {"path": relative_path, "reason": f"{type(exc).__name__}: {exc}"},
                source="tool",
                model_visible=True,
            )
            raise NeutralHarnessError(
                "deterministic whole-file apply failed",
                code="h0.edit_failed",
            ) from exc
        content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        self._emit(
            "edit.applied",
            {
                "path": relative_path,
                "changed_files": [relative_path],
                "content_sha256": content_sha256,
            },
            source="tool",
            model_visible=True,
        )
        return content_sha256

    def observe_verifier(self, verifier_id: str, verifier: Verifier) -> VerifierOutcome:
        """Run a pre-stop verifier observation used only to justify STOP proposal."""
        self._require_state(frozenset({LoopState.VERIFY}), "verifier observation")
        if verifier_id not in self._required_verifier_ids:
            raise NeutralHarnessError(
                "verifier is not in the required verifier set",
                code="h0.verifier_not_required",
            )
        self._loop.record_tool_call()
        self._emit(
            "verifier.started",
            {"verifier_id": verifier_id, "phase": "pre_stop_observation"},
            source="verifier",
            model_visible=True,
        )
        try:
            outcome = verifier(self._workspace)
        except Exception as exc:
            raise NeutralHarnessError(
                "verifier callback failed before producing evidence",
                code="h0.verifier_callback_failed",
            ) from exc
        _validate_verifier_outcome(outcome)
        self._emit(
            "verifier.result",
            {
                "verifier_id": verifier_id,
                "status": outcome.status,
                "result_identity": outcome.result_identity,
                "detail": outcome.detail,
                "phase": "pre_stop_observation",
            },
            source="verifier",
            model_visible=True,
        )
        self._observed_verifiers.add(verifier_id)
        return outcome

    def propose_stop(self, reason: str) -> StopProposal:
        missing = set(self._required_verifier_ids) - self._observed_verifiers
        if missing:
            raise NeutralHarnessError(
                f"required pre-stop verifier observations missing: {sorted(missing)}",
                code="h0.pre_stop_verifier_missing",
            )
        proposal = self._loop.propose_stop(reason, verifier_observed=True)
        self._emit(
            "run.stop_proposed",
            {"reason": reason, "canonical_success": False},
            source="harness",
            model_visible=True,
        )
        return proposal

    def finalize(self, verifiers: Mapping[str, Verifier]) -> FinalizationDecision:
        """Re-run required verifiers post-stop and delegate success to A006."""
        if not self._loop.stopped:
            raise NeutralHarnessError(
                "protected finalization requires a builder stop proposal",
                code="h0.stop_required_before_finalize",
            )
        if set(verifiers) != set(self._required_verifier_ids):
            raise NeutralHarnessError(
                "post-stop verifier mapping must equal the required verifier set",
                code="h0.post_stop_verifier_set_mismatch",
            )
        for verifier_id in self._required_verifier_ids:
            self._emit(
                "verifier.started",
                {"verifier_id": verifier_id, "phase": "post_stop_finalization"},
                source="verifier",
                model_visible=False,
            )
            try:
                outcome = verifiers[verifier_id](self._workspace)
            except Exception as exc:
                raise NeutralHarnessError(
                    "post-stop verifier callback failed before producing evidence",
                    code="h0.verifier_callback_failed",
                ) from exc
            _validate_verifier_outcome(outcome)
            self._emit(
                "verifier.result",
                {
                    "verifier_id": verifier_id,
                    "status": outcome.status,
                    "result_identity": outcome.result_identity,
                    "detail": outcome.detail,
                    "phase": "post_stop_finalization",
                },
                source="verifier",
                model_visible=False,
            )

        decision = finalize_run(
            copy.deepcopy(self._events),
            required_verifier_ids=self._required_verifier_ids,
        )
        self._events.append(decision.completion_event)
        self._logical_time += 1
        return decision
