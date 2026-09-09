import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPAIR = ROOT / "artifacts/manifests/B012-qwen-raw-code-completion-runtime-repair.json"
OLD_MANIFEST = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"
NEW_MANIFEST = ROOT / "benchmarks/manifests/B012-raw-code-proxy-completion-runtime.json"
OLD_HELPER = ROOT / "colab/mstr_b012_raw_code_one_shot.py"
NEW_HELPER = ROOT / "colab/mstr_b012_raw_code_completion.py"
WRAPPER = ROOT / "colab/mstr_b012_qwen_raw_code_completion.py"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"
INACTIVE_WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-completion-recovery.yml"


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_repair_is_inactive_and_authority_contained() -> None:
    repair = _read_json(REPAIR)
    assert repair["schema_version"] == "mstr.b012-qwen-raw-code-completion-runtime-repair.v1"
    assert repair["task_id"] == "B012"
    assert repair["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert repair["candidate_id"] == "qwen3.5-0.8b-control"
    assert repair["prior_qualification_run_id"] == 34155931982

    incident = repair["triggering_incident"]
    assert isinstance(incident, dict)
    assert incident["run_id"] == 34288154926
    assert incident["failure_classification"] == (
        "B012_EXECUTOR_RUNTIME_CLI_INCOMPATIBILITY_RAW_CODE_UNEXECUTED"
    )
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["candidate_admission_decision"] == "NONE"
    assert incident["candidate_execution_completion"] == "NOT_PROVEN"

    boundary = repair["activation_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["activation_required"] is True
    assert boundary["activation_is_separate_repository_change"] is True
    assert boundary["repair_pr_must_not_modify_active_workflow"] is True
    assert boundary["repair_pr_must_not_modify_executor_binding"] is True
    assert boundary["repair_pr_must_not_execute_model"] is True
    for key in (
        "retry_authority_created",
        "external_dispatch_authority_created",
        "cross_run_resume_authority_created",
        "candidate_expansion",
        "revision_or_file_expansion",
        "training",
        "weight_changing_training",
        "paid_compute",
        "paid_model_api",
        "production_release",
    ):
        assert boundary[key] is False, key
    assert boundary["paid_cost_usd"] == 0.0


def test_completion_manifest_preserves_frozen_raw_code_contract() -> None:
    old = _read_json(OLD_MANIFEST)
    new = _read_json(NEW_MANIFEST)

    assert new["schema_version"] == old["schema_version"]
    assert new["task_id"] == old["task_id"] == "B012"
    assert new["purpose"] == old["purpose"]
    assert new["verification"] == old["verification"]
    assert new["tasks"] == old["tasks"]

    old_execution = dict(old["execution"])
    new_execution = dict(new["execution"])
    assert old_execution.pop("runtime") == "llama.cpp-llama-cli-cpu"
    assert new_execution.pop("runtime") == "llama.cpp-llama-completion-cpu"
    assert new_execution == old_execution

    migration = new["runtime_migration"]
    assert isinstance(migration, dict)
    assert migration["runtime_commit"] == "3173a56471c1753650cd806694145ffd6dcace67"
    assert migration["parser_example"] == "LLAMA_EXAMPLE_COMPLETION"
    assert migration["conversation_mode"] == "EXPLICITLY_DISABLED_WITH_--no-conversation"
    assert migration["prompt_semantics"] == "RAW_PROMPT_TO_COMPLETION_PATH"
    assert migration["completion_capture"] == "STDOUT_WITH_PROMPT_DISPLAY_DISABLED"


def test_completion_helper_preserves_explicit_raw_completion_flags() -> None:
    old = OLD_HELPER.read_text(encoding="utf-8")
    new = NEW_HELPER.read_text(encoding="utf-8")

    for flag in ("--no-conversation", "--no-display-prompt", "--simple-io"):
        assert new.count(flag) == 1
        assert old.count(flag) == 1
    assert "llama-completion raw-code execution failed" in new
    assert "llama-cli raw-code execution failed" in old


def test_qwen_wrapper_builds_completion_target_but_requires_future_activation() -> None:
    wrapper = WRAPPER.read_text(encoding="utf-8")
    assert 'target="llama-completion"' in wrapper
    assert 'tools / "llama-completion"' in wrapper
    assert '"runtime_parser_example": "LLAMA_EXAMPLE_COMPLETION"' in wrapper
    assert 'ACTIVATION_KEY = "qwen_raw_code_completion_activation"' in wrapper
    expected_manifest_binding = (
        'COMPLETION_MANIFEST_PATH = '
        'Path("benchmarks/manifests/B012-raw-code-proxy-completion-runtime.json")'
    )
    assert expected_manifest_binding in wrapper
    assert "case_checkpoint.RAW_CODE_PATH = COMPLETION_MANIFEST_PATH" in wrapper
    assert 'activation.get("completion_raw_code_manifest_sha256")' in wrapper
    assert 'repair.get("status") != "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"' in wrapper
    assert 'activation.get("retry_authority_created") is not False' in wrapper
    assert 'activation.get("external_dispatch_authority_created") is not False' in wrapper
    assert 'activation.get("cross_run_resume_authority_created") is not False' in wrapper


def test_repair_keeps_active_workflow_unchanged_and_template_inactive() -> None:
    active = ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    inactive = INACTIVE_WORKFLOW.read_text(encoding="utf-8")

    assert "B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982" in active
    assert "colab/mstr_b012_qwen_raw_code_one_shot.py" in active
    assert "B012_RECOVER_RAW_CODE_COMPLETION qwen3.5-0.8b-control 34288154926" in inactive
    assert "colab/mstr_b012_qwen_raw_code_completion.py" in inactive
    assert INACTIVE_WORKFLOW.parts[-3] == "configs"
