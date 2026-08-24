from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.errors import ComparisonError
from mstr_qualify.reporting import (
    assert_comparable,
    comparability_key,
    comparability_mismatches,
    comparison_conditions,
    partition_comparable,
    validate_ttvc_summary,
)


def base(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "score_surface": "neutral_harness",
        "measurement_protocol": "MSTR-MEASURE-v0",
        "task_id": "task-1",
        "task_manifest_revision": "manifest-sha",
        "verifier_set_id": "V1",
        "timeout_seconds": 300,
        "cache_state": "process_cold",
        "hardware_class": "U1",
        "context_length": 8192,
        "interaction_contract_version": "interaction-v0",
        "sampling_config": {"temperature": 0.0, "top_p": 1.0},
        "seed": 0,
    }
    value.update(updates)
    return value


def test_identical_conditions_are_comparable_even_if_seed_differs() -> None:
    left = comparison_conditions(base(seed=1))
    right = comparison_conditions(base(seed=2))
    assert comparability_mismatches(left, right) == ()
    assert_comparable(left, right)
    assert comparability_key(left) == comparability_key(right)


@pytest.mark.parametrize(
    "field,value",
    [
        ("score_surface", "full_system"),
        ("measurement_protocol", "MSTR-MEASURE-v1"),
        ("task_id", "task-2"),
        ("task_manifest_revision", "other"),
        ("verifier_set_id", "V2"),
        ("timeout_seconds", 600),
        ("cache_state", "prefix_warm"),
        ("hardware_class", "U2"),
        ("context_length", 4096),
        ("interaction_contract_version", "interaction-v1"),
        ("sampling_config", {"temperature": 0.2}),
    ],
)
def test_each_material_condition_blocks_direct_comparison(field: str, value: object) -> None:
    left = comparison_conditions(base())
    right = comparison_conditions(base(**{field: value}))
    assert field in comparability_mismatches(left, right)
    with pytest.raises(ComparisonError, match="comparison.mismatch"):
        assert_comparable(left, right)


def test_partition_separates_noncomparable_groups() -> None:
    records = [
        comparison_conditions(base(seed=1)),
        comparison_conditions(base(seed=2)),
        comparison_conditions(base(cache_state="prefix_warm", seed=1)),
    ]
    groups = partition_comparable(records)
    assert sorted(map(len, groups.values())) == [1, 2]


def test_sampling_key_order_does_not_change_comparability() -> None:
    left = comparison_conditions(base(sampling_config={"top_p": 1.0, "temperature": 0.0}))
    right = comparison_conditions(base(sampling_config={"temperature": 0.0, "top_p": 1.0}))
    assert_comparable(left, right)
    assert comparability_key(left) == comparability_key(right)


@pytest.mark.parametrize(
    "field",
    [
        "score_surface",
        "measurement_protocol",
        "task_id",
        "task_manifest_revision",
        "verifier_set_id",
        "timeout_seconds",
        "cache_state",
        "hardware_class",
        "context_length",
        "interaction_contract_version",
        "sampling_config",
    ],
)
def test_missing_condition_fails_closed(field: str) -> None:
    value = base()
    value.pop(field)
    with pytest.raises(ComparisonError, match="comparison.conditions_missing"):
        comparison_conditions(value)


def test_unknown_condition_fails_closed() -> None:
    with pytest.raises(ComparisonError, match="comparison.conditions_unknown"):
        comparison_conditions(base(extra=True))


@pytest.mark.parametrize("rate", [-0.1, 1.1, True, float("nan"), float("inf")])
def test_ttvc_summary_rejects_invalid_solve_rate(rate: object) -> None:
    with pytest.raises(ComparisonError):
        validate_ttvc_summary(
            verified_completion_rate=rate,  # type: ignore[arg-type]
            timeout_seconds=300,
            median_ttvc_ms=1.0,
        )


def test_ttvc_summary_requires_success_for_median() -> None:
    with pytest.raises(ComparisonError, match="comparison.ttvc_without_success"):
        validate_ttvc_summary(
            verified_completion_rate=0,
            timeout_seconds=300,
            median_ttvc_ms=100,
        )
    validate_ttvc_summary(
        verified_completion_rate=0,
        timeout_seconds=300,
        median_ttvc_ms=None,
    )
    validate_ttvc_summary(
        verified_completion_rate=0.5,
        timeout_seconds=300,
        median_ttvc_ms=100,
    )


def test_sampling_config_rejects_nonfinite_json() -> None:
    with pytest.raises(ComparisonError, match="comparison.sampling_config"):
        comparison_conditions(base(sampling_config={"temperature": float("nan")}))


def test_ttvc_summary_rejects_nonfinite_median() -> None:
    with pytest.raises(ComparisonError, match="comparison.ttvc"):
        validate_ttvc_summary(
            verified_completion_rate=0.5,
            timeout_seconds=300,
            median_ttvc_ms=float("nan"),
        )


def test_reporting_fixtures_capture_cache_mismatch() -> None:
    fixture_dir = Path(__file__).parents[1] / "fixtures" / "reporting"
    left = comparison_conditions(
        json.loads((fixture_dir / "comparable.json").read_text(encoding="utf-8"))
    )
    right = comparison_conditions(
        json.loads((fixture_dir / "mismatch-cache.json").read_text(encoding="utf-8"))
    )
    assert comparability_mismatches(left, right) == ("cache_state",)
