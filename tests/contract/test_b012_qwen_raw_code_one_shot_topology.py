from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

import mstr_b012_raw_code_one_shot as one_shot  # noqa: E402

MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-one-shot-topology-repair.json"
RAW_CODE = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"
SHARED_HELPER = ROOT / "colab/mstr_b012_raw_code.py"
ONE_SHOT_HELPER = ROOT / "colab/mstr_b012_raw_code_one_shot.py"
CASE_CHECKPOINT = ROOT / "colab/mstr_b012_qwen_raw_code_recovery_case_checkpoint.py"
WRAPPER = ROOT / "colab/mstr_b012_qwen_raw_code_one_shot.py"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_one_shot_repair_is_inert_hash_bound_and_non_authorizing() -> None:
    manifest = _read_json(MANIFEST)
    assert manifest["schema_version"] == (
        "mstr.b012-qwen-raw-code-one-shot-topology-repair.v1"
    )
    assert manifest["repair_id"] == "B012_QWEN_RAW_CODE_ONE_SHOT_MODE_REPAIR_2026_09_08"
    assert manifest["task_id"] == "B012"
    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert manifest["base_main"] == "9ff1680c21be366f11133a4ba2e68ebe0fc1e53b"
    assert manifest["candidate_id"] == "qwen3.5-0.8b-control"
    assert manifest["prior_qualification_run_id"] == 34155931982

    trigger = manifest["triggering_incident"]
    assert isinstance(trigger, dict)
    assert trigger["run_id"] == 34265475666
    assert trigger["canonical_incident_merge_commit"] == (
        "9ff1680c21be366f11133a4ba2e68ebe0fc1e53b"
    )
    assert trigger["canonical_incident_postmerge_run_id"] == 34274596048
    assert trigger["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert trigger["model_quality_verdict"] == "NONE"
    assert trigger["candidate_admission_decision"] == "NONE"

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
        "cross_run_resume_authority_created",
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


def test_one_shot_repair_component_hashes_preserve_canonical_surfaces() -> None:
    manifest = _read_json(MANIFEST)
    components = manifest["components"]
    assert isinstance(components, dict)
    assert components["raw_code_manifest_sha256"] == _sha256(RAW_CODE)
    assert components["canonical_shared_raw_code_helper_sha256"] == _sha256(SHARED_HELPER)
    assert components["case_checkpoint_script_sha256"] == _sha256(CASE_CHECKPOINT)
    assert components["one_shot_raw_code_helper_sha256"] == _sha256(ONE_SHOT_HELPER)
    assert components["one_shot_wrapper_sha256"] == _sha256(WRAPPER)
    assert components["active_workflow_at_repair_base_sha256"] == _sha256(ACTIVE_WORKFLOW)

    assert _sha256(SHARED_HELPER) == (
        "bd6d34afd8af60497a4971bb7245fc359c4132bad3772be212b6848aa73060d8"
    )
    assert _sha256(CASE_CHECKPOINT) == (
        "c6cb947bd84101b572e4bb8140a393e7dc067c858172339758031f855c6c24a3"
    )
    assert _sha256(ACTIVE_WORKFLOW) == (
        "f15941577213c5e96a1ebb3993989693628eae5f2e28620f90e03110d303d127"
    )


def test_repair_preserves_frozen_raw_code_semantics() -> None:
    manifest = _read_json(MANIFEST)
    semantic = manifest["semantic_preservation"]
    topology = manifest["topology"]
    raw = _read_json(RAW_CODE)
    execution = raw["execution"]
    tasks = raw["tasks"]
    assert isinstance(semantic, dict)
    assert isinstance(topology, dict)
    assert isinstance(execution, dict)
    assert isinstance(tasks, list)

    assert [task["id"] for task in tasks if isinstance(task, dict)] == [
        "python-clamp",
        "python-dedupe",
        "python-safe-divide",
    ]
    assert execution == {
        "runtime": "llama.cpp-llama-cli-cpu",
        "context_tokens": 2048,
        "generated_tokens": 96,
        "threads": 2,
        "gpu_layers": 0,
        "temperature": 0.0,
        "seed": 42,
        "network_model_calls": 0,
    }
    for key in (
        "raw_code_manifest_unchanged",
        "raw_code_case_set_unchanged",
        "raw_code_case_order_unchanged",
        "raw_code_prompts_unchanged",
        "raw_code_sampling_unchanged",
        "runtime_revision_unchanged",
        "canonical_shared_raw_code_helper_unchanged",
        "case_checkpoint_topology_reused",
        "candidate_admission_not_decided_by_recovery",
        "score_is_observation_not_admission_gate",
    ):
        assert semantic[key] is True
    assert topology["raw_code_case_order"] == [
        "python-clamp",
        "python-dedupe",
        "python-safe-divide",
    ]
    assert topology["one_shot_raw_completion"] is True
    assert topology["explicit_conversation_disable"] is True
    assert topology["maximum_uncheckpointed_raw_code_cases"] == 1
    assert topology["durable_checkpoint_format"] == "JSON_ONLY"


def test_only_isolated_helper_forces_one_shot_mode() -> None:
    shared = SHARED_HELPER.read_text(encoding="utf-8")
    isolated = ONE_SHOT_HELPER.read_text(encoding="utf-8")
    assert "--no-conversation" not in shared
    assert isolated.count('"--no-conversation"') == 1
    assert isolated.count('"--no-display-prompt"') == 1
    assert isolated.count('"--simple-io"') == 1


def test_one_shot_helper_passes_exact_frozen_runtime_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = _read_json(RAW_CODE)
    tasks = raw["tasks"]
    assert isinstance(tasks, list)
    assert isinstance(tasks[0], dict)
    manifest = {"execution": raw["execution"], "tasks": [tasks[0]]}
    observed: dict[str, object] = {}

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        observed["argv"] = list(argv)
        observed["kwargs"] = dict(kwargs)
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout="    return value\n",
            stderr="",
        )

    monkeypatch.setattr(one_shot.subprocess, "run", fake_run)
    monkeypatch.setattr(one_shot, "sanitized_runtime_environment", lambda: {})
    result = one_shot.run_raw_code_proxy(
        executable=Path("/tmp/llama-cli"),
        model=Path("/tmp/qwen-q4.gguf"),
        manifest=manifest,
    )

    prompt = tasks[0]["prompt"]
    assert observed["argv"] == [
        "/tmp/llama-cli",
        "-m",
        "/tmp/qwen-q4.gguf",
        "-p",
        prompt,
        "-n",
        "96",
        "-c",
        "2048",
        "-t",
        "2",
        "-ngl",
        "0",
        "--temp",
        "0.0",
        "--seed",
        "42",
        "--no-conversation",
        "--no-display-prompt",
        "--simple-io",
    ]
    kwargs = observed["kwargs"]
    assert isinstance(kwargs, dict)
    assert kwargs["timeout"] == 600
    assert kwargs["check"] is False
    assert result["task_count"] == 1
    assert result["syntax_pass_count"] == 1
    assert result["syntax_pass_rate"] == 1.0
    assert result["interpretation"] == "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION"


def test_wrapper_binds_isolated_helper_only_after_canonical_activation() -> None:
    wrapper = WRAPPER.read_text(encoding="utf-8")
    assert "import mstr_b012_raw_code_one_shot as one_shot_raw_code" in wrapper
    assert "one_shot_raw_code_helper_sha256" in wrapper
    assert "require_file_sha256(repo_root / ONE_SHOT_HELPER_PATH" in wrapper
    assert (
        "case_checkpoint.run_raw_code_proxy = one_shot_raw_code.run_raw_code_proxy" in wrapper
    )
    assert 'ACTIVATION_KEY = "qwen_raw_code_one_shot_activation"' in wrapper
    assert "is not canonically activated" in wrapper


def test_repair_does_not_activate_dispatch_surface() -> None:
    manifest = _read_json(MANIFEST)
    activation = manifest["activation"]
    assert isinstance(activation, dict)
    assert activation["separate_activation_pr_required"] is True
    assert activation["active_workflow_materialized"] is False
    assert activation["package_performs_model_access"] is False
    assert activation["package_performs_model_execution"] is False

    workflow = ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    assert (
        "B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982" in workflow
    )
    assert "B012_RECOVER_RAW_CODE_ONE_SHOT" not in workflow
    assert "mstr_b012_qwen_raw_code_one_shot.py" not in workflow
