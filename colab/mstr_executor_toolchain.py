#!/usr/bin/env python3
"""Fail-closed helpers for the governed MSTR T031 execution toolchain."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

CHUNK = 1024 * 1024


class ToolchainError(RuntimeError):
    """Raised when a pinned execution identity cannot be reproduced exactly."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ToolchainError(f"JSON root must be an object: {path}")
    return value


def require_file_sha256(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise ToolchainError(
            f"SHA-256 mismatch for {path}: expected {expected}, got {actual}"
        )


def _validated_https_host(url: str, allowed_hosts: frozenset[str]) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme.lower() != "https":
        raise ToolchainError(f"non-HTTPS URL rejected: {url}")
    if parsed.username is not None or parsed.password is not None:
        raise ToolchainError("URL credentials are prohibited")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ToolchainError("invalid HTTPS URL port") from exc
    if port not in (None, 443):
        raise ToolchainError(f"nonstandard HTTPS port rejected: {port}")
    if host not in allowed_hosts:
        raise ToolchainError(f"host outside pinned allowlist: {host!r}")
    return host


class AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Permit redirects only when the target remains in the exact host allowlist."""

    def __init__(self, allowed_hosts: frozenset[str]) -> None:
        super().__init__()
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        _validated_https_host(newurl, self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_verified(
    *,
    url: str,
    expected_sha256: str,
    destination: Path,
    allowed_hosts: frozenset[str],
    user_agent: str,
) -> dict[str, object]:
    """Download one exact HTTPS object and verify its SHA-256 before returning."""

    initial_host = _validated_https_host(url, allowed_hosts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": user_agent})
    opener = urllib.request.build_opener(AllowlistedRedirectHandler(allowed_hosts))
    try:
        with opener.open(request, timeout=120) as response, destination.open("wb") as handle:
            final_host = _validated_https_host(response.geturl(), allowed_hosts)
            for chunk in iter(lambda: response.read(CHUNK), b""):
                handle.write(chunk)
        actual = sha256_file(destination)
        if actual != expected_sha256:
            raise ToolchainError(
                f"download hash mismatch for {destination.name}: "
                f"expected {expected_sha256}, got {actual}"
            )
        return {
            "url": url,
            "initial_host": initial_host,
            "final_host": final_host,
            "sha256": actual,
            "size_bytes": destination.stat().st_size,
        }
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def _run_checked(argv: list[str], *, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )
    if completed.returncode != 0:
        diagnostic = (completed.stdout + "\n" + completed.stderr).strip()[-4000:]
        raise ToolchainError(f"command failed ({completed.returncode}): {argv!r}\n{diagnostic}")
    return completed.stdout.strip()


def require_system_identity(lock: dict[str, object]) -> None:
    runner = lock.get("runner")
    if not isinstance(runner, dict):
        raise ToolchainError("toolchain lock runner object is missing")
    expected_python = runner.get("python_version")
    actual_python = ".".join(str(item) for item in sys.version_info[:3])
    if actual_python != expected_python:
        raise ToolchainError(
            f"Python identity mismatch: expected {expected_python}, got {actual_python}"
        )

    tools = runner.get("system_build_tools")
    if not isinstance(tools, dict):
        raise ToolchainError("system_build_tools lock is missing")
    probes = {
        "cmake": ["cmake", "--version"],
        "gcc": ["gcc", "--version"],
        "g++": ["g++", "--version"],
    }
    for name, argv in probes.items():
        expected = tools.get(name)
        output = _run_checked(argv)
        actual = output.splitlines()[0] if output else ""
        if actual != expected:
            raise ToolchainError(
                f"{name} identity mismatch: expected {expected!r}, got {actual!r}"
            )


def install_verified_python_toolchain(lock_path: Path, root: Path) -> Path:
    """Create a venv and install only direct, hash-verified wheels from the lock."""

    lock = read_json(lock_path)
    require_system_identity(lock)
    python_toolchain = lock.get("python_toolchain")
    if not isinstance(python_toolchain, dict):
        raise ToolchainError("python_toolchain lock is missing")
    hosts_raw = python_toolchain.get("hosts")
    if not isinstance(hosts_raw, list) or not all(isinstance(item, str) for item in hosts_raw):
        raise ToolchainError("python_toolchain hosts must be a string list")
    allowed_hosts = frozenset(hosts_raw)

    wheel_dir = root / "wheels"
    wheel_dir.mkdir(parents=True, exist_ok=True)
    downloads: list[tuple[Path, dict[str, object]]] = []

    pip_entry = python_toolchain.get("pip")
    package_entries = python_toolchain.get("packages")
    if not isinstance(pip_entry, dict) or not isinstance(package_entries, list):
        raise ToolchainError("pinned pip/package entries are missing")
    entries = [pip_entry, *package_entries]
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ToolchainError("package lock entry must be an object")
        name = entry.get("name")
        url = entry.get("url")
        expected_sha = entry.get("sha256")
        if not all(isinstance(value, str) for value in (name, url, expected_sha)):
            raise ToolchainError("package lock entry has invalid scalar fields")
        suffix = unquote(Path(urlparse(url).path).name) or f"package-{index}.whl"
        destination = wheel_dir / suffix
        meta = download_verified(
            url=url,
            expected_sha256=expected_sha,
            destination=destination,
            allowed_hosts=allowed_hosts,
            user_agent="mstr-t031-toolchain/1",
        )
        downloads.append((destination, meta))

    venv = root / "venv"
    _run_checked([sys.executable, "-m", "venv", str(venv)])
    python_exe = venv / "bin" / "python"
    pip_wheel = downloads[0][0]
    _run_checked(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            str(pip_wheel),
        ]
    )
    package_wheels = [str(path) for path, _ in downloads[1:]]
    _run_checked(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            *package_wheels,
        ]
    )
    shutil.rmtree(wheel_dir, ignore_errors=True)
    return python_exe


def sanitized_runtime_environment() -> dict[str, str]:
    """Strip upstream option/provider variables before llama.cpp execution."""

    blocked_prefixes = ("LLAMA_ARG_", "HF_", "HUGGINGFACE_", "CUDA_", "NVIDIA_")
    blocked_exact = {
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
    }
    return {
        key: value
        for key, value in os.environ.items()
        if key not in blocked_exact and not key.startswith(blocked_prefixes)
    }


def clone_exact_commit(
    *, repository: str, commit: str, destination: Path, build_flags: list[str], target: str
) -> Path:
    """Fetch exactly one llama.cpp commit and build exactly one requested target."""

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    env = sanitized_runtime_environment()
    _run_checked(["git", "-C", str(destination), "init"], env=env)
    _run_checked(["git", "-C", str(destination), "remote", "add", "origin", repository], env=env)
    _run_checked(
        ["git", "-C", str(destination), "fetch", "--depth", "1", "origin", commit],
        env=env,
    )
    _run_checked(["git", "-C", str(destination), "checkout", "--detach", commit], env=env)
    actual = _run_checked(["git", "-C", str(destination), "rev-parse", "HEAD"], env=env)
    if actual != commit:
        raise ToolchainError(f"llama.cpp commit mismatch: expected {commit}, got {actual}")

    build_dir = destination / "build"
    _run_checked(["cmake", "-S", str(destination), "-B", str(build_dir), *build_flags], env=env)
    _run_checked(
        [
            "cmake",
            "--build",
            str(build_dir),
            "--target",
            target,
            "-j",
            str(min(os.cpu_count() or 2, 4)),
        ],
        env=env,
    )
    executable = build_dir / "bin" / target
    if not executable.is_file():
        raise ToolchainError(f"built executable missing: {executable}")
    return executable
