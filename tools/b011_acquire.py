#!/usr/bin/env python3
"""Fail-closed MSTR-000B B011 ephemeral acquisition runner.

This runner executes only the exact model-weight access envelope already made
canonical for B011. It performs no inference, conversion, quantization, or
training. Binary bodies remain in the ephemeral runner and are deleted before
exit; only a JSON verification report may outlive the job.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

CHUNK_SIZE = 1024 * 1024
EXPECTED_B010_SHA256 = "4c2fd1469cdcf728063ab8f5b6a603191ffdc9e1a4d4c2d794abd2a24950c3ef"
EXPECTED_AUTHORITY_ID = "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
EXPECTED_DECISION = "FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE"
EXPECTED_CANDIDATES = ("mellum-4b", "qwen3.5-0.8b-control")
EXPECTED_TOTAL_CEILING = 9817996174


class AcquisitionFailure(RuntimeError):
    """A fail-closed B011 acquisition error with a stable classification."""

    def __init__(self, classification: str, message: str) -> None:
        super().__init__(message)
        self.classification = classification


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_relative_path(value: str) -> None:
    if not value or value.strip() != value or "\\" in value or "\x00" in value:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", f"unsafe path: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in value.split("/")):
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", f"unsafe path: {value!r}")


class AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject every redirect that is not HTTPS and explicitly allowlisted."""

    def __init__(self, allowed_hosts: set[str]) -> None:
        super().__init__()
        self.allowed_hosts = allowed_hosts
        self.redirect_hosts: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        parsed = urllib.parse.urlparse(newurl)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or host not in self.allowed_hosts:
            raise AcquisitionFailure(
                "EXCLUDED_NETWORK_MISMATCH",
                f"redirect outside authorized HTTPS allowlist: {newurl}",
            )
        self.redirect_hosts.append(host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def load_and_validate_envelope(manifest_path: Path, authority_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_bytes = manifest_path.read_bytes()
    manifest_sha = sha256_bytes(manifest_bytes)
    if manifest_sha != EXPECTED_B010_SHA256:
        raise AcquisitionFailure(
            "EXCLUDED_AUTHORITY_MISMATCH",
            f"B010 byte identity drifted: {manifest_sha}",
        )
    manifest = json.loads(manifest_bytes)
    authority = json.loads(authority_path.read_text(encoding="utf-8"))

    if manifest.get("schema_version") != "mstr.b010-new-candidate-weight-access.v1":
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "unexpected B010 schema")
    if authority.get("authority_id") != EXPECTED_AUTHORITY_ID or authority.get("status") != "AUTHORIZED_CANONICAL":
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "B011 authority is not canonical")
    scope = authority.get("scope")
    if not isinstance(scope, dict):
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "authority.scope missing")
    if scope.get("decision") != EXPECTED_DECISION:
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "Founder decision mismatch")
    if scope.get("b010_manifest", {}).get("sha256") != manifest_sha:
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "authority does not bind exact B010 bytes")

    candidate_ids = tuple(scope.get("candidate_ids", []))
    requested = tuple(manifest.get("decision", {}).get("new_weight_access_required_candidates", []))
    if candidate_ids != EXPECTED_CANDIDATES or requested != EXPECTED_CANDIDATES:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "candidate set drifted")

    limits = authority.get("cost_resource_ceiling", {}).get("limits", [])
    limits_by_resource = {item.get("resource"): item for item in limits if isinstance(item, dict)}
    if limits_by_resource.get("cost", {}).get("max") != 0.0:
        raise AcquisitionFailure("EXCLUDED_COST_MISMATCH", "USD ceiling is not zero")
    if limits_by_resource.get("required_download_bytes", {}).get("max") != EXPECTED_TOTAL_CEILING:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "aggregate byte ceiling drifted")

    for prohibited in (
        "gated_terms_acceptance",
        "git_model_binaries",
        "large_dataset_ingestion",
        "paid_compute",
        "paid_model_api",
        "production_release",
        "quantization_execution",
        "weight_changing_training",
    ):
        if scope.get(prohibited) is not False:
            raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", f"non-grant drifted: {prohibited}")
    if scope.get("founder_machine_large_artifacts") != 0:
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "founder-machine artifact ceiling drifted")

    manifest_env = {item["candidate_id"]: item for item in manifest.get("candidate_access_envelopes", [])}
    authority_env = {item["candidate_id"]: item for item in scope.get("candidate_access_envelopes", [])}
    if manifest_env != authority_env:
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "authority envelope differs from B010 envelope")
    if set(manifest_env) != set(EXPECTED_CANDIDATES):
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "unexpected candidate envelope")
    if sum(int(item["expected_required_download_bytes"]) for item in manifest_env.values()) != EXPECTED_TOTAL_CEILING:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "B010 candidate byte sum drifted")

    return manifest, authority


def validate_candidate(candidate: dict[str, Any]) -> set[str]:
    if candidate.get("new_weight_access_required") is not True or candidate.get("qualification_required") is not True:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "candidate is outside B011 acquisition requirement")
    if candidate.get("already_authorized_or_available_weight_artifacts") is not False:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "candidate availability state drifted")
    rights = candidate.get("rights_status", {})
    if rights.get("decision") != "pass_permissive" or rights.get("gated_terms_acceptance_required") is not False:
        raise AcquisitionFailure("EXCLUDED_RIGHTS_MISMATCH", "candidate rights are not pass_permissive/accountless")
    if rights.get("account_required") is not False or rights.get("clickthrough_required") is not False:
        raise AcquisitionFailure("EXCLUDED_RIGHTS_MISMATCH", "candidate now requires account/clickthrough")
    if candidate.get("usd_ceiling") != 0.0 or candidate.get("expected_usd") != 0.0:
        raise AcquisitionFailure("EXCLUDED_COST_MISMATCH", "candidate USD envelope drifted")
    if candidate.get("executor") != "B011_APPROVED_EPHEMERAL_CLOUD_RUNNER_AFTER_EXACT_FOUNDER_AUTHORIZATION":
        raise AcquisitionFailure("EXCLUDED_AUTHORITY_MISMATCH", "executor drifted")
    if candidate.get("storage") != "EXTERNAL_EPHEMERAL_OR_APPROVED_EXTERNAL_ACQUISITION_DIR; NEVER_GIT; NEVER_FOUNDER_MACHINE":
        raise AcquisitionFailure("EXCLUDED_STORAGE_MISMATCH", "storage boundary drifted")
    if candidate.get("network_policy") != "HTTPS_GET_ONLY_AFTER_B011_EXACT_FOUNDER_AUTHORIZATION; ABORT_ON_AUTH_GATING_PAYMENT_OR_UNLISTED_REDIRECT":
        raise AcquisitionFailure("EXCLUDED_NETWORK_MISMATCH", "network policy drifted")
    allowed_hosts = set(candidate.get("network_hosts", []))
    expected_hosts = {
        "huggingface.co",
        "cdn-lfs.huggingface.co",
        "cas-bridge.xethub.hf.co",
        "transfer.xethub.hf.co",
        "us.aws.cdn.hf.co",
    }
    if allowed_hosts != expected_hosts:
        raise AcquisitionFailure("EXCLUDED_NETWORK_MISMATCH", "host allowlist drifted")

    required_files = candidate.get("required_files")
    if not isinstance(required_files, list) or not required_files:
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "required_files is empty")
    total = 0
    seen: set[str] = set()
    for entry in required_files:
        path = entry.get("path")
        size = entry.get("size_bytes")
        if not isinstance(path, str) or path in seen:
            raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "duplicate/non-string required path")
        validate_relative_path(path)
        seen.add(path)
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", f"invalid size for {path}")
        total += size
        if entry.get("artifact_class") == "MODEL_WEIGHT":
            digest = entry.get("sha256")
            if not isinstance(digest, str) or len(digest) != 64:
                raise AcquisitionFailure("EXCLUDED_INTEGRITY_FAILURE", f"weight hash not pinned for {path}")
    if total != candidate.get("expected_required_download_bytes"):
        raise AcquisitionFailure("EXCLUDED_SCOPE_MISMATCH", "candidate byte ceiling does not equal required file sum")
    return allowed_hosts


def fetch_one(candidate: dict[str, Any], entry: dict[str, Any], workdir: Path, allowed_hosts: set[str]) -> dict[str, Any]:
    candidate_id = candidate["candidate_id"]
    path = entry["path"]
    expected_size = int(entry["size_bytes"])
    expected_sha = entry.get("sha256")
    repo = candidate["upstream_id"]
    revision = candidate["exact_revision"]
    quoted_path = urllib.parse.quote(path, safe="/")
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{quoted_path}"

    parsed_initial = urllib.parse.urlparse(url)
    if parsed_initial.scheme != "https" or parsed_initial.hostname not in allowed_hosts:
        raise AcquisitionFailure("EXCLUDED_NETWORK_MISMATCH", "initial URL outside allowlist")

    destination = workdir / candidate_id / PurePosixPath(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handler = AllowlistedRedirectHandler(allowed_hosts)
    opener = urllib.request.build_opener(handler)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "mstr-b011-acquire/1"})
    hasher = hashlib.sha256()
    size = 0
    final_host = parsed_initial.hostname or ""

    try:
        with opener.open(request, timeout=120) as response, destination.open("wb") as fh:  # noqa: S310
            final_url = response.geturl()
            parsed_final = urllib.parse.urlparse(final_url)
            final_host = parsed_final.hostname or ""
            if parsed_final.scheme != "https" or final_host not in allowed_hosts:
                raise AcquisitionFailure("EXCLUDED_NETWORK_MISMATCH", f"final URL outside allowlist: {final_url}")
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                size += len(chunk)
                if size > expected_size:
                    raise AcquisitionFailure(
                        "EXCLUDED_INTEGRITY_FAILURE",
                        f"received more than the authorized byte size for {path}",
                    )
                hasher.update(chunk)
                fh.write(chunk)
    except urllib.error.HTTPError as exc:
        destination.unlink(missing_ok=True)
        classification = "EXCLUDED_AUTH_GATING_OR_PAYMENT" if exc.code in {401, 402, 403} else "EXCLUDED_NETWORK_MISMATCH"
        raise AcquisitionFailure(classification, f"HTTP {exc.code} for {path}") from exc
    except AcquisitionFailure:
        destination.unlink(missing_ok=True)
        raise
    except Exception as exc:
        destination.unlink(missing_ok=True)
        raise AcquisitionFailure("EXCLUDED_NETWORK_MISMATCH", f"{type(exc).__name__} while fetching {path}") from exc

    actual_sha = hasher.hexdigest()
    if size != expected_size:
        destination.unlink(missing_ok=True)
        raise AcquisitionFailure(
            "EXCLUDED_INTEGRITY_FAILURE",
            f"size mismatch for {path}: expected {expected_size}, got {size}",
        )
    if expected_sha is not None and actual_sha != expected_sha:
        destination.unlink(missing_ok=True)
        raise AcquisitionFailure(
            "EXCLUDED_INTEGRITY_FAILURE",
            f"sha256 mismatch for {path}: expected {expected_sha}, got {actual_sha}",
        )

    return {
        "candidate_id": candidate_id,
        "filename": path,
        "artifact_class": entry["artifact_class"],
        "status": "ACQUIRED_VERIFIED",
        "sha256": actual_sha,
        "size_bytes": size,
        "expected_sha256": expected_sha,
        "model_repo": repo,
        "model_revision": revision,
        "initial_host": parsed_initial.hostname,
        "redirect_hosts": sorted(set(handler.redirect_hosts)),
        "final_host": final_host,
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--candidate", required=True, choices=EXPECTED_CANDIDATES)
    parser.add_argument("--canonical-main", required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    failure: AcquisitionFailure | None = None
    candidate: dict[str, Any] | None = None
    expected_bytes: int | None = None
    allowed_hosts: set[str] = set()
    try:
        manifest, _authority = load_and_validate_envelope(args.manifest, args.authority)
        candidate = next(item for item in manifest["candidate_access_envelopes"] if item["candidate_id"] == args.candidate)
        allowed_hosts = validate_candidate(candidate)
        expected_bytes = int(candidate["expected_required_download_bytes"])
        for entry in sorted(candidate["required_files"], key=lambda item: item["path"]):
            try:
                results.append(fetch_one(candidate, entry, args.workdir, allowed_hosts))
            except AcquisitionFailure as exc:
                failure = exc
                results.append(
                    {
                        "candidate_id": args.candidate,
                        "filename": entry["path"],
                        "artifact_class": entry.get("artifact_class"),
                        "status": exc.classification,
                        "error": str(exc),
                    }
                )
                break

        if failure is None:
            actual_total = sum(int(item["size_bytes"]) for item in results)
            if actual_total != expected_bytes:
                failure = AcquisitionFailure(
                    "EXCLUDED_INTEGRITY_FAILURE",
                    f"candidate byte total mismatch: expected {expected_bytes}, got {actual_total}",
                )
    except AcquisitionFailure as exc:
        failure = exc
    except Exception as exc:  # fail closed on any unexpected runner defect
        failure = AcquisitionFailure("EXCLUDED_RUNNER_FAILURE", f"{type(exc).__name__}: {exc}")
    finally:
        actual_total = sum(int(item.get("size_bytes", 0)) for item in results)
        report = {
            "schema_version": "mstr.b011-acquisition-report.v1",
            "task_id": "MSTR-000B / B011",
            "canonical_main": args.canonical_main,
            "b010_manifest_sha256": EXPECTED_B010_SHA256,
            "authority_id": EXPECTED_AUTHORITY_ID,
            "founder_decision": EXPECTED_DECISION,
            "candidate_id": args.candidate,
            "model_repo": candidate.get("upstream_id") if candidate else None,
            "model_revision": candidate.get("exact_revision") if candidate else None,
            "runner_environment": "github-actions-ephemeral/ubuntu-24.04/python-urllib",
            "resource_cost_usd": 0.0,
            "authorized_download_bytes": expected_bytes,
            "observed_download_bytes": actual_total,
            "network_allowlist": sorted(allowed_hosts),
            "result_classification": "ACQUIRED_VERIFIED" if failure is None else failure.classification,
            "error": None if failure is None else str(failure),
            "files": results,
            "binary_retention": "EPHEMERAL_RUNNER_ONLY_DELETED_BEFORE_EXIT",
            "prohibitions_respected": [
                "NO_AUTHENTICATION",
                "NO_GATED_TERMS_ACCEPTANCE",
                "NO_PAID_COMPUTE_OR_API",
                "NO_MODEL_EXECUTION",
                "NO_CONVERSION",
                "NO_QUANTIZATION",
                "NO_TRAINING",
                "NO_GIT_BINARIES",
                "NO_FOUNDER_MACHINE_BINARIES",
            ],
        }
        write_report(args.report, report)
        shutil.rmtree(args.workdir, ignore_errors=True)

    print(json.dumps({"report": str(args.report), "classification": report["result_classification"]}, sort_keys=True))
    return 0 if failure is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
