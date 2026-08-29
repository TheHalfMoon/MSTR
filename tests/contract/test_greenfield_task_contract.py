from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests/fixtures/schemas/valid/mstr-greenfield-task-v0.json"


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def test_b025_complexity_bands_are_exact_and_all_validate() -> None:
    expected = {
        "G0_FUNCTION",
        "G1_MODULE_TESTS",
        "G2_COMPONENT_FILE",
        "G3_MULTI_FILE_FEATURE",
        "G4_BOUNDED_PROGRAM",
        "G5_MULTI_ROUND_EVOLUTION",
    }
    for band in sorted(expected):
        value = fixture()
        value["complexity_band"] = band
        value["evolution_steps"] = (
            ["round-1", "round-2"] if band == "G5_MULTI_ROUND_EVOLUTION" else []
        )
        validate_instance("mstr-greenfield-task-v0", value)


def test_b025_g5_requires_multiple_evolution_steps() -> None:
    value = fixture()
    value["complexity_band"] = "G5_MULTI_ROUND_EVOLUTION"
    value["evolution_steps"] = ["round-1"]
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_non_g5_rejects_future_evolution_steps() -> None:
    value = fixture()
    value["evolution_steps"] = ["future-round"]
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_unverified_feature_tree_synthesis_cannot_self_admit() -> None:
    value = fixture()
    value["generation_method"] = "FEATURE_TREE_SYNTHESIS"
    value["provenance"]["source_class"] = "SYNTHETIC_VERIFIED"
    value["provenance"]["generator_identity"] = "generator:v1"
    value["synthesis_evidence"] = {
        "generator_kind": "FEATURE_TREE",
        "generator_identity": "generator:v1",
        "generator_revision": "revision:1",
        "proposal_only": True,
        "independent_verification_status": "NOT_RUN",
        "independent_verifier_identity": None,
        "verification_evidence_identity": None,
    }
    value["admission_class"] = "CURRICULUM_ELIGIBLE"
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_verified_feature_tree_proposal_may_pass_contract_gate() -> None:
    value = fixture()
    value["generation_method"] = "FEATURE_TREE_SYNTHESIS"
    value["provenance"]["source_class"] = "SYNTHETIC_VERIFIED"
    value["provenance"]["generator_identity"] = "generator:v1"
    value["synthesis_evidence"] = {
        "generator_kind": "FEATURE_TREE",
        "generator_identity": "generator:v1",
        "generator_revision": "revision:1",
        "proposal_only": True,
        "independent_verification_status": "VERIFIED",
        "independent_verifier_identity": "verifier:independent-v1",
        "verification_evidence_identity": "evidence:verification-v1",
    }
    validate_instance("mstr-greenfield-task-v0", value)


@pytest.mark.parametrize("status", ["INCOMPATIBLE", "UNRESOLVED"])
def test_b025_curriculum_eligible_fails_closed_on_rights(status: str) -> None:
    value = fixture()
    value["rights_decision"]["decision"] = status
    assert validation_errors("mstr-greenfield-task-v0", value)


@pytest.mark.parametrize(
    "field",
    [
        "benchmark_overlap",
        "hidden_answer_exposure",
        "future_history_exposure",
        "cross_split_duplicate",
    ],
)
def test_b025_curriculum_eligible_requires_clear_contamination(field: str) -> None:
    value = fixture()
    value["contamination_boundary"][field] = "UNRESOLVED"
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_hidden_behavior_must_remain_hidden() -> None:
    value = fixture()
    value["hidden_behavior_manifest"]["hidden_from_model"] = False
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_rejected_or_experimental_records_require_reasons() -> None:
    for admission in ("EXPERIMENTAL_ONLY", "REJECTED"):
        value = fixture()
        value["admission_class"] = admission
        assert validation_errors("mstr-greenfield-task-v0", value)
        value["admission_reasons"] = ["fixture.reason"]
        validate_instance("mstr-greenfield-task-v0", value)


def test_b025_schema_has_no_remote_reference() -> None:
    schema = json.loads(
        (ROOT / "schemas/mstr-greenfield-task-v0.schema.json").read_text(encoding="utf-8")
    )
    encoded = json.dumps(schema, sort_keys=True)
    assert "http" not in encoded.replace(
        "https://json-schema.org/draft/2020-12/schema", ""
    ).replace("https://mstr.local/schemas/mstr-greenfield-task-v0.json", "")


def test_b025_fixture_is_not_mutated_by_validation() -> None:
    value = fixture()
    before = copy.deepcopy(value)
    validate_instance("mstr-greenfield-task-v0", value)
    assert value == before
