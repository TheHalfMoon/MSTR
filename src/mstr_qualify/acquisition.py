"""Deterministic T028 acquisition planning and report verification.

The frozen T027 weight-access manifest is the single authority: this module
derives the exact per-file HTTPS GET plan (no authentication, no substitutions,
allowlisted hosts only) and verifies machine-readable acquisition reports
produced by ephemeral cloud runners (Colab notebook or GitHub Actions).

Nothing here performs downloads; execution happens exclusively inside
approved ephemeral runners per docs/canonical/STORAGE_ARCHITECTURE.md.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from .errors import QualificationError

ALLOWED_HOST = "huggingface.co"


@dataclass(frozen=True)
class PlannedFile:
    candidate_id: str
    model_repo: str
    model_revision: str
    filename: str
    url: str
    expected_sha256: str | None
    expected_size_bytes: int


def _resolve_url(model_repo: str, revision: str, filename: str) -> str:
    return f"https://{ALLOWED_HOST}/{model_repo}/resolve/{revision}/{filename}"


def build_acquisition_plan(t027_manifest: dict[str, Any]) -> tuple[PlannedFile, ...]:
    """Derive the complete pinned-download plan from the T027 manifest.

    Fails closed if any required weight file lacks a non-null upstream SHA-256
    or any declared host falls outside the manifest allowlist.
    """

    network = t027_manifest["network"]
    allowlist = set(network["allowlist_hosts"])
    if ALLOWED_HOST not in allowlist:
        raise QualificationError(
            "T027 allowlist must contain the canonical resolve host",
            code="acquisition.allowlist_missing_resolve_host",
        )
    if network["method"] != "HTTPS_GET_ONLY":
        raise QualificationError(
            "network method must remain HTTPS_GET_ONLY",
            code="acquisition.network_method_changed",
        )

    plan: list[PlannedFile] = []
    for candidate in t027_manifest["candidates"]:
        rights = candidate.get("rights_decision", "")
        if not isinstance(rights, str) or "READY_FOR_T028" not in rights:
            raise QualificationError(
                "candidate lacks a passing rights decision; refusing to acquire",
                code="acquisition.rights_gate_failed",
                details={
                    "candidate": candidate["candidate_id"],
                    "rights_decision": repr(rights),
                },
            )
        repo = candidate["exact_model_id"]
        revision = candidate["exact_revision"]
        integrity = {
            entry["file"]: entry for entry in candidate["expected_file_integrity"]
        }
        required = set(candidate["required_artifact_files"])
        missing_integrity = sorted(required - set(integrity))
        if missing_integrity:
            raise QualificationError(
                "required artifact file lacks an integrity entry",
                code="acquisition.integrity_entry_missing",
                details={"candidate": candidate["candidate_id"], "files": missing_integrity},
            )
        for filename in sorted(required):
            entry = integrity[filename]
            sha256 = entry.get("upstream_sha256")
            size = entry["expected_size_bytes"]
            is_weight = filename.endswith((".safetensors", ".bin"))
            if is_weight and not isinstance(sha256, str):
                raise QualificationError(
                    "weight file must carry a non-null upstream SHA-256",
                    code="acquisition.weight_hash_missing",
                    details={"candidate": candidate["candidate_id"], "file": filename},
                )
            plan.append(
                PlannedFile(
                    candidate_id=candidate["candidate_id"],
                    model_repo=repo,
                    model_revision=revision,
                    filename=filename,
                    url=_resolve_url(repo, revision, filename),
                    expected_sha256=sha256,
                    expected_size_bytes=size,
                )
            )
    return tuple(plan)


def verify_acquisition_report(
    report: dict[str, Any],
    t027_manifest: dict[str, Any],
) -> dict[str, Any]:
    """Cross-check an ephemeral-runner report against the frozen manifest.

    The report is the durable output of an ephemeral run. Verification fails
    closed on: unknown candidates, missing files, hash/size mismatches, or
    unverified weight files. Returns the normalized verdict map on success.
    """

    plan = build_acquisition_plan(t027_manifest)
    expected_by_key = {
        (f.candidate_id, f.filename): f for f in plan
    }
    results = report.get("files")
    if not isinstance(results, list):
        raise QualificationError(
            "report.files must be a list",
            code="acquisition.report_shape",
        )

    verdicts: dict[tuple[str, str], str] = {}
    seen: set[tuple[str, str]] = set()
    for item in results:
        key = (item.get("candidate_id"), item.get("filename"))
        if key not in expected_by_key:
            raise QualificationError(
                "report references a file outside the frozen plan",
                code="acquisition.report_unknown_file",
                details={"candidate_id": key[0], "filename": key[1]},
            )
        planned = expected_by_key[key]
        status = item.get("status")
        if status != "ACQUIRED_VERIFIED":
            verdicts[key] = status or "EXCLUDED_ARTIFACT_UNRESOLVED"
            continue
        if item.get("sha256") != planned.expected_sha256 and planned.expected_sha256:
            raise QualificationError(
                "reported hash does not match the frozen upstream SHA-256",
                code="acquisition.hash_mismatch",
                details={
                    "candidate_id": key[0],
                    "file": key[1],
                    "expected": planned.expected_sha256,
                    "actual": item.get("sha256"),
                },
            )
        if planned.expected_size_bytes is not None and item.get(
            "size_bytes"
        ) != planned.expected_size_bytes:
            raise QualificationError(
                "reported size does not match the frozen byte size",
                code="acquisition.size_mismatch",
                details={
                    "candidate_id": key[0],
                    "file": key[1],
                    "expected": planned.expected_size_bytes,
                    "actual": item.get("size_bytes"),
                },
            )
        if (
            planned.filename.endswith(_WEIGHT_SUFFIXES)
            and item.get("sha256") is None
        ):
            raise QualificationError(
                "weight file verified without a hash",
                code="acquisition.weight_hash_missing",
                details={"candidate_id": key[0], "file": key[1]},
            )
        verdicts[key] = "ACQUIRED_VERIFIED"
        seen.add(key)

    missing = set(expected_by_key) - seen
    if missing:
        raise QualificationError(
            "report omits files declared by the frozen plan",
            code="acquisition.report_incomplete",
            details={"missing": sorted(f"{c}:{f}" for c, f in missing)},
        )

    per_candidate: dict[str, str] = {}
    for candidate_id in {f.candidate_id for f in plan}:
        statuses = {
            v for (c, _), v in verdicts.items() if c == candidate_id
        }
        per_candidate[candidate_id] = (
            "ACQUIRED_VERIFIED" if statuses == {"ACQUIRED_VERIFIED"} else next(iter(statuses))
        )
    return {
        "per_file": {f"{c}:{f}": s for (c, f), s in sorted(verdicts.items())},
        "per_candidate": dict(sorted(per_candidate.items())),
        "plan_sha256_of_t027": _sha256_of_manifest(t027_manifest),
    }


_WEIGHT_SUFFIXES = (".safetensors", ".bin")


def _sha256_of_manifest(manifest: dict[str, Any]) -> str:
    import json

    blob = json.dumps(manifest, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
