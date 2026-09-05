#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

CORRECT_Q4KS = "a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9"
NEGATIVE_QUALIFICATION_RUN = 33964325389

manifest_path = Path("artifacts/manifests/quantization/T029-q4-profiles.json")
provenance_path = Path(
    "artifacts/manifests/quantization/T029-qwen3.5-2b-historical-provenance.json"
)
evidence_path = Path("evidence/T029-q4-profiles.md")
test_path = Path("tests/contract/test_t029_quantization_manifest.py")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
profiles = manifest["profiles"]
qwen = next(p for p in profiles if p["candidate_id"] == "qwen3.5-2b")
qwen["quantization_arms"]["Q4_K_S"] = {
    "output_sha256": CORRECT_Q4KS,
    "output_size_bytes": 1246308960,
    "duration_s": 38.1,
}
qwen["result_classification"] = "Q4_PROFILE_READY"
qwen.pop("historical_report_result_classification", None)
qwen.pop("qualification_defect", None)
manifest["completion_state"] = "Q4_PROFILE_SET_READY"
manifest["pending"] = []
manifest_path.write_text(
    json.dumps(manifest, sort_keys=False, separators=(",", ":")) + "\n",
    encoding="utf-8",
)

provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
provenance.pop("q4_k_s_historical_reported_output_sha256", None)
provenance.pop("q4_k_s_historical_reported_output_sha256_length", None)
provenance.pop("defect", None)
provenance["q4_k_s_sha256"] = CORRECT_Q4KS
provenance["q4_k_s_sha256_length"] = 64
provenance["primary_artifact_verdict"] = "Q4_PROFILE_READY"
provenance["reconciliation_negative_run"] = NEGATIVE_QUALIFICATION_RUN
provenance["interpretation"] = (
    "Fresh exact-head qualification downloaded the primary GitHub Actions artifact and "
    "verified both its archive SHA-256 and report SHA-256. The primary report contains a "
    "valid 64-hex Q4_K_S SHA-256. The earlier 65-hex value was a transcription error in "
    "the reconciliation candidate, not a historical execution defect. Qualification run "
    "33964325389 failed closed on that mismatch before merge. The canonical candidate now "
    "uses only the byte-verified primary artifact value; no inferred or truncated digest is used."
)
provenance_path.write_text(
    json.dumps(provenance, indent=2) + "\n",
    encoding="utf-8",
)

evidence = evidence_path.read_text(encoding="utf-8")
old_science = '''Canonical scientific interpretation of the recovered execution evidence is therefore:\n\n```text\nT029_Q4_PROFILE_CELLS_FULLY_VERIFIED = 7 / 8\nT029_QWEN35_2B_Q4_K_S = PENDING_INTEGRITY_REPAIR\nMINISTRAL_Q4_STATUS = Q4_PROFILE_READY\nMINISTRAL_Q4_UNSUPPORTED = NO\nMINISTRAL_Q4_INTEGRITY_FAILURE = NO\n```\n'''
new_science = '''Canonical scientific interpretation of the recovered execution evidence is therefore:\n\n```text\nT029_Q4_PROFILE_CELLS_FULLY_VERIFIED = 8 / 8\nT029_QWEN35_2B_Q4_K_S = VERIFIED_PRIMARY_ARTIFACT_SHA256\nMINISTRAL_Q4_STATUS = Q4_PROFILE_READY\nMINISTRAL_Q4_UNSUPPORTED = NO\nMINISTRAL_Q4_INTEGRITY_FAILURE = NO\n```\n'''
if old_science not in evidence:
    raise SystemExit("scientific interpretation block not found")
evidence = evidence.replace(old_science, new_science, 1)

start = evidence.index("## Qwen 3.5 2B Primary-Artifact Integrity Defect")
end = evidence.index("## Execution Readiness Boundary", start)
qwen_section = '''## Qwen 3.5 2B Primary-Artifact Verification\n\nFresh exact-head qualification re-downloaded the primary GitHub Actions artifact for historical run `32959707029` and verified the archive and report byte identities before interpreting the Q4_K_S value.\n\n```text\nRUN = 32959707029 / SUCCESS\nJOB = 98149126772 / quantize / SUCCESS\nARTIFACT_ID = 9603552151\nARTIFACT_NAME = t029-q4-qwen3.5-2b\nARTIFACT_ARCHIVE_DIGEST = sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3\nREPORT_PATH = t029-qwen3.5-2b.json\nREPORT_SHA256 = aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61\nQ4_K_S_SHA256 = a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9\nQ4_K_S_SHA256_LENGTH = 64\nRESULT = Q4_PROFILE_READY\n```\n\nThe primary artifact value is a valid 64-hex SHA-256. The earlier reconciliation candidate incorrectly transcribed a 65-hex value. Exact-head qualification run `33964325389` caught that mismatch fail-closed before merge. That run is preserved as negative reconciliation evidence; the incorrect transcription is not retained as scientific evidence and is not treated as a historical execution defect.\n\nThe corrected reconciliation uses only the byte-verified primary artifact value:\n\n```text\nqwen3.5-2b / Q4_K_M = VERIFIED_PRIMARY_ARTIFACT_HASH\nqwen3.5-2b / Q4_K_S = VERIFIED_PRIMARY_ARTIFACT_HASH\nINFERRED_OR_TRUNCATED_REPLACEMENT_HASH = NONE\nT029_Q4_PROFILE_SET = 8_FULLY_VERIFIED\n```\n\n'''
evidence = evidence[:start] + qwen_section + evidence[end:]
evidence = evidence.replace(
    "Before any fresh Qwen repair execution, exact-head qualification and independent semantic/security review must either identify an already-canonical authority that covers the frozen toolchain acquisition surface or leave execution fail-closed pending a separate exact Founder decision/governance amendment.",
    "Before any future T029 regeneration or new execution, exact-head qualification and independent semantic/security review must either identify an already-canonical authority that covers the frozen toolchain acquisition surface or leave that future execution fail-closed pending a separate exact Founder decision/governance amendment.",
)
evidence = evidence.replace(
    "T029_QWEN_REPAIR_EXECUTION_READY = NO\n",
    "T029_FUTURE_REGENERATION_EXECUTION_READY = NO\n",
)
evidence = evidence.replace(
    "T029_EXECUTION_PROFILE_SET = 7_FULL_1_PARTIAL_QWEN35_2B_Q4_K_S_REPAIR_REQUIRED",
    "T029_EXECUTION_PROFILE_SET = 8_FULLY_VERIFIED",
)
evidence_path.write_text(evidence, encoding="utf-8")

tests = test_path.read_text(encoding="utf-8")
start = tests.index("def test_t029_manifest_fails_closed_on_qwen_q4ks_integrity_defect()")
end = tests.index("\ndef test_all_other_q4_hash_cells_are_valid_sha256_hex()", start)
replacement = '''def test_t029_manifest_records_eight_ready_primary_artifact_profiles() -> None:\n    manifest = _load(MANIFEST_PATH)\n    assert manifest["format_version"] == "mstr.t029.quantization-manifest.v1"\n    assert manifest["task_id"] == "T029"\n    profiles = manifest["profiles"]\n    assert isinstance(profiles, list)\n    assert {profile["candidate_id"] for profile in profiles} == EXPECTED_CANDIDATES\n    assert manifest["completion_state"] == "Q4_PROFILE_SET_READY"\n    assert manifest["pending"] == []\n    assert all(profile["result_classification"] == "Q4_PROFILE_READY" for profile in profiles)\n    qwen = next(profile for profile in profiles if profile["candidate_id"] == "qwen3.5-2b")\n    q4ks = qwen["quantization_arms"]["Q4_K_S"]\n    assert q4ks["output_sha256"] == (\n        "a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9"\n    )\n    assert len(q4ks["output_sha256"]) == 64\n    assert q4ks["output_size_bytes"] == 1246308960\n\n'''
tests = tests[:start] + replacement + tests[end + 1 :]
tests = tests.replace(
    '''        for arm_name, arm in profile["quantization_arms"].items():\n            if profile["candidate_id"] == "qwen3.5-2b" and arm_name == "Q4_K_S":\n                continue\n            value = arm["output_sha256"]\n''',
    '''        for arm in profile["quantization_arms"].values():\n            value = arm["output_sha256"]\n''',
)
start = tests.index("def test_qwen_historical_provenance_preserves_invalid_primary_value()")
replacement = '''def test_qwen_historical_provenance_binds_valid_primary_value() -> None:\n    provenance = _load(QWEN_PROVENANCE)\n    assert provenance["workflow_run_id"] == 32959707029\n    assert provenance["workflow_run_conclusion"] == "success"\n    assert provenance["material_job_id"] == 98149126772\n    assert provenance["material_job_conclusion"] == "success"\n    assert provenance["artifact_id"] == 9603552151\n    assert (\n        provenance["artifact_archive_digest"]\n        == "sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3"\n    )\n    assert (\n        provenance["artifact_report_sha256"]\n        == "aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61"\n    )\n    assert provenance["q4_k_s_sha256"] == (\n        "a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9"\n    )\n    assert provenance["q4_k_s_sha256_length"] == 64\n    assert provenance["primary_artifact_verdict"] == "Q4_PROFILE_READY"\n    assert provenance["reconciliation_negative_run"] == 33964325389\n'''
tests = tests[:start] + replacement + "\n"
test_path.write_text(tests.rstrip() + "\n", encoding="utf-8")
