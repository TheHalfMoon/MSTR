#!/usr/bin/env python3
"""MSTR T028 ephemeral acquisition runner (Colab/any-cloud executable).

Executes the frozen T027 weight-access plan inside an ephemeral runner:
downloads each pinned file via plain HTTPS GET (no authentication, no gated
terms, USD 0.00), verifies size and SHA-256 per file against the manifest,
and emits a machine-verifiable report as the durable output.

Local binary copies live only for the duration of the run; the ephemeral VM
is destroyed after evidence is finalized (docs/canonical/STORAGE_ARCHITECTURE.md).

Usage:
    python mstr_t028_acquire.py --manifest artifacts/manifests/T027-weight-access.json \
        [--candidate qwen3.5-2b] [--workdir /tmp/mstr_t028] [--report out.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mstr_qualify.acquisition import build_acquisition_plan  # noqa: E402
from mstr_qualify.errors import QualificationError  # noqa: E402

CHUNK = 1024 * 1024


class _RedirectRecorder(urllib.request.HTTPRedirectHandler):
    """Captures every redirect host so the report can prove allowlist compliance."""

    def __init__(self) -> None:
        self.hosts: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        from urllib.parse import urlparse

        self.hosts.append(urlparse(newurl).hostname or "")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch_verified(planned, workdir: Path) -> dict:
    """Stream one pinned file to disk while verifying size+hash. Fail closed."""
    dest = workdir / planned.candidate_id / planned.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    hasher = hashlib.sha256()
    size = 0
    recorder = _RedirectRecorder()
    opener = urllib.request.build_opener(recorder)
    req = urllib.request.Request(  # noqa: S310 - host allowlisted by plan builder
        planned.url, method="GET", headers={"User-Agent": "mstr-t028-acquire/1"}
    )
    try:
        with opener.open(req) as resp, dest.open("wb") as fh:  # noqa: S310
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                hasher.update(chunk)
                size += len(chunk)
                fh.write(chunk)
    except Exception:  # noqa: BLE001 - fail closed with cleanup
        shutil.rmtree(dest.parent, ignore_errors=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_NETWORK_MISMATCH",
        }
    actual_sha = hasher.hexdigest()
    if planned.expected_size_bytes is not None and size != planned.expected_size_bytes:
        dest.unlink(missing_ok=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_INTEGRITY_FAILURE (size mismatch)",
            "size_bytes": size,
        }
    if planned.expected_sha256 is not None and actual_sha != planned.expected_sha256:
        dest.unlink(missing_ok=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_INTEGRITY_FAILURE (sha256 mismatch)",
            "sha256": actual_sha,
            "size_bytes": size,
        }
    return {
        "candidate_id": planned.candidate_id,
        "filename": planned.filename,
        "status": "ACQUIRED_VERIFIED",
        "sha256": actual_sha,
        "size_bytes": size,
        "model_repo": planned.model_repo,
        "model_revision": planned.model_revision,
        "redirect_hosts": sorted(set(recorder.hosts)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", default=None, help="single candidate id")
    parser.add_argument("--workdir", type=Path, default=Path("/tmp/mstr_t028"))
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    plan = build_acquisition_plan(manifest)
    if args.candidate:
        plan = tuple(f for f in plan if f.candidate_id == args.candidate)
        if not plan:
            print(f"unknown candidate: {args.candidate}", file=sys.stderr)
            return 2

    workdir = args.workdir
    results = [_fetch_verified(f, workdir) for f in plan]
    report = {
        "schema_version": "mstr.acquisition-report.v1",
        "task_id": "MSTR-000 / T028",
        "runner_environment": "ephemeral-runner/python-urllib",
        "resource_cost": "USD 0.00 (unauthenticated public artifact fetch)",
        "result_classification": (
            "ACQUIRED_VERIFIED"
            if all(r["status"] == "ACQUIRED_VERIFIED" for r in results)
            else "PARTIAL_FAILURES_PRESENT"
        ),
        "files": results,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    args.report.write_text(payload, encoding="utf-8")

    # Ephemeral-lifetime discipline: destroy local binary copies immediately.
    shutil.rmtree(workdir, ignore_errors=True)

    ok = all(r["status"] == "ACQUIRED_VERIFIED" for r in results)
    print(json.dumps({"report": str(args.report), "all_verified": ok}))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        raise SystemExit(3) from exc
