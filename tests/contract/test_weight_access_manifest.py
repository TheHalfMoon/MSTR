"""T027 contract tests: the frozen weight-access preflight manifest.

These tests pin the fail-closed properties of
``artifacts/manifests/T027-weight-access.json`` against the
``weight-access-manifest`` schema. They exist so that T028 cannot drift:
unpinned revisions, missing integrity evidence, undeclared network hosts,
ambiguous gating state, missing retention/cleanup, or a missing cost
ceiling must all be structurally impossible on this authority surface.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import SCHEMA_FILES, load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "artifacts" / "manifests" / "T027-weight-access.json"
T022_DECISION_PATH = ROOT / "artifacts" / "decisions" / "T022-static-candidate-admission.json"

EXPECTED_CANDIDATE_IDS = {
    "qwen3.5-2b",
    "qwen3.5-4b",
    "ministral-3-3b",
    "qwen3-4b",
    "granite-4.1-3b",
    "smollm3-3b",
    "qwen2.5-coder-1.5b",
    "yi-coder-1.5b",
}

_WEIGHT_SUFFIXES = (".safetensors", ".bin")


@pytest.fixture(scope="module")
def manifest() -> dict:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    validate_instance("weight-access-manifest", data)
    return data


# ---------------------------------------------------------------------------
# Frozen-set integrity
# ---------------------------------------------------------------------------


def test_manifest_covers_exactly_the_t022_admitted_set(manifest: dict) -> None:
    ids = {c["candidate_id"] for c in manifest["candidates"]}
    t022 = json.loads(T022_DECISION_PATH.read_text(encoding="utf-8"))
    admitted = set(t022["payload"]["selected_candidate_ids"])
    # No silent removal and no silent addition of candidates.
    assert ids == admitted == EXPECTED_CANDIDATE_IDS


def test_all_revisions_are_immutable_40_hex_sha256_pins(manifest: dict) -> None:
    for candidate in manifest["candidates"]:
        revision = candidate["exact_revision"]
        assert len(revision) == 40
        int(revision, 16)  # raises if not hex
        forbidden = {"latest", "main", "master", "current"}
        assert revision.lower() not in forbidden


def test_every_weight_file_has_upstream_sha256_and_size(manifest: dict) -> None:
    for candidate in manifest["candidates"]:
        entries = candidate["expected_file_integrity"]
        weights = [e for e in entries if e["file"].endswith(_WEIGHT_SUFFIXES)]
        assert weights, f"{candidate['candidate_id']}: no weight files declared"
        declared_required = set(candidate["required_artifact_files"])
        for entry in weights:
            assert entry["file"] in declared_required
            sha = entry["upstream_sha256"]
            assert isinstance(sha, str) and len(sha) == 64
            int(sha, 16)
            assert entry["expected_size_bytes"] > 0


def test_integrity_entries_match_required_file_set(manifest: dict) -> None:
    """Every required file carries an integrity entry; no orphan entries."""
    for candidate in manifest["candidates"]:
        required = set(candidate["required_artifact_files"])
        integrity = {e["file"] for e in candidate["expected_file_integrity"]}
        assert required == integrity


def test_aggregate_budget_equals_sum_of_per_candidate_budgets(
    manifest: dict,
) -> None:
    per_candidate = manifest["storage_budget"]["per_candidate"]
    aggregate = manifest["storage_budget"]["aggregate"]
    assert sum(b["download_bytes_expected"] for b in per_candidate) == aggregate[
        "total_download_bytes"
    ]
    assert sum(b["on_disk_bytes_expected"] for b in per_candidate) == aggregate[
        "total_final_storage_bytes"
    ]
    assert aggregate["total_peak_storage_bytes"] >= aggregate[
        "total_final_storage_bytes"
    ]


def test_per_candidate_download_matches_declared_file_sizes(manifest: dict) -> None:
    budgets = {
        b["candidate_id"]: b for b in manifest["storage_budget"]["per_candidate"]
    }
    for candidate in manifest["candidates"]:
        expected = sum(
            e["expected_size_bytes"]
            for e in candidate["expected_file_integrity"]
        )
        actual = budgets[candidate["candidate_id"]]["download_bytes_expected"]
        assert expected == actual


# ---------------------------------------------------------------------------
# Network / access surface
# ---------------------------------------------------------------------------


def test_network_is_https_get_only_with_explicit_host_allowlist(
    manifest: dict,
) -> None:
    network = manifest["network"]
    assert network["method"] == "HTTPS_GET_ONLY"
    assert network["allowlist_hosts"], "host allowlist must not be empty"
    assert network["unauthorized_categories"], (
        "unauthorized categories must be enumerated"
    )


def test_per_candidate_hosts_are_within_the_global_allowlist(
    manifest: dict,
) -> None:
    allowlist = set(manifest["network"]["allowlist_hosts"])
    for candidate in manifest["candidates"]:
        assert set(candidate["artifact_source_hosts"]) <= allowlist
        assert set(candidate["network_hosts_required_for_acquisition"]) <= allowlist


def test_no_candidate_requires_account_gating_or_terms_acceptance(
    manifest: dict,
) -> None:
    for candidate in manifest["candidates"]:
        for flag in (
            "authentication_required",
            "account_required",
            "gated_access",
            "clickthrough_required",
            "terms_acceptance_required",
        ):
            assert candidate[flag] is False, (
                f"{candidate['candidate_id']}: {flag} would require founder "
                "authorization before T028"
            )
        assert candidate["rights_decision"] == "READY_FOR_T028"


# ---------------------------------------------------------------------------
# Governance boundaries
# ---------------------------------------------------------------------------


def test_runtime_quantizer_status_never_claims_selection(manifest: dict) -> None:
    for candidate in manifest["candidates"]:
        assert candidate["runtime_quantizer_status"] == (
            "CANDIDATE_ONLY_NEEDS_T029_T030"
        )


def test_cost_ceiling_is_zero_everywhere(manifest: dict) -> None:
    cost_block = manifest["cost"]
    assert "USD 0.00" in cost_block["expected_monetary_cost"]
    for candidate in manifest["candidates"]:
        assert candidate["expected_monetary_cost"].strip().startswith("USD 0")
        assert "PAID_ACCESS" in candidate["cost_ceiling"] or "USD 0" in candidate[
            "cost_ceiling"
        ]


def test_retention_cleanup_and_git_exclusion_fully_declared(
    manifest: dict,
) -> None:
    top = manifest["retention_cleanup"]
    for field in (
        "retention_policy",
        "cleanup_policy",
        "cache_policy",
        "artifact_location_policy",
        "git_exclusion_summary",
    ):
        assert top[field].strip()
    git_block = manifest["git_exclusion"]
    assert any("safetensors" in pattern for pattern in git_block["weights_ignored"])
    assert any(
        "external" in path for path in git_block["gitignore_covers"]
    ), "acquired binaries must live under a gitignored external directory"


def test_t028_authority_envelope_blocks_automatic_start(manifest: dict) -> None:
    envelope = manifest["proposed_t028_authority_envelope"]
    assert "founder" in envelope["stays_blocked_until"].lower()
    assert envelope["what_T028_does_not"], "prohibitions must be explicit"


def test_no_candidate_claims_final_or_qualified_language(manifest: dict) -> None:
    prohibited = ("LOCAL_QUALIFIED", "FINALIST", "BACKBONE_WINNER")
    blob = json.dumps(manifest)
    for term in prohibited:
        assert term not in blob, f"T027 must not claim {term}"


def test_caveated_candidates_record_live_license_reverification(
    manifest: dict,
) -> None:
    caveated = {"ministral-3-3b", "granite-4.1-3b", "smollm3-3b"}
    by_id = {c["candidate_id"]: c for c in manifest["candidates"]}
    for cid in caveated:
        evidence_text = by_id[cid]["rights_decision_evidence"]
        assert "Re-verified live at pinned revision" in evidence_text
        assert "apache-2.0" in evidence_text.lower()


# ---------------------------------------------------------------------------
# Fail-closed mutations (schema-level rejections)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mutate", "fragment"),
    [
        (
            lambda m: m["candidates"][0].update(exact_revision="main"),
            "exact_revision",
        ),
        (
            lambda m: m["network"].update(allowlist_hosts=[]),
            "allowlist_hosts",
        ),
        (
            lambda m: m["candidates"][0].update(expected_file_integrity=[]),
            "expected_file_integrity",
        ),
        (
            lambda m: m["cost"].update(expected_monetary_cost=""),
            "expected_monetary_cost",
        ),
        (
            lambda m: m["retention_cleanup"].update(cleanup_policy=""),
            "cleanup_policy",
        ),
        (
            lambda m: m["candidates"][0].pop("license_evidence_url"),
            "license_evidence_url",
        ),
        (
            lambda m: m["candidates"][0].pop("failure_behavior"),
            "failure_behavior",
        ),
    ],
)
def test_structural_mutations_fail_closed(mutate, fragment: str) -> None:
    base = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    mutate(base)
    errors = _validation_errors(base)
    assert errors, f"mutation touching {fragment} must be rejected"
    assert fragment in "\n".join(errors)


def test_schema_rejects_moving_refs_by_pattern() -> None:
    schema = load_schema("weight-access-manifest")
    pattern = schema["$defs"]["candidate_entry"]["properties"]["exact_revision"][
        "pattern"
    ]
    import re

    for bad in ("latest", "main", "current model version", "release"):
        assert re.search(pattern, bad) is None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validation_errors(instance: object) -> tuple[str, ...]:
    from mstr_qualify.schemas import validation_errors as errs

    return errs("weight-access-manifest", instance)


def test_weight_access_schema_is_registered() -> None:
    assert "weight-access-manifest" in SCHEMA_FILES
