#!/usr/bin/env python3
"""Governed T031 local artifact/memory/throughput execution on an ephemeral CPU runner."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

from mstr_executor_toolchain import (
    ToolchainError,
    install_verified_python_toolchain,
    read_json,
    require_file_sha256,
    sha256_file,
)
from mstr_t031_artifacts import _prepare_llama_cpp, _quantize
from mstr_t031_governance import (
    LOCK_PATH,
    RUNTIME_PROFILE_PATH,
    ExecutionError,
    _require_binding,
    _require_live_main,
)
from mstr_t031_measure import _measure_set
from mstr_t031_source import _candidate_source, _download_candidate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = output_dir / f"T031-{args.candidate}-failure.json"
    workdir = args.workdir.resolve()

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    head = "UNKNOWN"
    try:
        if workdir.exists():
            shutil.rmtree(workdir)
        workdir.mkdir(parents=True)

        head = _require_live_main(repo_root)
        binding, envelope = _require_binding(repo_root)
        candidates = binding.get("candidate_ids")
        if not isinstance(candidates, list) or args.candidate not in candidates:
            raise ExecutionError(f"candidate is outside exact T031 authority: {args.candidate}")

        lock = read_json(repo_root / LOCK_PATH)
        task_binding = lock.get("task_binding")
        if not isinstance(task_binding, dict):
            raise ExecutionError("toolchain task binding is missing")
        contexts = task_binding.get("contexts")
        warmups = task_binding.get("warmups_excluded")
        measured = task_binding.get("measured_repetitions")
        decode_tokens = task_binding.get("decode_tokens")
        threads = task_binding.get("threads")
        if contexts != [4096, 8192, 16384]:
            raise ExecutionError("T031 context set drift detected")
        if (warmups, measured, decode_tokens, threads) != (2, 10, 128, 2):
            raise ExecutionError("T031 measurement protocol lock drift detected")

        q4_identity = envelope.get("q4_identity")
        runtime_identity = envelope.get("runtime_identity")
        if not isinstance(q4_identity, dict) or not isinstance(runtime_identity, dict):
            raise ExecutionError("T031 q4/runtime identity is missing")
        t029_manifest = q4_identity.get("t029_profile_manifest")
        runtime_profile = runtime_identity.get("profile")
        if not isinstance(t029_manifest, dict) or not isinstance(runtime_profile, dict):
            raise ExecutionError("T031 q4/runtime manifest binding is missing")
        for entry, path in (
            (t029_manifest, repo_root / "artifacts/manifests/quantization/T029-q4-profiles.json"),
            (runtime_profile, repo_root / RUNTIME_PROFILE_PATH),
        ):
            expected = entry.get("sha256")
            if not isinstance(expected, str):
                raise ExecutionError("canonical manifest SHA-256 is missing")
            require_file_sha256(path, expected)

        python_exe = install_verified_python_toolchain(repo_root / LOCK_PATH, workdir / "python")
        conversion_dir, quantize_bin, runtime_bin, tool_identity = _prepare_llama_cpp(
            lock=lock, workdir=workdir
        )

        # Recheck live main immediately before the first model-artifact byte is requested.
        _require_live_main(repo_root)
        source_dir = workdir / "source" / args.candidate
        source_records = _download_candidate(
            repo_root=repo_root,
            envelope=envelope,
            candidate_id=args.candidate,
            destination=source_dir,
        )

        source = _candidate_source(envelope, args.candidate)
        q4_profile = source.get("q4_profile")
        if not isinstance(q4_profile, dict):
            raise ExecutionError("candidate q4_profile is missing")
        if q4_profile.get("llama_cpp_commit") != tool_identity["conversion_quantization_commit"]:
            raise ExecutionError("candidate T029 quantizer commit does not match toolchain lock")

        q4_k_m, regeneration = _quantize(
            python_exe=python_exe,
            conversion_dir=conversion_dir,
            quantize_bin=quantize_bin,
            source_dir=source_dir,
            q4_profile=q4_profile,
            workdir=workdir,
        )
        q4_k_m_sha = sha256_file(q4_k_m)

        decode = _measure_set(
            executable=runtime_bin,
            model=q4_k_m,
            prompt_tokens=0,
            generated_tokens=decode_tokens,
            threads=threads,
            runtime_commit=str(tool_identity["runtime_commit"]),
            warmups=warmups,
            measured=measured,
        )

        rows: list[dict[str, object]] = []
        for context in contexts:
            require_file_sha256(q4_k_m, q4_k_m_sha)
            prefill = _measure_set(
                executable=runtime_bin,
                model=q4_k_m,
                prompt_tokens=context,
                generated_tokens=0,
                threads=threads,
                runtime_commit=str(tool_identity["runtime_commit"]),
                warmups=warmups,
                measured=measured,
            )
            rows.append(
                {
                    "schema_version": "mstr.t031-local-measurement.v1",
                    "task_id": "T031",
                    "candidate_id": args.candidate,
                    "context_tokens": context,
                    "run_state": "PROCESS_COLD_NATURAL_OS_CACHE",
                    "hosted_lane_claim": "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM",
                    "model_artifact": {
                        "quantization": "Q4_K_M",
                        "sha256": q4_k_m_sha,
                        "size_bytes": q4_k_m.stat().st_size,
                    },
                    "runtime": {
                        **tool_identity,
                        "threads": threads,
                        "gpu_layers": 0,
                        "device": "none",
                    },
                    "prefill": prefill,
                    "decode": decode,
                    "decode_semantics": "T030_ISOLATED_DECODE_COMPANION_NOT_POST_PREFILL_KV_CACHE",
                    "tokenizer_normalized_output_rates": (
                        "NOT_MEASURED_BY_T031_RUNTIME_MICROBENCHMARK"
                    ),
                    "u1_hardware_claim": False,
                }
            )

        result_path = output_dir / f"T031-{args.candidate}.jsonl"
        with result_path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
        summary = {
            "schema_version": "mstr.t031-local-measurement-summary.v1",
            "task_id": "T031",
            "candidate_id": args.candidate,
            "result_classification": "T031_HOSTED_REFERENCE_MEASUREMENT_COMPLETE",
            "canonical_main_at_start": head,
            "canonical_main_at_end": _require_live_main(repo_root),
            "started_utc": started_utc,
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "paid_cost_usd": 0.0,
            "training": False,
            "source_verification": source_records,
            "regeneration": regeneration,
            "q4_k_m_sha256": q4_k_m_sha,
            "q4_k_m_size_bytes": q4_k_m.stat().st_size,
            "contexts": contexts,
            "decode_semantics": "T030_ISOLATED_DECODE_COMPANION_NOT_POST_PREFILL_KV_CACHE",
            "hosted_lane_claim": "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM",
            "durable_result_jsonl_sha256": sha256_file(result_path),
        }
        _write_json(output_dir / f"T031-{args.candidate}-summary.json", summary)
        failure_path.unlink(missing_ok=True)
        return 0
    except (ExecutionError, ToolchainError, OSError, ValueError, KeyError) as exc:
        _write_json(
            failure_path,
            {
                "schema_version": "mstr.t031-local-measurement-failure.v1",
                "task_id": "T031",
                "candidate_id": args.candidate,
                "result_classification": "T031_EXECUTION_FAILED_CLOSED",
                "canonical_main_at_start": head,
                "started_utc": started_utc,
                "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "error_type": type(exc).__name__,
                "error": str(exc),
                "paid_cost_usd": 0.0,
                "training": False,
            },
        )
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        required=True,
        choices=[
            "granite-4.1-3b",
            "ministral-3-3b",
            "qwen2.5-coder-1.5b",
            "qwen3-4b",
            "qwen3.5-2b",
            "qwen3.5-4b",
            "smollm3-3b",
            "yi-coder-1.5b",
        ],
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "mstr-t031",
    )
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
