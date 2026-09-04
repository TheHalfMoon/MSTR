from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from mstr_qualify.errors import QualificationError
from mstr_qualify.schemas import validate_instance
from mstr_qualify.task_gate import (
    diagnose_task_node,
    evaluate_task_eligibility,
    evaluate_task_snapshot,
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
    assert catalog.nodes["B002"]["canonical_state"] == "COMPLETE_CANONICAL"
    assert catalog.nodes["B003"]["canonical_state"] == "COMPLETE_CANONICAL"


def test_b002_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B002", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b003_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B003", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b004_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B004", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b005_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B005", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b006_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B006", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b007_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B007", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b008_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B008", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b009_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B009", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b010_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B010", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b011_is_eligible_after_exact_founder_authority_capture() -> None:
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert "task.blocked" not in result["reasons"]
    assert "task.unresolved_binding" not in result["reasons"]
    predecessor = next(row for row in result["prerequisite_results"] if row["task_id"] == "B010")
    assert predecessor["satisfied"] is True
    assert result["authority_result"] == {
        "required": True,
        "authority_id": "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED",
        "satisfied": True,
        "reasons": [],
    }
    validate_instance("mstr-task-eligibility-v0", result)


def test_b006_fails_closed_when_b005_discovery_manifest_is_missing(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text(
        "- [x] **B005 Root task.**\n- [ ] **B006 Successor task.**\n",
        encoding="utf-8",
    )
    evidence = tmp_path / "evidence" / "mstr-000b" / "B005-code-backbone-rescan.md"
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
            "B005": {
                "canonical_state": "COMPLETE_CANONICAL",
                "closeout_rule": {"require_all_outputs": True},
                "prerequisites": [],
                "outputs": ["artifacts/manifests/B005-code-backbone-discovery.json"],
                "evidence_outputs": ["evidence/mstr-000b/B005-code-backbone-rescan.md"],
            },
            "B006": {
                "canonical_state": "PENDING",
                "prerequisites": ["B005"],
                "evidence_outputs": [],
            },
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    result = evaluate_task_snapshot(
        "B006",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    assert "prerequisite.unsatisfied:B005" in result["reasons"]
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert "missing:artifacts/manifests/B005-code-backbone-discovery.json" in predecessor["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b008_fails_closed_when_b007_corpus_is_missing(
    tmp_path: Path,
) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text(
        "- [x] **B007 Root task.**\n- [ ] **B008 Successor task.**\n", encoding="utf-8"
    )
    evidence = tmp_path / "evidence" / "mstr-000b" / "B007-tokenizer-protocol.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("canonical evidence\n", encoding="utf-8")
    manifest = tmp_path / "benchmarks" / "manifests" / "B007-tokenizer-economics.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{}\n", encoding="utf-8")
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
            "B007": {
                "canonical_state": "COMPLETE_CANONICAL",
                "closeout_rule": {"require_all_outputs": True},
                "prerequisites": [],
                "outputs": [
                    "benchmarks/manifests/B007-tokenizer-economics.json",
                    "benchmarks/fixtures/tokenizer-economics/B007-corpus.json",
                ],
                "evidence_outputs": ["evidence/mstr-000b/B007-tokenizer-protocol.md"],
            },
            "B008": {
                "canonical_state": "PENDING",
                "prerequisites": ["B007"],
                "evidence_outputs": [],
            },
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    result = evaluate_task_snapshot(
        "B008", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    assert result["eligible"] is False
    assert "prerequisite.unsatisfied:B007" in result["reasons"]
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False and predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert (
        "missing:benchmarks/fixtures/tokenizer-economics/B007-corpus.json" in predecessor["reasons"]
    )
    validate_instance("mstr-task-eligibility-v0", result)


def test_b009_fails_closed_when_one_b008_result_is_missing(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text(
        "- [x] **B008 Root task.**\n- [ ] **B009 Successor task.**\n",
        encoding="utf-8",
    )
    evidence = tmp_path / "evidence" / "mstr-000b" / "B008-tokenizer-economics.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("canonical evidence\n", encoding="utf-8")
    result_paths = [
        "artifacts/results/tokenizer/B008/granite-4.1-3b.json",
        "artifacts/results/tokenizer/B008/mellum-4b.json",
    ]
    present = tmp_path / result_paths[0]
    present.parent.mkdir(parents=True)
    present.write_text("{}\n", encoding="utf-8")
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
            "B008": {
                "canonical_state": "COMPLETE_CANONICAL",
                "closeout_rule": {"require_all_outputs": True},
                "prerequisites": [],
                "outputs": result_paths,
                "evidence_outputs": ["evidence/mstr-000b/B008-tokenizer-economics.md"],
            },
            "B009": {
                "canonical_state": "PENDING",
                "prerequisites": ["B008"],
                "evidence_outputs": [],
            },
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    result = evaluate_task_snapshot(
        "B009",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    assert "prerequisite.unsatisfied:B008" in result["reasons"]
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert f"missing:{result_paths[1]}" in predecessor["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b010_fails_closed_when_b009_decision_artifact_is_missing(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text(
        "- [x] **B009 Root task.**\n- [ ] **B010 Successor task.**\n",
        encoding="utf-8",
    )
    evidence = tmp_path / "evidence" / "mstr-000b" / "B009-compatibility.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("canonical evidence\n", encoding="utf-8")
    decision_path = "artifacts/decisions/B009-training-runtime-compatibility.json"
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
            "B009": {
                "canonical_state": "COMPLETE_CANONICAL",
                "closeout_rule": {"require_all_outputs": True},
                "prerequisites": [],
                "outputs": [decision_path],
                "evidence_outputs": ["evidence/mstr-000b/B009-compatibility.md"],
            },
            "B010": {
                "canonical_state": "PENDING",
                "prerequisites": ["B009"],
                "evidence_outputs": [],
            },
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    result = evaluate_task_snapshot(
        "B010", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    assert result["eligible"] is False
    assert "prerequisite.unsatisfied:B009" in result["reasons"]
    predecessor = result["prerequisite_results"][0]
    assert predecessor["task_id"] == "B009"
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert f"missing:{decision_path}" in predecessor["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_exact_founder_authority_unblocks_pending_b011() -> None:
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert "task.blocked" not in result["reasons"]
    assert "task.unresolved_binding" not in result["reasons"]
    assert result["authority_result"]["authority_id"] == (
        "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    )
    assert result["authority_result"]["satisfied"] is True


def test_terminal_task_is_not_execution_eligible() -> None:
    result = evaluate_task_snapshot("B001", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]


def test_unknown_task_id_is_configuration_error() -> None:
    with pytest.raises(QualificationError, match="unknown task id"):
        evaluate_task_snapshot("B999", canonical_main=_CANONICAL_MAIN)


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

    result = evaluate_task_snapshot(
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

    result = evaluate_task_snapshot(
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

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    assert catalog_path.read_bytes() == before


def _git(tmp_path: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_catalog_path_cannot_escape_repository(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}", encoding="utf-8")

    with pytest.raises(QualificationError) as captured:
        load_task_catalog(outside, repository_root=root)

    assert captured.value.code == "task_gate.catalog_outside_repository"


def test_unsafe_authority_id_cannot_traverse_artifact_directory(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "external_effect_class": "PAID_COMPUTE",
            "required_authority_id": "../escape",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    escaped = tmp_path / "artifacts" / "escape.json"
    escaped.parent.mkdir(parents=True)
    escaped.write_text(
        json.dumps(
            {
                "authority_id": "../escape",
                "task_id": "B002",
                "external_effect_class": "PAID_COMPUTE",
                "status": "AUTHORIZED_CANONICAL",
                "scope": {"executor": "fixture"},
                "cost_resource_ceiling": {"usd_max": 1},
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    assert result["authority_result"]["satisfied"] is False
    assert "authority.canonical_envelope_missing_or_invalid" in result["reasons"]


def test_authority_requires_scope_and_cost_resource_ceiling(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "external_effect_class": "PAID_COMPUTE",
            "required_authority_id": "AUTH-B002",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    authority = tmp_path / "artifacts" / "authorities" / "AUTH-B002.json"
    authority.parent.mkdir(parents=True)
    envelope = {
        "authority_id": "AUTH-B002",
        "task_id": "B002",
        "external_effect_class": "PAID_COMPUTE",
        "status": "AUTHORIZED_CANONICAL",
        "scope": {"executor": "fixture"},
    }
    authority.write_text(json.dumps(envelope), encoding="utf-8")

    missing_ceiling = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert missing_ceiling["eligible"] is False

    envelope["cost_resource_ceiling"] = {
        "cost_model": "fixed-cap",
        "limits": [
            {"resource": "cost", "max": 0, "unit": "USD"},
            {"resource": "wall_time", "max": 1, "unit": "minute"},
        ],
    }
    authority.write_text(json.dumps(envelope), encoding="utf-8")
    complete = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert complete["eligible"] is True


def test_unsafe_candidate_pool_id_cannot_traverse_decision_directory(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "candidate_dependent": True,
            "candidate_pool_requirement_id": "../escape",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    escaped = tmp_path / "artifacts" / "escape.json"
    escaped.parent.mkdir(parents=True)
    escaped.write_text(
        json.dumps(
            {
                "candidate_pool_id": "../escape",
                "stable_pool": True,
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    assert result["candidate_pool_result"]["satisfied"] is False
    assert "candidate_pool.canonical_decision_missing_or_invalid" in result["reasons"]


def test_real_evaluation_requires_verified_main_refs(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "B002 Test")
    _git(tmp_path, "config", "user.email", "b002@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture main")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(tmp_path, "update-ref", "refs/remotes/origin/main", head)

    result = evaluate_task_eligibility(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
    )
    assert result["eligible"] is True
    assert result["canonical_main"] == head

    _git(tmp_path, "switch", "-c", "feature")
    (tmp_path / "feature.txt").write_text("feature" + chr(10), encoding="utf-8")
    _git(tmp_path, "add", "feature.txt")
    _git(tmp_path, "commit", "-m", "feature commit")
    with pytest.raises(QualificationError) as feature:
        evaluate_task_eligibility(
            "B002",
            repository_root=tmp_path,
            catalog_path=catalog_path,
        )
    assert feature.value.code == "task_gate.not_canonical_main"

    _git(tmp_path, "switch", "main")
    with catalog_path.open("a", encoding="utf-8") as handle:
        handle.write(chr(10))
    with pytest.raises(QualificationError) as dirty:
        evaluate_task_eligibility(
            "B002",
            repository_root=tmp_path,
            catalog_path=catalog_path,
        )
    assert dirty.value.code == "task_gate.dirty_checkout"


def test_real_evaluation_rejects_main_tracking_ref_drift(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    _git(tmp_path, "init", "-b", "main")
    _git(tmp_path, "config", "user.name", "B002 Test")
    _git(tmp_path, "config", "user.email", "b002@example.invalid")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "fixture main")
    first_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(tmp_path, "update-ref", "refs/remotes/origin/main", first_head)

    (tmp_path / "main-drift.txt").write_text("drift" + chr(10), encoding="utf-8")
    _git(tmp_path, "add", "main-drift.txt")
    _git(tmp_path, "commit", "-m", "local main drift")

    with pytest.raises(QualificationError) as drift:
        evaluate_task_eligibility(
            "B002",
            repository_root=tmp_path,
            catalog_path=catalog_path,
        )
    assert drift.value.code == "task_gate.main_ref_mismatch"


def test_undeclared_not_required_state_cannot_satisfy_predecessor(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B001"]["canonical_state"] = "NOT_REQUIRED_FAKE"
    catalog_path.write_text(json.dumps(data), encoding="utf-8")

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["observed_state"] == "NOT_REQUIRED_FAKE"
    assert predecessor["satisfied"] is False
    assert "prerequisite.not_terminal" in predecessor["reasons"]
    assert "prerequisite.state_checkbox_conflict" in predecessor["reasons"]


def test_declared_not_required_state_can_satisfy_predecessor(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B001"]["canonical_state"] = "NOT_REQUIRED_FIXTURE"
    data["tasks"]["B001"]["closeout_rule"] = {
        "terminal_states": [
            "COMPLETE_CANONICAL",
            "NOT_REQUIRED_FIXTURE",
        ]
    }
    catalog_path.write_text(json.dumps(data), encoding="utf-8")

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is True
    assert predecessor["observed_state"] == "NOT_REQUIRED_FIXTURE"
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


def test_unknown_unresolved_binding_key_is_rejected(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["unresolved_bindings"] = {"B999": "typo must not disappear"}
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(QualificationError) as captured:
        load_task_catalog(catalog_path, repository_root=tmp_path)
    assert captured.value.code == "task_gate.catalog_unresolved_unknown"


def test_live_catalog_binds_reviewed_machine_outputs() -> None:
    catalog = load_task_catalog()
    assert catalog.nodes["B003"]["outputs"] == [
        "src/mstr_qualify/task_drift.py",
        "tests/**/*task_drift*.py",
        "tests/fixtures/**/*task_drift*",
    ]
    assert catalog.nodes["B006"]["outputs"] == ["artifacts/candidates/*.json"]
    assert catalog.nodes["B003"]["closeout_rule"]["require_all_outputs"] is True
    assert catalog.nodes["B006"]["closeout_rule"]["require_all_outputs"] is True


def test_b011_weight_access_observes_exact_authority_after_b010_resolution() -> None:
    catalog = load_task_catalog()
    node = catalog.nodes["B011"]
    assert node["canonical_state"] == "PENDING"
    assert node["external_effect_class"] == "MODEL_WEIGHT_ACCESS"
    assert node["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)
    assert result["eligible"] is True
    assert result["authority_result"]["required"] is True
    assert result["authority_result"]["satisfied"] is True


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlink unavailable: {exc}")


def test_external_symlink_cannot_satisfy_required_output(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B001"]["outputs"] = ["artifacts/B001-output.json"]
    data["tasks"]["B001"]["closeout_rule"] = {"require_all_outputs": True}
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    outside = tmp_path.parent / f"{tmp_path.name}-outside-output.json"
    outside.write_text("{}", encoding="utf-8")
    link = tmp_path / "artifacts" / "B001-output.json"
    link.parent.mkdir(parents=True)
    _symlink_or_skip(link, outside)
    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert result["eligible"] is False
    assert result["prerequisite_results"][0]["evidence_present"] is False


def test_external_authority_symlink_cannot_authorize(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "external_effect_class": "PAID_COMPUTE",
            "required_authority_id": "AUTH-B002",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    envelope = {
        "authority_id": "AUTH-B002",
        "task_id": "B002",
        "external_effect_class": "PAID_COMPUTE",
        "status": "AUTHORIZED_CANONICAL",
        "scope": {"executor": "fixture"},
        "cost_resource_ceiling": {
            "cost_model": "fixed-cap",
            "limits": [{"resource": "cost", "max": 0, "unit": "USD"}],
        },
    }
    outside = tmp_path.parent / f"{tmp_path.name}-outside-authority.json"
    outside.write_text(json.dumps(envelope), encoding="utf-8")
    link = tmp_path / "artifacts" / "authorities" / "AUTH-B002.json"
    link.parent.mkdir(parents=True)
    _symlink_or_skip(link, outside)
    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert result["eligible"] is False
    assert result["authority_result"]["satisfied"] is False


def test_external_candidate_pool_symlink_cannot_satisfy(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "candidate_dependent": True,
            "candidate_pool_requirement_id": "POOL-B002",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    outside = tmp_path.parent / f"{tmp_path.name}-outside-pool.json"
    outside.write_text(
        json.dumps(
            {
                "candidate_pool_id": "POOL-B002",
                "stable_pool": True,
            }
        ),
        encoding="utf-8",
    )
    link = tmp_path / "artifacts" / "decisions" / "POOL-B002.json"
    link.parent.mkdir(parents=True)
    _symlink_or_skip(link, outside)
    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert result["eligible"] is False
    assert result["candidate_pool_result"]["satisfied"] is False


def test_authority_ceiling_requires_model_units_and_nonnegative_limits(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"].update(
        {
            "external_effect_class": "PAID_COMPUTE",
            "required_authority_id": "AUTH-B002",
        }
    )
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    authority = tmp_path / "artifacts" / "authorities" / "AUTH-B002.json"
    authority.parent.mkdir(parents=True)
    base = {
        "authority_id": "AUTH-B002",
        "task_id": "B002",
        "external_effect_class": "PAID_COMPUTE",
        "status": "AUTHORIZED_CANONICAL",
        "scope": {"executor": "fixture"},
    }
    for ceiling in [
        {},
        {"cost_model": "fixed-cap", "limits": []},
        {"cost_model": "fixed-cap", "limits": [{"resource": "cost", "max": -1, "unit": "USD"}]},
        {"cost_model": "fixed-cap", "limits": [{"resource": "cost", "max": 1, "unit": ""}]},
    ]:
        authority.write_text(
            json.dumps(
                {
                    **base,
                    "cost_resource_ceiling": ceiling,
                }
            ),
            encoding="utf-8",
        )
        result = evaluate_task_snapshot(
            "B002",
            repository_root=tmp_path,
            catalog_path=catalog_path,
            canonical_main=_CANONICAL_MAIN,
        )
        assert result["eligible"] is False
        assert result["authority_result"]["satisfied"] is False


def test_tasks_file_symlink_outside_repository_is_rejected(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    tasks_path = tmp_path / "specs" / "002-code-model-supremacy-foundation" / "tasks.md"
    outside = tmp_path.parent / f"{tmp_path.name}-outside-tasks.md"
    outside.write_text(
        "- [x] **B001 Root task.**\n- [ ] **B002 Target task.**\n",
        encoding="utf-8",
    )
    tasks_path.unlink()
    _symlink_or_skip(tasks_path, outside)

    with pytest.raises(QualificationError) as captured:
        load_task_catalog(catalog_path, repository_root=tmp_path)
    assert captured.value.code == "task_gate.tasks_file_invalid"


def test_external_symlink_cannot_satisfy_literal_required_evidence(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    canonical_evidence = tmp_path / "evidence" / "B001.md"
    outside = tmp_path.parent / f"{tmp_path.name}-outside-evidence.md"
    outside.write_text("external evidence\n", encoding="utf-8")
    canonical_evidence.unlink()
    _symlink_or_skip(canonical_evidence, outside)

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["evidence_present"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]


def test_external_symlink_cannot_satisfy_globbed_required_evidence(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B001"]["evidence_outputs"] = ["evidence/*.md"]
    catalog_path.write_text(json.dumps(data), encoding="utf-8")

    canonical_evidence = tmp_path / "evidence" / "B001.md"
    outside = tmp_path.parent / f"{tmp_path.name}-outside-glob-evidence.md"
    outside.write_text("external evidence\n", encoding="utf-8")
    canonical_evidence.unlink()
    _symlink_or_skip(canonical_evidence, outside)

    result = evaluate_task_snapshot(
        "B002",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["evidence_present"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]


def test_b007_fails_closed_when_b006_candidate_outputs_are_missing(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text(
        "- [x] **B006 Predecessor task.**\n- [ ] **B007 Successor task.**\n",
        encoding="utf-8",
    )
    evidence = (
        tmp_path / "evidence" / "mstr-000b" / "candidates" / "B006-candidate-reconciliation.md"
    )
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
            "B006": {
                "canonical_state": "COMPLETE_CANONICAL",
                "closeout_rule": {"require_all_outputs": True},
                "prerequisites": [],
                "outputs": ["artifacts/candidates/*.json"],
                "evidence_outputs": ["evidence/mstr-000b/candidates/*.md"],
            },
            "B007": {
                "canonical_state": "PENDING",
                "prerequisites": ["B006"],
                "evidence_outputs": [],
            },
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    result = evaluate_task_snapshot(
        "B007", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )

    assert result["eligible"] is False
    assert "prerequisite.unsatisfied:B006" in result["reasons"]
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert "missing:artifacts/candidates/*.json" in predecessor["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b014_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B014", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b015_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B015", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b016_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B016", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b017_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B017", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b018_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B018", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b019_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B019", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B018")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []
    validate_instance("mstr-task-eligibility-v0", result)


def test_b020_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B020", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b014_closeout_does_not_change_b011_exact_authority_identity() -> None:
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["state_consistency_result"]["observed_state"] == "PENDING"
    assert result["authority_result"]["required"] is True
    assert result["authority_result"]["satisfied"] is True
    assert result["authority_result"]["authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    validate_instance("mstr-task-eligibility-v0", result)


def test_b021_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B021", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b022_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B022", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    validate_instance("mstr-task-eligibility-v0", result)


def test_b023_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B023", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A006",
        "A014",
        "B002",
        "B022",
    }
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_b024_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B024", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B023")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b026_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "B022",
        "B024",
        "B025",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL" for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_b027_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B027", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B026")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b027_closeout_is_satisfied_for_b031_prerequisite() -> None:
    result = evaluate_task_snapshot("B031", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B027")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b023_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B023-verifier-health-implementation.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #133" in evidence
    assert "`da0480c0eb39e4097cb2d3fd3337a7fc49ab75dc`" in evidence
    assert "`f71a15f967250c5c523749be9f9f3066feccb902`" in evidence
    assert "ENTRY_GATE_TASK = B023" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = fdca133e53a47b8966faef172812da58503576a0" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33526148972", "33527138891", "33528450915", "33528911288"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "review `5080178013` — NO ISSUES FOUND" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "VERIFIER_SUBPROCESS_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


def test_b024_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2] / "evidence" / "mstr-000b" / "B024-test-curriculum.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #135" in evidence
    assert "`fc6b64fc68d629900b414e6e4ea01c5bdc0eaee2`" in evidence
    assert "`138a2c2c1d86c050db79e3190ab24d7c1052fe44`" in evidence
    assert "ENTRY_GATE_TASK = B024" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 1ffa71c94bda161ec7be7784de3a6a4be81570ad" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33553919725", "33554572587", "33559716801", "33560182387"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "CodeRabbit comment `5498547347`" in evidence
    assert "e2805914-59c9-4314-99e2-04bcb3ed5892" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "TEST_GENERATION_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


def test_b026_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2] / "evidence" / "mstr-000b" / "B026-research-ladder.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #137" in evidence
    assert "`ba672f8eaaa9fe96e9ffdcba39e10f6d4123e421`" in evidence
    assert "`1aed67793fa14e6c9a7bbe4067ad521d16617b26`" in evidence
    assert "ENTRY_GATE_TASK = B026" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 823cd7ec3b4c537876a0795d0f0f8d4bd75acd85" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33677458758", "33678090319", "33682188378", "33683456723"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "CodeRabbit comment `5516237548`" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "RESEARCH_CAMPAIGN_EXECUTION = NONE" in evidence
    assert "VERIFIER_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


def test_b027_closeout_provenance_and_authority_boundary() -> None:
    evidence = (
        Path(__file__).resolve().parents[2] / "evidence" / "mstr-000b" / "B027-ladder-pilot.md"
    ).read_text(encoding="utf-8")

    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #141" in evidence
    assert "`b5e152552f3b840fd74f2fe9b092eca17b56a91d`" in evidence
    assert "`f667226dbf6cd380fefef5ff90fbc14eb1de3630`" in evidence
    assert "ENTRY_GATE_TASK = B027" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 312d40eee8400a0dab94633f891b206f66a82855" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    for run_id in ("33757330474", "33758435956", "33760082781", "33761211923"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "NO ACTIONABLE COMMENTS" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "RESEARCH_CAMPAIGN_EXTERNAL_EFFECT = NONE" in evidence
    assert "VERIFIER_EXTERNAL_EFFECT = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


def test_b025_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B025", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B014")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b025_prerequisite_remains_recorded_after_b026_closeout() -> None:
    result = evaluate_task_snapshot("B026", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert "task.already_terminal" in result["reasons"]
    predecessor = next(item for item in result["prerequisite_results"] if item["task_id"] == "B025")
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True
    validate_instance("mstr-task-eligibility-v0", result)


def test_b028_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B028", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "B009",
        "B014",
        "B022",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL" for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_external_prerequisite_missing_state_evidence_fails_closed(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text("- [ ] **B001 Target task.**\n", encoding="utf-8")
    a_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    a_tasks.parent.mkdir(parents=True)
    a_tasks.write_text("- [x] **A006 External task.**\n", encoding="utf-8")
    evidence = tmp_path / "evidence" / "mstr-000a" / "A006-finalizer.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text("# A006\n\n**Task:** `A006`\n**State:** `PENDING`\n", encoding="utf-8")
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
                "canonical_state": "PENDING",
                "prerequisites": ["A006"],
                "evidence_outputs": [],
            }
        },
        "external_prerequisites": {
            "A006": {
                "workstream_id": "MSTR-000A",
                "task_identity": "MSTR-000A / A006",
                "tasks_file": "specs/001-agent-harness-verified-loop-foundation/tasks.md",
                "state_evidence": "evidence/mstr-000a/A006-finalizer.md",
                "evidence_outputs": ["evidence/mstr-000a/A006-finalizer.md"],
                "required_state": "COMPLETE_CANONICAL",
            }
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["observed_state"] is None
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_state_unproven" in predecessor["reasons"]


def test_external_prerequisite_mismatched_evidence_identity_fails_closed(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "specs" / "002-code-model-supremacy-foundation"
    tasks_dir.mkdir(parents=True)
    (tasks_dir / "tasks.md").write_text("- [ ] **B001 Target task.**\n", encoding="utf-8")
    a_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    a_tasks.parent.mkdir(parents=True)
    a_tasks.write_text("- [x] **A006 External task.**\n", encoding="utf-8")
    evidence = tmp_path / "evidence" / "mstr-000a" / "A006-finalizer.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        "# Wrong task\n\n**Task:** `A014`\n**State:** `COMPLETE_CANONICAL`\n", encoding="utf-8"
    )
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
                "canonical_state": "PENDING",
                "prerequisites": ["A006"],
                "evidence_outputs": [],
            }
        },
        "external_prerequisites": {
            "A006": {
                "workstream_id": "MSTR-000A",
                "task_identity": "MSTR-000A / A006",
                "tasks_file": "specs/001-agent-harness-verified-loop-foundation/tasks.md",
                "state_evidence": "evidence/mstr-000a/A006-finalizer.md",
                "evidence_outputs": ["evidence/mstr-000a/A006-finalizer.md"],
                "required_state": "COMPLETE_CANONICAL",
            }
        },
    }
    catalog_path = tmp_path / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["observed_state"] == "COMPLETE_CANONICAL"
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_identity_unproven" in predecessor["reasons"]


def test_unknown_external_prerequisite_still_fails_closed(tmp_path: Path) -> None:
    catalog_path = _write_minimal_catalog(tmp_path, b001_checked=True)
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    data["tasks"]["B002"]["prerequisites"] = ["A999"]
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    result = evaluate_task_snapshot(
        "B002", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    assert result["eligible"] is False
    assert result["semantic_checks"]["prerequisite_set_complete"] is False
    assert result["prerequisite_results"][0]["reasons"] == ["prerequisite.missing_task_binding"]


def _write_external_binding_fixture(root: Path, evidence_text: str) -> Path:
    target_tasks = root / "specs" / "002-code-model-supremacy-foundation" / "tasks.md"
    target_tasks.parent.mkdir(parents=True)
    target_tasks.write_text("- [ ] **B001 Target task.**\n", encoding="utf-8")
    external_tasks = root / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.parent.mkdir(parents=True)
    external_tasks.write_text("- [x] **A006 External task.**\n", encoding="utf-8")
    evidence = root / "evidence" / "mstr-000a" / "A006-finalizer.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(evidence_text, encoding="utf-8")
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
                "canonical_state": "PENDING",
                "prerequisites": ["A006"],
                "evidence_outputs": [],
            }
        },
        "external_prerequisites": {
            "A006": {
                "workstream_id": "MSTR-000A",
                "task_identity": "MSTR-000A / A006",
                "tasks_file": "specs/001-agent-harness-verified-loop-foundation/tasks.md",
                "state_evidence": "evidence/mstr-000a/A006-finalizer.md",
                "evidence_outputs": ["evidence/mstr-000a/A006-finalizer.md"],
                "required_state": "COMPLETE_CANONICAL",
            }
        },
    }
    catalog_path = root / "configs" / "task-gate" / "mstr-000b.json"
    catalog_path.parent.mkdir(parents=True)
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    return catalog_path


def test_external_prerequisite_split_identity_and_state_records_fail_closed(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `A006`\n**State:** `PENDING`\n"
        "**Task:** `MSTR-000A / A014`\n**State:** `COMPLETE_CANONICAL`\n",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["observed_state"] is None
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_identity_unproven" in predecessor["reasons"]
    assert "prerequisite.external_state_unproven" in predecessor["reasons"]


def test_external_prerequisite_duplicate_identity_records_fail_closed(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `A006`\n**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_identity_unproven" in predecessor["reasons"]


def test_external_prerequisite_fully_qualified_identity_is_accepted(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is True
    assert predecessor["satisfied"] is True


def test_external_prerequisite_legacy_task_identity_requires_bound_namespace(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )
    assert result["eligible"] is True

    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    binding = payload["external_prerequisites"]["A006"]
    binding["state_evidence"] = "evidence/mstr-000b/A006-finalizer.md"
    binding["evidence_outputs"] = ["evidence/mstr-000b/A006-finalizer.md"]
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(QualificationError) as captured:
        load_task_catalog(catalog_path, repository_root=tmp_path)
    assert captured.value.code == "task_gate.catalog_external_workstream_evidence"


def test_external_prerequisite_workstream_tasks_file_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["external_prerequisites"]["A006"]["tasks_file"] = (
        "specs/002-code-model-supremacy-foundation/tasks.md"
    )
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(QualificationError) as captured:
        load_task_catalog(catalog_path, repository_root=tmp_path)
    assert captured.value.code == "task_gate.catalog_external_workstream_tasks_file"


def test_external_prerequisite_task_identity_binding_must_be_fully_qualified(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    payload["external_prerequisites"]["A006"]["task_identity"] = "A006"
    catalog_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(QualificationError) as captured:
        load_task_catalog(catalog_path, repository_root=tmp_path)
    assert captured.value.code == "task_gate.catalog_external_task_identity"


def test_external_prerequisite_missing_checklist_is_reported_unverifiable(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.unlink()

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]
    assert "prerequisite.state_checkbox_conflict" not in predecessor["reasons"]


def test_external_prerequisite_unchecked_checklist_remains_checkbox_conflict(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text("- [ ] **A006 External task.**\n", encoding="utf-8")

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert "prerequisite.state_checkbox_conflict" in predecessor["reasons"]
    assert "prerequisite.external_checkbox_unverifiable" not in predecessor["reasons"]


def test_external_prerequisite_checklist_title_does_not_require_trailing_period(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text("- [x] **A006 Implement boundary**\n", encoding="utf-8")

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


def test_external_prerequisite_non_utf8_checklist_fails_closed_without_exception(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_bytes(b"- [x] **A006 External task**\n\xff\xfe")

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_non_utf8_state_evidence_fails_closed_without_exception(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    evidence = tmp_path / "evidence" / "mstr-000a" / "A006-finalizer.md"
    evidence.write_bytes(b"**Task:** `MSTR-000A / A006`\n\xff\xfe")

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert "prerequisite.external_identity_unproven" in predecessor["reasons"]
    assert "prerequisite.external_state_unproven" in predecessor["reasons"]


def test_external_prerequisite_fenced_checklist_example_is_ignored(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        "```markdown\n- [x] **A006 Example only.**\n```\n",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_fenced_state_evidence_example_is_ignored(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "~~~text\n**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n~~~\n",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert "prerequisite.external_identity_unproven" in predecessor["reasons"]
    assert "prerequisite.external_state_unproven" in predecessor["reasons"]


def test_external_prerequisite_fenced_examples_do_not_duplicate_canonical_records(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "```markdown\n"
        "**Task:** `MSTR-000A / A006`\n"
        "**State:** `PENDING`\n"
        "```\n"
        "**Task:** `MSTR-000A / A006`\n"
        "**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        "~~~markdown\n- [ ] **A006 Example only.**\n~~~\n- [x] **A006 Canonical task**\n",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


def test_external_prerequisite_crlf_fenced_checklist_example_is_ignored(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_bytes(b"```markdown\r\n- [x] **A006 Example only.**\r\n```\r\n")

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_emphasized_duplicate_checklist_row_fails_closed(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        "- [x] **A006 Canonical task.**\n- [ ] **A006 Duplicate with *emphasis*.**\n",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_literal_directory_evidence_output_fails_closed(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    directory_output = "evidence/mstr-000a/supporting-artifact"
    data["external_prerequisites"]["A006"]["evidence_outputs"].append(directory_output)
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    (tmp_path / directory_output).mkdir()

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert f"missing:{directory_output}" in predecessor["reasons"]


def test_external_prerequisite_glob_directory_evidence_output_fails_closed(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    glob_output = "evidence/mstr-000a/supporting-*"
    data["external_prerequisites"]["A006"]["evidence_outputs"].append(glob_output)
    catalog_path.write_text(json.dumps(data), encoding="utf-8")
    (tmp_path / "evidence" / "mstr-000a" / "supporting-directory").mkdir()

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["evidence_present"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.required_artifact_missing" in predecessor["reasons"]
    assert f"missing:{glob_output}" in predecessor["reasons"]


def test_external_prerequisite_literal_t_fence_does_not_hide_duplicate_row(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        "- [x] **A006 Canonical row.**\nt```\n- [ ] **A006 Conflicting duplicate.**\n",
        encoding="utf-8",
    )
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


def test_external_prerequisite_tab_indented_fence_still_hides_fenced_duplicate(
    tmp_path: Path,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        "- [x] **A006 Canonical row.**\n\t```\n- [ ] **A006 Fenced duplicate.**\n\t```\n",
        encoding="utf-8",
    )
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is True
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


@pytest.mark.parametrize(
    ("tasks_text", "evidence_text", "expected_reason"),
    [
        (
            "- [x] **A006\nExternal task.**\n",
            "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
            "prerequisite.external_checkbox_unverifiable",
        ),
        (
            "- [x] **A006 External task.**\n",
            "**Task:**\n`MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
            "prerequisite.external_identity_unproven",
        ),
        (
            "- [x] **A006 External task.**\n",
            "**Task:** `MSTR-000A / A006`\n**State:**\n`COMPLETE_CANONICAL`\n",
            "prerequisite.external_state_unproven",
        ),
    ],
)
def test_external_prerequisite_newline_split_records_fail_closed(
    tmp_path: Path,
    tasks_text: str,
    evidence_text: str,
    expected_reason: str,
) -> None:
    catalog_path = _write_external_binding_fixture(tmp_path, evidence_text)
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(tasks_text, encoding="utf-8")
    result = evaluate_task_snapshot(
        "B001", repository_root=tmp_path, catalog_path=catalog_path, canonical_main=_CANONICAL_MAIN
    )
    predecessor = result["prerequisite_results"][0]
    assert result["eligible"] is False
    assert predecessor["satisfied"] is False
    assert expected_reason in predecessor["reasons"]


_SPLITLINES_NON_CRLF_BOUNDARIES = [
    "\v",
    "\f",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x85",
    "\u2028",
    "\u2029",
]


@pytest.mark.parametrize("separator", _SPLITLINES_NON_CRLF_BOUNDARIES)
def test_external_prerequisite_splitlines_boundary_duplicate_rows_fail_closed(
    tmp_path: Path,
    separator: str,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        f"- [x] **A006 Canonical row.**{separator}- [ ] **A006 Conflicting duplicate.**",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is False
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is False
    assert "prerequisite.external_checkbox_unverifiable" in predecessor["reasons"]


@pytest.mark.parametrize("separator", _SPLITLINES_NON_CRLF_BOUNDARIES)
def test_external_prerequisite_splitlines_boundary_fence_closes_before_canonical_row(
    tmp_path: Path,
    separator: str,
) -> None:
    catalog_path = _write_external_binding_fixture(
        tmp_path,
        "**Task:** `MSTR-000A / A006`\n**State:** `COMPLETE_CANONICAL`\n",
    )
    external_tasks = tmp_path / "specs" / "001-agent-harness-verified-loop-foundation" / "tasks.md"
    external_tasks.write_text(
        f"```{separator}"
        f"- [ ] **A006 Fenced example.**{separator}"
        f"```{separator}"
        "- [x] **A006 Canonical row.**",
        encoding="utf-8",
    )

    result = evaluate_task_snapshot(
        "B001",
        repository_root=tmp_path,
        catalog_path=catalog_path,
        canonical_main=_CANONICAL_MAIN,
    )

    assert result["eligible"] is True
    predecessor = result["prerequisite_results"][0]
    assert predecessor["satisfied"] is True
    assert predecessor["reasons"] == []


def test_b029_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B029", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A005",
        "A006",
        "A008",
        "A010",
        "B020",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL" for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)


def test_b030_is_terminal_after_canonical_closeout() -> None:
    result = evaluate_task_snapshot("B030", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert result["state_consistency_result"]["observed_state"] == "COMPLETE_CANONICAL"
    assert result["state_consistency_result"]["satisfied"] is True
    assert result["authority_result"]["required"] is False
    assert "task.already_terminal" in result["reasons"]
    assert {item["task_id"] for item in result["prerequisite_results"]} == {
        "A007",
        "A008",
        "A009",
        "B024",
        "B025",
    }
    assert all(
        item["observed_state"] == "COMPLETE_CANONICAL" for item in result["prerequisite_results"]
    )
    assert all(item["evidence_present"] is True for item in result["prerequisite_results"])
    assert all(item["satisfied"] is True for item in result["prerequisite_results"])
    validate_instance("mstr-task-eligibility-v0", result)
