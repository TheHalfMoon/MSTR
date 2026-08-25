"""Unit tests for the platform sampler protocol boundary (T023)."""

from __future__ import annotations

import pytest

from mstr_qualify.errors import QualificationError
from mstr_qualify.measurement.platform import (
    MemoryScope,
    MetricAvailability,
    ProcessTreeSample,
    SampledMetric,
    SamplingError,
    SystemMemoryPressure,
    SystemMemorySample,
    UnavailablePlatformSampler,
    require_available,
)


def _available(name: str, value: float | int, unit: str) -> SampledMetric:
    return SampledMetric(
        name=name,
        availability=MetricAvailability.AVAILABLE,
        value=value,
        unit=unit,
    )


class TestSampledMetric:
    def test_available_metric_requires_value_and_unit(self) -> None:
        with pytest.raises(SamplingError, match="concrete value"):
            SampledMetric(name="rss", availability=MetricAvailability.AVAILABLE, unit="bytes")
        with pytest.raises(SamplingError, match="unit"):
            SampledMetric(name="rss", availability=MetricAvailability.AVAILABLE, value=10)

    def test_unavailable_metric_must_not_carry_a_value(self) -> None:
        with pytest.raises(SamplingError, match="no value"):
            SampledMetric(
                name="rss",
                availability=MetricAvailability.UNSUPPORTED,
                value=0,
                unit="bytes",
            )

    def test_require_available_returns_value(self) -> None:
        assert require_available(_available("rss_bytes", 1024, "bytes")) == 1024

    def test_require_available_fails_closed_on_unavailable(self) -> None:
        metric = SampledMetric(name="rss", availability=MetricAvailability.UNAVAILABLE)
        with pytest.raises(SamplingError, match="not available"):
            require_available(metric)

    def test_blank_name_rejected(self) -> None:
        with pytest.raises(QualificationError):
            SampledMetric(name=" ", availability=MetricAvailability.UNAVAILABLE)


class TestProcessTreeSample:
    def test_scope_distinction_preserved(self) -> None:
        def make(scope: MemoryScope) -> ProcessTreeSample:
            return ProcessTreeSample(
                scope=scope,
                process_count=2,
                rss_bytes=_available("rss_bytes", scope.value.__len__(), "bytes"),
                peak_rss_bytes=_available("peak_rss_bytes", 2048, "bytes"),
                private_bytes=_available("private_bytes", 512, "bytes"),
                swap_used_bytes=_available("swap_used_bytes", 0, "bytes"),
            )

        core = make(MemoryScope.MSTR_CORE_TREE)
        tool = make(MemoryScope.TASK_TOOL_TREE)
        total = make(MemoryScope.TOTAL_AGENT_TREE)
        assert core.scope is MemoryScope.MSTR_CORE_TREE
        assert tool.scope is MemoryScope.TASK_TOOL_TREE
        assert total.scope is MemoryScope.TOTAL_AGENT_TREE

    def test_whole_system_pressure_rejected_in_process_sample(self) -> None:
        with pytest.raises(SamplingError, match="WHOLE_SYSTEM_PRESSURE"):
            ProcessTreeSample(
                scope=MemoryScope.WHOLE_SYSTEM_PRESSURE,
                process_count=1,
                rss_bytes=_available("rss_bytes", 1, "bytes"),
                peak_rss_bytes=_available("peak_rss_bytes", 1, "bytes"),
                private_bytes=_available("private_bytes", 1, "bytes"),
                swap_used_bytes=_available("swap_used_bytes", 0, "bytes"),
            )


class TestUnavailableSampler:
    def sampler(self) -> UnavailablePlatformSampler:
        return UnavailablePlatformSampler()

    def test_process_tree_metrics_explicitly_unsupported(self) -> None:
        sample = self.sampler().sample_process_tree(MemoryScope.MSTR_CORE_TREE)
        for metric in (
            sample.rss_bytes,
            sample.peak_rss_bytes,
            sample.private_bytes,
            sample.swap_used_bytes,
        ):
            assert metric.availability is MetricAvailability.UNSUPPORTED
            assert metric.value is None
            assert metric.note is not None

    def test_system_memory_reports_unknown_pressure_with_note(self) -> None:
        sample = self.sampler().sample_system_memory()
        assert sample.pressure_state is SystemMemoryPressure.UNKNOWN
        assert sample.notes
        assert sample.available_bytes.availability is MetricAvailability.UNSUPPORTED

    def test_unknown_pressure_without_notes_is_invalid(self) -> None:
        data = {
            "total_bytes": _available("total_bytes", 100, "bytes"),
            "available_bytes": _available("available_bytes", 50, "bytes"),
            "minimum_available_bytes_observed": _available("min", 40, "bytes"),
            "swap_configured_bytes": _available("swap_total", 0, "bytes"),
            "swap_used_bytes": _available("swap_used", 0, "bytes"),
            "major_page_faults_total": _available("majflt", 0, "count"),
        }
        with pytest.raises(SamplingError, match="UNKNOWN pressure"):
            SystemMemorySample(pressure_state=SystemMemoryPressure.UNKNOWN, **data)

    def test_page_size_validated(self) -> None:
        with pytest.raises(SamplingError, match="page_size"):
            UnavailablePlatformSampler(page_size_bytes=0)


class TestScopeVocabulary:
    def test_all_four_canonical_scopes_exist(self) -> None:
        values = {scope.value for scope in MemoryScope}
        assert values == {
            "mstr_core_tree",
            "task_tool_tree",
            "total_agent_tree",
            "whole_system_pressure",
        }
