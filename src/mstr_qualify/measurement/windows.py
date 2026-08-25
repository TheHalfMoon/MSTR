"""Windows memory/paging sampler via Win32 APIs (ctypes, local only).

Identity discipline: the working set maps to RSS; PrivateUsage keeps its
Windows identity as private_bytes; MEMORYSTATUSEX pagefile fields are
actually COMMIT limit/charge, so they are reported under commit identities
and swap metrics stay UNSUPPORTED (pagefile capacity needs another API);
PageFaultCount is total faults and is never relabeled as hard faults.

Real collectors run only when invoked on win32; tests inject doubles.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

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

_PROCESS_QUERY_INFORMATION = 0x0400
_PROCESS_VM_READ = 0x0010


@dataclass(frozen=True, slots=True)
class MemoryStatusSnapshot:
    """Snapshot mirroring MEMORYSTATUSEX field names."""

    ull_total_phys: int
    ull_avail_phys: int
    ull_total_pagefile: int  # actually the COMMIT LIMIT
    ull_avail_pagefile: int  # actually AVAILABLE COMMIT
    dw_memory_load: int


@dataclass(frozen=True, slots=True)
class ProcessMemorySnapshot:
    """Snapshot mirroring PROCESS_MEMORY_COUNTERS_EX field names."""

    working_set_size: int
    peak_working_set_size: int
    page_file_usage: int
    private_usage: int
    page_fault_count: int


def _win_global_memory_status() -> MemoryStatusSnapshot:
    """Real collector: kernel32!GlobalMemoryStatusEx."""
    import ctypes

    class _MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_uint64),
            ("ullAvailPhys", ctypes.c_uint64),
            ("ullTotalPageFile", ctypes.c_uint64),
            ("ullAvailPageFile", ctypes.c_uint64),
            ("ullTotalVirtual", ctypes.c_uint64),
            ("ullAvailVirtual", ctypes.c_uint64),
            ("ullAvailExtendedVirtual", ctypes.c_uint64),
        ]

    status = _MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(_MEMORYSTATUSEX)
    windll: Any = getattr(ctypes, "windll", None)
    kernel32 = windll.kernel32
    if not kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return MemoryStatusSnapshot(
        ull_total_phys=status.ullTotalPhys,
        ull_avail_phys=status.ullAvailPhys,
        ull_total_pagefile=status.ullTotalPageFile,
        ull_avail_pagefile=status.ullAvailPageFile,
        dw_memory_load=status.dwMemoryLoad,
    )


def _win_process_memory_counters(pid: int) -> ProcessMemorySnapshot:
    """Real collector: OpenProcess + psapi!GetProcessMemoryInfo."""
    import ctypes

    class _PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong),
            ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
            ("PrivateUsage", ctypes.c_size_t),
        ]

    windll: Any = getattr(ctypes, "windll", None)
    kernel32 = windll.kernel32
    handle = kernel32.OpenProcess(
        _PROCESS_QUERY_INFORMATION | _PROCESS_VM_READ, False, pid
    )
    if not handle:
        raise OSError(f"OpenProcess failed for pid {pid}")
    try:
        counters = _PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(_PROCESS_MEMORY_COUNTERS_EX)
        psapi = windll.psapi
        ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
        if not ok:
            raise OSError(f"GetProcessMemoryInfo failed for pid {pid}")
        return ProcessMemorySnapshot(
            working_set_size=counters.WorkingSetSize,
            peak_working_set_size=counters.PeakWorkingSetSize,
            page_file_usage=counters.PagefileUsage,
            private_usage=counters.PrivateUsage,
            page_fault_count=counters.PageFaultCount,
        )
    finally:
        kernel32.CloseHandle(handle)


def _default_system_collector() -> Callable[[], MemoryStatusSnapshot]:
    if sys.platform.startswith("win"):
        return _win_global_memory_status
    return _off_platform_system_collector


def _off_platform_system_collector() -> MemoryStatusSnapshot:
    raise SamplingError(
        "Windows system collection requires win32; inject a collector for tests",
        code="measurement.windows_off_platform",
    )


def _default_process_collector() -> Callable[[int], ProcessMemorySnapshot]:
    if sys.platform.startswith("win"):
        return _win_process_memory_counters
    return _off_platform_process_collector


def _off_platform_process_collector(pid: int) -> ProcessMemorySnapshot:
    raise SamplingError(
        f"Windows process collection requires win32 for pid {pid}; "
        "inject a collector for tests",
        code="measurement.windows_off_platform",
    )


@dataclass(frozen=True, slots=True)
class WindowsSamplerOptions:
    query_system_memory: Callable[[], MemoryStatusSnapshot] = field(
        default_factory=_default_system_collector
    )
    query_process_memory: Callable[[int], ProcessMemorySnapshot] = field(
        default_factory=_default_process_collector
    )
    core_pids: Sequence[int] = field(default_factory=tuple)
    tool_pids: Sequence[int] = field(default_factory=tuple)


class WindowsPlatformSampler:
    """Implements PlatformSampler for Windows x86_64 qualification lanes."""

    def __init__(self, options: WindowsSamplerOptions | None = None) -> None:
        self._options = options or WindowsSamplerOptions()

    def platform_family(self) -> str:
        return "windows"

    def page_size_bytes(self) -> int:
        return 4096

    def sample_process_tree(self, scope: MemoryScope) -> ProcessTreeSample:
        opts = self._options
        if scope is MemoryScope.WHOLE_SYSTEM_PRESSURE:
            raise SamplingError(
                "use sample_system_memory for whole-system pressure",
                code="measurement.wrong_scope",
            )
        pids = list(dict.fromkeys([*opts.core_pids, *opts.tool_pids]))
        if not pids:
            note = f"no processes attributed to {scope.value}"
            return ProcessTreeSample(
                scope=scope,
                process_count=0,
                rss_bytes=unavailable("rss_bytes", note=note),
                peak_rss_bytes=unavailable("peak_rss_bytes", note=note),
                private_bytes=unavailable("private_bytes", note=note),
                swap_used_bytes=unavailable("pagefile_backing_bytes", note=note),
            )

        ws_total = private_total = pagefile_used = 0
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
            private_total += counters.private_usage
            pagefile_used += counters.page_file_usage
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_metric("rss_bytes", ws_total),
            # Peak working sets are independent lifetime high-water marks;
            # summing them overstates concurrent tree peak, so tree peak is
            # withheld rather than fabricated.
            peak_rss_bytes=unavailable(
                "peak_rss_bytes",
                note=(
                    "true concurrent tree peak requires harness-side sampling; "
                    "summing per-process lifetime peaks would overstate demand"
                ),
            ),
            private_bytes=_metric("private_bytes", private_total),
            swap_used_bytes=_metric("pagefile_backing_bytes", pagefile_used),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        status = self._options.query_system_memory()
        notes = (
            "MEMORYSTATUSEX pagefile fields are the system COMMIT limit/charge; "
            "reported under commit identities while swap stays UNSUPPORTED",
            "memory pressure classification not derivable from dwMemoryLoad "
            "percent under MSTR-MEASURE-v0; left UNKNOWN rather than mapped",
        )
        return SystemMemorySample(
            total_bytes=_metric("total_bytes", status.ull_total_phys),
            available_bytes=_metric("available_bytes", status.ull_avail_phys),
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=unavailable(
                "swap_configured_bytes",
                unsupported=True,
                note=(
                    "pagefile capacity requires GetPerformanceInfo/WMI; "
                    "commit limit reported under commit_limit_bytes instead"
                ),
            ),
            swap_used_bytes=unavailable(
                "swap_used_bytes",
                unsupported=True,
                note=(
                    "pagefile usage requires GetPerformanceInfo/WMI; "
                    "commit charge reported under commit_charge_bytes instead"
                ),
            ),
            major_page_faults_total=unavailable(
                "major_page_faults_total",
                unsupported=True,
                note="hard-fault deltas require ETW tracing; PageFaultCount is total faults only",
            ),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=notes,
            extra_metrics=(
                _metric("commit_limit_bytes", status.ull_total_pagefile),
                _metric(
                    "commit_charge_bytes",
                    status.ull_total_pagefile - status.ull_avail_pagefile,
                ),
                SampledMetric(
                    name="memory_load_percent",
                    availability=MetricAvailability.AVAILABLE,
                    value=status.dw_memory_load,
                    unit="percent",
                    note="raw counter; NOT an MSTR-MEASURE-v0 pressure state",
                ),
            ),
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
