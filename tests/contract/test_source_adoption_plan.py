from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json"
TASKS = ROOT / "specs/002-code-model-supremacy-foundation/tasks.md"
CATALOG = ROOT / "configs/task-gate/mstr-000b.json"
STRATEGY = ROOT / "docs/canonical/MSTR_SOURCE_ADOPTION_AND_CAPABILITY_MINING_STRATEGY.md"


def test_source_adoption_amendment_is_planning_only() -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert len(snapshot["sources"]) == 18
    boundary = snapshot["authority_boundary"]
    assert boundary["source_code_permission_is_data_admission"] is False
    assert boundary["source_code_permission_is_model_weight_authority"] is False
    assert boundary["source_code_permission_is_training_authority"] is False
    assert boundary["source_code_permission_is_external_effect_authority"] is False
    assert boundary["training"] is False
    assert boundary["paid_cost_usd"] == 0.0


def test_completed_history_and_b031_machine_gate_are_unchanged() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["tasks"]
    for task_id in [f"B{i:03d}" for i in range(14, 31)]:
        assert catalog[task_id]["canonical_state"] == "COMPLETE_CANONICAL"
    assert catalog["B031"]["canonical_state"] == "PENDING"
    assert catalog["B032"]["prerequisites"] == ["B031"]
    assert catalog["B033"]["prerequisites"] == ["B032"]


def test_b032_b033_bind_source_adoption_without_authority_expansion() -> None:
    tasks = TASKS.read_text(encoding="utf-8")
    strategy = STRATEGY.read_text(encoding="utf-8")
    for token in (
        "SourceAdoptionRecord",
        "ExecutionBackendProfile",
        "ResumableTaskCheckpoint",
        "ImprovementDecisionRecord",
        "RepositoryContextIndexProfile",
        "TrainingBackendParityRecord",
        "MINIMAL_BASH_LINEAR_BASELINE",
    ):
        assert token in tasks
        assert token in strategy
    assert "B032 itself authorizes none of those external effects" in tasks
    assert "source-code-permission conflation" in tasks
