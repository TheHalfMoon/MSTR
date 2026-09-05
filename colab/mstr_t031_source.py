#!/usr/bin/env python3
"""T031 exact source identity and bounded model-artifact acquisition."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from mstr_executor_toolchain import download_verified, read_json
from mstr_t031_governance import ExecutionError


def _candidate_source(envelope: dict[str, object], candidate_id: str) -> dict[str, object]:
    source_identity = envelope.get("source_identity")
    if not isinstance(source_identity, dict):
        raise ExecutionError("source_identity is missing")
    sources = source_identity.get("candidate_sources")
    if not isinstance(sources, list):
        raise ExecutionError("candidate_sources is missing")
    matches = [
        item
        for item in sources
        if isinstance(item, dict) and item.get("candidate_id") == candidate_id
    ]
    if len(matches) != 1:
        raise ExecutionError(f"candidate source identity is not unique: {candidate_id}")
    return matches[0]


def _t028_hashes(repo_root: Path, candidate_id: str) -> dict[str, tuple[str, int]]:
    manifest = read_json(repo_root / f"artifacts/manifests/T028-artifact-{candidate_id}.json")
    files = manifest.get("files")
    if not isinstance(files, list):
        raise ExecutionError("T028 per-file manifest files list is missing")
    result: dict[str, tuple[str, int]] = {}
    prefix = f"{candidate_id}/"
    for entry in files:
        if not isinstance(entry, dict):
            raise ExecutionError("T028 file entry must be an object")
        path = entry.get("path")
        sha = entry.get("sha256")
        size = entry.get("size_bytes")
        if not isinstance(path, str) or not path.startswith(prefix):
            raise ExecutionError("T028 file path is not candidate-scoped")
        if not isinstance(sha, str) or not isinstance(size, int):
            raise ExecutionError("T028 file hash/size identity is invalid")
        name = path[len(prefix) :]
        if name in result:
            raise ExecutionError(f"duplicate T028 file identity: {name}")
        result[name] = (sha, size)
    return result


def _download_candidate(
    *,
    repo_root: Path,
    envelope: dict[str, object],
    candidate_id: str,
    destination: Path,
) -> list[dict[str, object]]:
    candidate = _candidate_source(envelope, candidate_id)
    auth_keys = ("account_required", "authentication_required")
    if any(candidate.get(key) is not False for key in auth_keys):
        raise ExecutionError("candidate unexpectedly requires account/authentication")
    gated = candidate.get("gated_access")
    terms = candidate.get("terms_acceptance_required")
    if gated is not False or terms is not False:
        raise ExecutionError("candidate unexpectedly requires gated terms")

    model_id = candidate.get("exact_model_id")
    revision = candidate.get("exact_revision")
    required_files = candidate.get("required_artifact_files")
    if not isinstance(model_id, str) or not isinstance(revision, str):
        raise ExecutionError("candidate model/revision identity is invalid")
    if not isinstance(required_files, list) or not all(
        isinstance(item, str) for item in required_files
    ):
        raise ExecutionError("candidate required_artifact_files is invalid")

    for filename in required_files:
        path = Path(filename)
        if (
            path.is_absolute()
            or "\\" in filename
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise ExecutionError(f"unsafe candidate source path rejected: {filename!r}")

    t028 = _t028_hashes(repo_root, candidate_id)
    if set(required_files) != set(t028):
        raise ExecutionError("T031 required files do not match canonical T028 per-file manifest")

    network = envelope.get("model_artifact_network")
    if not isinstance(network, dict):
        raise ExecutionError("model_artifact_network is missing")
    hosts = network.get("hosts")
    if not isinstance(hosts, list) or not all(isinstance(item, str) for item in hosts):
        raise ExecutionError("model artifact host allowlist is invalid")
    allowed_hosts = frozenset(hosts)
    if allowed_hosts != frozenset({"huggingface.co", "us.aws.cdn.hf.co"}):
        raise ExecutionError("model artifact host allowlist drift detected")

    records: list[dict[str, object]] = []
    total = 0
    for filename in sorted(required_files):
        expected_sha, expected_size = t028[filename]
        encoded_name = quote(filename, safe="/")
        url = f"https://huggingface.co/{model_id}/resolve/{revision}/{encoded_name}"
        target = destination / filename
        meta = download_verified(
            url=url,
            expected_sha256=expected_sha,
            destination=target,
            allowed_hosts=allowed_hosts,
            user_agent="mstr-t031-measure/1",
        )
        size = target.stat().st_size
        if size != expected_size:
            raise ExecutionError(
                f"T028 size mismatch for {filename}: expected {expected_size}, got {size}"
            )
        total += size
        records.append(
            {
                "file": filename,
                "sha256": expected_sha,
                "size_bytes": size,
                "initial_host": meta["initial_host"],
                "final_host": meta["final_host"],
                "verified_against": "T028_PER_FILE_SHA256_AND_SIZE",
            }
        )

    expected_total = candidate.get("expected_total_download_bytes")
    if not isinstance(expected_total, int) or total != expected_total:
        raise ExecutionError(
            f"candidate aggregate source bytes mismatch: expected {expected_total}, got {total}"
        )
    resource_ceiling = envelope.get("resource_ceiling")
    if not isinstance(resource_ceiling, dict):
        raise ExecutionError("resource_ceiling is missing")
    ceiling = resource_ceiling.get("aggregate_required_source_download_bytes")
    if not isinstance(ceiling, int) or total > ceiling:
        raise ExecutionError("candidate acquisition exceeds canonical source download ceiling")
    return records
