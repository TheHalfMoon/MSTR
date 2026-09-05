from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPOSITORY_ROOT / "colab" / "mstr_t029_quantize.py"


def _load_runner() -> ModuleType:
    spec = importlib.util.spec_from_file_location("mstr_t029_quantize", RUNNER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_replaces_non_utf8_subprocess_output() -> None:
    runner = _load_runner()
    code = "import os; os.write(2, b'quantizer\\xc4\\xffoutput')"

    return_code, output = runner.run([sys.executable, "-c", code])

    assert return_code == 0
    assert "quantizer" in output
    assert "output" in output
    assert "\ufffd" in output


def test_run_preserves_utf8_subprocess_output() -> None:
    runner = _load_runner()
    code = "import os; os.write(1, 'Q4_K_M ok\\n'.encode('utf-8'))"

    return_code, output = runner.run([sys.executable, "-c", code], env=os.environ.copy())

    assert return_code == 0
    assert output == "Q4_K_M ok\n"


def test_network_policy_accepts_only_https_allowlisted_hosts() -> None:
    runner = _load_runner()
    allowed = frozenset({"huggingface.co", "us.aws.cdn.hf.co"})

    assert runner._validated_https_host("https://huggingface.co/x", allowed) == "huggingface.co"
    assert (
        runner._validated_https_host("https://us.aws.cdn.hf.co/blob", allowed) == "us.aws.cdn.hf.co"
    )

    with pytest.raises(runner.NetworkPolicyError):
        runner._validated_https_host("http://huggingface.co/x", allowed)
    with pytest.raises(runner.NetworkPolicyError):
        runner._validated_https_host("https://example.com/x", allowed)


def test_redirect_handler_rejects_unlisted_host_before_following() -> None:
    runner = _load_runner()
    handler = runner.AllowlistedRedirectHandler(frozenset({"huggingface.co"}))

    with pytest.raises(runner.NetworkPolicyError):
        handler.redirect_request(None, None, 302, "Found", {}, "https://example.com/blob")


def test_network_addendum_must_bind_exact_t027_bytes(tmp_path: Path) -> None:
    runner = _load_runner()
    t027_path = tmp_path / "T027-weight-access.json"
    t027 = {
        "manifest_id": "T027-weight-access-preflight-frozen",
        "network": {
            "method": "HTTPS_GET_ONLY",
            "allowlist_hosts": ["huggingface.co"],
        },
    }
    t027_path.write_text(json.dumps(t027, sort_keys=True) + "\n", encoding="utf-8")

    addendum_path = tmp_path / "addendum.json"
    addendum = {
        "amends_manifest": {
            "path": "artifacts/manifests/T027-weight-access.json",
            "manifest_id": "T027-weight-access-preflight-frozen",
            "sha256": runner.sha256_file(t027_path),
        },
        "observed_redirect_hosts": ["huggingface.co", "us.aws.cdn.hf.co"],
        "added_hosts": ["us.aws.cdn.hf.co"],
    }
    addendum_path.write_text(json.dumps(addendum), encoding="utf-8")

    allowed = runner.load_model_artifact_allowlist(t027, t027_path, addendum_path)
    assert allowed == frozenset({"huggingface.co", "us.aws.cdn.hf.co"})

    addendum["amends_manifest"]["sha256"] = "0" * 64
    addendum_path.write_text(json.dumps(addendum), encoding="utf-8")
    with pytest.raises(runner.NetworkPolicyError):
        runner.load_model_artifact_allowlist(t027, t027_path, addendum_path)
