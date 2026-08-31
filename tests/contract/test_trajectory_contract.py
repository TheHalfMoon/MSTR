from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_NAME = "mstr-trajectory-manifest-v0"
RUNTIME_SCHEMA = ROOT / "schemas" / "mstr-trajectory-manifest-v0.schema.json"
DESIGN_SCHEMA = (
    ROOT
    / "specs"
    / "001-agent-harness-verified-loop-foundation"
    / "contracts"
    / "trajectory-manifest.schema.json"
)
TAXONOMY = ROOT / "artifacts" / "manifests" / "mstr-failure-taxonomy-v0.json"
VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / f"{SCHEMA_NAME}.json"

EXPECTED_TERMINAL_CLASSES = {
    "VERIFIED_SUCCESS",
    "RECOVERED_SUCCESS",
    "FAILED_VALID",
    "TIMEOUT_VALID",
    "INVALID_ENVIRONMENT",
    "INVALID_VERIFIER",
    "CONTAMINATED",
    "LEAKAGE_DETECTED",
    "AUTHORITY_VIOLATION",
}

EXPECTED_FAILURE_CLASSES = {
    "WRONG_LOCALIZATION",
    "BAD_ASSUMPTION",
    "STALE_FILE",
    "BAD_PATCH",
    "SYNTAX_ERROR",
    "TYPE_ERROR",
    "BUILD_FAILURE",
    "TEST_FAILURE",
    "DEPENDENCY_FAILURE",
    "TOOL_ERROR",
    "TIMEOUT",
    "INCOMPLETE_IMPLEMENTATION",
    "OVEREDIT",
    "REGRESSION",
    "FAKE_COMPLETION",
    "AUTHORITY_VIOLATION",
    "ENVIRONMENT_FAILURE",
    "VERIFIER_FAILURE",
}


def _valid() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def _assert_rejected(candidate: dict[str, object]) -> None:
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance(SCHEMA_NAME, candidate, schema_dir=ROOT / "schemas")


def test_runtime_and_design_trajectory_schemas_are_byte_identical() -> None:
    assert RUNTIME_SCHEMA.read_bytes() == DESIGN_SCHEMA.read_bytes()


def test_failure_taxonomy_is_exact_and_bound_into_schema() -> None:
    schema = load_schema(SCHEMA_NAME, schema_dir=ROOT / "schemas")
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    taxonomy_codes = {item["code"] for item in taxonomy["classes"]}
    schema_codes = set(schema["properties"]["failure_classes"]["items"]["enum"])
    terminal_codes = set(schema["properties"]["terminal_class"]["enum"])
    assert taxonomy["schema_version"] == "mstr.failure-taxonomy.v0"
    assert taxonomy_codes == EXPECTED_FAILURE_CLASSES == schema_codes
    assert set(taxonomy["terminal_classes"]) == EXPECTED_TERMINAL_CLASSES == terminal_codes


def test_clean_positive_sft_requires_healthy_stage_eligible_verifier() -> None:
    candidate = _valid()
    validate_instance(SCHEMA_NAME, candidate, schema_dir=ROOT / "schemas")

    partial = copy.deepcopy(candidate)
    partial_binding = partial["verifier_health_binding"]
    assert isinstance(partial_binding, dict)
    partial_binding["health_class"] = "PARTIAL"
    partial_binding["stage_admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
    _assert_rejected(partial)

    missing_health = copy.deepcopy(candidate)
    missing_health["verifier_health_binding"] = None
    _assert_rejected(missing_health)


def test_verifier_health_binding_must_match_run_identity() -> None:
    candidate = _valid()
    binding = candidate["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["verifier_manifest_id"] = "other-verifier"
    _assert_rejected(candidate)

    candidate = _valid()
    binding = candidate["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["task_identity"] = "other-task"
    _assert_rejected(candidate)


def test_failed_valid_preference_evidence_may_use_diagnostic_verifier_health() -> None:
    candidate = _valid()
    candidate["trajectory_id"] = "trajectory-a017-failed-preference"
    candidate["terminal_class"] = "FAILED_VALID"
    candidate["failure_classes"] = ["BAD_ASSUMPTION", "TEST_FAILURE"]
    candidate["training_admission"] = "ADMITTED_PREFERENCE"
    candidate["training_labels"] = {"label_kind": "FAILURE_PREFERENCE_EVIDENCE"}
    binding = candidate["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "PARTIAL"
    binding["stage_id"] = "MSTR-002-PREFERENCE"
    binding["stage_admission_class"] = "RESEARCH_DIAGNOSTIC_ONLY"
    validate_instance(SCHEMA_NAME, candidate, schema_dir=ROOT / "schemas")


def test_blocked_verifier_health_cannot_enter_training_admission() -> None:
    candidate = _valid()
    candidate["terminal_class"] = "FAILED_VALID"
    candidate["failure_classes"] = ["TEST_FAILURE"]
    candidate["training_admission"] = "ADMITTED_PREFERENCE"
    binding = candidate["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "BROKEN"
    binding["stage_id"] = "MSTR-002-PREFERENCE"
    binding["stage_admission_class"] = "BLOCKED"
    _assert_rejected(candidate)


@pytest.mark.parametrize("source_class", ["PRIVATE_USER_REPOSITORY", "PRODUCTION_TRACE"])
def test_private_or_production_trace_training_admission_is_rejected_in_v0(
    source_class: str,
) -> None:
    candidate = _valid()
    provenance = candidate["provenance"]
    assert isinstance(provenance, dict)
    provenance["source_class"] = source_class
    _assert_rejected(candidate)


def test_timeout_and_invalid_authority_semantics_fail_closed() -> None:
    timeout = _valid()
    timeout["terminal_class"] = "TIMEOUT_VALID"
    timeout["training_admission"] = "EVAL_ONLY"
    timeout["failure_classes"] = ["TEST_FAILURE"]
    _assert_rejected(timeout)

    authority = _valid()
    authority["terminal_class"] = "AUTHORITY_VIOLATION"
    authority["training_admission"] = "REJECTED"
    authority["failure_classes"] = ["AUTHORITY_VIOLATION"]
    authority["authority_violations"] = []
    _assert_rejected(authority)


def test_verified_success_cannot_hide_failures_or_recovery() -> None:
    candidate = _valid()
    candidate["failure_classes"] = ["TEST_FAILURE"]
    _assert_rejected(candidate)

    candidate = _valid()
    candidate["recovery_count"] = 1
    _assert_rejected(candidate)


def test_recovered_success_requires_failure_and_recovery_evidence() -> None:
    candidate = _valid()
    candidate["terminal_class"] = "RECOVERED_SUCCESS"
    candidate["failure_classes"] = ["TEST_FAILURE"]
    candidate["recovery_count"] = 1
    validate_instance(SCHEMA_NAME, candidate, schema_dir=ROOT / "schemas")

    missing_failure = copy.deepcopy(candidate)
    missing_failure["failure_classes"] = []
    _assert_rejected(missing_failure)


def test_trajectory_schema_has_no_remote_refs() -> None:
    schema = load_schema(SCHEMA_NAME, schema_dir=ROOT / "schemas")

    def walk(value: object) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "$ref":
                    assert isinstance(child, str)
                    assert child.startswith("#")
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)
