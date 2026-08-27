from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance
from mstr_qualify.task_gate import (
    diagnose_task_node,
    evaluate_task_eligibility,
    load_task_catalog,
)

_CANONICAL_MAIN = "a" * 40
_GATED_EFFECTS = (
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
)


def _base_node() -> dict[str, object]:
    return {
        "schema_version": "mstr.task-node.v0",
        "task_id": "B900",
        "workstream_id": "MSTR-000B",
        "title": "Gate fixture",
        "canonical_state": "PENDING",
        "prerequisites": [],
        "outputs": [],
        "evidence_outputs": ["evidence/fixture.md"],
        "candidate_dependent": False,
        "external_effect_class": "NO_EXTERNAL_EFFECT",
        "parallel_safe": False,
        "supersedes": [],
        "superseded_by": [],
        "closeout_rule": {
            "terminal_states": ["COMPLETE_CANONICAL"],
            "require_all_outputs": False,
            "require_all_evidence_outputs": True,
            "completion_requires_merge": True,
        },
    }


@pytest.mark.parametrize("effect", _GATED_EFFECTS)
def test_every_gated_effect_missing_authority_is_fail_closed(effect: str) -> None:
    node = _base_node()
    node["external_effect_class"] = effect

    result = diagnose_task_node(node, canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["authority_result"] == {
        "required": True,
        "authority_id": "MISSING_REQUIRED_AUTHORITY_ID",
        "satisfied": False,
        "reasons": ["authority.required_binding_missing"],
    }
    assert "task_node.invalid" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_candidate_dependent_missing_pool_requirement_is_fail_closed() -> None:
    node = _base_node()
    node["candidate_dependent"] = True

    result = diagnose_task_node(node, canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["candidate_pool_result"] == {
        "required": True,
        "requirement_id": "MISSING_CANDIDATE_POOL_REQUIREMENT_ID",
        "observed_pool_id": None,
        "satisfied": False,
        "reasons": ["candidate_pool.required_binding_missing"],
    }
    validate_instance("mstr-task-eligibility-v0", result)


def test_live_b002_catalog_covers_every_declared_b_task() -> None:
    catalog = load_task_catalog()

    assert set(catalog.nodes) == {f"B{index:03d}" for index in range(1, 35)}
    assert catalog.nodes["B001"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert catalog.nodes["B002"]["canonical_state"] == "PENDING"


def test_b002_is_bootstrap_eligible_from_canonical_b001() -> None:
    result = evaluate_task_eligibility("B002", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["prerequisite_results"][0]["task_id"] == "B001"
    assert result["prerequisite_results"][0]["satisfied"] is True
    assert result["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)


def test_b003_fails_closed_until_b002_closeout_is_canonical() -> None:
    result = evaluate_task_eligibility("B003", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["prerequisite_results"][0]["task_id"] == "B002"
    assert result["prerequisite_results"][0]["observed_state"] == "PENDING"
    assert result["prerequisite_results"][0]["satisfied"] is False
    assert "prerequisite.unsatisfied:B002" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_explicitly_blocked_task_never_becomes_eligible() -> None:
    result = evaluate_task_eligibility("B011", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert "task.blocked" in result["reasons"]
    assert "task.unresolved_binding" in result["reasons"]


def test_terminal_task_is_not_execution_eligible() -> None:
    result = evaluate_task_eligibility("B001", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]


def test_unknown_task_id_is_configuration_error() -> None:
    with pytest.raises(QualificationError, match="unknown task id"):
        evaluate_task_eligibility("B999", canonical_main=_CANONICAL_MAIN)


def _write_minimal_catalog(root: Path, *, b001_checked: bool) -> Path:
    tasks_dir = root / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    mark = "x" if b001_checked else " "
    (tasks_dir / "tasks.md").write_text(
        f"- [{mark}] **B001 Root task.**\n- [ ] **B002 Target task.**\n",
        encoding="utf-8",
    )
    evidence = root / "evidence" / "B001.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("canonical evidence\n", encoding="utf-8")
    payload = {
        "catalog_version": "mstr.task-catalog.v0",
        "workstream_id": "MSTR-000B",
        "tasks_file": "specs/002-code-model-supremacy-foundation/tasks.md",
        "defaults": {
            "outputs": [],
            "candidate_dependent": False,
            "external_effect_class": "NO_EXTERNAL_EFFECT",
            "parallel_safe": False,
            "supersedes": [],
            "superseded_by": [],
            "closeout_rule": {
                "terminal_states": ["COMPLETE_CANONICAL"],
                "require_all_outputs": False,
                "require_all_evidence_outputs": True,
                "completion_requires_merge": True,
            },
        },
        "tasks": {
            "B001": {
                "canonical_state": "COMPLETE_CANONICAL",
                "prerequisites": [],
                "evidence_outputs": ["evidence/B001.md"],
            },
            "B002": {
                "canonical_state": "PENDING",
                "prerequisites": ["B001"],
                "evidence_outputs": ["evidence/B002.md"],
            },
        },
    }
    catalog_path = root / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    return catalog_path


def test_checkbox_state_conflict_blocks_successor(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=False)

    result = evaluate_task_eligibility(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is False
    assert "prerequisite.state_checkbox_conflict" in predecessor["reasons"]


def test_missing_predecessor_binding_fails_closed(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"]["prerequisites"] = ["A999"]
    catalog_path.write_text(json.dumps(data), encoding="utf-8")

    result = evaluate_task_eligibility(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    assert result["semantic_checks"]["prerequisite_set_complete"] is False
    assert result["prerequisite_results"] == [
        {
            "task_id": "A999",
            "required_state": "COMPLETE_CANONICAL",
            "observed_state": None,
            "evidence_present": False,
            "satisfied": False,
            "reasons": ["prerequisite.missing_task_binding"],
        }
    ]


def test_catalog_input_is_not_mutated_by_evaluation(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    before = catalog_path.read_bytes()

    result = evaluate_task_eligibility(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    assert catalog_path.read_bytes() == before
