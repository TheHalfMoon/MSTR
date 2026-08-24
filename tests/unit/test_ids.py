from __future__ import annotations

from pathlib import Path

import pytest

from mstr_qualify.errors import IdentityError
from mstr_qualify.ids import (
    combine_sha256,
    sha256_bytes,
    sha256_file,
    sha256_text,
    stable_id,
    validate_sha256,
)

ABC_SHA256 = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_sha256_helpers_match_known_vector(tmp_path: Path) -> None:
    path = tmp_path / "abc.bin"
    path.write_bytes(b"abc")
    assert sha256_bytes(b"abc") == ABC_SHA256
    assert sha256_text("abc") == ABC_SHA256
    assert sha256_file(path, chunk_size=1) == ABC_SHA256


def test_validate_sha256_requires_canonical_lowercase() -> None:
    assert validate_sha256(ABC_SHA256) == ABC_SHA256
    with pytest.raises(IdentityError, match="64 lowercase"):
        validate_sha256(ABC_SHA256.upper())


def test_stable_id_is_deterministic_and_boundary_safe() -> None:
    first = stable_id("run", "ab", "c")
    assert first == stable_id("run", "ab", "c")
    assert first != stable_id("run", "a", "bc")
    assert first.startswith("run-")
    assert len(first.removeprefix("run-")) == 64


def test_stable_id_accepts_bytes_without_text_coercion() -> None:
    assert stable_id("artifact", b"abc") != stable_id("artifact", "abc\x00")


@pytest.mark.parametrize("namespace", ["", "Run", "has space", "_leading"])
def test_stable_id_rejects_invalid_namespace(namespace: str) -> None:
    with pytest.raises(IdentityError, match="namespace"):
        stable_id(namespace, "x")


def test_stable_id_requires_identity_material() -> None:
    with pytest.raises(IdentityError, match="at least one"):
        stable_id("run")


def test_combine_sha256_is_ordered_and_deterministic() -> None:
    a = sha256_text("a")
    b = sha256_text("b")
    assert combine_sha256([a, b]) == combine_sha256([a, b])
    assert combine_sha256([a, b]) != combine_sha256([b, a])


def test_sha256_file_wraps_read_failure(tmp_path: Path) -> None:
    with pytest.raises(IdentityError, match="unable to hash file"):
        sha256_file(tmp_path / "missing")


def test_sha256_file_rejects_nonpositive_chunk_size(tmp_path: Path) -> None:
    path = tmp_path / "x"
    path.write_bytes(b"x")
    with pytest.raises(IdentityError, match="chunk_size"):
        sha256_file(path, chunk_size=0)
