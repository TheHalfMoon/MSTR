"""Strict comparability rules for MSTR score surfaces and reports."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from .errors import ComparisonError
from .evidence import canonical_json_bytes
from .ids import stable_id

ScoreSurface = Literal["raw_model", "neutral_harness", "full_system"]

_SCORE_SURFACES = frozenset({"raw_model", "neutral_harness", "full_system"})
_CACHE_STATES = frozenset({"process_cold", "session_warm", "prefix_warm"})
_FIELDS = (
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
)


@dataclass(frozen=True, slots=True)
class ComparisonConditions:
    score_surface: ScoreSurface
    measurement_protocol: str
    task_id: str
    task_manifest_revision: str
    verifier_set_id: str
    timeout_seconds: int
    cache_state: str
    hardware_class: str
    context_length: int
    interaction_contract_version: str
    sampling_config: Mapping[str, Any]

    def as_mapping(self) -> dict[str, Any]:
        return {
            "score_surface": self.score_surface,
            "measurement_protocol": self.measurement_protocol,
            "task_id": self.task_id,
            "task_manifest_revision": self.task_manifest_revision,
            "verifier_set_id": self.verifier_set_id,
            "timeout_seconds": self.timeout_seconds,
            "cache_state": self.cache_state,
            "hardware_class": self.hardware_class,
            "context_length": self.context_length,
            "interaction_contract_version": self.interaction_contract_version,
            "sampling_config": dict(self.sampling_config),
        }


def _fail(message: str, code: str, **details: object) -> ComparisonError:
    return ComparisonError(message, code=code, details=details)


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or value.strip() != value:
        raise _fail(
            "comparison condition must be a non-empty trimmed string",
            "comparison.condition_string",
            field=field,
        )
    return value


def comparison_conditions(value: Mapping[str, Any]) -> ComparisonConditions:
    missing = [field for field in _FIELDS if field not in value]
    if missing:
        raise _fail(
            "comparison conditions are incomplete",
            "comparison.conditions_missing",
            fields=",".join(missing),
        )
    unknown = sorted(set(value) - set(_FIELDS) - {"seed"})
    if unknown:
        raise _fail(
            "comparison conditions contain unknown fields",
            "comparison.conditions_unknown",
            fields=",".join(unknown),
        )

    surface = value["score_surface"]
    if surface not in _SCORE_SURFACES:
        raise _fail(
            "invalid score surface",
            "comparison.score_surface",
            value=surface,
        )
    for field in (
        "measurement_protocol",
        "task_id",
        "task_manifest_revision",
        "verifier_set_id",
        "hardware_class",
        "interaction_contract_version",
    ):
        _nonempty_string(value[field], field)

    timeout = value["timeout_seconds"]
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        raise _fail(
            "timeout_seconds must be a positive integer",
            "comparison.timeout",
        )
    context_length = value["context_length"]
    if (
        isinstance(context_length, bool)
        or not isinstance(context_length, int)
        or context_length <= 0
    ):
        raise _fail(
            "context_length must be a positive integer",
            "comparison.context_length",
        )
    cache_state = value["cache_state"]
    if cache_state not in _CACHE_STATES:
        raise _fail(
            "unsupported cache state",
            "comparison.cache_state",
            value=cache_state,
        )
    sampling = value["sampling_config"]
    if not isinstance(sampling, dict):
        raise _fail(
            "sampling_config must be an object",
            "comparison.sampling_config",
        )
    try:
        canonical_json_bytes(sampling)
    except ValueError as exc:
        raise _fail(
            "sampling_config is not canonical JSON-compatible",
            "comparison.sampling_config",
        ) from exc

    return ComparisonConditions(
        score_surface=surface,
        measurement_protocol=value["measurement_protocol"],
        task_id=value["task_id"],
        task_manifest_revision=value["task_manifest_revision"],
        verifier_set_id=value["verifier_set_id"],
        timeout_seconds=timeout,
        cache_state=cache_state,
        hardware_class=value["hardware_class"],
        context_length=context_length,
        interaction_contract_version=value["interaction_contract_version"],
        sampling_config=dict(sampling),
    )


def comparability_mismatches(
    left: ComparisonConditions,
    right: ComparisonConditions,
) -> tuple[str, ...]:
    mismatches: list[str] = []
    left_map = left.as_mapping()
    right_map = right.as_mapping()
    for field in _FIELDS:
        if field == "sampling_config":
            if canonical_json_bytes(left_map[field]) != canonical_json_bytes(right_map[field]):
                mismatches.append(field)
        elif left_map[field] != right_map[field]:
            mismatches.append(field)
    return tuple(mismatches)


def assert_comparable(
    left: ComparisonConditions,
    right: ComparisonConditions,
) -> None:
    mismatches = comparability_mismatches(left, right)
    if mismatches:
        raise _fail(
            "score records are not directly comparable",
            "comparison.mismatch",
            fields=",".join(mismatches),
        )


def comparability_key(conditions: ComparisonConditions) -> str:
    return stable_id("comparison", canonical_json_bytes(conditions.as_mapping()))


def partition_comparable(
    records: Iterable[ComparisonConditions],
) -> dict[str, tuple[ComparisonConditions, ...]]:
    groups: dict[str, list[ComparisonConditions]] = {}
    for record in records:
        key = comparability_key(record)
        groups.setdefault(key, []).append(record)
    return {key: tuple(groups[key]) for key in sorted(groups)}


def validate_ttvc_summary(
    *,
    verified_completion_rate: float,
    timeout_seconds: int,
    median_ttvc_ms: float | None,
) -> None:
    if (
        isinstance(verified_completion_rate, bool)
        or not isinstance(verified_completion_rate, (int, float))
        or not math.isfinite(verified_completion_rate)
        or not 0 <= verified_completion_rate <= 1
    ):
        raise _fail(
            "verified_completion_rate must be between zero and one",
            "comparison.solve_rate",
        )
    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int)
        or timeout_seconds <= 0
    ):
        raise _fail("timeout_seconds must be positive", "comparison.timeout")
    if median_ttvc_ms is not None:
        if (
            isinstance(median_ttvc_ms, bool)
            or not isinstance(median_ttvc_ms, (int, float))
            or not math.isfinite(median_ttvc_ms)
            or median_ttvc_ms < 0
        ):
            raise _fail(
                "median_ttvc_ms must be non-negative or null",
                "comparison.ttvc",
            )
        if verified_completion_rate == 0:
            raise _fail(
                "median TTVC cannot be reported with zero verified completions",
                "comparison.ttvc_without_success",
            )
