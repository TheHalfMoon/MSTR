"""Runtime adapter boundary package for MSTR qualification."""

from .base import (
    AdapterError,
    AdapterStateError,
    DecodeResult,
    DummyRuntimeAdapter,
    LifecycleState,
    LoadRequest,
    PrefixCacheState,
    PrefillResult,
    RuntimeAdapter,
    RuntimeCapabilities,
    UnsupportedOperationError,
)
from .benchmark_cli import (
    BenchmarkCliError,
    BenchmarkCliProfile,
    BenchmarkCliRuntimeAdapter,
    BenchmarkObservation,
    CommandResult,
    load_benchmark_profile,
)

__all__ = [
    "AdapterError",
    "AdapterStateError",
    "BenchmarkCliError",
    "BenchmarkCliProfile",
    "BenchmarkCliRuntimeAdapter",
    "BenchmarkObservation",
    "CommandResult",
    "DecodeResult",
    "DummyRuntimeAdapter",
    "LifecycleState",
    "LoadRequest",
    "PrefixCacheState",
    "PrefillResult",
    "RuntimeAdapter",
    "RuntimeCapabilities",
    "UnsupportedOperationError",
    "load_benchmark_profile",
]
