from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

from mstr_qualify.errors import SchemaValidationError

ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "artifacts" / "results" / "research" / "B027"


def _json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_b027_pilot_proves_promotion_then_early_discard() -> None:
    ledger = _json(RESULT_ROOT / "campaign-ledger.json")
    sequence = ledger["sequence"]
    assert isinstance(sequence, list)
    assert [row["decision"] for row in sequence] == ["PROMOTE", "STOP"]
    assert [row["level"] for row in sequence] == [
        "L0_CONTRACT_SMOKE",
        "L1_CODE_PROXY",
    ]
    assert sequence[1]["early_discard_gate"] == "code_proxy_thresholds"
    assert ledger["levels_not_executed"] == [
        "L2_EXECUTABLE_REPO",
        "L3_DIRECTION_TO_DONE",
        "L4_Q4_UNIVERSAL_LAPTOP",
    ]
    assert ledger["campaign_result"] == "QUALIFIED_PROMOTION_AND_EARLY_DISCARD"


def test_b027_registry_records_are_content_bound_and_zero_external_effect() -> None:
    ledger = _json(RESULT_ROOT / "campaign-ledger.json")
    sequence = ledger["sequence"]
    assert isinstance(sequence, list)
    effects = ledger["governed_effects"]
    assert isinstance(effects, dict)
    assert not any(effects.values())
    for row in sequence:
        assert isinstance(row, dict)
        path = RESULT_ROOT / "registry" / f"{row['experiment_id']}.json"
        record = _json(path)
        assert _sha256(path) == row["record_sha256"]
        assert record["governed_effects"] == effects
        assert record["external_effect_authority"] is None
        cost = record["aggregate_resource_cost"]
        assert isinstance(cost, dict)
        assert cost["paid_cost_usd"] == 0
        results = record["material_results"]
        assert isinstance(results, list) and len(results) == 1
        result = results[0]
        assert isinstance(result, dict)
        assert result["model_execution_count_or_na"] == 0
        assert result["network_model_or_teacher_call_count_or_na"] == 0
        resource = result["resource_cost"]
        assert isinstance(resource, dict)
        assert resource["network_bytes_or_na"] == 0


def test_b027_l1_consumes_exact_l0_and_stops_on_declared_gate() -> None:
    ledger = _json(RESULT_ROOT / "campaign-ledger.json")
    sequence = ledger["sequence"]
    assert isinstance(sequence, list) and len(sequence) == 2
    l0_row, l1_row = sequence
    assert isinstance(l0_row, dict) and isinstance(l1_row, dict)
    l0 = _json(RESULT_ROOT / "registry" / f"{l0_row['experiment_id']}.json")
    l1 = _json(RESULT_ROOT / "registry" / f"{l1_row['experiment_id']}.json")
    predecessor = l1["predecessor_promotion"]
    assert isinstance(predecessor, dict)
    assert predecessor["experiment_id"] == l0["experiment_id"]
    assert predecessor["experiment_record_sha256"] == l0_row["record_sha256"]
    assert l1["parent_identity"] == l0["promoted_result_id_or_na"]
    gates = l1["hard_gate_results"]
    assert isinstance(gates, list)
    gate = next(
        row
        for row in gates
        if isinstance(row, dict) and row["gate_id"] == "code_proxy_thresholds"
    )
    assert gate["status"] == "FAIL"
    assert l1["promotion_decision"] == "STOP"
    assert l1["promoted_result_id_or_na"] == "N/A"
    assert not (RESULT_ROOT / "registry" / "b027-l2.json").exists()


def test_b027_uses_one_immutable_evaluator_identity() -> None:
    ledger = _json(RESULT_ROOT / "campaign-ledger.json")
    evaluator = ledger["frozen_evaluation_identity"]
    assert isinstance(evaluator, str) and evaluator.startswith("sha256:")
    sequence = ledger["sequence"]
    assert isinstance(sequence, list)
    for row in sequence:
        assert isinstance(row, dict)
        record = _json(
            RESULT_ROOT / "registry" / f"{row['experiment_id']}.json"
        )
        assert record["frozen_evaluation_identity"] == evaluator


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def test_b027_canonical_validation_fails_closed_without_mutating_refs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clone = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(ROOT), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    candidate_head = _git(ROOT, "rev-parse", "HEAD")
    canonical_entry = "312d40eee8400a0dab94633f891b206f66a82855"
    assert candidate_head != canonical_entry
    _git(clone, "checkout", "--detach", candidate_head)
    _git(clone, "update-ref", "refs/heads/main", canonical_entry)
    _git(clone, "update-ref", "refs/remotes/origin/main", canonical_entry)

    spec = importlib.util.spec_from_file_location(
        "b027_ladder_pilot_regression",
        ROOT / "scripts" / "research" / "b027_ladder_pilot.py",
    )
    assert spec is not None and spec.loader is not None
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    monkeypatch.setattr(pilot, "ROOT", clone)
    monkeypatch.setattr(
        pilot,
        "RESULT_ROOT",
        clone / "artifacts" / "results" / "research" / "B027",
    )

    record = json.loads(
        (
            clone
            / "artifacts"
            / "results"
            / "research"
            / "B027"
            / "registry"
            / "b027-l0-contract-smoke.json"
        ).read_text(encoding="utf-8")
    )
    before = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}")
        for ref in ("refs/heads/main", "refs/remotes/origin/main")
    }
    with pytest.raises(SchemaValidationError):
        pilot._validate_record_canonical(record)
    after = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}")
        for ref in ("refs/heads/main", "refs/remotes/origin/main")
    }
    assert after == before
    assert before == {
        "refs/heads/main": canonical_entry,
        "refs/remotes/origin/main": canonical_entry,
    }


def test_b027_harness_never_rewrites_canonical_refs(tmp_path: Path) -> None:
    source = (ROOT / "scripts" / "research" / "b027_ladder_pilot.py").read_text(
        encoding="utf-8"
    )
    assert "update-ref" not in source

    clone = tmp_path / "run-repo"
    subprocess.run(
        ["git", "clone", "--no-hardlinks", str(ROOT), str(clone)],
        check=True,
        capture_output=True,
        text=True,
    )
    candidate_head = _git(ROOT, "rev-parse", "HEAD")
    canonical_entry = "312d40eee8400a0dab94633f891b206f66a82855"
    assert candidate_head != canonical_entry
    _git(clone, "checkout", "-B", "test-b027-run", candidate_head)
    _git(clone, "branch", "--force", "main", canonical_entry)
    _git(clone, "branch", "--force", "--remotes", "origin/main", canonical_entry)
    _git(clone, "config", "user.name", "B027 Contract Test")
    _git(clone, "config", "user.email", "b027-contract-test@example.invalid")

    refs = ("refs/heads/main", "refs/remotes/origin/main")
    before = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}") for ref in refs
    }

    spec = importlib.util.spec_from_file_location(
        "b027_ladder_pilot_run_regression",
        clone / "scripts" / "research" / "b027_ladder_pilot.py",
    )
    assert spec is not None and spec.loader is not None
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)
    pilot.run()

    after = {
        ref: _git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}") for ref in refs
    }
    assert after == before
    assert before == {
        "refs/heads/main": canonical_entry,
        "refs/remotes/origin/main": canonical_entry,
    }
