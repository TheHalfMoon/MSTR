from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / "artifacts/authorities/B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION.json"
ENVELOPE = ROOT / "artifacts/manifests/B012-equivalent-qualification-execution-envelope.json"
B010 = ROOT / "artifacts/manifests/B010-new-candidate-weight-access.json"
B011 = ROOT / "artifacts/manifests/B011-acquired-candidates.json"
MELLUM_ARTIFACT = ROOT / "artifacts/manifests/B011-artifact-mellum-4b.json"
QWEN_ARTIFACT = ROOT / "artifacts/manifests/B011-artifact-qwen3.5-0.8b-control.json"
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
LOCK = ROOT / "artifacts/manifests/B012-executor-toolchain-lock.json"
RAW_CODE = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"
RUNTIME_PROFILE = ROOT / "configs/runtimes/llama-cpp-cpu.json"
T031_LOCK = ROOT / "artifacts/manifests/T031-executor-toolchain-lock.json"
T031_REPLAY_OVERLAY = ROOT / "artifacts/manifests/T031-t029-producer-replay-overlay.json"
TOOLCHAIN_HELPER = ROOT / "colab/mstr_executor_toolchain.py"
REPLAY_HELPER = ROOT / "colab/mstr_t031_replay.py"
T031_MEASURE = ROOT / "colab/mstr_t031_measure.py"
GOVERNANCE = ROOT / "colab/mstr_b012_governance.py"
SOURCE = ROOT / "colab/mstr_b012_source.py"
ARTIFACTS = ROOT / "colab/mstr_b012_artifacts.py"
RAW_EXECUTOR = ROOT / "colab/mstr_b012_raw_code.py"
EXECUTOR = ROOT / "colab/mstr_b012_execute.py"
WORKFLOW = ROOT / ".github/workflows/b012-qualify.yml"

CANDIDATES = ["mellum-4b", "qwen3.5-0.8b-control"]


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_binding_matches_canonical_authority_and_envelope() -> None:
    authority = _read_json(AUTHORITY)
    envelope = _read_json(ENVELOPE)
    binding = _read_json(BINDING)

    assert authority["status"] == "AUTHORIZED_CANONICAL"
    assert authority["authority_id"] == "B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION"
    assert authority["task_id"] == "B012"
    assert binding["status"] == "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"
    assert binding["task_id"] == "B012"
    assert binding["source_main"] == "603a6865fdbf5a5434565e870d73054c5b574f2a"
    assert binding["candidate_ids"] == CANDIDATES
    assert envelope["candidate_ids"] == CANDIDATES
    assert envelope["authority_id"] == authority["authority_id"]
    assert envelope["dispatch_state"] == "BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING"

    scope = authority["scope"]
    assert isinstance(scope, dict)
    assert scope["candidate_ids"] == CANDIDATES
    assert scope["new_candidate_access"] is False
    assert scope["training"] is False
    assert scope["weight_changing_training"] is False
    assert scope["paid_compute"] is False
    assert scope["paid_model_api"] is False
    assert scope["git_model_binaries"] is False
    assert scope["founder_machine_large_artifacts"] == 0

    prohibited = envelope["prohibited_operations"]
    assert isinstance(prohibited, list)
    assert "K2_OR_ANY_NEW_CANDIDATE" in prohibited
    assert "CANDIDATE_REVISION_OR_FILE_EXPANSION" in prohibited
    assert "WEIGHT_CHANGING_TRAINING" in prohibited
    assert "TRAINING" in prohibited
    assert "PAID_COMPUTE" in prohibited
    assert "PAID_MODEL_API" in prohibited
    assert "GIT_MODEL_BINARIES" in prohibited
    assert "FOUNDER_MACHINE_MODEL_BINARIES" in prohibited

    assert binding["authority_sha256"] == _sha256(AUTHORITY)
    assert binding["envelope_sha256"] == _sha256(ENVELOPE)
    assert binding["b010_sha256"] == _sha256(B010)
    assert binding["b011_sha256"] == _sha256(B011)
    assert binding["mellum_b011_artifact_sha256"] == _sha256(MELLUM_ARTIFACT)
    assert binding["qwen_b011_artifact_sha256"] == _sha256(QWEN_ARTIFACT)


def test_binding_hashes_every_execution_component() -> None:
    binding = _read_json(BINDING)
    expected = {
        LOCK: binding["toolchain_lock_sha256"],
        RAW_CODE: binding["raw_code_manifest_sha256"],
        RUNTIME_PROFILE: binding["runtime_profile_sha256"],
        T031_LOCK: binding["reused_t031_lock_sha256"],
        T031_REPLAY_OVERLAY: binding["reused_t031_replay_overlay_sha256"],
        TOOLCHAIN_HELPER: binding["toolchain_helper_sha256"],
        REPLAY_HELPER: binding["replay_helper_sha256"],
        T031_MEASURE: binding["reused_measurement_helper_sha256"],
        GOVERNANCE: binding["governance_script_sha256"],
        SOURCE: binding["source_script_sha256"],
        ARTIFACTS: binding["artifact_script_sha256"],
        RAW_EXECUTOR: binding["raw_code_script_sha256"],
        EXECUTOR: binding["executor_script_sha256"],
        WORKFLOW: binding["workflow_sha256"],
    }
    for path, digest in expected.items():
        assert isinstance(digest, str)
        assert _sha256(path) == digest


def test_lock_and_binding_preserve_zero_cost_no_transfer_boundary() -> None:
    lock = _read_json(LOCK)
    binding = _read_json(BINDING)
    envelope = _read_json(ENVELOPE)

    task = lock["task_binding"]
    reuse = lock["explicit_dependency_reuse"]
    ceiling = lock["resource_ceiling"]
    assert isinstance(task, dict)
    assert isinstance(reuse, dict)
    assert isinstance(ceiling, dict)
    assert task["candidate_ids"] == CANDIDATES
    assert reuse["source_task"] == "T031"
    assert reuse["authority_transfer"] is False
    assert reuse["package_count"] == 40
    assert ceiling["paid_cost_usd"] == 0.0
    assert ceiling["paid_compute"] is False
    assert ceiling["paid_model_api"] is False
    assert ceiling["founder_machine_model_binaries"] == 0
    assert ceiling["git_model_binaries"] == 0

    boundary = binding["execution_boundary"]
    assert isinstance(boundary, dict)
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
    assert boundary["git_model_binaries"] == 0
    assert boundary["founder_machine_model_binaries"] == 0
    assert boundary["paid_cost_usd"] == 0.0
    assert boundary["durable_outputs"] == ["JSON"]

    resource = envelope["resource_ceiling"]
    assert isinstance(resource, dict)
    assert resource["paid_cost_usd"] == 0.0
    assert resource["paid_compute"] is False
    assert resource["paid_model_api"] is False
    assert resource["aggregate_required_source_download_bytes"] == 9817996174


def test_issue_comment_dispatch_is_canonical_owner_scoped() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = _read_json(BINDING)

    assert "issue_comment:" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "\n  push:" not in workflow
    assert "github.event.issue.number == 162" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert "B012_RUN mellum-4b" in workflow
    assert "B012_RUN qwen3.5-0.8b-control" in workflow
    assert "ref: main" in workflow
    assert "persist-credentials: false" in workflow
    assert "group: b012-equivalent-qualification-single-candidate" in workflow
    assert "cancel-in-progress: false" in workflow
    assert 'python-version: "3.11.16"' in workflow

    dispatch = binding["dispatch_boundary"]
    assert isinstance(dispatch, dict)
    assert dispatch["surface"] == "ISSUE_COMMENT_CANONICAL_MAIN"
    assert dispatch["issue"] == 162
    assert dispatch["checkout_ref"] == "main"
    assert dispatch["owner"] == "TheHalfMoon"
    assert dispatch["owner_association"] == "OWNER"
    assert dispatch["max_parallel_candidates"] == 1
    assert dispatch["max_job_minutes"] == 120
    assert dispatch["canonicalization_required"] is True


def test_source_and_executor_keep_exact_candidate_and_failure_boundaries() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")
    raw = _read_json(RAW_CODE)

    assert "candidate outside B012 envelope" in source
    assert "B011 source is not ACQUIRED_VERIFIED" in source
    assert "B011/B012 upstream identity drift detected" in source
    assert "B010/B011 exact required-file set mismatch" in source
    assert "B012 candidate download-byte ceiling drift detected" in source
    assert 'https://huggingface.co/{upstream}/resolve/{revision}/{filename}' in source
    assert "allowed_hosts=allowed_hosts" in source

    assert 'choices=["mellum-4b", "qwen3.5-0.8b-control"]' in executor
    assert "candidate outside exact B012 authority" in executor
    assert '"candidate_admission_decision": "NOT_MADE_BY_B012_EXECUTOR"' in executor
    assert '"result_classification": "B012_EXECUTION_FAILED_CLOSED"' in executor
    assert '"paid_cost_usd": 0.0' in executor
    assert '"training": False' in executor
    assert "shutil.rmtree(workdir, ignore_errors=True)" in executor

    execution = raw["execution"]
    verification = raw["verification"]
    assert isinstance(execution, dict)
    assert isinstance(verification, dict)
    assert execution["network_model_calls"] == 0
    assert verification["score_is_observation_not_admission_gate"] is True
    tasks = raw["tasks"]
    assert isinstance(tasks, list)
    assert len(tasks) == 3


def test_resolution_evidence_is_no_model_and_non_authorizing() -> None:
    binding = _read_json(BINDING)
    evidence = binding["resolution_evidence"]
    reuse = binding["dependency_reuse"]
    assert isinstance(evidence, dict)
    assert isinstance(reuse, dict)
    assert evidence["run_id"] == 34037510185
    assert evidence["evidence_head"] == "c705528fb8a2790233b17cdd1721ad45b28f6316"
    assert evidence["artifact_id"] == 9990642177
    assert evidence["artifact_zip_sha256"] == (
        "12b88955e202d56ba2c4c2b2597433a269b6025c9b28560bd0feaf95b134d34a"
    )
    assert evidence["model_access"] == "NONE"
    assert evidence["training"] is False
    assert evidence["paid_cost_usd"] == 0.0
    assert reuse["source_task"] == "T031"
    assert reuse["package_identity_only"] is True
    assert reuse["authority_transfer"] is False
    assert binding["satisfies_pending_condition"] == (
        "SEPARATELY_REVIEWED_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING; "
        "DOES_NOT_EXPAND_B012_FOUNDER_AUTHORITY"
    )
