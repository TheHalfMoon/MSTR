from __future__ import annotations

from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parents[2]
REPLAY = ROOT / "colab/mstr_t031_replay.py"


def test_pep440_release_zero_padding_is_semantically_equivalent() -> None:
    assert Version("13.0.3") == Version("13.0.3.0")


def test_replay_version_guard_uses_pep440_equivalence_without_weakening_wheel_identity() -> None:
    source = REPLAY.read_text(encoding="utf-8")

    assert "from packaging.version import Version;" in source
    assert "Version(actual[name])==Version(expected[name])" in source
    assert "assert actual==expected" not in source
    assert 'expected_sha256=entry["sha256"]' in source
    assert '"--no-index"' in source
    assert '"--no-deps"' in source
    assert "producer replay package-count binding drift detected" in source
