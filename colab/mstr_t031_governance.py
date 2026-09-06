#!/usr/bin/env python3
"""T031 canonical authority, live-main, and binding guards."""

from __future__ import annotations

import subprocess
from pathlib import Path

from mstr_executor_toolchain import (
    read_json,
    require_file_sha256,
    sanitized_runtime_environment,
)

AUTHORITY_PATH = Path(
    "artifacts/authorities/T031_FOUNDER_AUTHORITY_FOR_LOCAL_MEASUREMENT_REGENERATION.json"
)
ENVELOPE_PATH = Path("artifacts/manifests/T031-local-measurement-execution-envelope.json")
LOCK_PATH = Path("artifacts/manifests/T031-executor-toolchain-lock.json")
REPLAY_OVERLAY_PATH = Path(
    "artifacts/manifests/T031-t029-historical-producer-replay-overlay.json"
)
BINDING_PATH = Path("artifacts/manifests/T031-executor-toolchain-binding.json")
RUNTIME_PROFILE_PATH = Path("configs/runtimes/llama-cpp-cpu.json")
WORKFLOW_PATH = Path(".github/workflows/t031-measure.yml")
HELPER_PATH = Path("colab/mstr_executor_toolchain.py")
REPLAY_HELPER_PATH = Path("colab/mstr_t031_replay.py")
HISTORICAL_REPLAY_HELPER_PATH = Path("colab/mstr_t031_historical_replay.py")
GOVERNANCE_PATH = Path("colab/mstr_t031_governance.py")
SOURCE_PATH = Path("colab/mstr_t031_source.py")
ARTIFACT_PATH = Path("colab/mstr_t031_artifacts.py")
MEASURE_PATH = Path("colab/mstr_t031_measure.py")
RUNNER_PATH = Path("colab/mstr_t031_execute.py")

HISTORICAL_CUTOFF_UTC = "2026-08-26T10:44:06Z"
HISTORICAL_SHARDS = (
    (
        "artifacts/manifests/T031-t029-historical-pypi-packages-01.json",
        "ce67c3b4dd5e11501171a1980e2e538ec2470bd4cfc1b333a94314979efc3cd5",
    ),
    (
        "artifacts/manifests/T031-t029-historical-pypi-packages-02.json",
        "e11128c67ab76e0ec93a416b75442c626b7adc4ed4fe1a7f701465787ba46938",
    ),
    (
        "artifacts/manifests/T031-t029-historical-pypi-packages-03.json",
        "bac8e225f74c32e542ef907c35d892837ddbac25fcc298e625ad7d94f12f9ec9",
    ),
)


class ExecutionError(RuntimeError):
    """Raised when any canonical T031 execution condition is not satisfied."""


def _run(
    argv: list[str],
    *,
    timeout: float,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=timeout,
            env=env,
            cwd=cwd,
        )
    except subprocess.TimeoutExpired as exc:
        raise ExecutionError(f"command timed out after {timeout}s: {argv!r}") from exc
    if completed.returncode != 0:
        diagnostic = (completed.stdout + "\n" + completed.stderr).strip()[-4000:]
        raise ExecutionError(f"command failed ({completed.returncode}): {argv!r}\n{diagnostic}")
    return completed


def _live_main_sha() -> str:
    completed = _run(
        [
            "git",
            "ls-remote",
            "https://github.com/TheHalfMoon/MSTR.git",
            "refs/heads/main",
        ],
        timeout=60,
        env=sanitized_runtime_environment(),
    )
    fields = completed.stdout.strip().split()
    if len(fields) != 2 or fields[1] != "refs/heads/main" or len(fields[0]) != 40:
        raise ExecutionError("unable to resolve exact live main identity")
    return fields[0]


def _require_live_main(repo_root: Path) -> str:
    head = _run(
        ["git", "rev-parse", "HEAD"],
        timeout=30,
        env=sanitized_runtime_environment(),
        cwd=repo_root,
    ).stdout.strip()
    live_main = _live_main_sha()
    if head != live_main:
        raise ExecutionError(
            f"live-main guard failed: checked-out HEAD={head}, remote main={live_main}"
        )
    return head


def _require_binding(repo_root: Path) -> tuple[dict[str, object], dict[str, object]]:
    binding = read_json(repo_root / BINDING_PATH)
    authority = read_json(repo_root / AUTHORITY_PATH)
    envelope = read_json(repo_root / ENVELOPE_PATH)
    lock = read_json(repo_root / LOCK_PATH)
    replay_overlay = read_json(repo_root / REPLAY_OVERLAY_PATH)

    scalar_bindings = {
        repo_root / AUTHORITY_PATH: binding.get("authority_sha256"),
        repo_root / ENVELOPE_PATH: binding.get("envelope_sha256"),
        repo_root / LOCK_PATH: binding.get("toolchain_lock_sha256"),
        repo_root / REPLAY_OVERLAY_PATH: binding.get("producer_replay_overlay_sha256"),
        repo_root / HELPER_PATH: binding.get("toolchain_helper_sha256"),
        repo_root / REPLAY_HELPER_PATH: binding.get("producer_replay_helper_sha256"),
        repo_root / HISTORICAL_REPLAY_HELPER_PATH: binding.get("historical_replay_helper_sha256"),
        repo_root / GOVERNANCE_PATH: binding.get("governance_script_sha256"),
        repo_root / SOURCE_PATH: binding.get("source_script_sha256"),
        repo_root / ARTIFACT_PATH: binding.get("artifact_script_sha256"),
        repo_root / MEASURE_PATH: binding.get("measurement_script_sha256"),
        repo_root / RUNNER_PATH: binding.get("executor_script_sha256"),
        repo_root / WORKFLOW_PATH: binding.get("workflow_sha256"),
    }
    for path, expected in scalar_bindings.items():
        if not isinstance(expected, str):
            raise ExecutionError(f"binding SHA-256 missing for {path}")
        require_file_sha256(path, expected)

    if authority.get("status") != "AUTHORIZED_CANONICAL":
        raise ExecutionError("T031 authority is not AUTHORIZED_CANONICAL")
    scope = authority.get("scope")
    if not isinstance(scope, dict):
        raise ExecutionError("T031 authority scope is missing")
    bounded = scope.get("bounded_execution_envelope")
    if not isinstance(bounded, dict):
        raise ExecutionError("T031 bounded execution envelope binding is missing")
    if bounded.get("sha256") != binding.get("envelope_sha256"):
        raise ExecutionError("authority/envelope binding drift detected")

    if replay_overlay.get("schema_version") != (
        "mstr.t031-t029-historical-producer-replay-overlay.v1"
    ):
        raise ExecutionError("T031 historical replay overlay schema drift detected")
    if replay_overlay.get("status") != "EVIDENCE_BOUNDED_REPLAY":
        raise ExecutionError("T031 producer replay overlay status drift detected")
    if replay_overlay.get("task_id") != "T031":
        raise ExecutionError("T031 producer replay overlay task binding drift detected")
    if replay_overlay.get("python_version") != "3.11.16":
        raise ExecutionError("T031 historical replay Python drift detected")
    if replay_overlay.get("package_count") != 59:
        raise ExecutionError("T031 historical replay package-count drift detected")
    if replay_overlay.get("historical_cutoff_utc") != HISTORICAL_CUTOFF_UTC:
        raise ExecutionError("T031 historical replay cutoff drift detected")

    shards = replay_overlay.get("historical_package_shards")
    if not isinstance(shards, list) or len(shards) != len(HISTORICAL_SHARDS):
        raise ExecutionError("T031 historical replay shard bindings are missing")
    observed_shards: list[tuple[str, str]] = []
    for item in shards:
        if not isinstance(item, dict):
            raise ExecutionError("T031 historical replay shard binding is invalid")
        path_value = item.get("path")
        digest = item.get("sha256")
        if not isinstance(path_value, str) or not isinstance(digest, str):
            raise ExecutionError("T031 historical replay shard scalar is invalid")
        observed_shards.append((path_value, digest))
    if tuple(observed_shards) != HISTORICAL_SHARDS:
        raise ExecutionError("T031 historical replay shard identity drift detected")
    for path_value, digest in HISTORICAL_SHARDS:
        require_file_sha256(repo_root / path_value, digest)

    reconstruction = replay_overlay.get("reconstruction_basis")
    if not isinstance(reconstruction, dict):
        raise ExecutionError("T031 historical replay reconstruction basis is missing")
    if reconstruction.get("historical_transitive_identity_claim") is not False:
        raise ExecutionError("T031 replay must not claim unrecorded historical transitive identity")
    if reconstruction.get("equivalence_gate") != "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH":
        raise ExecutionError("T031 historical artifact-equivalence gate drift detected")

    smoke = replay_overlay.get("historical_smoke_evidence")
    if not isinstance(smoke, dict):
        raise ExecutionError("T031 historical replay smoke evidence is missing")
    expected_smoke = {
        "run_id": 34042093348,
        "artifact_id": 9991993338,
        "artifact_zip_sha256": "c4c84abc0bd38b767c97a78cecb391a4a532f87d6254b7f6d5fd8ec887ce3ca9",
        "package_count": 59,
        "wheel_bytes": 2777196141,
        "closure_installable": True,
        "stage_semantics_proven": False,
        "model_access": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
    }
    for key, expected in expected_smoke.items():
        if smoke.get(key) != expected:
            raise ExecutionError(f"T031 historical smoke evidence drift detected: {key}")

    replay_boundary = replay_overlay.get("execution_boundary")
    if not isinstance(replay_boundary, dict):
        raise ExecutionError("T031 producer replay execution boundary is missing")
    for key in (
        "model_access_authority_expansion",
        "candidate_revision_or_file_expansion",
        "b012_execution",
        "t032_execution",
        "t033_execution",
        "t034_admission_decision",
        "training",
    ):
        if replay_boundary.get(key) is not False:
            raise ExecutionError(f"producer replay authority expansion drift detected: {key}")
    if replay_boundary.get("paid_cost_usd") != 0.0:
        raise ExecutionError("producer replay paid-cost boundary drift detected")
    if replay_boundary.get("git_model_binaries") != 0:
        raise ExecutionError("producer replay Git model-binary boundary drift detected")
    if replay_boundary.get("founder_machine_model_binaries") != 0:
        raise ExecutionError("producer replay founder-machine binary boundary drift detected")

    candidate_ids = binding.get("candidate_ids")
    envelope_candidates = envelope.get("candidate_ids")
    lock_binding = lock.get("task_binding")
    if not isinstance(lock_binding, dict):
        raise ExecutionError("toolchain task binding is missing")
    if candidate_ids != envelope_candidates or candidate_ids != lock_binding.get("candidate_ids"):
        raise ExecutionError("candidate set drift detected across binding/envelope/toolchain")

    prohibited_false = {
        "b010_b012_candidates",
        "candidate_revision_or_file_expansion",
        "new_candidates",
        "paid_compute",
        "paid_model_api",
        "production_release",
        "t032_execution",
        "t033_execution",
        "t034_admission_decision",
        "training",
        "weight_changing_training",
    }
    for key in prohibited_false:
        if scope.get(key) is not False:
            raise ExecutionError(f"authority prohibition drift detected: {key}")
    if scope.get("git_model_binaries") is not False:
        raise ExecutionError("Git model binaries must remain prohibited")
    if scope.get("founder_machine_large_artifacts") != 0:
        raise ExecutionError("founder-machine large artifacts must remain zero")

    return binding, envelope
