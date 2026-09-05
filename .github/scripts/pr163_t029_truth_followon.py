#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

manifest_path = Path("artifacts/manifests/quantization/T029-q4-profiles.json")
runner_evidence_path = Path("evidence/T029-runner-recovery.md")
test_path = Path("tests/contract/test_t029_quantization_manifest.py")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest["pending"] == []
assert len(manifest["profiles"]) == 8
assert all(p["result_classification"] == "Q4_PROFILE_READY" for p in manifest["profiles"])
manifest["completion_state"] = "Q4_PROFILE_SET_READY_NOT_T029_COMPLETE_CANONICAL"
manifest_path.write_text(
    json.dumps(manifest, sort_keys=False, separators=(",", ":")) + "\n",
    encoding="utf-8",
)

text = runner_evidence_path.read_text(encoding="utf-8")
old = "Seven T029 candidates retain fully usable historical Q4 profile evidence. The primary `qwen3.5-2b` artifact records an impossible 65-hex Q4_K_S SHA-256 field, so that single cell is now fail-closed pending governed repair execution. The Ministral runner-decoding recovery remains scientifically resolved. T029 remains open until the Qwen integrity defect is repaired and the current-main reconciliation passes fresh qualification, independent review, mandatory premerge, guarded merge, postmerge proof, and separate canonical task closeout."
new = "All eight T029 candidates retain byte-verified historical Q4 profile evidence. Fresh exact-head qualification re-downloaded the primary `qwen3.5-2b` artifact and proved that its Q4_K_S SHA-256 is the valid 64-hex value recorded in the corrected manifest; the earlier 65-hex value was a reconciliation transcription error caught before merge, not a historical execution defect. The Ministral runner-decoding recovery remains scientifically resolved. T029 remains open until the current-main reconciliation passes fresh qualification, independent review, mandatory premerge, guarded merge, postmerge proof, and separate canonical task closeout."
if old not in text:
    raise SystemExit("stale runner boundary paragraph not found")
text = text.replace(old, new, 1)
text = text.replace(
    "T029_Q4_PROFILE_SET = 7_FULL_1_PARTIAL_QWEN35_2B_Q4_K_S_REPAIR_REQUIRED",
    "T029_Q4_PROFILE_SET = 8_FULLY_VERIFIED",
)
runner_evidence_path.write_text(text.rstrip() + "\n", encoding="utf-8")

tests = test_path.read_text(encoding="utf-8")
tests = tests.replace(
    'assert manifest["completion_state"] == "Q4_PROFILE_SET_READY"',
    'assert (\n        manifest["completion_state"]\n        == "Q4_PROFILE_SET_READY_NOT_T029_COMPLETE_CANONICAL"\n    )',
    1,
)
test_path.write_text(tests.rstrip() + "\n", encoding="utf-8")
