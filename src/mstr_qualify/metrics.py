"""Failure-inclusive A016 diagnostic metrics for Direction-to-Done evaluation."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from statistics import median
from typing import Any, Literal

from .errors import QualificationError

RunDisposition = Literal["eligible", "excluded", "invalid"]

_METRIC_SCHEMA_VERSION = "mstr.metric-record.v0"
_AGGREGATION_POLICY_ID = "MSTR-A016-METRICS-v0"
_ZERO_SOLVE_BEHAVIOR = (
    "TTVC_AND_PER_VERIFIED_COMPLETION_METRICS_ARE_NULL;"
    "DVCR_AND_FAILURE_INCLUSIVE_RATES_REMAIN_DEFINED_WHEN_ELIGIBLE_ATTEMPTS_EXIST"
)


class MetricComputationError(QualificationError):
    """Fail-closed error for malformed or contradictory metric observations."""

    default_code = "metric.invalid"


@dataclass(frozen=True, slots=True)
class RunMetricObservation:
    """One task-attempt observation consumed by the A016 metric aggregator.

    `eligible` attempts participate in failure-inclusive denominators. `excluded`
    and `invalid` attempts remain counted as evidence but do not enter score
    denominators. A successful TTVC exists only for independently verified
    completion; failed/invalid/excluded attempts cannot report a TTVC value.
    """

    run_id: str
    disposition: RunDisposition = "eligible"
    exclusion_reason: str | None = None
    verified_completion: bool = False
    ttvc_seconds: float | None = None
    first_implementation_accepted: bool = False
    proposed_edit_units: int = 0
    surviving_edit_units: int = 0
    repair_attempted: bool = False
    repair_succeeded: bool = False
    tool_calls: int = 0
    tool_errors: int = 0
    tokens: int = 0
    context_tokens: int = 0
    harness_wall_time_overhead_seconds: float = 0.0
    harness_memory_overhead_bytes: int = 0

    def __post_init__(self) -> None:
        _validate_observation(self)


@dataclass(frozen=True, slots=True)
class MetricRecord:
    """Deterministic aggregate metric record for one comparable evaluation cell."""

    schema_version: str
    aggregation_policy_id: str
    attempt_count: int
    eligible_attempt_count: int
    verified_completion_count: int
    excluded_run_count: int
    invalid_run_count: int
    exclusions: tuple[tuple[str, int], ...]
    invalid_reasons: tuple[tuple[str, int], ...]
    dvcr_denominator: int
    ttvc_denominator: int
    first_pass_accept_denominator: int
    edit_survival_denominator_units: int
    repair_success_denominator: int
    tool_error_denominator: int
    per_verified_completion_denominator: int
    harness_overhead_denominator: int
    dvcr: float | None
    ttvc_seconds: float | None
    first_pass_accept_rate: float | None
    edit_survival_rate: float | None
    repair_success_rate: float | None
    tool_error_rate: float | None
    tool_calls_per_verified_completion: float | None
    tokens_per_verified_completion: float | None
    context_tokens_per_verified_completion: float | None
    harness_wall_time_overhead: float | None
    harness_memory_overhead: float | None
    q4_artifact_bytes: int | None
    zero_solve: bool
    zero_solve_behavior: str

    def as_mapping(self) -> dict[str, Any]:
        """Return a JSON-compatible mapping with explicit denominator metadata."""

        return {
            "aggregation_policy_id": self.aggregation_policy_id,
            "attempt_count": self.attempt_count,
            "context_tokens_per_verified_completion": self.context_tokens_per_verified_completion,
            "denominators": {
                "dvcr": self.dvcr_denominator,
                "edit_survival_rate_units": self.edit_survival_denominator_units,
                "first_pass_accept_rate": self.first_pass_accept_denominator,
                "harness_overhead": self.harness_overhead_denominator,
                "per_verified_completion": self.per_verified_completion_denominator,
                "repair_success_rate": self.repair_success_denominator,
                "tool_error_rate": self.tool_error_denominator,
                "ttvc_seconds": self.ttvc_denominator,
            },
            "dvcr": self.dvcr,
            "edit_survival_rate": self.edit_survival_rate,
            "eligible_attempt_count": self.eligible_attempt_count,
            "excluded_run_count": self.excluded_run_count,
            "exclusions": [
                {"count": count, "reason": reason} for reason, count in self.exclusions
            ],
            "first_pass_accept_rate": self.first_pass_accept_rate,
            "harness_memory_overhead": self.harness_memory_overhead,
            "harness_wall_time_overhead": self.harness_wall_time_overhead,
            "invalid_reasons": [
                {"count": count, "reason": reason}
                for reason, count in self.invalid_reasons
            ],
            "invalid_run_count": self.invalid_run_count,
            "q4_artifact_bytes": self.q4_artifact_bytes,
            "repair_success_rate": self.repair_success_rate,
            "schema_version": self.schema_version,
            "tokens_per_verified_completion": self.tokens_per_verified_completion,
            "tool_calls_per_verified_completion": self.tool_calls_per_verified_completion,
            "tool_error_rate": self.tool_error_rate,
            "ttvc_seconds": self.ttvc_seconds,
            "verified_completion_count": self.verified_completion_count,
            "zero_solve": self.zero_solve,
            "zero_solve_behavior": self.zero_solve_behavior,
        }


def _metric_error(message: str, code: str, **details: object) -> MetricComputationError:
    return MetricComputationError(message, code=code, details=details)


def _validate_nonnegative_int(value: int, field: str, run_id: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise _metric_error(
            "metric count must be a non-negative integer",
            "metric.count",
            field=field,
            run_id=run_id,
        )


def _validate_nonnegative_float(value: float, field: str, run_id: str) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
    ):
        raise _metric_error(
            "metric duration/overhead must be finite and non-negative",
            "metric.number",
            field=field,
            run_id=run_id,
        )


def _validate_observation(observation: RunMetricObservation) -> None:
    if not observation.run_id or observation.run_id.strip() != observation.run_id:
        raise _metric_error(
            "run_id must be a non-empty trimmed string",
            "metric.run_id",
        )
    if observation.disposition not in {"eligible", "excluded", "invalid"}:
        raise _metric_error(
            "unsupported metric observation disposition",
            "metric.disposition",
            run_id=observation.run_id,
            disposition=observation.disposition,
        )
    if observation.disposition == "eligible":
        if observation.exclusion_reason is not None:
            raise _metric_error(
                "eligible observations cannot carry an exclusion reason",
                "metric.eligible_exclusion_reason",
                run_id=observation.run_id,
            )
    elif (
        observation.exclusion_reason is None
        or not observation.exclusion_reason
        or observation.exclusion_reason.strip() != observation.exclusion_reason
    ):
        raise _metric_error(
            "excluded/invalid observations require a non-empty trimmed reason",
            "metric.exclusion_reason",
            run_id=observation.run_id,
        )

    for field in (
        "proposed_edit_units",
        "surviving_edit_units",
        "tool_calls",
        "tool_errors",
        "tokens",
        "context_tokens",
        "harness_memory_overhead_bytes",
    ):
        _validate_nonnegative_int(getattr(observation, field), field, observation.run_id)
    _validate_nonnegative_float(
        observation.harness_wall_time_overhead_seconds,
        "harness_wall_time_overhead_seconds",
        observation.run_id,
    )

    if observation.surviving_edit_units > observation.proposed_edit_units:
        raise _metric_error(
            "surviving edit units cannot exceed proposed edit units",
            "metric.edit_survival_bounds",
            run_id=observation.run_id,
        )
    if observation.tool_errors > observation.tool_calls:
        raise _metric_error(
            "tool errors cannot exceed tool calls",
            "metric.tool_error_bounds",
            run_id=observation.run_id,
        )
    if observation.repair_succeeded and not observation.repair_attempted:
        raise _metric_error(
            "repair success requires a repair attempt",
            "metric.repair_without_attempt",
            run_id=observation.run_id,
        )
    if observation.first_implementation_accepted and observation.repair_attempted:
        raise _metric_error(
            "first-pass acceptance cannot also require repair",
            "metric.first_pass_with_repair",
            run_id=observation.run_id,
        )
    if observation.first_implementation_accepted and not observation.verified_completion:
        raise _metric_error(
            "first-pass acceptance requires verified completion",
            "metric.first_pass_without_success",
            run_id=observation.run_id,
        )
    if observation.repair_succeeded and not observation.verified_completion:
        raise _metric_error(
            "repair success requires verified completion",
            "metric.repair_without_success",
            run_id=observation.run_id,
        )
    if not observation.verified_completion and observation.surviving_edit_units != 0:
        raise _metric_error(
            "failed/non-completing attempts cannot claim final surviving edit content",
            "metric.edit_survival_without_success",
            run_id=observation.run_id,
        )

    if observation.verified_completion:
        if observation.disposition != "eligible":
            raise _metric_error(
                "excluded/invalid observations cannot claim verified completion",
                "metric.success_not_eligible",
                run_id=observation.run_id,
            )
        if observation.ttvc_seconds is None:
            raise _metric_error(
                "verified completion requires TTVC",
                "metric.ttvc_missing",
                run_id=observation.run_id,
            )
        _validate_nonnegative_float(
            observation.ttvc_seconds,
            "ttvc_seconds",
            observation.run_id,
        )
    elif observation.ttvc_seconds is not None:
        raise _metric_error(
            "TTVC may be reported only for verified completion",
            "metric.ttvc_without_success",
            run_id=observation.run_id,
        )


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _per_completion(total: int, verified_count: int) -> float | None:
    if verified_count == 0:
        return None
    return total / verified_count


def _mean(total: int | float, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return float(total) / denominator


def compute_metric_record(
    observations: Iterable[RunMetricObservation],
    *,
    q4_artifact_bytes: int | None = None,
) -> MetricRecord:
    """Compute A016 metrics without hiding failures, exclusions, or zero solves.

    Semantics are frozen as follows:
    - DVCR and FPAR use every eligible direction attempt as denominator.
    - TTVC is the median time among independently verified completions only.
    - ESR is surviving/proposed edit units across eligible attempts; failed attempts
      can contribute proposed units but necessarily contribute zero surviving units.
    - RSR uses eligible attempts that entered repair as denominator.
    - TER uses all tool calls from eligible attempts as denominator.
    - tool/tokens/context per verified completion divide failure-inclusive totals by
      the number of verified completions.
    - harness overhead is the arithmetic mean across eligible attempts.
    - excluded and invalid runs remain explicitly counted but never enter score
      denominators.
    """

    records = tuple(observations)
    if q4_artifact_bytes is not None:
        _validate_nonnegative_int(q4_artifact_bytes, "q4_artifact_bytes", "aggregate")

    eligible = tuple(record for record in records if record.disposition == "eligible")
    excluded = tuple(record for record in records if record.disposition == "excluded")
    invalid = tuple(record for record in records if record.disposition == "invalid")
    verified = tuple(record for record in eligible if record.verified_completion)

    eligible_count = len(eligible)
    verified_count = len(verified)
    proposed_edit_units = sum(record.proposed_edit_units for record in eligible)
    surviving_edit_units = sum(record.surviving_edit_units for record in eligible)
    repair_attempts = sum(1 for record in eligible if record.repair_attempted)
    repair_successes = sum(1 for record in eligible if record.repair_succeeded)
    tool_calls = sum(record.tool_calls for record in eligible)
    tool_errors = sum(record.tool_errors for record in eligible)
    total_tokens = sum(record.tokens for record in eligible)
    total_context_tokens = sum(record.context_tokens for record in eligible)
    total_harness_wall = sum(record.harness_wall_time_overhead_seconds for record in eligible)
    total_harness_memory = sum(record.harness_memory_overhead_bytes for record in eligible)
    first_pass_successes = sum(
        1 for record in eligible if record.first_implementation_accepted
    )

    ttvc_values = [record.ttvc_seconds for record in verified]
    if any(value is None for value in ttvc_values):  # defensive; constructor already rejects
        raise _metric_error("verified TTVC set is incomplete", "metric.ttvc_missing")
    ttvc = float(median(value for value in ttvc_values if value is not None)) if verified else None

    exclusion_counts = Counter(
        record.exclusion_reason for record in excluded if record.exclusion_reason is not None
    )
    invalid_counts = Counter(
        record.exclusion_reason for record in invalid if record.exclusion_reason is not None
    )

    return MetricRecord(
        schema_version=_METRIC_SCHEMA_VERSION,
        aggregation_policy_id=_AGGREGATION_POLICY_ID,
        attempt_count=len(records),
        eligible_attempt_count=eligible_count,
        verified_completion_count=verified_count,
        excluded_run_count=len(excluded),
        invalid_run_count=len(invalid),
        exclusions=tuple(sorted(exclusion_counts.items())),
        invalid_reasons=tuple(sorted(invalid_counts.items())),
        dvcr_denominator=eligible_count,
        ttvc_denominator=verified_count,
        first_pass_accept_denominator=eligible_count,
        edit_survival_denominator_units=proposed_edit_units,
        repair_success_denominator=repair_attempts,
        tool_error_denominator=tool_calls,
        per_verified_completion_denominator=verified_count,
        harness_overhead_denominator=eligible_count,
        dvcr=_rate(verified_count, eligible_count),
        ttvc_seconds=ttvc,
        first_pass_accept_rate=_rate(first_pass_successes, eligible_count),
        edit_survival_rate=_rate(surviving_edit_units, proposed_edit_units),
        repair_success_rate=_rate(repair_successes, repair_attempts),
        tool_error_rate=_rate(tool_errors, tool_calls),
        tool_calls_per_verified_completion=_per_completion(tool_calls, verified_count),
        tokens_per_verified_completion=_per_completion(total_tokens, verified_count),
        context_tokens_per_verified_completion=_per_completion(
            total_context_tokens,
            verified_count,
        ),
        harness_wall_time_overhead=_mean(total_harness_wall, eligible_count),
        harness_memory_overhead=_mean(total_harness_memory, eligible_count),
        q4_artifact_bytes=q4_artifact_bytes,
        zero_solve=verified_count == 0,
        zero_solve_behavior=_ZERO_SOLVE_BEHAVIOR,
    )
