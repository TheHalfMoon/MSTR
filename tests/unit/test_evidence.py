from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from mstr_qualify.errors import ArtifactIntegrityError, PolicyViolationError
from mstr_qualify.evidence import (
    canonical_json_bytes,
    finalize_evidence,
    load_finalized_evidence,
    supersede_evidence,
    validate_supersession_chain,
    write_finalized_evidence,
)


def test_canonical_json_is_order_independent_and_utf8() -> None:
    left = {"z": [True, None, 2.5], "unicode": "مرحبا", "a": 1}
    right = {"a": 1, "unicode": "مرحبا", "z": [True, None, 2.5]}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert b"\\u" not in canonical_json_bytes(left)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_canonical_json_rejects_non_finite_numbers(bad: float) -> None:
    with pytest.raises(PolicyViolationError, match="evidence.non_finite_number"):
        canonical_json_bytes({"bad": bad})


def test_canonical_json_rejects_non_json_values() -> None:
    with pytest.raises(PolicyViolationError, match="evidence.value_type"):
        canonical_json_bytes({"bad": (1, 2)})
    with pytest.raises(PolicyViolationError, match="evidence.object_key_type"):
        canonical_json_bytes({1: "bad"})


def test_finalize_is_deterministic_and_content_addressed() -> None:
    first = finalize_evidence("run", {"b": 2, "a": 1})
    second = finalize_evidence("run", {"a": 1, "b": 2})
    assert first.sha256 == second.sha256
    assert first.canonical_bytes == second.canonical_bytes
    assert len(first.sha256) == 64


def test_supersession_requires_reason_and_preserves_parent() -> None:
    original = finalize_evidence("run", {"score": 1})
    corrected = supersede_evidence(original, {"score": 2}, reason="verifier correction")
    assert corrected.sha256 != original.sha256
    assert corrected.supersedes == original.sha256
    with pytest.raises(PolicyViolationError, match="evidence.supersession_reason_missing"):
        finalize_evidence("run", {"score": 2}, supersedes=original.sha256)


def test_reason_without_parent_fails_closed() -> None:
    with pytest.raises(PolicyViolationError, match="evidence.supersession_reason_without_parent"):
        finalize_evidence("run", {"score": 1}, supersession_reason="orphan reason")


def test_write_is_write_once_and_idempotent(tmp_path: Path) -> None:
    evidence = finalize_evidence("run", {"score": 1})
    path = write_finalized_evidence(tmp_path, evidence)
    assert path.read_bytes() == evidence.canonical_bytes
    assert write_finalized_evidence(tmp_path, evidence) == path


def test_write_rejects_hash_mismatch(tmp_path: Path) -> None:
    evidence = finalize_evidence("run", {"score": 1})
    corrupt = replace(evidence, canonical_bytes=b"{}\n")
    with pytest.raises(ArtifactIntegrityError, match="evidence.hash_mismatch"):
        write_finalized_evidence(tmp_path, corrupt)


def test_existing_content_addressed_path_cannot_be_overwritten(tmp_path: Path) -> None:
    evidence = finalize_evidence("run", {"score": 1})
    target = tmp_path / f"{evidence.sha256}.json"
    target.write_bytes(b"different\n")
    with pytest.raises(ArtifactIntegrityError, match="evidence.immutable_conflict"):
        write_finalized_evidence(tmp_path, evidence)


def test_load_rejects_noncanonical_json(tmp_path: Path) -> None:
    path = tmp_path / "pretty.json"
    path.write_text('{"schema_version": "mstr.evidence-envelope.v1", "record_type":"x", "supersedes":null, "supersession_reason":null, "payload":{}}\n', encoding="utf-8")
    with pytest.raises(ArtifactIntegrityError, match="evidence.not_canonical"):
        load_finalized_evidence(path)


def test_supersession_chain_is_closed_and_acyclic() -> None:
    a = finalize_evidence("run", {"v": 1})
    b = supersede_evidence(a, {"v": 2}, reason="correction")
    c = supersede_evidence(b, {"v": 3}, reason="second correction")
    validate_supersession_chain([c, a, b])
    with pytest.raises(PolicyViolationError, match="evidence.supersession_parent_missing"):
        validate_supersession_chain([b])


def test_supersession_cycle_is_rejected() -> None:
    a = finalize_evidence("run", {"v": 1})
    b = finalize_evidence("run", {"v": 2})
    a_cycle = replace(a, supersedes=b.sha256)
    b_cycle = replace(b, supersedes=a.sha256)
    with pytest.raises(PolicyViolationError, match="evidence.supersession_cycle"):
        validate_supersession_chain([a_cycle, b_cycle])


def test_supersession_chain_rejects_forged_record_integrity() -> None:
    evidence = finalize_evidence("run", {"v": 1})
    forged = replace(evidence, canonical_bytes=b"{}\n")
    with pytest.raises(ArtifactIntegrityError, match="evidence.hash_mismatch"):
        validate_supersession_chain([forged])
