"""T028 storage-architecture amendment contract tests.

Pins the zero-large-artifact founder-environment decision:
- the amendment binds to the exact frozen T027 manifest by path/id/SHA-256;
- candidate identities, revisions, hashes, rights, network scope, and the
  USD 0.00 cost ceiling are declared unchanged;
- ephemeral runner semantics are fail-closed (pinned-only, HTTPS GET, hash
  verification, report-as-durable-output);
- the founder Mac receives only code/config/manifest/hash/metric/evidence/report
  artifacts and never model binaries.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance

ROOT = Path(__file__).resolve().parents[2]
AMENDMENT_PATH = ROOT / "artifacts" / "manifests" / "T028-storage-amendment.json"
T027_PATH = ROOT / "artifacts" / "manifests" / "T027-weight-access.json"


@pytest.fixture(scope="module")
def amendment() -> dict:
    data = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8"))
    validate_instance("storage-amendment", data)
    return data


def test_amendment_binds_to_exact_frozen_t027_manifest_bytes(amendment: dict) -> None:
    """Schema pins the exact frozen bytes; instance must equal the on-disk hash."""
    from mstr_qualify.schemas import load_schema

    schema = load_schema("storage-amendment")
    pinned = schema["properties"]["amends_manifest"]["properties"]["sha256"]["const"]
    assert amendment["amends_manifest"]["sha256"] == pinned
    actual = hashlib.sha256(T027_PATH.read_bytes()).hexdigest()
    assert amendment["amends_manifest"]["sha256"] == actual
    assert amendment["amends_manifest"]["path"] == str(
        T027_PATH.relative_to(ROOT).as_posix()
    )
    assert (
        amendment["amends_manifest"]["manifest_id"]
        == "T027-weight-access-preflight-frozen"
    )


def test_all_acquisition_authority_fields_declared_unchanged(amendment: dict) -> None:
    unchanged = set(amendment["amends_manifest"]["unchanged_fields"])
    required = {
        "candidates",
        "exact_model_ids",
        "exact_revisions",
        "expected_file_integrity",
        "rights_decisions",
        "network_allowlist",
        "gating_status",
        "cost_ceiling",
    }
    assert required <= unchanged


def test_founder_mac_is_zero_large_artifact(amendment: dict) -> None:
    assert amendment["policy"]["founder_mac_large_artifacts"] == "ZERO"
    assert amendment["policy"]["supersedes_local_retention_clause"] is True
    mac_receives = set(amendment["mac_receives"])
    assert {"MANIFESTS", "HASHES", "EVIDENCE", "REPORTS"} <= mac_receives
    assert "MODEL_BINARIES_ON_FOUNDER_MAC" in amendment["prohibitions"]
    assert "MODEL_BINARIES_IN_GIT" in amendment["prohibitions"]


def test_every_executor_is_ephemeral_free_and_unauthenticated(
    amendment: dict,
) -> None:
    assert amendment["approved_executors"], "at least one executor required"
    for executor in amendment["approved_executors"]:
        assert executor["kind"] == "EPHEMERAL_CLOUD_RUNNER"
        assert executor["network_scope"] == "HTTPS_GET_ONLY_PER_T027_ALLOWLIST"
        assert executor["authentication_required"] is False
        assert executor["monetary_cost"].startswith("USD 0")


def test_runner_contract_pins_fail_closed_semantics(amendment: dict) -> None:
    contract = amendment["ephemeral_runner_contract"]
    assert contract["authority_source"] == (
        "ARTIFACTS_MANIFESTS_T027_WEIGHT_ACCESS_JSON_ONLY"
    )
    assert contract["fetch_method"] == "HTTPS_GET_ONLY"
    assert "HARD_CANDIDATE_FAILURE" in contract["integrity_rule"]
    assert contract["local_copy_lifetime"].startswith("RUN_DURATION_ONLY")
    assert contract["substitute_revisions_allowed"] is False
    assert contract["latest_refs_allowed"] is False
    assert contract["unrelated_files_allowed"] is False


def test_cost_ceiling_remains_zero(amendment: dict) -> None:
    assert amendment["cost_ceiling"]["acquisition_cost"] == "USD 0.00"


def test_canonical_base_is_immutable_pin(amendment: dict) -> None:
    revision = amendment["canonical_base"]
    assert len(revision) == 40
    int(revision, 16)


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (lambda m: m.update(schema_version="mstr.weight-access-manifest.v1"), "schema_version"),
        (lambda m: m.update(canonical_base="latest"), "canonical_base"),
        (lambda m: m["amends_manifest"].update(sha256="c" * 64), "sha256"),
        (
            lambda m: m["amends_manifest"].update(
                path="artifacts/manifests/other.json"
            ),
            "amends_manifest.path",
        ),
        (
            lambda m: m["policy"].update(founder_mac_large_artifacts="SOME"),
            "founder_mac_large_artifacts",
        ),
        (
            lambda m: m["ephemeral_runner_contract"].pop("required_report_identity"),
            "required_report_identity",
        ),
        (lambda m: m["approved_executors"][0].update(monetary_cost="USD 5.00"), "monetary_cost"),
        (lambda m: m["ephemeral_runner_contract"].update(fetch_method="ANY_HTTP"), "fetch_method"),
        (lambda m: m["cost_ceiling"].update(acquisition_cost="USD 1.00"), "acquisition_cost"),
    ],
)
def test_structural_mutations_fail_closed(mutate, fragment: str) -> None:
    base = json.loads(AMENDMENT_PATH.read_text(encoding="utf-8"))
    mutate(base)
    from mstr_qualify.schemas import validation_errors

    errors = validation_errors("storage-amendment", base)
    assert errors, f"mutation touching {fragment} must be rejected"
    assert fragment in "\n".join(errors)
