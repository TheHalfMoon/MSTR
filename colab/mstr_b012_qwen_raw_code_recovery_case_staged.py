#!/usr/bin/env python3
"""Case-staged B012 Qwen raw-code recovery with per-case durable checkpoints."""

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
from mstr_b012_qwen_raw_code_recovery_staged import (
    CANDIDATE_ID,
    EXPECTED_Q4_K_M_SHA256,
    EXPECTED_Q4_K_M_SIZE_BYTES,
    PRIOR_MAIN,
    PRIOR_RUN_ID,
    PRIOR_STAGE05_ARTIFACT_DIGEST,
    PRIOR_STAGE05_ARTIFACT_ID,
    PRIOR_STAGE05_CHECKPOINT_SHA256,
    _prepare_minimal_tools,
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

TRIGGERING_INCIDENT_RUN_ID = 34231845282
REPAIR_MANIFEST_PATH = Path(
    "artifacts/manifests/B012-qwen-raw-code-recovery-case-staged-topology.json"
)
CASE_STAGED_SCRIPT_PATH = Path("colab/mstr_b012_qwen_raw_code_recovery_case_staged.py")
CASE_STAGED_WORKFLOW_PATH = Path(
    "configs/workflows/b012-qwen-raw-code-recovery-case-staged.yml"
)

RAW_CODE_TASK_ORDER = (
    "python-clamp",
    "python-dedupe",
    "python-safe-divide",
)
TASK_BY_STAGE = {
    "raw-code-python-clamp": "python-clamp",
    "raw-code-python-dedupe": "python-dedupe",
    "raw-code-python-safe-divide": "python-safe-divide",
}
STAGES = (
    "init",
    "source",
    "quantize",
    "raw-code-python-clamp",
    "raw-code-python-dedupe",
    "raw-code-python-safe-divide",
    "finalize",
)
STAGE_LABELS = {
    "init": "01-init",
    "source": "02-source",
    "quantize": "03-quantize",
    "raw-code-python-clamp": "04a-raw-code-python-clamp",
    "raw-code-python-dedupe": "04b-raw-code-python-dedupe",
    "raw-code-python-safe-divide": "04c-raw-code-python-safe-divide",
    "finalize": "05-finalize",
}
PREDECESSORS: dict[str, str | None] = {
    "init": None,
    "source": "init",
    "quantize": "source",
    "raw-code-python-clamp": "quantize",
    "raw-code-python-dedupe": "raw-code-python-clamp",
    "raw-code-python-safe-divide": "raw-code-python-dedupe",
    "finalize": "raw-code-python-safe-divide",
}


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ExecutionError(f"B012 Qwen case-staged JSON object is invalid: {path}")
    return payload


def _state_path(output_dir: Path) -> Path:
    return output_dir / f"B012-{CANDIDATE_ID}-raw-code-recovery-case-stage-state.json"


def _failure_path(output_dir: Path) -> Path:
    return output_dir / f"B012-{CANDIDATE_ID}-raw-code-recovery-case-failure.json"


def _checkpoint_path(output_dir: Path, stage: str) -> Path:
    return output_dir / (
        f"B012-{CANDIDATE_ID}-raw-code-recovery-case-checkpoint-{STAGE_LABELS[stage]}.json"
    )


def _result_path(output_dir: Path) -> Path:
    return output_dir / f"B012-{CANDIDATE_ID}-raw-code-recovery.json"


def _completed_stages(state: dict[str, object]) -> list[str]:
    completed = state.get("completed_stages")
    if not isinstance(completed, list) or not all(isinstance(item, str) for item in completed):
        raise ExecutionError("B012 Qwen case-staged completed-stage state is invalid")
    return list(completed)


def _path_from_state(state: dict[str, object], key: str) -> Path:
    paths = state.get("local_ephemeral_paths")
    if not isinstance(paths, dict):
        raise ExecutionError("B012 Qwen case-staged local path state is missing")
    value = paths.get(key)
    if not isinstance(value, str) or not value:
        raise ExecutionError(f"B012 Qwen case-staged local path is missing: {key}")
    return Path(value)


def _load_state(output_dir: Path, stage: str) -> dict[str, object]:
    if stage == "init":
        raise ExecutionError("B012 Qwen case-staged init must not load prior state")
    state = _read(_state_path(output_dir))
    if state.get("task_id") != "B012" or state.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen case-staged state identity drift detected")
    expected = PREDECESSORS[stage]
    completed = _completed_stages(state)
    if expected is None or not completed or completed[-1] != expected:
        raise ExecutionError(
            f"B012 Qwen case-staged transition invalid: stage={stage}, predecessor={expected}"
        )
    if stage in completed:
        raise ExecutionError(f"B012 Qwen case-staged action already completed: {stage}")
    return state


def _require_repair_activation(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    binding, envelope, lock = _require_binding(repo_root)
    repair = read_json(repo_root / REPAIR_MANIFEST_PATH)
    if repair.get("status") != "READY_FOR_SEPARATE_CANONICAL_ACTIVATION":
        raise ExecutionError("B012 Qwen case-staged repair manifest is not activation-ready")
    activation = binding.get("qwen_raw_code_recovery_case_staged_activation")
    if not isinstance(activation, dict):
        raise ExecutionError("B012 Qwen case-staged recovery is not activated")
    if activation.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen case-staged activation candidate drift detected")
    if activation.get("prior_run_id") != PRIOR_RUN_ID:
        raise ExecutionError("B012 Qwen case-staged activation prior-run drift detected")
    if activation.get("triggering_incident_run_id") != TRIGGERING_INCIDENT_RUN_ID:
        raise ExecutionError("B012 Qwen case-staged activation incident drift detected")

    expected_manifest = activation.get("repair_manifest_sha256")
    expected_script = activation.get("case_staged_script_sha256")
    expected_workflow = activation.get("active_workflow_sha256")
    if not all(
        isinstance(value, str) for value in (expected_manifest, expected_script, expected_workflow)
    ):
        raise ExecutionError("B012 Qwen case-staged activation hash binding is incomplete")
    require_file_sha256(repo_root / REPAIR_MANIFEST_PATH, str(expected_manifest))
    require_file_sha256(repo_root / CASE_STAGED_SCRIPT_PATH, str(expected_script))
    require_file_sha256(
        repo_root / ".github/workflows/b012-qwen-raw-code-recovery.yml",
        str(expected_workflow),
    )
    for key in (
        "retry_authority_created",
        "external_dispatch_authority_created",
        "candidate_expansion",
        "revision_or_file_expansion",
        "training",
        "weight_changing_training",
        "paid_compute",
        "paid_model_api",
        "production_release",
    ):
        if activation.get(key) is not False:
            raise ExecutionError(f"B012 Qwen case-staged activation widens boundary: {key}")
    return binding, envelope, lock, repair


def _require_stage_main(
    repo_root: Path, state: dict[str, object]
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    live = _require_live_main(repo_root)
    canonical_start = state.get("canonical_main_at_start")
    if not isinstance(canonical_start, str) or live != canonical_start:
        raise ExecutionError(
            f"B012 Qwen case-staged canonical-main drift: start={canonical_start}, live={live}"
        )
    return _require_repair_activation(repo_root)


def _require_same_main(repo_root: Path, state: dict[str, object]) -> str:
    live = _require_live_main(repo_root)
    canonical_start = state.get("canonical_main_at_start")
    if not isinstance(canonical_start, str) or live != canonical_start:
        raise ExecutionError(
            f"B012 Qwen case-staged canonical-main drift: start={canonical_start}, live={live}"
        )
    return live


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
            raise ExecutionError("B012 Qwen case-staged init unexpectedly has predecessors")
    elif not completed or completed[-1] != expected:
        raise ExecutionError(
            f"B012 Qwen case-stage completion order invalid: stage={stage}, predecessor={expected}"
        )
    completed.append(stage)
    state["completed_stages"] = completed
    state["last_completed_stage"] = stage
    _write(_state_path(output_dir), state)
    _write(
        _checkpoint_path(output_dir, stage),
        {
            "schema_version": "mstr.b012-qwen-raw-code-recovery-case-checkpoint.v1",
            "task_id": "B012",
            "candidate_id": CANDIDATE_ID,
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
        },
    )


def _single_case_manifest(
    raw_manifest: dict[str, object], task_id: str
) -> dict[str, object]:
    tasks = raw_manifest.get("tasks")
    if not isinstance(tasks, list):
        raise ExecutionError("B012 raw-code task list is invalid")
    ids = [task.get("id") for task in tasks if isinstance(task, dict)]
    if ids != list(RAW_CODE_TASK_ORDER):
        raise ExecutionError(f"B012 raw-code task order drift detected: {ids}")
    selected = [task for task in tasks if isinstance(task, dict) and task.get("id") == task_id]
    if len(selected) != 1:
        raise ExecutionError(f"B012 raw-code task selection failed: {task_id}")
    case_manifest = dict(raw_manifest)
    case_manifest["tasks"] = selected
    return case_manifest


def _aggregate_case_results(case_results: dict[str, object]) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    syntax_pass_count = 0
    for task_id in RAW_CODE_TASK_ORDER:
        result = case_results.get(task_id)
        if not isinstance(result, dict):
            raise ExecutionError(f"B012 raw-code case result is missing: {task_id}")
        if result.get("task_count") != 1:
            raise ExecutionError(f"B012 raw-code case result count drift: {task_id}")
        case_rows = result.get("rows")
        if (
            not isinstance(case_rows, list)
            or len(case_rows) != 1
            or not isinstance(case_rows[0], dict)
            or case_rows[0].get("task_id") != task_id
        ):
            raise ExecutionError(f"B012 raw-code case row identity drift: {task_id}")
        pass_count = result.get("syntax_pass_count")
        if not isinstance(pass_count, int) or pass_count not in (0, 1):
            raise ExecutionError(f"B012 raw-code syntax count drift: {task_id}")
        syntax_pass_count += pass_count
        rows.append(dict(case_rows[0]))
    return {
        "task_count": len(rows),
        "syntax_pass_count": syntax_pass_count,
        "syntax_pass_rate": syntax_pass_count / len(rows),
        "rows": rows,
        "interpretation": "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION",
    }


def _stage_init(*, repo_root: Path, output_dir: Path, workdir: Path) -> None:
    if workdir.exists():
        shutil.rmtree(workdir)
    workdir.mkdir(parents=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in output_dir.glob(f"B012-{CANDIDATE_ID}-raw-code-recovery*.json"):
        path.unlink()

    canonical_start = _require_live_main(repo_root)
    _, _, lock, repair = _require_repair_activation(repo_root)
    if canonical_start in (PRIOR_MAIN, str(repair.get("base_main", ""))):
        raise ExecutionError("B012 Qwen case-staged recovery requires later canonical activation")
    python_exe, replay_identity = install_replay_toolchain(
        base_lock_path=repo_root / T031_LOCK_PATH,
        overlay_path=repo_root / T031_REPLAY_OVERLAY_PATH,
        root=workdir / "python",
    )
    conversion_dir, quantizer, cli, tool_identity = _prepare_minimal_tools(
        lock=lock, workdir=workdir
    )
    canonical_end = _require_live_main(repo_root)
    if canonical_end != canonical_start:
        raise ExecutionError("B012 Qwen canonical main moved during case-staged initialization")

    state: dict[str, object] = {
        "schema_version": "mstr.b012-qwen-raw-code-recovery-case-stage-state.v1",
        "task_id": "B012",
        "candidate_id": CANDIDATE_ID,
        "canonical_main_at_start": canonical_start,
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_stages": [],
        "last_completed_stage": None,
        "model_access_state": "NONE",
        "training": False,
        "paid_cost_usd": 0.0,
        "producer_replay": replay_identity,
        "tool_identity": tool_identity,
        "repair_id": repair.get("repair_id"),
        "triggering_incident_run_id": TRIGGERING_INCIDENT_RUN_ID,
        "raw_code_case_results": {},
        "local_ephemeral_paths": {
            "workdir": str(workdir),
            "python_exe": str(python_exe),
            "conversion_dir": str(conversion_dir),
            "quantizer": str(quantizer),
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
            "triggering_incident_run_id": TRIGGERING_INCIDENT_RUN_ID,
        },
    )


def _stage_source(*, repo_root: Path, output_dir: Path) -> None:
    state = _load_state(output_dir, "source")
    _, envelope, _, _ = _require_stage_main(repo_root, state)
    source_dir = _path_from_state(state, "workdir") / "source" / CANDIDATE_ID
    state["model_access_state"] = "EXACT_B010_FILE_REACQUISITION_IN_PROGRESS"
    _write(_state_path(output_dir), state)
    source_records = download_candidate(
        repo_root=repo_root,
        envelope=envelope,
        candidate_id=CANDIDATE_ID,
        destination=source_dir,
    )
    _require_same_main(repo_root, state)
    state["model_access_state"] = "EXACT_B010_FILES_REACQUIRED_VERIFIED"
    state["source_verification"] = source_records
    paths = state.get("local_ephemeral_paths")
    if not isinstance(paths, dict):
        raise ExecutionError("B012 Qwen case-staged local path state invalid after source")
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


def _stage_quantize(*, repo_root: Path, output_dir: Path) -> None:
    state = _load_state(output_dir, "quantize")
    _require_stage_main(repo_root, state)
    state["model_access_state"] = "EXACT_Q4_REGENERATION_IN_PROGRESS"
    _write(_state_path(output_dir), state)
    q4, quantization = convert_quantize(
        python_exe=_path_from_state(state, "python_exe"),
        conversion_dir=_path_from_state(state, "conversion_dir"),
        quantize_bin=_path_from_state(state, "quantizer"),
        source_dir=_path_from_state(state, "source_dir"),
        candidate_id=CANDIDATE_ID,
        workdir=_path_from_state(state, "workdir"),
    )
    regenerated_sha = sha256_file(q4)
    regenerated_size = q4.stat().st_size
    if regenerated_sha != EXPECTED_Q4_K_M_SHA256:
        raise ExecutionError("B012 Qwen case-staged regenerated Q4 SHA-256 mismatch")
    if regenerated_size != EXPECTED_Q4_K_M_SIZE_BYTES:
        raise ExecutionError("B012 Qwen case-staged regenerated Q4 size mismatch")
    _require_same_main(repo_root, state)
    state["model_access_state"] = "EXACT_Q4_REGENERATED_VERIFIED"
    state["regenerated_q4"] = {
        "sha256": regenerated_sha,
        "size_bytes": regenerated_size,
        "matches_prior_stage03": True,
        "quantization": quantization,
    }
    paths = state.get("local_ephemeral_paths")
    if not isinstance(paths, dict):
        raise ExecutionError("B012 Qwen case-staged local path state invalid after quantize")
    paths["q4"] = str(q4)
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="quantize",
        checkpoint_payload={
            "q4_k_m_sha256": regenerated_sha,
            "q4_k_m_size_bytes": regenerated_size,
            "matches_prior_stage03": True,
            "quantization": quantization,
        },
    )


def _stage_raw_code_case(*, repo_root: Path, output_dir: Path, stage: str) -> None:
    task_id = TASK_BY_STAGE.get(stage)
    if task_id is None:
        raise ExecutionError(f"unsupported B012 Qwen raw-code case stage: {stage}")
    state = _load_state(output_dir, stage)
    _require_stage_main(repo_root, state)
    state["model_access_state"] = f"RAW_CODE_CASE_EXECUTION_IN_PROGRESS:{task_id}"
    _write(_state_path(output_dir), state)

    raw_manifest = read_json(repo_root / RAW_CODE_PATH)
    raw_code_case = run_raw_code_proxy(
        executable=_path_from_state(state, "cli"),
        model=_path_from_state(state, "q4"),
        manifest=_single_case_manifest(raw_manifest, task_id),
    )
    _require_same_main(repo_root, state)
    case_results = state.get("raw_code_case_results")
    if not isinstance(case_results, dict):
        raise ExecutionError("B012 Qwen raw-code case result state is invalid")
    case_results[task_id] = raw_code_case
    state["model_access_state"] = f"RAW_CODE_CASE_COMPLETE:{task_id}"
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage=stage,
        checkpoint_payload={
            "raw_code_task_id": task_id,
            "raw_code_proxy_case": raw_code_case,
            "maximum_uncheckpointed_raw_code_cases": 1,
        },
    )


def _stage_finalize(*, repo_root: Path, output_dir: Path) -> None:
    state = _load_state(output_dir, "finalize")
    _require_stage_main(repo_root, state)
    source_records = state.get("source_verification")
    regenerated_q4 = state.get("regenerated_q4")
    case_results = state.get("raw_code_case_results")
    if not isinstance(source_records, list):
        raise ExecutionError("B012 Qwen case-staged source verification is missing")
    if not isinstance(regenerated_q4, dict):
        raise ExecutionError("B012 Qwen case-staged Q4 evidence is missing")
    if not isinstance(case_results, dict):
        raise ExecutionError("B012 Qwen case-staged raw-code case evidence is missing")
    raw_code = _aggregate_case_results(case_results)
    canonical_end = _require_live_main(repo_root)
    if canonical_end != state.get("canonical_main_at_start"):
        raise ExecutionError("B012 Qwen case-staged canonical main moved before finalize")
    verified_bytes = sum(
        int(record["size_bytes"])
        for record in source_records
        if isinstance(record, dict) and isinstance(record.get("size_bytes"), int)
    )
    result = {
        "schema_version": "mstr.b012-qwen-raw-code-recovery-result.v3",
        "task_id": "B012",
        "candidate_id": CANDIDATE_ID,
        "result_classification": "B012_RAW_CODE_RECOVERY_COMPLETE",
        "candidate_admission_decision": "NOT_MADE_BY_B012_RECOVERY",
        "canonical_main_at_start": state["canonical_main_at_start"],
        "canonical_main_at_end": canonical_end,
        "started_utc": state.get("started_utc"),
        "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed_stages": list(STAGES),
        "prior_stage_evidence": {
            "run_id": PRIOR_RUN_ID,
            "canonical_main": PRIOR_MAIN,
            "stage05_artifact_id": PRIOR_STAGE05_ARTIFACT_ID,
            "stage05_artifact_digest": PRIOR_STAGE05_ARTIFACT_DIGEST,
            "stage05_checkpoint_sha256": PRIOR_STAGE05_CHECKPOINT_SHA256,
            "prefill_decode_rerun": False,
        },
        "repair_lineage": {
            "triggering_incident_run_id": TRIGGERING_INCIDENT_RUN_ID,
            "raw_code_case_order": list(RAW_CODE_TASK_ORDER),
            "maximum_uncheckpointed_raw_code_cases": 1,
        },
        "source_reacquisition": {
            "verified_download_bytes": verified_bytes,
            "source_verification": source_records,
        },
        "producer_replay": state.get("producer_replay"),
        "tool_identity": state.get("tool_identity"),
        "regenerated_q4": regenerated_q4,
        "raw_code_proxy": raw_code,
        "recovery_repair_id": state.get("repair_id"),
        "model_access_state": state.get("model_access_state"),
        "training": False,
        "paid_cost_usd": 0.0,
        "durable_binary_artifacts": False,
    }
    _write(_result_path(output_dir), result)
    _complete_stage(
        output_dir=output_dir,
        state=state,
        stage="finalize",
        checkpoint_payload={
            "result_classification": "B012_RAW_CODE_RECOVERY_COMPLETE",
            "result_json_sha256": sha256_file(_result_path(output_dir)),
            "candidate_admission_decision": "NOT_MADE_BY_B012_RECOVERY",
            "raw_code_case_order": list(RAW_CODE_TASK_ORDER),
        },
    )


def _write_failure(*, output_dir: Path, stage: str, exc: Exception) -> None:
    state_path = _state_path(output_dir)
    state = _read(state_path) if state_path.exists() else {}
    completed_case_ids = [
        TASK_BY_STAGE[item]
        for item in state.get("completed_stages", [])
        if isinstance(item, str) and item in TASK_BY_STAGE
    ]
    failure = {
        "schema_version": "mstr.b012-qwen-raw-code-recovery-case-failure.v1",
        "task_id": "B012",
        "candidate_id": CANDIDATE_ID,
        "result_classification": "B012_RAW_CODE_RECOVERY_FAILED_CLOSED",
        "execution_stage": f"CASE_STAGED_{stage.upper().replace('-', '_')}",
        "started_utc": state.get("started_utc"),
        "failed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prior_run_id": PRIOR_RUN_ID,
        "triggering_incident_run_id": TRIGGERING_INCIDENT_RUN_ID,
        "error_type": type(exc).__name__,
        "error": str(exc),
        "completed_stages": state.get("completed_stages", []),
        "completed_raw_code_case_ids": completed_case_ids,
        "last_durable_checkpoint_stage": state.get("last_completed_stage"),
        "model_access_state": state.get("model_access_state", "NONE_OR_UNKNOWN"),
        "expected_q4_k_m_sha256": EXPECTED_Q4_K_M_SHA256,
        "expected_q4_k_m_size_bytes": EXPECTED_Q4_K_M_SIZE_BYTES,
        "candidate_admission_decision": "NONE",
        "model_quality_verdict": "NONE",
        "retry_authority_created": False,
        "external_dispatch_authority_created": False,
        "training": False,
        "paid_cost_usd": 0.0,
    }
    _write(_failure_path(output_dir), failure)


def execute(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = args.output_dir.resolve()
    workdir = args.workdir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        if args.stage == "init":
            _stage_init(repo_root=repo_root, output_dir=output_dir, workdir=workdir)
        elif args.stage == "source":
            _stage_source(repo_root=repo_root, output_dir=output_dir)
        elif args.stage == "quantize":
            _stage_quantize(repo_root=repo_root, output_dir=output_dir)
        elif args.stage in TASK_BY_STAGE:
            _stage_raw_code_case(repo_root=repo_root, output_dir=output_dir, stage=args.stage)
        elif args.stage == "finalize":
            _stage_finalize(repo_root=repo_root, output_dir=output_dir)
        else:
            raise ExecutionError(f"unsupported B012 Qwen case-staged recovery stage: {args.stage}")
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
        _write_failure(output_dir=output_dir, stage=args.stage, exc=exc)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    return execute(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
