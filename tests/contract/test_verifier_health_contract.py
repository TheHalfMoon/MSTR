from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.cli import _SCHEMA_VERSION_TO_SCHEMA_NAME
from mstr_qualify.schemas import SCHEMA_FILES, validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_NAME = "mstr-verifier-health-v0"
VERSION = "mstr.verifier-health.v0"
VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / f"{SCHEMA_NAME}.json"
INVALID = ROOT / "tests" / "fixtures" / "schemas" / "invalid" / f"{SCHEMA_NAME}.json"


def fixture() -> dict[str, object]:
    decoded = json.loads(VALID.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def errors(value: object) -> tuple[str, ...]:
    return validation_errors(SCHEMA_NAME, value)


def stage(record: dict[str, object]) -> dict[str, object]:
    stages = record["training_stage_eligibility"]
    assert isinstance(stages, list)
    value = stages[0]
    assert isinstance(value, dict)
    return value


def test_b022_schema_is_registered_for_offline_validation() -> None:
    assert SCHEMA_FILES[SCHEMA_NAME] == "mstr-verifier-health-v0.schema.json"
    assert _SCHEMA_VERSION_TO_SCHEMA_NAME[VERSION] == SCHEMA_NAME


def test_b022_design_and_runtime_schemas_are_byte_identical() -> None:
    runtime = ROOT / "schemas" / "mstr-verifier-health-v0.schema.json"
    design = (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-verifier-health-v0.schema.json"
    )
    assert runtime.read_bytes() == design.read_bytes()


def test_b022_valid_healthy_fixture_passes() -> None:
    validate_instance(SCHEMA_NAME, fixture())


def test_b022_invalid_clean_positive_broken_fixture_fails_closed() -> None:
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    assert errors(invalid)


@pytest.mark.parametrize(
    "field",
    [
        "evaluator_hashes",
        "protected_paths",
        "protected_path_integrity",
        "reference_oracle_status",
        "noop_fail_status",
        "known_bad_fail_status",
        "mutation_results",
        "generated_test_independence",
        "leakage_checks",
        "disagreement_signals",
        "health_class",
        "training_stage_eligibility",
    ],
)
def test_b022_required_verifier_health_surface_fails_closed_when_missing(field: str) -> None:
    record = fixture()
    del record[field]
    assert errors(record)


def test_b022_evaluator_hash_must_be_sha256() -> None:
    record = fixture()
    hashes = record["evaluator_hashes"]
    assert isinstance(hashes, list)
    item = hashes[0]
    assert isinstance(item, dict)
    item["sha256"] = "not-a-sha256"
    assert errors(record)


@pytest.mark.parametrize(
    "health_class",
    ["PARTIAL", "DISAGREEMENT"],
)
def test_b022_partial_or_disagreement_cannot_claim_clean_positive(
    health_class: str,
) -> None:
    record = fixture()
    record["health_class"] = health_class
    assert errors(record)


@pytest.mark.parametrize(
    "health_class",
    ["BROKEN", "LEAKED", "TAMPERED"],
)
def test_b022_blocking_health_classes_require_blocked_stage(
    health_class: str,
) -> None:
    record = fixture()
    record["health_class"] = health_class
    current_stage = stage(record)
    current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
    current_stage["reason_codes"] = ["not-clean-positive"]
    assert errors(record)


@pytest.mark.parametrize(
    "health_class",
    ["PARTIAL", "DISAGREEMENT"],
)
def test_b022_partial_or_disagreement_may_be_research_diagnostic(
    health_class: str,
) -> None:
    record = fixture()
    record["health_class"] = health_class
    current_stage = stage(record)
    current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
    current_stage["reason_codes"] = ["health-below-clean-positive-threshold"]
    validate_instance(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    "health_class",
    ["BROKEN", "LEAKED", "TAMPERED"],
)
def test_b022_blocking_health_classes_may_only_be_blocked(
    health_class: str,
) -> None:
    record = fixture()
    record["health_class"] = health_class
    current_stage = stage(record)
    current_stage["admission_class"] = "BLOCKED"
    current_stage["reason_codes"] = ["verifier-health-blocking"]
    validate_instance(SCHEMA_NAME, record)


def test_b022_non_clean_stage_requires_reason_code() -> None:
    record = fixture()
    record["health_class"] = "PARTIAL"
    current_stage = stage(record)
    current_stage["admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
    assert errors(record)


def test_b022_clean_positive_stage_rejects_reason_codes() -> None:
    record = fixture()
    current_stage = stage(record)
    current_stage["reason_codes"] = ["unexpected"]
    assert errors(record)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("reference_oracle_status", "NOT_APPLICABLE"),
        ("noop_fail_status", "NOT_APPLICABLE"),
        ("known_bad_fail_status", "NOT_APPLICABLE"),
        ("generated_test_independence", "NOT_APPLICABLE"),
    ],
)
def test_b022_explicit_not_applicable_is_supported_where_defined(
    field: str,
    value: str,
) -> None:
    record = fixture()
    record[field] = value
    validate_instance(SCHEMA_NAME, record)


def test_b022_unknown_fields_fail_closed() -> None:
    record = fixture()
    record["training_authorized"] = True
    assert errors(record)


def test_b022_schema_freezes_exact_health_classes() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "mstr-verifier-health-v0.schema.json").read_text(encoding="utf-8")
    )
    assert schema["properties"]["health_class"]["enum"] == [
        "HEALTHY",
        "PARTIAL",
        "DISAGREEMENT",
        "BROKEN",
        "LEAKED",
        "TAMPERED",
    ]


def test_b022_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B022-verifier-health.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B022" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 127fd5fd1a5a6f1843f207a0272664ae8cb129f4" in evidence
    assert "ENTRY_GATE_RUN = 33245383036" in evidence
    assert "ENTRY_GATE_JOB = 99081833546" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "VERIFIER_EVALUATOR_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B023_VERIFIER_HEALTH_EVALUATOR_AUTHORITY = NONE" in evidence
    assert "B024_TEST_GENERATION_CURRICULUM_AUTHORITY = NONE" in evidence


def test_b022_fixture_mutations_do_not_change_input_helper() -> None:
    first = fixture()
    second = copy.deepcopy(first)
    second["health_class"] = "PARTIAL"
    assert first["health_class"] == "HEALTHY"


def test_b022_canonical_closeout_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B022-verifier-health.md").read_text(
        encoding="utf-8"
    )
    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #85" in evidence
    assert "`ab3330afdef9c9329b1d2bb2a7e5aab09064f62b`" in evidence
    assert "`97bf66a98bad51ff0d574d90a04fa47b802708ee`" in evidence
    for run_id in ("33245760496", "33245884971", "33245974810", "33246110168"):
        assert f"run `{run_id}` — SUCCESS" in evidence
    assert "review `5057533717` — NO BLOCKING FINDINGS" in evidence
    assert "VERIFIER_EVALUATOR_EXECUTION = NONE" in evidence
    assert "B023_VERIFIER_HEALTH_EVALUATOR_AUTHORITY = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
