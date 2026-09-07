from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_EVIDENCE = ROOT / (
    "artifacts/results/equivalent/B012/failures/B012-mellum-4b-run-34064172421.json"
)
SECOND_EVIDENCE = ROOT / (
    "artifacts/results/equivalent/B012/failures/B012-mellum-4b-run-34068813113.json"
)
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"

FIRST_EVIDENCE_SHA256 = "e5abc34f9d251951d4b38508fd0c6f67d8200282f564279a4c6fada65e354030"
SECOND_EVIDENCE_SHA256 = "f20f8a1048392932d477c521329566341f0c1a13115caa3091bb27dfcb38df75"
FAILURE_CLASS = "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RESULT"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_non_verdict_shutdown(
    evidence: dict[str, object], *, run_id: int, job_id: int, canonical_main: str
) -> None:
    assert evidence["task_id"] == "B012"
    assert evidence["candidate_id"] == "mellum-4b"
    assert evidence["run_id"] == run_id
    assert evidence["job_id"] == job_id
    assert evidence["canonical_main_at_start"] == canonical_main
    assert evidence["failure_classification"] == FAILURE_CLASS
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


def test_first_runner_shutdown_failure_remains_preserved_without_quality_claim() -> None:
    evidence = _read_json(FIRST_EVIDENCE)

    assert _sha256(FIRST_EVIDENCE) == FIRST_EVIDENCE_SHA256
    _assert_non_verdict_shutdown(
        evidence,
        run_id=34064172421,
        job_id=101569918156,
        canonical_main="f207ed9080fba1bb597a4091029dfd2a381eb346",
    )


def test_second_runner_shutdown_failure_is_preserved_as_recurrence() -> None:
    evidence = _read_json(SECOND_EVIDENCE)

    assert _sha256(SECOND_EVIDENCE) == SECOND_EVIDENCE_SHA256
    _assert_non_verdict_shutdown(
        evidence,
        run_id=34068813113,
        job_id=101582272038,
        canonical_main="61bacde1ee21831080accc8a226433562a6aeaf9",
    )
    assert evidence["prior_runner_shutdown_run_id"] == 34064172421
    assert evidence["same_failure_class_as_prior_runner_shutdown"] is True
    assert evidence["same_single_job_execution_topology_as_prior_runner_shutdown"] is True
    assert evidence["repeating_same_topology_authorized_by_this_evidence"] is False


def test_binding_records_recurrence_without_authority_expansion() -> None:
    binding = _read_json(BINDING)
    first = binding["runner_shutdown_recovery"]
    second = binding["repeated_runner_shutdown_recovery"]
    boundary = binding["execution_boundary"]
    assert isinstance(first, dict)
    assert isinstance(second, dict)
    assert isinstance(boundary, dict)

    assert first["run_id"] == 34064172421
    assert first["job_id"] == 101569918156
    assert first["failure_evidence_sha256"] == _sha256(FIRST_EVIDENCE)
    assert first["retry_authority_created"] is False

    assert second["run_id"] == 34068813113
    assert second["job_id"] == 101582272038
    assert second["candidate_id"] == "mellum-4b"
    assert second["failure_classification"] == FAILURE_CLASS
    assert second["failure_evidence_sha256"] == _sha256(SECOND_EVIDENCE)
    assert second["prior_runner_shutdown_run_id"] == 34064172421
    assert second["same_failure_class_recurred"] is True
    assert second["same_single_job_execution_topology"] is True
    assert second["repeating_same_topology_authorized_by_this_evidence"] is False
    assert second["model_quality_verdict"] == "NONE"
    assert second["model_access_before_shutdown"] == "UNKNOWN_UNRECORDED"
    assert second["durable_artifact_count"] == 0
    assert second["retry_authority_created"] is False

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


def test_binding_blocks_same_topology_until_separately_reviewed_repair() -> None:
    binding = _read_json(BINDING)

    assert binding["status"] == "BLOCKED_PENDING_RUNNER_SHUTDOWN_TOPOLOGY_REPAIR"
    second = binding["repeated_runner_shutdown_recovery"]
    assert isinstance(second, dict)
    assert second["repeating_same_topology_authorized_by_this_evidence"] is False
