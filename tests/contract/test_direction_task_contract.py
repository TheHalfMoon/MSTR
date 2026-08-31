from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from mstr_qualify.cli import run_validate
from mstr_qualify.schemas import SCHEMA_FILES, validate_instance

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas/mstr-direction-task-v0.schema.json"
DESIGN_SCHEMA = (
    ROOT
    / "specs"
    / "001-agent-harness-verified-loop-foundation"
    / "contracts"
    / "mstr-direction-task-v0.schema.json"
)
VALID = ROOT / "tests/fixtures/schemas/valid/mstr-direction-task-v0.json"
INVALID = ROOT / "tests/fixtures/schemas/invalid/mstr-direction-task-v0.json"
TAXONOMY = ROOT / "benchmarks/direction-to-done/v0-taxonomy.json"

EXPECTED_FAMILIES = {
    "TERSE_FEATURE_DIRECTION",
    "MULTI_FILE_CONSTRUCTION",
    "REPAIR",
    "BUILD_TOOLING",
    "BOUNDED_GREENFIELD",
    "WEPLD_SPEC_DRIVEN",
    "FAILURE_RECOVERY",
    "SECURITY_SENSITIVE",
}


def _schema() -> dict[str, object]:
    return json.loads(SCHEMA.read_text(encoding="utf-8"))


def _fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def _errors(value: object) -> list[object]:
    return list(Draft202012Validator(_schema()).iter_errors(value))


def test_a015_is_registered_as_first_class_offline_schema() -> None:
    assert SCHEMA_FILES["mstr-direction-task-v0"] == "mstr-direction-task-v0.schema.json"
    validate_instance("mstr-direction-task-v0", _fixture())


def test_a015_cli_auto_detects_valid_and_invalid_direction_task_files() -> None:
    valid_code, valid_payload = run_validate([VALID])
    invalid_code, invalid_payload = run_validate([INVALID])
    assert valid_code == 0
    assert valid_payload["status"] == "pass"
    assert valid_payload["files"][0]["schema_version"] == "mstr.direction-task.v0"
    assert invalid_code == 1
    assert invalid_payload["status"] == "fail"


def test_a015_runtime_schema_matches_design_source_byte_for_byte() -> None:
    assert SCHEMA.read_bytes() == DESIGN_SCHEMA.read_bytes()


def test_a015_schema_is_valid_draft_202012_and_has_no_remote_refs() -> None:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    encoded = json.dumps(schema, sort_keys=True)
    encoded = encoded.replace("https://json-schema.org/draft/2020-12/schema", "")
    encoded = encoded.replace("https://mstr.local/schemas/mstr-direction-task-v0.json", "")
    assert "http://" not in encoded
    assert "https://" not in encoded


def test_a015_valid_fixture_passes_and_invalid_fixture_fails() -> None:
    assert _errors(_fixture()) == []
    invalid = json.loads(INVALID.read_text(encoding="utf-8"))
    assert _errors(invalid)


def test_a015_taxonomy_is_exact_and_public_surface_contains_no_hidden_payload() -> None:
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    assert set(taxonomy["task_families"]) == EXPECTED_FAMILIES
    posture = taxonomy["public_repository_posture"]
    assert posture["contains_taxonomy_and_contract_fixtures_only"] is True
    assert posture["contains_private_fresh_tasks"] is False
    assert posture["contains_hidden_acceptance_payloads"] is False
    assert posture["contains_model_answers_or_future_fixes"] is False


def test_a015_every_family_is_representable_under_exact_conditional_rules() -> None:
    for family in sorted(EXPECTED_FAMILIES):
        value = _fixture()
        value["task_family"] = family
        if family in {
            "TERSE_FEATURE_DIRECTION",
            "MULTI_FILE_CONSTRUCTION",
            "BOUNDED_GREENFIELD",
        }:
            value["b025_extension"]["required_for_headline_convergence"] = True
            value["b025_extension"]["greenfield_manifest_id"] = (
                f"fixture:b025:{family.lower()}"
            )
        if family == "WEPLD_SPEC_DRIVEN":
            value["wepld_binding"] = {
                "required": True,
                "spec_task_identity": "fixture:wepld:task-001",
            }
        if family == "FAILURE_RECOVERY":
            value["recovery_path_required"] = True
        if family == "SECURITY_SENSITIVE":
            value["security_sensitive"] = True
        assert _errors(value) == []


def test_a015_feature_greenfield_families_require_b025_extension_identity() -> None:
    for family in (
        "TERSE_FEATURE_DIRECTION",
        "MULTI_FILE_CONSTRUCTION",
        "BOUNDED_GREENFIELD",
    ):
        value = _fixture()
        value["task_family"] = family
        value["b025_extension"]["required_for_headline_convergence"] = True
        value["b025_extension"]["greenfield_manifest_id"] = None
        assert _errors(value)


def test_a015_wepld_family_requires_exact_spec_task_binding() -> None:
    value = _fixture()
    value["task_family"] = "WEPLD_SPEC_DRIVEN"
    assert _errors(value)
    value["wepld_binding"] = {
        "required": True,
        "spec_task_identity": "fixture:wepld:task-001",
    }
    assert _errors(value) == []


def test_a015_failure_recovery_and_security_families_fail_closed() -> None:
    recovery = _fixture()
    recovery["task_family"] = "FAILURE_RECOVERY"
    assert _errors(recovery)
    recovery["recovery_path_required"] = True
    assert _errors(recovery) == []

    security = _fixture()
    security["task_family"] = "SECURITY_SENSITIVE"
    assert _errors(security)
    security["security_sensitive"] = True
    assert _errors(security) == []


def test_a015_acceptance_surface_remains_verifier_owned_and_hidden() -> None:
    for field, invalid_value in (
        ("verifier_owned", False),
        ("hidden_from_model", False),
        ("public_repo_contains_acceptance_payload", True),
    ):
        value = _fixture()
        value["acceptance_surface"][field] = invalid_value
        assert _errors(value)


def test_a015_private_fresh_task_cannot_be_contract_fixture_execution() -> None:
    value = _fixture()
    value["freshness_provenance"]["surface_class"] = "PRIVATE_FRESH"
    assert _errors(value)
    value["execution_posture"] = "DOWNSTREAM_GATED"
    assert _errors(value) == []


def test_a015_validation_does_not_mutate_fixture() -> None:
    value = _fixture()
    before = copy.deepcopy(value)
    assert _errors(value) == []
    assert value == before
