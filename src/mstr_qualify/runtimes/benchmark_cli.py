"""T030 portable CPU benchmark-CLI runtime adapter.

The adapter binds the T023 RuntimeAdapter lifecycle to an already-installed,
local benchmark executable. It never downloads a runtime or model artifact,
never uses provider repository flags, and forces CPU-only execution through
the configured GPU-layer argument.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ids import sha256_file, validate_sha256
from .base import (
    AdapterError,
    AdapterStateError,
    DecodeResult,
    LifecycleState,
    LoadRequest,
    PrefixCacheState,
    PrefillResult,
    RuntimeCapabilities,
    UnsupportedOperationError,
    require_ready,
    validate_decode_count,
)


class BenchmarkCliError(AdapterError):
    """Stable failure boundary for portable benchmark CLI adapters."""

    default_code = "runtime.benchmark_cli"


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[tuple[str, ...], float], CommandResult]


@dataclass(frozen=True, slots=True)
class BenchmarkObservation:
    """Last verified benchmark observation retained for T031+ measurement plumbing."""

    operation: str
    prompt_tokens: int
    generated_tokens: int
    threads: int
    gpu_layers: int
    average_nanoseconds: int
    average_tokens_per_second: float
    runtime_build_commit: str | None

    def __post_init__(self) -> None:
        if self.operation not in {"prefill", "decode"}:
            raise BenchmarkCliError(
                "benchmark observation operation is invalid",
                code="runtime.benchmark_observation_operation",
                details={"operation": self.operation},
            )
        if min(self.prompt_tokens, self.generated_tokens, self.average_nanoseconds) < 0:
            raise BenchmarkCliError(
                "benchmark observation contains a negative measurement",
                code="runtime.benchmark_observation_negative",
            )
        if self.threads < 1:
            raise BenchmarkCliError(
                "benchmark observation threads must be positive",
                code="runtime.benchmark_observation_threads",
            )
        if self.gpu_layers != 0:
            raise BenchmarkCliError(
                "portable CPU observation must report zero GPU layers",
                code="runtime.benchmark_observation_gpu",
                details={"gpu_layers": self.gpu_layers},
            )
        if self.average_tokens_per_second < 0:
            raise BenchmarkCliError(
                "average tokens per second must be non-negative",
                code="runtime.benchmark_observation_rate",
            )


@dataclass(frozen=True, slots=True)
class BenchmarkCliProfile:
    """Pinned command-line contract for one portable CPU benchmark runtime."""

    runtime_id: str
    executable: str
    upstream_repository: str
    upstream_revision: str
    supported_formats: tuple[str, ...] = ("gguf",)
    model_arg: str = "-m"
    prompt_arg: str = "-p"
    generation_arg: str = "-n"
    threads_arg: str = "-t"
    gpu_layers_arg: str = "-ngl"
    repetitions_arg: str = "-r"
    output_args: tuple[str, ...] = ("-o", "json")

    def __post_init__(self) -> None:
        string_fields = {
            "runtime_id": self.runtime_id,
            "executable": self.executable,
            "upstream_repository": self.upstream_repository,
            "upstream_revision": self.upstream_revision,
            "model_arg": self.model_arg,
            "prompt_arg": self.prompt_arg,
            "generation_arg": self.generation_arg,
            "threads_arg": self.threads_arg,
            "gpu_layers_arg": self.gpu_layers_arg,
            "repetitions_arg": self.repetitions_arg,
        }
        for name, value in string_fields.items():
            if not value or value.strip() != value:
                raise BenchmarkCliError(
                    "benchmark profile strings must be non-empty and canonical",
                    code="runtime.benchmark_profile_string",
                    details={"field": name},
                )
        if not self.supported_formats or len(set(self.supported_formats)) != len(
            self.supported_formats
        ):
            raise BenchmarkCliError(
                "benchmark profile needs unique supported formats",
                code="runtime.benchmark_profile_formats",
            )
        if not self.output_args or any(not item for item in self.output_args):
            raise BenchmarkCliError(
                "benchmark profile output arguments are required",
                code="runtime.benchmark_profile_output",
            )


def load_benchmark_profile(path: Path) -> BenchmarkCliProfile:
    """Load a strict profile from repository-owned JSON without side effects."""

    try:
        decoded: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BenchmarkCliError(
            "unable to load benchmark runtime profile",
            code="runtime.benchmark_profile_read",
            details={"path": str(path)},
        ) from exc
    if not isinstance(decoded, dict):
        raise BenchmarkCliError(
            "benchmark runtime profile root must be an object",
            code="runtime.benchmark_profile_root",
        )

    required = {
        "runtime_id",
        "executable",
        "upstream_repository",
        "upstream_revision",
        "supported_formats",
        "arguments",
    }
    if set(decoded) != required:
        raise BenchmarkCliError(
            "benchmark runtime profile fields do not match the frozen contract",
            code="runtime.benchmark_profile_fields",
            details={"fields": ",".join(sorted(decoded))},
        )
    arguments = decoded["arguments"]
    if not isinstance(arguments, dict):
        raise BenchmarkCliError(
            "benchmark runtime profile arguments must be an object",
            code="runtime.benchmark_profile_arguments",
        )
    expected_argument_fields = {
        "model",
        "prompt_tokens",
        "generation_tokens",
        "threads",
        "gpu_layers",
        "repetitions",
        "output",
    }
    if set(arguments) != expected_argument_fields:
        raise BenchmarkCliError(
            "benchmark runtime argument fields do not match the frozen contract",
            code="runtime.benchmark_profile_argument_fields",
        )
    formats = decoded["supported_formats"]
    output = arguments["output"]
    if not isinstance(formats, list) or not all(isinstance(item, str) for item in formats):
        raise BenchmarkCliError(
            "supported_formats must be a string array",
            code="runtime.benchmark_profile_format_type",
        )
    if not isinstance(output, list) or not all(isinstance(item, str) for item in output):
        raise BenchmarkCliError(
            "output arguments must be a string array",
            code="runtime.benchmark_profile_output_type",
        )

    scalar_values = {
        "runtime_id": decoded["runtime_id"],
        "executable": decoded["executable"],
        "upstream_repository": decoded["upstream_repository"],
        "upstream_revision": decoded["upstream_revision"],
        "model": arguments["model"],
        "prompt_tokens": arguments["prompt_tokens"],
        "generation_tokens": arguments["generation_tokens"],
        "threads": arguments["threads"],
        "gpu_layers": arguments["gpu_layers"],
        "repetitions": arguments["repetitions"],
    }
    if not all(isinstance(value, str) for value in scalar_values.values()):
        raise BenchmarkCliError(
            "benchmark runtime profile scalar fields must be strings",
            code="runtime.benchmark_profile_scalar_type",
        )

    return BenchmarkCliProfile(
        runtime_id=str(decoded["runtime_id"]),
        executable=str(decoded["executable"]),
        upstream_repository=str(decoded["upstream_repository"]),
        upstream_revision=str(decoded["upstream_revision"]),
        supported_formats=tuple(formats),
        model_arg=str(arguments["model"]),
        prompt_arg=str(arguments["prompt_tokens"]),
        generation_arg=str(arguments["generation_tokens"]),
        threads_arg=str(arguments["threads"]),
        gpu_layers_arg=str(arguments["gpu_layers"]),
        repetitions_arg=str(arguments["repetitions"]),
        output_args=tuple(output),
    )


def _subprocess_runner(argv: tuple[str, ...], timeout_seconds: float) -> CommandResult:
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise BenchmarkCliError(
            "runtime executable was not found",
            code="runtime.executable_missing",
            details={"executable": argv[0]},
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BenchmarkCliError(
            "runtime benchmark timed out",
            code="runtime.process_timeout",
            details={"timeout_seconds": timeout_seconds},
        ) from exc
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


class BenchmarkCliRuntimeAdapter:
    """Portable CPU adapter for local benchmark CLIs such as llama-bench.

    The artifact path and executable are supplied by the caller/environment.
    The T023 LoadRequest remains identity-only. Before READY, this adapter
    verifies the local artifact bytes against the exact requested SHA-256.
    Each benchmark call is an isolated process, so prefix cache state is
    explicitly EMPTY and never represented as reusable state.
    """

    def __init__(
        self,
        *,
        profile: BenchmarkCliProfile,
        artifact_path: Path,
        threads: int,
        timeout_seconds: float = 600.0,
        command_runner: CommandRunner | None = None,
    ) -> None:
        if threads < 1:
            raise BenchmarkCliError(
                "threads must be positive",
                code="runtime.threads_invalid",
                details={"threads": threads},
            )
        if timeout_seconds <= 0:
            raise BenchmarkCliError(
                "timeout_seconds must be positive",
                code="runtime.timeout_invalid",
            )
        self._profile = profile
        self._artifact_path = artifact_path
        self._threads = threads
        self._timeout_seconds = timeout_seconds
        self._command_runner = command_runner or _subprocess_runner
        self._state = LifecycleState.UNINITIALIZED
        self._request: LoadRequest | None = None
        self._last_observation: BenchmarkObservation | None = None

    @property
    def state(self) -> LifecycleState:
        return self._state

    @property
    def last_observation(self) -> BenchmarkObservation | None:
        return self._last_observation

    def platform_family(self) -> str:
        return self._profile.runtime_id

    def capabilities(self) -> RuntimeCapabilities:
        return RuntimeCapabilities(
            supported_formats=self._profile.supported_formats,
            max_context_length=None,
            supports_cpu_only=True,
            supports_prefix_cache=False,
            notes=(
                "local_artifact_only",
                "network_acquisition_prohibited",
                "isolated_benchmark_process_no_reusable_prefix_cache",
            ),
        )

    def load(self, request: LoadRequest) -> PrefixCacheState:
        if self._state is not LifecycleState.UNINITIALIZED:
            raise AdapterStateError(
                "load is only valid from lifecycle state UNINITIALIZED",
                code="runtime.invalid_load_state",
                details={"state": self._state.value},
            )
        if not self.capabilities().supports_format(request.format_name):
            raise UnsupportedOperationError(
                "requested artifact format is not supported by benchmark adapter",
                code="runtime.format_unsupported",
                details={"format": request.format_name},
            )
        if not self._artifact_path.is_file():
            raise BenchmarkCliError(
                "local model artifact does not exist",
                code="runtime.artifact_missing",
                details={"path": str(self._artifact_path)},
            )
        expected = validate_sha256(request.artifact_sha256)
        actual = sha256_file(self._artifact_path)
        if actual != expected:
            raise BenchmarkCliError(
                "local model artifact SHA-256 does not match LoadRequest",
                code="runtime.artifact_hash_mismatch",
                details={"expected": expected, "actual": actual},
            )
        self._request = request
        self._state = LifecycleState.READY
        self._last_observation = None
        return PrefixCacheState.EMPTY

    def _request_ready(self) -> LoadRequest:
        require_ready(self._state)
        if self._request is None:
            raise AdapterStateError(
                "READY adapter is missing its load identity",
                code="runtime.ready_identity_missing",
            )
        return self._request

    def _command(self, *, prompt_tokens: int, generation_tokens: int) -> tuple[str, ...]:
        return (
            self._profile.executable,
            self._profile.model_arg,
            str(self._artifact_path),
            self._profile.prompt_arg,
            str(prompt_tokens),
            self._profile.generation_arg,
            str(generation_tokens),
            self._profile.threads_arg,
            str(self._threads),
            self._profile.gpu_layers_arg,
            "0",
            self._profile.repetitions_arg,
            "1",
            *self._profile.output_args,
        )

    def _run_benchmark(
        self,
        *,
        operation: str,
        prompt_tokens: int,
        generation_tokens: int,
    ) -> BenchmarkObservation:
        outcome = self._command_runner(
            self._command(
                prompt_tokens=prompt_tokens,
                generation_tokens=generation_tokens,
            ),
            self._timeout_seconds,
        )
        if outcome.returncode != 0:
            diagnostic = (outcome.stdout + "\n" + outcome.stderr).strip()[-1000:]
            raise BenchmarkCliError(
                "runtime benchmark process returned non-zero",
                code="runtime.process_failure",
                details={"returncode": outcome.returncode, "diagnostic": diagnostic},
            )
        try:
            payload: Any = json.loads(outcome.stdout)
        except json.JSONDecodeError as exc:
            raise BenchmarkCliError(
                "runtime benchmark stdout is not valid JSON",
                code="runtime.output_json",
            ) from exc
        if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], Mapping):
            raise BenchmarkCliError(
                "runtime benchmark JSON must contain exactly one result object",
                code="runtime.output_shape",
            )
        row = payload[0]
        required_types: dict[str, type] = {
            "n_prompt": int,
            "n_gen": int,
            "n_threads": int,
            "n_gpu_layers": int,
            "avg_ns": int,
            "avg_ts": (int, float),  # type: ignore[dict-item]
        }
        for field, expected_type in required_types.items():
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, expected_type):
                raise BenchmarkCliError(
                    "runtime benchmark result field has invalid type",
                    code="runtime.output_field_type",
                    details={"field": field},
                )
        identities = {
            "n_prompt": (int(row["n_prompt"]), prompt_tokens),
            "n_gen": (int(row["n_gen"]), generation_tokens),
            "n_threads": (int(row["n_threads"]), self._threads),
            "n_gpu_layers": (int(row["n_gpu_layers"]), 0),
        }
        for field, (actual, expected) in identities.items():
            if actual != expected:
                raise BenchmarkCliError(
                    "runtime benchmark result does not match requested identity",
                    code="runtime.output_identity",
                    details={"field": field, "expected": expected, "actual": actual},
                )
        observation = BenchmarkObservation(
            operation=operation,
            prompt_tokens=prompt_tokens,
            generated_tokens=generation_tokens,
            threads=self._threads,
            gpu_layers=0,
            average_nanoseconds=int(row["avg_ns"]),
            average_tokens_per_second=float(row["avg_ts"]),
            runtime_build_commit=(
                str(row["build_commit"])
                if isinstance(row.get("build_commit"), str) and row["build_commit"]
                else None
            ),
        )
        self._last_observation = observation
        return observation

    def prefill(self, prompt_tokens: int) -> PrefillResult:
        request = self._request_ready()
        if prompt_tokens < 0:
            raise AdapterStateError(
                "prompt_tokens must be non-negative",
                code="runtime.prefill_tokens",
                details={"prompt_tokens": prompt_tokens},
            )
        if prompt_tokens > request.context_length:
            raise UnsupportedOperationError(
                "prefill exceeds the declared context length",
                code="runtime.context_unsupported",
                details={"requested": prompt_tokens, "context_length": request.context_length},
            )
        self._run_benchmark(
            operation="prefill",
            prompt_tokens=prompt_tokens,
            generation_tokens=0,
        )
        return PrefillResult(
            prompt_tokens=prompt_tokens,
            cache_state_after=PrefixCacheState.EMPTY,
        )

    def decode(self, max_new_tokens: int) -> DecodeResult:
        request = self._request_ready()
        budget = validate_decode_count(max_new_tokens)
        if budget > request.context_length:
            raise UnsupportedOperationError(
                "decode budget exceeds the declared context length",
                code="runtime.context_unsupported",
                details={"requested": budget, "context_length": request.context_length},
            )
        self._run_benchmark(
            operation="decode",
            prompt_tokens=0,
            generation_tokens=budget,
        )
        return DecodeResult(generated_tokens=budget)

    def cache_state(self) -> PrefixCacheState:
        self._request_ready()
        return PrefixCacheState.EMPTY

    def terminate(self) -> None:
        if self._state is LifecycleState.TERMINATED:
            raise AdapterStateError(
                "adapter already terminated; duplicate termination is prohibited",
                code="runtime.double_terminate",
            )
        self._state = LifecycleState.TERMINATED
        self._request = None
        self._last_observation = None
