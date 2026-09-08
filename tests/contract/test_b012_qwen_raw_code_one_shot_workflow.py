from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "artifacts/manifests/B012-qwen-raw-code-one-shot-topology-repair.json"
WORKFLOW_SPEC = ROOT / "configs/workflows/b012-qwen-raw-code-one-shot-recovery.yml"
ACTIVE_WORKFLOW = ROOT / ".github/workflows/b012-qwen-raw-code-recovery.yml"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_one_shot_workflow_is_materialized_owner_scoped_and_json_only() -> None:
    manifest = _read_json(MANIFEST)
    activation = manifest["activation"]
    assert isinstance(activation, dict)
    spec = WORKFLOW_SPEC.read_text(encoding="utf-8")
    active = ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    command = "B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982"

    assert activation["active_workflow_materialized"] is True
    assert activation["separate_activation_pr_required"] is True
    assert WORKFLOW_SPEC.read_bytes() == ACTIVE_WORKFLOW.read_bytes()
    assert command in spec
    assert command in active
    assert "github.event.issue.number == 162" in spec
    assert "github.event.comment.user.login == 'TheHalfMoon'" in spec
    assert "github.event.comment.author_association == 'OWNER'" in spec
    assert "python colab/mstr_b012_qwen_raw_code_one_shot.py" in spec
    assert "timeout-minutes: 45" in spec
    assert "cancel-in-progress: false" in spec
    assert spec.count("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02") == 7
    assert spec.count("retention-days: 7") == 7
    assert ".gguf" not in spec
    assert ".safetensors" not in spec
    assert "actions/download-artifact@" not in spec
    assert "actions/cache@" not in spec


def test_active_recovery_surface_is_exactly_the_reviewed_one_shot_spec() -> None:
    active = ACTIVE_WORKFLOW.read_text(encoding="utf-8")
    assert "B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982" not in active
    assert "B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982" in active
    assert "python colab/mstr_b012_qwen_raw_code_one_shot.py" in active
