from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_qwen_raw_code_recovery_staged as staged  # noqa: E402

MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-recovery-staged-topology.json"
SCRIPT = COLAB / "mstr_b012_qwen_raw_code_recovery_staged.py"
WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-recovery-staged.yml"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_qwen_staged_repair_is_hash_bound_and_non_authorizing() -> None:
    manifest = _read_json(MANIFEST)
    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert manifest["candidate_id"] == "qwen3.5-0.8b-control"
    assert manifest["prior_qualification_run_id"] == 34155931982
    assert manifest["expected_q4_k_m_sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )
    assert manifest["expected_q4_k_m_size_bytes"] == 541903296
    assert manifest["staged_script_sha256"] == _sha256(SCRIPT)
    assert manifest["staged_workflow_sha256"] == _sha256(WORKFLOW)

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


def test_qwen_staged_topology_has_five_ordered_json_checkpoint_boundaries() -> None:
    manifest = _read_json(MANIFEST)
    topology = manifest["topology"]
    durability = manifest["durability_boundary"]
    assert isinstance(topology, dict)
    assert isinstance(durability, dict)

    assert staged.STAGES == ("init", "source", "quantize", "raw-code", "finalize")
    assert staged.PREDECESSORS == {
        "init": None,
        "source": "init",
        "quantize": "source",
        "raw-code": "quantize",
        "finalize": "raw-code",
    }
    assert topology["stages"] == list(staged.STAGES)
    assert topology["single_ephemeral_job"] is True
    assert topology["max_job_minutes"] == 45
    assert topology["durable_checkpoint_after_each_completed_stage"] is True
    assert topology["durable_checkpoint_format"] == "JSON_ONLY"
    assert topology["large_binary_artifact_uploads"] is False
    assert topology["large_binary_transfer_between_jobs"] is False
    assert topology["source_reacquisition_count_per_dispatch"] == 1
    assert topology["prefill_rerun"] is False
    assert topology["decode_rerun"] is False
    assert durability["init_checkpoint_precedes_model_access"] is True
    assert durability["quantize_checkpoint_records_exact_q4_identity_before_raw_code"] is True
    assert durability["stage_interrupted_before_its_upload_remains_not_proven"] is True


def test_qwen_staged_workflow_has_new_exact_dispatch_and_json_only_uploads() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "github.event.issue.number == 162" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert (
        "github.event.comment.body == 'B012_RECOVER_RAW_CODE_STAGED "
        "qwen3.5-0.8b-control 34155931982'"
    ) in workflow
    assert "timeout-minutes: 45" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "mstr_b012_qwen_raw_code_recovery_staged.py" in workflow
    upload_pin = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    assert workflow.count(upload_pin) == 5
    assert workflow.count("${{ runner.temp }}/b012-qwen-raw-code-results/*.json") == 5
    assert ".gguf" not in workflow
    assert ".safetensors" not in workflow
    assert "actions/download-artifact@" not in workflow
    assert "actions/cache@" not in workflow


def test_qwen_staged_script_preserves_exact_recovery_scope() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'CANDIDATE_ID = "qwen3.5-0.8b-control"' in source
    assert "PRIOR_RUN_ID = 34155931982" in source
    assert 'target="llama-quantize"' in source
    assert 'target="llama-cli"' in source
    assert "llama-bench" not in source
    assert "_stage_prefill" not in source
    assert "_stage_decode" not in source
    assert source.count("download_candidate(") == 1
    assert source.count("convert_quantize(") == 1
    assert source.count("run_raw_code_proxy(") == 1
    assert "B012_RAW_CODE_RECOVERY_FAILED_CLOSED" in source
    assert "retry_authority_created" in source
    assert "external_dispatch_authority_created" in source
    assert "EXACT_B010_FILE_REACQUISITION_IN_PROGRESS" in source
    assert "EXACT_Q4_REGENERATION_IN_PROGRESS" in source
    assert "RAW_CODE_EXECUTION_IN_PROGRESS" in source
    assert '"completed_stages": list(STAGES)' in source


def test_qwen_staged_checkpoint_is_json_only_and_non_authorizing(tmp_path: Path) -> None:
    state: dict[str, object] = {
        "task_id": "B012",
        "candidate_id": "qwen3.5-0.8b-control",
        "canonical_main_at_start": "a" * 40,
        "completed_stages": [],
        "last_completed_stage": None,
        "model_access_state": "NONE",
    }
    staged._complete_stage(
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
    assert checkpoint["model_access_state"] == "NONE"
    assert checkpoint["training"] is False
    assert checkpoint["paid_cost_usd"] == 0.0
    assert checkpoint["durable_binary_artifacts"] is False
    assert checkpoint["durable_output_format"] == "JSON_ONLY"


def test_qwen_staged_recovery_activation_is_preserved_after_case_checkpoint_supersession() -> None:
    manifest = _read_json(MANIFEST)
    binding = _read_json(BINDING)
    activation = binding["qwen_raw_code_recovery_staged_activation"]
    assert isinstance(activation, dict)

    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert ACTIVE_WORKFLOW.read_bytes() != WORKFLOW.read_bytes()
    assert (
        "B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982"
        in ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    )
    assert binding["status"] == "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"
    assert activation["repair_id"] == manifest["repair_id"]
    assert activation["candidate_id"] == "qwen3.5-0.8b-control"
    assert activation["prior_run_id"] == 34155931982
    assert activation["repair_manifest_sha256"] == _sha256(MANIFEST)
    assert activation["staged_script_sha256"] == _sha256(SCRIPT)
    assert activation["active_workflow_sha256"] == _sha256(WORKFLOW)
    assert activation["activation_base_main"] == "0cff2d57ab78c0189c8557f3e2ec59300bd8082d"
    assert activation["repair_package_postmerge_run_id"] == 34177394009
    assert activation["repair_package_postmerge_evidence_head"] == (
        "6e26a1bcaf844cd9a4ff100de54f116cdca77853"
    )
    assert activation["activation_is_separate_repository_change"] is True
    assert activation["retry_authority_created"] is False
    assert activation["external_dispatch_authority_created"] is False
    assert activation["candidate_expansion"] is False
    assert activation["revision_or_file_expansion"] is False
    assert activation["model_access"] == "NONE"
    assert activation["model_execution"] == "NONE"
    assert activation["training"] is False
    assert activation["weight_changing_training"] is False
    assert activation["paid_compute"] is False
    assert activation["paid_model_api"] is False
    assert activation["paid_cost_usd"] == 0.0
    assert activation["production_release"] is False
