"""Platform sampling boundary for MSTR measurement.

T023 defines the vocabulary and protocol used by every OS sampler
(Windows/Linux/macOS, implemented in T025) plus deterministic test doubles.
The central rule: unavailable or unsupported metrics are represented
explicitly — never invented, never defaulted to zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from ..errors import QualificationError


class SamplingError(QualificationError):
    default_code = "measurement.sampling"


class MemoryScope(Enum):
    """MSTR-MEASURE-v0 memory attribution scopes.

    The four scopes must remain distinct: MSTR_CORE_TREE is the model/system
    footprint headline, TASK_TOOL_TREE belongs to repository toolchains,
    TOTAL_AGENT_TREE aggregates both where lineage permits, and
    WHOLE_SYSTEM_PRESSURE describes the entire laptop rather than any tree.
    """

    MSTR_CORE_TREE = "mstr_core_tree"
    TASK_TOOL_TREE = "task_tool_tree"
    TOTAL_AGENT_TREE = "total_agent_tree"
    WHOLE_SYSTEM_PRESSURE = "whole_system_pressure"


class MetricAvailability(Enum):
    """Explicit availability semantics for sampled metrics."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"


class SystemMemoryPressure(Enum):
    """Whole-system pressure state; UNKNOWN means not exposed by the OS API."""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SampledMetric:
    """One metric sample with mandatory explicit availability.

    A value may only exist when availability is AVAILABLE. This makes it a
    type-level error to smuggle an invented zero into evidence.
    """

    name: str
    availability: MetricAvailability
    value: float | int | None = None
    unit: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() != self.name:
            raise SamplingError(
                "metric name must be non-empty with no surrounding whitespace",
                code="measurement.metric_name",
            )
        if self.availability is MetricAvailability.AVAILABLE:
            if self.value is None:
                raise SamplingError(
                    "AVAILABLE metric requires a concrete value",
                    code="measurement.available_without_value",
                    details={"name": self.name},
                )
            if self.unit is None or not self.unit.strip():
                raise SamplingError(
                    "AVAILABLE metric requires a unit",
                    code="measurement.available_without_unit",
                    details={"name": self.name},
                )
        else:
            if self.value is not None:
                raise SamplingError(
                    "unavailable/unsupported metric must carry no value",
                    code="measurement.unavailable_with_value",
                    details={"name": self.name},
                )


def require_available(metric: SampledMetric) -> float | int:
    """Extract a concrete value or fail closed for missing/unsupported data."""
    if metric.availability is not MetricAvailability.AVAILABLE or metric.value is None:
        raise SamplingError(
            "metric is not available; consumers must not substitute defaults",
            code="measurement.metric_not_available",
            details={"name": metric.name, "availability": metric.availability.value},
        )
    return metric.value


def unavailable(name: str, *, unsupported: bool = False, note: str | None = None) -> SampledMetric:
    availability = MetricAvailability.UNSUPPORTED if unsupported else MetricAvailability.UNAVAILABLE
    return SampledMetric(name=name, availability=availability, note=note)


@dataclass(frozen=True, slots=True)
class ProcessTreeSample:
    """Process-attribution sample for one scope.

    ``rss_bytes`` is the common headline (working set / VmRSS / resident_size
    depending on OS). Other fields stay explicitly unavailable when the
    platform does not expose them reliably.
    """

    scope: MemoryScope
    process_count: int
    rss_bytes: SampledMetric
    peak_rss_bytes: SampledMetric
    private_bytes: SampledMetric
    swap_used_bytes: SampledMetric

    def __post_init__(self) -> None:
        if self.scope is MemoryScope.WHOLE_SYSTEM_PRESSURE:
            raise SamplingError(
                "WHOLE_SYSTEM_PRESSURE uses SystemMemorySample, not ProcessTreeSample",
                code="measurement.wrong_sample_type",
            )
        if self.process_count < 0:
            raise SamplingError(
                "process_count must be non-negative",
                code="measurement.process_count",
                details={"process_count": self.process_count},
            )


@dataclass(frozen=True, slots=True)
class SystemMemorySample:
    """Whole-system memory/paging snapshot."""

    total_bytes: SampledMetric
    available_bytes: SampledMetric
    minimum_available_bytes_observed: SampledMetric
    swap_configured_bytes: SampledMetric
    swap_used_bytes: SampledMetric
    major_page_faults_total: SampledMetric
    pressure_state: SystemMemoryPressure
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.pressure_state is SystemMemoryPressure.UNKNOWN and len(self.notes) == 0:
            raise SamplingError(
                "UNKNOWN pressure state requires an explanatory note",
                code="measurement.unknown_pressure_noteless",
            )


class PlatformSampler(Protocol):
    """Protocol boundary for per-OS memory/paging samplers.

    Implementations must:

    - read only local OS interfaces (no network);
    - map each raw OS concept to its honest metric identity without claiming
      cross-OS equivalence;
    - mark metrics the OS does not expose as UNAVAILABLE/UNSUPPORTED;
    - be constructible and unit-testable on any development machine via
      injected data sources.
    """

    def platform_family(self) -> str:
        """One of ``windows``, ``linux``, ``macos`` (or a dummy family in tests)."""
        ...

    def page_size_bytes(self) -> int:
        ...

    def sample_process_tree(self, scope: MemoryScope) -> ProcessTreeSample:
        ...

    def sample_system_memory(self) -> SystemMemorySample:
        ...


class UnavailablePlatformSampler:
    """Deterministic sampler that reports everything explicitly unsupported.

    Used by tests and dry runs on hosts where no real sampler backend is
    selected. It never fabricates values.
    """

    def __init__(self, *, family: str = "unavailable", page_size_bytes: int = 4096) -> None:
        if page_size_bytes < 1:
            raise SamplingError(
                "page_size_bytes must be positive",
                code="measurement.page_size",
                details={"page_size_bytes": page_size_bytes},
            )
        self._family = family
        self._page_size = page_size_bytes

    def platform_family(self) -> str:
        return self._family

    def page_size_bytes(self) -> int:
        return self._page_size

    def _unsupported(self, name: str, reason: str) -> SampledMetric:
        return SampledMetric(
            name=name,
            availability=MetricAvailability.UNSUPPORTED,
            note=reason,
        )

    def sample_process_tree(self, scope: MemoryScope) -> ProcessTreeSample:
        reason = f"no sampler backend selected for {scope.value}"
        return ProcessTreeSample(
            scope=scope,
            process_count=0,
            rss_bytes=self._unsupported("rss_bytes", reason),
            peak_rss_bytes=self._unsupported("peak_rss_bytes", reason),
            private_bytes=self._unsupported("private_bytes", reason),
            swap_used_bytes=self._unsupported("swap_used_bytes", reason),
        )

    def sample_system_memory(self) -> SystemMemorySample:
        reason = "no sampler backend selected"
        return SystemMemorySample(
            total_bytes=self._unsupported("total_bytes", reason),
            available_bytes=self._unsupported("available_bytes", reason),
            minimum_available_bytes_observed=self._unsupported(
                "minimum_available_bytes_observed", reason
            ),
            swap_configured_bytes=self._unsupported("swap_configured_bytes", reason),
            swap_used_bytes=self._unsupported("swap_used_bytes", reason),
            major_page_faults_total=self._unsupported("major_page_faults_total", reason),
            pressure_state=SystemMemoryPressure.UNKNOWN,
            notes=("pressure classification requires a real platform backend",),
        )

