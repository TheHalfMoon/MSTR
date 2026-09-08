#!/usr/bin/env python3
"""B012 Qwen one-shot raw-code recovery activation wrapper."""

from __future__ import annotations

from pathlib import Path

import mstr_b012_qwen_raw_code_recovery_case_checkpoint as case_checkpoint
import mstr_b012_raw_code_one_shot as one_shot_raw_code
from mstr_b012_governance import ExecutionError
from mstr_executor_toolchain import read_json, require_file_sha256

CANDIDATE_ID = "qwen3.5-0.8b-control"
PRIOR_QUALIFICATION_RUN_ID = 34155931982
TRIGGERING_INCIDENT_RUN_ID = 34265475666
REPAIR_MANIFEST_PATH = Path("artifacts/manifests/B012-qwen-raw-code-one-shot-topology-repair.json")
SCRIPT_PATH = Path("colab/mstr_b012_qwen_raw_code_one_shot.py")
ONE_SHOT_HELPER_PATH = Path("colab/mstr_b012_raw_code_one_shot.py")
ACTIVE_WORKFLOW_PATH = Path(".github/workflows/b012-qwen-raw-code-recovery.yml")
ACTIVATION_KEY = "qwen_raw_code_one_shot_activation"


def _require_one_shot_activation(
    repo_root: Path,
) -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object]]:
    binding, envelope, lock = case_checkpoint._require_binding(repo_root)
    repair = read_json(repo_root / REPAIR_MANIFEST_PATH)
    if repair.get("status") != "READY_FOR_SEPARATE_CANONICAL_ACTIVATION":
        raise ExecutionError("B012 Qwen one-shot repair is not activation-ready")
    if repair.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen one-shot repair candidate drift detected")
    if repair.get("prior_qualification_run_id") != PRIOR_QUALIFICATION_RUN_ID:
        raise ExecutionError("B012 Qwen one-shot qualification identity drift detected")
    trigger = repair.get("triggering_incident")
    if not isinstance(trigger, dict) or trigger.get("run_id") != TRIGGERING_INCIDENT_RUN_ID:
        raise ExecutionError("B012 Qwen one-shot triggering incident drift detected")

    activation = binding.get(ACTIVATION_KEY)
    if not isinstance(activation, dict):
        raise ExecutionError("B012 Qwen one-shot recovery is not canonically activated")
    if activation.get("candidate_id") != CANDIDATE_ID:
        raise ExecutionError("B012 Qwen one-shot activation candidate drift detected")
    if activation.get("prior_qualification_run_id") != PRIOR_QUALIFICATION_RUN_ID:
        raise ExecutionError("B012 Qwen one-shot activation qualification drift detected")
    if activation.get("triggering_incident_run_id") != TRIGGERING_INCIDENT_RUN_ID:
        raise ExecutionError("B012 Qwen one-shot activation incident drift detected")

    expected_manifest = activation.get("repair_manifest_sha256")
    expected_script = activation.get("one_shot_script_sha256")
    expected_helper = activation.get("one_shot_raw_code_helper_sha256")
    expected_workflow = activation.get("active_workflow_sha256")
    if not all(
        isinstance(value, str)
        for value in (expected_manifest, expected_script, expected_helper, expected_workflow)
    ):
        raise ExecutionError("B012 Qwen one-shot activation hash binding is incomplete")

    require_file_sha256(repo_root / REPAIR_MANIFEST_PATH, str(expected_manifest))
    require_file_sha256(repo_root / SCRIPT_PATH, str(expected_script))
    require_file_sha256(repo_root / ONE_SHOT_HELPER_PATH, str(expected_helper))
    require_file_sha256(repo_root / ACTIVE_WORKFLOW_PATH, str(expected_workflow))
    if activation.get("retry_authority_created") is not False:
        raise ExecutionError("B012 Qwen one-shot repair must not fabricate retry authority")
    if activation.get("external_dispatch_authority_created") is not False:
        raise ExecutionError("B012 Qwen one-shot repair must not fabricate dispatch authority")
    if activation.get("cross_run_resume_authority_created") is not False:
        raise ExecutionError("B012 Qwen one-shot repair must not fabricate resume authority")
    return binding, envelope, lock, repair


def _activate_variant() -> None:
    case_checkpoint.REPAIR_MANIFEST_PATH = REPAIR_MANIFEST_PATH
    case_checkpoint.SCRIPT_PATH = SCRIPT_PATH
    case_checkpoint.ACTIVE_WORKFLOW_PATH = ACTIVE_WORKFLOW_PATH
    case_checkpoint._require_activation = _require_one_shot_activation
    case_checkpoint.run_raw_code_proxy = one_shot_raw_code.run_raw_code_proxy


def main() -> int:
    _activate_variant()
    return case_checkpoint.main()


if __name__ == "__main__":
    raise SystemExit(main())
