#!/usr/bin/env python3
"""Bounded B012 Qwen raw-code recovery after a durable Stage 05 checkpoint."""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from mstr_b012_artifacts import convert_quantize
from mstr_b012_governance import (
    RAW_CODE_PATH,
    T031_LOCK_PATH,
    T031_REPLAY_OVERLAY_PATH,
    ExecutionError,
    _require_binding,
    _require_live_main,
)
from mstr_b012_raw_code import run_raw_code_proxy
from mstr_b012_source import download_candidate
from mstr_executor_toolchain import (
    ToolchainError,
    clone_exact_commit,
    read_json,
    require_file_sha256,
    sha256_file,
)
from mstr_t031_replay import install_replay_toolchain

CANDIDATE_ID = "qwen3.5-0.8b-control"
PRIOR_RUN_ID = 34155931982
PRIOR_MAIN = "7ebb02c3c46c64d226d412def8bc88fd5f2c1594"
PRIOR_STAGE05_ARTIFACT_ID = 10031329744
PRIOR_STAGE05_ARTIFACT_DIGEST = (
    "sha256:726e154a9e94c67eea4b0bdec5440912af6055e46cac9f95861872a044616fee"
)
PRIOR_STAGE05_CHECKPOINT_SHA256 = (
    "2141781456f54623e6b87c9e7528ea767f49062670fbb62b77d639b3ec3d1f88"
)
EXPECTED_Q4_K_M_SHA256 = "47f87d507130b70d7b54a159e7bf982e4fbe7dc75eae74e3cd9c9c9284805626"
EXPECTED_Q4_K_M_SIZE_BYTES = 541903296

RECOVERY_MANIFEST_PATH = Path(
    "artifacts/manifests/B012-qwen-raw-code-runner-shutdown-recovery.json"
)
ACTIVE_WORKFLOW_PATH = Path(".github/workflows/b012-qwen-raw-code-recovery.yml")
SCRIPT_PATH = Path("colab/mstr_b012_qwen_raw_code_recovery.py")


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_recovery_activation(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    binding, envelope, lock = _require_binding(repo_root)
    manifest = read_json(repo_root / RECOVERY_MANIFEST_PATH)
    if manifest.get("status") != "ACTIVATED_CANONICAL":
        raise ExecutionError("B012 Qwen raw-code recovery is not canonically activated")
    if manifest.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen recovery candidate identity drift detected")
    if manifest.get("prior_run_id") != PRIOR_RUN_ID:
        raise ExecutionError("B012 Qwen recovery prior-run identity drift detected")
    if manifest.get("prior_stage05_artifact_id") != PRIOR_STAGE05_ARTIFACT_ID:
        raise ExecutionError("B012 Qwen recovery Stage 05 artifact identity drift detected")
    if manifest.get("prior_stage05_artifact_digest") != PRIOR_STAGE05_ARTIFACT_DIGEST:
        raise ExecutionError("B012 Qwen recovery Stage 05 artifact digest drift detected")
    if manifest.get("prior_stage05_checkpoint_sha256") != PRIOR_STAGE05_CHECKPOINT_SHA256:
        raise ExecutionError("B012 Qwen recovery Stage 05 checkpoint digest drift detected")
    if manifest.get("expected_q4_k_m_sha256") != EXPECTED_Q4_K_M_SHA256:
        raise ExecutionError("B012 Qwen recovery Q4 identity drift detected")
    if manifest.get("expected_q4_k_m_size_bytes") != EXPECTED_Q4_K_M_SIZE_BYTES:
        raise ExecutionError("B012 Qwen recovery Q4 size drift detected")

    expected_script = manifest.get("recovery_script_sha256")
    expected_workflow = manifest.get("recovery_workflow_sha256")
    if not isinstance(expected_script, str) or not isinstance(expected_workflow, str):
        raise ExecutionError("B012 Qwen recovery component binding is incomplete")
    require_file_sha256(repo_root / SCRIPT_PATH, expected_script)
    require_file_sha256(repo_root / ACTIVE_WORKFLOW_PATH, expected_workflow)

    expected_manifest = binding.get("qwen_raw_code_recovery_manifest_sha256")
    if not isinstance(expected_manifest, str):
        raise ExecutionError("B012 Qwen recovery is not bound into the active executor binding")
    require_file_sha256(repo_root / RECOVERY_MANIFEST_PATH, expected_manifest)

    activation = manifest.get("activation")
    if not isinstance(activation, dict):
        raise ExecutionError("B012 Qwen recovery activation record is missing")
    if activation.get("retry_authority_created") is not False:
        raise ExecutionError("B012 Qwen recovery must not fabricate retry authority")
    if activation.get("external_dispatch_authority_created") is not False:
        raise ExecutionError("B012 Qwen recovery must not fabricate dispatch authority")
    return binding, envelope, lock, manifest


def _prepare_minimal_tools(
    *, lock: dict[str, object], workdir: Path
) -> tuple[Path, Path, Path, dict[str, object]]:
    llama = lock.get("llama_cpp")
    if not isinstance(llama, dict):
        raise ExecutionError("B012 llama.cpp lock is missing")
    repository = llama.get("repository")
    conversion_commit = llama.get("conversion_quantization_commit")
    runtime_commit = llama.get("runtime_commit")
    build_flags = llama.get("build_flags")
    if (
        not isinstance(repository, str)
        or not isinstance(conversion_commit, str)
        or not isinstance(runtime_commit, str)
        or not isinstance(build_flags, list)
        or not all(isinstance(item, str) for item in build_flags)
    ):
        raise ExecutionError("B012 Qwen recovery llama.cpp identity is invalid")

    conversion_dir = workdir / "llama-convert"
    quantizer = clone_exact_commit(
        repository=repository,
        commit=conversion_commit,
        destination=conversion_dir,
        build_flags=build_flags,
        target="llama-quantize",
    )
    tools = workdir / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    quantizer_copy = tools / "llama-quantize"
    shutil.copy2(quantizer, quantizer_copy)
    shutil.rmtree(conversion_dir / "build", ignore_errors=True)
    shutil.rmtree(conversion_dir / ".git", ignore_errors=True)

    runtime_dir = workdir / "llama-runtime"
    cli = clone_exact_commit(
        repository=repository,
        commit=runtime_commit,
        destination=runtime_dir,
        build_flags=build_flags,
        target="llama-cli",
    )
    cli_copy = tools / "llama-cli"
    shutil.copy2(cli, cli_copy)
    shutil.rmtree(runtime_dir, ignore_errors=True)
    return conversion_dir, quantizer_copy, cli_copy, {
        "repository": repository,
        "conversion_quantization_commit": conversion_commit,
        "runtime_commit": runtime_commit,
        "build_flags": build_flags,
        "recovery_targets": ["llama-quantize", "llama-cli"],
        "llama_bench_built": False,
    }


def execute(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    workdir = args.workdir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        main_start = _require_live_main(repo_root)
        _, envelope, lock, manifest = _require_recovery_activation(repo_root)
        if main_start == PRIOR_MAIN:
            raise ExecutionError(
                "B012 Qwen recovery activation must be a later canonical main "
                "than the interrupted run"
            )

        python_exe, replay_identity = install_replay_toolchain(
            base_lock_path=repo_root / T031_LOCK_PATH,
            overlay_path=repo_root / T031_REPLAY_OVERLAY_PATH,
            root=workdir / "python",
        )
        conversion_dir, quantizer, cli, tool_identity = _prepare_minimal_tools(
            lock=lock, workdir=workdir
        )
        source_dir = workdir / "source" / CANDIDATE_ID
        source_records = download_candidate(
            repo_root=repo_root,
            envelope=envelope,
            candidate_id=CANDIDATE_ID,
            destination=source_dir,
        )
        q4, quantization = convert_quantize(
            python_exe=python_exe,
            conversion_dir=conversion_dir,
            quantize_bin=quantizer,
            source_dir=source_dir,
            candidate_id=CANDIDATE_ID,
            workdir=workdir,
        )
        regenerated_sha = sha256_file(q4)
        regenerated_size = q4.stat().st_size
        if regenerated_sha != EXPECTED_Q4_K_M_SHA256:
            raise ExecutionError("B012 Qwen recovery regenerated Q4 SHA-256 mismatch")
        if regenerated_size != EXPECTED_Q4_K_M_SIZE_BYTES:
            raise ExecutionError("B012 Qwen recovery regenerated Q4 size mismatch")

        raw_manifest = read_json(repo_root / RAW_CODE_PATH)
        raw_code = run_raw_code_proxy(
            executable=cli,
            model=q4,
            manifest=raw_manifest,
        )
        main_end = _require_live_main(repo_root)
        if main_end != main_start:
            raise ExecutionError(
                f"B012 Qwen recovery canonical main drift: start={main_start}, end={main_end}"
            )

        verified_bytes = sum(
            int(record["size_bytes"])
            for record in source_records
            if isinstance(record, dict) and isinstance(record.get("size_bytes"), int)
        )
        result = {
            "schema_version": "mstr.b012-qwen-raw-code-recovery-result.v1",
            "task_id": "B012",
            "candidate_id": CANDIDATE_ID,
            "result_classification": "B012_RAW_CODE_RECOVERY_COMPLETE",
            "candidate_admission_decision": "NOT_MADE_BY_B012_RECOVERY",
            "canonical_main_at_start": main_start,
            "canonical_main_at_end": main_end,
            "started_utc": started_utc,
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "prior_stage_evidence": {
                "run_id": PRIOR_RUN_ID,
                "canonical_main": PRIOR_MAIN,
                "stage05_artifact_id": PRIOR_STAGE05_ARTIFACT_ID,
                "stage05_artifact_digest": PRIOR_STAGE05_ARTIFACT_DIGEST,
                "stage05_checkpoint_sha256": PRIOR_STAGE05_CHECKPOINT_SHA256,
                "prefill_decode_rerun": False,
            },
            "source_reacquisition": {
                "verified_download_bytes": verified_bytes,
                "source_verification": source_records,
            },
            "producer_replay": replay_identity,
            "tool_identity": tool_identity,
            "regenerated_q4": {
                "sha256": regenerated_sha,
                "size_bytes": regenerated_size,
                "matches_prior_stage03": True,
                "quantization": quantization,
            },
            "raw_code_proxy": raw_code,
            "recovery_manifest_id": manifest.get("recovery_id"),
            "training": False,
            "paid_cost_usd": 0.0,
            "durable_binary_artifacts": False,
        }
        _write(output_dir / f"B012-{CANDIDATE_ID}-raw-code-recovery.json", result)
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
        failure = {
            "schema_version": "mstr.b012-qwen-raw-code-recovery-failure.v1",
            "task_id": "B012",
            "candidate_id": CANDIDATE_ID,
            "result_classification": "B012_RAW_CODE_RECOVERY_FAILED_CLOSED",
            "started_utc": started_utc,
            "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "prior_run_id": PRIOR_RUN_ID,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "candidate_admission_decision": "NONE",
            "training": False,
            "paid_cost_usd": 0.0,
        }
        _write(output_dir / f"B012-{CANDIDATE_ID}-raw-code-recovery-failure.json", failure)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
