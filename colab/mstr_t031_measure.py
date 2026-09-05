#!/usr/bin/env python3
"""T031 process-cold CPU measurement primitives and deterministic statistics."""

from __future__ import annotations

import json
import math
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

from mstr_executor_toolchain import sanitized_runtime_environment
from mstr_t031_governance import ExecutionError


def _read_meminfo() -> dict[str, int]:
    result: dict[str, int] = {}
    for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
        name, value = line.split(":", 1)
        fields = value.strip().split()
        if not fields:
            continue
        number = int(fields[0])
        result[name] = number * 1024 if len(fields) > 1 and fields[1] == "kB" else number
    return result


def _read_vmstat() -> dict[str, int]:
    result: dict[str, int] = {}
    for line in Path("/proc/vmstat").read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if len(fields) == 2:
            result[fields[0]] = int(fields[1])
    return result


def _process_sample(pid: int) -> dict[str, int]:
    result = {"rss_bytes": 0, "swap_bytes": 0, "hwm_bytes": 0, "majflt": 0}
    status = Path(f"/proc/{pid}/status")
    if status.is_file():
        for line in status.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("VmRSS:"):
                result["rss_bytes"] = int(line.split()[1]) * 1024
            elif line.startswith("VmSwap:"):
                result["swap_bytes"] = int(line.split()[1]) * 1024
            elif line.startswith("VmHWM:"):
                result["hwm_bytes"] = int(line.split()[1]) * 1024
    stat_path = Path(f"/proc/{pid}/stat")
    if stat_path.is_file():
        fields = stat_path.read_text(encoding="utf-8", errors="replace").split()
        if len(fields) > 11:
            result["majflt"] = int(fields[11])
    return result


def _parse_benchmark_row(
    stdout: str,
    *,
    model: Path,
    prompt_tokens: int,
    generated_tokens: int,
    threads: int,
    runtime_commit: str,
) -> dict[str, object]:
    try:
        payload: Any = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ExecutionError("llama-bench stdout is not valid JSON") from exc
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise ExecutionError("llama-bench JSON must contain exactly one result object")
    row = payload[0]
    expected = {
        "n_prompt": prompt_tokens,
        "n_gen": generated_tokens,
        "n_threads": threads,
        "n_gpu_layers": 0,
        "devices": "none",
        "model_filename": str(model),
    }
    for key, value in expected.items():
        if row.get(key) != value:
            raise ExecutionError(
                f"llama-bench identity mismatch for {key}: expected {value!r}, got {row.get(key)!r}"
            )
    build_commit = row.get("build_commit")
    if not isinstance(build_commit, str) or not runtime_commit.startswith(build_commit):
        raise ExecutionError("llama-bench build commit does not match pinned runtime commit")
    avg_ns = row.get("avg_ns")
    avg_ts = row.get("avg_ts")
    if isinstance(avg_ns, bool) or not isinstance(avg_ns, int) or avg_ns <= 0:
        raise ExecutionError("llama-bench avg_ns must be a positive integer")
    if isinstance(avg_ts, bool) or not isinstance(avg_ts, (int, float)):
        raise ExecutionError("llama-bench avg_ts must be numeric")
    avg_ts_float = float(avg_ts)
    if not math.isfinite(avg_ts_float) or avg_ts_float <= 0:
        raise ExecutionError("llama-bench avg_ts must be finite and positive")
    return {
        "avg_ns": avg_ns,
        "avg_tokens_per_second": avg_ts_float,
        "build_commit": build_commit,
    }


def _bench_once(
    *,
    executable: Path,
    model: Path,
    prompt_tokens: int,
    generated_tokens: int,
    threads: int,
    runtime_commit: str,
    timeout: float,
) -> dict[str, object]:
    argv = [
        str(executable),
        "-m",
        str(model),
        "-p",
        str(prompt_tokens),
        "-n",
        str(generated_tokens),
        "-t",
        str(threads),
        "-ngl",
        "0",
        "-r",
        "1",
        "--device",
        "none",
        "-o",
        "json",
    ]
    before_mem = _read_meminfo()
    before_vm = _read_vmstat()
    started = time.monotonic()
    process = subprocess.Popen(
        argv,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=sanitized_runtime_environment(),
    )
    peak_rss = 0
    peak_swap = 0
    peak_hwm = 0
    peak_majflt = 0
    min_available = before_mem.get("MemAvailable", 0)
    while process.poll() is None:
        if time.monotonic() - started > timeout:
            process.kill()
            process.wait(timeout=10)
            raise ExecutionError(f"llama-bench timed out after {timeout}s")
        sample = _process_sample(process.pid)
        peak_rss = max(peak_rss, sample["rss_bytes"])
        peak_swap = max(peak_swap, sample["swap_bytes"])
        peak_hwm = max(peak_hwm, sample["hwm_bytes"])
        peak_majflt = max(peak_majflt, sample["majflt"])
        current_mem = _read_meminfo()
        min_available = min(min_available, current_mem.get("MemAvailable", min_available))
        time.sleep(0.05)
    stdout, stderr = process.communicate(timeout=10)
    wall_seconds = time.monotonic() - started
    if process.returncode != 0:
        diagnostic = (stdout + "\n" + stderr).strip()[-4000:]
        raise ExecutionError(f"llama-bench failed ({process.returncode}): {diagnostic}")
    parsed = _parse_benchmark_row(
        stdout,
        model=model,
        prompt_tokens=prompt_tokens,
        generated_tokens=generated_tokens,
        threads=threads,
        runtime_commit=runtime_commit,
    )
    after_mem = _read_meminfo()
    after_vm = _read_vmstat()
    benchmark_seconds = int(parsed["avg_ns"]) / 1_000_000_000
    return {
        **parsed,
        "process_wall_seconds": wall_seconds,
        "estimated_load_and_process_startup_seconds": max(0.0, wall_seconds - benchmark_seconds),
        "process_peak_rss_bytes": peak_rss,
        "process_peak_swap_bytes": peak_swap,
        "process_peak_hwm_bytes": peak_hwm,
        "process_peak_major_faults": peak_majflt,
        "system_total_ram_bytes": before_mem.get("MemTotal"),
        "system_available_memory_before_bytes": before_mem.get("MemAvailable"),
        "system_available_memory_after_bytes": after_mem.get("MemAvailable"),
        "system_min_available_memory_bytes": min_available,
        "system_swap_total_bytes": before_mem.get("SwapTotal"),
        "system_swap_free_before_bytes": before_mem.get("SwapFree"),
        "system_swap_free_after_bytes": after_mem.get("SwapFree"),
        "system_pgmajfault_delta": after_vm.get("pgmajfault", 0) - before_vm.get("pgmajfault", 0),
        "system_pswpin_delta": after_vm.get("pswpin", 0) - before_vm.get("pswpin", 0),
        "system_pswpout_delta": after_vm.get("pswpout", 0) - before_vm.get("pswpout", 0),
    }


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(fraction * len(ordered)) - 1))
    return ordered[index]


def _stats(values: list[float]) -> dict[str, object]:
    if not values:
        raise ExecutionError("cannot summarize an empty measurement list")
    return {
        "sample_count": len(values),
        "median": statistics.median(values),
        "p90": _percentile(values, 0.90),
        "min": min(values),
        "max": max(values),
    }


def _summarize_runs(runs: list[dict[str, object]]) -> dict[str, object]:
    fields = [
        "avg_tokens_per_second",
        "process_wall_seconds",
        "estimated_load_and_process_startup_seconds",
        "process_peak_rss_bytes",
        "process_peak_swap_bytes",
        "process_peak_hwm_bytes",
        "process_peak_major_faults",
        "system_min_available_memory_bytes",
        "system_pgmajfault_delta",
        "system_pswpin_delta",
        "system_pswpout_delta",
    ]
    summary: dict[str, object] = {}
    for field in fields:
        values = [float(run[field]) for run in runs if isinstance(run.get(field), (int, float))]
        summary[field] = _stats(values)
    return summary


def _measure_set(
    *,
    executable: Path,
    model: Path,
    prompt_tokens: int,
    generated_tokens: int,
    threads: int,
    runtime_commit: str,
    warmups: int,
    measured: int,
) -> dict[str, object]:
    for _ in range(warmups):
        _bench_once(
            executable=executable,
            model=model,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            timeout=900,
        )
    runs = [
        _bench_once(
            executable=executable,
            model=model,
            prompt_tokens=prompt_tokens,
            generated_tokens=generated_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            timeout=900,
        )
        for _ in range(measured)
    ]
    return {
        "warmups_excluded": warmups,
        "measured_repetitions": measured,
        "runs": runs,
        "statistics": _summarize_runs(runs),
    }
