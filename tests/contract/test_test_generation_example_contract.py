from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json"


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def test_b024_valid_reproduction_regression_fixture_passes() -> None:
    validate_instance("mstr-test-generation-example-v0", fixture())


@pytest.mark.parametrize("decision", ["INCOMPATIBLE", "UNRESOLVED"])
def test_b024_admit_fails_closed_on_rights(decision: str) -> None:
    value = fixture()
    value["generated_test_rights_decision"]["decision"] = decision
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    "field",
    [
        "benchmark_overlap",
        "hidden_answer_exposure",
        "future_history_exposure",
        "cross_split_duplicate",
    ],
)
def test_b024_admit_requires_clear_contamination(field: str) -> None:
    value = fixture()
    value["contamination_status"][field] = "UNRESOLVED"
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("answer_encoding", "DETECTED"),
        ("test_weakening", "DETECTED"),
        ("evaluator_modification", "DETECTED"),
        ("protected_path_status", "TAMPERED"),
    ],
)
def test_b024_admit_rejects_integrity_shortcuts(field: str, bad: str) -> None:
    value = fixture()
    value["integrity_checks"][field] = bad
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_admit_rejects_deleted_or_protected_test_changes() -> None:
    value = fixture()
    value["generated_test_patch"]["deleted_existing_test_paths"] = ["tests/old_test.py"]
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["generated_test_patch"]["protected_path_changes"] = ["tests/hidden_oracle.py"]
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    "health",
    ["PARTIAL", "DISAGREEMENT", "BROKEN", "LEAKED", "TAMPERED"],
)
def test_b024_clean_admit_requires_healthy_verifier(health: str) -> None:
    value = fixture()
    value["verifier_health_binding"]["health_class"] = health
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_default_repair_proof_requires_fail_before_pass_after() -> None:
    value = fixture()
    value["behavioral_proof"]["pre_fix_result"]["status"] = "PASS"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["status"] = "FAIL"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_same_test_artifact_is_required_pre_and_post() -> None:
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["test_artifact_sha256"] = "3" * 64
    errors = validation_errors("mstr-test-generation-example-v0", value)
    assert any("must match generated_test_patch.test_artifact_sha256" in error for error in errors)


def test_b024_pre_post_revision_identity_is_bound() -> None:
    value = fixture()
    value["behavioral_proof"]["pre_fix_result"]["revision"] = "wrong-base"
    assert any(
        "must match base_revision" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["revision"] = "wrong-fix"
    assert any(
        "must match fix_revision" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_pre_post_environment_and_verifier_must_match() -> None:
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["environment_identity"] = "other-env"
    assert any(
        "environment_identity must match" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["verifier_manifest_id"] = "other-verifier"
    assert any(
        "verifier_manifest_id must match" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_reproduction_requirement_is_semantically_bound() -> None:
    value = fixture()
    value["behavior_contract"]["test_classes"] = ["TARGETED_REGRESSION"]
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_property_or_metamorphic_requirement_is_semantically_bound() -> None:
    value = fixture()
    value["behavior_contract"]["property_or_metamorphic_applicable"] = True
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["behavior_contract"]["test_classes"].append("PROPERTY")
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_task_specific_proof_requires_independent_evidence() -> None:
    value = fixture()
    value["behavioral_proof"]["proof_kind"] = "TASK_SPECIFIC_BEHAVIOR"
    value["behavioral_proof"]["pre_fix_result"]["status"] = "PASS"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["behavioral_proof"]["independent_acceptance_evidence_identity"] = (
        "fixture-independent-acceptance-v1"
    )
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_mutation_accounting_and_strength_fail_closed() -> None:
    value = fixture()
    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": "fixture-mutation-v1",
        "mutants_evaluated": 2,
        "mutants_killed": 3,
    }
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["mutation_strength"]["status"] = "WEAK"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_rejected_records_require_reasons() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["admission_reasons"] = ["fixture.reject"]
    validate_instance("mstr-test-generation-example-v0", value)



def test_b024_admit_requires_complete_generated_test_provenance() -> None:
    value = fixture()
    value["generated_test_provenance"]["provenance_status"] = "UNRESOLVED"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_generated_sources_require_generator_identity() -> None:
    value = fixture()
    provenance = value["generated_test_provenance"]
    assert isinstance(provenance, dict)
    provenance["source_class"] = "STUDENT_GENERATED"
    provenance["generator_identity"] = None
    assert validation_errors("mstr-test-generation-example-v0", value)
    provenance["generator_identity"] = "student-generator:fixture-v1"
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_verifier_health_binding_matches_task_and_executed_verifier() -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["task_identity"] = "other-task"
    assert any(
        "verifier_health_binding.task_identity" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )

    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["verifier_manifest_id"] = "other-verifier"
    assert any(
        "must match executed verifier manifest" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_adequate_mutation_strength_requires_real_evidence() -> None:
    value = fixture()
    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": None,
        "mutants_evaluated": 0,
        "mutants_killed": 0,
    }
    assert validation_errors("mstr-test-generation-example-v0", value)

    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": "fixture-mutation:v1",
        "mutants_evaluated": 2,
        "mutants_killed": 1,
    }
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_fail_before_pass_after_requires_distinct_revisions() -> None:
    value = fixture()
    value["fix_revision"] = value["base_revision"]
    proof = value["behavioral_proof"]
    assert isinstance(proof, dict)
    post = proof["post_fix_result"]
    assert isinstance(post, dict)
    post["revision"] = value["base_revision"]

    errors = validation_errors("mstr-test-generation-example-v0", value)
    assert any("requires a revision distinct from base_revision" in error for error in errors)


@pytest.mark.parametrize(
    "stage_class",
    ["RESEARCH_DIAGNOSTIC_ONLY", "BLOCKED"],
)
def test_b024_admit_requires_clean_positive_stage_eligibility(stage_class: str) -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "HEALTHY"
    binding["stage_admission_class"] = stage_class
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_verifier_health_binding_requires_exact_stage_identity() -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding.pop("stage_id")
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_nonhealthy_health_cannot_claim_clean_positive_stage() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    value["admission_reasons"] = ["VERIFIER_HEALTH_NOT_CLEAN_POSITIVE"]
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "PARTIAL"
    binding["stage_admission_class"] = "CLEAN_POSITIVE_ELIGIBLE"
    assert validation_errors("mstr-test-generation-example-v0", value)

def test_b024_schema_has_no_remote_reference() -> None:
    schema = json.loads(
        (ROOT / "schemas/mstr-test-generation-example-v0.schema.json").read_text(
            encoding="utf-8"
        )
    )
    encoded = json.dumps(schema, sort_keys=True)
    assert "http" not in encoded.replace(
        "https://json-schema.org/draft/2020-12/schema", ""
    ).replace("https://mstr.local/schemas/mstr-test-generation-example-v0.json", "")


def test_b024_fixture_is_not_mutated_by_validation() -> None:
    value = fixture()
    before = copy.deepcopy(value)
    validate_instance("mstr-test-generation-example-v0", value)
    assert value == before
