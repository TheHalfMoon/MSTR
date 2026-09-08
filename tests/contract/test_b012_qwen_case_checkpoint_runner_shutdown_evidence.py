from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
INCIDENT = ROOT / (
    "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-raw-code-case-checkpoint-recovery-run-34265475666.json"
)
CHECKPOINT_DIR = ROOT / "artifacts/results/equivalent/B012/checkpoints/34265475666"
INIT = CHECKPOINT_DIR / (
    "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-01-init.json"
)
SOURCE = CHECKPOINT_DIR / (
    "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-02-source.json"
)
QUANTIZE = CHECKPOINT_DIR / (
    "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-03-quantize.json"
)
STATE = CHECKPOINT_DIR / "B012-qwen3.5-0.8b-control-raw-code-recovery-case-state.json"

INCIDENT_SHA256 = "e03d0030cb500a2fc97ec3a2f66c17b463028582643d9169c7be6994bc955152"
CHECKPOINT_SHA256 = {
    "init": "fabc44925fdb8243d5eeca856b6e9b5fd83db54c4dc9cca27967409382721fb4",
    "source": "38f9693bd55f77f8634ce01dec0e932e990790735399ade55f0a4230bdbf585e",
    "quantize": "ed15864153a8e4b26fffca5298dcbd80763e9c7edd0106845555b8325b079205",
}
STATE_SHA256 = "e5accce8487556a649db0c147a3c5876c0b31f8c1c0b334e48510f3680f58733"
FAILURE_CLASS = (
    "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN"
)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_case_checkpoint_runner_shutdown_incident_is_exact_and_non_verdict() -> None:
    incident = _read_json(INCIDENT)

    assert _sha256(INCIDENT) == INCIDENT_SHA256
    assert incident["task_id"] == "B012"
    assert incident["candidate_id"] == "qwen3.5-0.8b-control"
    assert incident["run_id"] == 34265475666
    assert incident["run_attempt"] == 1
    assert incident["job_id"] == 102193622602
    assert incident["workflow_head_sha"] == "145be15a32448d00fada0e2d9bf736f265c942a1"
    assert incident["canonical_main_at_start"] == "145be15a32448d00fada0e2d9bf736f265c942a1"
    assert incident["failure_classification"] == FAILURE_CLASS
    assert incident["durable_stages"] == ["init", "source", "quantize"]
    assert incident["interrupted_stage"] == "raw-code-python-clamp"
    assert incident["interrupted_stage_conclusion"] == "cancelled"
    assert incident["interrupted_stage_checkpoint_upload_conclusion"] == "skipped"
    assert incident["durable_raw_code_case_count"] == 0
    assert incident["durable_raw_code_cases"] == []
    assert incident["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert incident["candidate_admission_decision"] == "NONE"
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["candidate_execution_completion"] == "NOT_PROVEN"
    assert incident["ephemeral_cleanup_completion"] == "NOT_PROVEN"

    for key in (
        "retry_authority_created",
        "external_dispatch_authority_created",
        "same_case_checkpoint_topology_redispatch_authorized_by_this_evidence",
        "cross_run_resume_authority_created",
        "training",
        "paid_model_api",
        "candidate_expansion",
        "revision_or_file_expansion",
    ):
        assert incident[key] is False


def test_captured_checkpoint_json_is_byte_exact_and_complete_through_quantize() -> None:
    paths = {"init": INIT, "source": SOURCE, "quantize": QUANTIZE}
    for stage, path in paths.items():
        assert _sha256(path) == CHECKPOINT_SHA256[stage]

    init = _read_json(INIT)
    source = _read_json(SOURCE)
    quantize = _read_json(QUANTIZE)
    state = _read_json(STATE)

    assert init["completed_stages"] == ["init"]
    assert source["completed_stages"] == ["init", "source"]
    assert quantize["completed_stages"] == ["init", "source", "quantize"]
    assert source["checkpoint_payload"]["verified_file_count"] == 9
    assert source["checkpoint_payload"]["verified_download_bytes"] == 1769897109
    assert quantize["checkpoint_payload"]["matches_prior_stage03"] is True
    assert quantize["checkpoint_payload"]["q4_k_m_sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )
    assert quantize["checkpoint_payload"]["q4_k_m_size_bytes"] == 541903296

    assert _sha256(STATE) == STATE_SHA256
    assert state["completed_stages"] == ["init", "source", "quantize"]
    assert state["last_completed_stage"] == "quantize"
    assert state["raw_code_case_results"] == {}
    assert state["model_access_state"] == "EXACT_Q4_REGENERATED_VERIFIED"
    assert state["regenerated_q4"]["sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )


def test_incident_canonicalization_manifest_binds_all_captured_json() -> None:
    incident = _read_json(INCIDENT)
    canonicalization = incident["checkpoint_canonicalization"]
    assert isinstance(canonicalization, dict)

    assert canonicalization["required_checkpoint_json_count"] == 3
    assert canonicalization["all_required_checkpoint_json_captured"] is True
    assert canonicalization["terminal_case_state_captured"] is True
    assert canonicalization["artifact_zip_bodies_committed_to_git"] is False
    assert canonicalization["model_or_derived_binary_committed_to_git"] is False
    assert canonicalization["hash_verification"] == "PASS"

    checkpoints = canonicalization["required_checkpoints"]
    assert isinstance(checkpoints, list)
    assert [entry["stage"] for entry in checkpoints] == ["init", "source", "quantize"]
    assert [entry["sha256"] for entry in checkpoints] == [
        CHECKPOINT_SHA256["init"],
        CHECKPOINT_SHA256["source"],
        CHECKPOINT_SHA256["quantize"],
    ]
    assert canonicalization["terminal_case_state"]["sha256"] == STATE_SHA256


def test_executor_binding_reblocks_same_topology_and_hash_binds_incident() -> None:
    binding = _read_json(BINDING)
    shutdown = binding["qwen_raw_code_case_checkpoint_runner_shutdown"]
    assert isinstance(shutdown, dict)

    assert binding["status"] == "BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR"
    assert shutdown["run_id"] == 34265475666
    assert shutdown["job_id"] == 102193622602
    assert shutdown["candidate_id"] == "qwen3.5-0.8b-control"
    assert shutdown["failure_classification"] == FAILURE_CLASS
    assert shutdown["failure_evidence_sha256"] == _sha256(INCIDENT)
    assert shutdown["failure_evidence_sha256"] == INCIDENT_SHA256
    assert shutdown["durable_stages"] == ["init", "source", "quantize"]
    assert shutdown["durable_raw_code_case_count"] == 0
    assert shutdown["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert shutdown["model_quality_verdict"] == "NONE"
    assert shutdown["same_case_checkpoint_topology_redispatch_authorized_by_this_evidence"] is False
    assert shutdown["cross_run_resume_authority_created"] is False
    assert shutdown["retry_authority_created"] is False
    assert shutdown["external_dispatch_authority_created"] is False
