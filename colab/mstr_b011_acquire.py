#!/usr/bin/env python3
"""Execute one exact B011 candidate acquisition on an approved ephemeral runner.

The runner is intentionally acquisition-only: no inference, conversion,
quantization, training, or gated/authenticated access is performed. Every file
is streamed through HTTPS GET, redirect hosts are rejected before following if
outside the frozen B010 allowlist, size is bounded while streaming, SHA-256 is
computed, and local copies are destroyed before exit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from mstr_qualify.b011_acquisition import (  # noqa: E402
    B010_SHA256,
    AUTHORITY_ID,
    assert_allowed_redirect,
    build_b011_plan,
    load_b011_inputs,
    verify_b011_report,
)
from mstr_qualify.errors import QualificationError  # noqa: E402

CHUNK = 1024 * 1024


class _StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts: tuple[str, ...]) -> None:
        self.allowed_hosts = allowed_hosts
        self.hosts: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        try:
            host = assert_allowed_redirect(newurl, self.allowed_hosts)
        except QualificationError as exc:
            raise urllib.error.HTTPError(
                newurl,
                code,
                f"B011 fail-closed redirect rejection: {exc}",
                headers,
                fp,
            ) from exc
        self.hosts.append(host)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(planned, workdir: Path) -> dict:
    dest = workdir / planned.candidate_id / planned.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    recorder = _StrictRedirectHandler(planned.allowed_hosts)
    opener = urllib.request.build_opener(recorder)
    request = urllib.request.Request(
        planned.url,
        method="GET",
        headers={"User-Agent": "mstr-b011-acquire/1"},
    )
    hasher = hashlib.sha256()
    size = 0
    try:
        with opener.open(request) as response, dest.open("wb") as fh:  # noqa: S310
            final_url = response.geturl()
            assert_allowed_redirect(final_url, planned.allowed_hosts)
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                size += len(chunk)
                if size > planned.expected_size_bytes:
                    raise QualificationError(
                        "download exceeded frozen B011 byte size",
                        code="b011.download_oversize",
                        details={"file": planned.filename, "expected": planned.expected_size_bytes, "actual": size},
                    )
                hasher.update(chunk)
                fh.write(chunk)
    except Exception as exc:  # noqa: BLE001 - durable fail-closed evidence
        shutil.rmtree(dest.parent, ignore_errors=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_NETWORK_OR_INTEGRITY_FAILURE",
            "error": type(exc).__name__,
            "redirect_hosts": sorted(set(recorder.hosts)),
        }

    digest = hasher.hexdigest()
    if size != planned.expected_size_bytes:
        dest.unlink(missing_ok=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_INTEGRITY_FAILURE",
            "reason": "size_mismatch",
            "size_bytes": size,
            "sha256": digest,
            "redirect_hosts": sorted(set(recorder.hosts)),
        }
    if planned.expected_sha256 is not None and digest != planned.expected_sha256:
        dest.unlink(missing_ok=True)
        return {
            "candidate_id": planned.candidate_id,
            "filename": planned.filename,
            "status": "EXCLUDED_INTEGRITY_FAILURE",
            "reason": "sha256_mismatch",
            "size_bytes": size,
            "sha256": digest,
            "redirect_hosts": sorted(set(recorder.hosts)),
        }
    return {
        "candidate_id": planned.candidate_id,
        "filename": planned.filename,
        "status": "ACQUIRED_VERIFIED",
        "sha256": digest,
        "size_bytes": size,
        "model_repo": planned.model_repo,
        "model_revision": planned.model_revision,
        "redirect_hosts": sorted(set(recorder.hosts)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    b010, authority = load_b011_inputs(args.manifest, args.authority)
    full_plan = build_b011_plan(b010, authority)
    plan = tuple(p for p in full_plan if p.candidate_id == args.candidate)
    if not plan:
        print(f"FAIL CLOSED: unauthorized B011 candidate: {args.candidate}", file=sys.stderr)
        return 2

    results: list[dict] = []
    try:
        for planned in plan:
            row = _fetch(planned, args.workdir)
            results.append(row)
            if row["status"] != "ACQUIRED_VERIFIED":
                break

        expected_bytes = sum(p.expected_size_bytes for p in plan)
        actual_bytes = sum(int(r.get("size_bytes", 0)) for r in results if r.get("status") == "ACQUIRED_VERIFIED")
        all_verified = len(results) == len(plan) and all(r["status"] == "ACQUIRED_VERIFIED" for r in results)
        report = {
            "schema_version": "mstr.b011-acquisition-report.v1",
            "task_id": "MSTR-000B / B011",
            "authority_id": AUTHORITY_ID,
            "b010_sha256": B010_SHA256,
            "candidate_id": args.candidate,
            "runner_environment": "ephemeral-github-actions/python-urllib",
            "resource_cost_usd": 0.0,
            "expected_download_bytes": expected_bytes,
            "actual_download_bytes": actual_bytes,
            "result_classification": "ACQUIRED_VERIFIED" if all_verified else "FAIL_CLOSED",
            "files": results,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if all_verified:
            verify_b011_report(report, full_plan)
        print(json.dumps({"candidate": args.candidate, "all_verified": all_verified, "report": str(args.report)}))
        return 0 if all_verified else 1
    finally:
        shutil.rmtree(args.workdir, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        raise SystemExit(3) from exc
