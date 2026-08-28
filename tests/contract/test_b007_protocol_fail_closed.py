from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "benchmarks" / "manifests" / "B007-tokenizer-economics.json"
SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "b007-tokenizer-economics-protocol-v0.schema.json"
)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _validator() -> Draft202012Validator:
    schema = _load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _assert_rejected(instance: dict[str, Any]) -> None:
    assert list(_validator().iter_errors(instance))


def test_current_b007_protocol_conforms_to_fail_closed_schema() -> None:
    assert not list(_validator().iter_errors(_load(MANIFEST)))


def test_missing_tokenizer_identity_requirement_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    del instance["tokenizer_identity"]["all_loaded_tokenizer_artifact_sha256_inventory_required"]
    _assert_rejected(instance)


def test_comparability_weakening_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    instance["comparability"]["same_effective_settings_policy_required"] = False
    _assert_rejected(instance)


def test_category_summary_shape_drift_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    del instance["corpus"]["category_summary"][0]["profiles"]
    _assert_rejected(instance)


def test_entry_pin_shape_drift_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    del instance["corpus"]["entry_pins"][0]["sha256"]
    _assert_rejected(instance)


def test_structural_observation_drift_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    del instance["metrics"]["required_structural_observations"]["tool_json"]
    _assert_rejected(instance)


def test_b008_output_requirement_drift_is_rejected() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    instance["b008_output_requirements"].remove("loaded_tokenizer_artifact_sha256_inventory")
    _assert_rejected(instance)


def test_authority_note_and_false_flags_are_frozen() -> None:
    instance = copy.deepcopy(_load(MANIFEST))
    instance["authority"]["tokenizer_measurement_authorized_by_b007"] = True
    _assert_rejected(instance)
