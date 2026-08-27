from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "benchmarks" / "fixtures" / "tokenizer-economics" / "B007-corpus.json"
MANIFEST = ROOT / "benchmarks" / "manifests" / "B007-tokenizer-economics.json"
CORPUS_SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "b007-tokenizer-economics-corpus-v0.schema.json"
)
PROTOCOL_SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "b007-tokenizer-economics-protocol-v0.schema.json"
)

REQUIRED_CATEGORIES = [
    "python",
    "typescript",
    "javascript",
    "rust",
    "go",
    "java",
    "c",
    "cpp",
    "sql",
    "shell",
    "json",
    "yaml",
    "toml",
    "diff",
    "stack_trace",
    "file_paths",
    "tool_json",
]


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_strict(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys)
    assert isinstance(value, dict)
    return value


def _validator(path: Path) -> Draft202012Validator:
    schema = _load_strict(path)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def _git_blob_sha1(raw: bytes) -> str:
    prefix = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(prefix + raw).hexdigest()  # noqa: S324 - Git object identity, not security.


def test_b007_schemas_are_valid_and_current_artifacts_conform() -> None:
    corpus = _load_strict(CORPUS)
    manifest = _load_strict(MANIFEST)
    assert not list(_validator(CORPUS_SCHEMA).iter_errors(corpus))
    assert not list(_validator(PROTOCOL_SCHEMA).iter_errors(manifest))


def test_b007_corpus_file_and_decoded_entry_integrity() -> None:
    raw = CORPUS.read_bytes()
    corpus = _load_strict(CORPUS)
    manifest = _load_strict(MANIFEST)
    corpus_ref = manifest["corpus"]

    assert len(raw) == corpus_ref["fixture_file_bytes"]
    assert hashlib.sha256(raw).hexdigest() == corpus_ref["fixture_sha256"]
    assert _git_blob_sha1(raw) == corpus_ref["expected_git_blob_sha1"]

    entries = corpus["entries"]
    assert len(entries) == corpus_ref["entry_count"] == 34
    fixture_ids = [entry["fixture_id"] for entry in entries]
    assert len(fixture_ids) == len(set(fixture_ids))

    decoded_total = 0
    pins: list[dict[str, Any]] = []
    for entry in entries:
        content = entry["content_utf8"]
        assert isinstance(content, str)
        encoded = content.encode("utf-8")
        assert len(encoded) == entry["byte_count"]
        assert hashlib.sha256(encoded).hexdigest() == entry["sha256"]
        decoded_total += len(encoded)
        pins.append(
            {
                "fixture_id": entry["fixture_id"],
                "category": entry["category"],
                "profile": entry["profile"],
                "byte_count": entry["byte_count"],
                "sha256": entry["sha256"],
            }
        )

    assert decoded_total == corpus_ref["decoded_content_bytes"]
    assert pins == corpus_ref["entry_pins"]


def test_b007_category_profiles_and_distribution_are_stratified() -> None:
    corpus = _load_strict(CORPUS)
    manifest = _load_strict(MANIFEST)
    entries = corpus["entries"]

    assert manifest["corpus"]["required_categories"] == REQUIRED_CATEGORIES
    assert manifest["corpus"]["profiles_required"] == ["baseline", "adversarial"]

    category_counts = Counter(entry["category"] for entry in entries)
    assert category_counts == Counter({category: 2 for category in REQUIRED_CATEGORIES})

    for category in REQUIRED_CATEGORIES:
        profiles = {entry["profile"] for entry in entries if entry["category"] == category}
        assert profiles == {"baseline", "adversarial"}

    byte_counts = sorted(entry["byte_count"] for entry in entries)
    distribution = manifest["corpus"]["entry_byte_distribution"]
    assert distribution["min"] == byte_counts[0]
    assert distribution["max"] == byte_counts[-1]
    middle = (byte_counts[16] + byte_counts[17]) / 2
    assert distribution["median"] == middle

    summaries = manifest["corpus"]["category_summary"]
    assert [item["category"] for item in summaries] == REQUIRED_CATEGORIES
    for summary in summaries:
        category_entries = [entry for entry in entries if entry["category"] == summary["category"]]
        counts = [entry["byte_count"] for entry in category_entries]
        assert summary["entry_count"] == 2
        assert summary["decoded_bytes"] == sum(counts)
        assert summary["min_entry_bytes"] == min(counts)
        assert summary["max_entry_bytes"] == max(counts)
        assert summary["profiles"] == ["baseline", "adversarial"]


def test_b007_contains_adversarial_tokenization_sensitive_surfaces() -> None:
    corpus = _load_strict(CORPUS)
    adversarial = "\n".join(
        entry["content_utf8"] for entry in corpus["entries"] if entry["profile"] == "adversarial"
    )
    assert any(ord(character) > 127 for character in adversarial)
    assert "long_identifier_name_2026" in adversarial
    assert "VeryLongComponentName2026" in adversarial
    assert "<<'JSON'" in adversarial
    assert "&d" in adversarial and "<<: *d" in adversarial
    assert "[[replica]]" in adversarial
    assert "rename from" in adversarial and "Binary files" in adversarial
    assert "Caused by:" in adversarial
    assert "C:\\Users\\builder" in adversarial and "//server/share" in adversarial
    assert '"errors"' in adversarial and '"ranges"' in adversarial


def test_b007_protocol_fails_closed_if_authority_or_encoding_controls_are_weakened() -> None:
    manifest = _load_strict(MANIFEST)
    validator = _validator(PROTOCOL_SCHEMA)

    unsafe_authority = copy.deepcopy(manifest)
    unsafe_authority["authority"]["model_weight_access_authorized"] = True
    assert list(validator.iter_errors(unsafe_authority))

    unsafe_special_tokens = copy.deepcopy(manifest)
    unsafe_special_tokens["encoding_contract"]["add_special_tokens"] = True
    assert list(validator.iter_errors(unsafe_special_tokens))

    unsafe_claim = copy.deepcopy(manifest)
    unsafe_claim["claim_scope"] = "POPULATION_REPRESENTATIVE"
    assert list(validator.iter_errors(unsafe_claim))


def test_b007_corpus_schema_rejects_external_source_or_profile_drift() -> None:
    corpus = _load_strict(CORPUS)
    validator = _validator(CORPUS_SCHEMA)

    external = copy.deepcopy(corpus)
    external["external_source_content"] = True
    assert list(validator.iter_errors(external))

    bad_profile = copy.deepcopy(corpus)
    bad_profile["entries"][0]["profile"] = "representative"
    assert list(validator.iter_errors(bad_profile))
