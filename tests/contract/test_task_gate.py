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


def test_b008_is_eligible_after_b007_closeout() -> None:
    result = evaluate_task_snapshot("B008", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is True
    assert result["reasons"] == []
    assert result["prerequisite_results"][0]["task_id"] == "B007"
    assert result["prerequisite_results"][0]["satisfied"] is True
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


def test_explicitly_blocked_task_never_becomes_eligible() -> None:
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)

    assert result["eligible"] is False
    assert "task.blocked" in result["reasons"]
    assert "task.unresolved_binding" in result["reasons"]


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


def test_b011_stays_weight_access_fail_closed_until_b010_resolution() -> None:
    catalog = load_task_catalog()
    node = catalog.nodes["B011"]
    assert node["canonical_state"] == "BLOCKED"
    assert node["external_effect_class"] == "MODEL_WEIGHT_ACCESS"
    assert node["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)
    assert result["eligible"] is False
    assert result["authority_result"]["required"] is True
    assert result["authority_result"]["satisfied"] is False


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
