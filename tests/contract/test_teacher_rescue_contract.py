from __future__ import annotations

import copy
import json
from pathlib import Path

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-teacher-rescue-record-v0.json"
)
INVALID = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "invalid"
    / "mstr-teacher-rescue-record-v0.json"
)


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def errors(value: object) -> tuple[str, ...]:
    return validation_errors("mstr-teacher-rescue-record-v0", value)


def test_b019_valid_fixture_passes() -> None:
    validate_instance("mstr-teacher-rescue-record-v0", fixture())


def test_b019_invalid_unresolved_output_rights_fails_closed() -> None:
    assert errors(json.loads(INVALID.read_text(encoding="utf-8")))


def test_b019_provenance_must_exactly_cover_outputs() -> None:
    value = fixture()
    value["output_provenance"] = []
    assert any("exactly cover teacher output ids" in item for item in errors(value))


def test_b019_rights_must_exactly_cover_outputs() -> None:
    value = fixture()
    value["output_rights_decisions"] = []
    assert any("exactly cover teacher output ids" in item for item in errors(value))


def test_b019_duplicate_output_id_fails_closed() -> None:
    value = fixture()
    value["teacher_outputs"].append(copy.deepcopy(value["teacher_outputs"][0]))
    assert any("duplicate output_id" in item for item in errors(value))


def test_b019_required_execution_must_be_independently_bound() -> None:
    value = fixture()
    value["independent_execution_results"] = []
    assert any("execution-required teacher output ids" in item for item in errors(value))


def test_b019_solution_and_test_outputs_cannot_opt_out_of_execution() -> None:
    for output_kind in ("SOLUTION", "TEST"):
        value = fixture()
        value["teacher_outputs"][0]["output_kind"] = output_kind
        value["teacher_outputs"][0]["execution_required"] = False
        value["independent_execution_results"] = []
        assert errors(value)


def test_b019_admit_rejects_failed_execution() -> None:
    value = fixture()
    value["independent_execution_results"][0]["result"] = "FAIL"
    assert errors(value)


def test_b019_admit_rejects_non_sandboxed_execution() -> None:
    value = fixture()
    value["independent_execution_results"][0]["sandboxed"] = False
    assert errors(value)


def test_b019_admit_rejects_contamination() -> None:
    value = fixture()
    value["teacher_outputs"][0]["contamination_status"] = "DETECTED"
    assert errors(value)


def test_b019_admit_requires_healthy_independent_verifier() -> None:
    for field, invalid in (
        ("health_class", "PARTIAL"),
        ("independence", "UNRESOLVED"),
        ("teacher_output_sole_authority", True),
    ):
        value = fixture()
        value["verifier_health"][field] = invalid
        assert errors(value)


def test_b019_reject_requires_reason() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    assert errors(value)


def test_b019_external_effect_requires_existing_authority_identity() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "REMOTE_API"
    value["cost_record"]["network_used"] = True
    value["cost_record"]["model_execution_occurred"] = True
    assert any("external_effect_authority_identity" in item for item in errors(value))


def test_b019_reference_only_cannot_claim_external_effect() -> None:
    value = fixture()
    value["cost_record"]["paid_cost_usd"] = 0.01
    value["cost_record"]["external_effect_authority_identity"] = "authority-fixture"
    assert any("REFERENCE_ONLY" in item for item in errors(value))


def test_b019_remote_api_record_requires_network_and_execution_facts() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "REMOTE_API"
    assert any("REMOTE_API" in item for item in errors(value))


def test_b019_local_model_record_requires_model_execution_fact() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "LOCAL_MODEL"
    assert any("LOCAL_MODEL" in item for item in errors(value))


def test_b019_zero_effect_record_rejects_spurious_authority_identity() -> None:
    value = fixture()
    value["cost_record"]["external_effect_authority_identity"] = "stale-authority"
    assert any("must be null" in item for item in errors(value))


def test_b019_difficulty_and_verifier_authority_remain_external() -> None:
    policy = (ROOT / "docs" / "data" / "TEACHER_RESCUE_POLICY.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        ROOT / "evidence" / "mstr-000b" / "B019-teacher-policy.md"
    ).read_text(encoding="utf-8")
    for text in (policy, evidence):
        assert "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE" in text
        assert "B022_VERIFIER_HEALTH_AUTHORITY = NONE" in text
        assert "MODEL_EXECUTION = NONE" in text
        assert "PAID_MODEL_API = NONE" in text
        assert "WEIGHT_CHANGING_TRAINING = NONE" in text
