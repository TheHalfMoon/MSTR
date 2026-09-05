"""T030 portable CPU benchmark-CLI runtime adapter.

This module binds the canonical T023 RuntimeAdapter lifecycle to an
already-installed local benchmark executable. It performs no artifact/runtime
acquisition and accepts only identity-checked local model bytes.
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from ..ids import sha256_file, validate_sha256
from .base import (
    AdapterError,
    AdapterStateError,
    DecodeResult,
    LifecycleState,
    LoadRequest,
    PrefillResult,
    PrefixCacheState,
    RuntimeCapabilities,
    UnsupportedOperationError,
    require_ready,
    validate_decode_count,
)

_SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
_SHORT_GIT_RE = re.compile(r"^[0-9a-f]{7,40}$")
_FORBIDDEN_NETWORK_FLAGS = (
    "-hf",
    "-hfr",
    "--hf-repo",
    "-hff",
    "--hf-file",
    "-hft",
    "--hf-token",
    "-rpc",
    "--rpc",
)
_DEVICE_FLAGS = frozenset({"-dev", "--device"})


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
    """One verified benchmark observation retained for T031+ plumbing."""

    operation: str
    prompt_tokens: int
    generated_tokens: int
    threads: int
    gpu_layers: int
    average_nanoseconds: int
    average_tokens_per_second: float
    runtime_build_commit: str

    def __post_init__(self) -> None:
        if self.operation not in {"prefill", "decode"}:
            raise BenchmarkCliError(
                "benchmark observation operation is invalid",
                code="runtime.benchmark_observation_operation",
                details={"operation": self.operation},
            )
        if min(self.prompt_tokens, self.generated_tokens) < 0:
            raise BenchmarkCliError(
                "benchmark observation contains a negative token count",
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
        if self.average_nanoseconds <= 0:
            raise BenchmarkCliError(
                "average benchmark nanoseconds must be positive",
                code="runtime.benchmark_observation_measurement",
            )
        if (
            not math.isfinite(self.average_tokens_per_second)
            or self.average_tokens_per_second <= 0
        ):
            raise BenchmarkCliError(
                "average tokens per second must be finite and positive",
                code="runtime.benchmark_observation_measurement",
            )
        if not _SHORT_GIT_RE.fullmatch(self.runtime_build_commit):
            raise BenchmarkCliError(
                "runtime build commit must be a lowercase Git commit prefix",
                code="runtime.benchmark_observation_build",
            )


def _contains_forbidden_network_flag(token: str) -> bool:
    return any(
        token == flag or token.startswith(f"{flag}=")
        for flag in _FORBIDDEN_NETWORK_FLAGS
    )


def _validate_cpu_device_args(tokens: tuple[str, ...]) -> None:
    positions = [index for index, token in enumerate(tokens) if token in _DEVICE_FLAGS]
    if len(positions) != 1:
        raise BenchmarkCliError(
            "portable CPU profile must contain exactly one device selector",
            code="runtime.benchmark_profile_cpu_device",
        )
    position = positions[0]
    if position + 1 >= len(tokens) or tokens[position + 1] != "none":
        raise BenchmarkCliError(
            "portable CPU profile must select device=none",
            code="runtime.benchmark_profile_cpu_device",
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
    output_args: tuple[str, ...] = ("--device", "none", "-o", "json")

    def __post_init__(self) -> None:
        strings = (
            self.runtime_id,
            self.executable,
            self.upstream_repository,
            self.upstream_revision,
            self.model_arg,
            self.prompt_arg,
            self.generation_arg,
            self.threads_arg,
            self.gpu_layers_arg,
            self.repetitions_arg,
        )
        if any(not value or value.strip() != value for value in strings):
            raise BenchmarkCliError(
                "benchmark profile strings must be non-empty and canonical",
                code="runtime.benchmark_profile_string",
            )
        if not _SHA1_RE.fullmatch(self.upstream_revision):
            raise BenchmarkCliError(
                "upstream_revision must be an exact 40-character Git commit",
                code="runtime.benchmark_profile_revision",
            )
        if (
            not self.supported_formats
            or len(set(self.supported_formats)) != len(self.supported_formats)
            or any(not value or value.strip() != value for value in self.supported_formats)
        ):
            raise BenchmarkCliError(
                "benchmark profile needs unique canonical supported formats",
                code="runtime.benchmark_profile_formats",
            )
        if not self.output_args or any(
            not value or value.strip() != value for value in self.output_args
        ):
            raise BenchmarkCliError(
                "benchmark profile output arguments are required and canonical",
                code="runtime.benchmark_profile_output",
            )
        if "json" not in self.output_args:
            raise BenchmarkCliError(
                "benchmark profile must request JSON output",
                code="runtime.benchmark_profile_output_json",
            )
        command_tokens = (
            self.model_arg,
            self.prompt_arg,
            self.generation_arg,
            self.threads_arg,
            self.gpu_layers_arg,
            self.repetitions_arg,
            *self.output_args,
        )
        forbidden = sorted(
            token for token in command_tokens if _contains_forbidden_network_flag(token)
        )
        if forbidden:
            raise BenchmarkCliError(
                "benchmark profile must not contain network acquisition or RPC flags",
                code="runtime.benchmark_profile_network_flag",
                details={"flags": ",".join(forbidden)},
            )
        _validate_cpu_device_args(command_tokens)


def _read_json_object(path: Path) -> dict[str, object]:
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
    return cast(dict[str, object], decoded)


def _require_exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    *,
    code: str,
) -> None:
    if set(value) != expected:
        raise BenchmarkCliError(
            "benchmark runtime profile fields do not match the frozen contract",
            code=code,
            details={"fields": ",".join(sorted(value))},
        )


def _require_string(value: object, *, field: str) -> str:
    if not isinstance(value, str):
        raise BenchmarkCliError(
            "benchmark runtime profile field must be a string",
            code="runtime.benchmark_profile_scalar_type",
            details={"field": field},
        )
    return value


def _require_string_tuple(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise BenchmarkCliError(
            "benchmark runtime profile field must be a string array",
            code="runtime.benchmark_profile_array_type",
            details={"field": field},
        )
    return tuple(cast(list[str], value))


def load_benchmark_profile(path: Path) -> BenchmarkCliProfile:
    """Load a strict repository-owned profile without side effects."""

    decoded = _read_json_object(path)
    _require_exact_keys(
        decoded,
        {
            "runtime_id",
            "executable",
            "upstream_repository",
            "upstream_revision",
            "supported_formats",
            "arguments",
        },
        code="runtime.benchmark_profile_fields",
    )
    raw_arguments = decoded["arguments"]
    if not isinstance(raw_arguments, dict):
        raise BenchmarkCliError(
            "benchmark runtime profile arguments must be an object",
            code="runtime.benchmark_profile_arguments",
        )
    arguments = cast(dict[str, object], raw_arguments)
    _require_exact_keys(
        arguments,
        {
            "model",
            "prompt_tokens",
            "generation_tokens",
            "threads",
            "gpu_layers",
            "repetitions",
            "output",
        },
        code="runtime.benchmark_profile_argument_fields",
    )
    return BenchmarkCliProfile(
        runtime_id=_require_string(decoded["runtime_id"], field="runtime_id"),
        executable=_require_string(decoded["executable"], field="executable"),
        upstream_repository=_require_string(
            decoded["upstream_repository"], field="upstream_repository"
        ),
        upstream_revision=_require_string(
            decoded["upstream_revision"], field="upstream_revision"
        ),
        supported_formats=_require_string_tuple(
            decoded["supported_formats"], field="supported_formats"
        ),
        model_arg=_require_string(arguments["model"], field="arguments.model"),
        prompt_arg=_require_string(
            arguments["prompt_tokens"], field="arguments.prompt_tokens"
        ),
        generation_arg=_require_string(
            arguments["generation_tokens"], field="arguments.generation_tokens"
        ),
        threads_arg=_require_string(arguments["threads"], field="arguments.threads"),
        gpu_layers_arg=_require_string(
            arguments["gpu_layers"], field="arguments.gpu_layers"
        ),
        repetitions_arg=_require_string(
            arguments["repetitions"], field="arguments.repetitions"
        ),
        output_args=_require_string_tuple(arguments["output"], field="arguments.output"),
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


def _require_integer(row: Mapping[str, object], field: str) -> int:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise BenchmarkCliError(
            "runtime benchmark result field must be an integer",
            code="runtime.output_field_type",
            details={"field": field},
        )
    return value


def _require_number(row: Mapping[str, object], field: str) -> float:
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BenchmarkCliError(
            "runtime benchmark result field must be numeric",
            code="runtime.output_field_type",
            details={"field": field},
        )
    number = float(value)
    if not math.isfinite(number):
        raise BenchmarkCliError(
            "runtime benchmark numeric result must be finite",
            code="runtime.output_nonfinite",
            details={"field": field},
        )
    return number


def _require_string_field(row: Mapping[str, object], field: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise BenchmarkCliError(
            "runtime benchmark result field must be a non-empty string",
            code="runtime.output_field_type",
            details={"field": field},
        )
    return value


class BenchmarkCliRuntimeAdapter:
    """Portable CPU adapter for local benchmark CLIs such as llama-bench."""

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
                "rpc_prohibited",
                "device_none_required",
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
        if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
            raise BenchmarkCliError(
                "runtime benchmark JSON must contain exactly one result object",
                code="runtime.output_shape",
            )
        row = cast(dict[str, object], payload[0])

        reported_prompt = _require_integer(row, "n_prompt")
        reported_generation = _require_integer(row, "n_gen")
        reported_threads = _require_integer(row, "n_threads")
        reported_gpu_layers = _require_integer(row, "n_gpu_layers")
        average_nanoseconds = _require_integer(row, "avg_ns")
        average_tokens_per_second = _require_number(row, "avg_ts")
        reported_devices = _require_string_field(row, "devices")

        identities = {
            "n_prompt": (reported_prompt, prompt_tokens),
            "n_gen": (reported_generation, generation_tokens),
            "n_threads": (reported_threads, self._threads),
            "n_gpu_layers": (reported_gpu_layers, 0),
        }
        for field, (actual, expected) in identities.items():
            if actual != expected:
                raise BenchmarkCliError(
                    "runtime benchmark result does not match requested identity",
                    code="runtime.output_identity",
                    details={"field": field, "expected": expected, "actual": actual},
                )
        if reported_devices != "none":
            raise BenchmarkCliError(
                "runtime benchmark result does not prove CPU-only device selection",
                code="runtime.output_device_identity",
                details={"devices": reported_devices},
            )

        model_filename = _require_string_field(row, "model_filename")
        if model_filename != str(self._artifact_path):
            raise BenchmarkCliError(
                "runtime benchmark result does not match the loaded artifact path",
                code="runtime.output_model_identity",
            )
        build_commit = _require_string_field(row, "build_commit")
        if (
            not _SHORT_GIT_RE.fullmatch(build_commit)
            or not self._profile.upstream_revision.startswith(build_commit)
        ):
            raise BenchmarkCliError(
                "runtime benchmark build commit does not match the pinned profile revision",
                code="runtime.build_identity",
                details={"reported": build_commit, "pinned": self._profile.upstream_revision},
            )

        observation = BenchmarkObservation(
            operation=operation,
            prompt_tokens=prompt_tokens,
            generated_tokens=generation_tokens,
            threads=self._threads,
            gpu_layers=reported_gpu_layers,
            average_nanoseconds=average_nanoseconds,
            average_tokens_per_second=average_tokens_per_second,
            runtime_build_commit=build_commit,
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
                details={
                    "requested": prompt_tokens,
                    "context_length": request.context_length,
                },
            )
        if prompt_tokens > 0:
            self._run_benchmark(
                operation="prefill",
                prompt_tokens=prompt_tokens,
                generation_tokens=0,
            )
        else:
            self._last_observation = None
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
