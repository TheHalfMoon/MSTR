from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / (
    "artifacts/results/equivalent/B012/failures/"
    "B012-mellum-4b-run-34064172421.json"
)
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_runner_shutdown_failure_is_preserved_without_quality_claim() -> None:
    evidence = _read_json(EVIDENCE)

    assert _sha256(EVIDENCE) == (
        "e5abc34f9d251951d4b38508fd0c6f67d8200282f564279a4c6fada65e354030"
    )
    assert evidence["task_id"] == "B012"
    assert evidence["candidate_id"] == "mellum-4b"
    assert evidence["run_id"] == 34064172421
    assert evidence["job_id"] == 101569918156
    assert evidence["canonical_main_at_start"] == (
        "f207ed9080fba1bb597a4091029dfd2a381eb346"
    )
    assert evidence["failure_classification"] == (
        "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RESULT"
    )
    assert evidence["workflow_conclusion"] == "failure"
    assert evidence["execution_step_conclusion"] == "cancelled"
    assert evidence["artifact_upload_step_conclusion"] == "skipped"
    assert evidence["durable_artifact_count"] == 0
    assert evidence["executor_authored_failure_json"] is False
    assert evidence["model_quality_verdict"] == "NONE"
    assert evidence["model_access_before_shutdown"] == "UNKNOWN_UNRECORDED"
    assert evidence["candidate_execution_completion"] == "NOT_PROVEN"
    assert evidence["training"] is False
    assert evidence["paid_model_api"] is False
    assert evidence["candidate_expansion"] is False
    assert evidence["retry_authority_created"] is False
    assert evidence["same_action_retry_performed_by_this_evidence"] is False


def test_binding_records_classification_without_authority_expansion() -> None:
    binding = _read_json(BINDING)
    recovery = binding["runner_shutdown_recovery"]
    boundary = binding["execution_boundary"]
    assert isinstance(recovery, dict)
    assert isinstance(boundary, dict)

    assert recovery["run_id"] == 34064172421
    assert recovery["job_id"] == 101569918156
    assert recovery["candidate_id"] == "mellum-4b"
    assert recovery["failure_classification"] == (
        "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RESULT"
    )
    assert recovery["failure_evidence_sha256"] == _sha256(EVIDENCE)
    assert recovery["model_quality_verdict"] == "NONE"
    assert recovery["model_access_before_shutdown"] == "UNKNOWN_UNRECORDED"
    assert recovery["durable_artifact_count"] == 0
    assert recovery["retry_authority_created"] is False

    for key in (
        "authority_transfer",
        "candidate_revision_or_file_expansion",
        "new_candidates",
        "training",
        "weight_changing_training",
        "paid_compute",
        "paid_model_api",
        "production_release",
    ):
        assert boundary[key] is False
