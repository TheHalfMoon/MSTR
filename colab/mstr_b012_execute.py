#!/usr/bin/env python3
"""Governed B012 equivalent qualification on one ephemeral CPU runner."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from pathlib import Path

from mstr_b012_artifacts import convert_quantize, prepare_tools
from mstr_b012_governance import (
    RAW_CODE_PATH,
    T031_LOCK_PATH,
    T031_REPLAY_OVERLAY_PATH,
    ExecutionError,
    _require_binding,
    _require_live_main,
)
from mstr_b012_measure import (
    B012BenchmarkError,
    effective_benchmark_wall_budget,
    measure_set_bounded,
    validate_benchmark_budget,
)
from mstr_b012_raw_code import run_raw_code_proxy
from mstr_b012_source import download_candidate
from mstr_executor_toolchain import ToolchainError, read_json, sha256_file
from mstr_t031_replay import install_replay_toolchain


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _runtime_integer(runtime_cfg: dict[str, object], key: str) -> int:
    value = runtime_cfg.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ExecutionError(f"B012 runtime benchmark integer is invalid: {key}")
    return value


def execute(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = output_dir / f"B012-{args.candidate}-failure.json"
    workdir = args.workdir.resolve()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    execution_started_monotonic = time.monotonic()
    head = "UNKNOWN"
    replay_identity: dict[str, object] | None = None
    execution_stage = "INITIALIZATION"
    benchmark_context: dict[str, object] | None = None
    try:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)

        execution_stage = "CANONICAL_GOVERNANCE"
        head = _require_live_main(repo_root)
        binding, envelope, lock = _require_binding(repo_root)
        if args.candidate not in binding.get("candidate_ids", []):
            raise ExecutionError(f"candidate outside exact B012 authority: {args.candidate}")

        execution_stage = "REPLAY_TOOLCHAIN"
        python_exe, replay_identity = install_replay_toolchain(
            base_lock_path=repo_root / T031_LOCK_PATH,
            overlay_path=repo_root / T031_REPLAY_OVERLAY_PATH,
            root=workdir / "python",
        )

        execution_stage = "RUNTIME_TOOLCHAIN"
        conversion_dir, quantizer, bench, cli, tool_identity = prepare_tools(
            lock=lock, workdir=workdir
        )
        _require_live_main(repo_root)

        execution_stage = "SOURCE_DOWNLOAD"
        source_dir = workdir / "source" / args.candidate
        source_records = download_candidate(
            repo_root=repo_root,
            envelope=envelope,
            candidate_id=args.candidate,
            destination=source_dir,
        )

        execution_stage = "CONVERT_AND_QUANTIZE"
        q4, quantization = convert_quantize(
            python_exe=python_exe,
            conversion_dir=conversion_dir,
            quantize_bin=quantizer,
            source_dir=source_dir,
            candidate_id=args.candidate,
            workdir=workdir,
        )
        q4_sha = sha256_file(q4)
        q4_size = q4.stat().st_size

        task_binding = lock.get("task_binding")
        if not isinstance(task_binding, dict):
            raise ExecutionError("B012 task binding is missing")
        runtime_cfg = task_binding.get("runtime_benchmark")
        if not isinstance(runtime_cfg, dict):
            raise ExecutionError("B012 runtime benchmark binding is missing")
        runner_cfg = lock.get("runner")
        if not isinstance(runner_cfg, dict):
            raise ExecutionError("B012 runner binding is missing")

        warmups = _runtime_integer(runtime_cfg, "warmups_excluded")
        measured = _runtime_integer(runtime_cfg, "measured_repetitions")
        threads = _runtime_integer(runtime_cfg, "threads")
        prompt_tokens = _runtime_integer(runtime_cfg, "prompt_tokens")
        decode_tokens = _runtime_integer(runtime_cfg, "decode_tokens")
        budget = validate_benchmark_budget(
            runtime_cfg=runtime_cfg,
            max_job_minutes=runner_cfg.get("max_job_minutes"),
        )
        execution_stage = "RUNTIME_BENCHMARK_BUDGET"
        pre_benchmark_elapsed_seconds = max(0.0, time.monotonic() - execution_started_monotonic)
        effective_benchmark_budget_seconds = effective_benchmark_wall_budget(
            budget=budget,
            pre_benchmark_elapsed_seconds=pre_benchmark_elapsed_seconds,
        )
        runtime_budget_observation: dict[str, object] = {
            **budget,
            "pre_benchmark_elapsed_seconds": pre_benchmark_elapsed_seconds,
            "effective_benchmark_wall_budget_seconds": effective_benchmark_budget_seconds,
        }
        runtime_commit = str(tool_identity["runtime_commit"])
        benchmark_started = execution_started_monotonic + pre_benchmark_elapsed_seconds

        execution_stage = "RUNTIME_BENCHMARK_PREFILL"
        prefill = measure_set_bounded(
            arm="prefill_8k",
            executable=bench,
            model=q4,
            prompt_tokens=prompt_tokens,
            generated_tokens=0,
            threads=threads,
            runtime_commit=runtime_commit,
            warmups=warmups,
            measured=measured,
            configured_timeout_seconds=budget["per_invocation_timeout_seconds"],
            budget_seconds=effective_benchmark_budget_seconds,
            benchmark_started_monotonic=benchmark_started,
        )

        execution_stage = "RUNTIME_BENCHMARK_DECODE"
        decode = measure_set_bounded(
            arm="isolated_decode_128",
            executable=bench,
            model=q4,
            prompt_tokens=0,
            generated_tokens=decode_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            warmups=warmups,
            measured=measured,
            configured_timeout_seconds=budget["per_invocation_timeout_seconds"],
            budget_seconds=effective_benchmark_budget_seconds,
            benchmark_started_monotonic=benchmark_started,
        )

        execution_stage = "RAW_CODE_PROXY"
        raw_manifest = read_json(repo_root / RAW_CODE_PATH)
        raw_code = run_raw_code_proxy(executable=cli, model=q4, manifest=raw_manifest)

        execution_stage = "FINAL_LIVE_MAIN_GUARD"
        canonical_end = _require_live_main(repo_root)

        execution_stage = "EVIDENCE_SERIALIZATION"
        q4_manifest = {
            "schema_version": "mstr.b012-q4-profile.v1",
            "task_id": "B012",
            "candidate_id": args.candidate,
            "source_main": head,
            "tool_identity": tool_identity,
            "producer_replay": replay_identity,
            "quantization": quantization,
            "primary_q4_k_m_sha256": q4_sha,
            "primary_q4_k_m_size_bytes": q4_size,
            "q4_k_m_le_3gb_observation": q4_size <= 3_000_000_000,
        }
        q4_path = output_dir / f"B012-{args.candidate}-q4.json"
        _write(q4_path, q4_manifest)
        result = {
            "schema_version": "mstr.b012-equivalent-qualification-result.v1",
            "task_id": "B012",
            "candidate_id": args.candidate,
            "result_classification": "B012_EQUIVALENT_EVIDENCE_COMPLETE",
            "candidate_admission_decision": "NOT_MADE_BY_B012_EXECUTOR",
            "canonical_main_at_start": head,
            "canonical_main_at_end": canonical_end,
            "started_utc": started_utc,
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "paid_cost_usd": 0.0,
            "training": False,
            "source_verification": source_records,
            "producer_replay": replay_identity,
            "tool_identity": tool_identity,
            "q4_manifest_sha256": sha256_file(q4_path),
            "q4_k_m_sha256": q4_sha,
            "q4_k_m_size_bytes": q4_size,
            "hosted_lane_claim": "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM",
            "runtime_benchmark_budget": runtime_budget_observation,
            "runtime_resource": {"prefill_8k": prefill, "isolated_decode_128": decode},
            "raw_code_proxy": raw_code,
        }
        _write(output_dir / f"B012-{args.candidate}-qualification.json", result)
        failure_path.unlink(missing_ok=True)
        return 0
    except (
        ExecutionError,
        ToolchainError,
        RuntimeError,
        OSError,
        ValueError,
        KeyError,
        json.JSONDecodeError,
    ) as exc:
        if isinstance(exc, B012BenchmarkError):
            benchmark_context = exc.context
        failure: dict[str, object] = {
            "schema_version": "mstr.b012-equivalent-qualification-failure.v1",
            "task_id": "B012",
            "candidate_id": args.candidate,
            "result_classification": "B012_EXECUTION_FAILED_CLOSED",
            "canonical_main_at_start": head,
            "started_utc": started_utc,
            "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "execution_stage": execution_stage,
            "producer_replay": replay_identity,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "paid_cost_usd": 0.0,
            "training": False,
        }
        if benchmark_context is not None:
            failure["benchmark_context"] = benchmark_context
        _write(failure_path, failure)
        return 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, choices=["mellum-4b", "qwen3.5-0.8b-control"])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--workdir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "mstr-b012"
    )
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
