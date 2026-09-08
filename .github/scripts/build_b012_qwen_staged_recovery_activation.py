#!/usr/bin/env python3
"""Build the repository-only B012 staged Qwen recovery activation atomically."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = "0cff2d57ab78c0189c8557f3e2ec59300bd8082d"
TARGET = "fix/b012-qwen-staged-recovery-activation"
POSTMERGE_RUN_ID = 34177394009
POSTMERGE_EVIDENCE_HEAD = "6e26a1bcaf844cd9a4ff100de54f116cdca77853"
REPAIR_ID = "B012_QWEN_RAW_CODE_STAGED_DURABILITY_REPAIR_2026_09_08"
CANDIDATE = "qwen3.5-0.8b-control"
PRIOR_RUN_ID = 34155931982

ROOT = Path.cwd()
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"
STAGED_WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-recovery-staged.yml"
STAGED_SCRIPT = ROOT / "colab/mstr_b012_qwen_raw_code_recovery_staged.py"
REPAIR_MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-recovery-staged-topology.json"
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B012-qwen-staged-recovery-activation.md"

STATUS_BLOCKED = "BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR"
STATUS_ACTIVE = "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"

STATUS_TESTS = [
    ROOT / "tests/contract/test_b012_executor_binding.py",
    ROOT / "tests/contract/test_b012_qwen_raw_code_recovery.py",
    ROOT / "tests/contract/test_b012_runner_shutdown_evidence.py",
    ROOT / "tests/contract/test_b012_stage_checkpoint_topology.py",
]
STAGED_TEST = ROOT / "tests/contract/test_b012_qwen_staged_recovery_topology.py"

ALLOWED = {
    ".github/workflows/b012-qwen-raw-code-recovery.yml",
    "artifacts/manifests/B012-executor-toolchain-binding.json",
    "artifacts/manifests/B012-qwen-raw-code-recovery-staged-topology.json",
    "evidence/mstr-000b/B012-qwen-staged-recovery-activation.md",
    "tests/contract/test_b012_executor_binding.py",
    "tests/contract/test_b012_qwen_raw_code_recovery.py",
    "tests/contract/test_b012_qwen_staged_recovery_topology.py",
    "tests/contract/test_b012_runner_shutdown_evidence.py",
    "tests/contract/test_b012_stage_checkpoint_topology.py",
}


def run(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        text=True,
        capture_output=capture,
    )


def output(*args: str) -> str:
    return run(*args, capture=True).stdout.strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, object]) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def replace_required(path: Path, old: str, new: str, *, minimum: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count < minimum:
        raise RuntimeError(f"required text not found in {path}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def guard_exact_base() -> None:
    run("git", "fetch", "origin", "main", TARGET, "--quiet")
    if output("git", "rev-parse", "origin/main") != BASE:
        raise RuntimeError("canonical main moved before activation build")
    if output("git", "rev-parse", f"origin/{TARGET}") != BASE:
        raise RuntimeError("target activation branch is not the exact untouched base")


def assert_exact_main_b012_eligibility() -> None:
    run("python", "-m", "pip", "install", "-e", ".[dev]")
    result = run("python", "-m", "mstr_qualify", "task", "eligible", "B012", capture=True)
    data = json.loads(result.stdout)
    assert data["task_id"] == "B012"
    assert data["canonical_main"] == BASE
    assert data["eligible"] is True
    assert data["authority_result"]["satisfied"] is True
    assert data["state_consistency_result"]["observed_state"] == "PENDING"
    assert data["supersession_result"]["superseded"] is False
    assert all(item["satisfied"] for item in data["prerequisite_results"])


def materialize_activation() -> None:
    shutil.copyfile(STAGED_WORKFLOW, ACTIVE_WORKFLOW)

    repair = load_json(REPAIR_MANIFEST)
    assert repair["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"
    assert repair["repair_id"] == REPAIR_ID
    assert repair["candidate_id"] == CANDIDATE
    assert repair["prior_qualification_run_id"] == PRIOR_RUN_ID
    activation = repair["activation"]
    assert isinstance(activation, dict)
    activation.update(
        {
            "activation_base_main": BASE,
            "repair_package_merge_commit": BASE,
            "repair_package_postmerge_run_id": POSTMERGE_RUN_ID,
            "repair_package_postmerge_evidence_head": POSTMERGE_EVIDENCE_HEAD,
            "active_workflow_materialized": True,
            "activation_repository_change_only": True,
            "activation_model_access": "NONE",
            "activation_model_execution": "NONE",
            "activation_paid_cost_usd": 0.0,
        }
    )
    write_json(REPAIR_MANIFEST, repair)

    repair_hash = sha256(REPAIR_MANIFEST)
    script_hash = sha256(STAGED_SCRIPT)
    workflow_hash = sha256(ACTIVE_WORKFLOW)
    assert workflow_hash == sha256(STAGED_WORKFLOW)
    assert script_hash == repair["staged_script_sha256"]
    assert workflow_hash == repair["staged_workflow_sha256"]

    binding = load_json(BINDING)
    assert binding["status"] == STATUS_BLOCKED
    incident = binding["qwen_raw_code_recovery_runner_shutdown"]
    assert isinstance(incident, dict)
    assert incident["run_id"] == 34169060075
    assert incident["model_quality_verdict"] == "NONE"
    assert incident["retry_authority_created"] is False
    assert incident["external_dispatch_authority_created"] is False

    binding["status"] = STATUS_ACTIVE
    binding["qwen_raw_code_recovery_staged_activation"] = {
        "repair_id": REPAIR_ID,
        "candidate_id": CANDIDATE,
        "prior_run_id": PRIOR_RUN_ID,
        "repair_manifest_sha256": repair_hash,
        "staged_script_sha256": script_hash,
        "active_workflow_sha256": workflow_hash,
        "activation_base_main": BASE,
        "repair_package_merge_commit": BASE,
        "repair_package_postmerge_run_id": POSTMERGE_RUN_ID,
        "repair_package_postmerge_evidence_head": POSTMERGE_EVIDENCE_HEAD,
        "activation_is_separate_repository_change": True,
        "retry_authority_created": False,
        "external_dispatch_authority_created": False,
        "candidate_expansion": False,
        "revision_or_file_expansion": False,
        "model_access": "NONE",
        "model_execution": "NONE",
        "training": False,
        "weight_changing_training": False,
        "paid_compute": False,
        "paid_model_api": False,
        "paid_cost_usd": 0.0,
        "production_release": False,
    }
    write_json(BINDING, binding)

    for path in STATUS_TESTS:
        replace_required(path, STATUS_BLOCKED, STATUS_ACTIVE)

    qwen_test = ROOT / "tests/contract/test_b012_qwen_raw_code_recovery.py"
    replace_required(
        qwen_test,
        "    assert ACTIVE_WORKFLOW.read_bytes() == WORKFLOW_SPEC.read_bytes()\n",
        "    assert binding[\"qwen_raw_code_recovery_activation\"][\"active_workflow_sha256\"] == _sha256(WORKFLOW_SPEC)\n",
    )
    replace_required(
        qwen_test,
        '    assert activation["active_workflow_sha256"] == _sha256(ACTIVE_WORKFLOW)\n',
        '    assert activation["active_workflow_sha256"] == _sha256(WORKFLOW_SPEC)\n',
    )
    replace_required(
        qwen_test,
        "def test_qwen_recovery_workflow_has_exact_dispatch_boundary() -> None:\n    text = ACTIVE_WORKFLOW.read_text(encoding=\"utf-8\")\n    assert text == WORKFLOW_SPEC.read_text(encoding=\"utf-8\")\n",
        "def test_historical_qwen_recovery_workflow_spec_preserves_exact_dispatch_boundary() -> None:\n    text = WORKFLOW_SPEC.read_text(encoding=\"utf-8\")\n",
    )

    staged_text = STAGED_TEST.read_text(encoding="utf-8")
    marker = 'WORKFLOW = ROOT / "configs/workflows/b012-qwen-raw-code-recovery-staged.yml"\n'
    if marker not in staged_text:
        raise RuntimeError("staged test constant marker missing")
    staged_text = staged_text.replace(
        marker,
        marker
        + 'ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"\n'
        + 'BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"\n',
        1,
    )
    staged_text += '''\n\ndef test_qwen_staged_recovery_is_materialized_as_current_active_workflow() -> None:\n    manifest = _read_json(MANIFEST)\n    binding = _read_json(BINDING)\n    activation = binding["qwen_raw_code_recovery_staged_activation"]\n    assert isinstance(activation, dict)\n\n    assert manifest["status"] == "READY_FOR_SEPARATE_CANONICAL_ACTIVATION"\n    assert ACTIVE_WORKFLOW.read_bytes() == WORKFLOW.read_bytes()\n    assert binding["status"] == "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"\n    assert activation["repair_id"] == manifest["repair_id"]\n    assert activation["candidate_id"] == "qwen3.5-0.8b-control"\n    assert activation["prior_run_id"] == 34155931982\n    assert activation["repair_manifest_sha256"] == _sha256(MANIFEST)\n    assert activation["staged_script_sha256"] == _sha256(SCRIPT)\n    assert activation["active_workflow_sha256"] == _sha256(ACTIVE_WORKFLOW)\n    assert activation["activation_base_main"] == "0cff2d57ab78c0189c8557f3e2ec59300bd8082d"\n    assert activation["repair_package_postmerge_run_id"] == 34177394009\n    assert activation["repair_package_postmerge_evidence_head"] == (\n        "6e26a1bcaf844cd9a4ff100de54f116cdca77853"\n    )\n    assert activation["activation_is_separate_repository_change"] is True\n    assert activation["retry_authority_created"] is False\n    assert activation["external_dispatch_authority_created"] is False\n    assert activation["candidate_expansion"] is False\n    assert activation["revision_or_file_expansion"] is False\n    assert activation["model_access"] == "NONE"\n    assert activation["model_execution"] == "NONE"\n    assert activation["training"] is False\n    assert activation["weight_changing_training"] is False\n    assert activation["paid_compute"] is False\n    assert activation["paid_model_api"] is False\n    assert activation["paid_cost_usd"] == 0.0\n    assert activation["production_release"] is False\n'''
    STAGED_TEST.write_text(staged_text, encoding="utf-8")

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        f"""# B012 Qwen Staged Raw-Code Recovery Activation\n\n## Exact repository identity\n\n```text\nACTIVATION_BASE_MAIN = {BASE}\nREPAIR_PACKAGE_MERGE_COMMIT = {BASE}\nREPAIR_PACKAGE_POSTMERGE_RUN = {POSTMERGE_RUN_ID} / SUCCESS\nREPAIR_PACKAGE_POSTMERGE_EVIDENCE_HEAD = {POSTMERGE_EVIDENCE_HEAD}\nREPAIR_ID = {REPAIR_ID}\nCANDIDATE_ID = {CANDIDATE}\nPRIOR_QUALIFICATION_RUN_ID = {PRIOR_RUN_ID}\n```\n\n## Activation change\n\nThe separately reviewed staged durability workflow is materialized byte-for-byte at `.github/workflows/b012-qwen-raw-code-recovery.yml`. The executor binding is restored to `SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL` and binds the exact repair manifest, staged executor, and active workflow SHA-256 identities.\n\nThe staged repair manifest intentionally remains `READY_FOR_SEPARATE_CANONICAL_ACTIVATION` because the staged executor requires that exact repair-package state while independently verifying canonical binding activation.\n\n## Authority boundary\n\nThis repository-only activation performs no model access or model execution and creates no new dispatch/retry authority. It does not expand candidate identity, revision, files, network hosts, cost, retention, or output classes.\n\n```text\nMODEL_ACCESS_DURING_ACTIVATION = NONE\nMODEL_EXECUTION_DURING_ACTIVATION = NONE\nTRAINING = FALSE\nWEIGHT_CHANGING_TRAINING = FALSE\nPAID_COMPUTE = FALSE\nPAID_MODEL_API = FALSE\nCANDIDATE_EXPANSION = FALSE\nREVISION_OR_FILE_EXPANSION = FALSE\nRETRY_AUTHORITY_CREATED = FALSE\nEXTERNAL_DISPATCH_AUTHORITY_CREATED = FALSE\nPRODUCTION_RELEASE = FALSE\n```\n\nThe exact issue-comment dispatch remains a later postmerge action under the existing canonical `B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION` envelope.\n""",
        encoding="utf-8",
    )


def run_gates() -> None:
    focused = [
        "tests/contract/test_b012_authority.py",
        "tests/contract/test_b012_executor_binding.py",
        "tests/contract/test_b012_qwen_raw_code_recovery.py",
        "tests/contract/test_b012_qwen_staged_recovery_topology.py",
        "tests/contract/test_b012_runner_shutdown_evidence.py",
        "tests/contract/test_b012_stage_checkpoint_topology.py",
    ]
    run("python", "-m", "pytest", "-q", *focused)
    run("python", "-m", "mstr_qualify", "validate")
    run("python", "-m", "ruff", "check", ".")
    run(
        "python",
        "-m",
        "ruff",
        "format",
        "--check",
        "tests/contract/test_b012_executor_binding.py",
        "tests/contract/test_b012_qwen_raw_code_recovery.py",
        "tests/contract/test_b012_qwen_staged_recovery_topology.py",
        "tests/contract/test_b012_runner_shutdown_evidence.py",
        "tests/contract/test_b012_stage_checkpoint_topology.py",
    )
    run("python", "-m", "pytest", "-q")
    run("python", "-m", "mypy", "src/mstr_qualify")


def final_scope_and_live_guard() -> None:
    changed = set(output("git", "diff", "--name-only", BASE).splitlines())
    if changed != ALLOWED:
        raise RuntimeError(f"activation scope drift: {sorted(changed)}")
    if output("git", "ls-remote", "origin", "refs/heads/main").split()[0] != BASE:
        raise RuntimeError("canonical main moved before activation commit")
    if output("git", "ls-remote", "origin", f"refs/heads/{TARGET}").split()[0] != BASE:
        raise RuntimeError("target activation branch moved before publication")


def main() -> None:
    guard_exact_base()
    run("git", "checkout", "-B", TARGET, f"origin/{TARGET}")
    if output("git", "rev-parse", "HEAD") != BASE:
        raise RuntimeError("activation checkout identity mismatch")

    assert_exact_main_b012_eligibility()
    materialize_activation()
    run_gates()
    final_scope_and_live_guard()

    run("git", "config", "user.name", "MSTR Evidence Builder")
    run("git", "config", "user.email", "actions@users.noreply.github.com")
    run("git", "add", *sorted(ALLOWED))
    run("git", "commit", "-m", "fix(b012): activate staged Qwen raw-code recovery")
    head = output("git", "rev-parse", "HEAD")
    run("git", "push", "origin", f"HEAD:refs/heads/{TARGET}")
    print(f"B012_STAGED_ACTIVATION_HEAD={head}")
    print("B012_STAGED_ACTIVATION_BUILDER=PASS")


if __name__ == "__main__":
    main()
