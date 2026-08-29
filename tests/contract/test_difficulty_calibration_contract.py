from __future__ import annotations

import copy
import json
import math
from pathlib import Path

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / "mstr-difficulty-calibration-v0.json"
INVALID = (
    ROOT / "tests" / "fixtures" / "schemas" / "invalid" / "mstr-difficulty-calibration-v0.json"
)


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def errors(value: object) -> tuple[str, ...]:
    return validation_errors("mstr-difficulty-calibration-v0", value)


def test_b020_valid_fixture_passes() -> None:
    validate_instance("mstr-difficulty-calibration-v0", fixture())


def test_b020_invalid_fixture_fails_closed() -> None:
    assert errors(json.loads(INVALID.read_text(encoding="utf-8")))


def test_b020_success_count_cannot_exceed_attempt_count() -> None:
    value = fixture()
    value["attempt_count"] = 3
    value["success_count"] = 4
    assert any("cannot exceed attempt_count" in item for item in errors(value))


def test_b020_failure_distribution_exactly_covers_failed_attempts() -> None:
    value = fixture()
    value["failure_distribution"][0]["count"] = 1
    assert any("exactly cover attempt_count - success_count" in item for item in errors(value))


def test_b020_duplicate_failure_class_fails_closed() -> None:
    value = fixture()
    duplicate = copy.deepcopy(value["failure_distribution"][0])
    duplicate["count"] = 1
    value["failure_distribution"].append(duplicate)
    value["failure_distribution"][1]["count"] = 0
    assert any("duplicate failure_class" in item for item in errors(value))


def test_b020_harness_identity_must_match_student_identity() -> None:
    value = fixture()
    value["harness_profile_id"] = "different-harness"
    assert any(
        "must match student_model_identity.harness_profile_id" in item for item in errors(value)
    )


def test_b020_sampling_identity_must_match_student_identity() -> None:
    value = fixture()
    value["sampling_identity"] = "different-sampling"
    assert any(
        "must match student_model_identity.sampling_identity" in item for item in errors(value)
    )


def test_b020_contract_does_not_freeze_probability_thresholds() -> None:
    for difficulty_class in (
        "TOO_EASY",
        "LEARNABLE_FRONTIER",
        "HARD_FRONTIER",
        "CURRENTLY_UNPRODUCTIVE",
        "INVALID",
    ):
        value = fixture()
        value["difficulty_class"] = difficulty_class
        value["estimated_solve_probability"] = 0.5
        assert not errors(value), difficulty_class


def test_b020_non_finite_probability_fails_closed() -> None:
    value = fixture()
    value["estimated_solve_probability"] = math.nan
    assert any("must be finite" in item for item in errors(value))


def test_b020_non_finite_structural_numeric_feature_fails_closed() -> None:
    for non_finite in (math.nan, math.inf, -math.inf):
        value = fixture()
        value["structural_features"]["numeric_probe"] = non_finite
        assert any("numeric value must be finite" in item for item in errors(value))


def test_b020_machine_readable_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B020-difficulty-contract.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B020" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = ef90e96ba3d4e2c253987d1d104e0de26ce93529" in evidence
    assert "ENTRY_GATE_RUN = 33198484632" in evidence
    assert "ENTRY_GATE_JOB = 98941644785" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B020_CALIBRATION_EXECUTION = NONE" in evidence
    assert "B021_FRONTIER_SAMPLER_EXECUTION = NONE" in evidence


def test_b020_canonical_closeout_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B020-difficulty-contract.md").read_text(
        encoding="utf-8"
    )
    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #81" in evidence
    assert "`189509470eae10f1080938b0b2b873f375842f35`" in evidence
    assert "`f5a4892bff6bc20e376efcaa8f554c15ac88bca8`" in evidence
    for run_id in (
        "33199352285",
        "33200021831",
        "33234320679",
        "33234412303",
        "33234492918",
        "33234636531",
    ):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B020_CALIBRATION_EXECUTION = NONE" in evidence
    assert "B021_FRONTIER_SAMPLER_EXECUTION = NONE" in evidence
