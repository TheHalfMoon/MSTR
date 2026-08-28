import json
from pathlib import Path

RESULT_DIR = Path("artifacts/results/tokenizer/B008")
REQUIRED = {
    "candidate_id",
    "tokenizer_id",
    "tokenizer_revision",
    "loaded_tokenizer_artifact_sha256_inventory",
    "tokenizer_implementation_id",
    "tokenizer_implementation_version",
    "measurement_runtime_identity",
    "effective_runtime_settings",
    "token_count_api_identity",
    "acquisition_source_and_provenance",
    "protocol_id",
    "corpus_fixture_sha256",
    "per_entry_metrics",
    "per_category_metrics",
    "aggregate_metrics",
    "structural_observations",
    "measurement_failures",
    "measured_at",
    "executor_identity",
}
CORPUS_SHA = "425456fa39ae5dc67214b4871b1ac948c63bf9f0ae72a1407a5908d4a5c9e1d6"


def _results():
    return [json.loads(path.read_text()) for path in sorted(RESULT_DIR.glob("*.json"))]


def test_b008_has_exact_static_qualified_candidate_set():
    expected = set()
    for path in Path("artifacts/candidates").glob("*.json"):
        data = json.loads(path.read_text())
        rights = data.get("rights", {})
        if (
            data.get("status") == "static_qualified"
            and rights.get("decision") == "pass_permissive"
            and rights.get("account_gate_required") is False
            and rights.get("clickthrough_gate_required") is False
        ):
            expected.add(data["candidate_id"])
    results = _results()
    assert len(results) == 10
    assert {row["candidate_id"] for row in results} == expected


def test_b008_results_satisfy_frozen_output_requirements():
    for row in _results():
        assert REQUIRED <= set(row)
        assert row["protocol_id"] == "MSTR-TOKENIZER-ECONOMICS-v0"
        assert row["corpus_fixture_sha256"] == CORPUS_SHA
        assert row["measurement_failures"] == []
        assert len(row["per_entry_metrics"]) == 34
        assert len(row["per_category_metrics"]) == 17
        inventory = row["loaded_tokenizer_artifact_sha256_inventory"]
        assert len(inventory) == 1
        assert inventory[0]["path"] == "tokenizer.json"
        assert len(inventory[0]["sha256"]) == 64
        assert inventory[0]["bytes"] > 0
        assert row["effective_runtime_settings"]["add_special_tokens"] is False
        assert row["effective_runtime_settings"]["padding"] == "NONE"
        assert row["effective_runtime_settings"]["truncation"] == "NONE"
        agg = row["aggregate_metrics"]
        assert agg["total_bytes"] == 3605
        assert agg["total_tokens"] > 0
        assert agg["weighted_bytes_per_token"] > 0
        assert agg["estimated_effective_payload_bytes_at_8192_tokens"] > 0


def test_identical_tokenizer_bytes_produce_identical_metrics():
    groups = {}
    for row in _results():
        digest = row["loaded_tokenizer_artifact_sha256_inventory"][0]["sha256"]
        groups.setdefault(digest, []).append(row)
    for rows in groups.values():
        first = rows[0]
        for row in rows[1:]:
            assert row["per_entry_metrics"] == first["per_entry_metrics"]
            assert row["per_category_metrics"] == first["per_category_metrics"]
            assert row["aggregate_metrics"] == first["aggregate_metrics"]
