from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.errors import SchemaValidationError
from mstr_qualify.schemas import load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
NAMES = (
    "mstr-environment-manifest-v0",
    "mstr-setup-manifest-v0",
    "mstr-verifier-manifest-v0",
)


def _fixture(kind: str, name: str) -> dict[str, object]:
    path = ROOT / "tests" / "fixtures" / "schemas" / kind / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", NAMES)
def test_design_and_runtime_contracts_are_byte_identical(name: str) -> None:
    runtime = ROOT / "schemas" / f"{name}.schema.json"
    design = (
        ROOT
        / "specs"
        / "001-agent-harness-verified-loop-foundation"
        / "contracts"
        / f"{name}.schema.json"
    )
    assert runtime.read_bytes() == design.read_bytes()


@pytest.mark.parametrize("name", NAMES)
def test_known_good_contract_fixture_is_valid(name: str) -> None:
    validate_instance(name, _fixture("valid", name))


@pytest.mark.parametrize("name", NAMES)
def test_known_bad_contract_fixture_fails_closed(name: str) -> None:
    with pytest.raises(SchemaValidationError):
        validate_instance(name, _fixture("invalid", name))


def test_environment_contract_rejects_implicit_network_authority() -> None:
    value = _fixture("valid", "mstr-environment-manifest-v0")
    effect = value["effect_policy"]
    assert isinstance(effect, dict)
    effect["network_access"] = "ALLOWLIST"
    effect["allowed_hosts"] = ["example.com"]
    effect["authority_id"] = None
    with pytest.raises(SchemaValidationError):
        validate_instance("mstr-environment-manifest-v0", value)


def test_verifier_contract_cannot_replace_a006_success_authority() -> None:
    schema = load_schema("mstr-verifier-manifest-v0")
    assert schema["properties"]["finalizer_contract_id"]["const"] == "A006_PROTECTED_FINALIZER"
    assert schema["properties"]["success_semantics"]["const"] == "VERIFIER_EVIDENCE_ONLY"
