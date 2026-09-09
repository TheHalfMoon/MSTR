#!/usr/bin/env python3
"""B012 Qwen raw-code recovery variant using pinned llama-completion."""

from __future__ import annotations

import shutil
from pathlib import Path

import mstr_b012_qwen_raw_code_recovery_case_checkpoint as case_checkpoint
import mstr_b012_raw_code_completion as completion_raw_code
from mstr_b012_governance import ExecutionError
from mstr_executor_toolchain import clone_exact_commit, read_json, require_file_sha256

CANDIDATE_ID = "qwen3.5-0.8b-control"
PRIOR_QUALIFICATION_RUN_ID = 34155931982
TRIGGERING_INCIDENT_RUN_ID = 34288154926
REPAIR_MANIFEST_PATH = Path(
    "artifacts/manifests/B012-qwen-raw-code-completion-runtime-repair.json"
)
SCRIPT_PATH = Path("colab/mstr_b012_qwen_raw_code_completion.py")
COMPLETION_HELPER_PATH = Path("colab/mstr_b012_raw_code_completion.py")
ACTIVE_WORKFLOW_PATH = Path(".github/workflows/b012-qwen-raw-code-recovery.yml")
ACTIVATION_KEY = "qwen_raw_code_completion_activation"


def _prepare_completion_tools(
    *, lock: dict[str, object], workdir: Path
) -> tuple[Path, Path, Path, dict[str, object]]:
    llama = lock.get("llama_cpp")
    if not isinstance(llama, dict):
        raise ExecutionError("B012 llama.cpp lock is missing")
    repository = llama.get("repository")
    conversion_commit = llama.get("conversion_quantization_commit")
    runtime_commit = llama.get("runtime_commit")
    build_flags = llama.get("build_flags")
    if (
        not isinstance(repository, str)
        or not isinstance(conversion_commit, str)
        or not isinstance(runtime_commit, str)
        or not isinstance(build_flags, list)
        or not all(isinstance(item, str) for item in build_flags)
    ):
        raise ExecutionError("B012 Qwen completion llama.cpp identity is invalid")

    conversion_dir = workdir / "llama-convert"
    quantizer = clone_exact_commit(
        repository=repository,
        commit=conversion_commit,
        destination=conversion_dir,
        build_flags=build_flags,
        target="llama-quantize",
    )
    tools = workdir / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    quantizer_copy = tools / "llama-quantize"
    shutil.copy2(quantizer, quantizer_copy)
    shutil.rmtree(conversion_dir / "build", ignore_errors=True)
    shutil.rmtree(conversion_dir / ".git", ignore_errors=True)

    runtime_dir = workdir / "llama-runtime"
    completion = clone_exact_commit(
        repository=repository,
        commit=runtime_commit,
        destination=runtime_dir,
        build_flags=build_flags,
        target="llama-completion",
    )
    completion_copy = tools / "llama-completion"
    shutil.copy2(completion, completion_copy)
    shutil.rmtree(runtime_dir, ignore_errors=True)
    return (
        conversion_dir,
        quantizer_copy,
        completion_copy,
        {
            "repository": repository,
            "conversion_quantization_commit": conversion_commit,
            "runtime_commit": runtime_commit,
            "build_flags": build_flags,
            "recovery_targets": ["llama-quantize", "llama-completion"],
            "runtime_parser_example": "LLAMA_EXAMPLE_COMPLETION",
            "llama_bench_built": False,
        },
    )


def _require_completion_activation(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    binding, envelope, lock = case_checkpoint._require_binding(repo_root)
    repair = read_json(repo_root / REPAIR_MANIFEST_PATH)
    if repair.get("status") != "READY_FOR_SEPARATE_CANONICAL_ACTIVATION":
        raise ExecutionError("B012 Qwen completion repair is not activation-ready")
    if repair.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen completion repair candidate drift detected")
    if repair.get("prior_qualification_run_id") != PRIOR_QUALIFICATION_RUN_ID:
        raise ExecutionError("B012 Qwen completion qualification identity drift detected")
    trigger = repair.get("triggering_incident")
    if not isinstance(trigger, dict) or trigger.get("run_id") != TRIGGERING_INCIDENT_RUN_ID:
        raise ExecutionError("B012 Qwen completion triggering incident drift detected")

    activation = binding.get(ACTIVATION_KEY)
    if not isinstance(activation, dict):
        raise ExecutionError("B012 Qwen completion recovery is not canonically activated")
    if activation.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen completion activation candidate drift detected")
    if activation.get("prior_qualification_run_id") != PRIOR_QUALIFICATION_RUN_ID:
        raise ExecutionError("B012 Qwen completion activation qualification drift detected")
    if activation.get("triggering_incident_run_id") != TRIGGERING_INCIDENT_RUN_ID:
        raise ExecutionError("B012 Qwen completion activation incident drift detected")

    expected_manifest = activation.get("repair_manifest_sha256")
    expected_script = activation.get("completion_script_sha256")
    expected_helper = activation.get("completion_raw_code_helper_sha256")
    expected_workflow = activation.get("active_workflow_sha256")
    if not all(
        isinstance(value, str)
        for value in (expected_manifest, expected_script, expected_helper, expected_workflow)
    ):
        raise ExecutionError("B012 Qwen completion activation hash binding is incomplete")

    require_file_sha256(repo_root / REPAIR_MANIFEST_PATH, str(expected_manifest))
    require_file_sha256(repo_root / SCRIPT_PATH, str(expected_script))
    require_file_sha256(repo_root / COMPLETION_HELPER_PATH, str(expected_helper))
    require_file_sha256(repo_root / ACTIVE_WORKFLOW_PATH, str(expected_workflow))
    if activation.get("retry_authority_created") is not False:
        raise ExecutionError("B012 Qwen completion repair must not fabricate retry authority")
    if activation.get("external_dispatch_authority_created") is not False:
        raise ExecutionError("B012 Qwen completion repair must not fabricate dispatch authority")
    if activation.get("cross_run_resume_authority_created") is not False:
        raise ExecutionError("B012 Qwen completion repair must not fabricate resume authority")
    return binding, envelope, lock, repair


def _activate_variant() -> None:
    case_checkpoint.REPAIR_MANIFEST_PATH = REPAIR_MANIFEST_PATH
    case_checkpoint.SCRIPT_PATH = SCRIPT_PATH
    case_checkpoint.ACTIVE_WORKFLOW_PATH = ACTIVE_WORKFLOW_PATH
    case_checkpoint._require_activation = _require_completion_activation
    case_checkpoint._prepare_minimal_tools = _prepare_completion_tools
    case_checkpoint.run_raw_code_proxy = completion_raw_code.run_raw_code_proxy


def main() -> int:
    _activate_variant()
    return case_checkpoint.main()


if __name__ == "__main__":
    raise SystemExit(main())
