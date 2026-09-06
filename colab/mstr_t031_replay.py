#!/usr/bin/env python3
"""Evidence-bounded T029 producer replay installer for governed T031 execution."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from mstr_executor_toolchain import (
    INSTALL_TIMEOUT_SECONDS,
    LOCAL_SETUP_TIMEOUT_SECONDS,
    SYSTEM_PROBE_TIMEOUT_SECONDS,
    ToolchainError,
    _run_checked,
    download_verified,
    read_json,
)


def _normalized_package_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ToolchainError("package name must be a non-empty string")
    return value.lower().replace("_", "-")


def _require_replay_system_identity(
    base_lock: dict[str, object], overlay: dict[str, object]
) -> str:
    """Require the replay Python and the base lock's system build-tool identities."""

    expected_python = overlay.get("python_version")
    if not isinstance(expected_python, str):
        raise ToolchainError("producer replay Python identity is missing")
    actual_python = ".".join(str(item) for item in sys.version_info[:3])
    if actual_python != expected_python:
        raise ToolchainError(
            f"producer replay Python mismatch: expected {expected_python}, got {actual_python}"
        )

    runner = base_lock.get("runner")
    if not isinstance(runner, dict):
        raise ToolchainError("base toolchain runner object is missing")
    tools = runner.get("system_build_tools")
    if not isinstance(tools, dict):
        raise ToolchainError("base system_build_tools lock is missing")
    probes = {
        "cmake": ["cmake", "--version"],
        "gcc": ["gcc", "--version"],
        "g++": ["g++", "--version"],
    }
    for name, argv in probes.items():
        expected = tools.get(name)
        if not isinstance(expected, str):
            raise ToolchainError(f"base system tool identity is missing: {name}")
        output = _run_checked(argv, timeout=SYSTEM_PROBE_TIMEOUT_SECONDS)
        actual = output.splitlines()[0] if output else ""
        if actual != expected:
            raise ToolchainError(
                f"{name} identity mismatch: expected {expected!r}, got {actual!r}"
            )
    return actual_python


def _validated_package_entries(
    entries: object,
    *,
    allowed_hosts: frozenset[str],
    label: str,
) -> list[dict[str, str]]:
    if not isinstance(entries, list):
        raise ToolchainError(f"{label} package list is missing")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in entries:
        if not isinstance(raw, dict):
            raise ToolchainError(f"{label} package entry must be an object")
        name = _normalized_package_name(raw.get("name"))
        version = raw.get("version")
        url = raw.get("url")
        sha256 = raw.get("sha256")
        if not all(isinstance(value, str) and value for value in (version, url, sha256)):
            raise ToolchainError(f"{label} package entry has invalid scalar fields: {name}")
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme.lower() != "https" or host not in allowed_hosts:
            raise ToolchainError(f"{label} package URL is outside its exact HTTPS allowlist: {name}")
        if name in seen:
            raise ToolchainError(f"duplicate {label} package identity: {name}")
        seen.add(name)
        result.append(
            {"name": name, "version": version, "url": url, "sha256": sha256}
        )
    return result


def _download_entries(
    *,
    entries: list[dict[str, str]],
    destination: Path,
    allowed_hosts: frozenset[str],
    user_agent: str,
) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, entry in enumerate(entries):
        suffix = unquote(Path(urlparse(entry["url"]).path).name) or f"package-{index}.whl"
        target = destination / suffix
        download_verified(
            url=entry["url"],
            expected_sha256=entry["sha256"],
            destination=target,
            allowed_hosts=allowed_hosts,
            user_agent=user_agent,
        )
        paths.append(target)
    return paths


def install_replay_toolchain(
    *, base_lock_path: Path, overlay_path: Path, root: Path
) -> tuple[Path, dict[str, object]]:
    """Install the base transitive lock plus the exact T029 replay overlay."""

    base_lock = read_json(base_lock_path)
    overlay = read_json(overlay_path)
    if overlay.get("status") != "EVIDENCE_BOUNDED_REPLAY" or overlay.get("task_id") != "T031":
        raise ToolchainError("T031 producer replay overlay is not canonicalizable")
    python_version = _require_replay_system_identity(base_lock, overlay)

    base_python = base_lock.get("python_toolchain")
    if not isinstance(base_python, dict):
        raise ToolchainError("base python_toolchain lock is missing")
    base_hosts_raw = base_python.get("hosts")
    if not isinstance(base_hosts_raw, list) or not all(
        isinstance(item, str) for item in base_hosts_raw
    ):
        raise ToolchainError("base python_toolchain hosts must be a string list")
    base_hosts = frozenset(base_hosts_raw)

    overlay_hosts_raw = overlay.get("hosts")
    if not isinstance(overlay_hosts_raw, list) or not all(
        isinstance(item, str) for item in overlay_hosts_raw
    ):
        raise ToolchainError("producer replay hosts must be a string list")
    overlay_hosts = frozenset(overlay_hosts_raw)
    if overlay_hosts != frozenset(
        {"files.pythonhosted.org", "download.pytorch.org", "download-r2.pytorch.org"}
    ):
        raise ToolchainError("producer replay package host allowlist drift detected")

    overlay_entries = _validated_package_entries(
        overlay.get("packages"), allowed_hosts=overlay_hosts, label="producer replay"
    )
    overlay_names = {entry["name"] for entry in overlay_entries}
    if overlay_names != {
        "gguf",
        "numpy",
        "protobuf",
        "safetensors",
        "sentencepiece",
        "torch",
        "transformers",
    }:
        raise ToolchainError("producer replay direct package set drift detected")

    pip_entry_raw = base_python.get("pip")
    if not isinstance(pip_entry_raw, dict):
        raise ToolchainError("base pinned pip entry is missing")
    pip_entries = _validated_package_entries(
        [pip_entry_raw], allowed_hosts=base_hosts, label="base pip"
    )
    base_entries = _validated_package_entries(
        base_python.get("packages"), allowed_hosts=base_hosts, label="base transitive"
    )
    retained_base_entries = [
        entry for entry in base_entries if entry["name"] not in overlay_names
    ]

    wheel_root = root / "wheels"
    pip_paths = _download_entries(
        entries=pip_entries,
        destination=wheel_root / "pip",
        allowed_hosts=base_hosts,
        user_agent="mstr-t031-replay-base/1",
    )
    base_paths = _download_entries(
        entries=retained_base_entries,
        destination=wheel_root / "base",
        allowed_hosts=base_hosts,
        user_agent="mstr-t031-replay-base/1",
    )
    overlay_paths = _download_entries(
        entries=overlay_entries,
        destination=wheel_root / "overlay",
        allowed_hosts=overlay_hosts,
        user_agent="mstr-t031-replay-overlay/1",
    )

    venv = root / "venv"
    _run_checked(
        [sys.executable, "-m", "venv", str(venv)],
        timeout=LOCAL_SETUP_TIMEOUT_SECONDS,
    )
    python_exe = venv / "bin" / "python"
    _run_checked(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            str(pip_paths[0]),
        ],
        timeout=INSTALL_TIMEOUT_SECONDS,
    )
    _run_checked(
        [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-deps",
            *[str(path) for path in base_paths],
            *[str(path) for path in overlay_paths],
        ],
        timeout=INSTALL_TIMEOUT_SECONDS,
    )

    expected_overlay = {
        entry["name"]: entry["version"] for entry in overlay_entries
    }
    verification_script = (
        "import importlib.metadata,json,sys;"
        "expected=json.loads(sys.argv[1]);"
        "actual={name:importlib.metadata.version(name) for name in expected};"
        "assert actual==expected,(actual,expected);"
        "print(json.dumps(actual,sort_keys=True))"
    )
    verified_json = _run_checked(
        [str(python_exe), "-c", verification_script, json.dumps(expected_overlay, sort_keys=True)],
        timeout=LOCAL_SETUP_TIMEOUT_SECONDS,
    )
    _run_checked(
        [str(python_exe), "-m", "pip", "check"],
        timeout=LOCAL_SETUP_TIMEOUT_SECONDS,
    )
    shutil.rmtree(wheel_root, ignore_errors=True)

    verified = json.loads(verified_json)
    if not isinstance(verified, dict):
        raise ToolchainError("producer replay version verification did not return an object")
    return python_exe, {
        "overlay_id": overlay.get("overlay_id"),
        "python_version": python_version,
        "packages": verified,
        "equivalence_gate": "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH",
    }
