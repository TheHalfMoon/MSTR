#!/usr/bin/env python3
"""Stage-addressable B012 equivalent qualification on one ephemeral CPU runner."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
from pathlib import Path

from mstr_b012_artifacts import convert_quantize, prepare_tools
from mstr_b012_governance import (
    BINDING_PATH,
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
from mstr_executor_toolchain import (
    ToolchainError,
    read_json,
    require_file_sha256,
    sha256_file,
)
from mstr_t031_replay import install_replay_toolchain

STAGES = ("init", "source", "quantize", "prefill", "decode", "raw-code", "finalize")
STAGE_LABELS = {
    "init": "01-init",
    "source": "02-source",
    "quantize": "03-quantize",
    "prefill": "04-prefill",
    "decode": "05-decode",
    "raw-code": "06-raw-code",
    "finalize": "07-finalize",
}
PREDECESSORS: dict[str, str | None] = {
    "init": None,
    "source": "init",
    "quantize": "source",
    "prefill": "quantize",
    "decode": "prefill",
    "raw-code": "decode",
    "finalize": "raw-code",
}


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExecutionError(f"B012 staged JSON object is invalid: {path}")
    return value


def _state_path(output_dir: Path, candidate: str) -> Path:
    return output_dir / f"B012-{candidate}-stage-state.json"


def _failure_path(output_dir: Path, candidate: str) -> Path:
    return output_dir / f"B012-{candidate}-failure.json"


def _checkpoint_path(output_dir: Path, candidate: str, stage: str) -> Path:
    return output_dir / f"B012-{candidate}-checkpoint-{STAGE_LABELS[stage]}.json"


def _runtime_integer(runtime_cfg: dict[str, object], key: str) -> int:
    value = runtime_cfg.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ExecutionError(f"B012 runtime benchmark integer is invalid: {key}")
    return value


def _path_from_state(state: dict[str, object], key: str) -> Path:
    paths = state.get("local_ephemeral_paths")
    if not isinstance(paths, dict):
        raise ExecutionError("B012 staged local path state is missing")
    value = paths.get(key)
    if not isinstance(value, str) or not value:
        raise ExecutionError(f"B012 staged local path is missing: {key}")
    return Path(value)


def _completed_stages(state: dict[str, object]) -> list[str]:
    completed = state.get("completed_stages")
    if not isinstance(completed, list) or not all(isinstance(item, str) for item in completed):
        raise ExecutionError("B012 completed stage state is invalid")
    return list(completed)


def _load_state(output_dir: Path, candidate: str, stage: str) -> dict[str, object]:
    if stage == "init":
        raise ExecutionError("B012 init stage must not load prior state")
    state = _read(_state_path(output_dir, candidate))
    if state.get("candidate_id") != candidate or state.get("task_id") != "B012":
        raise ExecutionError("B012 staged state identity drift detected")
    expected = PREDECESSORS[stage]
    completed = _completed_stages(state)
    if expected is None or not completed or completed[-1] != expected:
        raise ExecutionError(
            f"B012 staged transition invalid: stage={stage}, expected_predecessor={expected}"
        )
    if stage in completed:
        raise ExecutionError(f"B012 staged action already completed: {stage}")
    return state


TOPOLOGY_REPAIR_PATH = Path(
    "artifacts/manifests/B012-runner-shutdown-topology-repair.json"
)


def _require_staged_binding(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    binding = read_json(repo_root / BINDING_PATH)
    expected_manifest = binding.get("runner_shutdown_topology_repair_manifest_sha256")
    if not isinstance(expected_manifest, str):
        raise ExecutionError("B012 topology-repair manifest is not activated in the executor binding")
    require_file_sha256(repo_root / TOPOLOGY_REPAIR_PATH, expected_manifest)
    repair = read_json(repo_root / TOPOLOGY_REPAIR_PATH)
    expected_executor = repair.get("staged_executor_sha256")
    expected_workflow = repair.get("candidate_workflow_sha256")
    if not isinstance(expected_executor, str) or not isinstance(expected_workflow, str):
        raise ExecutionError("B012 topology-repair component binding is incomplete")
    require_file_sha256(repo_root / "colab/mstr_b012_staged.py", expected_executor)
    if binding.get("workflow_sha256") != expected_workflow:
        raise ExecutionError("B012 active workflow does not match reviewed topology-repair bytes")
    return _require_binding(repo_root)


def _require_stage_main(
    repo_root: Path, state: dict[str, object]
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    live = _require_live_main(repo_root)
    canonical_start = state.get("canonical_main_at_start")
    if not isinstance(canonical_start, str) or live != canonical_start:
        raise ExecutionError(
            f"B012 staged canonical-main drift: start={canonical_start}, live={live}"
        )
    return _require_staged_binding(repo_root)


def _complete_stage(
    *,
    output_dir: Path,
    state: dict[str, object],
    stage: str,
    checkpoint_payload: dict[str, object],
) -> None:
    completed = _completed_stages(state)
    expected = PREDECESSORS[stage]
    if expected is None:
        if completed:
            raise ExecutionError("B012 init stage unexpectedly has completed predecessors")
    elif not completed or completed[-1] != expected:
        raise ExecutionError(
            f"B012 stage completion order invalid: stage={stage}, predecessor={expected}"
        )
    completed.append(stage)
    state["completed_stages"] = completed
    state["last_completed_stage"] = stage
    _write(_state_path(output_dir, str(state["candidate_id"])), state)
    checkpoint = {
        "schema_version": "mstr.b012-stage-checkpoint.v1",
        "task_id": "B012",
        "candidate_id": state["candidate_id"],
        "stage": stage,
        "stage_label": STAGE_LABELS[stage],
        "canonical_main_at_start": state["canonical_main_at_start"],
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_stages": completed,
        "model_access_state": state.get("model_access_state", "UNKNOWN"),
        "training": False,
        "paid_cost_usd": 0.0,
        "durable_binary_artifacts": False,
        "durable_output_format": "JSON_ONLY",
        "checkpoint_payload": checkpoint_payload,
    }
    _write(_checkpoint_path(output_dir, str(state["candidate_id"]), stage), checkpoint)


def _stage_init(
    *, repo_root: Path, output_dir: Path, workdir: Path, candidate: str
) -> None:
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    state_path = _state_path(output_dir, candidate)
    failure_path = _failure_path(output_dir, candidate)
    state_path.unlink(missing_ok=True)
    failure_path.unlink(missing_ok=True)
    for label in STAGE_LABELS.values():
        (output_dir / f"B012-{candidate}-checkpoint-{label}.json").unlink(missing_ok=True)

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    execution_started_monotonic = time.monotonic()
    head = _require_live_main(repo_root)
    binding, _, lock = _require_staged_binding(repo_root)
    if candidate not in binding.get("candidate_ids", []):
        raise ExecutionError(f"candidate outside exact B012 authority: {candidate}")

    python_exe, replay_identity = install_replay_toolchain(
        base_lock_path=repo_root / T031_LOCK_PATH,
        overlay_path=repo_root / T031_REPLAY_OVERLAY_PATH,
        root=workdir / "python",
    )
    conversion_dir, quantizer, bench, cli, tool_identity = prepare_tools(
        lock=lock, workdir=workdir
    )
    canonical_end = _require_live_main(repo_root)
    if canonical_end != head:
        raise ExecutionError("B012 canonical main moved during staged toolchain setup")

    state: dict[str, object] = {
        "schema_version": "mstr.b012-stage-state.v1",
        "task_id": "B012",
        "candidate_id": candidate,
        "canonical_main_at_start": head,
        "started_utc": started_utc,
        "execution_started_monotonic": execution_started_monotonic,
        "completed_stages": [],
        "last_completed_stage": None,
        "model_access_state": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
        "producer_replay": replay_identity,
        "tool_identity": tool_identity,
        "local_ephemeral_paths": {
            "workdir": str(workdir),
            "python_exe": str(python_exe),
            "conversion_dir": str(conversion_dir),
            "quantizer": str(quantizer),
            "bench": str(bench),
            "cli": str(cli),
        },
    }
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="init",
        checkpoint_payload={
            "canonical_main_at_end": canonical_end,
            "producer_replay": replay_identity,
            "tool_identity": tool_identity,
            "model_access": "NONE",
        },
    )


def _stage_source(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "source")
    _, envelope, _ = _require_stage_main(repo_root, state)
    workdir = _path_from_state(state, "workdir")
    source_dir = workdir / "source" / candidate
    source_records = download_candidate(
        repo_root=repo_root,
        envelope=envelope,
        candidate_id=candidate,
        destination=source_dir,
    )
    _require_live_main(repo_root)
    state["model_access_state"] = "EXACT_B010_FILES_REACQUIRED_VERIFIED"
    state["source_verification"] = source_records
    paths = state["local_ephemeral_paths"]
    if not isinstance(paths, dict):
        raise ExecutionError("B012 local path state is invalid after source download")
    paths["source_dir"] = str(source_dir)
    verified_bytes = sum(
        int(record["size_bytes"])
        for record in source_records
        if isinstance(record, dict) and isinstance(record.get("size_bytes"), int)
    )
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="source",
        checkpoint_payload={
            "verified_file_count": len(source_records),
            "verified_download_bytes": verified_bytes,
            "source_verification": source_records,
        },
    )


def _stage_quantize(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "quantize")
    _require_stage_main(repo_root, state)
    workdir = _path_from_state(state, "workdir")
    q4, quantization = convert_quantize(
        python_exe=_path_from_state(state, "python_exe"),
        conversion_dir=_path_from_state(state, "conversion_dir"),
        quantize_bin=_path_from_state(state, "quantizer"),
        source_dir=_path_from_state(state, "source_dir"),
        candidate_id=candidate,
        workdir=workdir,
    )
    q4_sha = sha256_file(q4)
    q4_size = q4.stat().st_size
    q4_manifest = {
        "schema_version": "mstr.b012-q4-profile.v1",
        "task_id": "B012",
        "candidate_id": candidate,
        "source_main": state["canonical_main_at_start"],
        "tool_identity": state["tool_identity"],
        "producer_replay": state["producer_replay"],
        "quantization": quantization,
        "primary_q4_k_m_sha256": q4_sha,
        "primary_q4_k_m_size_bytes": q4_size,
        "q4_k_m_le_3gb_observation": q4_size <= 3_000_000_000,
    }
    q4_path = output_dir / f"B012-{candidate}-q4.json"
    _write(q4_path, q4_manifest)
    state["quantization"] = quantization
    state["q4_k_m_sha256"] = q4_sha
    state["q4_k_m_size_bytes"] = q4_size
    state["q4_manifest_path"] = str(q4_path)
    paths = state["local_ephemeral_paths"]
    if not isinstance(paths, dict):
        raise ExecutionError("B012 local path state is invalid after quantization")
    paths["q4"] = str(q4)
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="quantize",
        checkpoint_payload={
            "q4_k_m_sha256": q4_sha,
            "q4_k_m_size_bytes": q4_size,
            "q4_k_m_le_3gb_observation": q4_size <= 3_000_000_000,
            "q4_manifest_sha256": sha256_file(q4_path),
            "quantization": quantization,
        },
    )


def _runtime_configuration(
    lock: dict[str, object],
) -> tuple[dict[str, object], dict[str, object], dict[str, int]]:
    task_binding = lock.get("task_binding")
    if not isinstance(task_binding, dict):
        raise ExecutionError("B012 task binding is missing")
    runtime_cfg = task_binding.get("runtime_benchmark")
    if not isinstance(runtime_cfg, dict):
        raise ExecutionError("B012 runtime benchmark binding is missing")
    runner_cfg = lock.get("runner")
    if not isinstance(runner_cfg, dict):
        raise ExecutionError("B012 runner binding is missing")
    budget = validate_benchmark_budget(
        runtime_cfg=runtime_cfg,
        max_job_minutes=runner_cfg.get("max_job_minutes"),
    )
    return runtime_cfg, runner_cfg, budget


def _stage_prefill(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "prefill")
    _, _, lock = _require_stage_main(repo_root, state)
    runtime_cfg, _, budget = _runtime_configuration(lock)
    execution_started = state.get("execution_started_monotonic")
    if not isinstance(execution_started, (int, float)) or isinstance(execution_started, bool):
        raise ExecutionError("B012 staged execution monotonic start is invalid")

    benchmark_started = time.monotonic()
    pre_benchmark_elapsed = max(0.0, benchmark_started - float(execution_started))
    effective_budget = effective_benchmark_wall_budget(
        budget=budget,
        pre_benchmark_elapsed_seconds=pre_benchmark_elapsed,
    )
    runtime_budget_observation: dict[str, object] = {
        **budget,
        "pre_benchmark_elapsed_seconds": pre_benchmark_elapsed,
        "effective_benchmark_wall_budget_seconds": effective_budget,
        "benchmark_started_monotonic": benchmark_started,
        "shared_across_prefill_and_decode_processes": True,
    }
    tool_identity = state.get("tool_identity")
    if not isinstance(tool_identity, dict):
        raise ExecutionError("B012 staged tool identity is missing")
    runtime_commit = tool_identity.get("runtime_commit")
    if not isinstance(runtime_commit, str):
        raise ExecutionError("B012 staged runtime commit is missing")

    prefill = measure_set_bounded(
        arm="prefill_8k",
        executable=_path_from_state(state, "bench"),
        model=_path_from_state(state, "q4"),
        prompt_tokens=_runtime_integer(runtime_cfg, "prompt_tokens"),
        generated_tokens=0,
        threads=_runtime_integer(runtime_cfg, "threads"),
        runtime_commit=runtime_commit,
        warmups=_runtime_integer(runtime_cfg, "warmups_excluded"),
        measured=_runtime_integer(runtime_cfg, "measured_repetitions"),
        configured_timeout_seconds=budget["per_invocation_timeout_seconds"],
        budget_seconds=effective_budget,
        benchmark_started_monotonic=benchmark_started,
    )
    state["runtime_benchmark_budget"] = runtime_budget_observation
    state["runtime_prefill_8k"] = prefill
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="prefill",
        checkpoint_payload={
            "runtime_benchmark_budget": runtime_budget_observation,
            "prefill_8k": prefill,
        },
    )


def _stage_decode(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "decode")
    _, _, lock = _require_stage_main(repo_root, state)
    runtime_cfg, _, budget = _runtime_configuration(lock)
    observation = state.get("runtime_benchmark_budget")
    if not isinstance(observation, dict):
        raise ExecutionError("B012 staged runtime budget observation is missing")
    benchmark_started = observation.get("benchmark_started_monotonic")
    effective_budget = observation.get("effective_benchmark_wall_budget_seconds")
    if (
        isinstance(benchmark_started, bool)
        or not isinstance(benchmark_started, (int, float))
        or isinstance(effective_budget, bool)
        or not isinstance(effective_budget, (int, float))
        or float(effective_budget) <= 0
    ):
        raise ExecutionError("B012 staged shared benchmark clock is invalid")
    if observation.get("per_invocation_timeout_seconds") != budget["per_invocation_timeout_seconds"]:
        raise ExecutionError("B012 staged benchmark timeout drift detected")
    if observation.get("benchmark_wall_budget_seconds") != budget["benchmark_wall_budget_seconds"]:
        raise ExecutionError("B012 staged benchmark wall budget drift detected")

    tool_identity = state.get("tool_identity")
    if not isinstance(tool_identity, dict) or not isinstance(tool_identity.get("runtime_commit"), str):
        raise ExecutionError("B012 staged runtime identity is missing")
    decode = measure_set_bounded(
        arm="isolated_decode_128",
        executable=_path_from_state(state, "bench"),
        model=_path_from_state(state, "q4"),
        prompt_tokens=0,
        generated_tokens=_runtime_integer(runtime_cfg, "decode_tokens"),
        threads=_runtime_integer(runtime_cfg, "threads"),
        runtime_commit=str(tool_identity["runtime_commit"]),
        warmups=_runtime_integer(runtime_cfg, "warmups_excluded"),
        measured=_runtime_integer(runtime_cfg, "measured_repetitions"),
        configured_timeout_seconds=budget["per_invocation_timeout_seconds"],
        budget_seconds=float(effective_budget),
        benchmark_started_monotonic=float(benchmark_started),
    )
    state["runtime_decode_128"] = decode
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="decode",
        checkpoint_payload={
            "shared_benchmark_started_monotonic": float(benchmark_started),
            "effective_benchmark_wall_budget_seconds": float(effective_budget),
            "isolated_decode_128": decode,
        },
    )


def _stage_raw_code(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "raw-code")
    _require_stage_main(repo_root, state)
    raw_manifest = read_json(repo_root / RAW_CODE_PATH)
    raw_code = run_raw_code_proxy(
        executable=_path_from_state(state, "cli"),
        model=_path_from_state(state, "q4"),
        manifest=raw_manifest,
    )
    state["raw_code_proxy"] = raw_code
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="raw-code",
        checkpoint_payload={"raw_code_proxy": raw_code},
    )


def _stage_finalize(
    *, repo_root: Path, output_dir: Path, candidate: str
) -> None:
    state = _load_state(output_dir, candidate, "finalize")
    _require_stage_main(repo_root, state)
    canonical_end = _require_live_main(repo_root)
    q4_path_value = state.get("q4_manifest_path")
    if not isinstance(q4_path_value, str):
        raise ExecutionError("B012 staged Q4 manifest path is missing")
    q4_path = Path(q4_path_value)
    if not q4_path.is_file():
        raise ExecutionError("B012 staged Q4 manifest file is missing")
    source_verification = state.get("source_verification")
    prefill = state.get("runtime_prefill_8k")
    decode = state.get("runtime_decode_128")
    raw_code = state.get("raw_code_proxy")
    runtime_budget = state.get("runtime_benchmark_budget")
    quantization = state.get("quantization")
    if not isinstance(source_verification, list):
        raise ExecutionError("B012 staged source verification is missing")
    if not all(isinstance(value, dict) for value in (prefill, decode, raw_code, runtime_budget, quantization)):
        raise ExecutionError("B012 staged qualification evidence is incomplete")

    result = {
        "schema_version": "mstr.b012-equivalent-qualification-result.v1",
        "task_id": "B012",
        "candidate_id": candidate,
        "result_classification": "B012_EQUIVALENT_EVIDENCE_COMPLETE",
        "candidate_admission_decision": "NOT_MADE_BY_B012_EXECUTOR",
        "canonical_main_at_start": state["canonical_main_at_start"],
        "canonical_main_at_end": canonical_end,
        "started_utc": state["started_utc"],
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "paid_cost_usd": 0.0,
        "training": False,
        "source_verification": source_verification,
        "producer_replay": state["producer_replay"],
        "tool_identity": state["tool_identity"],
        "q4_manifest_sha256": sha256_file(q4_path),
        "q4_k_m_sha256": state["q4_k_m_sha256"],
        "q4_k_m_size_bytes": state["q4_k_m_size_bytes"],
        "hosted_lane_claim": "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM",
        "runtime_benchmark_budget": runtime_budget,
        "runtime_resource": {
            "prefill_8k": prefill,
            "isolated_decode_128": decode,
        },
        "raw_code_proxy": raw_code,
        "stage_checkpoint_topology": {
            "single_ephemeral_job": True,
            "source_reacquisition_count": 1,
            "durable_checkpoints_json_only": True,
            "completed_stages_before_finalization": _completed_stages(state),
        },
    }
    qualification_path = output_dir / f"B012-{candidate}-qualification.json"
    _write(qualification_path, result)
    state["qualification_path"] = str(qualification_path)
    state["canonical_main_at_end"] = canonical_end
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="finalize",
        checkpoint_payload={
            "qualification_sha256": sha256_file(qualification_path),
            "canonical_main_at_end": canonical_end,
            "result_classification": "B012_EQUIVALENT_EVIDENCE_COMPLETE",
        },
    )
    _failure_path(output_dir, candidate).unlink(missing_ok=True)


def _write_failure(
    *,
    output_dir: Path,
    candidate: str,
    stage: str,
    exc: BaseException,
) -> None:
    state_path = _state_path(output_dir, candidate)
    state: dict[str, object] = {}
    if state_path.is_file():
        try:
            state = _read(state_path)
        except (OSError, ValueError, json.JSONDecodeError, ExecutionError):
            state = {}
    failure: dict[str, object] = {
        "schema_version": "mstr.b012-equivalent-qualification-failure.v1",
        "task_id": "B012",
        "candidate_id": candidate,
        "result_classification": "B012_EXECUTION_FAILED_CLOSED",
        "canonical_main_at_start": state.get("canonical_main_at_start", "UNKNOWN"),
        "started_utc": state.get("started_utc", "UNKNOWN"),
        "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "execution_stage": f"STAGED_{stage.upper().replace('-', '_')}",
        "completed_stages": state.get("completed_stages", []),
        "last_durable_checkpoint_stage": state.get("last_completed_stage"),
        "model_access_state": state.get("model_access_state", "UNKNOWN_UNRECORDED"),
        "producer_replay": state.get("producer_replay"),
        "error_type": type(exc).__name__,
        "error": str(exc),
        "paid_cost_usd": 0.0,
        "training": False,
        "topology": "SINGLE_EPHEMERAL_JOB_WITH_JSON_STAGE_CHECKPOINTS",
    }
    if isinstance(exc, B012BenchmarkError):
        failure["benchmark_context"] = exc.context
    _write(_failure_path(output_dir, candidate), failure)


def run_stage(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    workdir = args.workdir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        if args.stage == "init":
            _stage_init(
                repo_root=repo_root,
                output_dir=output_dir,
                workdir=workdir,
                candidate=args.candidate,
            )
        elif args.stage == "source":
            _stage_source(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        elif args.stage == "quantize":
            _stage_quantize(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        elif args.stage == "prefill":
            _stage_prefill(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        elif args.stage == "decode":
            _stage_decode(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        elif args.stage == "raw-code":
            _stage_raw_code(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        elif args.stage == "finalize":
            _stage_finalize(repo_root=repo_root, output_dir=output_dir, candidate=args.candidate)
        else:
            raise ExecutionError(f"unsupported B012 stage: {args.stage}")
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
        _write_failure(
            output_dir=output_dir,
            candidate=args.candidate,
            stage=args.stage,
            exc=exc,
        )
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--candidate",
        required=True,
        choices=["mellum-4b", "qwen3.5-0.8b-control"],
    )
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "mstr-b012",
    )
    return run_stage(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
