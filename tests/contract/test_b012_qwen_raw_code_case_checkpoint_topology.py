from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_qwen_raw_code_recovery_case_checkpoint as case_checkpoint  # noqa: E402

MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-case-checkpoint-topology.json"
SCRIPT = COLAB / "mstr_b012_qwen_raw_code_recovery_case_checkpoint.py"
WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-case-checkpoint-recovery.yml"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"
RAW_CODE = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"
INCIDENT = ROOT / (
    "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-raw-code-staged-recovery-run-34231845282.json"
)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_case_checkpoint_repair_is_hash_bound_and_non_authorizing() -> None:
    manifest = _read_json(MANIFEST)
    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert manifest["base_main"] == "2d35efe6d7350f6aa0241ee9de128134cd321f90"
    assert manifest["candidate_id"] == "qwen3.5-0.8b-control"
    assert manifest["prior_qualification_run_id"] == 34155931982
    assert manifest["case_checkpoint_script_sha256"] == _sha256(SCRIPT)
    assert manifest["case_checkpoint_workflow_sha256"] == _sha256(WORKFLOW)
    assert manifest["raw_code_manifest_sha256"] == _sha256(RAW_CODE)

    authority = manifest["authority_boundary"]
    assert isinstance(authority, dict)
    assert authority["existing_authority_id"] == (
        "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"
    )
    for key in (
        "authority_scope_modified",
        "authority_transfer",
        "retry_authority_created",
        "external_dispatch_authority_created",
        "candidate_expansion",
        "candidate_revision_or_file_expansion",
        "training",
        "weight_changing_training",
        "paid_compute",
        "paid_model_api",
        "production_release",
    ):
        assert authority[key] is False
    assert authority["git_model_binaries"] == 0
    assert authority["founder_machine_model_binaries"] == 0
    assert authority["paid_cost_usd"] == 0.0


def test_case_checkpoint_topology_has_exact_frozen_case_order() -> None:
    manifest = _read_json(MANIFEST)
    topology = manifest["topology"]
    durability = manifest["durability_boundary"]
    assert isinstance(topology, dict)
    assert isinstance(durability, dict)

    expected_cases = ["python-clamp", "python-dedupe", "python-safe-divide"]
    expected_stages = [
        "init",
        "source",
        "quantize",
        "raw-code-python-clamp",
        "raw-code-python-dedupe",
        "raw-code-python-safe-divide",
        "finalize",
    ]
    assert list(case_checkpoint.CASE_IDS) == expected_cases
    assert list(case_checkpoint.STAGES) == expected_stages
    assert topology["raw_code_case_order"] == expected_cases
    assert topology["stages"] == expected_stages
    assert topology["maximum_uncheckpointed_raw_code_cases"] == 1
    assert topology["durable_upload_after_each_raw_code_case"] is True
    assert topology["durable_checkpoint_format"] == "JSON_ONLY"
    assert topology["single_ephemeral_job"] is True
    assert topology["max_job_minutes"] == 45
    assert topology["source_reacquisition_count_per_dispatch"] == 1
    assert topology["prefill_rerun"] is False
    assert topology["decode_rerun"] is False
    assert topology["large_binary_artifact_uploads"] is False
    assert durability["each_raw_code_case_reverifies_exact_q4_before_model_execution"] is True
    assert durability["each_completed_raw_code_case_upload_precedes_next_case"] is True
    assert durability["cross_run_resume_authority_created"] is False
    assert durability["same_failed_topology_redispatch_authorized"] is False


def test_case_checkpoint_repair_preserves_exact_raw_code_manifest() -> None:
    manifest = _read_json(MANIFEST)
    semantic = manifest["semantic_preservation"]
    assert isinstance(semantic, dict)
    raw = _read_json(RAW_CODE)
    tasks = raw["tasks"]
    assert isinstance(tasks, list)
    assert [task["id"] for task in tasks if isinstance(task, dict)] == [
        "python-clamp",
        "python-dedupe",
        "python-safe-divide",
    ]
    for key in (
        "raw_code_manifest_unchanged",
        "raw_code_case_set_unchanged",
        "raw_code_case_order_unchanged",
        "raw_code_prompts_unchanged",
        "raw_code_sampling_unchanged",
        "raw_code_helper_unchanged",
        "runtime_and_tool_revisions_unchanged",
        "candidate_admission_not_decided_by_recovery",
        "score_is_observation_not_admission_gate",
    ):
        assert semantic[key] is True


def test_case_checkpoint_workflow_is_non_active_and_json_only() -> None:
    manifest = _read_json(MANIFEST)
    activation = manifest["activation"]
    assert isinstance(activation, dict)
    workflow = WORKFLOW.read_text(encoding="utf-8")
    active = ACTIVE_WORKFLOW.read_text(encoding="utf-8")

    assert activation["active_workflow_materialized"] is False
    assert WORKFLOW.read_bytes() != ACTIVE_WORKFLOW.read_bytes()
    assert "B012_RECOVER_RAW_CODE_STAGED qwen3.5-0.8b-control 34155931982" in active
    assert "B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982" in workflow
    assert "timeout-minutes: 45" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "if: always()" in workflow
    for case_id in ("python-clamp", "python-dedupe", "python-safe-divide"):
        assert f"--stage raw-code-{case_id}" in workflow
    upload_pin = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    assert workflow.count(upload_pin) == 7
    assert workflow.count("${{ runner.temp }}/b012-qwen-raw-code-results/*.json") == 7
    assert ".gguf" not in workflow
    assert ".safetensors" not in workflow
    assert "actions/download-artifact@" not in workflow
    assert "actions/cache@" not in workflow


def test_single_case_manifest_preserves_execution_and_selects_one_frozen_case() -> None:
    raw = _read_json(RAW_CODE)
    selected = case_checkpoint._single_case_manifest(raw, "python-dedupe")
    assert selected["execution"] == raw["execution"]
    assert selected["verification"] == raw["verification"]
    tasks = selected["tasks"]
    assert isinstance(tasks, list)
    assert len(tasks) == 1
    assert isinstance(tasks[0], dict)
    assert tasks[0] == raw["tasks"][1]
    assert selected is not raw


def test_aggregate_raw_code_proxy_preserves_frozen_order_and_observation_semantics() -> None:
    state: dict[str, object] = {
        "raw_code_case_results": {
            "python-clamp": {
                "task_count": 1,
                "rows": [{"task_id": "python-clamp", "syntax_valid": True}],
            },
            "python-dedupe": {
                "task_count": 1,
                "rows": [{"task_id": "python-dedupe", "syntax_valid": False}],
            },
            "python-safe-divide": {
                "task_count": 1,
                "rows": [{"task_id": "python-safe-divide", "syntax_valid": True}],
            },
        }
    }
    aggregate = case_checkpoint._aggregate_raw_code_proxy(state)
    assert aggregate["task_count"] == 3
    assert aggregate["syntax_pass_count"] == 2
    assert aggregate["syntax_pass_rate"] == 2 / 3
    rows = aggregate["rows"]
    assert isinstance(rows, list)
    assert [row["task_id"] for row in rows if isinstance(row, dict)] == [
        "python-clamp",
        "python-dedupe",
        "python-safe-divide",
    ]
    assert aggregate["interpretation"] == "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION"


def test_case_checkpoint_incident_prerequisite_is_canonical_and_fail_closed() -> None:
    manifest = _read_json(MANIFEST)
    incident = _read_json(INCIDENT)
    trigger = manifest["triggering_incident"]
    assert isinstance(trigger, dict)
    assert trigger["run_id"] == 34231845282
    assert trigger["canonical_incident_merge_commit"] == (
        "2d35efe6d7350f6aa0241ee9de128134cd321f90"
    )
    assert trigger["canonical_incident_postmerge_run_id"] == 34250328560
    assert incident["failure_classification"] == (
        "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN"
    )
    assert incident["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["candidate_admission_decision"] == "NONE"
    assert incident["retry_authority_created"] is False
    assert incident["external_dispatch_authority_created"] is False


def test_checkpoint_payload_is_json_only_and_non_authorizing(tmp_path: Path) -> None:
    state: dict[str, object] = {
        "task_id": "B012",
        "candidate_id": "qwen3.5-0.8b-control",
        "canonical_main_at_start": "a" * 40,
        "completed_stages": [],
        "last_completed_stage": None,
        "model_access_state": "NONE",
    }
    case_checkpoint._complete_stage(
        output_dir=tmp_path,
        state=state,
        stage="init",
        checkpoint_payload={"synthetic": True},
    )
    checkpoint = _read_json(
        tmp_path / "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-01-init.json"
    )
    assert checkpoint["stage"] == "init"
    assert checkpoint["completed_stages"] == ["init"]
    assert checkpoint["training"] is False
    assert checkpoint["paid_cost_usd"] == 0.0
    assert checkpoint["durable_binary_artifacts"] is False
    assert checkpoint["durable_output_format"] == "JSON_ONLY"
