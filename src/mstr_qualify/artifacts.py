"""Local artifact manifest loading and fail-closed integrity verification.

T024 verifies manifests/files supplied locally. This module never fetches
weights and never touches the network: it validates exact artifact identity
(SHA-256, declared size) against files already present on local storage.
Any mismatch, missing file, unexpected file, malformed manifest, path
traversal attempt, symlink entry, or duplicate identity fails closed.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .errors import ArtifactIntegrityError, IdentityError
from .ids import sha256_file, validate_sha256

MANIFEST_SCHEMA_VERSION = "mstr.artifact-manifest.v1"

_TRAVERSAL_COMPONENTS = frozenset({".", ".."})


def _fail(
    message: str,
    code: str,
    details: Mapping[str, object] | None = None,
) -> ArtifactIntegrityError:
    return ArtifactIntegrityError(message, code=code, details=details)


@dataclass(frozen=True, slots=True)
class ArtifactFileEntry:
    """One manifest-declared file with its mandatory integrity identity."""

    relative_path: str
    sha256: str
    size_bytes: int | None

    def __post_init__(self) -> None:
        try:
            validate_sha256(self.sha256)
        except IdentityError as exc:
            raise _fail(
                "artifact entry sha256 is not a canonical SHA-256 identity",
                code="artifact.entry_sha256",
                details={"path": self.relative_path, "reason": str(exc)},
            ) from exc
        if not self.relative_path or self.relative_path.strip() != self.relative_path:
            raise _fail(
                "artifact file path must be non-empty with no surrounding whitespace",
                code="artifact.entry_path",
                details={"path": self.relative_path},
            )
        _validate_relative_path(self.relative_path)
        if self.size_bytes is not None and self.size_bytes < 0:
            raise _fail(
                "declared size must be non-negative when present",
                code="artifact.entry_size",
                details={"size": self.size_bytes},
            )


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    """Exact artifact identity: one artifact id plus a deterministic file set."""

    artifact_id: str
    format_name: str
    entries: tuple[ArtifactFileEntry, ...]

    @property
    def sorted_entries(self) -> tuple[ArtifactFileEntry, ...]:
        return tuple(sorted(self.entries, key=lambda entry: entry.relative_path))

    def __post_init__(self) -> None:
        if not self.artifact_id or self.artifact_id.strip() != self.artifact_id:
            raise _fail(
                "artifact_id must be non-empty with no surrounding whitespace",
                code="artifact.manifest_id",
            )
        if not self.format_name or self.format_name.strip() != self.format_name:
            raise _fail(
                "format_name must be non-empty with no surrounding whitespace",
                code="artifact.manifest_format",
            )
        if not self.entries:
            raise _fail(
                "artifact manifest must declare at least one file entry",
                code="artifact.manifest_empty",
            )
        paths = [entry.relative_path for entry in self.entries]
        if len(set(paths)) != len(paths):
            duplicates = sorted({p for p in paths if paths.count(p) > 1})
            raise _fail(
                "duplicate file identity in manifest is prohibited",
                code="artifact.duplicate_entry",
                details={"paths": ",".join(duplicates)},
            )


def _validate_relative_path(value: str) -> None:
    """Reject absolute paths, traversal components, and separator hazards."""
    # Raw-component checks run before PurePosixPath normalization so that
    # repeated separators, dot components, and empties cannot collapse into
    # an apparently valid path.
    raw_parts = value.split("/")
    for part in raw_parts:
        if part in _TRAVERSAL_COMPONENTS:
            raise _fail(
                "path traversal components are prohibited in artifact manifests",
                code="artifact.path_traversal",
                details={"path": value, "component": part},
            )
        if part == "":
            raise _fail(
                "empty path components (repeated separators) are prohibited",
                code="artifact.path_component_empty",
                details={"path": value},
            )
    pure = PurePosixPath(value)
    if pure.is_absolute() or value.startswith("/") or value.startswith("\\"):
        raise _fail(
            "absolute artifact file paths are prohibited",
            code="artifact.path_absolute",
            details={"path": value},
        )
    if value.startswith("./") or value == ".":
        raise _fail(
            "relative-dot artifact path components are prohibited",
            code="artifact.path_dot_component",
            details={"path": value},
        )
    if "\\" in value or "\x00" in value:
        raise _fail(
            "artifact file paths must use POSIX separators only",
            code="artifact.path_separator",
            details={"path": value},
        )
    for part in pure.parts:
        if not part.strip():
            raise _fail(
                "empty path components are prohibited",
                code="artifact.path_component_empty",
                details={"path": value},
            )
        if os.path.isabs(part):
            # Windows drive-letter style component (e.g. "C:") caught here.
            raise _fail(
                "absolute-style path component is prohibited",
                code="artifact.path_component_absolute",
                details={"path": value, "component": part},
            )


def parse_artifact_manifest(data: Mapping[str, Any]) -> ArtifactManifest:
    """Build an :class:`ArtifactManifest` from decoded JSON data, fail-closed."""
    schema_version = data.get("schema_version")
    if schema_version != MANIFEST_SCHEMA_VERSION:
        raise _fail(
            "unsupported artifact manifest schema_version",
            code="artifact.schema_version",
            details={"found": str(schema_version), "expected": MANIFEST_SCHEMA_VERSION},
        )

    for field in ("artifact_id", "format_name", "files"):
        if field not in data:
            raise _fail(
                "artifact manifest is missing a required field",
                code="artifact.manifest_missing_field",
                details={"field": field},
            )

    for field in ("artifact_id", "format_name"):
        if not isinstance(data[field], str):
            raise _fail(
                "artifact manifest identity fields must be strings",
                code="artifact.manifest_field_type",
                details={"field": field},
            )

    raw_files = data["files"]
    if not isinstance(raw_files, list) or not raw_files:
        raise _fail(
            "artifact manifest files must be a non-empty list",
            code="artifact.files_type",
        )

    entries: list[ArtifactFileEntry] = []
    seen_paths: set[str] = set()
    for item in raw_files:
        if not isinstance(item, dict):
            raise _fail(
                "each artifact file entry must be an object",
                code="artifact.entry_type",
            )
        missing = {"path", "sha256"} - set(item)
        if missing:
            raise _fail(
                "artifact file entry is missing required fields",
                code="artifact.entry_missing_field",
                details={"fields": ",".join(sorted(missing))},
            )
        path = item["path"]
        sha256 = item["sha256"]
        if not isinstance(path, str) or not isinstance(sha256, str):
            raise _fail(
                "artifact entry path and sha256 must be strings",
                code="artifact.entry_field_type",
            )
        size_raw = item.get("size_bytes")
        if isinstance(size_raw, bool) or (size_raw is not None and not isinstance(size_raw, int)):
            raise _fail(
                "artifact entry size_bytes must be an integer when present",
                code="artifact.entry_size_type",
                details={"value": repr(size_raw)},
            )
        if path in seen_paths:
            raise _fail(
                "duplicate file identity in manifest is prohibited",
                code="artifact.duplicate_entry",
                details={"paths": path},
            )
        seen_paths.add(path)
        entries.append(ArtifactFileEntry(relative_path=path, sha256=sha256, size_bytes=size_raw))

    return ArtifactManifest(
        artifact_id=data["artifact_id"],
        format_name=data["format_name"],
        entries=tuple(entries),
    )


def load_artifact_manifest(path: Path) -> ArtifactManifest:
    """Load and validate an artifact manifest from local JSON storage."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _fail(
            "unable to read artifact manifest",
            "artifact.manifest_read",
            details={"path": str(path)},
        ) from exc
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _fail(
            "artifact manifest is not valid JSON",
            code="artifact.manifest_json_invalid",
            details={"path": str(path), "line": exc.lineno, "column": exc.colno},
        ) from exc
    if not isinstance(decoded, dict):
        raise _fail("artifact manifest root must be a JSON object", "artifact.manifest_root")
    return parse_artifact_manifest(decoded)


def _resolve_under_root(root: Path, relative_path: str) -> Path:
    candidate = root / relative_path
    try:
        resolved_root = root.resolve()
        resolved_candidate = candidate.resolve()
    except OSError as exc:
        raise _fail(
            "unable to resolve artifact path inside verification root",
            code="artifact.path_resolve_failed",
            details={"path": relative_path, "reason": str(exc)},
        ) from exc
    if resolved_candidate == resolved_root or resolved_root not in resolved_candidate.parents:
        raise _fail(
            "resolved artifact path escapes the verification root",
            code="artifact.path_escape",
            details={"path": relative_path},
        )
    return candidate


def verify_artifact(manifest: ArtifactManifest, root: Path) -> dict[str, Any]:
    """Verify every declared file against the local tree, failing closed.

    Verification semantics:

    - every declared file must exist as a regular file inside ``root``;
    - symlinks are rejected outright (explicit policy: no link following);
    - SHA-256 must match exactly; declared size must match when present;
    - the on-disk file set must equal the declared set exactly — extra
      unexpected files are a failure;
    - any failure raises :class:`ArtifactIntegrityError`; a bad artifact can
      never silently normalize into PASS.

    Returns the verified identity report on success.
    """
    if root.is_symlink():
        raise _fail(
            "symlinked verification roots are prohibited",
            code="artifact.symlink_rejected",
            details={"path": str(root)},
        )
    if not root.is_dir():
        raise _fail(
            "verification root must be an existing directory",
            "artifact.root_missing",
            details={"path": str(root)},
        )

    verified_files: list[dict[str, Any]] = []
    declared_paths = {entry.relative_path for entry in manifest.entries}
    for entry in manifest.sorted_entries:
        candidate = root / entry.relative_path
        # Explicit policy: symlinks are never followed anywhere in the tree.
        if candidate.is_symlink():
            raise _fail(
                "symlinked artifact files are prohibited",
                code="artifact.symlink_rejected",
                details={"path": entry.relative_path},
            )
        _resolve_under_root(root, entry.relative_path)
        _reject_intermediate_symlinks(root, entry.relative_path)
        if not candidate.is_file():
            raise _fail(
                "declared artifact file is missing or not a regular file",
                code="artifact.missing_file",
                details={"path": entry.relative_path},
            )
        actual_size = candidate.stat().st_size
        if entry.size_bytes is not None and actual_size != entry.size_bytes:
            raise _fail(
                "artifact file size mismatch",
                code="artifact.size_mismatch",
                details={
                    "path": entry.relative_path,
                    "expected": entry.size_bytes,
                    "actual": actual_size,
                },
            )
        actual_sha256 = _hash_file_checked(candidate, entry.relative_path)
        if actual_sha256 != entry.sha256:
            raise _fail(
                "artifact file SHA-256 mismatch",
                code="artifact.hash_mismatch",
                details={
                    "path": entry.relative_path,
                    "expected": entry.sha256,
                    "actual": actual_sha256,
                },
            )
        verified_files.append(
            {
                "path": entry.relative_path,
                "sha256": actual_sha256,
                "size_bytes": actual_size,
            }
        )

    unexpected = sorted(_discover_relative_files(root) - declared_paths)
    if unexpected:
        raise _fail(
            "unexpected files present in artifact directory",
            code="artifact.unexpected_file",
            details={"paths": ",".join(unexpected[:16]), "count": len(unexpected)},
        )

    return {
        "artifact_id": manifest.artifact_id,
        "format_name": manifest.format_name,
        "verified": True,
        "file_count": len(verified_files),
        "total_bytes": sum(int(item["size_bytes"]) for item in verified_files),
        "files": verified_files,
    }


def _reject_intermediate_symlinks(root: Path, relative_path: str) -> None:
    """Reject symlinked intermediate directories along a declared file path."""
    parts = relative_path.split("/")
    for index in range(1, len(parts)):
        intermediate = root.joinpath(*parts[:index])
        if intermediate.is_symlink():
            raise _fail(
                "symlinked directories inside artifact trees are prohibited",
                code="artifact.symlink_rejected",
                details={"path": "/".join(parts[:index])},
            )


def _hash_file_checked(path: Path, relative_path: str) -> str:
    """Hash a local file, converting identity failures to artifact failures."""
    try:
        return sha256_file(path)
    except IdentityError as exc:
        raise _fail(
            "unable to hash declared artifact file",
            code="artifact.file_hash_read",
            details={"path": relative_path, "reason": str(exc)},
        ) from exc


def _discover_relative_files(root: Path) -> set[str]:
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Deterministic ordering regardless of OS directory enumeration.
        dirnames.sort()
        base = Path(dirpath)
        # Explicit policy: directory symlinks are rejected too; os.walk with
        # followlinks=False lists them here so they can never be traversed.
        for name in sorted(dirnames):
            if (base / name).is_symlink():
                raise _fail(
                    "symlinked directories inside artifact trees are prohibited",
                    code="artifact.symlink_rejected",
                    details={"path": (base / name).relative_to(root).as_posix()},
                )
        for name in sorted(filenames):
            absolute = base / name
            relative = absolute.relative_to(root).as_posix()
            if absolute.is_symlink():
                raise _fail(
                    "symlinked artifact files are prohibited",
                    code="artifact.symlink_rejected",
                    details={"path": relative},
                )
            found.append(relative)
    return set(found)


def summarize_verified(report: Mapping[str, Any]) -> str:
    """Render a compact deterministic one-line summary of a verified report."""
    return (
        f"{report['artifact_id']} format={report['format_name']} "
        f"files={report['file_count']} bytes={report['total_bytes']}"
    )
