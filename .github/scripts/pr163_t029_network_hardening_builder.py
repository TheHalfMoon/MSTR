from __future__ import annotations

from pathlib import Path

RUNNER = Path("colab/mstr_t029_quantize.py")
TEST = Path("tests/unit/test_t029_quantize_runner.py")
WORKFLOW = Path(".github/workflows/t029-quantize.yml")

runner = RUNNER.read_text(encoding="utf-8")

runner = runner.replace(
    "import urllib.request\nfrom pathlib import Path\n",
    "import urllib.request\nfrom pathlib import Path\nfrom urllib.parse import urlparse\n",
    1,
)

anchor = "CHUNK = 1024 * 1024\n\n\ndef sha256_file(path: Path) -> str:\n"
insert = '''CHUNK = 1024 * 1024\n\n\nclass NetworkPolicyError(RuntimeError):\n    \"\"\"Raised when model-artifact acquisition would leave the canonical HTTPS allowlist.\"\"\"\n\n\ndef _validated_https_host(url: str, allowed_hosts: frozenset[str]) -> str:\n    parsed = urlparse(url)\n    host = (parsed.hostname or \"\").lower()\n    if parsed.scheme.lower() != \"https\":\n        raise NetworkPolicyError(f\"non-HTTPS model-artifact URL rejected: {url}\")\n    if host not in allowed_hosts:\n        raise NetworkPolicyError(f\"model-artifact host outside canonical allowlist: {host!r}\")\n    return host\n\n\nclass AllowlistedRedirectHandler(urllib.request.HTTPRedirectHandler):\n    def __init__(self, allowed_hosts: frozenset[str]) -> None:\n        super().__init__()\n        self.allowed_hosts = allowed_hosts\n\n    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]\n        _validated_https_host(newurl, self.allowed_hosts)\n        return super().redirect_request(req, fp, code, msg, headers, newurl)\n\n\ndef load_model_artifact_allowlist(\n    t027_manifest: dict,\n    t027_manifest_path: Path,\n    network_addendum_path: Path | None,\n) -> frozenset[str]:\n    network = t027_manifest.get(\"network\", {})\n    if network.get(\"method\") != \"HTTPS_GET_ONLY\":\n        raise NetworkPolicyError(\"T027 network method must remain HTTPS_GET_ONLY\")\n\n    hosts = {str(host).lower() for host in network.get(\"allowlist_hosts\", [])}\n    if \"huggingface.co\" not in hosts:\n        raise NetworkPolicyError(\"T027 allowlist must contain huggingface.co\")\n\n    if network_addendum_path is not None:\n        addendum = json.loads(network_addendum_path.read_text(encoding=\"utf-8\"))\n        binding = addendum.get(\"amends_manifest\", {})\n        expected_path = \"artifacts/manifests/T027-weight-access.json\"\n        if binding.get(\"path\") != expected_path:\n            raise NetworkPolicyError(\"network addendum is not bound to the canonical T027 path\")\n        if binding.get(\"manifest_id\") != t027_manifest.get(\"manifest_id\"):\n            raise NetworkPolicyError(\"network addendum manifest id does not match T027\")\n        if binding.get(\"sha256\") != sha256_file(t027_manifest_path):\n            raise NetworkPolicyError(\"network addendum T027 SHA-256 binding mismatch\")\n\n        added_hosts = {str(host).lower() for host in addendum.get(\"added_hosts\", [])}\n        observed_hosts = {\n            str(host).lower() for host in addendum.get(\"observed_redirect_hosts\", [])\n        }\n        if not added_hosts or not added_hosts.issubset(observed_hosts):\n            raise NetworkPolicyError(\"network addendum hosts are not a bounded observed subset\")\n        hosts.update(added_hosts)\n\n    return frozenset(hosts)\n\n\ndef sha256_file(path: Path) -> str:\n'''
if anchor not in runner:
    raise SystemExit("runner anchor not found")
runner = runner.replace(anchor, insert, 1)

old_download = '''def download_pinned(repo: str, revision: str, filename: str, dest: Path) -> dict:\n    url = f"https://huggingface.co/{repo}/resolve/{revision}/{filename}"\n    dest.parent.mkdir(parents=True, exist_ok=True)\n    req = urllib.request.Request(url, method="GET",\n                                 headers={"User-Agent": "mstr-t029-quantize/1"})\n    try:\n        with urllib.request.urlopen(req) as resp, dest.open("wb") as fh:\n            while True:\n                chunk = resp.read(CHUNK)\n                if not chunk:\n                    break\n                fh.write(chunk)\n        return {"file": filename, "status": "ACQUIRED_VERIFIED", "sha256": sha256_file(dest)}\n    except Exception as exc:\n        return {"file": filename, "status": f"EXCLUDED_NETWORK ({type(exc).__name__})"}\n'''
new_download = '''def download_pinned(\n    repo: str,\n    revision: str,\n    filename: str,\n    dest: Path,\n    allowed_hosts: frozenset[str],\n) -> dict:\n    url = f"https://huggingface.co/{repo}/resolve/{revision}/{filename}"\n    dest.parent.mkdir(parents=True, exist_ok=True)\n    req = urllib.request.Request(\n        url,\n        method="GET",\n        headers={"User-Agent": "mstr-t029-quantize/1"},\n    )\n    try:\n        initial_host = _validated_https_host(url, allowed_hosts)\n        opener = urllib.request.build_opener(AllowlistedRedirectHandler(allowed_hosts))\n        with opener.open(req) as resp, dest.open("wb") as fh:\n            final_host = _validated_https_host(resp.geturl(), allowed_hosts)\n            while True:\n                chunk = resp.read(CHUNK)\n                if not chunk:\n                    break\n                fh.write(chunk)\n        return {\n            "file": filename,\n            "status": "ACQUIRED_VERIFIED",\n            "sha256": sha256_file(dest),\n            "initial_host": initial_host,\n            "final_host": final_host,\n        }\n    except NetworkPolicyError as exc:\n        dest.unlink(missing_ok=True)\n        return {\n            "file": filename,\n            "status": "EXCLUDED_NETWORK_POLICY",\n            "error": str(exc),\n        }\n    except Exception as exc:\n        dest.unlink(missing_ok=True)\n        return {"file": filename, "status": f"EXCLUDED_NETWORK ({type(exc).__name__})"}\n'''
if old_download not in runner:
    raise SystemExit("download block not found")
runner = runner.replace(old_download, new_download, 1)

runner = runner.replace(
    '    ap.add_argument("--t027-manifest", type=Path, required=True)\n',
    '    ap.add_argument("--t027-manifest", type=Path, required=True)\n'
    '    ap.add_argument("--network-addendum", type=Path)\n',
    1,
)

runner = runner.replace(
    '    t027 = json.loads(args.t027_manifest.read_text(encoding="utf-8"))\n',
    '    t027 = json.loads(args.t027_manifest.read_text(encoding="utf-8"))\n'
    '    try:\n'
    '        allowed_hosts = load_model_artifact_allowlist(\n'
    '            t027, args.t027_manifest, args.network_addendum\n'
    '        )\n'
    '    except NetworkPolicyError as exc:\n'
    '        report = {\n'
    '            "schema_version": "mstr.quantization-report.v1",\n'
    '            "candidate_id": args.candidate,\n'
    '            "result_classification": "Q4_INTEGRITY_FAILURE",\n'
    '            "error": str(exc),\n'
    '        }\n'
    '        args.report.parent.mkdir(parents=True, exist_ok=True)\n'
    '        args.report.write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")\n'
    '        shutil.rmtree(workdir, ignore_errors=True)\n'
    '        return 1\n',
    1,
)

runner = runner.replace(
    '        result = download_pinned(repo, revision, fn, src_dir / fn)\n'
    '        actual_sha = sha256_file(src_dir / fn) if (src_dir / fn).is_file() else None\n'
    '        if actual_sha and entry.get("upstream_sha256"):\n'
    '            ok = actual_sha == entry["upstream_sha256"]\n'
    '            result["verified"] = ok\n'
    '            if not ok:\n'
    '                result["status"] = "EXCLUDED_INTEGRITY_FAILURE"\n'
    '        elif actual_sha is not None and not entry.get("upstream_sha256"):\n'
    '            expected_size = entry.get("expected_size_bytes")\n'
    '            if expected_size is not None:\n'
    '                actual_size = (src_dir / fn).stat().st_size\n'
    '                result["verified"] = actual_size == expected_size\n'
    '                if not result["verified"]:\n'
    '                    result["status"] = "EXCLUDED_INTEGRITY_FAILURE"\n'
    '                    result["size_bytes"] = actual_size\n'
    '            else:\n'
    '                result["verified"] = True\n',
    '        result = download_pinned(repo, revision, fn, src_dir / fn, allowed_hosts)\n'
    '        source_path = src_dir / fn\n'
    '        if source_path.is_file():\n'
    '            actual_sha = sha256_file(source_path)\n'
    '            actual_size = source_path.stat().st_size\n'
    '            expected_sha = entry.get("upstream_sha256")\n'
    '            expected_size = entry.get("expected_size_bytes")\n'
    '            hash_ok = expected_sha is None or actual_sha == expected_sha\n'
    '            size_ok = expected_size is None or actual_size == expected_size\n'
    '            result["sha256"] = actual_sha\n'
    '            result["size_bytes"] = actual_size\n'
    '            result["verified"] = hash_ok and size_ok\n'
    '            if not result["verified"]:\n'
    '                result["status"] = "EXCLUDED_INTEGRITY_FAILURE"\n'
    '                source_path.unlink(missing_ok=True)\n',
    1,
)

runner = runner.replace(
    '        "source_verification": acquired,\n',
    '        "source_verification": acquired,\n'
    '        "model_artifact_network_allowlist": sorted(allowed_hosts),\n',
    1,
)

RUNNER.write_text(runner, encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
test = test.replace("import os\nimport sys\n", "import json\nimport os\nimport sys\n", 1)
test = test.replace("from types import ModuleType\n", "from types import ModuleType\n\nimport pytest\n", 1)

test += '''\n\ndef test_network_policy_accepts_only_https_allowlisted_hosts() -> None:\n    runner = _load_runner()\n    allowed = frozenset({"huggingface.co", "us.aws.cdn.hf.co"})\n\n    assert runner._validated_https_host("https://huggingface.co/x", allowed) == "huggingface.co"\n    assert runner._validated_https_host("https://us.aws.cdn.hf.co/blob", allowed) == "us.aws.cdn.hf.co"\n\n    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("http://huggingface.co/x", allowed)\n    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("https://example.com/x", allowed)\n\n\ndef test_redirect_handler_rejects_unlisted_host_before_following() -> None:\n    runner = _load_runner()\n    handler = runner.AllowlistedRedirectHandler(frozenset({"huggingface.co"}))\n\n    with pytest.raises(runner.NetworkPolicyError):\n        handler.redirect_request(None, None, 302, "Found", {}, "https://example.com/blob")\n\n\ndef test_network_addendum_must_bind_exact_t027_bytes(tmp_path: Path) -> None:\n    runner = _load_runner()\n    t027_path = tmp_path / "T027-weight-access.json"\n    t027 = {\n        "manifest_id": "T027-weight-access-preflight-frozen",\n        "network": {\n            "method": "HTTPS_GET_ONLY",\n            "allowlist_hosts": ["huggingface.co"],\n        },\n    }\n    t027_path.write_text(json.dumps(t027, sort_keys=True) + "\\n", encoding="utf-8")\n\n    addendum_path = tmp_path / "addendum.json"\n    addendum = {\n        "amends_manifest": {\n            "path": "artifacts/manifests/T027-weight-access.json",\n            "manifest_id": "T027-weight-access-preflight-frozen",\n            "sha256": runner.sha256_file(t027_path),\n        },\n        "observed_redirect_hosts": ["huggingface.co", "us.aws.cdn.hf.co"],\n        "added_hosts": ["us.aws.cdn.hf.co"],\n    }\n    addendum_path.write_text(json.dumps(addendum), encoding="utf-8")\n\n    allowed = runner.load_model_artifact_allowlist(t027, t027_path, addendum_path)\n    assert allowed == frozenset({"huggingface.co", "us.aws.cdn.hf.co"})\n\n    addendum["amends_manifest"]["sha256"] = "0" * 64\n    addendum_path.write_text(json.dumps(addendum), encoding="utf-8")\n    with pytest.raises(runner.NetworkPolicyError):\n        runner.load_model_artifact_allowlist(t027, t027_path, addendum_path)\n'''
TEST.write_text(test, encoding="utf-8")

workflow = WORKFLOW.read_text(encoding="utf-8")
workflow = workflow.replace(
    '            --t027-manifest artifacts/manifests/T027-weight-access.json \\\n',
    '            --t027-manifest artifacts/manifests/T027-weight-access.json \\\n'
    '            --network-addendum artifacts/manifests/T028-network-scope-addendum.json \\\n',
    1,
)
WORKFLOW.write_text(workflow, encoding="utf-8")
