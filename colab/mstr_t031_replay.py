#!/usr/bin/env python3
"""Evidence-bounded T029 producer replay installer for governed T031 execution."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
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
    require_file_sha256,
)

DIRECT_REPLAY_PACKAGES = frozenset(
    {"gguf", "numpy", "protobuf", "safetensors", "sentencepiece", "torch", "transformers"}
)
HISTORICAL_CUTOFF_UTC = "2026-08-26T10:44:06Z"
HISTORICAL_SHARD_PATHS = (
    "artifacts/manifests/T031-t029-historical-pypi-packages-01.json",
    "artifacts/manifests/T031-t029-historical-pypi-packages-02.json",
    "artifacts/manifests/T031-t029-historical-pypi-packages-03.json",
)


def _normalized_package_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ToolchainError("package name must be a non-empty string")
    return value.lower().replace("_", "-")


def _require_replay_system_identity(
    base_lock: dict[str, object], overlay: dict[str, object]
) -> str:
    """Require replay Python and the base lock's system build-tool identities."""

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
            raise ToolchainError(f"{name} identity mismatch: expected {expected!r}, got {actual!r}")
    return actual_python


def _validated_package_entries(
    entries: object,
    *,
    allowed_hosts: frozenset[str],
    label: str,
) -> list[dict[str, object]]:
    if not isinstance(entries, list):
        raise ToolchainError(f"{label} package list is missing")
    result: list[dict[str, object]] = []
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
        if len(str(sha256)) != 64:
            raise ToolchainError(f"{label} package SHA-256 length is invalid: {name}")
        parsed = urlparse(str(url))
        host = (parsed.hostname or "").lower()
        if parsed.scheme.lower() != "https" or host not in allowed_hosts:
            raise ToolchainError(
                f"{label} package URL is outside its exact HTTPS allowlist: {name}"
            )
        if name in seen:
            raise ToolchainError(f"duplicate {label} package identity: {name}")
        seen.add(name)
        record: dict[str, object] = {
            "name": name,
            "version": str(version),
            "url": str(url),
            "sha256": str(sha256),
        }
        size_bytes = raw.get("size_bytes")
        if size_bytes is not None:
            if not isinstance(size_bytes, int) or size_bytes <= 0:
                raise ToolchainError(f"{label} package size is invalid: {name}")
            record["size_bytes"] = size_bytes
        result.append(record)
    return result


def _historical_package_entries(
    *, overlay: dict[str, object], overlay_path: Path, allowed_hosts: frozenset[str]
) -> list[dict[str, object]]:
    shard_bindings = overlay.get("historical_package_shards")
    if shard_bindings is None:
        return _validated_package_entries(
            overlay.get("packages"), allowed_hosts=allowed_hosts, label="producer replay closure"
        )
    if not isinstance(shard_bindings, list):
        raise ToolchainError("historical replay shard binding list is invalid")
    if overlay.get("historical_cutoff_utc") != HISTORICAL_CUTOFF_UTC:
        raise ToolchainError("historical replay cutoff drift detected")
    observed_paths = [item.get("path") for item in shard_bindings if isinstance(item, dict)]
    if observed_paths != list(HISTORICAL_SHARD_PATHS):
        raise ToolchainError("historical replay shard path set drift detected")

    repo_root = overlay_path.resolve().parents[2]
    cutoff = datetime.fromisoformat(HISTORICAL_CUTOFF_UTC.replace("Z", "+00:00"))
    packages: list[dict[str, object]] = []
    for index, binding in enumerate(shard_bindings, start=1):
        if not isinstance(binding, dict):
            raise ToolchainError("historical replay shard binding must be an object")
        path_value = binding.get("path")
        sha256 = binding.get("sha256")
        if not isinstance(path_value, str) or not isinstance(sha256, str) or len(sha256) != 64:
            raise ToolchainError("historical replay shard binding scalar is invalid")
        shard_path = repo_root / path_value
        require_file_sha256(shard_path, sha256)
        shard = read_json(shard_path)
        if (
            shard.get("schema_version") != "mstr.t031-historical-package-shard.v1"
            or shard.get("task_id") != "T031"
            or shard.get("shard_index") != index
        ):
            raise ToolchainError(f"historical replay shard identity drift detected: {path_value}")
        raw_packages = shard.get("packages")
        entries = _validated_package_entries(
            raw_packages, allowed_hosts=allowed_hosts, label=f"historical replay shard {index}"
        )
        if not isinstance(raw_packages, list):
            raise ToolchainError(f"historical replay shard package list is invalid: {path_value}")
        for raw, entry in zip(raw_packages, entries, strict=True):
            if not isinstance(raw, dict):
                raise ToolchainError("historical replay shard package entry is invalid")
            uploaded_raw = raw.get("upload_time_iso_8601")
            if not isinstance(uploaded_raw, str):
                raise ToolchainError(
                    f"historical replay upload timestamp is missing: {entry['name']}"
                )
            uploaded = datetime.fromisoformat(uploaded_raw.replace("Z", "+00:00"))
            if uploaded.tzinfo is None:
                uploaded = uploaded.replace(tzinfo=timezone.utc)
            if uploaded > cutoff:
                raise ToolchainError(
                    f"historical replay package exceeds T029 cutoff: {entry['name']}"
                )
            size_bytes = raw.get("size_bytes")
            if not isinstance(size_bytes, int) or size_bytes <= 0:
                raise ToolchainError(f"historical replay package size is invalid: {entry['name']}")
            entry["size_bytes"] = size_bytes
            packages.append(entry)

    names = [_normalized_package_name(item.get("name")) for item in packages]
    if len(names) != len(set(names)):
        raise ToolchainError("duplicate package identity across historical replay shards")
    return packages


def _download_entries(
    *,
    entries: list[dict[str, object]],
    destination: Path,
    allowed_hosts: frozenset[str],
    user_agent: str,
) -> list[Path]:
    destination.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for index, entry in enumerate(entries):
        url = str(entry["url"])
        suffix = unquote(Path(urlparse(url).path).name) or f"package-{index}.whl"
        target = destination / suffix
        download_verified(
            url=url,
            expected_sha256=str(entry["sha256"]),
            destination=target,
            allowed_hosts=allowed_hosts,
            user_agent=user_agent,
        )
        expected_size = entry.get("size_bytes")
        if isinstance(expected_size, int) and target.stat().st_size != expected_size:
            target.unlink(missing_ok=True)
            raise ToolchainError(f"downloaded size mismatch: {entry['name']}")
        paths.append(target)
    return paths


def install_replay_toolchain(
    *, base_lock_path: Path, overlay_path: Path, root: Path
) -> tuple[Path, dict[str, object]]:
    """Install the exact evidence-bounded T029 replay dependency closure plus pinned pip."""

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
    allowed_overlay_hosts = {
        frozenset({"files.pythonhosted.org"}),
        frozenset(
            {"files.pythonhosted.org", "download.pytorch.org", "download-r2.pytorch.org"}
        ),
    }
    if overlay_hosts not in allowed_overlay_hosts:
        raise ToolchainError("producer replay package host allowlist drift detected")

    direct_raw = overlay.get("direct_package_names")
    if not isinstance(direct_raw, list) or not all(isinstance(item, str) for item in direct_raw):
        raise ToolchainError("producer replay direct package names are missing")
    direct_names = {_normalized_package_name(item) for item in direct_raw}
    if direct_names != DIRECT_REPLAY_PACKAGES:
        raise ToolchainError("producer replay direct package set drift detected")

    overlay_entries = _historical_package_entries(
        overlay=overlay, overlay_path=overlay_path, allowed_hosts=overlay_hosts
    )
    overlay_names = {_normalized_package_name(entry.get("name")) for entry in overlay_entries}
    if not DIRECT_REPLAY_PACKAGES.issubset(overlay_names):
        raise ToolchainError("producer replay closure is missing a direct package")
    package_count = overlay.get("package_count")
    if not isinstance(package_count, int) or package_count != len(overlay_entries):
        raise ToolchainError("producer replay package-count binding drift detected")

    pip_entry_raw = base_python.get("pip")
    if not isinstance(pip_entry_raw, dict):
        raise ToolchainError("base pinned pip entry is missing")
    pip_entries = _validated_package_entries(
        [pip_entry_raw], allowed_hosts=base_hosts, label="base pip"
    )

    wheel_root = root / "wheels"
    pip_paths = _download_entries(
        entries=pip_entries,
        destination=wheel_root / "pip",
        allowed_hosts=base_hosts,
        user_agent="mstr-t031-replay-pip/3",
    )
    overlay_paths = _download_entries(
        entries=overlay_entries,
        destination=wheel_root / "closure",
        allowed_hosts=overlay_hosts,
        user_agent="mstr-t031-replay-closure/3",
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
            *[str(path) for path in overlay_paths],
        ],
        timeout=INSTALL_TIMEOUT_SECONDS,
    )

    expected = {str(entry["name"]): str(entry["version"]) for entry in overlay_entries}
    verification_script = (
        "import importlib.metadata,json,sys;"
        "expected=json.loads(sys.argv[1]);"
        "actual={name:importlib.metadata.version(name) for name in expected};"
        "assert actual==expected,(actual,expected);"
        "print(json.dumps(actual,sort_keys=True))"
    )
    verified_json = _run_checked(
        [str(python_exe), "-c", verification_script, json.dumps(expected, sort_keys=True)],
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
        "package_count": len(verified),
        "packages": verified,
        "historical_transitive_identity_claim": overlay.get("historical_package_shards")
        is not None,
        "historical_cutoff_utc": overlay.get("historical_cutoff_utc"),
        "equivalence_gate": "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH",
    }
