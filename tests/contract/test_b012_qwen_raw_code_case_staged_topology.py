from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_qwen_raw_code_recovery_case_staged as repair  # noqa: E402

MANIFEST = (
    ROOT
    / "artifacts/manifests/B012-qwen-raw-code-recovery-case-staged-topology.json"
)
SCRIPT = COLAB / "mstr_b012_qwen_raw_code_recovery_case_staged.py"
WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-recovery-case-staged.yml"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
RAW_CODE_MANIFEST = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"
RAW_CODE_HELPER = COLAB / "mstr_b012_raw_code.py"

EXPECTED_STAGES = (
    "init",
    "source",
    "quantize",
    "raw-code-python-clamp",
    "raw-code-python-dedupe",
    "raw-code-python-safe-divide",
    "finalize",
)
EXPECTED_TASKS = (
    "python-clamp",
    "python-dedupe",
    "python-safe-divide",
)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_case_staged_repair_is_hash_bound_non_active_and_non_authorizing() -> None:
    manifest = _read_json(MANIFEST)
    binding = _read_json(BINDING)

    assert manifest["schema_version"] == (
        "mstr.b012-qwen-raw-code-case-staged-topology-repair.v1"
    )
    assert manifest["repair_id"] == (
        "B012_QWEN_RAW_CODE_CASE_STAGED_DURABILITY_REPAIR_2026_09_08"
    )
    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert manifest["base_main"] == "2d35efe6d7350f6aa0241ee9de128134cd321f90"
    assert manifest["candidate_id"] == "qwen3.5-0.8b-control"
    assert manifest["prior_qualification_run_id"] == 34155931982

    assert manifest["case_staged_script_sha256"] == _sha256(SCRIPT)
    assert manifest["case_staged_workflow_sha256"] == _sha256(WORKFLOW)
    assert manifest["raw_code_manifest_sha256"] == _sha256(RAW_CODE_MANIFEST)
    assert manifest["raw_code_helper_sha256"] == _sha256(RAW_CODE_HELPER)

    assert manifest["case_staged_script_sha256"] == (
        "e6264c2930d61e54f190a07ddc645162b658b04f694bc33a94b7c70df4a127d7"
    )
    assert manifest["case_staged_workflow_sha256"] == (
        "dc1aad036035a721473a727be28ffe051cb546e86c899a1efcd3c09f624c4565"
    )
    assert manifest["raw_code_manifest_sha256"] == (
        "038586bb8156add6bb2de8573a9d15d0f1201909c36820a6cc608a2b5d393349"
    )
    assert manifest["raw_code_helper_sha256"] == (
        "bd6d34afd8af60497a4971bb7245fc359c4132bad3772be212b6848aa73060d8"
    )

    assert binding["status"] == "BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR"
    assert "qwen_raw_code_recovery_case_staged_activation" not in binding

    activation = manifest["activation"]
    assert isinstance(activation, dict)
    assert activation["separate_activation_pr_required"] is True
    assert activation["package_performs_model_access"] is False
    assert activation["package_performs_model_execution"] is False
    assert activation["active_workflow_target"] == (
        ".github/workflows/b012-qwen-raw-code-recovery.yml"
    )
    assert activation["exact_issue_command"] == (
        "B012_RECOVER_RAW_CODE_CASE_STAGED qwen3.5-0.8b-control "
        "34155931982 34231845282"
    )

    authority = manifest["authority_boundary"]
    assert isinstance(authority, dict)
    assert authority["existing_authority_id"] == (
        "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"
    )
    for key in (
        "authority_scope_modified",
        "authority_transfer",
        "candidate_expansion",
        "candidate_revision_or_file_expansion",
        "external_dispatch_authority_created",
        "paid_compute",
        "paid_model_api",
        "production_release",
        "retry_authority_created",
        "training",
        "weight_changing_training",
    ):
        assert authority[key] is False
    assert authority["paid_cost_usd"] == 0.0
    assert authority["git_model_binaries"] == 0
    assert authority["founder_machine_model_binaries"] == 0

    assert ACTIVE_WORKFLOW.read_bytes() != WORKFLOW.read_bytes()


def test_case_staged_topology_has_one_case_per_durable_raw_code_boundary() -> None:
    manifest = _read_json(MANIFEST)
    topology = manifest["topology"]
    durability = manifest["durability_boundary"]
    assert isinstance(topology, dict)
    assert isinstance(durability, dict)

    assert repair.STAGES == EXPECTED_STAGES
    assert repair.RAW_CODE_TASK_ORDER == EXPECTED_TASKS
    assert repair.TASK_BY_STAGE == {
        "raw-code-python-clamp": "python-clamp",
        "raw-code-python-dedupe": "python-dedupe",
        "raw-code-python-safe-divide": "python-safe-divide",
    }
    assert repair.PREDECESSORS == {
        "init": None,
        "source": "init",
        "quantize": "source",
        "raw-code-python-clamp": "quantize",
        "raw-code-python-dedupe": "raw-code-python-clamp",
        "raw-code-python-safe-divide": "raw-code-python-dedupe",
        "finalize": "raw-code-python-safe-divide",
    }

    assert topology["stages"] == list(EXPECTED_STAGES)
    assert topology["raw_code_case_order"] == list(EXPECTED_TASKS)
    assert topology["raw_code_case_count"] == 3
    assert topology["maximum_uncheckpointed_raw_code_cases"] == 1
    assert topology["durable_checkpoint_after_each_completed_stage"] is True
    assert topology["durable_checkpoint_format"] == "JSON_ONLY"
    assert topology["checkpoint_upload_boundaries"] == 7
    assert topology["single_ephemeral_job"] is True
    assert topology["source_reacquisition_count_per_dispatch"] == 1
    assert topology["large_binary_artifact_uploads"] is False
    assert topology["large_binary_transfer_between_jobs"] is False

    assert durability["completed_raw_code_case_checkpoint_precedes_next_case"] is True
    assert topology["maximum_uncheckpointed_raw_code_cases"] == 1
    assert durability["prior_case_uploads_survive_later_case_shutdown"] is True


def test_case_projection_preserves_frozen_manifest_and_task_order() -> None:
    raw_manifest = _read_json(RAW_CODE_MANIFEST)
    original = json.loads(json.dumps(raw_manifest))

    for task_id in EXPECTED_TASKS:
        projected = repair._single_case_manifest(raw_manifest, task_id)
        assert projected["execution"] == raw_manifest["execution"]
        assert projected["verification"] == raw_manifest["verification"]
        tasks = projected["tasks"]
        assert isinstance(tasks, list)
        assert len(tasks) == 1
        assert isinstance(tasks[0], dict)
        assert tasks[0]["id"] == task_id

    assert raw_manifest == original


def test_case_result_aggregation_restores_original_observational_shape() -> None:
    case_results: dict[str, object] = {}
    for index, task_id in enumerate(EXPECTED_TASKS):
        syntax_valid = index != 1
        case_results[task_id] = {
            "task_count": 1,
            "syntax_pass_count": int(syntax_valid),
            "syntax_pass_rate": float(syntax_valid),
            "rows": [
                {
                    "task_id": task_id,
                    "completion": f"# {task_id}",
                    "syntax_valid": syntax_valid,
                    "syntax_error": None if syntax_valid else "synthetic",
                    "required_substrings": {"return": syntax_valid},
                    "wall_seconds": 0.01,
                }
            ],
            "interpretation": "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION",
        }

    aggregate = repair._aggregate_case_results(case_results)
    assert aggregate["task_count"] == 3
    assert aggregate["syntax_pass_count"] == 2
    assert aggregate["syntax_pass_rate"] == 2 / 3
    rows = aggregate["rows"]
    assert isinstance(rows, list)
    assert [row["task_id"] for row in rows] == list(EXPECTED_TASKS)
    assert aggregate["interpretation"] == "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION"


def test_case_staged_workflow_has_exact_trigger_and_seven_json_uploads() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "github.event.issue.number == 162" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert (
        "github.event.comment.body == 'B012_RECOVER_RAW_CODE_CASE_STAGED "
        "qwen3.5-0.8b-control 34155931982 34231845282'"
    ) in workflow
    assert "runs-on: ubuntu-24.04" in workflow
    assert "timeout-minutes: 45" in workflow
    assert "cancel-in-progress: false" in workflow

    for stage in EXPECTED_STAGES:
        assert workflow.count(f"--stage {stage}") == 1

    upload_pin = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    assert workflow.count(upload_pin) == 7
    assert workflow.count("${{ runner.temp }}/b012-qwen-raw-code-results/*.json") == 7
    assert ".gguf" not in workflow
    assert ".safetensors" not in workflow
    assert "actions/download-artifact@" not in workflow
    assert "actions/cache@" not in workflow


def test_case_staged_script_preserves_execution_and_authority_boundaries() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    old_helper = RAW_CODE_HELPER.read_text(encoding="utf-8")

    assert 'CANDIDATE_ID = "qwen3.5-0.8b-control"' not in source
    assert "PRIOR_RUN_ID = 34155931982" not in source
    assert "TRIGGERING_INCIDENT_RUN_ID = 34231845282" in source
    assert source.count("download_candidate(") == 1
    assert source.count("convert_quantize(") == 1
    assert "run_raw_code_proxy(" in source
    assert "_stage_prefill" not in source
    assert "_stage_decode" not in source
    assert "llama-bench" not in source
    assert "B012_RAW_CODE_RECOVERY_FAILED_CLOSED" in source
    assert "candidate_admission_decision" in source
    assert "model_quality_verdict" in source
    assert "retry_authority_created" in source
    assert "external_dispatch_authority_created" in source
    assert "maximum_uncheckpointed_raw_code_cases" in source

    assert "def run_raw_code_proxy(" not in source
    assert "def run_raw_code_proxy(" in old_helper
