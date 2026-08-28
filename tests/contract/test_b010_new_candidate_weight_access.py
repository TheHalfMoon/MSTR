from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_MANIFEST = _ROOT / "artifacts" / "manifests" / "B010-new-candidate-weight-access.json"


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_b010_freezes_only_newly_admitted_equivalent_qualification_candidates() -> None:
    manifest = _load(_MANIFEST)
    assert manifest["task_id"] == "B010"
    assert manifest["state"] == "IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT"
    assert manifest["canonical_main_at_execution"] == "e3ee155a7e0ed491984908998546900e594bda9a"
    decision = manifest["decision"]
    assert decision["qualification_candidates"] == ["mellum-4b", "qwen3.5-0.8b-control"]
    assert decision["new_weight_access_required_candidates"] == [
        "mellum-4b",
        "qwen3.5-0.8b-control",
    ]
    assert decision["no_new_candidates_marker"] is None
    assert decision["no_new_access_marker"] is None

    source = {
        row["candidate_id"]: row
        for row in (
            _load(path) for path in sorted((_ROOT / "artifacts" / "candidates").glob("*.json"))
        )
    }
    envelopes = {row["candidate_id"]: row for row in manifest["candidate_access_envelopes"]}
    assert set(envelopes) == {"mellum-4b", "qwen3.5-0.8b-control"}
    for candidate_id, envelope in envelopes.items():
        candidate = source[candidate_id]
        assert candidate["status"] == "static_qualified"
        assert candidate["rights"]["decision"] == "pass_permissive"
        assert envelope["upstream_id"] == candidate["upstream_id"]
        assert envelope["exact_revision"] == candidate["upstream_revision"]
        assert envelope["qualification_required"] is True
        assert envelope["new_weight_access_required"] is True
        assert envelope["already_authorized_or_available_weight_artifacts"] is False


def test_b010_new_access_is_not_confused_with_prior_t028_or_b008_tokenizers() -> None:
    manifest = _load(_MANIFEST)
    prior = _load(_ROOT / "artifacts" / "manifests" / "T028-acquired-artifacts.json")
    prior_ids = {row["candidate_id"] for row in prior["candidates"]}
    expected_prior = {
        "granite-4.1-3b",
        "ministral-3-3b",
        "qwen2.5-coder-1.5b",
        "qwen3-4b",
        "qwen3.5-2b",
        "qwen3.5-4b",
        "smollm3-3b",
        "yi-coder-1.5b",
    }
    assert prior_ids == expected_prior
    access = set(manifest["decision"]["new_weight_access_required_candidates"])
    assert access.isdisjoint(prior_ids)

    b008 = (_ROOT / "evidence" / "mstr-000b" / "B008-tokenizer-economics.md").read_text(
        encoding="utf-8"
    )
    assert "MODEL_WEIGHT_ACCESS = NONE" in b008
    assert "tokenizer.json" in b008
    assert (
        "All temporary tokenizer files are deleted in the ephemeral runner before completion."
        in b008
    )
    for envelope in manifest["candidate_access_envelopes"]:
        assert (
            envelope["available_artifact_evidence"]["b008_scope"]
            == "TOKENIZER_JSON_ONLY_EPHEMERAL_AND_DESTROYED"
        )
        assert envelope["available_artifact_evidence"]["t028_contains_candidate"] is False


def test_b010_access_envelopes_bind_exact_weight_hashes_bytes_and_zero_cost() -> None:
    manifest = _load(_MANIFEST)
    envelopes = {row["candidate_id"]: row for row in manifest["candidate_access_envelopes"]}
    expected = {
        "mellum-4b": {
            "weight_bytes": 8038527904,
            "download_bytes": 8048099065,
            "weights": {
                "model-00001-of-00002.safetensors": (
                    4986625856,
                    "04bf4f574526ebecd75283af1f7ed0a412362388ddd28360c1581706cb3a00d2",
                ),
                "model-00002-of-00002.safetensors": (
                    3051902048,
                    "8fa0269d11332e13874280dbf5a15d5d6086d038656832c16e984544caf4b21b",
                ),
            },
        },
        "qwen3.5-0.8b-control": {
            "weight_bytes": 1746942600,
            "download_bytes": 1769897109,
            "weights": {
                "model.safetensors-00001-of-00001.safetensors": (
                    1746942600,
                    "c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c",
                ),
            },
        },
    }
    for candidate_id, facts in expected.items():
        envelope = envelopes[candidate_id]
        assert envelope["expected_weight_bytes"] == facts["weight_bytes"]
        assert envelope["expected_required_download_bytes"] == facts["download_bytes"]
        assert envelope["usd_ceiling"] == 0.0
        assert envelope["expected_usd"] == 0.0
        assert envelope["rights_status"]["gated_terms_acceptance_required"] is False
        assert envelope["rights_status"]["account_required"] is False
        weights = {
            row["path"]: (row["size_bytes"], row["sha256"])
            for row in envelope["required_files"]
            if row["artifact_class"] == "MODEL_WEIGHT"
        }
        assert weights == facts["weights"]
        assert "huggingface.co" in envelope["network_hosts"]
        assert "us.aws.cdn.hf.co" in envelope["network_hosts"]
        assert "AFTER_B011_EXACT_FOUNDER_AUTHORIZATION" in envelope["network_policy"]


def test_b010_remains_plan_only_and_requires_separate_b011_founder_authority() -> None:
    manifest = _load(_MANIFEST)
    handoff = manifest["b011_handoff"]
    assert handoff["requires_separate_founder_authorization"] is True
    assert handoff["authorized_by_b010"] is False
    assert "mellum-4b" in handoff["exact_authority_needed"]
    assert "qwen3.5-0.8b-control" in handoff["exact_authority_needed"]
    authority = manifest["authority_boundary"]
    assert authority["founder_machine_large_artifacts"] == 0
    for key, value in authority.items():
        if key != "founder_machine_large_artifacts":
            assert value is False, key
