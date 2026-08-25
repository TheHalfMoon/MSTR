"""Unit tests for the Linux sampler (mocked /proc data; no Linux required)."""

from __future__ import annotations

import pytest

from mstr_qualify.measurement.linux import (
    LinuxPlatformSampler,
    LinuxSamplerOptions,
    parse_meminfo,
    parse_proc_status_kv,
    parse_vmstat_swap_io,
)
from mstr_qualify.measurement.platform import (
    MemoryScope,
    MetricAvailability,
    SystemMemoryPressure,
)

STATUS_TEMPLATE = """Name:\tproc-{pid}
VmRSS:\t{rss} kB
VmHWM:\t{hwm} kB
VmSwap:\t{swap} kB
RssAnon:\t{anon} kB
"""

MEMINFO = """MemTotal:       8167300 kB
MemFree:         512000 kB
MemAvailable:   3200000 kB
Buffers:         128000 kB
Cached:         1800000 kB
SwapTotal:      2097148 kB
SwapFree:       1048574 kB
"""

VMSTAT = """pswpin 1200
pswpout 3400
someother 99
"""


def _reader_factory(status_by_pid: dict[int, dict[str, int]]):
    def reader(path: str) -> str:
        if path == "/proc/meminfo":
            return MEMINFO
        if path == "/proc/vmstat":
            return VMSTAT
        if path.startswith("/proc/") and path.endswith("/status"):
            pid = int(path.split("/")[2])
            fields = status_by_pid.get(pid)
            if fields is None:
                raise FileNotFoundError(path)
            return STATUS_TEMPLATE.format(pid=pid, **fields)  # type: ignore[arg-type]
        raise FileNotFoundError(path)

    return reader


def _fields(rss: int, hwm: int, swap: int, anon: int) -> dict[str, int]:
    return {"rss": rss, "hwm": hwm, "swap": swap, "anon": anon}


def _sampler(
    status_by_pid: dict[int, dict[str, int]],
    core: tuple[int, ...] = (1,),
    tool: tuple[int, ...] = (),
) -> LinuxPlatformSampler:
    options = LinuxSamplerOptions(
        proc_reader=_reader_factory(status_by_pid),
        core_pids=core,
        tool_pids=tool,
        page_size_bytes=4096,
    )
    return LinuxPlatformSampler(options)


class TestParsers:
    def test_status_kv_parses_kb_fields(self) -> None:
        values = parse_proc_status_kv("VmRSS:\t1234 kB\nState:\tS (sleeping)\nVmHWM: 999 kB\n")
        assert values == {"VmRSS": 1234, "VmHWM": 999}

    def test_meminfo_parses_wanted_fields_only(self) -> None:
        values = parse_meminfo(MEMINFO)
        assert values["MemTotal"] == 8167300
        assert "Cached" not in values

    def test_vmstat_swap_io_multiplies_page_size(self) -> None:
        io = parse_vmstat_swap_io(VMSTAT, page_size_bytes=4096)
        assert io["pswpin"] == 1200 * 4 * 1024
        assert io["pswpout"] == 3400 * 4 * 1024


class TestProcessTreeSampling:
    def test_core_tree_aggregates_rss_and_swap_peak_withheld(self) -> None:
        sampler = _sampler(
            {
                10: _fields(100_000, 150_000, 5_000, 60_000),
                11: _fields(200_000, 250_000, 3_000, 70_000),
            },
            core=(10, 11),
        )
        sample = sampler.sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        assert sample.scope is MemoryScope.MSTR_CORE_TREE
        assert sample.process_count == 2
        assert sample.rss_bytes.value == (300_000 * 1024)
        assert sample.swap_used_bytes.value == (8_000 * 1024)
        assert sample.private_bytes.name == "rss_anon_bytes"
        assert sample.peak_rss_bytes.availability is MetricAvailability.UNAVAILABLE
        assert "overstate" in (sample.peak_rss_bytes.note or "")
        note = sample.private_bytes.note
        assert note is not None and "distinct from private working set" in note

    def test_tool_tree_and_total_tree_are_distinct_scopes(self) -> None:
        sampler = _sampler(
            {20: _fields(50_000, 50_000, 0, 10_000)},
            core=(20,),
            tool=(),
        )
        core = sampler.sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        tool = sampler.sample_process_tree(MemoryScope.TASK_TOOL_TREE)
        total = sampler.sample_process_tree(MemoryScope.TOTAL_AGENT_TREE)
        assert core.process_count == 1
        assert tool.process_count == 0
        assert total.process_count == 1
        assert tool.rss_bytes.availability is MetricAvailability.UNAVAILABLE
        assert total.rss_bytes.value == core.rss_bytes.value

    def test_empty_scope_reports_unavailable_not_zero(self) -> None:
        sampler = _sampler({}, core=(), tool=())
        sample = sampler.sample_process_tree(MemoryScope.TASK_TOOL_TREE)
        assert sample.rss_bytes.value is None
        assert sample.rss_bytes.availability is MetricAvailability.UNAVAILABLE


class TestSystemSampling:
    def test_vmstat_swap_io_surfaces_in_extras(self) -> None:
        sample = _sampler({}).sample_system_memory()
        extras = {m.name: m for m in sample.extra_metrics}
        assert extras["swap_in_total_bytes"].value == 1200 * 4 * 1024
        assert extras["swap_out_total_bytes"].value == 3400 * 4 * 1024

    def test_system_memory_from_meminfo(self) -> None:
        sample = _sampler({}).sample_system_memory()
        assert sample.total_bytes.value == 8_167_300 * 1024
        assert sample.available_bytes.value == 3_200_000 * 1024
        assert sample.swap_configured_bytes.value == 2_097_148 * 1024
        swap_delta_kb = 2_097_148 - 1_048_574
        assert sample.swap_used_bytes.value == swap_delta_kb * 1024

    def test_pressure_left_unknown_with_note(self) -> None:
        sample = _sampler({}).sample_system_memory()
        assert sample.pressure_state is SystemMemoryPressure.UNKNOWN
        assert any("PSI" in note for note in sample.notes)

    def test_minimum_available_tracked_harness_side_is_unavailable(self) -> None:
        sample = _sampler({}).sample_system_memory()
        observed = sample.minimum_available_bytes_observed
        assert observed.availability is MetricAvailability.UNAVAILABLE


def test_invalid_page_size_rejected() -> None:
    with pytest.raises(Exception, match="page_size"):
        LinuxSamplerOptions(page_size_bytes=0)
