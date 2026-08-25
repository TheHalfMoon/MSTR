"""macOS memory/paging sampler via Mach/proc/sysctl APIs (local only).

Identity discipline: ri_resident_size maps to RSS; ri_phys_footprint keeps
its own identity (never equated to Windows private bytes); total physical
RAM comes from hw.memsize, never from summing page classes; the default
page size is queried from the host. Real collectors run only on darwin;
tests inject doubles.
"""

from __future__ import annotations

import os
import re
import sys
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

_RUSAGE_INFO_V4 = 5


@dataclass(frozen=True, slots=True)
class ProcRusageSnapshot:
    """Snapshot mirroring rusage_info_v4 fields used by this sampler."""

    ri_resident_size: int
    ri_phys_footprint: int
    ri_pageins: int


@dataclass(frozen=True, slots=True)
class VmStatisticsSnapshot:
    """Snapshot mirroring vm_statistics64 page counts."""

    free_pages: int
    active_pages: int
    inactive_pages: int
    wired_pages: int
    compressed_pages: int
    pageins: int
    pageouts: int


def _darwin_proc_pid_rusage(pid: int) -> ProcRusageSnapshot:
    """Real collector: libproc!proc_pid_rusage with rusage_info_v4 layout."""
    import ctypes

    class _RUUSAGE_INFO_V4(ctypes.Structure):
        _fields_ = [
            ("ri_uuid", ctypes.c_uint8 * 16),
            ("ri_user_time", ctypes.c_uint64),
            ("ri_system_time", ctypes.c_uint64),
            ("ri_pkg_idle_wkups", ctypes.c_uint32),
            ("ri_interrupt_wkups", ctypes.c_uint32),
            ("ri_pageins", ctypes.c_uint32),
            ("ri_wired_size", ctypes.c_uint64),
            ("ri_resident_size", ctypes.c_uint64),
            ("ri_phys_footprint", ctypes.c_uint64),
            ("ri_released_footprint", ctypes.c_uint64),
            ("ri_logical_writes", ctypes.c_uint64),
            ("ri_lifetime_max_phys_footprint", ctypes.c_uint64),
            ("ri_instructions", ctypes.c_uint64),
            ("ri_cycles", ctypes.c_uint64),
            ("ri_billed_system_time", ctypes.c_uint64),
            ("ri_unbilled_system_time", ctypes.c_uint64),
            ("ri_page_faults", ctypes.c_uint64),
        ]

    libc = ctypes.CDLL(None)
    info = _RUUSAGE_INFO_V4()
    info_ptr = ctypes.cast(ctypes.pointer(info), ctypes.c_void_p)
    ok = libc.proc_pid_rusage(ctypes.c_int(pid), _RUSAGE_INFO_V4, ctypes.byref(info_ptr))
    if ok != 0:
        raise OSError(f"proc_pid_rusage failed for pid {pid}")
    return ProcRusageSnapshot(
        ri_resident_size=info.ri_resident_size,
        ri_phys_footprint=info.ri_phys_footprint,
        ri_pageins=info.ri_pageins,
    )


_VM_STATS64_FIELDS = (
    "free_count",
    "active_count",
    "inactive_count",
    "wire_count",
    "zero_fill_count",
    "reactivations",
    "pageins",
    "pageouts",
    "faults",
    "cow_faults",
    "lookups",
    "hits",
    "purges",
    "purgeable_count",
    "speculative_count",
    "decompressions",
    "compressions",
    "swapins",
    "swapouts",
    "compressor_page_count",
    "throttled_count",
    "error_count",
)
HOST_VM_INFO64 = 4  # per <mach/host_info.h>


def _darwin_host_vm_statistics() -> VmStatisticsSnapshot:
    """Real collector: mach host_statistics64(HOST_VM_INFO64)."""
    import ctypes

    class _VM_STATISTICS64(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint32) for name in _VM_STATS64_FIELDS]

    libc = ctypes.CDLL(None)
    if libc.mach_host_self.restype is None:
        libc.mach_host_self.restype = ctypes.c_uint32
    host = libc.mach_host_self()

    stats = _VM_STATISTICS64()
    count_out = ctypes.c_uint32(len(_VM_STATS64_FIELDS))
    kern = libc.host_statistics64(
        host, HOST_VM_INFO64, ctypes.byref(stats), ctypes.byref(count_out)
    )
    if kern != 0:
        raise OSError(f"host_statistics64 failed with kern={kern}")
    return VmStatisticsSnapshot(
        free_pages=stats.free_count,
        active_pages=stats.active_count,
        inactive_pages=stats.inactive_count,
        wired_pages=stats.wire_count,
        compressed_pages=stats.compressor_page_count,
        pageins=stats.pageins,
        pageouts=stats.pageouts,
    )


def _sysctl_string(name: str) -> str | None:
    """Read a string sysctl via sysctlbyname (e.g. vm.swapusage)."""
    import ctypes

    libc = ctypes.CDLL(None)
    size = ctypes.c_size_t(0)
    if libc.sysctlbyname(name.encode(), None, ctypes.byref(size), None, 0) != 0:
        return None
    buffer = ctypes.create_string_buffer(size.value)
    if libc.sysctlbyname(name.encode(), buffer, ctypes.byref(size), None, 0) != 0:
        return None
    return buffer.value.decode("utf-8", errors="replace")


def _sysctl_uint64(name: str) -> int | None:
    raw = _sysctl_string_raw_bytes(name)
    if raw is None or len(raw) != 8:
        return None
    import struct

    unpacked: int | None = struct.unpack("<Q", raw)[0]
    return unpacked


def _sysctl_string_raw_bytes(name: str) -> bytes | None:
    import ctypes

    libc = ctypes.CDLL(None)
    size = ctypes.c_size_t(0)
    if libc.sysctlbyname(name.encode(), None, ctypes.byref(size), None, 0) != 0:
        return None
    buffer = ctypes.create_string_buffer(size.value)
    if libc.sysctlbyname(name.encode(), buffer, ctypes.byref(size), None, 0) != 0:
        return None
    return buffer.raw[: size.value]


def _default_total_memory_collector() -> Callable[[], int]:
    if sys.platform == "darwin":
        return lambda: _require_int(_sysctl_uint64("hw.memsize"), "hw.memsize")
    return _off_platform_total_memory


def _off_platform_total_memory() -> int:
    raise SamplingError(
        "macOS total-memory collection requires darwin sysctls; inject a collector for tests",
        code="measurement.macos_off_platform",
    )


def _require_int(value: int | None, what: str) -> int:
    if value is None:
        raise SamplingError(
            f"unable to read {what}",
            code="measurement.macos_sysctl_missing",
            details={"source": what},
        )
    return value


def _host_page_size() -> int:
    try:
        value = os.sysconf("SC_PAGE_SIZE")  # POSIX hosts incl. darwin/linux
        if isinstance(value, int) and value > 0:
            return value
    except (ValueError, OSError):
        pass
    # Apple Silicon reference lane assumption when host query unavailable.
    return 16384


def _off_platform_proc_rusage(pid: int) -> ProcRusageSnapshot:
    raise SamplingError(
        f"macOS process collection requires darwin for pid {pid}; inject a collector for tests",
        code="measurement.macos_off_platform",
    )


def _off_platform_vm_stats() -> VmStatisticsSnapshot:
    raise SamplingError(
        "macOS VM-statistics collection requires darwin mach calls; "
        "inject a collector for tests",
        code="measurement.macos_off_platform",
    )


def _off_platform_swap_usage() -> str:
    raise SamplingError(
        "macOS swap reading requires darwin sysctl vm.swapusage; inject a collector for tests",
        code="measurement.macos_off_platform",
    )


_SWAP_USAGE_LINE = re.compile(r"(?:total|used|free)\s*=\s*(\d+)")


def parse_swap_usage_text(text: str) -> tuple[int | None, int | None]:
    """Parse ``total = X used = Y free = Z`` byte triple from vm_swapusage."""
    numbers = _SWAP_USAGE_LINE.findall(text)
    if len(numbers) < 3:
        return None, None
    total_b = int(numbers[0])
    used_b = int(numbers[1])
    return total_b, used_b


def _default_proc_rusage() -> Callable[[int], ProcRusageSnapshot]:
    return _darwin_proc_pid_rusage if sys.platform == "darwin" else _off_platform_proc_rusage


def _default_vm_statistics() -> Callable[[], VmStatisticsSnapshot]:
    return _darwin_host_vm_statistics if sys.platform == "darwin" else _off_platform_vm_stats


def _default_swap_reader() -> Callable[[], str]:
    return _read_swap_usage_darwin if sys.platform == "darwin" else _off_platform_swap_usage


def _read_swap_usage_darwin() -> str:
    text = _sysctl_string("vm.swapusage")
    if text is None:
        raise SamplingError(
            "vm.swapusage unavailable",
            code="measurement.macos_sysctl_missing",
            details={"source": "vm.swapusage"},
        )
    return text


@dataclass(frozen=True, slots=True)
class MacOSSamplerOptions:
    proc_rusage: Callable[[int], ProcRusageSnapshot] = field(
        default_factory=_default_proc_rusage
    )
    host_vm_statistics: Callable[[], VmStatisticsSnapshot] = field(
        default_factory=_default_vm_statistics
    )
    read_swap_usage: Callable[[], str] = field(default_factory=_default_swap_reader)
    total_physical_bytes: Callable[[], int] = field(
        default_factory=_default_total_memory_collector
    )
    core_pids: Sequence[int] = field(default_factory=tuple)
    tool_pids: Sequence[int] = field(default_factory=tuple)
    page_size_bytes: int = field(default_factory=_host_page_size)

    def __post_init__(self) -> None:
        if self.page_size_bytes < 1:
            raise SamplingError(
                "page_size_bytes must be positive",
                code="measurement.page_size",
                details={"page_size_bytes": self.page_size_bytes},
            )


class MacOSPlatformSampler:
    """Implements PlatformSampler for macOS arm64/M1-class qualification lanes."""

    def __init__(self, options: MacOSSamplerOptions | None = None) -> None:
        self._options = options or MacOSSamplerOptions()

    def platform_family(self) -> str:
        return "macos"

    def page_size_bytes(self) -> int:
        return self._options.page_size_bytes

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
                peak_rss_bytes=unavailable(
                    "peak_rss_bytes",
                    unsupported=True,
                    note="no peak resident counter exposed by proc_pid_rusage",
                ),
                private_bytes=unavailable("rss_anon_or_footprint_bytes", note=note),
                swap_used_bytes=unavailable("swap_used_bytes", note=note),
            )
        rss_total = footprint_total = 0
        try:
            for pid in pids:
                rusage = opts.proc_rusage(pid)
                rss_total += rusage.ri_resident_size
                footprint_total += rusage.ri_phys_footprint
        except OSError as exc:
            raise SamplingError(
                "process rusage collection failed",
                code="measurement.macos_process_query_failed",
                details={"reason": str(exc)},
            ) from exc
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_bytes_metric("rss_bytes", rss_total),
            peak_rss_bytes=unavailable(
                "peak_rss_bytes",
                unsupported=True,
                note=(
                    "true concurrent tree peak requires harness-side sampling; "
                    "proc_pid_rusage exposes current resident size only"
                ),
            ),
            private_bytes=_bytes_metric("phys_footprint_bytes", footprint_total),
            swap_used_bytes=unavailable(
                "swap_used_bytes",
                unsupported=True,
                note="per-process swap attribution not exposed by proc_pid_rusage",
            ),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        opts = self._options
        stats = opts.host_vm_statistics()
        page = opts.page_size_bytes
        free_estimate = (stats.free_pages + stats.inactive_pages) * page
        try:
            swap_text = opts.read_swap_usage()
        except (SamplingError, OSError):
            swap_total = swap_used = None
        else:
            swap_total, swap_used = parse_swap_usage_text(swap_text)
        try:
            total_bytes_value: int | None = opts.total_physical_bytes()
        except (SamplingError, OSError):
            total_bytes_value = None
        notes = (
            "kern.memorystatus pressure level requires notification machinery; left UNKNOWN",
            "host_statistics64 pageins/pageouts kept as their own identities in extras; "
            "they are not relabeled as major-fault counts",
        )
        extras = [
            SampledMetric(
                name="pageins_total",
                availability=MetricAvailability.AVAILABLE,
                value=stats.pageins,
                unit="count",
                note="raw host counter",
            ),
            SampledMetric(
                name="pageouts_total",
                availability=MetricAvailability.AVAILABLE,
                value=stats.pageouts,
                unit="count",
                note="raw host counter",
            ),
        ]
        available = SampledMetric(
            name="available_bytes",
            availability=MetricAvailability.AVAILABLE,
            value=free_estimate,
            unit="bytes",
            note="estimate = (free + inactive) pages * page_size; macOS method",
        )
        total_metric = (
            None
            if total_bytes_value is None
            else _bytes_metric("total_bytes", total_bytes_value)
        )
        return SystemMemorySample(
            total_bytes=_or_unavailable("total_bytes", total_metric),
            available_bytes=available,
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=_or_unavailable(
                "swap_configured_bytes",
                None if swap_total is None else _bytes_metric("swap_configured_bytes", swap_total),
                note="vm.swapusage unavailable",
            ),
            swap_used_bytes=_or_unavailable(
                "swap_used_bytes",
                None if swap_used is None else _bytes_metric("swap_used_bytes", swap_used),
                note="vm.swapusage unavailable",
            ),
            major_page_faults_total=unavailable(
                "major_page_faults_total",
                unsupported=True,
                note=(
                    "host_statistics64 pageins are not major-fault counts per se; "
                    "identity preserved rather than relabeled"
                ),
            ),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=notes,
            extra_metrics=tuple(extras),
        )


def _or_unavailable(
    name: str,
    metric: SampledMetric | None,
    note: str = "not exposed by this host",
) -> SampledMetric:
    return metric if metric is not None else unavailable(name, note=note)


def _bytes_metric(name: str, value: int) -> SampledMetric:
    return SampledMetric(
        name=name,
        availability=MetricAvailability.AVAILABLE,
        value=value,
        unit="bytes",
    )


def create_sampler(options: MacOSSamplerOptions | None = None) -> MacOSPlatformSampler:
    """Factory used by host detection helpers and tests."""
    return MacOSPlatformSampler(options)
