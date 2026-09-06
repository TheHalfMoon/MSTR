#!/usr/bin/env python3
"""Hash-bound pre-cutoff T029 replay reconstruction adapter for governed T031 execution."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from mstr_executor_toolchain import ToolchainError, read_json, require_file_sha256
from mstr_t031_replay import DIRECT_REPLAY_PACKAGES, install_replay_toolchain

HISTORICAL_CUTOFF_UTC = "2026-08-26T10:44:06Z"
HISTORICAL_SHARD_PATHS = (
    "artifacts/manifests/T031-t029-historical-pypi-packages-01.json",
    "artifacts/manifests/T031-t029-historical-pypi-packages-02.json",
    "artifacts/manifests/T031-t029-historical-pypi-packages-03.json",
)
HISTORICAL_DIRECT_VERSIONS = {
    "gguf": "0.19.0",
    "numpy": "2.4.6",
    "protobuf": "7.36.0",
    "safetensors": "0.8.0",
    "sentencepiece": "0.2.2",
    "torch": "2.13.0",
    "transformers": "5.15.1",
}


def _normalized_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ToolchainError("historical replay package name is invalid")
    return value.lower().replace("_", "-")


def _load_historical_packages(
    *, overlay: dict[str, object], overlay_path: Path
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Load and verify the hash-bound pre-cutoff PyPI wheel reconstruction manifests."""

    if overlay.get("historical_cutoff_utc") != HISTORICAL_CUTOFF_UTC:
        raise ToolchainError("historical replay cutoff drift detected")
    package_count = overlay.get("package_count")
    if package_count != 59:
        raise ToolchainError("historical replay package-count binding drift detected")

    shard_bindings = overlay.get("historical_package_shards")
    if not isinstance(shard_bindings, list) or len(shard_bindings) != 3:
        raise ToolchainError("historical replay shard bindings are missing")
    paths = [item.get("path") for item in shard_bindings if isinstance(item, dict)]
    if paths != list(HISTORICAL_SHARD_PATHS):
        raise ToolchainError("historical replay shard path set drift detected")

    hosts_raw = overlay.get("hosts")
    if not isinstance(hosts_raw, list) or not all(isinstance(item, str) for item in hosts_raw):
        raise ToolchainError("historical replay host allowlist is invalid")
    allowed_hosts = frozenset(hosts_raw)
    if allowed_hosts != frozenset(
        {"files.pythonhosted.org", "download.pytorch.org", "download-r2.pytorch.org"}
    ):
        raise ToolchainError("historical replay host allowlist drift detected")

    repo_root = overlay_path.resolve().parents[2]
    cutoff = datetime.fromisoformat(HISTORICAL_CUTOFF_UTC.replace("Z", "+00:00"))
    packages: list[dict[str, object]] = []
    shard_identity: list[dict[str, str]] = []
    names: set[str] = set()

    for index, binding in enumerate(shard_bindings, start=1):
        if not isinstance(binding, dict):
            raise ToolchainError("historical replay shard binding must be an object")
        path_value = binding.get("path")
        digest = binding.get("sha256")
        if not isinstance(path_value, str) or not isinstance(digest, str) or len(digest) != 64:
            raise ToolchainError("historical replay shard binding scalar is invalid")
        shard_path = repo_root / path_value
        require_file_sha256(shard_path, digest)
        shard = read_json(shard_path)
        if shard.get("schema_version") != "mstr.t031-historical-package-shard.v1":
            raise ToolchainError(f"historical replay shard schema drift detected: {path_value}")
        if shard.get("task_id") != "T031" or shard.get("shard_index") != index:
            raise ToolchainError(f"historical replay shard identity drift detected: {path_value}")
        raw_packages = shard.get("packages")
        if not isinstance(raw_packages, list) or not raw_packages:
            raise ToolchainError(f"historical replay shard package list is invalid: {path_value}")
        shard_identity.append({"path": path_value, "sha256": digest})

        for raw in raw_packages:
            if not isinstance(raw, dict):
                raise ToolchainError("historical replay package entry must be an object")
            name = _normalized_name(raw.get("name"))
            version = raw.get("version")
            url = raw.get("url")
            sha256 = raw.get("sha256")
            size_bytes = raw.get("size_bytes")
            uploaded_raw = raw.get("upload_time_iso_8601")
            requested = raw.get("requested")
            if name in names:
                raise ToolchainError(f"duplicate historical replay package identity: {name}")
            if not isinstance(version, str) or not version:
                raise ToolchainError(f"historical replay package version is invalid: {name}")
            if not isinstance(url, str) or not isinstance(sha256, str) or len(sha256) != 64:
                raise ToolchainError(
                    f"historical replay package artifact identity is invalid: {name}"
                )
            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            if parsed.scheme.lower() != "https" or host not in allowed_hosts:
                raise ToolchainError(f"historical replay package URL is outside allowlist: {name}")
            if not isinstance(size_bytes, int) or size_bytes <= 0:
                raise ToolchainError(f"historical replay package size is invalid: {name}")
            if not isinstance(uploaded_raw, str):
                raise ToolchainError(f"historical replay upload timestamp is missing: {name}")
            uploaded = datetime.fromisoformat(uploaded_raw.replace("Z", "+00:00"))
            if uploaded > cutoff:
                raise ToolchainError(f"historical replay package exceeds T029 cutoff: {name}")
            if not isinstance(requested, bool):
                raise ToolchainError(f"historical replay requested flag is invalid: {name}")
            names.add(name)
            packages.append(
                {
                    "name": name,
                    "version": version,
                    "url": url,
                    "sha256": sha256,
                    "size_bytes": size_bytes,
                    "requested": requested,
                    "upload_time_iso_8601": uploaded_raw,
                }
            )

    if len(packages) != 59:
        raise ToolchainError("historical replay package count does not equal 59")
    direct_names = {_normalized_name(item) for item in overlay.get("direct_package_names", [])}
    if direct_names != DIRECT_REPLAY_PACKAGES:
        raise ToolchainError("historical replay direct package set drift detected")
    by_name = {str(item["name"]): item for item in packages}
    for name, version in HISTORICAL_DIRECT_VERSIONS.items():
        item = by_name.get(name)
        if item is None or item.get("version") != version or item.get("requested") is not True:
            raise ToolchainError(
                f"historical replay direct package identity drift detected: {name}"
            )
    return packages, shard_identity


def install_historical_replay_toolchain(
    *, base_lock_path: Path, overlay_path: Path, root: Path
) -> tuple[Path, dict[str, object]]:
    """Install the hash-bound 59-wheel pre-cutoff reconstruction via the frozen installer."""

    overlay = read_json(overlay_path)
    if overlay.get("status") != "EVIDENCE_BOUNDED_REPLAY" or overlay.get("task_id") != "T031":
        raise ToolchainError("historical T031 producer replay overlay is not canonicalizable")
    packages, shard_identity = _load_historical_packages(
        overlay=overlay,
        overlay_path=overlay_path,
    )

    synthesized = dict(overlay)
    synthesized.pop("historical_package_shards", None)
    synthesized.pop("historical_cutoff_utc", None)
    synthesized["packages"] = [
        {
            "name": item["name"],
            "version": item["version"],
            "url": item["url"],
            "sha256": item["sha256"],
        }
        for item in packages
    ]
    synthesized["package_count"] = 59
    synthesized_path = root / "historical-replay-overlay.json"
    synthesized_path.parent.mkdir(parents=True, exist_ok=True)
    synthesized_path.write_text(
        json.dumps(synthesized, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    python_exe, identity = install_replay_toolchain(
        base_lock_path=base_lock_path,
        overlay_path=synthesized_path,
        root=root,
    )
    identity.update(
        {
            "historical_transitive_identity_claim": False,
            "historical_cutoff_utc": HISTORICAL_CUTOFF_UTC,
            "historical_package_shards": shard_identity,
            "package_count": 59,
            "reconstruction_semantics": (
                "PRE_CUTOFF_PYPI_WHEEL_SET_RECONSTRUCTED_FOR_T029_EXECUTION_WINDOW"
            ),
            "equivalence_gate": "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH",
        }
    )
    return python_exe, identity
