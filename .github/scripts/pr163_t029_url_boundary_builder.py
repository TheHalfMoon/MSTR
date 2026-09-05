#!/usr/bin/env python3
from pathlib import Path

runner_path = Path("colab/mstr_t029_quantize.py")
test_path = Path("tests/unit/test_t029_quantize_runner.py")
evidence_path = Path("evidence/T029-q4-profiles.md")

runner = runner_path.read_text(encoding="utf-8")
old = '''    if parsed.scheme.lower() != "https":\n        raise NetworkPolicyError(f"non-HTTPS model-artifact URL rejected: {url}")\n    if host not in allowed_hosts:\n        raise NetworkPolicyError(f"model-artifact host outside canonical allowlist: {host!r}")\n    return host\n'''
new = '''    if parsed.scheme.lower() != "https":\n        raise NetworkPolicyError(f"non-HTTPS model-artifact URL rejected: {url}")\n    if parsed.username is not None or parsed.password is not None:\n        raise NetworkPolicyError("model-artifact URL credentials are prohibited")\n    try:\n        port = parsed.port\n    except ValueError as exc:\n        raise NetworkPolicyError("invalid model-artifact URL port") from exc\n    if port not in (None, 443):\n        raise NetworkPolicyError(f"nonstandard model-artifact HTTPS port rejected: {port}")\n    if host not in allowed_hosts:\n        raise NetworkPolicyError(f"model-artifact host outside canonical allowlist: {host!r}")\n    return host\n'''
if old not in runner:
    raise SystemExit("expected runner URL validation block not found")
runner_path.write_text(runner.replace(old, new, 1), encoding="utf-8")

tests = test_path.read_text(encoding="utf-8")
anchor = '''    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("https://example.com/x", allowed)\n\n\ndef test_redirect_handler_rejects_unlisted_host_before_following() -> None:\n'''
replacement = '''    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("https://example.com/x", allowed)\n    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("https://user@huggingface.co/x", allowed)\n    with pytest.raises(runner.NetworkPolicyError):\n        runner._validated_https_host("https://huggingface.co:8443/x", allowed)\n\n    assert runner._validated_https_host("https://huggingface.co:443/x", allowed) == "huggingface.co"\n\n\ndef test_redirect_handler_rejects_unlisted_host_before_following() -> None:\n'''
if anchor not in tests:
    raise SystemExit("expected network-policy test anchor not found")
test_path.write_text(tests.replace(anchor, replacement, 1), encoding="utf-8")

evidence = evidence_path.read_text(encoding="utf-8")
anchor = '''A fresh governed T029 repair execution is required for this cell before the profile set may return to 8/8.\n\n## Historical Qualification Boundary\n'''
replacement = '''A fresh governed T029 repair execution is required for this cell before the profile set may return to 8/8.\n\n## Execution Readiness Boundary\n\nThe current reconciliation also identifies a separate execution-readiness question in the historical T029 workflow. Model-artifact acquisition is now fail-closed on the exact T027 HTTPS host allowlist plus the byte-bound `T028-network-scope-addendum-us-aws-cdn` addendum. However, the workflow still provisions conversion/build tooling through package indexes and clones the pinned llama.cpp source from GitHub. Canonical T027 evidence lists package indexes and unrelated/git-protocol network surfaces as unauthorized, while the storage architecture requires external effects to remain within exact authority.\n\nTherefore this reconciliation does **not** treat the historical workflow as dispatch-ready merely because model-artifact redirect enforcement is hardened. Before any fresh Qwen repair execution, exact-head qualification and independent semantic/security review must either identify an already-canonical authority that covers the frozen toolchain acquisition surface or leave execution fail-closed pending a separate exact Founder decision/governance amendment. No package-index, llama.cpp source, model-weight, conversion, or quantization network action is authorized by this reconciliation.\n\n```text\nT029_RECONCILIATION_MERGE_ELIGIBILITY = MAY_BE_QUALIFIED_WITHOUT_EXTERNAL_EXECUTION\nT029_QWEN_REPAIR_EXECUTION_READY = NO\nTOOLCHAIN_NETWORK_AUTHORITY = MUST_BE_PROVEN_BEFORE_DISPATCH\nMODEL_ARTIFACT_NETWORK = T027_ALLOWLIST_PLUS_BOUND_T028_ADDENDUM_ONLY\n```\n\n## Historical Qualification Boundary\n'''
if anchor not in evidence:
    raise SystemExit("expected T029 evidence execution anchor not found")
evidence_path.write_text(evidence.replace(anchor, replacement, 1), encoding="utf-8")
