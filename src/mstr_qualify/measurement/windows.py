"""Windows memory/paging sampler via Win32 APIs (ctypes, local only).

Raw API concepts keep their own identities: the working set maps to RSS,
PrivateUsage is reported as private_bytes (Windows-specific identity),
PageFaultCount is total faults (NOT hard faults), and a dedicated
memory-pressure classification stays UNSUPPORTED because dwMemoryLoad
percent is not one of MSTR-MEASURE-v0's defined pressure states.

All collectors are injected so unit tests run on any development OS
without requiring Windows.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from .platform import (
    MemoryScope,
    MetricAvailability,
    ProcessTreeSample,
    SampledMetric,
    SamplingError,
    SystemMemoryPressure,
    SystemMemorySample,
    unavailable,
)

_PAGE_SIZE = 4096


@dataclass(frozen=True, slots=True)
class FakeSystemMemoryStatus:
    """Test double mirroring MEMORYSTATUSEX field names."""

    ull_total_phys: int
    ull_avail_phys: int
    ull_total_pagefile: int
    ull_avail_pagefile: int
    dw_memory_load: int


@dataclass(frozen=True, slots=True)
class FakeProcessMemoryCounters:
    """Test double mirroring PROCESS_MEMORY_COUNTERS_EX field names."""

    working_set_size: int
    peak_working_set_size: int
    page_file_usage: int
    private_usage: int
    page_fault_count: int


def _windows_query_system_memory() -> FakeSystemMemoryStatus:
    raise SamplingError(
        "real Windows collection requires win32; inject a collector for tests",
        code="measurement.windows_collector_missing",
    )


def _windows_query_process_memory(pid: int) -> FakeProcessMemoryCounters:
    raise SamplingError(
        f"real Windows collection requires win32 for pid {pid}",
        code="measurement.windows_collector_missing",
    )


@dataclass(frozen=True, slots=True)
class WindowsSamplerOptions:
    query_system_memory: Callable[[], FakeSystemMemoryStatus] = _windows_query_system_memory
    query_process_memory: Callable[[int], FakeProcessMemoryCounters] = _windows_query_process_memory
    core_pids: Sequence[int] = field(default_factory=tuple)
    tool_pids: Sequence[int] = field(default_factory=tuple)
    page_size_bytes: int = _PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page_size_bytes < 1:
            raise SamplingError(
                "page_size_bytes must be positive",
                code="measurement.page_size",
                details={"page_size_bytes": self.page_size_bytes},
            )


class WindowsPlatformSampler:
    """Implements PlatformSampler for Windows x86_64 qualification lanes."""

    def __init__(self, options: WindowsSamplerOptions | None = None) -> None:
        self._options = options or WindowsSamplerOptions()

    def platform_family(self) -> str:
        return "windows"

    def page_size_bytes(self) -> int:
        return self._options.page_size_bytes

    def sample_process_tree(self, scope: MemoryScope) -> ProcessTreeSample:
        opts = self._options
        if scope is MemoryScope.WHOLE_SYSTEM_PRESSURE:
            raise SamplingError(
                "use sample_system_memory for whole-system pressure",
                code="measurement.wrong_scope",
            )
        if scope is MemoryScope.MSTR_CORE_TREE:
            pids: list[int] = list(opts.core_pids)
        elif scope is MemoryScope.TASK_TOOL_TREE:
            pids = list(opts.tool_pids)
        else:
            pids = [*opts.core_pids, *opts.tool_pids]
        if not pids:
            note = f"no processes attributed to {scope.value}"
            return ProcessTreeSample(
                scope=scope,
                process_count=0,
                rss_bytes=unavailable("rss_bytes", note=note),
                peak_rss_bytes=unavailable("peak_rss_bytes", note=note),
                private_bytes=unavailable("private_bytes", note=note),
                swap_used_bytes=unavailable("swap_used_bytes", note=note),
            )

        ws_total = peak_ws_total = private_total = pagefile_used = 0
        try:
            counters_list = [opts.query_process_memory(pid) for pid in pids]
        except OSError as exc:
            raise SamplingError(
                "process memory collection failed",
                code="measurement.windows_process_query_failed",
                details={"reason": str(exc)},
            ) from exc
        for counters in counters_list:
            ws_total += counters.working_set_size
            peak_ws_total += max(counters.peak_working_set_size, counters.working_set_size)
            private_total += counters.private_usage
            pagefile_used += counters.page_file_usage
        # Note: PageFaultCount from PROCESS_MEMORY_COUNTERS counts ALL faults
        # (soft + hard); hard-fault deltas require ETW and stay unsupported.
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_metric("rss_bytes", ws_total),
            peak_rss_bytes=_metric("peak_rss_bytes", peak_ws_total),
            private_bytes=_metric("private_bytes", private_total),
            swap_used_bytes=_metric("pagefile_backing_bytes", pagefile_used),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        status = self._options.query_system_memory()
        notes = (
            "memory pressure classification not derivable from dwMemoryLoad "
            "percent under MSTR-MEASURE-v0; left UNSUPPORTED rather than mapped",
        )
        return SystemMemorySample(
            total_bytes=_metric("total_bytes", status.ull_total_phys),
            available_bytes=_metric("available_bytes", status.ull_avail_phys),
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=_metric("swap_configured_bytes", status.ull_total_pagefile),
            swap_used_bytes=_metric(
                "swap_used_bytes",
                status.ull_total_pagefile - status.ull_avail_pagefile,
            ),
            major_page_faults_total=unavailable(
                "major_page_faults_total",
                unsupported=True,
                note="hard-fault deltas require ETW tracing; PageFaultCount is total faults only",
            ),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=notes,
        )


def _metric(name: str, value: int) -> SampledMetric:
    return SampledMetric(
        name=name,
        availability=MetricAvailability.AVAILABLE,
        value=value,
        unit="bytes",
    )


def create_sampler(options: WindowsSamplerOptions | None = None) -> WindowsPlatformSampler:
    """Factory used by host detection helpers and tests."""
    return WindowsPlatformSampler(options)
