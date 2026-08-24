"""Canonical, immutable evidence serialization with explicit supersession."""
from __future__ import annotations

import json
import math
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ArtifactIntegrityError, PolicyViolationError
from .ids import sha256_bytes, validate_sha256

_ENVELOPE_SCHEMA = "mstr.evidence-envelope.v1"


@dataclass(frozen=True, slots=True)
class FinalizedEvidence:
    """Finalized evidence whose canonical bytes are the authoritative record."""

    sha256: str
    canonical_bytes: bytes
    record_type: str
    supersedes: str | None


def _validate_json_value(value: Any, *, path: str = "$") -> None:
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise PolicyViolationError(
                "evidence contains a non-finite number",
                code="evidence.non_finite_number",
                details={"path": path},
            )
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_json_value(child, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise PolicyViolationError(
                    "evidence object keys must be strings",
                    code="evidence.object_key_type",
                    details={"path": path},
                )
            _validate_json_value(child, path=f"{path}.{key}")
        return
    raise PolicyViolationError(
        "evidence contains a non-JSON value",
        code="evidence.value_type",
        details={"path": path, "type": type(value).__name__},
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize strict JSON using the byte-stable MSTR canonical JSON v1 form."""

    _validate_json_value(value)
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return rendered.encode("utf-8") + b"\n"


def _validate_record_type(record_type: str) -> str:
    if not record_type or record_type.strip() != record_type:
        raise PolicyViolationError(
            "record_type must be non-empty and have no surrounding whitespace",
            code="evidence.record_type",
        )
    return record_type


def _build_envelope(
    record_type: str,
    payload: Mapping[str, Any],
    *,
    supersedes: str | None,
    supersession_reason: str | None,
) -> dict[str, Any]:
    _validate_record_type(record_type)
    if supersedes is None:
        if supersession_reason is not None:
            raise PolicyViolationError(
                "supersession_reason requires supersedes",
                code="evidence.supersession_reason_without_parent",
            )
    else:
        validate_sha256(supersedes)
        if not isinstance(supersession_reason, str) or not supersession_reason.strip():
            raise PolicyViolationError(
                "superseding evidence requires a non-empty reason",
                code="evidence.supersession_reason_missing",
            )
    return {
        "schema_version": _ENVELOPE_SCHEMA,
        "record_type": record_type,
        "supersedes": supersedes,
        "supersession_reason": supersession_reason,
        "payload": dict(payload),
    }


def finalize_evidence(
    record_type: str,
    payload: Mapping[str, Any],
    *,
    supersedes: str | None = None,
    supersession_reason: str | None = None,
) -> FinalizedEvidence:
    """Freeze an evidence envelope into canonical bytes and a content SHA-256."""

    envelope = _build_envelope(
        record_type,
        payload,
        supersedes=supersedes,
        supersession_reason=supersession_reason,
    )
    canonical = canonical_json_bytes(envelope)
    return FinalizedEvidence(
        sha256=sha256_bytes(canonical),
        canonical_bytes=canonical,
        record_type=record_type,
        supersedes=supersedes,
    )


def supersede_evidence(
    previous: FinalizedEvidence,
    payload: Mapping[str, Any],
    *,
    reason: str,
    record_type: str | None = None,
) -> FinalizedEvidence:
    """Create a new immutable record that explicitly supersedes *previous*."""

    return finalize_evidence(
        record_type or previous.record_type,
        payload,
        supersedes=previous.sha256,
        supersession_reason=reason,
    )


def load_finalized_evidence(path: Path) -> FinalizedEvidence:
    """Load evidence and reject non-canonical or structurally invalid bytes."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ArtifactIntegrityError(
            "unable to read evidence",
            code="evidence.read",
            details={"path": str(path)},
        ) from exc
    try:
        decoded = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ArtifactIntegrityError(
            "evidence is not valid UTF-8 JSON",
            code="evidence.json_invalid",
            details={"path": str(path)},
        ) from exc
    if not isinstance(decoded, dict):
        raise ArtifactIntegrityError(
            "evidence envelope must be a JSON object",
            code="evidence.envelope_type",
            details={"path": str(path)},
        )
    try:
        canonical = canonical_json_bytes(decoded)
    except PolicyViolationError as exc:
        raise ArtifactIntegrityError(
            "evidence contains values outside canonical JSON policy",
            code="evidence.canonical_policy",
            details={"path": str(path)},
        ) from exc
    if raw != canonical:
        raise ArtifactIntegrityError(
            "evidence bytes are not in canonical MSTR form",
            code="evidence.not_canonical",
            details={"path": str(path)},
        )
    if decoded.get("schema_version") != _ENVELOPE_SCHEMA:
        raise ArtifactIntegrityError(
            "unsupported evidence envelope schema",
            code="evidence.schema_version",
            details={"path": str(path)},
        )
    record_type = decoded.get("record_type")
    if not isinstance(record_type, str):
        raise ArtifactIntegrityError(
            "evidence record_type is invalid",
            code="evidence.record_type_invalid",
            details={"path": str(path)},
        )
    payload = decoded.get("payload")
    if not isinstance(payload, dict):
        raise ArtifactIntegrityError(
            "evidence payload must be an object",
            code="evidence.payload_type",
            details={"path": str(path)},
        )
    supersedes = decoded.get("supersedes")
    reason = decoded.get("supersession_reason")
    try:
        _build_envelope(
            record_type,
            payload,
            supersedes=supersedes,
            supersession_reason=reason,
        )
    except (PolicyViolationError, ValueError) as exc:
        raise ArtifactIntegrityError(
            "evidence supersession metadata is invalid",
            code="evidence.supersession_invalid",
            details={"path": str(path)},
        ) from exc
    return FinalizedEvidence(
        sha256=sha256_bytes(raw),
        canonical_bytes=raw,
        record_type=record_type,
        supersedes=supersedes,
    )


def _validate_finalized_integrity(evidence: FinalizedEvidence) -> None:
    validate_sha256(evidence.sha256)
    if sha256_bytes(evidence.canonical_bytes) != evidence.sha256:
        raise ArtifactIntegrityError(
            "finalized evidence bytes do not match their SHA-256",
            code="evidence.hash_mismatch",
        )


def write_finalized_evidence(directory: Path, evidence: FinalizedEvidence) -> Path:
    """Write content-addressed evidence once; identical retries are idempotent."""

    _validate_finalized_integrity(evidence)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{evidence.sha256}.json"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        try:
            existing = target.read_bytes()
        except OSError as exc:
            raise ArtifactIntegrityError(
                "unable to verify existing immutable evidence",
                code="evidence.existing_read",
                details={"path": str(target)},
            ) from exc
        if existing != evidence.canonical_bytes:
            raise ArtifactIntegrityError(
                "content-addressed evidence path already contains different bytes",
                code="evidence.immutable_conflict",
                details={"path": str(target)},
            )
        return target
    except OSError as exc:
        raise ArtifactIntegrityError(
            "unable to create immutable evidence",
            code="evidence.write",
            details={"path": str(target)},
        ) from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(evidence.canonical_bytes)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        try:
            target.unlink(missing_ok=True)
        except OSError:
            pass
        raise ArtifactIntegrityError(
            "unable to finalize immutable evidence write",
            code="evidence.write",
            details={"path": str(target)},
        ) from exc
    return target


def validate_supersession_chain(records: Iterable[FinalizedEvidence]) -> None:
    """Require a closed, acyclic supersession graph for the provided records."""

    by_hash: dict[str, FinalizedEvidence] = {}
    for record in records:
        _validate_finalized_integrity(record)
        if record.sha256 in by_hash:
            raise PolicyViolationError(
                "duplicate evidence identity in supersession set",
                code="evidence.duplicate_identity",
                details={"sha256": record.sha256},
            )
        by_hash[record.sha256] = record

    for record in by_hash.values():
        if record.supersedes is not None and record.supersedes not in by_hash:
            raise PolicyViolationError(
                "supersession parent is missing from the validation set",
                code="evidence.supersession_parent_missing",
                details={"sha256": record.sha256, "supersedes": record.supersedes},
            )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(identity: str) -> None:
        if identity in visited:
            return
        if identity in visiting:
            raise PolicyViolationError(
                "supersession cycle detected",
                code="evidence.supersession_cycle",
                details={"sha256": identity},
            )
        visiting.add(identity)
        parent = by_hash[identity].supersedes
        if parent is not None:
            visit(parent)
        visiting.remove(identity)
        visited.add(identity)

    for identity in sorted(by_hash):
        visit(identity)
