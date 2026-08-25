"""Unit tests for the macOS sampler (mocked collectors; no macOS needed)."""

from __future__ import annotations

import pytest

from mstr_qualify.measurement.macos import (
    FakeProcRusage,
    FakeVmStatistics,
    MacOSPlatformSampler,
    MacOSSamplerOptions,
    parse_swap_usage_text,
)
from mstr_qualify.measurement.platform import (
    MemoryScope,
    MetricAvailability,
    SystemMemoryPressure,
)

PAGE = 16384


def _rusage(pid: int) -> FakeProcRusage:
    return FakeProcRusage(
        ri_resident_size=900_000 + pid,
        ri_phys_footprint=1_200_000 + pid,
        ri_pageins=42,
    )


def _vm_stats() -> FakeVmStatistics:
    return FakeVmStatistics(
        free_pages=10_000,
        active_pages=50_000,
        inactive_pages=20_000,
        wired_pages=30_000,
        compressed_pages=8_000,
        pageins=111,
        pageouts=222,
    )


def _swap_text() -> str:
    return "Swap usage: total = 2147483648 used = 536870912 free = 1610612736"


def _sampler(core: tuple[int, ...] = (7,), tool: tuple[int, ...] = (9,)) -> MacOSPlatformSampler:
    options = MacOSSamplerOptions(
        proc_rusage=_rusage,
        host_vm_statistics=_vm_stats,
        read_swap_usage=_swap_text,
        core_pids=core,
        tool_pids=tool,
        page_size_bytes=PAGE,
    )
    return MacOSPlatformSampler(options)


class TestProcessTree:
    def test_resident_and_footprint_keep_distinct_identities(self) -> None:
        sample = _sampler().sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        assert sample.rss_bytes.value == 900_007
        assert sample.private_bytes.name == "phys_footprint_bytes"
        assert sample.private_bytes.value == 1_200_007

    def test_peak_rss_explicitly_unsupported(self) -> None:
        sample = _sampler().sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        assert sample.peak_rss_bytes.availability is MetricAvailability.UNSUPPORTED
        assert "resident" in (sample.peak_rss_bytes.note or "")

    def test_total_tree_aggregates_both_pids(self) -> None:
        sample = _sampler().sample_process_tree(MemoryScope.TOTAL_AGENT_TREE)
        assert sample.process_count == 2
        assert sample.rss_bytes.value == 900_007 + 900_009


class TestSystemMemory:
    def test_available_is_labeled_estimate(self) -> None:
        sample = _sampler().sample_system_memory()
        assert sample.available_bytes.note is not None
        assert "estimate" in sample.available_bytes.note
        expected = (10_000 + 20_000) * PAGE
        assert sample.available_bytes.value == expected

    def test_total_sums_all_page_classes(self) -> None:
        sample = _sampler().sample_system_memory()
        assert sample.total_bytes.value == (10_000 + 50_000 + 20_000 + 30_000 + 8_000) * PAGE

    def test_swap_usage_parsed_from_sysctl_text(self) -> None:
        sample = _sampler().sample_system_memory()
        assert sample.swap_configured_bytes.value == 2_147_483_648
        assert sample.swap_used_bytes.value == 536_870_912

    def test_pressure_left_unknown_with_note(self) -> None:
        sample = _sampler().sample_system_memory()
        assert sample.pressure_state is SystemMemoryPressure.UNKNOWN
        assert any("memorystatus" in note for note in sample.notes)


class TestParsing:
    def test_swap_usage_parser(self) -> None:
        total, used = parse_swap_usage_text(_swap_text())
        assert total == 2_147_483_648
        assert used == 536_870_912

    def test_swap_usage_garbage_returns_nones(self) -> None:
        assert parse_swap_usage_text("no numbers here") == (None, None)


def test_invalid_page_size_rejected() -> None:
    with pytest.raises(Exception, match="page_size"):
        MacOSSamplerOptions(page_size_bytes=0)
