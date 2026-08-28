from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-software-evolution-record-v0.json"
)
INVALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "invalid"
    / "mstr-software-evolution-record-v0.json"
)
SCHEMA_NAME = "mstr-software-evolution-record-v0"


def _valid_record() -> dict[str, object]:
    decoded = json.loads(VALID_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def test_forward_step_fixture_passes() -> None:
    validate_instance(SCHEMA_NAME, _valid_record())


def test_canonical_future_leak_fixture_fails_closed() -> None:
    decoded = json.loads(INVALID_FIXTURE.read_text(encoding="utf-8"))
    errors = validation_errors(SCHEMA_NAME, decoded)
    assert errors
    assert any("future_patch_visibility" in error for error in errors)


@pytest.mark.parametrize(
    "field",
    [
        "final_revision_visibility",
        "future_patch_visibility",
        "future_test_result_visibility",
        "future_review_visibility",
    ],
)
def test_forward_step_rejects_every_future_visibility_channel(field: str) -> None:
    record = _valid_record()
    boundary = record["future_history_boundary"]
    assert isinstance(boundary, dict)
    boundary[field] = "VISIBLE_AS_RETROSPECTIVE_CONTEXT"
    assert validation_errors(SCHEMA_NAME, record)


def test_forward_step_rejects_retrospective_reason() -> None:
    record = _valid_record()
    boundary = record["future_history_boundary"]
    assert isinstance(boundary, dict)
    boundary["retrospective_context_reason"] = "This must not exist in forward projection."
    assert validation_errors(SCHEMA_NAME, record)


def test_retrospective_review_requires_explicit_reason_and_visibility() -> None:
    record = _valid_record()
    boundary = record["future_history_boundary"]
    assert isinstance(boundary, dict)
    boundary["projection_mode"] = "RETROSPECTIVE_REVIEW"
    boundary["future_review_visibility"] = "VISIBLE_AS_RETROSPECTIVE_CONTEXT"

    assert validation_errors(SCHEMA_NAME, record)

    boundary["retrospective_context_reason"] = (
        "Retrospective review projection intentionally exposes later review feedback."
    )
    validate_instance(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    ("collection", "index"),
    [
        ("change_events", 0),
        ("test_ci_events", 0),
        ("review_events", 0),
        ("recovery_events", 0),
    ],
)
def test_every_evolution_event_declares_model_visibility(
    collection: str, index: int
) -> None:
    record = _valid_record()
    events = record[collection]
    assert isinstance(events, list)
    event = events[index]
    assert isinstance(event, dict)
    del event["model_visibility"]
    assert validation_errors(SCHEMA_NAME, record)


@pytest.mark.parametrize(
    "field",
    [
        "visible_context_manifest",
        "future_history_boundary",
        "provenance",
        "rights",
        "contamination_status",
        "final_verifier_identity",
    ],
)
def test_identity_and_leakage_evidence_is_mandatory(field: str) -> None:
    record = _valid_record()
    del record[field]
    assert validation_errors(SCHEMA_NAME, record)


def test_visible_context_manifest_requires_explicit_future_exclusion_list() -> None:
    record = _valid_record()
    manifest = record["visible_context_manifest"]
    assert isinstance(manifest, dict)
    del manifest["excluded_future_event_ids"]
    assert validation_errors(SCHEMA_NAME, record)


def test_rights_and_contamination_can_record_fail_closed_evidence_states() -> None:
    record = _valid_record()
    rights = record["rights"]
    assert isinstance(rights, dict)
    rights["decision"] = "UNRESOLVED"
    record["contamination_status"] = "UNRESOLVED"

    validate_instance(SCHEMA_NAME, record)


def test_schema_rejects_unknown_event_fields() -> None:
    record = _valid_record()
    mutated = copy.deepcopy(record)
    changes = mutated["change_events"]
    assert isinstance(changes, list)
    first = changes[0]
    assert isinstance(first, dict)
    first["future_patch_contents"] = "leaked patch"
    assert validation_errors(SCHEMA_NAME, mutated)
