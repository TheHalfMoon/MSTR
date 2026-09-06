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
    LOCK_PATH,
    RAW_CODE_PATH,
    T031_LOCK_PATH,
    T031_REPLAY_OVERLAY_PATH,
    ExecutionError,
    _require_binding,
    _require_live_main,
)
from mstr_b012_raw_code import run_raw_code_proxy
from mstr_b012_source import download_candidate
from mstr_executor_toolchain import ToolchainError, read_json, sha256_file
from mstr_t031_measure import _measure_set
from mstr_t031_replay import install_replay_toolchain


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = output_dir / f"B012-{args.candidate}-failure.json"
    workdir = args.workdir.resolve()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = "UNKNOWN"
    replay_identity: dict[str, object] | None = None
    try:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)
        head = _require_live_main(repo_root)
        binding, envelope, lock = _require_binding(repo_root)
        if args.candidate not in binding.get("candidate_ids", []):
            raise ExecutionError(f"candidate outside exact B012 authority: {args.candidate}")

        python_exe, replay_identity = install_replay_toolchain(
            base_lock_path=repo_root / T031_LOCK_PATH,
            overlay_path=repo_root / T031_REPLAY_OVERLAY_PATH,
            root=workdir / "python",
        )
        conversion_dir, quantizer, bench, cli, tool_identity = prepare_tools(lock=lock, workdir=workdir)
        _require_live_main(repo_root)
        source_dir = workdir / "source" / args.candidate
        source_records = download_candidate(
            repo_root=repo_root,
            envelope=envelope,
            candidate_id=args.candidate,
            destination=source_dir,
        )
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
        warmups = runtime_cfg.get("warmups_excluded")
        measured = runtime_cfg.get("measured_repetitions")
        threads = runtime_cfg.get("threads")
        prompt_tokens = runtime_cfg.get("prompt_tokens")
        decode_tokens = runtime_cfg.get("decode_tokens")
        if not all(isinstance(value, int) for value in (warmups, measured, threads, prompt_tokens, decode_tokens)):
            raise ExecutionError("B012 runtime benchmark integers are invalid")
        runtime_commit = str(tool_identity["runtime_commit"])
        prefill = _measure_set(
            executable=bench,
            model=q4,
            prompt_tokens=prompt_tokens,
            generated_tokens=0,
            threads=threads,
            runtime_commit=runtime_commit,
            warmups=warmups,
            measured=measured,
        )
        decode = _measure_set(
            executable=bench,
            model=q4,
            prompt_tokens=0,
            generated_tokens=decode_tokens,
            threads=threads,
            runtime_commit=runtime_commit,
            warmups=warmups,
            measured=measured,
        )
        raw_manifest = read_json(repo_root / RAW_CODE_PATH)
        raw_code = run_raw_code_proxy(executable=cli, model=q4, manifest=raw_manifest)
        canonical_end = _require_live_main(repo_root)

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
            "runtime_resource": {"prefill_8k": prefill, "isolated_decode_128": decode},
            "raw_code_proxy": raw_code,
        }
        _write(output_dir / f"B012-{args.candidate}-qualification.json", result)
        failure_path.unlink(missing_ok=True)
        return 0
    except (ExecutionError, ToolchainError, RuntimeError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        _write(failure_path, {
            "schema_version": "mstr.b012-equivalent-qualification-failure.v1",
            "task_id": "B012",
            "candidate_id": args.candidate,
            "result_classification": "B012_EXECUTION_FAILED_CLOSED",
            "canonical_main_at_start": head,
            "started_utc": started_utc,
            "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "producer_replay": replay_identity,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "paid_cost_usd": 0.0,
            "training": False,
        })
        return 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, choices=["mellum-4b", "qwen3.5-0.8b-control"])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "mstr-b012")
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
