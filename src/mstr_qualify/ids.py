"""Stable SHA-256 and identifier helpers for qualification evidence."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from pathlib import Path

from .errors import IdentityError

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_NAMESPACE_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_STABLE_ID_DOMAIN = b"mstr.stable-id.v1\x00"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path, *, chunk_size: int = 1024 * 1024) -> str:
    if chunk_size <= 0:
        raise IdentityError("chunk_size must be greater than zero", code="identity.chunk_size")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(chunk_size), b""):
                digest.update(chunk)
    except OSError as exc:
        raise IdentityError(
            "unable to hash file",
            code="identity.file_read",
            details={"path": str(path)},
        ) from exc
    return digest.hexdigest()


def validate_sha256(value: str) -> str:
    if not _SHA256_RE.fullmatch(value):
        raise IdentityError(
            "SHA-256 identity must be exactly 64 lowercase hexadecimal characters",
            code="identity.sha256_format",
            details={"value": value},
        )
    return value


def _encode_part(part: str | bytes) -> bytes:
    return part.encode("utf-8") if isinstance(part, str) else part


def stable_id(namespace: str, *parts: str | bytes) -> str:
    """Create a collision-resistant deterministic ID with unambiguous part framing."""

    if not _NAMESPACE_RE.fullmatch(namespace):
        raise IdentityError(
            "identifier namespace must match [a-z0-9][a-z0-9._-]*",
            code="identity.namespace",
            details={"namespace": namespace},
        )
    if not parts:
        raise IdentityError("stable_id requires at least one identity part", code="identity.empty")

    digest = hashlib.sha256()
    digest.update(_STABLE_ID_DOMAIN)
    namespace_bytes = namespace.encode("ascii")
    digest.update(len(namespace_bytes).to_bytes(4, "big"))
    digest.update(namespace_bytes)
    for part in parts:
        encoded = _encode_part(part)
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return f"{namespace}-{digest.hexdigest()}"


def combine_sha256(values: Iterable[str]) -> str:
    """Hash an ordered sequence of already-canonical SHA-256 identities."""

    canonical = [validate_sha256(value) for value in values]
    digest = hashlib.sha256()
    digest.update(b"mstr.sha256-list.v1\x00")
    for value in canonical:
        digest.update(bytes.fromhex(value))
    return digest.hexdigest()
