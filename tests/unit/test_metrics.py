from __future__ import annotations

import math

import pytest

from mstr_qualify.metrics import (
    MetricComputationError,
    RunMetricObservation,
    compute_metric_record,
)


def test_compute_metric_record_is_failure_inclusive_and_explicit() -> None:
    record = compute_metric_record(
        [
            RunMetricObservation(
                run_id="success-first-pass",
                verified_completion=True,
                ttvc_seconds=12.0,
                first_implementation_accepted=True,
                proposed_edit_units=10,
                surviving_edit_units=8,
                tool_calls=4,
                tool_errors=0,
                tokens=100,
                context_tokens=80,
                harness_wall_time_overhead_seconds=1.0,
                harness_memory_overhead_bytes=1000,
            ),
            RunMetricObservation(
                run_id="success-repair",
                verified_completion=True,
                ttvc_seconds=18.0,
                proposed_edit_units=20,
                surviving_edit_units=10,
                repair_attempted=True,
                repair_succeeded=True,
                tool_calls=6,
                tool_errors=1,
                tokens=200,
                context_tokens=120,
                harness_wall_time_overhead_seconds=3.0,
                harness_memory_overhead_bytes=3000,
            ),
            RunMetricObservation(
                run_id="failed",
                proposed_edit_units=10,
                repair_attempted=True,
                tool_calls=2,
                tool_errors=1,
                tokens=60,
                context_tokens=40,
                harness_wall_time_overhead_seconds=2.0,
                harness_memory_overhead_bytes=2000,
            ),
        ],
        q4_artifact_bytes=2_500_000_000,
    )

    assert record.attempt_count == 3
    assert record.eligible_attempt_count == 3
    assert record.verified_completion_count == 2
    assert record.dvcr == pytest.approx(2 / 3)
    assert record.ttvc_seconds == 15.0
    assert record.first_pass_accept_rate == pytest.approx(1 / 3)
    assert record.edit_survival_rate == pytest.approx(18 / 40)
    assert record.repair_success_rate == 0.5
    assert record.tool_error_rate == pytest.approx(2 / 12)
    assert record.tool_calls_per_verified_completion == 6.0
    assert record.tokens_per_verified_completion == 180.0
    assert record.context_tokens_per_verified_completion == 120.0
    assert record.harness_wall_time_overhead == 2.0
    assert record.harness_memory_overhead == 2000.0
    assert record.q4_artifact_bytes == 2_500_000_000
    assert record.zero_solve is False
    assert record.dvcr_denominator == 3
    assert record.ttvc_denominator == 2
    assert record.first_pass_accept_denominator == 3
    assert record.edit_survival_denominator_units == 40
    assert record.repair_success_denominator == 2
    assert record.tool_error_denominator == 12
    assert record.per_verified_completion_denominator == 2
    assert record.harness_overhead_denominator == 3


def test_zero_solve_keeps_failure_rates_and_nulls_success_only_metrics() -> None:
    record = compute_metric_record(
        [
            RunMetricObservation(
                run_id="failure-a",
                proposed_edit_units=4,
                repair_attempted=True,
                tool_calls=2,
                tool_errors=1,
                tokens=40,
                context_tokens=20,
            ),
            RunMetricObservation(run_id="failure-b", tool_calls=1, tokens=10),
        ]
    )

    assert record.zero_solve is True
    assert record.dvcr == 0.0
    assert record.ttvc_seconds is None
    assert record.first_pass_accept_rate == 0.0
    assert record.edit_survival_rate == 0.0
    assert record.repair_success_rate == 0.0
    assert record.tool_error_rate == pytest.approx(1 / 3)
    assert record.tool_calls_per_verified_completion is None
    assert record.tokens_per_verified_completion is None
    assert record.context_tokens_per_verified_completion is None
    assert record.ttvc_denominator == 0
    assert record.per_verified_completion_denominator == 0
    assert "ARE_NULL" in record.zero_solve_behavior


def test_no_eligible_attempts_are_not_reported_as_zero_percent_performance() -> None:
    record = compute_metric_record(
        [
            RunMetricObservation(
                run_id="excluded",
                disposition="excluded",
                exclusion_reason="OUT_OF_SCOPE",
            ),
            RunMetricObservation(
                run_id="invalid",
                disposition="invalid",
                exclusion_reason="BROKEN_ENVIRONMENT",
            ),
        ]
    )

    assert record.attempt_count == 2
    assert record.eligible_attempt_count == 0
    assert record.excluded_run_count == 1
    assert record.invalid_run_count == 1
    assert record.exclusions == (("OUT_OF_SCOPE", 1),)
    assert record.invalid_reasons == (("BROKEN_ENVIRONMENT", 1),)
    assert record.dvcr is None
    assert record.first_pass_accept_rate is None
    assert record.ttvc_seconds is None
    assert record.harness_wall_time_overhead is None
    assert record.harness_memory_overhead is None
    assert record.zero_solve is True


def test_exclusion_and_invalid_reason_counts_are_deterministically_sorted() -> None:
    record = compute_metric_record(
        [
            RunMetricObservation("x2", "excluded", "ZETA"),
            RunMetricObservation("x1", "excluded", "ALPHA"),
            RunMetricObservation("x3", "excluded", "ZETA"),
            RunMetricObservation("i2", "invalid", "TIMEOUT_SETUP"),
            RunMetricObservation("i1", "invalid", "BROKEN_ENVIRONMENT"),
        ]
    )

    assert record.exclusions == (("ALPHA", 1), ("ZETA", 2))
    assert record.invalid_reasons == (("BROKEN_ENVIRONMENT", 1), ("TIMEOUT_SETUP", 1))
    assert record.as_mapping()["exclusions"] == [
        {"count": 1, "reason": "ALPHA"},
        {"count": 2, "reason": "ZETA"},
    ]


@pytest.mark.parametrize(
    ("kwargs", "code"),
    [
        ({"run_id": " bad"}, "metric.run_id"),
        (
            {"run_id": "eligible-reason", "exclusion_reason": "NO"},
            "metric.eligible_exclusion_reason",
        ),
        (
            {"run_id": "excluded-no-reason", "disposition": "excluded"},
            "metric.exclusion_reason",
        ),
        (
            {"run_id": "success-no-ttvc", "verified_completion": True},
            "metric.ttvc_missing",
        ),
        (
            {"run_id": "failure-ttvc", "ttvc_seconds": 1.0},
            "metric.ttvc_without_success",
        ),
        (
            {
                "run_id": "excluded-success",
                "disposition": "excluded",
                "exclusion_reason": "OUT",
                "verified_completion": True,
                "ttvc_seconds": 1.0,
            },
            "metric.success_not_eligible",
        ),
        (
            {"run_id": "first-pass-failure", "first_implementation_accepted": True},
            "metric.first_pass_without_success",
        ),
        (
            {
                "run_id": "first-pass-repair",
                "verified_completion": True,
                "ttvc_seconds": 1.0,
                "first_implementation_accepted": True,
                "repair_attempted": True,
            },
            "metric.first_pass_with_repair",
        ),
        (
            {"run_id": "repair-no-attempt", "repair_succeeded": True},
            "metric.repair_without_attempt",
        ),
        (
            {
                "run_id": "repair-no-success",
                "repair_attempted": True,
                "repair_succeeded": True,
            },
            "metric.repair_without_success",
        ),
        (
            {"run_id": "bad-edit-count", "proposed_edit_units": 1, "surviving_edit_units": 2},
            "metric.edit_survival_bounds",
        ),
        (
            {"run_id": "failed-survival", "proposed_edit_units": 1, "surviving_edit_units": 1},
            "metric.edit_survival_without_success",
        ),
        (
            {"run_id": "bad-tools", "tool_calls": 1, "tool_errors": 2},
            "metric.tool_error_bounds",
        ),
        ({"run_id": "negative-tokens", "tokens": -1}, "metric.count"),
        (
            {"run_id": "nonfinite-overhead", "harness_wall_time_overhead_seconds": math.inf},
            "metric.number",
        ),
    ],
)
def test_observation_validation_fails_closed(kwargs: dict[str, object], code: str) -> None:
    with pytest.raises(MetricComputationError) as excinfo:
        RunMetricObservation(**kwargs)  # type: ignore[arg-type]
    assert excinfo.value.code == code


def test_q4_artifact_size_validation_fails_closed() -> None:
    with pytest.raises(MetricComputationError) as excinfo:
        compute_metric_record([], q4_artifact_bytes=-1)
    assert excinfo.value.code == "metric.count"


def test_ttvc_is_median_of_verified_completions_only() -> None:
    record = compute_metric_record(
        [
            RunMetricObservation("a", verified_completion=True, ttvc_seconds=30.0),
            RunMetricObservation("b", verified_completion=True, ttvc_seconds=10.0),
            RunMetricObservation("c", verified_completion=True, ttvc_seconds=20.0),
            RunMetricObservation("failure"),
        ]
    )
    assert record.ttvc_seconds == 20.0
    assert record.dvcr == 0.75
    assert record.ttvc_denominator == 3
    assert record.dvcr_denominator == 4
