from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import SCHEMA_FILES, load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"
LEGACY_DESIGN_SCHEMA_DIR = (
    ROOT / "specs" / "000-universal-laptop-interaction-contract" / "contracts"
)
DESIGN_SCHEMA_OVERRIDES = {
    "mstr-task-node-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-task-node-v0.schema.json"
    ),
    "mstr-task-eligibility-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-task-eligibility-v0.schema.json"
    ),
    "mstr-data-constitution-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-data-constitution-v0.schema.json"
    ),
    "mstr-self-alignment-generation-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-self-alignment-generation-v0.schema.json"
    ),
    "mstr-teacher-rescue-record-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-teacher-rescue-record-v0.schema.json"
    ),
    "mstr-difficulty-calibration-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-difficulty-calibration-v0.schema.json"
    ),
    "mstr-verifier-health-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-verifier-health-v0.schema.json"
    ),
    "mstr-greenfield-task-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-greenfield-task-v0.schema.json"
    ),
    "mstr-training-method-cell-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-training-method-cell-v0.schema.json"
    ),
    "mstr-q4-promotion-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-q4-promotion-v0.schema.json"
    ),
    "mstr-software-evolution-record-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-software-evolution-record-v0.schema.json"
    ),
    "mstr-environment-manifest-v0": (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / "mstr-environment-manifest-v0.schema.json"
    ),
    "mstr-setup-manifest-v0": (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / "mstr-setup-manifest-v0.schema.json"
    ),
    "mstr-verifier-manifest-v0": (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / "mstr-verifier-manifest-v0.schema.json"
    ),
    "mstr-capability-profile-v0": (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / "mstr-capability-profile-v0.schema.json"
    ),
    "mstr-direction-task-v0": (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / "mstr-direction-task-v0.schema.json"
    ),
}


def _fixture(kind: str, schema_name: str) -> object:
    dedicated = FIXTURES / kind / f"{schema_name}.json"
    if dedicated.exists():
        return json.loads(dedicated.read_text(encoding="utf-8"))
    fixtures = json.loads((FIXTURES / kind / "fixtures.json").read_text(encoding="utf-8"))
    return fixtures[schema_name]


def _design_schema_path(schema_name: str) -> Path:
    override = DESIGN_SCHEMA_OVERRIDES.get(schema_name)
    if override is not None:
        return override
    return LEGACY_DESIGN_SCHEMA_DIR / SCHEMA_FILES[schema_name]


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_runtime_schema_is_valid_draft_202012(schema_name: str) -> None:
    schema = load_schema(schema_name, schema_dir=ROOT / "schemas")
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_runtime_schema_matches_design_source_byte_for_byte(schema_name: str) -> None:
    filename = SCHEMA_FILES[schema_name]
    runtime = (ROOT / "schemas" / filename).read_bytes()
    design = _design_schema_path(schema_name).read_bytes()
    assert runtime == design


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_valid_fixture_passes(schema_name: str) -> None:
    validate_instance(schema_name, _fixture("valid", schema_name), schema_dir=ROOT / "schemas")


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_invalid_fixture_fails_closed(schema_name: str) -> None:
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance(
            schema_name, _fixture("invalid", schema_name), schema_dir=ROOT / "schemas"
        )


def test_unknown_schema_name_fails_closed() -> None:
    with pytest.raises(ValueError, match="unknown schema"):
        load_schema("../../candidate-record", schema_dir=ROOT / "schemas")


def test_external_ref_is_rejected_before_validation(tmp_path: Path) -> None:
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "https://example.invalid/remote.json",
    }
    (tmp_path / SCHEMA_FILES["candidate-record"]).write_text(json.dumps(schema), encoding="utf-8")
    with pytest.raises(ValueError, match="external schema reference is prohibited"):
        load_schema("candidate-record", schema_dir=tmp_path)
