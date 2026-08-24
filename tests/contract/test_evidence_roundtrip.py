from __future__ import annotations

import json
from pathlib import Path

from mstr_qualify.evidence import (
    canonical_json_bytes,
    finalize_evidence,
    load_finalized_evidence,
    write_finalized_evidence,
)

FIXTURE = Path(__file__).parents[1] / "fixtures" / "evidence" / "canonical-envelope.json"


def test_golden_canonical_fixture_is_byte_stable() -> None:
    decoded = json.loads(FIXTURE.read_bytes())
    assert canonical_json_bytes(decoded) == FIXTURE.read_bytes()


def test_finalize_matches_golden_fixture() -> None:
    evidence = finalize_evidence("fixture", {"z": [True, None, 2.5], "unicode": "مرحبا", "a": 1})
    assert evidence.canonical_bytes == FIXTURE.read_bytes()


def test_write_load_roundtrip_preserves_identity(tmp_path: Path) -> None:
    original = finalize_evidence("fixture", {"a": 1})
    path = write_finalized_evidence(tmp_path, original)
    loaded = load_finalized_evidence(path)
    assert loaded == original
