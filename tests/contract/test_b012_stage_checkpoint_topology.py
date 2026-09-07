from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_staged as staged  # noqa: E402

BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
REPAIR = ROOT / "artifacts/manifests/B012-runner-shutdown-topology-repair.json"
CANDIDATE_WORKFLOW = ROOT / "configs/workflows/b012-qualify-staged.yml"
STAGED_EXECUTOR = COLAB / "mstr_b012_staged.py"

EXPECTED_STAGES = (
    "init",
    "source",
    "quantize",
    "prefill",
    "decode",
    "raw-code",
    "finalize",
)


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_repair_package_is_hash_bound_after_separate_canonical_activation() -> None:
    binding = _read_json(BINDING)
    repair = _read_json(REPAIR)

    assert binding["status"] == "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"
    assert binding["runner_shutdown_topology_repair_manifest_sha256"] == _sha256(REPAIR)
    assert binding["workflow_sha256"] == _sha256(
        ROOT / ".github/workflows/b012-qualify.yml"
    )

    assert repair["activation_state"] == "ACTIVATED_BY_SEPARATE_CANONICAL_BINDING_CHANGE"
    assert repair["activation_target"] == ".github/workflows/b012-qualify.yml"
    assert repair["candidate_workflow_path"] == "configs/workflows/b012-qualify-staged.yml"
    assert repair["candidate_workflow_sha256"] == _sha256(CANDIDATE_WORKFLOW)
    assert repair["staged_executor_path"] == "colab/mstr_b012_staged.py"
    assert repair["staged_executor_sha256"] == _sha256(STAGED_EXECUTOR)
    assert repair["model_execution_performed_by_repair"] is False
    assert repair["model_access_performed_by_repair"] is False
    assert repair["training_performed_by_repair"] is False
    assert repair["paid_cost_usd"] == 0.0

    recovery = repair["recovery_semantics"]
    assert isinstance(recovery, dict)
    assert recovery["same_monolithic_topology_repetition"] is False
    assert recovery["repair_is_new_repository_evidence"] is True
    assert recovery["retry_same_failed_action_without_new_evidence"] is False
    assert recovery["retry_authority_created"] is False
    assert recovery["external_dispatch_authority_created"] is False
    assert recovery["activation_requires_exact_main_task_eligibility"] is True
    assert (
        recovery["activation_requires_reverification_of_canonical_external_effect_authority"]
        is True
    )
    assert recovery["activation_requires_separate_review_and_merge"] is True

    activation = binding["runner_shutdown_topology_activation"]
    assert isinstance(activation, dict)
    assert activation["repair_manifest_sha256"] == _sha256(REPAIR)
    assert activation["staged_executor_sha256"] == _sha256(STAGED_EXECUTOR)
    assert activation["active_workflow_sha256"] == _sha256(
        ROOT / ".github/workflows/b012-qualify.yml"
    )
    assert activation["activation_is_separate_repository_change"] is True
    assert activation["retry_authority_created"] is False
    assert activation["external_dispatch_authority_created"] is False


def test_candidate_workflow_uses_seven_ordered_stages_and_json_only_uploads() -> None:
    workflow = CANDIDATE_WORKFLOW.read_text(encoding="utf-8")
    repair = _read_json(REPAIR)

    assert repair["candidate_workflow_sha256"] == _sha256(CANDIDATE_WORKFLOW)
    assert "runs-on: ubuntu-24.04" in workflow
    assert "timeout-minutes: 120" in workflow
    assert "group: b012-equivalent-qualification-single-candidate" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "\n  push:" not in workflow
    assert "actions/cache@" not in workflow
    assert "actions/download-artifact@" not in workflow
    assert "mstr_b012_execute.py" not in workflow

    for stage in EXPECTED_STAGES:
        assert workflow.count(f"--stage {stage}") == 1

    upload_pin = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
    assert workflow.count(upload_pin) == 7
    assert workflow.count("${{ runner.temp }}/b012-results/*.json") == 7
    assert ".gguf" not in workflow
    assert ".safetensors" not in workflow
    upload_paths = "\n".join(
        line for line in workflow.splitlines() if line.lstrip().startswith("path:")
    )
    assert "b012-work" not in upload_paths


def test_stage_transition_contract_is_linear_and_source_is_not_reacquired_twice() -> None:
    assert staged.STAGES == EXPECTED_STAGES
    assert staged.PREDECESSORS == {
        "init": None,
        "source": "init",
        "quantize": "source",
        "prefill": "quantize",
        "decode": "prefill",
        "raw-code": "decode",
        "finalize": "raw-code",
    }

    source = STAGED_EXECUTOR.read_text(encoding="utf-8")
    assert source.count("download_candidate(") == 1
    assert source.count("convert_quantize(") == 1
    assert 'arm="prefill_8k"' in source
    assert 'arm="isolated_decode_128"' in source
    assert 'state["runtime_benchmark_budget"] = runtime_budget_observation' in source
    assert 'benchmark_started = observation.get("benchmark_started_monotonic")' in source
    assert "shared_across_prefill_and_decode_processes" in source


def test_repair_preserves_exact_resource_authority_and_benchmark_boundaries() -> None:
    repair = _read_json(REPAIR)

    topology = repair["topology"]
    benchmark = repair["benchmark_semantics"]
    resource = repair["resource_boundary"]
    authority = repair["authority_boundary"]
    assert isinstance(topology, dict)
    assert isinstance(benchmark, dict)
    assert isinstance(resource, dict)
    assert isinstance(authority, dict)

    assert topology["single_ephemeral_job"] is True
    assert topology["source_reacquisition_count_per_candidate_run"] == 1
    assert topology["duplicate_source_downloads_introduced"] is False
    assert topology["large_binary_transfer_between_jobs"] is False
    assert topology["large_binary_artifact_uploads"] is False
    assert topology["durable_checkpoint_after_each_completed_stage"] is True
    assert topology["durable_checkpoint_format"] == "JSON_ONLY"
    assert topology["stages"] == list(EXPECTED_STAGES)

    assert benchmark == {
        "authorized_job_ceiling_seconds": 7200,
        "benchmark_wall_budget_seconds": 4800,
        "decode_tokens": 128,
        "measured_repetitions": 3,
        "modified_by_repair": False,
        "per_invocation_timeout_seconds": 900,
        "prefill_decode_share_one_monotonic_budget_clock": True,
        "prompt_tokens": 8192,
        "reserved_non_benchmark_seconds": 2400,
        "threads": 2,
        "warmups_excluded": 1,
    }

    assert resource["aggregate_required_source_download_bytes"] == 9817996174
    assert resource["resource_ceiling_modified"] is False
    assert resource["paid_cost_usd"] == 0.0
    assert resource["paid_compute"] is False
    assert resource["paid_model_api"] is False
    assert resource["git_model_binaries"] == 0
    assert resource["founder_machine_model_binaries"] == 0

    assert authority["candidate_ids"] == ["mellum-4b", "qwen3.5-0.8b-control"]
    for key in (
        "candidate_revision_or_file_expansion",
        "new_candidates",
        "training",
        "weight_changing_training",
        "production_release",
        "authority_scope_modified",
        "authority_transfer",
    ):
        assert authority[key] is False


def test_checkpoint_serialization_is_json_only_and_non_authorizing(tmp_path: Path) -> None:
    state: dict[str, object] = {
        "task_id": "B012",
        "candidate_id": "mellum-4b",
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
    checkpoint = _read_json(tmp_path / "B012-mellum-4b-checkpoint-01-init.json")
    assert checkpoint["schema_version"] == "mstr.b012-stage-checkpoint.v1"
    assert checkpoint["stage"] == "init"
    assert checkpoint["completed_stages"] == ["init"]
    assert checkpoint["durable_output_format"] == "JSON_ONLY"
    assert checkpoint["durable_binary_artifacts"] is False
    assert checkpoint["training"] is False
    assert checkpoint["paid_cost_usd"] == 0.0


def test_failure_evidence_preserves_last_completed_checkpoint(tmp_path: Path) -> None:
    state = {
        "schema_version": "mstr.b012-stage-state.v1",
        "task_id": "B012",
        "candidate_id": "mellum-4b",
        "canonical_main_at_start": "b" * 40,
        "started_utc": "2026-09-07T00:00:00Z",
        "completed_stages": ["init", "source", "quantize"],
        "last_completed_stage": "quantize",
        "model_access_state": "EXACT_B010_FILES_REACQUIRED_VERIFIED",
        "producer_replay": {"synthetic": True},
    }
    staged._write(staged._state_path(tmp_path, "mellum-4b"), state)
    staged._write_failure(
        output_dir=tmp_path,
        candidate="mellum-4b",
        stage="prefill",
        exc=staged.ExecutionError("synthetic failure"),
    )
    failure = _read_json(tmp_path / "B012-mellum-4b-failure.json")
    assert failure["result_classification"] == "B012_EXECUTION_FAILED_CLOSED"
    assert failure["execution_stage"] == "STAGED_PREFILL"
    assert failure["completed_stages"] == ["init", "source", "quantize"]
    assert failure["last_durable_checkpoint_stage"] == "quantize"
    assert failure["model_access_state"] == "EXACT_B010_FILES_REACQUIRED_VERIFIED"
    assert failure["training"] is False
    assert failure["paid_cost_usd"] == 0.0
