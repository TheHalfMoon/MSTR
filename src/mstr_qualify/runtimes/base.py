"""Runtime adapter boundary for MSTR qualification.

T023 defines the protocol every candidate runtime adapter must satisfy, an
explicit lifecycle state machine, capability discovery, and a deterministic
dummy implementation that requires no model artifacts, no network access,
and no external processes. No real backend is preselected by this module.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ..errors import QualificationError
from ..ids import validate_sha256


class AdapterError(QualificationError):
    """Base error for runtime adapter boundary violations."""

    default_code = "runtime.adapter"


class AdapterStateError(AdapterError):
    default_code = "runtime.state"


class UnsupportedOperationError(AdapterError):
    default_code = "runtime.unsupported"


class LifecycleState(Enum):
    """Explicit lifecycle states; transitions are validated fail-closed."""

    UNINITIALIZED = "uninitialized"
    READY = "ready"
    TERMINATED = "terminated"


class PrefixCacheState(Enum):
    """Prefix cache identity required by MSTR-MEASURE-v0 run-state reporting."""

    EMPTY = "empty"
    POPULATED = "populated"


@dataclass(frozen=True, slots=True)
class LoadRequest:
    """Identity-only load request; never contains weight bytes or paths.

    The artifact identity fields mirror the ModelArtifact record so any real
    adapter must be able to prove what it loaded without this harness ever
    fetching binaries itself.
    """

    artifact_id: str
    artifact_sha256: str
    format_name: str
    context_length: int

    def __post_init__(self) -> None:
        if not self.artifact_id or self.artifact_id.strip() != self.artifact_id:
            raise AdapterStateError(
                "artifact_id must be non-empty with no surrounding whitespace",
                code="runtime.load_request_artifact_id",
            )
        validate_sha256(self.artifact_sha256)
        if not self.format_name or self.format_name.strip() != self.format_name:
            raise AdapterStateError(
                "format_name must be non-empty with no surrounding whitespace",
                code="runtime.load_request_format",
            )
        if self.context_length < 1:
            raise AdapterStateError(
                "context_length must be positive",
                code="runtime.load_request_context",
                details={"context_length": self.context_length},
            )


@dataclass(frozen=True, slots=True)
class RuntimeCapabilities:
    """Static capability description discovered before any load attempt."""

    supported_formats: tuple[str, ...]
    max_context_length: int | None
    supports_cpu_only: bool | None
    supports_prefix_cache: bool | None
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.max_context_length is not None and self.max_context_length < 1:
            raise AdapterStateError(
                "max_context_length must be positive when present",
                code="runtime.capability_context",
            )
        if len(set(self.supported_formats)) != len(self.supported_formats):
            raise AdapterStateError(
                "supported_formats must not contain duplicates",
                code="runtime.capability_formats",
            )
        if len(set(self.notes)) != len(self.notes):
            raise AdapterStateError(
                "capability notes must not contain duplicates",
                code="runtime.capability_notes",
            )

    def supports_format(self, format_name: str) -> bool:
        return format_name in self.supported_formats


@dataclass(frozen=True, slots=True)
class PrefillResult:
    prompt_tokens: int
    cache_state_after: PrefixCacheState

    def __post_init__(self) -> None:
        if self.prompt_tokens < 0:
            raise AdapterStateError(
                "prompt_tokens must be non-negative",
                code="runtime.prefill_tokens",
                details={"prompt_tokens": self.prompt_tokens},
            )


@dataclass(frozen=True, slots=True)
class DecodeResult:
    generated_tokens: int

    def __post_init__(self) -> None:
        if self.generated_tokens < 0:
            raise AdapterStateError(
                "generated_tokens must be non-negative",
                code="runtime.decode_tokens",
                details={"generated_tokens": self.generated_tokens},
            )


class RuntimeAdapter(Protocol):
    """Protocol boundary for candidate runtime backends.

    Implementations must:

    - keep the full lifecycle explicit (discover -> load -> infer -> terminate);
    - return deterministic structured results for identical inputs;
    - expose capabilities explicitly instead of guessing them at call time;
    - represent unavailable/unsupported operations by raising
      :class:`UnsupportedOperationError` rather than returning fake values;
    - perform no hidden network access and no model-artifact acquisition;
    - terminate cleanly and remain terminable exactly once per lifecycle.
    """

    def platform_family(self) -> str:
        """Stable identifier of the backend family (e.g. ``dummy``)."""
        ...

    def capabilities(self) -> RuntimeCapabilities:
        """Discover static capabilities without loading anything."""
        ...

    def load(self, request: LoadRequest) -> PrefixCacheState:
        """Transition UNINITIALIZED -> READY for the identified artifact."""
        ...

    def prefill(self, prompt_tokens: int) -> PrefillResult:
        """Prefill the declared prompt token count."""
        ...

    def decode(self, max_new_tokens: int) -> DecodeResult:
        """Decode up to ``max_new_tokens`` tokens."""
        ...

    def cache_state(self) -> PrefixCacheState:
        """Report current prefix cache state while READY."""
        ...

    def terminate(self) -> None:
        """Clean teardown; idempotent-safe only via explicit state checks."""
        ...


def require_ready(state: LifecycleState) -> None:
    if state is not LifecycleState.READY:
        raise AdapterStateError(
            "operation requires lifecycle state READY",
            code="runtime.not_ready",
            details={"state": state.value},
        )


def validate_decode_count(max_new_tokens: int) -> int:
    if max_new_tokens < 1:
        raise AdapterStateError(
            "max_new_tokens must be at least one",
            code="runtime.decode_budget",
            details={"max_new_tokens": max_new_tokens},
        )
    return max_new_tokens


class DummyRuntimeAdapter:
    """Deterministic in-memory adapter used by tests and dry-run validation.

    It performs zero I/O: no files are read, no network is touched, and no
    model weights exist anywhere in its execution path. Identical call
    sequences always produce identical structured results.
    """

    def __init__(
        self,
        *,
        supported_formats: Sequence[str] = ("dummy-format",),
        max_context_length: int | None = None,
    ) -> None:
        formats = tuple(supported_formats)
        if not formats:
            raise AdapterStateError(
                "DummyRuntimeAdapter needs at least one supported format",
                code="runtime.dummy_formats",
            )
        self._capabilities = RuntimeCapabilities(
            supported_formats=formats,
            max_context_length=max_context_length,
            supports_cpu_only=True,
            supports_prefix_cache=True,
        )
        self._state = LifecycleState.UNINITIALIZED
        self._loaded_artifact_id: str | None = None
        self._cache_state = PrefixCacheState.EMPTY

    @property
    def state(self) -> LifecycleState:
        return self._state

    @property
    def loaded_artifact_id(self) -> str | None:
        return self._loaded_artifact_id

    def platform_family(self) -> str:
        return "dummy"

    def capabilities(self) -> RuntimeCapabilities:
        return self._capabilities

    def _require_uninitialized(self) -> None:
        if self._state is not LifecycleState.UNINITIALIZED:
            raise AdapterStateError(
                "load is only valid from lifecycle state UNINITIALIZED",
                code="runtime.invalid_load_state",
                details={"state": self._state.value},
            )

    def load(self, request: LoadRequest) -> PrefixCacheState:
        self._require_uninitialized()
        caps = self._capabilities
        if not caps.supports_format(request.format_name):
            raise UnsupportedOperationError(
                "requested artifact format is not supported by this adapter",
                code="runtime.format_unsupported",
                details={
                    "format": request.format_name,
                    "supported": ",".join(caps.supported_formats),
                },
            )
        if (
            caps.max_context_length is not None
            and request.context_length > caps.max_context_length
        ):
            raise UnsupportedOperationError(
                "requested context length exceeds adapter maximum",
                code="runtime.context_unsupported",
                details={
                    "requested": request.context_length,
                    "max": caps.max_context_length,
                },
            )
        # Deterministic dummy behavior: nothing is fetched or executed.
        self._state = LifecycleState.READY
        self._loaded_artifact_id = request.artifact_id
        self._cache_state = PrefixCacheState.EMPTY
        return self._cache_state

    def prefill(self, prompt_tokens: int) -> PrefillResult:
        require_ready(self._state)
        result = PrefillResult(
            prompt_tokens=prompt_tokens,
            cache_state_after=PrefixCacheState.POPULATED,
        )
        self._cache_state = PrefixCacheState.POPULATED
        return result

    def decode(self, max_new_tokens: int) -> DecodeResult:
        require_ready(self._state)
        budget = validate_decode_count(max_new_tokens)
        return DecodeResult(generated_tokens=budget)

    def cache_state(self) -> PrefixCacheState:
        require_ready(self._state)
        return self._cache_state

    def terminate(self) -> None:
        if self._state is LifecycleState.TERMINATED:
            raise AdapterStateError(
                "adapter already terminated; duplicate termination is prohibited",
                code="runtime.double_terminate",
            )
        self._state = LifecycleState.TERMINATED
        self._loaded_artifact_id = None
        self._cache_state = PrefixCacheState.EMPTY
