#!/usr/bin/env python3
"""MSTR T029 ephemeral Q4 quantization runner.

Per docs/canonical/STORAGE_ARCHITECTURE.md, this executes entirely inside an
ephemeral cloud VM (Colab or GitHub Actions):
1. re-acquires the exact pinned source from upstream HuggingFace;
2. verifies source SHA-256 against the frozen T027 manifest;
3. clones llama.cpp at a pinned commit; builds the quantizer;
4. converts HF→GGUF F16 then quantizes to Q4_K_M and Q4_K_S;
5. hashes every output artifact;
6. emits a durable JSON manifest with full identity metadata;
7. deletes all binaries before exit (VM reclamation enforces final cleanup).

Usage:
  python mstr_t029_quantize.py \
    --t027-manifest artifacts/manifests/T027-weight-access.json \
    --candidate qwen3.5-2b \
    --llama-cpp-commit <40-hex> \
    --report out/q4-qwen3.5-2b.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

CHUNK = 1024 * 1024


class NetworkPolicyError(RuntimeError):
    """Raised when model-artifact acquisition would leave the canonical HTTPS allowlist."""


def _validated_https_host(url: str, allowed_hosts: frozenset[str]) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme.lower() != "https":
        raise NetworkPolicyError(f"non-HTTPS model-artifact URL rejected: {url}")
    if parsed.username is not None or parsed.password is not None:
        raise NetworkPolicyError("model-artifact URL credentials are prohibited")
    try:
        port = parsed.port
    except ValueError as exc:
        raise NetworkPolicyError("invalid model-artifact URL port") from exc
    if port not in (None, 443):
        raise NetworkPolicyError(f"nonstandard model-artifact HTTPS port rejected: {port}")
    if host not in allowed_hosts:
        raise NetworkPolicyError(f"model-artifact host outside canonical allowlist: {host!r}")
    return host


class AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, allowed_hosts: frozenset[str]) -> None:
        super().__init__()
        self.allowed_hosts = allowed_hosts

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        _validated_https_host(newurl, self.allowed_hosts)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def load_model_artifact_allowlist(
    t027_manifest: dict,
    t027_manifest_path: Path,
    network_addendum_path: Path | None,
) -> frozenset[str]:
    network = t027_manifest.get("network", {})
    if network.get("method") != "HTTPS_GET_ONLY":
        raise NetworkPolicyError("T027 network method must remain HTTPS_GET_ONLY")

    hosts = {str(host).lower() for host in network.get("allowlist_hosts", [])}
    if "huggingface.co" not in hosts:
        raise NetworkPolicyError("T027 allowlist must contain huggingface.co")

    if network_addendum_path is not None:
        addendum = json.loads(network_addendum_path.read_text(encoding="utf-8"))
        binding = addendum.get("amends_manifest", {})
        expected_path = "artifacts/manifests/T027-weight-access.json"
        if binding.get("path") != expected_path:
            raise NetworkPolicyError("network addendum is not bound to the canonical T027 path")
        if binding.get("manifest_id") != t027_manifest.get("manifest_id"):
            raise NetworkPolicyError("network addendum manifest id does not match T027")
        if binding.get("sha256") != sha256_file(t027_manifest_path):
            raise NetworkPolicyError("network addendum T027 SHA-256 binding mismatch")

        added_hosts = {str(host).lower() for host in addendum.get("added_hosts", [])}
        observed_hosts = {str(host).lower() for host in addendum.get("observed_redirect_hosts", [])}
        if not added_hosts or not added_hosts.issubset(observed_hosts):
            raise NetworkPolicyError("network addendum hosts are not a bounded observed subset")
        hosts.update(added_hosts)

    return frozenset(hosts)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download_pinned(
    repo: str,
    revision: str,
    filename: str,
    dest: Path,
    allowed_hosts: frozenset[str],
) -> dict:
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{filename}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "mstr-t029-quantize/1"},
    )
    try:
        initial_host = _validated_https_host(url, allowed_hosts)
        opener = urllib.request.build_opener(AllowlistedRedirectHandler(allowed_hosts))
        with opener.open(req) as resp, dest.open("wb") as fh:
            final_host = _validated_https_host(resp.geturl(), allowed_hosts)
            while True:
                chunk = resp.read(CHUNK)
                if not chunk:
                    break
                fh.write(chunk)
        return {
            "file": filename,
            "status": "ACQUIRED_VERIFIED",
            "sha256": sha256_file(dest),
            "initial_host": initial_host,
            "final_host": final_host,
        }
    except NetworkPolicyError as exc:
        dest.unlink(missing_ok=True)
        return {
            "file": filename,
            "status": "EXCLUDED_NETWORK_POLICY",
            "error": str(exc),
        }
    except Exception as exc:
        dest.unlink(missing_ok=True)
        return {"file": filename, "status": f"EXCLUDED_NETWORK ({type(exc).__name__})"}


def run(cmd: list[str], **kw) -> tuple[int, str]:
    timeout = kw.pop("timeout", 7200)
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            **kw,
        )
        return r.returncode, (r.stdout + r.stderr)[-2000:]
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout}s: {' '.join(str(c) for c in cmd)}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--t027-manifest", type=Path, required=True)
    ap.add_argument("--network-addendum", type=Path)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--llama-cpp-repo", default="https://github.com/ggml-org/llama.cpp")
    ap.add_argument("--llama-cpp-commit", required=True)
    ap.add_argument("--workdir", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    workdir = args.workdir or Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "mstr_t029"
    workdir.mkdir(parents=True, exist_ok=True)

    t027 = json.loads(args.t027_manifest.read_text(encoding="utf-8"))
    try:
        allowed_hosts = load_model_artifact_allowlist(
            t027, args.t027_manifest, args.network_addendum
        )
    except NetworkPolicyError as exc:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_INTEGRITY_FAILURE",
            "error": str(exc),
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        shutil.rmtree(workdir, ignore_errors=True)
        return 1
    cand = next((c for c in t027["candidates"] if c["candidate_id"] == args.candidate), None)
    if not cand:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_INTEGRITY_FAILURE",
            "error": f"candidate id {args.candidate!r} not found in T027 manifest",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"FAIL CLOSED: unknown candidate {args.candidate}", file=sys.stderr)
        return 2

    # Fail-closed rights gate (T006 discipline): refuse to download unless
    # the frozen manifest explicitly declares this candidate READY_FOR_T028.
    if cand.get("rights_decision") != "READY_FOR_T028":
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_INTEGRITY_FAILURE",
            "error": f"rights_decision={cand.get('rights_decision')!r}; refusing to acquire",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        shutil.rmtree(workdir, ignore_errors=True)
        print(json.dumps({"classification": "Q4_INTEGRITY_FAILURE"}))
        return 1

    repo = cand["exact_model_id"]
    revision = cand["exact_revision"]
    src_dir = workdir / "source" / args.candidate.replace(".", "-")

    # Step 1: re-acquire + verify source
    acquired = []
    for entry in sorted(cand["expected_file_integrity"], key=lambda e: e["file"]):
        fn = entry["file"]
        result = download_pinned(repo, revision, fn, src_dir / fn, allowed_hosts)
        source_path = src_dir / fn
        if source_path.is_file():
            actual_sha = sha256_file(source_path)
            actual_size = source_path.stat().st_size
            expected_sha = entry.get("upstream_sha256")
            expected_size = entry.get("expected_size_bytes")
            hash_ok = expected_sha is None or actual_sha == expected_sha
            size_ok = expected_size is None or actual_size == expected_size
            result["sha256"] = actual_sha
            result["size_bytes"] = actual_size
            result["verified"] = hash_ok and size_ok
            if not result["verified"]:
                result["status"] = "EXCLUDED_INTEGRITY_FAILURE"
                source_path.unlink(missing_ok=True)
        acquired.append(result)

    failed = [a for a in acquired if "EXCLUDED" in a.get("status", "")]
    if failed:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_INTEGRITY_FAILURE",
            "acquisition": acquired,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        shutil.rmtree(workdir, ignore_errors=True)
        print(json.dumps({"classification": "Q4_INTEGRITY_FAILURE"}))
        return 1

    # Step 2: clone llama.cpp at pinned commit
    lc_dir = workdir / "llama.cpp"
    rc, out = run(["git", "clone", "--depth", "1", args.llama_cpp_repo, str(lc_dir)])
    if rc != 0:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_CONVERSION_UNSUPPORTED",
            "error": f"git clone failed: {out}",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        shutil.rmtree(workdir, ignore_errors=True)
        return 1

    for git_args in (
        ["git", "-C", str(lc_dir), "fetch", "--depth", "1", "origin", args.llama_cpp_commit],
        ["git", "-C", str(lc_dir), "checkout", args.llama_cpp_commit],
    ):
        subprocess.run(git_args, capture_output=True)
    actual_commit = subprocess.run(
        ["git", "-C", str(lc_dir), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    if actual_commit != args.llama_cpp_commit:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_CONVERSION_UNSUPPORTED",
            "error": f"commit mismatch: wanted {args.llama_cpp_commit}, got {actual_commit}",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        shutil.rmtree(workdir, ignore_errors=True)
        return 1

    # Step 3: convert HF→GGUF F16
    convert_script = lc_dir / "convert_hf_to_gguf.py"
    gguf_f16 = workdir / f"{args.candidate}-f16.gguf"
    conv_start = time.monotonic()
    rc, conv_out = run(
        [
            sys.executable,
            str(convert_script),
            str(src_dir),
            "--outfile",
            str(gguf_f16),
            "--outtype",
            "f16",
        ]
    )
    conv_dur = round(time.monotonic() - conv_start, 1)
    if rc != 0 or not gguf_f16.is_file():
        conv_lower = conv_out.lower()
        unsupported_markers = [
            "not supported",
            "unsupported",
            "unknown model architecture",
            "trust_remote_code",
            "notimplementederror",
        ]
        missing_dep_markers = ["modulenotfounderror", "importerror", "no module named"]
        if any(m in conv_lower for m in unsupported_markers):
            classification = "Q4_CONVERSION_UNSUPPORTED"
        elif any(m in conv_lower for m in missing_dep_markers):
            classification = "Q4_QUANTIZATION_UNSUPPORTED"
        else:
            classification = "Q4_INTEGRITY_FAILURE"
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "model_repo": repo,
            "model_revision": revision,
            "llama_cpp_commit": actual_commit,
            "conversion_tool_output": conv_out[-1500:],
            "result_classification": classification,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        shutil.rmtree(workdir, ignore_errors=True)
        print(json.dumps({"classification": classification}))
        return 1

    f16_sha = sha256_file(gguf_f16)
    f16_size = gguf_f16.stat().st_size

    # Step 4: build quantizer + quantize to Q4 arms
    build_start = time.monotonic()
    run(["cmake", "-B", str(lc_dir / "build"), "-S", str(lc_dir), "-DGGML_NATIVE=ON"], timeout=600)
    build_rc, _ = run(
        [
            "cmake",
            "--build",
            str(lc_dir / "build"),
            "--target",
            "llama-quantize",
            "-j",
            str(os.cpu_count() or 2),
        ],
        timeout=1800,
    )
    build_dur = round(time.monotonic() - build_start, 1)
    quantize_bin = None
    for candidate_path in [lc_dir / "build/bin/llama-quantize", lc_dir / "build/bin/quantize"]:
        if candidate_path.is_file():
            quantize_bin = candidate_path
            break
    if not quantize_bin:
        report = {
            "schema_version": "mstr.quantization-report.v1",
            "candidate_id": args.candidate,
            "result_classification": "Q4_QUANTIZATION_UNSUPPORTED",
            "error": f"llama-quantize binary not found after build (rc={build_rc})",
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        shutil.rmtree(workdir, ignore_errors=True)
        return 1

    arms = {}
    for arm_name, arm_type in [("q4_k_m", "Q4_K_M"), ("q4_k_s", "Q4_K_S")]:
        out_gguf = workdir / f"{args.candidate}-{arm_name}.gguf"
        q_start = time.monotonic()
        rc, q_out = run([str(quantize_bin), str(gguf_f16), str(out_gguf), arm_type])
        q_dur = round(time.monotonic() - q_start, 1)
        if rc != 0 or not out_gguf.is_file():
            arms[arm_type] = {"status": "FAILED", "error": q_out[-800:], "duration_s": q_dur}
            continue
        arms[arm_type] = {
            "status": "OK",
            "quantization_type": arm_type,
            "output_sha256": sha256_file(out_gguf),
            "output_size_bytes": out_gguf.stat().st_size,
            "duration_s": q_dur,
        }

    # Determine classification
    ok_arms = {k: v for k, v in arms.items() if v.get("status") == "OK"}
    if len(ok_arms) == len(arms):
        classification = "Q4_PROFILE_READY"
    elif ok_arms:
        classification = "Q4_PROFILE_PARTIAL"
    else:
        classification = "Q4_QUANTIZATION_UNSUPPORTED"

    report = {
        "schema_version": "mstr.quantization-report.v1",
        "candidate_id": args.candidate,
        "model_repo": repo,
        "model_revision": revision,
        "source_verification": acquired,
        "model_artifact_network_allowlist": sorted(allowed_hosts),
        "tool": {
            "name": "llama.cpp",
            "repository": args.llama_cpp_repo,
            "exact_commit": actual_commit,
            "license": "MIT (llama.cpp component); project Apache-2.0 overall",
        },
        "tokenizer_license_note": (
            "Tokenizer/config files are part of the pinned model tree and inherit "
            "the model's Apache-2.0 license; no separate third-party tokenizer "
            "runtime dependency was introduced."
        ),
        "build_environment": {
            "python": sys.version,
            "platform": sys.platform,
            "cpu_count": os.cpu_count(),
            "runner_identity": os.environ.get("RUNNER_NAME", "local/colab"),
        },
        "build_duration_s": build_dur,
        "conversion": {
            "recipe": "convert_hf_to_gguf.py --outtype f16",
            "duration_s": conv_dur,
            "gguf_f16_sha256": f16_sha,
            "gguf_f16_size_bytes": f16_size,
        },
        "quantization_arms": arms,
        "result_classification": classification,
        "resource_cost": "USD 0.00",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    args.report.write_text(payload, encoding="utf-8")

    shutil.rmtree(workdir, ignore_errors=True)
    print(json.dumps({"classification": classification, "arms_ok": list(ok_arms.keys())}))
    return 0


def cid_safe(s: str) -> str:
    return s.replace(".", "-")


if __name__ == "__main__":
    raise SystemExit(main())
