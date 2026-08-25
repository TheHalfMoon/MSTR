"""Linux memory/paging sampler using /proc (local reads only).

Raw kernel counters map to MSTR-MEASURE-v0 metric identities honestly:
VmRSS/VmHWM map to RSS/peak RSS, RssAnon keeps its own metric identity
(never silently equated to "private bytes"), and metrics the OS does not
expose are marked UNAVAILABLE/UNSUPPORTED rather than invented.

All data sources are injected so unit tests run on any development OS.
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

ProcReader = Callable[[str], str]


def _read_local(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


_KB = 1024
_STATUS_LINE = re.compile(r"^([A-Za-z]+):\s+(\d+)\s+kB\s*$")
_MEMINFO_FIELDS = ("MemTotal", "MemAvailable", "MemFree", "SwapTotal", "SwapFree")


def parse_proc_status_kv(text: str) -> dict[str, int]:
    """Parse ``Field: <n> kB`` lines from /proc/<pid>/status into kilobytes."""
    values: dict[str, int] = {}
    for line in text.splitlines():
        match = _STATUS_LINE.match(line)
        if match:
            values[match.group(1)] = int(match.group(2))
    return values


def parse_meminfo(text: str) -> dict[str, int]:
    """Parse MemTotal/MemAvailable/MemFree/SwapTotal/SwapFree (kB)."""
    values: dict[str, int] = {}
    for line in text.splitlines():
        match = _STATUS_LINE.match(line)
        if match and match.group(1) in _MEMINFO_FIELDS:
            values[match.group(1)] = int(match.group(2))
    return values


def parse_vmstat_swap_io(text: str, *, page_size_bytes: int) -> dict[str, int]:
    """Extract cumulative pswpin/pswpout as byte totals from /proc/vmstat."""
    pages: dict[str, int] = {}
    for line in text.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] in ("pswpin", "pswpout"):
            pages[fields[0]] = int(fields[1])
    factor_kb = max(page_size_bytes // _KB, 1)
    return {name: count * factor_kb * _KB for name, count in pages.items()}


@dataclass(frozen=True, slots=True)
class LinuxSamplerOptions:
    """Injected data sources; defaults read real local files."""

    proc_reader: ProcReader = _read_local
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


class LinuxPlatformSampler:
    """Implements PlatformSampler for Linux x86_64 qualification lanes."""

    def __init__(self, options: LinuxSamplerOptions | None = None) -> None:
        self._options = options or LinuxSamplerOptions()

    def platform_family(self) -> str:
        return "linux"

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

        rss_total = peak_total = swap_total = anon_total = 0
        seen_any = False
        for pid in pids:
            status = parse_proc_status_kv(self._options.proc_reader(f"/proc/{pid}/status"))
            seen_any = True
            rss_total += status.get("VmRSS", 0) * _KB
            peak_total += max(status.get("VmHWM", 0), status.get("VmRSS", 0)) * _KB
            swap_total += status.get("VmSwap", 0) * _KB
            anon_total += status.get("RssAnon", 0) * _KB
        if not seen_any:
            note = f"no processes attributed to {scope.value}"
            return ProcessTreeSample(
                scope=scope,
                process_count=0,
                rss_bytes=unavailable("rss_bytes", note=note),
                peak_rss_bytes=unavailable("peak_rss_bytes", note=note),
                private_bytes=unavailable("private_bytes"),
                swap_used_bytes=unavailable("swap_used_bytes", note=note),
            )
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_bytes_metric("rss_bytes", rss_total),
            peak_rss_bytes=_bytes_metric("peak_rss_bytes", peak_total),
            # RssAnon is anonymous resident memory — a related but distinct
            # concept from Windows private working set; identity preserved.
            private_bytes=SampledMetric(
                name="rss_anon_bytes",
                availability=MetricAvailability.AVAILABLE,
                value=anon_total,
                unit="bytes",
                note="RssAnon (anonymous resident); not equivalent to private working set",
            ),
            swap_used_bytes=_bytes_metric("swap_used_bytes", swap_total),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        reader = self._options.proc_reader
        meminfo = parse_meminfo(reader("/proc/meminfo"))
        total_kb = meminfo.get("MemTotal")
        available_kb = meminfo.get("MemAvailable")
        swap_total_kb = meminfo.get("SwapTotal")
        swap_free_kb = meminfo.get("SwapFree")

        notes = ["pressure classification requires PSI thresholds frozen by a later task"]
        try:
            parse_vmstat_swap_io(
                reader("/proc/vmstat"),
                page_size_bytes=self._options.page_size_bytes,
            )
            vmstat_ok = True
        except OSError:
            vmstat_ok = False
            notes.append("/proc/vmstat unavailable; cumulative swap I/O not reported")
        del vmstat_ok

        return SystemMemorySample(
            total_bytes=_or_unavailable(
                "total_bytes", _kb_opt("total_bytes", total_kb)
            ),
            available_bytes=_or_unavailable(
                "available_bytes", _kb_opt("available_bytes", available_kb)
            ),
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=_or_unavailable(
                "swap_configured_bytes",
                _kb_opt("swap_configured_bytes", swap_total_kb),
            ),
            swap_used_bytes=_or_unavailable(
                "swap_used_bytes",
                None
                if (swap_total_kb is None or swap_free_kb is None)
                else _bytes_metric("swap_used_bytes", (swap_total_kb - swap_free_kb) * _KB),
                note="SwapTotal/SwapFree not both exposed",
            ),
            major_page_faults_total=unavailable(
                "major_page_faults_total",
                unsupported=True,
                note=(
                    "per-tree counters belong to task-tool consumers; "
                    "no single system-wide counter exposed here"
                ),
            ),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=tuple(notes),
        )


def _or_unavailable(
    name: str,
    metric: SampledMetric | None,
    note: str = "not exposed by this host",
) -> SampledMetric:
    return metric if metric is not None else unavailable(name, note=note)


def _bytes_metric(name: str, value_bytes: int) -> SampledMetric:
    return SampledMetric(
        name=name,
        availability=MetricAvailability.AVAILABLE,
        value=value_bytes,
        unit="bytes",
    )


def _kb_opt(name: str, kb: int | None) -> SampledMetric | None:
    return None if kb is None else _bytes_metric(name, kb * _KB)


def create_sampler(options: LinuxSamplerOptions | None = None) -> LinuxPlatformSampler:
    """Factory used by host detection helpers and tests."""
    return LinuxPlatformSampler(options)
