"""Unit tests for artifact manifest/hash verification (T024)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from mstr_qualify.artifacts import (
    MANIFEST_SCHEMA_VERSION,
    ArtifactFileEntry,
    ArtifactManifest,
    load_artifact_manifest,
    parse_artifact_manifest,
    summarize_verified,
    verify_artifact,
)
from mstr_qualify.errors import ArtifactIntegrityError

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "artifacts"
VALID_FIXTURE_DIR = FIXTURE_ROOT / "valid"

ALPHA_SHA = "1956e00312d912f86659c43cb2db601dd4999edaabf77448c6bbe423154c2d5b"


def _entry(
    path: str = "alpha.txt",
    sha: str = ALPHA_SHA,
    size: int | None = None,
) -> ArtifactFileEntry:
    return ArtifactFileEntry(relative_path=path, sha256=sha, size_bytes=size)


def _manifest(entries: tuple[ArtifactFileEntry, ...] | None = None) -> ArtifactManifest:
    if entries is None:
        entries = (_entry(),)
    return ArtifactManifest(artifact_id="artifact-x", format_name="fixture-format", entries=entries)


def _make_tree(tmp_path: Path) -> Path:
    root = tmp_path / "artifact"
    root.mkdir()
    (root / "alpha.txt").write_text("alpha artifact payload\n", encoding="utf-8")
    return root


class TestManifestLoading:
    def test_valid_fixture_manifest_loads_and_sorts_deterministically(self) -> None:
        manifest = load_artifact_manifest(VALID_FIXTURE_DIR / "manifest.json")
        assert manifest.artifact_id == "fixture-artifact-1"
        assert manifest.format_name == "fixture-format"
        paths = [entry.relative_path for entry in manifest.sorted_entries]
        assert paths == sorted(paths)
        assert len(manifest.entries) == 2

    def test_malformed_json_fails_closed(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        with pytest.raises(ArtifactIntegrityError, match="not valid JSON"):
            load_artifact_manifest(bad)

    def test_non_object_root_fails_closed(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text("[1, 2]", encoding="utf-8")
        with pytest.raises(ArtifactIntegrityError, match="root"):
            load_artifact_manifest(bad)

    def test_wrong_schema_version_rejected(self) -> None:
        with pytest.raises(ArtifactIntegrityError, match="schema_version"):
            parse_artifact_manifest({"schema_version": "mstr.other.v9"})

    @pytest.mark.parametrize("field", ["artifact_id", "format_name", "files"])
    def test_missing_required_field_rejected(self, field: str) -> None:
        data = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "artifact_id": "a",
            "format_name": "f",
            "files": [{"path": "p.bin", "sha256": "a" * 64}],
        }
        del data[field]
        with pytest.raises(ArtifactIntegrityError, match="required field"):
            parse_artifact_manifest(data)

    def test_duplicate_entry_identity_rejected(self) -> None:
        entry = {"path": "same.bin", "sha256": "a" * 64}
        data = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "artifact_id": "a",
            "format_name": "f",
            "files": [dict(entry), dict(entry)],
        }
        with pytest.raises(ArtifactIntegrityError, match="duplicate"):
            parse_artifact_manifest(data)

    def test_entry_missing_sha256_rejected(self) -> None:
        data = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "artifact_id": "a",
            "format_name": "f",
            "files": [{"path": "p.bin"}],
        }
        with pytest.raises(ArtifactIntegrityError, match="missing required fields"):
            parse_artifact_manifest(data)


class TestPathSafetyAtLoadTime:
    @pytest.mark.parametrize(
        "path",
        [
            "../escape.txt",
            "/absolute/path.txt",
            "C:\\\\evil.txt",
            "back\\\\slash.txt",
            "nested/../traversal.txt",
            "./dot.txt",
            "",
            " padded.txt",
        ],
    )
    def test_unsafe_paths_fail_closed(self, path: str) -> None:
        with pytest.raises(ArtifactIntegrityError):
            _entry(path=path)


class TestVerification:
    def test_exact_match_passes_with_report(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        report = verify_artifact(_manifest((_entry(size=23),)), root)
        assert report["verified"] is True
        assert report["file_count"] == 1
        assert report["total_bytes"] == 23
        assert report["files"][0]["sha256"] == ALPHA_SHA

    def test_hash_mismatch_fails_closed(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        (root / "alpha.txt").write_text("tampered\n", encoding="utf-8")
        with pytest.raises(ArtifactIntegrityError, match="SHA-256 mismatch"):
            verify_artifact(_manifest(), root)

    def test_size_mismatch_fails_closed_when_declared(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        with pytest.raises(ArtifactIntegrityError, match="size mismatch"):
            verify_artifact(_manifest((_entry(size=999),)), root)

    def test_undeclared_size_skips_size_check_but_still_hashes(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        report = verify_artifact(_manifest((_entry(size=None),)), root)
        assert report["total_bytes"] == 23

    def test_missing_file_fails_closed(self, tmp_path: Path) -> None:
        root = tmp_path / "empty-root"
        root.mkdir()
        with pytest.raises(ArtifactIntegrityError, match="missing"):
            verify_artifact(_manifest(), root)

    def test_symlinked_declared_file_rejected(self, tmp_path: Path) -> None:
        real_dir = tmp_path / "real"
        real_dir.mkdir()
        (real_dir / "alpha.txt").write_text("alpha artifact payload\n", encoding="utf-8")
        root = tmp_path / "linkroot"
        root.mkdir()
        os.symlink(real_dir / "alpha.txt", root / "alpha.txt")
        with pytest.raises(ArtifactIntegrityError, match="symlink"):
            verify_artifact(_manifest(), root)

    def test_traversal_escape_via_resolution_rejected(self, tmp_path: Path) -> None:
        # Constructed directly to bypass the load-time guard and prove the
        # resolve-time traversal protection independently.
        entry = ArtifactFileEntry.__new__(ArtifactFileEntry)
        object.__setattr__(entry, "relative_path", "../outside.txt")
        object.__setattr__(entry, "sha256", ALPHA_SHA)
        object.__setattr__(entry, "size_bytes", None)
        root = _make_tree(tmp_path)
        with pytest.raises(ArtifactIntegrityError, match="escape"):
            verify_artifact(_manifest((entry,)), root)

    def test_unexpected_extra_file_fails_closed(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        (root / "surprise.txt").write_text("extra\n", encoding="utf-8")
        (root / "sub").mkdir()
        (root / "sub" / "deep.txt").write_text("deep extra\n", encoding="utf-8")
        with pytest.raises(ArtifactIntegrityError, match="unexpected files"):
            verify_artifact(_manifest(), root)

    def test_nonexistent_root_fails_closed(self, tmp_path: Path) -> None:
        with pytest.raises(ArtifactIntegrityError, match="root"):
            verify_artifact(_manifest(), tmp_path / "does-not-exist")

    def test_empty_manifest_rejected_at_construction(self) -> None:
        with pytest.raises(ArtifactIntegrityError, match="at least one file"):
            _manifest(entries=())

    def test_directory_in_place_of_file_fails_closed(self, tmp_path: Path) -> None:
        root = tmp_path / "dirroot"
        (root / "alpha.txt").mkdir(parents=True)
        with pytest.raises(ArtifactIntegrityError, match="regular file|missing"):
            verify_artifact(_manifest(), root)


class TestSummary:
    def test_summary_is_deterministic(self, tmp_path: Path) -> None:
        root = _make_tree(tmp_path)
        report = verify_artifact(_manifest((_entry(size=23),)), root)
        first = summarize_verified(report)
        second = summarize_verified(verify_artifact(_manifest((_entry(size=23),)), root))
        assert first == second
        assert "artifact-x" in first


class TestJsonRoundTripOfValidFixture:
    def test_fixture_manifest_json_matches_parsed_shape(self) -> None:
        decoded = json.loads((VALID_FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8"))
        parsed = parse_artifact_manifest(decoded)
        assert {e.relative_path for e in parsed.entries} == {"alpha.txt", "nested/beta.bin"}
