"""A008: H1 MSTR-native typed harness.

H1 extends the canonical H0/A003-A006 spine without creating a second success
or event authority. It adds typed tool envelopes, compare-before-apply stale
protection, explicit selective/no-retrieval context, bounded recovery cadence,
A004 compaction, and measured-only prefix/cache observations.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mstr_qualify.harness.build_loop import LoopSnapshot, LoopState
from mstr_qualify.harness.neutral import (
    CommandResult,
    CommandRunner,
    NeutralHarness,
    NeutralHarnessError,
    SearchMatch,
    Verifier,
    VerifierOutcome,
)
from mstr_qualify.state import AgentState, CompactionPolicy, compact_agent_state

ContextMode = Literal["NO_RETRIEVAL", "EXPLICIT_PATHS"]
PrefixCacheState = Literal["UNMEASURED", "MEASURED"]
_ABSENT_SHA256 = "ABSENT"


class NativeHarnessError(NeutralHarnessError):
    """Fail-closed H1 error with a stable machine code."""


@dataclass(frozen=True)
class ReadRequest:
    path: str


@dataclass(frozen=True)
class ReadResult:
    path: str
    content: str
    content_sha256: str
    result_identity: str


@dataclass(frozen=True)
class SearchRequest:
    needle: str
    paths: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SearchResult:
    matches: tuple[SearchMatch, ...]
    result_identity: str


@dataclass(frozen=True)
class ShellRequest:
    argv: tuple[str, ...]


@dataclass(frozen=True)
class ShellResult:
    command: CommandResult
    result_identity: str


@dataclass(frozen=True)
class EditRequest:
    path: str
    content: str
    expected_sha256: str


@dataclass(frozen=True)
class EditResult:
    path: str
    previous_sha256: str
    content_sha256: str
    result_identity: str


@dataclass(frozen=True)
class ContextRequest:
    mode: ContextMode
    paths: tuple[str, ...] = ()
    max_chars: int | None = None


@dataclass(frozen=True)
class ContextFile:
    path: str
    content: str
    content_sha256: str
    truncated: bool


@dataclass(frozen=True)
class ContextSelectionResult:
    mode: ContextMode
    files: tuple[ContextFile, ...]
    truncated: bool
    result_identity: str


@dataclass(frozen=True)
class RecoveryCadence:
    max_consecutive_failures: int = 2

    def __post_init__(self) -> None:
        if self.max_consecutive_failures < 1:
            raise NativeHarnessError(
                "max_consecutive_failures must be positive",
                code="h1.recovery_policy_invalid",
            )


@dataclass(frozen=True)
class PrefixCacheMeasurement:
    """Runtime-observed prefix/cache accounting; estimates are not accepted."""

    input_tokens: int
    shared_prefix_tokens: int
    cache_read_tokens: int | None = None
    measurement_source: Literal["MEASURED_RUNTIME"] = "MEASURED_RUNTIME"

    def __post_init__(self) -> None:
        values = (self.input_tokens, self.shared_prefix_tokens)
        if any(value < 0 for value in values):
            raise NativeHarnessError(
                "prefix/cache token counts must be non-negative",
                code="h1.prefix_measurement_invalid",
            )
        if self.shared_prefix_tokens > self.input_tokens:
            raise NativeHarnessError(
                "shared prefix tokens cannot exceed input tokens",
                code="h1.prefix_measurement_invalid",
            )
        if self.cache_read_tokens is not None:
            if self.cache_read_tokens < 0 or self.cache_read_tokens > self.input_tokens:
                raise NativeHarnessError(
                    "cache read tokens must be within the input-token envelope",
                    code="h1.prefix_measurement_invalid",
                )

    @property
    def prefix_reuse_ratio(self) -> float | None:
        if self.input_tokens == 0:
            return None
        return self.shared_prefix_tokens / self.input_tokens


@dataclass(frozen=True)
class NativeSnapshot:
    loop: LoopSnapshot
    consecutive_failures: int
    recovery_required: bool
    prefix_cache_state: PrefixCacheState
    prefix_measurements: int


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _stable_identity(kind: str, payload: object) -> str:
    encoded = json.dumps(
        {"kind": kind, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _valid_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value)


class NativeHarness(NeutralHarness):
    """H1 typed harness over the canonical H0 loop/event/finalizer spine."""

    def __init__(
        self,
        workspace: Path,
        contract: Mapping[str, Any],
        *,
        run_id: str,
        required_verifier_ids: Sequence[str],
        command_runner: CommandRunner | None = None,
        max_search_matches: int = 100,
        context_max_files: int = 8,
        context_max_chars: int = 8192,
        recovery_cadence: RecoveryCadence | None = None,
        compaction_policy: CompactionPolicy | None = None,
    ) -> None:
        super().__init__(
            workspace,
            contract,
            run_id=run_id,
            required_verifier_ids=required_verifier_ids,
            command_runner=command_runner,
            max_search_matches=max_search_matches,
        )
        if context_max_files < 1 or context_max_chars < 1:
            raise NativeHarnessError(
                "context limits must be positive",
                code="h1.context_policy_invalid",
            )
        self._context_max_files = context_max_files
        self._context_max_chars = context_max_chars
        self._recovery_cadence = recovery_cadence or RecoveryCadence()
        self._compaction_policy = compaction_policy or CompactionPolicy()
        self._consecutive_failures = 0
        self._prefix_measurements: list[PrefixCacheMeasurement] = []

    # H1's public tool surface is typed. Internal H0 primitives remain the
    # implementation substrate but are deliberately not callable as H1 tools.
    def read_text(self, relative_path: str) -> str:
        raise NativeHarnessError(
            "H1 requires ReadRequest/ReadResult via read_typed()",
            code="h1.untyped_tool_forbidden",
        )

    def search_text(
        self,
        needle: str,
        *,
        relative_paths: Sequence[str] | None = None,
    ) -> tuple[SearchMatch, ...]:
        raise NativeHarnessError(
            "H1 requires SearchRequest/SearchResult via search_typed()",
            code="h1.untyped_tool_forbidden",
        )

    def run_shell(self, argv: Sequence[str]) -> CommandResult:
        raise NativeHarnessError(
            "H1 requires ShellRequest/ShellResult via run_shell_typed()",
            code="h1.untyped_tool_forbidden",
        )

    def apply_file(self, relative_path: str, content: str) -> str:
        raise NativeHarnessError(
            "H1 forbids unchecked whole-file apply; use apply_stale_safe_edit()",
            code="h1.unsafe_edit_forbidden",
        )

    @property
    def recovery_required(self) -> bool:
        return (
            self._consecutive_failures
            >= self._recovery_cadence.max_consecutive_failures
        )

    @property
    def prefix_cache_state(self) -> PrefixCacheState:
        return "MEASURED" if self._prefix_measurements else "UNMEASURED"

    @property
    def prefix_measurements(self) -> tuple[PrefixCacheMeasurement, ...]:
        return tuple(self._prefix_measurements)

    def native_snapshot(self) -> NativeSnapshot:
        return NativeSnapshot(
            loop=self.snapshot(),
            consecutive_failures=self._consecutive_failures,
            recovery_required=self.recovery_required,
            prefix_cache_state=self.prefix_cache_state,
            prefix_measurements=len(self._prefix_measurements),
        )

    def _require_recovery_clear(self) -> None:
        if self.recovery_required:
            raise NativeHarnessError(
                "recovery is required before another mutating/tool action",
                code="h1.recovery_required",
            )

    def _record_action_outcome(self, success: bool) -> None:
        if success:
            self._consecutive_failures = 0
        else:
            self._consecutive_failures += 1

    def read_typed(self, request: ReadRequest) -> ReadResult:
        content = super().read_text(request.path)
        digest = _sha256_text(content)
        identity = _stable_identity(
            "repository.read_utf8",
            {"path": request.path, "content_sha256": digest},
        )
        return ReadResult(request.path, content, digest, identity)

    def search_typed(self, request: SearchRequest) -> SearchResult:
        matches = super().search_text(
            request.needle,
            relative_paths=request.paths,
        )
        payload = [
            {"path": match.path, "line_number": match.line_number, "line": match.line}
            for match in matches
        ]
        return SearchResult(
            matches=matches,
            result_identity=_stable_identity("repository.search_literal", payload),
        )

    def run_shell_typed(self, request: ShellRequest) -> ShellResult:
        self._require_recovery_clear()
        try:
            result = super().run_shell(request.argv)
        except NeutralHarnessError as exc:
            if exc.code == "h0.shell_runner_failed":
                self._record_action_outcome(False)
            raise
        self._record_action_outcome(result.returncode == 0)
        identity = _stable_identity(
            "shell.argv_no_shell",
            {
                "argv": list(result.argv),
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )
        return ShellResult(result, identity)

    def apply_stale_safe_edit(self, request: EditRequest) -> EditResult:
        self._require_recovery_clear()
        self._require_state(frozenset({LoopState.ACT}), "stale-safe file apply")
        if not isinstance(request.content, str):
            raise NativeHarnessError(
                "edit content must be UTF-8 text",
                code="h1.edit_content_invalid",
            )
        expected = request.expected_sha256
        if expected != _ABSENT_SHA256 and not _valid_sha256(expected):
            raise NativeHarnessError(
                "expected_sha256 must be a lowercase SHA-256 digest or ABSENT",
                code="h1.edit_expected_identity_invalid",
            )

        path = self._resolve_path(request.path)
        if path.exists() and (not path.is_file() or path.is_symlink()):
            raise NativeHarnessError(
                "edit target must be a regular non-symlink file",
                code="h1.edit_target_invalid",
            )
        actual = _ABSENT_SHA256 if not path.exists() else hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            self._loop.record_tool_call()
            self._emit(
                "edit.proposed",
                {"path": request.path, "expected_sha256": expected},
                source="harness",
                model_visible=False,
            )
            self._emit(
                "edit.rejected",
                {
                    "path": request.path,
                    "reason": "stale_base",
                    "expected_sha256": expected,
                    "actual_sha256": actual,
                },
                source="tool",
                model_visible=True,
            )
            self._record_action_outcome(False)
            raise NativeHarnessError(
                "edit base identity changed since inspection",
                code="h1.edit_stale",
            )

        digest = super().apply_file(request.path, request.content)
        self._record_action_outcome(True)
        identity = _stable_identity(
            "edit.stale_safe_whole_file",
            {
                "path": request.path,
                "previous_sha256": actual,
                "content_sha256": digest,
            },
        )
        return EditResult(request.path, actual, digest, identity)

    def select_context(self, request: ContextRequest) -> ContextSelectionResult:
        if request.mode == "NO_RETRIEVAL":
            if request.paths:
                raise NativeHarnessError(
                    "NO_RETRIEVAL context cannot include paths",
                    code="h1.context_request_invalid",
                )
            self._emit(
                "context.observed",
                {"files_inspected": [], "h1_context_mode": "NO_RETRIEVAL"},
                source="harness",
                model_visible=True,
            )
            return ContextSelectionResult(
                mode="NO_RETRIEVAL",
                files=(),
                truncated=False,
                result_identity=_stable_identity(
                    "context.selection", {"mode": "NO_RETRIEVAL", "files": []}
                ),
            )

        if request.mode != "EXPLICIT_PATHS":
            raise NativeHarnessError(
                "unsupported H1 context mode",
                code="h1.context_request_invalid",
            )
        if not request.paths or len(set(request.paths)) != len(request.paths):
            raise NativeHarnessError(
                "EXPLICIT_PATHS requires a non-empty unique path set",
                code="h1.context_request_invalid",
            )
        if len(request.paths) > self._context_max_files:
            raise NativeHarnessError(
                "context request exceeds the configured file ceiling",
                code="h1.context_budget_exceeded",
            )
        max_chars = request.max_chars or self._context_max_chars
        if max_chars < 1 or max_chars > self._context_max_chars:
            raise NativeHarnessError(
                "context request exceeds the configured character ceiling",
                code="h1.context_budget_exceeded",
            )

        selected: list[ContextFile] = []
        used = 0
        ordered = tuple(sorted(request.paths))
        for path in ordered:
            if used >= max_chars:
                break
            content = super().read_text(path)
            digest = _sha256_text(content)
            remaining = max_chars - used
            excerpt = content[:remaining]
            truncated = len(excerpt) != len(content)
            selected.append(ContextFile(path, excerpt, digest, truncated))
            used += len(excerpt)

        overall_truncated = len(selected) != len(ordered) or any(
            item.truncated for item in selected
        )
        payload = {
            "mode": "EXPLICIT_PATHS",
            "files": [
                {
                    "path": item.path,
                    "content": item.content,
                    "content_sha256": item.content_sha256,
                    "truncated": item.truncated,
                }
                for item in selected
            ],
            "truncated": overall_truncated,
        }
        return ContextSelectionResult(
            mode="EXPLICIT_PATHS",
            files=tuple(selected),
            truncated=overall_truncated,
            result_identity=_stable_identity("context.selection", payload),
        )

    def observe_verifier(self, verifier_id: str, verifier: Verifier) -> VerifierOutcome:
        outcome = super().observe_verifier(verifier_id, verifier)
        self._record_action_outcome(outcome.status == "PASS")
        return outcome

    def recover(
        self,
        *,
        reason: str,
        evidence: str,
        next_state: LoopState = LoopState.PLAN,
    ) -> NativeSnapshot:
        if self._consecutive_failures < 1:
            raise NativeHarnessError(
                "recovery requires observed failure evidence",
                code="h1.recovery_without_failure",
            )
        if not reason.strip() or not evidence.strip():
            raise NativeHarnessError(
                "recovery reason and evidence must be non-empty",
                code="h1.recovery_evidence_invalid",
            )
        if next_state not in {
            LoopState.LOCALIZE,
            LoopState.PLAN,
            LoopState.ACT,
            LoopState.VERIFY,
        }:
            raise NativeHarnessError(
                "invalid post-recovery state",
                code="h1.recovery_next_state_invalid",
            )
        current = self.snapshot().state
        if current not in {
            LoopState.ACT,
            LoopState.OBSERVE,
            LoopState.VERIFY,
            LoopState.RECOVER,
        }:
            raise NativeHarnessError(
                "recovery is not legal from the current loop state",
                code="h1.recovery_state_invalid",
            )
        self._loop.record_repair()
        if current is not LoopState.RECOVER:
            self.transition(LoopState.RECOVER)
        self._emit(
            "recovery.started",
            {"reason": reason, "consecutive_failures": self._consecutive_failures},
            source="harness",
            model_visible=True,
        )
        self._emit(
            "recovery.result",
            {"success": True, "detail": evidence},
            source="harness",
            model_visible=True,
        )
        self._consecutive_failures = 0
        self.transition(next_state)
        return self.native_snapshot()

    def compact_state(self) -> AgentState:
        return compact_agent_state(self.project_state(), self._compaction_policy)

    def record_prefix_cache_measurement(
        self,
        measurement: PrefixCacheMeasurement,
    ) -> PrefixCacheMeasurement:
        self._prefix_measurements.append(measurement)
        self._emit(
            "context.compacted",
            {
                "h1_prefix_cache": {
                    "measurement_source": measurement.measurement_source,
                    "input_tokens": measurement.input_tokens,
                    "shared_prefix_tokens": measurement.shared_prefix_tokens,
                    "cache_read_tokens": measurement.cache_read_tokens,
                    "prefix_reuse_ratio": measurement.prefix_reuse_ratio,
                }
            },
            source="harness",
            model_visible=False,
        )
        return measurement
