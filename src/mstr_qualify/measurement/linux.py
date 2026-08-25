"""Linux memory/paging sampler using /proc (local reads only).

Raw kernel counters map to MSTR-MEASURE-v0 metric identities honestly:
VmRSS maps to RSS; RssAnon keeps its own identity (never equated to
private bytes); a missing /proc field makes the aggregate unavailable
instead of becoming an invented zero; per-process lifetime HWM sums are
NOT reported as tree peak (processes do not peak concurrently).
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


_TRACKED_FIELDS = ("VmRSS", "VmHWM", "VmSwap", "RssAnon")


class LinuxPlatformSampler:
    """Implements PlatformSampler for Linux x86_64 qualification lanes."""

    def __init__(self, options: LinuxSamplerOptions | None = None) -> None:
        self._options = options or LinuxSamplerOptions()

    def platform_family(self) -> str:
        return "linux"

    def page_size_bytes(self) -> int:
        return self._options.page_size_bytes

    def _pids_for(self, scope: MemoryScope) -> list[int]:
        opts = self._options
        if scope is MemoryScope.MSTR_CORE_TREE:
            pids: list[int] = list(opts.core_pids)
        elif scope is MemoryScope.TASK_TOOL_TREE:
            pids = list(opts.tool_pids)
        else:
            pids = [*opts.core_pids, *opts.tool_pids]
        # Ordered dedupe so overlapping attribution is never double-counted.
        return list(dict.fromkeys(pids))

    def sample_process_tree(self, scope: MemoryScope) -> ProcessTreeSample:
        if scope is MemoryScope.WHOLE_SYSTEM_PRESSURE:
            raise SamplingError(
                "use sample_system_memory for whole-system pressure",
                code="measurement.wrong_scope",
            )
        pids = self._pids_for(scope)
        if not pids:
            note = f"no processes attributed to {scope.value}"
            return ProcessTreeSample(
                scope=scope,
                process_count=0,
                rss_bytes=unavailable("rss_bytes", note=note),
                peak_rss_bytes=unavailable("peak_rss_bytes", note=note),
                private_bytes=unavailable("rss_anon_bytes", note=note),
                swap_used_bytes=unavailable("swap_used_bytes", note=note),
            )

        totals_kb: dict[str, int] = dict.fromkeys(_TRACKED_FIELDS, 0)
        complete: dict[str, bool] = dict.fromkeys(_TRACKED_FIELDS, True)
        for pid in pids:
            status = parse_proc_status_kv(self._options.proc_reader(f"/proc/{pid}/status"))
            for name in _TRACKED_FIELDS:
                value_kb = status.get(name)
                if value_kb is None:
                    complete[name] = False
                else:
                    totals_kb[name] += value_kb
        return ProcessTreeSample(
            scope=scope,
            process_count=len(pids),
            rss_bytes=_conditional_metric("rss_bytes", "VmRSS", totals_kb, complete),
            peak_rss_bytes=unavailable(
                "peak_rss_bytes",
                note=(
                    "true concurrent tree peak requires harness-side sampling; "
                    "summing per-process VmHWM high-water marks would "
                    "overstate demand and is not reported"
                ),
            ),
            private_bytes=SampledMetric(
                name="rss_anon_bytes",
                availability=(
                    MetricAvailability.AVAILABLE
                    if complete["RssAnon"]
                    else MetricAvailability.UNAVAILABLE
                ),
                value=None if not complete["RssAnon"] else totals_kb["RssAnon"] * _KB,
                unit="bytes" if complete["RssAnon"] else None,
                note="RssAnon (anonymous resident); distinct from private working set"
                if complete["RssAnon"]
                else "RssAnon missing for at least one sampled process",
            ),
            swap_used_bytes=_conditional_metric("swap_used_bytes", "VmSwap", totals_kb, complete),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        reader = self._options.proc_reader
        meminfo = parse_meminfo(reader("/proc/meminfo"))
        total_kb = meminfo.get("MemTotal")
        available_kb = meminfo.get("MemAvailable")
        swap_total_kb = meminfo.get("SwapTotal")
        swap_free_kb = meminfo.get("SwapFree")

        extras: list[SampledMetric] = []
        notes = ["pressure classification requires PSI thresholds frozen by a later task"]
        try:
            swap_io = parse_vmstat_swap_io(
                reader("/proc/vmstat"),
                page_size_bytes=self._options.page_size_bytes,
            )
        except OSError:
            notes.append("/proc/vmstat unavailable; cumulative swap I/O not reported")
        else:
            if "pswpin" in swap_io:
                extras.append(_bytes_metric("swap_in_total_bytes", swap_io["pswpin"]))
            if "pswpout" in swap_io:
                extras.append(_bytes_metric("swap_out_total_bytes", swap_io["pswpout"]))

        return SystemMemorySample(
            total_bytes=_kb_opt_or_unavailable("total_bytes", total_kb),
            available_bytes=_kb_opt_or_unavailable("available_bytes", available_kb),
            minimum_available_bytes_observed=unavailable(
                "minimum_available_bytes_observed",
                note="requires harness-side minimum tracking across samples",
            ),
            swap_configured_bytes=_kb_opt_or_unavailable("swap_configured_bytes", swap_total_kb),
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
            extra_metrics=tuple(extras),
        )


def _conditional_metric(
    metric_name: str,
    field_name: str,
    totals_kb: dict[str, int],
    complete: dict[str, bool],
) -> SampledMetric:
    """Aggregate only when every sampled process exposed the raw field."""
    if complete[field_name]:
        return _bytes_metric(metric_name, totals_kb[field_name] * _KB)
    return unavailable(
        metric_name,
        note=f"{field_name} missing for at least one sampled process; aggregate withheld",
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


def _kb_opt_or_unavailable(name: str, kb: int | None) -> SampledMetric:
    return _or_unavailable(name, _kb_opt(name, kb))


def create_sampler(options: LinuxSamplerOptions | None = None) -> LinuxPlatformSampler:
    """Factory used by host detection helpers and tests."""
    return LinuxPlatformSampler(options)
