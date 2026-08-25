"""macOS memory/paging sampler via Mach/proc APIs (local reads only).

Raw API concepts keep their own identities: ri_resident_size maps to RSS,
ri_phys_footprint is reported as footprint (macOS-specific identity, not
equated to Windows private bytes), and macOS pressure levels are not
synthesized here. All collectors are injected for OS-independent tests.
"""

from __future__ import annotations

import re
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

Collector = Callable[[int], "FakeProcRusage"]
HostStatsCollector = Callable[[], "FakeVmStatistics"]
SwapUsageCollector = Callable[[], str]


@dataclass(frozen=True, slots=True)
class FakeProcRusage:
    """Test double mirroring rusage_info_v4 field names (bytes)."""

    ri_resident_size: int
    ri_phys_footprint: int
    ri_pageins: int


@dataclass(frozen=True, slots=True)
class FakeVmStatistics:
    """Test double mirroring vm_statistics64 page counts."""

    free_pages: int
    active_pages: int
    inactive_pages: int
    wired_pages: int
    compressed_pages: int
    pageins: int
    pageouts: int


def _macos_proc_pid_rusage(pid: int) -> FakeProcRusage:
    raise SamplingError(
        f"real macOS collection requires libproc for pid {pid}",
        code="measurement.macos_collector_missing",
    )


def _macos_host_vm_statistics() -> FakeVmStatistics:
    raise SamplingError(
        "real macOS collection requires mach host_statistics64",
        code="measurement.macos_collector_missing",
    )


def _macos_read_swap_usage() -> str:
    raise SamplingError(
        "real macOS swap reading requires sysctl kern.vm_swapusage",
        code="measurement.macos_collector_missing",
    )


def _default_page_size() -> int:
    return 4096


def parse_swap_usage_text(text: str) -> tuple[int | None, int | None]:
    """Parse ``total = X used = Y free = Z`` byte triple from vm_swapusage."""
    numbers = re.findall(r"(?:total|used|free)\s*=\s*(\d+)", text)
    if len(numbers) < 3:
        return None, None
    total_b = int(numbers[0])
    used_b = int(numbers[1])
    return total_b, used_b


@dataclass(frozen=True, slots=True)
class MacOSSamplerOptions:
    proc_rusage: Callable[[int], FakeProcRusage] = _macos_proc_pid_rusage
    host_vm_statistics: HostStatsCollector = _macos_host_vm_statistics
    read_swap_usage: SwapUsageCollector = _macos_read_swap_usage
    core_pids: Sequence[int] = field(default_factory=tuple)
    tool_pids: Sequence[int] = field(default_factory=tuple)
    page_size_bytes: int = 4096

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
                peak_rss_bytes=unavailable(
                    "peak_rss_bytes",
                    unsupported=True,
                    note="no peak resident counter exposed by proc_pid_rusage",
                ),
                private_bytes=unavailable("private_bytes", note=note),
                swap_used_bytes=unavailable("swap_used_bytes", note=note),
            )
        rss_total = footprint_total = 0
        for pid in pids:
            rusage = opts.proc_rusage(pid)
            rss_total += rusage.ri_resident_size
            footprint_total += rusage.ri_phys_footprint
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_bytes_metric("rss_bytes", rss_total),
            peak_rss_bytes=unavailable(
                "peak_rss_bytes",
                unsupported=True,
                note="proc_pid_rusage exposes current resident size only",
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
            swap_total, swap_used = parse_swap_usage_text(opts.read_swap_usage())
        except (SamplingError, OSError):
            swap_total = swap_used = None
        # Apple-style availability estimate (free + inactive); labeled as an
        # estimate because macOS has no single authoritative counter.
        available = SampledMetric(
            name="available_bytes",
            availability=MetricAvailability.AVAILABLE,
            value=free_estimate,
            unit="bytes",
            note="estimate = (free + inactive) pages * page_size; macOS method",
        )
        return SystemMemorySample(
            total_bytes=_bytes_metric("total_bytes", _sum_all_pages(stats) * page),
            available_bytes=available,
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=_or_unavailable(
                "swap_configured_bytes",
                None if swap_total is None else _bytes_metric(
                    "swap_configured_bytes", swap_total
                ),
            ),
            swap_used_bytes=_or_unavailable(
                "swap_used_bytes",
                None if swap_used is None else _bytes_metric("swap_used_bytes", swap_used),
                note="vm_swapusage unavailable",
            ),
            major_page_faults_total=unavailable(
                "major_page_faults_total",
                unsupported=True,
                note=(
                    "host_statistics64 pageins are not major-fault counts "
                    "per se; identity preserved rather than relabeled"
                ),
            ),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=(
                "kern.memorystatus pressure level requires notification "
                "machinery; left UNKNOWN",
            ),
        )


def _or_unavailable(
    name: str,
    metric: SampledMetric | None,
    note: str = "not exposed by this host",
) -> SampledMetric:
    return metric if metric is not None else unavailable(name, note=note)


def _sum_all_pages(stats: FakeVmStatistics) -> int:
    return (
        stats.free_pages
        + stats.active_pages
        + stats.inactive_pages
        + stats.wired_pages
        + stats.compressed_pages
    )


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
