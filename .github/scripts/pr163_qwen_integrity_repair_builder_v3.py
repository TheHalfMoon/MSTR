#!/usr/bin/env python3
"""Fail-close the invalid historical qwen3.5-2b T029 Q4_K_S hash evidence."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    manifest_path = Path("artifacts/manifests/quantization/T029-q4-profiles.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = manifest["profiles"]
    qwen = next(profile for profile in profiles if profile["candidate_id"] == "qwen3.5-2b")
    arm = qwen["quantization_arms"]["Q4_K_S"]
    historical = arm["output_sha256"]

    assert isinstance(historical, str)
    assert len(historical) == 65
    assert historical == historical.lower()
    assert all(character in "0123456789abcdef" for character in historical)
    assert qwen["actions_run_id"] == 32959707029
    assert qwen["actions_artifact_id"] == 9603552151
    assert qwen["result_classification"] == "Q4_PROFILE_READY"

    arm["historical_reported_output_sha256"] = historical
    arm["output_sha256"] = None
    arm["integrity_status"] = "INVALID_RECORDED_SHA256_65_HEX"
    qwen["historical_report_result_classification"] = "Q4_PROFILE_READY"
    qwen["result_classification"] = "Q4_PROFILE_PARTIAL"
    qwen["qualification_defect"] = "Q4_K_S_RECORDED_SHA256_INVALID_65_HEX"
    manifest["pending"] = [
        {
            "candidate_id": "qwen3.5-2b",
            "cell": "Q4_K_S",
            "reason": (
                "PRIMARY_ACTIONS_ARTIFACT_RECORDED_INVALID_65_HEX_SHA256_"
                "REQUIRES_GOVERNED_REPAIR_EXECUTION"
            ),
        }
    ]
    manifest["completion_state"] = (
        "Q4_PROFILE_SET_INCOMPLETE_PENDING_QWEN35_2B_Q4_K_S_REPAIR"
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    provenance = {
        "format_version": "mstr.t029.qwen35-2b-historical-provenance.v1",
        "task_id": "T029",
        "candidate_id": "qwen3.5-2b",
        "historical_execution_head": "406de41d132fa6d24d55814f3f6dd4fced5f12bd",
        "workflow_run_id": 32959707029,
        "workflow_run_conclusion": "success",
        "material_job_id": 98149126772,
        "material_job_name": "quantize",
        "material_job_conclusion": "success",
        "artifact_id": 9603552151,
        "artifact_name": "t029-q4-qwen3.5-2b",
        "artifact_archive_digest": (
            "sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3"
        ),
        "artifact_report_path": "t029-qwen3.5-2b.json",
        "artifact_report_sha256": (
            "aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61"
        ),
        "model_revision": "b1485b2fa6dfa1287294f269f5fb618e03d52d7c",
        "llama_cpp_commit": "fc35562ba46fbbf8e30cac85edbb39642c37d248",
        "historical_report_result_classification": "Q4_PROFILE_READY",
        "q4_k_m_sha256": (
            "ef3b6b42698ac3955488998f250cc0f1e42ef7dd0819fe7bd86a902f6f90be56"
        ),
        "q4_k_m_size_bytes": 1312164448,
        "q4_k_s_historical_reported_output_sha256": historical,
        "q4_k_s_historical_reported_output_sha256_length": len(historical),
        "q4_k_s_size_bytes": 1246308960,
        "defect": "PRIMARY_ARTIFACT_Q4_K_S_HASH_IS_65_HEX_AND_CANNOT_BE_A_SHA256_DIGEST",
        "interpretation": (
            "The primary GitHub Actions artifact itself contains a 65-hex Q4_K_S value. "
            "The exact execution runner uses hashlib.sha256(...).hexdigest(), which can "
            "only emit 64 hex characters. The historical READY classification therefore "
            "cannot satisfy T029 exact-hash qualification for this cell. No character is "
            "guessed, truncated, or repaired from inference; the Q4_K_S cell remains "
            "pending until a governed repair execution produces a valid digest."
        ),
    }
    Path(
        "artifacts/manifests/quantization/"
        "T029-qwen3.5-2b-historical-provenance.json"
    ).write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    evidence_path = Path("evidence/T029-q4-profiles.md")
    text = evidence_path.read_text(encoding="utf-8")
    old = (
        "T029_Q4_PROFILE_CELLS_READY = 8 / 8\n"
        "MINISTRAL_Q4_STATUS = Q4_PROFILE_READY"
    )
    new = (
        "T029_Q4_PROFILE_CELLS_FULLY_VERIFIED = 7 / 8\n"
        "T029_QWEN35_2B_Q4_K_S = PENDING_INTEGRITY_REPAIR\n"
        "MINISTRAL_Q4_STATUS = Q4_PROFILE_READY"
    )
    assert old in text
    text = text.replace(old, new, 1)
    marker = "## Historical Qualification Boundary\n"
    assert marker in text
    section = f"""## Qwen 3.5 2B Primary-Artifact Integrity Defect

Fresh reconciliation against the primary GitHub Actions artifact for historical run `32959707029` found a fail-closed evidence defect that historical PR #95 did not detect.

```text
RUN = 32959707029 / SUCCESS
JOB = 98149126772 / quantize / SUCCESS
ARTIFACT_ID = 9603552151
ARTIFACT_NAME = t029-q4-qwen3.5-2b
ARTIFACT_ARCHIVE_DIGEST = sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3
REPORT_PATH = t029-qwen3.5-2b.json
REPORT_SHA256 = aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61
```

The primary report itself records this Q4_K_S value:

```text
{historical}
```

It contains 65 hexadecimal characters. The exact historical runner records output hashes with `hashlib.sha256(...).hexdigest()`, which can only emit 64 hexadecimal characters. The historical `Q4_PROFILE_READY` classification therefore cannot satisfy T029's exact-hash requirement for this one cell.

The reconciliation fails closed:

```text
qwen3.5-2b / Q4_K_M = VERIFIED_HISTORICAL_HASH
qwen3.5-2b / Q4_K_S = PENDING_INTEGRITY_REPAIR
HISTORICAL_65_HEX_VALUE = PRESERVED_AS_NEGATIVE_PROVENANCE
INFERRED_OR_TRUNCATED_REPLACEMENT_HASH = NONE
```

A fresh governed T029 repair execution is required for this cell before the profile set may return to 8/8.

"""
    text = text.replace(marker, section + marker, 1)
    text = text.replace(
        "T029_EXECUTION_PROFILE_SET = READY_8_OF_8",
        "T029_EXECUTION_PROFILE_SET = 7_FULL_1_PARTIAL_QWEN35_2B_Q4_K_S_REPAIR_REQUIRED",
        1,
    )
    evidence_path.write_text(text, encoding="utf-8")

    runner_evidence_path = Path("evidence/T029-runner-recovery.md")
    text = runner_evidence_path.read_text(encoding="utf-8")
    old = (
        "All eight T029 Q4 profile cells have durable `Q4_PROFILE_READY` evidence. "
        "The runner recovery is scientifically resolved, but T029 remains open until "
        "this current-main reconciliation passes fresh qualification, independent "
        "review, mandatory premerge, guarded merge, postmerge proof, and separate "
        "canonical task closeout."
    )
    new = (
        "Seven T029 candidates retain fully usable historical Q4 profile evidence. "
        "The primary `qwen3.5-2b` artifact records an impossible 65-hex Q4_K_S SHA-256 "
        "field, so that single cell is now fail-closed pending governed repair "
        "execution. The Ministral runner-decoding recovery remains scientifically "
        "resolved. T029 remains open until the Qwen integrity defect is repaired and "
        "the current-main reconciliation passes fresh qualification, independent "
        "review, mandatory premerge, guarded merge, postmerge proof, and separate "
        "canonical task closeout."
    )
    assert old in text
    text = text.replace(old, new, 1)
    text = text.replace(
        "T029_Q4_PROFILE_SET = READY_8_OF_8",
        "T029_Q4_PROFILE_SET = 7_FULL_1_PARTIAL_QWEN35_2B_Q4_K_S_REPAIR_REQUIRED",
        1,
    )
    runner_evidence_path.write_text(text, encoding="utf-8")

    contract = '''from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-q4-profiles.json"
MINISTRAL_PROVENANCE = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-ministral-recovery-provenance.json"
QWEN_PROVENANCE = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-qwen3.5-2b-historical-provenance.json"
EXPECTED_CANDIDATES = {
    "granite-4.1-3b",
    "ministral-3-3b",
    "qwen2.5-coder-1.5b",
    "qwen3-4b",
    "qwen3.5-2b",
    "qwen3.5-4b",
    "smollm3-3b",
    "yi-coder-1.5b",
}


def _load(path: Path) -> dict[str, object]:
    decoded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def test_t029_manifest_fails_closed_on_qwen_q4ks_integrity_defect() -> None:
    manifest = _load(MANIFEST_PATH)
    assert manifest["format_version"] == "mstr.t029.quantization-manifest.v1"
    assert manifest["task_id"] == "T029"
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    assert {profile["candidate_id"] for profile in profiles} == EXPECTED_CANDIDATES
    assert manifest["completion_state"] == "Q4_PROFILE_SET_INCOMPLETE_PENDING_QWEN35_2B_Q4_K_S_REPAIR"
    assert manifest["pending"] == [
        {
            "candidate_id": "qwen3.5-2b",
            "cell": "Q4_K_S",
            "reason": "PRIMARY_ACTIONS_ARTIFACT_RECORDED_INVALID_65_HEX_SHA256_REQUIRES_GOVERNED_REPAIR_EXECUTION",
        }
    ]
    qwen = next(profile for profile in profiles if profile["candidate_id"] == "qwen3.5-2b")
    assert qwen["historical_report_result_classification"] == "Q4_PROFILE_READY"
    assert qwen["result_classification"] == "Q4_PROFILE_PARTIAL"
    assert qwen["qualification_defect"] == "Q4_K_S_RECORDED_SHA256_INVALID_65_HEX"
    assert len(qwen["quantization_arms"]["Q4_K_M"]["output_sha256"]) == 64
    q4ks = qwen["quantization_arms"]["Q4_K_S"]
    assert q4ks["output_sha256"] is None
    assert q4ks["integrity_status"] == "INVALID_RECORDED_SHA256_65_HEX"
    assert len(q4ks["historical_reported_output_sha256"]) == 65


def test_all_other_q4_hash_cells_are_valid_sha256_hex() -> None:
    manifest = _load(MANIFEST_PATH)
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    for profile in profiles:
        assert len(profile["model_revision"]) == 40
        assert len(profile["llama_cpp_commit"]) == 40
        assert len(profile["f16_sha256"]) == 64
        for arm_name, arm in profile["quantization_arms"].items():
            if profile["candidate_id"] == "qwen3.5-2b" and arm_name == "Q4_K_S":
                continue
            value = arm["output_sha256"]
            assert isinstance(value, str)
            assert len(value) == 64
            assert all(character in "0123456789abcdef" for character in value)
            assert arm["output_size_bytes"] > 0


def test_ministral_recovery_provenance_binds_primary_artifact() -> None:
    provenance = _load(MINISTRAL_PROVENANCE)
    assert provenance["workflow_run_id"] == 33263175072
    assert provenance["workflow_run_conclusion"] == "failure"
    assert provenance["material_job_id"] == 99232907513
    assert provenance["material_job_conclusion"] == "success"
    assert provenance["artifact_id"] == 9729481097
    assert provenance["artifact_report_sha256"] == "120dfabdc328bb7f2adceffd534c651edef57d6dfb9f5dbf0add627f1364b194"
    assert len(provenance["q4_k_m_sha256"]) == 64
    assert len(provenance["q4_k_s_sha256"]) == 64


def test_qwen_historical_provenance_preserves_invalid_primary_value() -> None:
    provenance = _load(QWEN_PROVENANCE)
    assert provenance["workflow_run_id"] == 32959707029
    assert provenance["workflow_run_conclusion"] == "success"
    assert provenance["material_job_id"] == 98149126772
    assert provenance["material_job_conclusion"] == "success"
    assert provenance["artifact_id"] == 9603552151
    assert provenance["artifact_archive_digest"] == "sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3"
    assert provenance["artifact_report_sha256"] == "aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61"
    historical = provenance["q4_k_s_historical_reported_output_sha256"]
    assert provenance["q4_k_s_historical_reported_output_sha256_length"] == 65
    assert isinstance(historical, str)
    assert len(historical) == 65
    assert provenance["defect"] == "PRIMARY_ARTIFACT_Q4_K_S_HASH_IS_65_HEX_AND_CANNOT_BE_A_SHA256_DIGEST"
'''
    Path("tests/contract/test_t029_quantization_manifest.py").write_text(
        contract,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
