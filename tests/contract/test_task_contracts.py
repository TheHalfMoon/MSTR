from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "mstr-000b" / "B001" / "task-node-fail-closed.json"

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


def _fixtures() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


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


def test_eligible_result_cannot_hide_a_failed_authority_check() -> None:
    record = json.loads(
        (
            ROOT
            / "tests"
            / "fixtures"
            / "schemas"
            / "valid"
            / "mstr-task-eligibility-v0.json"
        ).read_text(encoding="utf-8")
    )
    record["authority_result"]["satisfied"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")


def test_ineligible_result_requires_a_reason() -> None:
    record = json.loads(
        (
            ROOT
            / "tests"
            / "fixtures"
            / "schemas"
            / "valid"
            / "mstr-task-eligibility-v0.json"
        ).read_text(encoding="utf-8")
    )
    record["eligible"] = False
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-task-eligibility-v0", record, schema_dir=ROOT / "schemas")
