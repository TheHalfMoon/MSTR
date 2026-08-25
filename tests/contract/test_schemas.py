from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import SCHEMA_FILES, load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"


def _fixture(kind: str, schema_name: str) -> object:
    fixtures = json.loads((FIXTURES / kind / "fixtures.json").read_text(encoding="utf-8"))
    return fixtures[schema_name]


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_runtime_schema_is_valid_draft_202012(schema_name: str) -> None:
    schema = load_schema(schema_name, schema_dir=ROOT / "schemas")
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"


@pytest.mark.parametrize("schema_name", sorted(SCHEMA_FILES))
def test_runtime_schema_matches_design_source_byte_for_byte(schema_name: str) -> None:
    filename = SCHEMA_FILES[schema_name]
    runtime = (ROOT / "schemas" / filename).read_bytes()
    design = (
        ROOT
        / "specs"
        / "000-universal-laptop-interaction-contract"
        / "contracts"
        / filename
    ).read_bytes()
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
