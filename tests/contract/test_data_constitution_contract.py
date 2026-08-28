from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from mstr_qualify.cli import run_validate
from mstr_qualify.schemas import SCHEMA_FILES, validate_instance

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SCHEMA = ROOT / "schemas" / "mstr-data-constitution-v0.schema.json"
DESIGN_SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "mstr-data-constitution-v0.schema.json"
)
VALID_FIXTURE = ROOT / "tests" / "fixtures" / "schemas" / "valid" / "mstr-data-constitution-v0.json"
INVALID_FIXTURE = (
    ROOT / "tests" / "fixtures" / "schemas" / "invalid" / "mstr-data-constitution-v0.json"
)


def _load(path: Path) -> dict[str, Any]:
    decoded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def _validator() -> Draft202012Validator:
    schema = _load(RUNTIME_SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _assert_rejected(instance: dict[str, Any]) -> None:
    assert list(_validator().iter_errors(instance))


def test_runtime_schema_is_valid_draft_202012() -> None:
    _validator()


def test_runtime_and_design_schema_are_byte_identical() -> None:
    assert RUNTIME_SCHEMA.read_bytes() == DESIGN_SCHEMA.read_bytes()


def test_canonical_fixture_passes() -> None:
    assert not list(_validator().iter_errors(_load(VALID_FIXTURE)))


def test_private_user_data_allow_fixture_fails_closed() -> None:
    _assert_rejected(_load(INVALID_FIXTURE))


@pytest.mark.parametrize(
    ("section", "field", "unsafe_value"),
    [
        ("target_distribution_policy", "fixed_percentages_in_b014", True),
        ("target_distribution_policy", "stage_specific_manifest_required", False),
        ("provenance_policy", "unresolved_provenance_admission", "ALLOW"),
        ("rights_policy", "unresolved_rights_admission", "ALLOW"),
        ("rights_policy", "incompatible_rights_admission", "ALLOW"),
        ("contamination_policy", "unresolved_contamination_admission", "ALLOW"),
        ("benchmark_exclusion_policy", "benchmark_eval_items_in_training", "ALLOWED"),
        ("benchmark_exclusion_policy", "hidden_tests_in_training", "ALLOWED"),
        ("synthetic_policy", "unverified_admission", "ALLOW"),
        ("student_generated_policy", "independent_verifier_required", False),
        ("student_generated_policy", "unresolved_admission", "ALLOW"),
        ("teacher_policy", "teacher_identity_is_truth", True),
        ("teacher_policy", "paid_or_api_teacher_authorized_by_constitution", True),
        ("teacher_policy", "unresolved_admission", "ALLOW"),
        ("difficulty_policy", "checkpoint_relative", False),
        ("difficulty_policy", "invalid_positive_admission", "ALLOW"),
        ("training_eval_boundary_policy", "future_history_visibility_required", False),
        ("training_eval_boundary_policy", "hidden_tests_training_visibility", "ALLOWED"),
        ("stage_admission_rules", "target_distribution_manifest_bound", False),
        ("stage_admission_rules", "unresolved_evidence_admission", "ALLOW"),
        ("stage_admission_rules", "private_user_data_default_rejection_enforced", False),
        ("private_user_data_policy", "private_user_repositories_default_ingest", True),
        ("private_user_data_policy", "production_traces_default_ingest", True),
        ("private_user_data_policy", "hidden_telemetry_allowed", True),
    ],
)
def test_fail_closed_policy_mutations_are_rejected(
    section: str,
    field: str,
    unsafe_value: object,
) -> None:
    instance = copy.deepcopy(_load(VALID_FIXTURE))
    policy = instance[section]
    assert isinstance(policy, dict)
    policy[field] = unsafe_value
    _assert_rejected(instance)


def test_core_prohibited_source_class_cannot_be_removed() -> None:
    instance = copy.deepcopy(_load(VALID_FIXTURE))
    prohibited = instance["prohibited_source_classes"]
    assert isinstance(prohibited, list)
    prohibited.remove("PRIVATE_USER_REPOSITORY")
    _assert_rejected(instance)


def test_canonical_software_role_taxonomy_cannot_drift() -> None:
    instance = copy.deepcopy(_load(VALID_FIXTURE))
    roles = instance["software_role_taxonomy"]
    assert isinstance(roles, list)
    roles.remove("SOFTWARE_EVOLUTION")
    _assert_rejected(instance)


def test_language_mix_stays_owned_by_b015() -> None:
    instance = copy.deepcopy(_load(VALID_FIXTURE))
    language_policy = instance["language_target_policy"]
    assert isinstance(language_policy, dict)
    language_policy["required_policy_task_id"] = "B014"
    _assert_rejected(instance)


def test_broken_verifier_can_never_be_clean_positive() -> None:
    instance = copy.deepcopy(_load(VALID_FIXTURE))
    thresholds = instance["verifier_health_thresholds"]
    assert isinstance(thresholds, dict)
    thresholds["clean_positive_allowed_classes"] = ["HEALTHY", "BROKEN"]
    _assert_rejected(instance)


def test_shared_schema_registry_exposes_data_constitution() -> None:
    assert SCHEMA_FILES["mstr-data-constitution-v0"] == "mstr-data-constitution-v0.schema.json"
    validate_instance("mstr-data-constitution-v0", _load(VALID_FIXTURE))


def test_cli_auto_detects_data_constitution_schema_version() -> None:
    code, payload = run_validate([VALID_FIXTURE])
    assert code == 0
    assert payload["status"] == "pass"
    assert payload["files"][0]["schema_version"] == "mstr.data-constitution.v0"

    bad_code, bad_payload = run_validate([INVALID_FIXTURE])
    assert bad_code == 1
    assert bad_payload["status"] == "fail"
    assert bad_payload["files"][0]["status"] == "fail"
