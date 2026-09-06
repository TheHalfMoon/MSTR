#!/usr/bin/env python3
"""B012 exact authority, canonical-main, and executor-binding guards."""

from __future__ import annotations

import subprocess
from pathlib import Path

from mstr_executor_toolchain import read_json, require_file_sha256, sanitized_runtime_environment

AUTHORITY_PATH = Path(
    "artifacts/authorities/B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION.json"
)
ENVELOPE_PATH = Path("artifacts/manifests/B012-equivalent-qualification-execution-envelope.json")
B010_PATH = Path("artifacts/manifests/B010-new-candidate-weight-access.json")
B011_PATH = Path("artifacts/manifests/B011-acquired-candidates.json")
MELLUM_ARTIFACT_PATH = Path("artifacts/manifests/B011-artifact-mellum-4b.json")
QWEN_ARTIFACT_PATH = Path("artifacts/manifests/B011-artifact-qwen3.5-0.8b-control.json")
LOCK_PATH = Path("artifacts/manifests/B012-executor-toolchain-lock.json")
BINDING_PATH = Path("artifacts/manifests/B012-executor-toolchain-binding.json")
RAW_CODE_PATH = Path("benchmarks/manifests/B012-raw-code-proxy.json")
RUNTIME_PROFILE_PATH = Path("configs/runtimes/llama-cpp-cpu.json")
T031_LOCK_PATH = Path("artifacts/manifests/T031-executor-toolchain-lock.json")
T031_REPLAY_OVERLAY_PATH = Path("artifacts/manifests/T031-t029-producer-replay-overlay.json")
TOOLCHAIN_HELPER_PATH = Path("colab/mstr_executor_toolchain.py")
REPLAY_HELPER_PATH = Path("colab/mstr_t031_replay.py")
T031_MEASURE_PATH = Path("colab/mstr_t031_measure.py")
GOVERNANCE_PATH = Path("colab/mstr_b012_governance.py")
SOURCE_PATH = Path("colab/mstr_b012_source.py")
ARTIFACT_PATH = Path("colab/mstr_b012_artifacts.py")
RAW_EXEC_PATH = Path("colab/mstr_b012_raw_code.py")
RUNNER_PATH = Path("colab/mstr_b012_execute.py")
WORKFLOW_PATH = Path(".github/workflows/b012-qualify.yml")


class ExecutionError(RuntimeError):
    """Raised when a B012 execution condition fails closed."""


def _run(
    argv: list[str], *, timeout: float, env: dict[str, str] | None = None, cwd: Path | None = None
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
        ["git", "ls-remote", "https://github.com/TheHalfMoon/MSTR.git", "refs/heads/main"],
        timeout=60,
        env=sanitized_runtime_environment(),
    )
    fields = completed.stdout.strip().split()
    if len(fields) != 2 or fields[1] != "refs/heads/main" or len(fields[0]) != 40:
        raise ExecutionError("unable to resolve exact live main identity")
    return fields[0]


def _require_live_main(repo_root: Path) -> str:
    head = _run(
        ["git", "rev-parse", "HEAD"], timeout=30, env=sanitized_runtime_environment(), cwd=repo_root
    ).stdout.strip()
    live = _live_main_sha()
    if head != live:
        raise ExecutionError(f"live-main guard failed: checked-out HEAD={head}, remote main={live}")
    return head


def _require_binding(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    binding = read_json(repo_root / BINDING_PATH)
    authority = read_json(repo_root / AUTHORITY_PATH)
    envelope = read_json(repo_root / ENVELOPE_PATH)
    b011 = read_json(repo_root / B011_PATH)
    lock = read_json(repo_root / LOCK_PATH)

    paths = {
        AUTHORITY_PATH: "authority_sha256",
        ENVELOPE_PATH: "envelope_sha256",
        B010_PATH: "b010_sha256",
        B011_PATH: "b011_sha256",
        MELLUM_ARTIFACT_PATH: "mellum_b011_artifact_sha256",
        QWEN_ARTIFACT_PATH: "qwen_b011_artifact_sha256",
        LOCK_PATH: "toolchain_lock_sha256",
        RAW_CODE_PATH: "raw_code_manifest_sha256",
        RUNTIME_PROFILE_PATH: "runtime_profile_sha256",
        T031_LOCK_PATH: "reused_t031_lock_sha256",
        T031_REPLAY_OVERLAY_PATH: "reused_t031_replay_overlay_sha256",
        TOOLCHAIN_HELPER_PATH: "toolchain_helper_sha256",
        REPLAY_HELPER_PATH: "replay_helper_sha256",
        T031_MEASURE_PATH: "reused_measurement_helper_sha256",
        GOVERNANCE_PATH: "governance_script_sha256",
        SOURCE_PATH: "source_script_sha256",
        ARTIFACT_PATH: "artifact_script_sha256",
        RAW_EXEC_PATH: "raw_code_script_sha256",
        RUNNER_PATH: "executor_script_sha256",
        WORKFLOW_PATH: "workflow_sha256",
    }
    for relative, key in paths.items():
        expected = binding.get(key)
        if not isinstance(expected, str):
            raise ExecutionError(f"binding SHA-256 missing: {key}")
        require_file_sha256(repo_root / relative, expected)

    candidates = ["mellum-4b", "qwen3.5-0.8b-control"]
    if authority.get("status") != "AUTHORIZED_CANONICAL" or authority.get("task_id") != "B012":
        raise ExecutionError("B012 authority is not canonical")
    if authority.get("authority_id") != "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION":
        raise ExecutionError("B012 authority identity drift detected")
    scope = authority.get("scope")
    if not isinstance(scope, dict) or scope.get("candidate_ids") != candidates:
        raise ExecutionError("B012 authority candidate scope drift detected")
    bounded = scope.get("bounded_execution_envelope")
    if not isinstance(bounded, dict) or bounded.get("sha256") != binding.get("envelope_sha256"):
        raise ExecutionError("B012 authority/envelope binding drift detected")
    if envelope.get("candidate_ids") != candidates or binding.get("candidate_ids") != candidates:
        raise ExecutionError("B012 candidate set drift detected")
    if envelope.get("authority_id") != authority.get("authority_id"):
        raise ExecutionError("B012 envelope authority drift detected")
    if envelope.get("dispatch_state") != "BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING":
        raise ExecutionError("unexpected B012 envelope dispatch-state drift")
    if binding.get("status") != "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL":
        raise ExecutionError("B012 executor binding status is not executable when canonical")

    reuse = lock.get("explicit_dependency_reuse")
    if not isinstance(reuse, dict) or reuse.get("authority_transfer") is not False:
        raise ExecutionError("dependency reuse authority boundary is invalid")
    if reuse.get("source_task") != "T031" or reuse.get("package_count") != 40:
        raise ExecutionError("pinned dependency reuse identity drift detected")
    if reuse.get("base_lock_sha256") != binding.get("reused_t031_lock_sha256"):
        raise ExecutionError("reused T031 lock binding drift detected")
    if reuse.get("producer_replay_overlay_sha256") != binding.get(
        "reused_t031_replay_overlay_sha256"
    ):
        raise ExecutionError("reused replay overlay binding drift detected")

    if (
        b011.get("resource_cost_usd") != 0.0
        or b011.get("observed_total_download_bytes") != 9817996174
    ):
        raise ExecutionError("B011 acquired-source evidence drift detected")
    b011_candidates = b011.get("candidates")
    if not isinstance(b011_candidates, list):
        raise ExecutionError("B011 acquired candidate list is missing")
    observed = {
        item.get("candidate_id"): item.get("status")
        for item in b011_candidates
        if isinstance(item, dict)
    }
    if observed != {"mellum-4b": "ACQUIRED_VERIFIED", "qwen3.5-0.8b-control": "ACQUIRED_VERIFIED"}:
        raise ExecutionError("B011 acquired candidate status drift detected")

    if scope.get("paid_compute") is not False or scope.get("paid_model_api") is not False:
        raise ExecutionError("paid execution remains prohibited")
    if scope.get("training") is not False or scope.get("weight_changing_training") is not False:
        raise ExecutionError("training remains prohibited")
    if scope.get("new_candidate_access") is not False:
        raise ExecutionError("new candidate access remains prohibited")
    prohibited = envelope.get("prohibited_operations")
    if not isinstance(prohibited, list):
        raise ExecutionError("B012 prohibited-operation envelope is missing")
    required_prohibitions = {
        "K2_OR_ANY_NEW_CANDIDATE",
        "CANDIDATE_REVISION_OR_FILE_EXPANSION",
    }
    if not required_prohibitions.issubset({item for item in prohibited if isinstance(item, str)}):
        raise ExecutionError("candidate scope expansion prohibition drift detected")
    if (
        scope.get("git_model_binaries") is not False
        or scope.get("founder_machine_large_artifacts") != 0
    ):
        raise ExecutionError("model binary retention boundary drift detected")

    return binding, envelope, lock
