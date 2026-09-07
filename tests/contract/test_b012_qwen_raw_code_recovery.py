from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-runner-shutdown-recovery.json"
INCIDENT = (
    ROOT / "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-run-34155931982.json"
)
RECOVERY_INCIDENT = (
    ROOT / "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-raw-code-recovery-run-34169060075.json"
)
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
RUNNER = ROOT / "colab/mstr_b012_qwen_raw_code_recovery.py"
WORKFLOW_SPEC = ROOT / "configs/workflows/b012-qwen-raw-code-recovery.yml"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"

RECOVERY_INCIDENT_SHA256 = "3994421abe4d368746672f539edca2c509188147cadf9f1d6fd142f9ff9dc8ea"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_qwen_raw_code_recovery_is_activated_and_exactly_bound() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    assert manifest["status"] == "ACTIVATED_CANONICAL"
    assert manifest["candidate_id"] == "qwen3.5-0.8b-control"
    assert manifest["prior_run_id"] == 34155931982
    assert manifest["prior_stage05_artifact_id"] == 10031329744
    assert manifest["prior_stage05_artifact_digest"] == (
        "sha256:726e154a9e94c67eea4b0bdec5440912af6055e46cac9f95861872a044616fee"
    )
    assert manifest["prior_stage05_checkpoint_sha256"] == (
        "2141781456f54623e6b87c9e7528ea767f49062670fbb62b77d639b3ec3d1f88"
    )
    assert manifest["expected_q4_k_m_sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )
    assert manifest["expected_q4_k_m_size_bytes"] == 541903296
    assert manifest["recovery_script_sha256"] == _sha256(RUNNER)
    assert manifest["recovery_workflow_sha256"] == _sha256(WORKFLOW_SPEC)
    assert manifest["incident_evidence_sha256"] == _sha256(INCIDENT)
    assert ACTIVE_WORKFLOW.read_bytes() == WORKFLOW_SPEC.read_bytes()
    assert binding["qwen_raw_code_recovery_manifest_sha256"] == _sha256(MANIFEST)
    activation = binding["qwen_raw_code_recovery_activation"]
    assert activation["recovery_manifest_sha256"] == _sha256(MANIFEST)
    assert activation["recovery_script_sha256"] == _sha256(RUNNER)
    assert activation["active_workflow_sha256"] == _sha256(ACTIVE_WORKFLOW)
    assert activation["incident_evidence_sha256"] == _sha256(INCIDENT)
    assert activation["retry_authority_created"] is False
    assert activation["external_dispatch_authority_created"] is False
    assert activation["candidate_expansion"] is False
    assert activation["revision_or_file_expansion"] is False
    assert activation["model_access"] == "NONE"
    assert activation["training"] is False
    assert activation["paid_cost_usd"] == 0.0


def test_qwen_recovery_scope_skips_completed_benchmarks() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    scope = manifest["recovery_scope"]
    assert scope["reacquire_exact_b010_qwen_files"] is True
    assert scope["require_q4_k_m_identity_match_to_prior_stage03"] is True
    assert scope["rerun_prefill"] is False
    assert scope["rerun_decode"] is False
    assert scope["run_raw_code_proxy"] is True
    assert scope["candidate_expansion"] is False
    assert scope["revision_or_file_expansion"] is False
    assert scope["training"] is False
    assert scope["paid_compute"] is False
    assert scope["paid_model_api"] is False
    assert scope["git_model_binaries"] is False
    assert scope["founder_machine_model_binaries"] is False
    assert scope["durable_outputs"] == ["JSON"]


def test_qwen_recovery_runner_is_fail_closed_and_minimal() -> None:
    source = RUNNER.read_text(encoding="utf-8")
    assert 'CANDIDATE_ID = "qwen3.5-0.8b-control"' in source
    assert "PRIOR_RUN_ID = 34155931982" in source
    assert 'target="llama-quantize"' in source
    assert 'target="llama-cli"' in source
    assert "llama-bench" not in source
    assert "measure_set_bounded" not in source
    assert "_stage_prefill" not in source
    assert "_stage_decode" not in source
    assert "run_raw_code_proxy" in source
    assert "download_candidate" in source
    assert "convert_quantize" in source
    assert "B012_RAW_CODE_RECOVERY_FAILED_CLOSED" in source
    assert "observed_regenerated_q4_sha256" in source
    assert "observed_regenerated_q4_size_bytes" in source
    assert "ACTIVATED_CANONICAL" in source


def test_qwen_recovery_workflow_has_exact_dispatch_boundary() -> None:
    text = ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    assert text == WORKFLOW_SPEC.read_text(encoding="utf-8")
    assert "github.event.issue.number == 162" in text
    assert "github.event.comment.user.login == 'TheHalfMoon'" in text
    assert "github.event.comment.author_association == 'OWNER'" in text
    assert (
        "github.event.comment.body == 'B012_RECOVER_RAW_CODE qwen3.5-0.8b-control 34155931982'"
    ) in text
    assert "timeout-minutes: 45" in text
    assert "cancel-in-progress: false" in text
    assert "mstr_b012_qwen_raw_code_recovery.py" in text
    assert "upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in text
    assert ".gguf" not in text
    assert ".safetensors" not in text


def test_qwen_shutdown_incident_is_not_a_model_verdict_or_retry_grant() -> None:
    incident = json.loads(INCIDENT.read_text(encoding="utf-8"))
    assert incident["workflow_run_id"] == 34155931982
    assert incident["workflow_job_id"] == 101847640786
    assert incident["last_durable_stage"] == "decode"
    assert incident["interrupted_stage"] == "raw-code"
    assert incident["interrupted_step_conclusion"] == "cancelled"
    assert incident["durable_artifact_count"] == 5
    assert incident["q4_k_m_sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )
    assert incident["q4_identity_provenance"]["stage03_artifact_id"] == 10031142398
    assert incident["raw_code_result"] == "NONE"
    assert incident["candidate_admission_decision"] == "NONE"
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["retry_authority_created"] is False
    assert incident["external_dispatch_authority_created"] is False


def test_repeated_qwen_recovery_shutdown_is_preserved_without_quality_claim() -> None:
    incident = json.loads(RECOVERY_INCIDENT.read_text(encoding="utf-8"))
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    recovery = binding["qwen_raw_code_recovery_runner_shutdown"]

    assert _sha256(RECOVERY_INCIDENT) == RECOVERY_INCIDENT_SHA256
    assert incident["run_id"] == 34169060075
    assert incident["job_id"] == 101885732522
    assert incident["canonical_main_at_start"] == (
        "5e74e77c1fc86d4ebc7e64654f45bd18f565edd6"
    )
    assert incident["failure_classification"] == (
        "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RECOVERY_RESULT"
    )
    assert incident["workflow_conclusion"] == "failure"
    assert incident["execution_step_conclusion"] == "cancelled"
    assert incident["artifact_upload_step_conclusion"] == "skipped"
    assert incident["cleanup_step_conclusion"] == "skipped"
    assert incident["durable_artifact_count"] == 0
    assert incident["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["candidate_admission_decision"] == "NONE"
    assert incident["regenerated_q4_identity_before_shutdown"] == "UNKNOWN_UNRECORDED"
    assert incident["ephemeral_cleanup_completion"] == "NOT_PROVEN"
    assert incident["retry_authority_created"] is False
    assert incident["external_dispatch_authority_created"] is False
    assert incident["repeating_same_recovery_topology_authorized_by_this_evidence"] is False

    assert binding["status"] == "BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR"
    assert recovery["run_id"] == 34169060075
    assert recovery["failure_evidence_sha256"] == _sha256(RECOVERY_INCIDENT)
    assert recovery["model_quality_verdict"] == "NONE"
    assert recovery["repeating_same_recovery_topology_authorized_by_this_evidence"] is False
    assert recovery["retry_authority_created"] is False
    assert recovery["external_dispatch_authority_created"] is False
