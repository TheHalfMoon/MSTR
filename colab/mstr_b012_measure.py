#!/usr/bin/env python3
"""B012-specific bounded CPU benchmark orchestration and failure diagnostics."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from pathlib import Path

from mstr_b012_governance import ExecutionError
from mstr_t031_governance import ExecutionError as T031ExecutionError
from mstr_t031_measure import _bench_once, _summarize_runs


class B012BenchmarkError(ExecutionError):
    """Fail-closed benchmark error carrying the exact invocation identity."""

    def __init__(self, message: str, *, context: dict[str, object]) -> None:
        super().__init__(message)
        self.context = context


def validate_benchmark_budget(
    *, runtime_cfg: dict[str, object], max_job_minutes: object
) -> dict[str, int]:
    """Validate that the frozen benchmark budget fits inside the authorized job ceiling."""
    keys = (
        "per_invocation_timeout_seconds",
        "benchmark_wall_budget_seconds",
        "reserved_non_benchmark_seconds",
        "authorized_job_ceiling_seconds",
    )
    values: dict[str, int] = {}
    for key in keys:
        value = runtime_cfg.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ExecutionError(f"B012 benchmark budget value is invalid: {key}")
        values[key] = value

    if isinstance(max_job_minutes, bool) or not isinstance(max_job_minutes, int):
        raise ExecutionError("B012 runner max_job_minutes is invalid")
    if max_job_minutes <= 0:
        raise ExecutionError("B012 runner max_job_minutes must be positive")

    authorized_job_seconds = max_job_minutes * 60
    if values["authorized_job_ceiling_seconds"] != authorized_job_seconds:
        raise ExecutionError("B012 authorized job ceiling does not match runner timeout")
    if (
        values["benchmark_wall_budget_seconds"]
        + values["reserved_non_benchmark_seconds"]
        > values["authorized_job_ceiling_seconds"]
    ):
        raise ExecutionError("B012 benchmark and reserve budgets exceed the authorized job ceiling")
    if values["per_invocation_timeout_seconds"] > values["benchmark_wall_budget_seconds"]:
        raise ExecutionError("B012 per-invocation timeout exceeds the benchmark wall budget")
    return values


def effective_benchmark_wall_budget(
    *, budget: dict[str, int], pre_benchmark_elapsed_seconds: float
) -> float:
    """Clamp benchmark time so the full locked non-benchmark reserve remains after setup."""
    if not math.isfinite(pre_benchmark_elapsed_seconds) or pre_benchmark_elapsed_seconds < 0:
        raise ExecutionError("B012 pre-benchmark elapsed time is invalid")
    available_after_setup_and_reserve = (
        float(budget["authorized_job_ceiling_seconds"])
        - float(budget["reserved_non_benchmark_seconds"])
        - pre_benchmark_elapsed_seconds
    )
    effective = min(
        float(budget["benchmark_wall_budget_seconds"]), available_after_setup_and_reserve
    )
    if effective <= 0:
        raise ExecutionError(
            "B012 non-benchmark reserve cannot be preserved before benchmark launch"
        )
    return effective


def _context(
    *,
    arm: str,
    phase: str,
    repetition_index: int,
    configured_timeout_seconds: int,
    effective_timeout_seconds: float,
    budget_seconds: float,
    elapsed_before_seconds: float,
    remaining_before_seconds: float,
    elapsed_after_seconds: float | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "benchmark_arm": arm,
        "benchmark_phase": phase,
        "repetition_index": repetition_index,
        "configured_per_invocation_timeout_seconds": configured_timeout_seconds,
        "effective_invocation_timeout_seconds": effective_timeout_seconds,
        "benchmark_wall_budget_seconds": budget_seconds,
        "benchmark_elapsed_before_seconds": elapsed_before_seconds,
        "benchmark_remaining_before_seconds": remaining_before_seconds,
    }
    if elapsed_after_seconds is not None:
        payload["benchmark_elapsed_after_seconds"] = elapsed_after_seconds
        payload["benchmark_remaining_after_seconds"] = max(
            0.0, budget_seconds - elapsed_after_seconds
        )
    return payload


def _run_one(
    *,
    arm: str,
    phase: str,
    repetition_index: int,
    executable: Path,
    model: Path,
    prompt_tokens: int,
    generated_tokens: int,
    threads: int,
    runtime_commit: str,
    configured_timeout_seconds: int,
    budget_seconds: float,
    benchmark_started_monotonic: float,
    monotonic: Callable[[], float],
) -> dict[str, object]:
    elapsed_before = max(0.0, monotonic() - benchmark_started_monotonic)
    remaining_before = budget_seconds - elapsed_before
    if remaining_before <= 0:
        context = _context(
            arm=arm,
            phase=phase,
            repetition_index=repetition_index,
            configured_timeout_seconds=configured_timeout_seconds,
            effective_timeout_seconds=0.0,
            budget_seconds=budget_seconds,
            elapsed_before_seconds=elapsed_before,
            remaining_before_seconds=remaining_before,
        )
        raise B012BenchmarkError(
            "B012 benchmark wall budget exhausted before the next invocation",
            context=context,
        )

    effective_timeout = min(float(configured_timeout_seconds), remaining_before)
    invocation_context = _context(
        arm=arm,
        phase=phase,
        repetition_index=repetition_index,
        configured_timeout_seconds=configured_timeout_seconds,
        effective_timeout_seconds=effective_timeout,
        budget_seconds=budget_seconds,
        elapsed_before_seconds=elapsed_before,
        remaining_before_seconds=remaining_before,
    )
    try:
        result = _bench_once(
            executable=executable,
            model=model,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            timeout=effective_timeout,
        )
    except T031ExecutionError as exc:
        elapsed_after = max(0.0, monotonic() - benchmark_started_monotonic)
        context = _context(
            arm=arm,
            phase=phase,
            repetition_index=repetition_index,
            configured_timeout_seconds=configured_timeout_seconds,
            effective_timeout_seconds=effective_timeout,
            budget_seconds=budget_seconds,
            elapsed_before_seconds=elapsed_before,
            remaining_before_seconds=remaining_before,
            elapsed_after_seconds=elapsed_after,
        )
        raise B012BenchmarkError(
            f"B012 benchmark invocation failed closed: {exc}", context=context
        ) from exc

    elapsed_after = max(0.0, monotonic() - benchmark_started_monotonic)
    result = dict(result)
    result["b012_invocation_context"] = {
        **invocation_context,
        "benchmark_elapsed_after_seconds": elapsed_after,
        "benchmark_remaining_after_seconds": max(0.0, budget_seconds - elapsed_after),
    }
    return result


def measure_set_bounded(
    *,
    arm: str,
    executable: Path,
    model: Path,
    prompt_tokens: int,
    generated_tokens: int,
    threads: int,
    runtime_commit: str,
    warmups: int,
    measured: int,
    configured_timeout_seconds: int,
    budget_seconds: float,
    benchmark_started_monotonic: float,
    monotonic: Callable[[], float] = time.monotonic,
) -> dict[str, object]:
    """Run one frozen T031-equivalent arm under the B012 aggregate wall budget."""
    if warmups < 0 or measured <= 0:
        raise ExecutionError("B012 benchmark repetition counts are invalid")

    for repetition_index in range(warmups):
        _run_one(
            arm=arm,
            phase="warmup_excluded",
            repetition_index=repetition_index,
            executable=executable,
            model=model,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            configured_timeout_seconds=configured_timeout_seconds,
            budget_seconds=budget_seconds,
            benchmark_started_monotonic=benchmark_started_monotonic,
            monotonic=monotonic,
        )

    runs = [
        _run_one(
            arm=arm,
            phase="measured",
            repetition_index=repetition_index,
            executable=executable,
            model=model,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            configured_timeout_seconds=configured_timeout_seconds,
            budget_seconds=budget_seconds,
            benchmark_started_monotonic=benchmark_started_monotonic,
            monotonic=monotonic,
        )
        for repetition_index in range(measured)
    ]
    return {
        "warmups_excluded": warmups,
        "measured_repetitions": measured,
        "runs": runs,
        "statistics": _summarize_runs(runs),
    }
