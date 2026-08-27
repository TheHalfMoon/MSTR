from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.schemas import validate_instance

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "mstr-000b" / "B001" / "task-node-fail-closed.json"
VALID_SCHEMA_FIXTURES = ROOT / "tests" / "fixtures" / "schemas" / "valid"

AUTHORITY_GATED_CLASSES = {
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
}


def _fixtures() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _valid_fixture(schema_name: str) -> dict[str, Any]:
    return json.loads((VALID_SCHEMA_FIXTURES / f"{schema_name}.json").read_text(encoding="utf-8"))


def test_every_authority_gated_class_has_a_missing_authority_fixture() -> None:
    fixture = _fixtures()
    assert set(fixture["authority_gated_classes"]) == AUTHORITY_GATED_CLASSES
    records = fixture["authority_missing"]
    assert {record["external_effect_class"] for record in records} == AUTHORITY_GATED_CLASSES


@pytest.mark.parametrize("external_effect_class", sorted(AUTHORITY_GATED_CLASSES))
def test_authority_gated_task_without_authority_fails_closed(
    external_effect_class: str,
) -> None:
    records = _fixtures()["authority_missing"]
    record = next(
        item for item in records if item["external_effect_class"] == external_effect_class
    )
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-node-v0", record, schema_dir=ROOT / "schemas")


def test_candidate_dependent_task_without_pool_requirement_fails_closed() -> None:
    record = _fixtures()["candidate_pool_missing"]
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-node-v0", record, schema_dir=ROOT / "schemas")


def test_closeout_rule_rejects_nonterminal_task_state() -> None:
    record = _valid_fixture("mstr-task-node-v0")
    record["closeout_rule"]["terminal_states"] = ["ACTIVE"]
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-node-v0", record, schema_dir=ROOT / "schemas")


def test_eligibility_result_requires_task_node_digest_binding() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    del record["task_node_sha256"]
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_eligible_result_cannot_hide_a_failed_authority_check() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["authority_result"]["satisfied"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_eligible_result_requires_prerequisite_evidence() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["prerequisite_results"][0]["evidence_present"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_eligible_result_cannot_be_superseded() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["supersession_result"].update(
        {"superseded": True, "superseded_by": ["B999"], "satisfied": True}
    )
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_eligible_result_rejects_failed_cross_contract_semantic_check() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["prerequisite_results"][0]["observed_state"] = "PENDING"
    record["semantic_checks"]["prerequisite_states_satisfied"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_required_candidate_pool_must_bind_observed_pool_identity_when_eligible() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["candidate_pool_result"].update(
        {"required": True, "requirement_id": "candidate-pool-required", "observed_pool_id": None}
    )
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_missing_required_candidate_pool_is_representable_when_ineligible() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["eligible"] = False
    record["candidate_pool_result"].update(
        {
            "required": True,
            "requirement_id": "candidate-pool-required",
            "observed_pool_id": None,
            "satisfied": False,
            "reasons": ["required candidate pool is unavailable"],
        }
    )
    record["semantic_checks"]["candidate_pool_requirement_complete"] = False
    record["reasons"] = ["candidate-pool requirement is not satisfied"]
    validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_ineligible_result_requires_a_reason() -> None:
    record = _valid_fixture("mstr-task-eligibility-v0")
    record["eligible"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")
