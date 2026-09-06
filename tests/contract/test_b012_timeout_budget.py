from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_measure as measure  # noqa: E402
from mstr_t031_governance import ExecutionError as T031ExecutionError  # noqa: E402


def _sample() -> dict[str, object]:
    return {
        "avg_ns": 1_000_000_000,
        "avg_tokens_per_second": 10.0,
        "build_commit": "3173a56",
        "process_wall_seconds": 1.0,
        "estimated_load_and_process_startup_seconds": 0.0,
        "process_peak_rss_bytes": 1,
        "process_peak_swap_bytes": 0,
        "process_peak_hwm_bytes": 1,
        "process_peak_major_faults": 0,
        "system_total_ram_bytes": 1,
        "system_available_memory_before_bytes": 1,
        "system_available_memory_after_bytes": 1,
        "system_min_available_memory_bytes": 1,
        "system_swap_total_bytes": 0,
        "system_swap_free_before_bytes": 0,
        "system_swap_free_after_bytes": 0,
        "system_pgmajfault_delta": 0,
        "system_pswpin_delta": 0,
        "system_pswpout_delta": 0,
    }


def test_budget_matches_authorized_job_ceiling() -> None:
    runtime_cfg: dict[str, object] = {
        "per_invocation_timeout_seconds": 900,
        "benchmark_wall_budget_seconds": 4800,
        "reserved_non_benchmark_seconds": 2400,
        "authorized_job_ceiling_seconds": 7200,
    }
    observed = measure.validate_benchmark_budget(runtime_cfg=runtime_cfg, max_job_minutes=120)
    assert observed == runtime_cfg


def test_budget_rejects_aggregate_overrun() -> None:
    runtime_cfg: dict[str, object] = {
        "per_invocation_timeout_seconds": 900,
        "benchmark_wall_budget_seconds": 5000,
        "reserved_non_benchmark_seconds": 2400,
        "authorized_job_ceiling_seconds": 7200,
    }
    with pytest.raises(measure.ExecutionError, match="exceed the authorized job ceiling"):
        measure.validate_benchmark_budget(runtime_cfg=runtime_cfg, max_job_minutes=120)


def test_bounded_measurement_preserves_frozen_repetition_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[float] = []

    def fake_bench_once(**kwargs: object) -> dict[str, object]:
        timeout = kwargs["timeout"]
        assert isinstance(timeout, float)
        calls.append(timeout)
        return _sample()

    monkeypatch.setattr(measure, "_bench_once", fake_bench_once)
    result = measure.measure_set_bounded(
        arm="prefill_8k",
        executable=Path("llama-bench"),
        model=Path("model.gguf"),
        prompt_tokens=8192,
        generated_tokens=0,
        threads=2,
        runtime_commit="3173a56471c1753650cd806694145ffd6dcace67",
        warmups=1,
        measured=3,
        configured_timeout_seconds=900,
        budget_seconds=4800,
        benchmark_started_monotonic=0.0,
        monotonic=lambda: 0.0,
    )
    assert calls == [900.0, 900.0, 900.0, 900.0]
    assert result["warmups_excluded"] == 1
    assert result["measured_repetitions"] == 3
    runs = result["runs"]
    assert isinstance(runs, list)
    assert len(runs) == 3
    for index, run in enumerate(runs):
        assert isinstance(run, dict)
        context = run["b012_invocation_context"]
        assert isinstance(context, dict)
        assert context["benchmark_arm"] == "prefill_8k"
        assert context["benchmark_phase"] == "measured"
        assert context["repetition_index"] == index


def test_timeout_failure_records_exact_arm_phase_and_repetition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def timeout_bench_once(**kwargs: object) -> dict[str, object]:
        raise T031ExecutionError(f"llama-bench timed out after {kwargs['timeout']}s")

    monkeypatch.setattr(measure, "_bench_once", timeout_bench_once)
    with pytest.raises(measure.B012BenchmarkError) as captured:
        measure.measure_set_bounded(
            arm="isolated_decode_128",
            executable=Path("llama-bench"),
            model=Path("model.gguf"),
            prompt_tokens=0,
            generated_tokens=128,
            threads=2,
            runtime_commit="3173a56471c1753650cd806694145ffd6dcace67",
            warmups=1,
            measured=3,
            configured_timeout_seconds=900,
            budget_seconds=4800,
            benchmark_started_monotonic=0.0,
            monotonic=lambda: 0.0,
        )
    context = captured.value.context
    assert context["benchmark_arm"] == "isolated_decode_128"
    assert context["benchmark_phase"] == "warmup_excluded"
    assert context["repetition_index"] == 0
    assert context["configured_per_invocation_timeout_seconds"] == 900
    assert context["effective_invocation_timeout_seconds"] == 900.0


def test_wall_budget_exhaustion_fails_before_launch(monkeypatch: pytest.MonkeyPatch) -> None:
    launched = False

    def forbidden_bench_once(**kwargs: object) -> dict[str, object]:
        nonlocal launched
        launched = True
        return _sample()

    monkeypatch.setattr(measure, "_bench_once", forbidden_bench_once)
    with pytest.raises(measure.B012BenchmarkError) as captured:
        measure.measure_set_bounded(
            arm="prefill_8k",
            executable=Path("llama-bench"),
            model=Path("model.gguf"),
            prompt_tokens=8192,
            generated_tokens=0,
            threads=2,
            runtime_commit="3173a56471c1753650cd806694145ffd6dcace67",
            warmups=1,
            measured=3,
            configured_timeout_seconds=900,
            budget_seconds=4800,
            benchmark_started_monotonic=0.0,
            monotonic=lambda: 4801.0,
        )
    assert launched is False
    assert captured.value.context["effective_invocation_timeout_seconds"] == 0.0
    assert captured.value.context["benchmark_remaining_before_seconds"] == -1.0


def test_remaining_budget_caps_effective_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    observed_timeouts: list[float] = []

    def timeout_bench_once(**kwargs: object) -> dict[str, object]:
        timeout = kwargs["timeout"]
        assert isinstance(timeout, float)
        observed_timeouts.append(timeout)
        raise T031ExecutionError("synthetic budget-capped timeout")

    monkeypatch.setattr(measure, "_bench_once", timeout_bench_once)
    with pytest.raises(measure.B012BenchmarkError) as captured:
        measure.measure_set_bounded(
            arm="prefill_8k",
            executable=Path("llama-bench"),
            model=Path("model.gguf"),
            prompt_tokens=8192,
            generated_tokens=0,
            threads=2,
            runtime_commit="3173a56471c1753650cd806694145ffd6dcace67",
            warmups=1,
            measured=3,
            configured_timeout_seconds=900,
            budget_seconds=4800,
            benchmark_started_monotonic=0.0,
            monotonic=lambda: 4799.75,
        )
    assert observed_timeouts == [pytest.approx(0.25)]
    context = captured.value.context
    assert context["configured_per_invocation_timeout_seconds"] == 900
    assert context["benchmark_remaining_before_seconds"] == pytest.approx(0.25)
    assert context["effective_invocation_timeout_seconds"] == pytest.approx(0.25)
