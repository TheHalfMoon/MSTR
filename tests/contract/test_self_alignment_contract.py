from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.cli import _SCHEMA_VERSION_TO_SCHEMA_NAME
from mstr_qualify.schemas import SCHEMA_FILES, validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_NAME = "mstr-self-alignment-generation-v0"
VERSION = "mstr.self-alignment-generation.v0"
VALID_FIXTURE = (
    ROOT / "tests" / "fixtures" / "schemas" / "valid" / "mstr-self-alignment-generation-v0.json"
)
INVALID_FIXTURE = (
    ROOT / "tests" / "fixtures" / "schemas" / "invalid" / "mstr-self-alignment-generation-v0.json"
)


def _valid_record() -> dict[str, object]:
    decoded = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def _generated(record: dict[str, object], collection: str, index: int = 0) -> dict[str, object]:
    if collection == "generated_task":
        artifact = record[collection]
    else:
        artifacts = record[collection]
        assert isinstance(artifacts, list)
        artifact = artifacts[index]
    assert isinstance(artifact, dict)
    return artifact


def test_b018_schema_is_registered_for_offline_validation() -> None:
    assert SCHEMA_FILES[SCHEMA_NAME] == "mstr-self-alignment-generation-v0.schema.json"
    assert _SCHEMA_VERSION_TO_SCHEMA_NAME[VERSION] == SCHEMA_NAME


def test_design_and_runtime_schemas_are_byte_identical() -> None:
    runtime = ROOT / "schemas" / "mstr-self-alignment-generation-v0.schema.json"
    design = (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-self-alignment-generation-v0.schema.json"
    )
    assert runtime.read_bytes() == design.read_bytes()


def test_valid_admit_fixture_passes() -> None:
    validate_instance(SCHEMA_NAME, _valid_record())


def test_canonical_unresolved_generated_test_rights_fixture_fails_closed() -> None:
    decoded = json.loads(INVALID_FIXTURE.read_text(encoding="utf-8"))
    errors = validation_errors(SCHEMA_NAME, decoded)
    assert errors
    assert any("UNRESOLVED" in error or "COMPATIBLE" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("seed_contamination_status", "UNRESOLVED"),
        ("contamination_status", "DETECTED"),
    ],
)
def test_admit_requires_clear_contamination(field: str, value: str) -> None:
    record = _valid_record()
    record[field] = value
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("lineage_status", "INCOMPLETE"),
        ("lineage_status", "UNRESOLVED"),
    ],
)
def test_admit_requires_complete_seed_provenance(field: str, value: str) -> None:
    record = _valid_record()
    provenance = record["seed_provenance"]
    assert isinstance(provenance, dict)
    provenance[field] = value
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("decision", ["INCOMPATIBLE", "UNRESOLVED"])
def test_admit_requires_compatible_seed_rights(decision: str) -> None:
    record = _valid_record()
    rights = record["seed_rights_decision"]
    assert isinstance(rights, dict)
    rights["decision"] = decision
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("collection", ["generated_task", "generated_solutions", "generated_tests"])
def test_every_generated_artifact_requires_complete_provenance(collection: str) -> None:
    record = _valid_record()
    artifact = _generated(record, collection)
    provenance = artifact["provenance"]
    assert isinstance(provenance, dict)
    provenance["lineage_status"] = "UNRESOLVED"
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("collection", ["generated_task", "generated_solutions", "generated_tests"])
@pytest.mark.parametrize("decision", ["INCOMPATIBLE", "UNRESOLVED"])
def test_every_generated_artifact_requires_compatible_rights(
    collection: str, decision: str
) -> None:
    record = _valid_record()
    artifact = _generated(record, collection)
    rights = artifact["rights_decision"]
    assert isinstance(rights, dict)
    rights["decision"] = decision
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("collection", ["generated_task", "generated_solutions", "generated_tests"])
def test_every_generated_artifact_requires_clear_contamination(collection: str) -> None:
    record = _valid_record()
    artifact = _generated(record, collection)
    artifact["contamination_status"] = "UNRESOLVED"
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("collection", ["generated_solutions", "generated_tests"])
def test_executable_artifacts_require_execution_evidence(collection: str) -> None:
    record = _valid_record()
    artifact = _generated(record, collection)
    del artifact["execution_result"]
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize("collection", ["generated_solutions", "generated_tests"])
def test_admit_requires_sandboxed_passing_execution(collection: str) -> None:
    record = _valid_record()
    artifact = _generated(record, collection)
    execution = artifact["execution_result"]
    assert isinstance(execution, dict)
    execution["sandboxed"] = False
    assert validation_errors(SCHEMA_NAME, record)

    record = _valid_record()
    artifact = _generated(record, collection)
    execution = artifact["execution_result"]
    assert isinstance(execution, dict)
    execution["result"] = "FAIL"
    assert validation_errors(SCHEMA_NAME, record)


def test_task_record_rejects_fake_execution_result() -> None:
    record = _valid_record()
    task = _generated(record, "generated_task")
    task["execution_result"] = {
        "sandboxed": True,
        "result": "PASS",
        "evidence_identity": "not-applicable-to-task",
    }
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("health_class", "PARTIAL"),
        ("health_class", "BROKEN"),
        ("independence", "NOT_INDEPENDENT"),
        ("independence", "UNRESOLVED"),
        ("generated_tests_sole_authority", True),
    ],
)
def test_admit_requires_healthy_independent_verifier(field: str, value: object) -> None:
    record = _valid_record()
    health = record["verifier_health"]
    assert isinstance(health, dict)
    health[field] = value
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    "field",
    ["model_id", "checkpoint_id", "harness_profile_id", "sampling_identity"],
)
def test_exact_student_harness_sampling_identity_is_mandatory(field: str) -> None:
    record = _valid_record()
    identity = record["student_model_identity"]
    assert isinstance(identity, dict)
    del identity[field]
    assert validation_errors(SCHEMA_NAME, record)


def test_invalid_difficulty_cannot_be_admitted() -> None:
    record = _valid_record()
    difficulty = record["difficulty_record"]
    assert isinstance(difficulty, dict)
    difficulty["difficulty_class"] = "INVALID"
    assert validation_errors(SCHEMA_NAME, record)


def test_reject_record_preserves_negative_evidence() -> None:
    record = _valid_record()
    record["admission_decision"] = "REJECT"
    record["admission_reasons"] = ["generated_test_rights_unresolved"]
    test = _generated(record, "generated_tests")
    rights = test["rights_decision"]
    assert isinstance(rights, dict)
    rights["decision"] = "UNRESOLVED"
    rights_bindings = record["generated_artifact_rights_decisions"]
    assert isinstance(rights_bindings, list)
    test_rights_binding = next(
        binding
        for binding in rights_bindings
        if isinstance(binding, dict) and binding.get("artifact_id") == "test"
    )
    bound_rights = test_rights_binding["rights_decision"]
    assert isinstance(bound_rights, dict)
    bound_rights["decision"] = "UNRESOLVED"
    health = record["verifier_health"]
    assert isinstance(health, dict)
    health["health_class"] = "BROKEN"
    difficulty = record["difficulty_record"]
    assert isinstance(difficulty, dict)
    difficulty["difficulty_class"] = "INVALID"
    validate_instance(SCHEMA_NAME, record)


def test_reject_requires_a_reason() -> None:
    record = _valid_record()
    record["admission_decision"] = "REJECT"
    record["admission_reasons"] = []
    assert validation_errors(SCHEMA_NAME, record)


def test_admit_rejects_unexplained_reasons() -> None:
    record = _valid_record()
    record["admission_reasons"] = ["should-not-exist-on-admit"]
    assert validation_errors(SCHEMA_NAME, record)


def test_schema_rejects_unknown_fields() -> None:
    record = _valid_record()
    record["training_authorized"] = True
    assert validation_errors(SCHEMA_NAME, record)


def test_b018_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B018-self-alignment-contract.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B018" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = 73b60aa9421f51be52560bbbca6e8dd46b77b6c9" in evidence
    assert "ENTRY_GATE_RUN = 33185451160" in evidence
    assert "ENTRY_GATE_JOB = 98897160421" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


@pytest.mark.parametrize(
    "field",
    [
        "generated_artifact_provenance",
        "generated_artifact_rights_decisions",
        "execution_results",
    ],
)
def test_canonical_generated_evidence_arrays_are_required(field: str) -> None:
    record = _valid_record()
    del record[field]
    assert validation_errors(SCHEMA_NAME, record)


def test_generated_provenance_bindings_must_exactly_cover_artifacts() -> None:
    record = _valid_record()
    bindings = record["generated_artifact_provenance"]
    assert isinstance(bindings, list)
    bindings.pop()
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("exactly cover generated artifact ids" in error for error in errors)


def test_generated_provenance_binding_must_match_artifact() -> None:
    record = _valid_record()
    bindings = record["generated_artifact_provenance"]
    assert isinstance(bindings, list)
    binding = bindings[0]
    assert isinstance(binding, dict)
    provenance = binding["provenance"]
    assert isinstance(provenance, dict)
    provenance["source_revision"] = "mismatched-revision"
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("does not match artifact provenance" in error for error in errors)


def test_generated_rights_binding_must_match_artifact() -> None:
    record = _valid_record()
    bindings = record["generated_artifact_rights_decisions"]
    assert isinstance(bindings, list)
    binding = bindings[0]
    assert isinstance(binding, dict)
    rights = binding["rights_decision"]
    assert isinstance(rights, dict)
    rights["license_or_terms_identity"] = "mismatched-rights"
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("does not match artifact rights_decision" in error for error in errors)


def test_execution_bindings_must_exactly_cover_executable_artifacts() -> None:
    record = _valid_record()
    bindings = record["execution_results"]
    assert isinstance(bindings, list)
    bindings.pop()
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("exactly cover executable artifact ids" in error for error in errors)


def test_execution_binding_must_match_artifact_result() -> None:
    record = _valid_record()
    bindings = record["execution_results"]
    assert isinstance(bindings, list)
    binding = bindings[0]
    assert isinstance(binding, dict)
    result = binding["execution_result"]
    assert isinstance(result, dict)
    result["evidence_identity"] = "mismatched-execution"
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("does not match artifact execution_result" in error for error in errors)


def test_execution_binding_must_match_environment_identity() -> None:
    record = _valid_record()
    bindings = record["execution_results"]
    assert isinstance(bindings, list)
    binding = bindings[0]
    assert isinstance(binding, dict)
    binding["environment_identity"] = "other-sandbox"
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("does not match environment_identity" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (
            "student_model_identity",
            {
                "model_id": "other-model",
                "checkpoint_id": "other-checkpoint",
                "harness_profile_id": "fixture-harness",
                "sampling_identity": "fixture-sampling",
            },
        ),
        ("harness_profile_id", "other-harness"),
        ("sampling_identity", "other-sampling"),
    ],
)
def test_difficulty_binding_must_match_exact_student_harness_sampling_identity(
    field: str, value: object
) -> None:
    record = _valid_record()
    difficulty = record["difficulty_record"]
    assert isinstance(difficulty, dict)
    difficulty[field] = value
    errors = validation_errors(SCHEMA_NAME, record)
    assert any("difficulty_record" in error and "match" in error for error in errors)


def test_schema_exposes_exact_canonical_self_alignment_evidence_fields() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "mstr-self-alignment-generation-v0.schema.json").read_text(
            encoding="utf-8"
        )
    )
    required = set(schema["required"])
    assert {
        "generated_artifact_provenance",
        "generated_artifact_rights_decisions",
        "execution_results",
    } <= required


def test_b018_does_not_claim_b020_or_b022_authority() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B018-self-alignment-contract.md").read_text(
        encoding="utf-8"
    )
    assert "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE" in evidence
    assert "B022_VERIFIER_HEALTH_AUTHORITY = NONE" in evidence
