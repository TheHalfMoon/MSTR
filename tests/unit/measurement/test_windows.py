"""Unit tests for the Windows sampler (mocked collectors; no Windows needed)."""

from __future__ import annotations

import pytest

from mstr_qualify.measurement.platform import (
    MemoryScope,
    MetricAvailability,
    SystemMemoryPressure,
)
from mstr_qualify.measurement.windows import (
    ProcessMemorySnapshot,
    WindowsPlatformSampler,
    WindowsSamplerOptions,
)

_TOTAL_PHYS = 8 * 1024**3
_AVAIL_PHYS = 2 * 1024**3
_COMMIT_LIMIT = 4 * 1024**3
_AVAIL_COMMIT = 3 * 1024**3


def _system_status() -> object:
    from mstr_qualify.measurement.windows import MemoryStatusSnapshot

    return MemoryStatusSnapshot(
        ull_total_phys=_TOTAL_PHYS,
        ull_avail_phys=_AVAIL_PHYS,
        ull_total_pagefile=_COMMIT_LIMIT,
        ull_avail_pagefile=_AVAIL_COMMIT,
        dw_memory_load=75,
    )


def _counters(
    ws: int,
    peak: int,
    pagefile: int,
    private: int,
    faults: int,
) -> ProcessMemorySnapshot:
    return ProcessMemorySnapshot(
        working_set_size=ws,
        peak_working_set_size=peak,
        page_file_usage=pagefile,
        private_usage=private,
        page_fault_count=faults,
    )


def _sampler(
    core: tuple[int, ...] = (100,),
    tool: tuple[int, ...] = (200,),
) -> WindowsPlatformSampler:
    by_pid = {
        100: _counters(1_000_000, 1_500_000, 400_000, 800_000, 12_000),
        200: _counters(500_000, 700_000, 100_000, 300_000, 5_000),
    }
    options = WindowsSamplerOptions(
        query_system_memory=_system_status,
        query_process_memory=lambda pid: by_pid[pid],
        core_pids=core,
        tool_pids=tool,
    )
    return WindowsPlatformSampler(options)


class TestProcessTree:
    def test_core_tree_sums_working_set_private_and_pagefile(self) -> None:
        sample = _sampler(core=(100,), tool=()).sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        assert sample.rss_bytes.value == 1_000_000
        assert sample.private_bytes.value == 800_000
        assert sample.swap_used_bytes.name == "pagefile_backing_bytes"
        assert sample.swap_used_bytes.value == 400_000
        assert sample.scope is MemoryScope.MSTR_CORE_TREE

    def test_tree_peak_withheld_not_summed_from_lifetime_peaks(self) -> None:
        sample = _sampler(core=(100,), tool=()).sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        assert sample.peak_rss_bytes.availability is MetricAvailability.UNAVAILABLE
        assert "overstate" in (sample.peak_rss_bytes.note or "")

    def test_total_tree_combines_core_and_tool_with_dedupe(self) -> None:
        sample = _sampler().sample_process_tree(MemoryScope.TOTAL_AGENT_TREE)
        assert sample.process_count == 2
        assert sample.rss_bytes.value == 1_500_000
        assert sample.private_bytes.value == 1_100_000

    def test_overlapping_pids_deduplicated(self) -> None:
        sample = _sampler(core=(100,), tool=(100,)).sample_process_tree(
            MemoryScope.TOTAL_AGENT_TREE
        )
        assert sample.process_count == 1
        assert sample.rss_bytes.value == 1_000_000


class TestSystemMemory:
    def test_commit_identities_in_extras_not_swap(self) -> None:
        # MEMORYSTATUSEX pagefile fields are commit limit/charge; they must be
        # reported under commit identities while swap stays UNSUPPORTED.
        sample = _sampler().sample_system_memory()
        extras = {m.name: m for m in sample.extra_metrics}
        assert extras["commit_limit_bytes"].value == _COMMIT_LIMIT
        assert extras["commit_charge_bytes"].value == _COMMIT_LIMIT - _AVAIL_COMMIT
        assert sample.swap_configured_bytes.availability is MetricAvailability.UNSUPPORTED
        assert sample.swap_used_bytes.availability is MetricAvailability.UNSUPPORTED

    def test_total_and_available_map_to_bytes_metrics(self) -> None:
        sample = _sampler().sample_system_memory()
        assert sample.total_bytes.value == _TOTAL_PHYS
        assert sample.available_bytes.value == _AVAIL_PHYS

    def test_dw_memory_load_is_not_converted_into_pressure_state(self) -> None:
        # dwMemoryLoad percent is not an MSTR-MEASURE-v0 pressure state;
        # classification must stay UNKNOWN rather than being invented.
        sample = _sampler().sample_system_memory()
        assert sample.pressure_state is SystemMemoryPressure.UNKNOWN
        assert any("dwMemoryLoad" in note for note in sample.notes)

    def test_hard_faults_stay_unsupported(self) -> None:
        # PageFaultCount is total faults; hard-fault deltas need ETW.
        sample = _sampler().sample_system_memory()
        assert sample.major_page_faults_total.availability is MetricAvailability.UNSUPPORTED
        assert "ETW" in (sample.major_page_faults_total.note or "")


def test_invalid_page_size_rejected() -> None:
    with pytest.raises(Exception, match="page_size"):
        WindowsSamplerOptions(page_size_bytes=0)
