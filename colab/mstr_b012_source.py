#!/usr/bin/env python3
"""Exact B011-backed source reacquisition for B012."""

from __future__ import annotations

from pathlib import Path

from mstr_b012_governance import B011_PATH, ExecutionError, MELLUM_ARTIFACT_PATH, QWEN_ARTIFACT_PATH
from mstr_executor_toolchain import download_verified, read_json


def _candidate_envelope(envelope: dict[str, object], candidate_id: str) -> dict[str, object]:
    items = envelope.get("candidate_access_envelopes")
    if not isinstance(items, list):
        raise ExecutionError("B012 candidate access envelopes are missing")
    for item in items:
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id:
            return item
    raise ExecutionError(f"candidate outside B012 envelope: {candidate_id}")


def _artifact_manifest(repo_root: Path, candidate_id: str) -> dict[str, object]:
    path = MELLUM_ARTIFACT_PATH if candidate_id == "mellum-4b" else QWEN_ARTIFACT_PATH
    return read_json(repo_root / path)


def _b011_candidate(repo_root: Path, candidate_id: str) -> dict[str, object]:
    acquired = read_json(repo_root / B011_PATH)
    items = acquired.get("candidates")
    if not isinstance(items, list):
        raise ExecutionError("B011 acquired candidate list is missing")
    for item in items:
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id:
            if item.get("status") != "ACQUIRED_VERIFIED":
                raise ExecutionError(f"B011 source is not ACQUIRED_VERIFIED: {candidate_id}")
            return item
    raise ExecutionError(f"B011 source evidence missing: {candidate_id}")


def download_candidate(*, repo_root: Path, envelope: dict[str, object], candidate_id: str, destination: Path) -> list[dict[str, object]]:
    candidate = _candidate_envelope(envelope, candidate_id)
    b011 = _b011_candidate(repo_root, candidate_id)
    manifest = _artifact_manifest(repo_root, candidate_id)
    upstream = candidate.get("upstream_id")
    revision = candidate.get("exact_revision")
    if not isinstance(upstream, str) or not isinstance(revision, str):
        raise ExecutionError("B012 upstream identity is invalid")
    if b011.get("model_repo") != upstream or b011.get("revision") != revision:
        raise ExecutionError("B011/B012 upstream identity drift detected")

    network = envelope.get("model_artifact_network")
    if not isinstance(network, dict) or network.get("https_get_only") is not True:
        raise ExecutionError("B012 model network policy must remain HTTPS GET only")
    hosts = network.get("hosts")
    if not isinstance(hosts, list) or not all(isinstance(item, str) for item in hosts):
        raise ExecutionError("B012 network host allowlist is invalid")
    allowed_hosts = frozenset(hosts)

    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise ExecutionError("B011 artifact manifest files are missing")
    required = candidate.get("required_files")
    if not isinstance(required, list):
        raise ExecutionError("B012 required file list is missing")
    required_by_name = {item.get("path"): item for item in required if isinstance(item, dict)}

    records: list[dict[str, object]] = []
    total = 0
    for entry in files:
        if not isinstance(entry, dict):
            raise ExecutionError("B011 artifact file entry is invalid")
        stored_path = entry.get("path")
        sha = entry.get("sha256")
        size = entry.get("size_bytes")
        if not isinstance(stored_path, str) or not isinstance(sha, str) or not isinstance(size, int):
            raise ExecutionError("B011 artifact identity is incomplete")
        prefix = f"{candidate_id}/"
        if not stored_path.startswith(prefix):
            raise ExecutionError("B011 artifact path is outside candidate directory")
        filename = stored_path[len(prefix):]
        expected = required_by_name.get(filename)
        if not isinstance(expected, dict) or expected.get("size_bytes") != size:
            raise ExecutionError(f"B010/B011 file-scope drift detected: {filename}")
        url = f"https://huggingface.co/{upstream}/resolve/{revision}/{filename}"
        meta = download_verified(
            url=url,
            expected_sha256=sha,
            destination=destination / filename,
            allowed_hosts=allowed_hosts,
            user_agent="mstr-b012-equivalent-qualification/1",
        )
        if meta.get("size_bytes") != size:
            raise ExecutionError(f"downloaded size mismatch: {filename}")
        total += size
        records.append({"file": filename, "expected_sha256": sha, "expected_size_bytes": size, **meta})

    expected_names = set(required_by_name)
    observed_names = {str(item["file"]) for item in records}
    if observed_names != expected_names:
        raise ExecutionError("B010/B011 exact required-file set mismatch")
    if total != candidate.get("expected_required_download_bytes"):
        raise ExecutionError("B012 candidate download-byte ceiling drift detected")
    return records
