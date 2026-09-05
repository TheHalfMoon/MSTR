from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-q4-profiles.json"
MINISTRAL_PROVENANCE = (
    REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-ministral-recovery-provenance.json"
)
QWEN_PROVENANCE = (
    REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-qwen3.5-2b-historical-provenance.json"
)
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


def test_t029_manifest_records_eight_ready_primary_artifact_profiles() -> None:
    manifest = _load(MANIFEST_PATH)
    assert manifest["format_version"] == "mstr.t029.quantization-manifest.v1"
    assert manifest["task_id"] == "T029"
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    assert {profile["candidate_id"] for profile in profiles} == EXPECTED_CANDIDATES
    assert (
        manifest["completion_state"]
        == "Q4_PROFILE_SET_READY_NOT_T029_COMPLETE_CANONICAL"
    )
    assert manifest["pending"] == []
    assert all(profile["result_classification"] == "Q4_PROFILE_READY" for profile in profiles)
    qwen = next(profile for profile in profiles if profile["candidate_id"] == "qwen3.5-2b")
    q4ks = qwen["quantization_arms"]["Q4_K_S"]
    assert q4ks["output_sha256"] == (
        "a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9"
    )
    assert len(q4ks["output_sha256"]) == 64
    assert q4ks["output_size_bytes"] == 1246308960

def test_all_other_q4_hash_cells_are_valid_sha256_hex() -> None:
    manifest = _load(MANIFEST_PATH)
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    for profile in profiles:
        assert len(profile["model_revision"]) == 40
        assert len(profile["llama_cpp_commit"]) == 40
        assert len(profile["f16_sha256"]) == 64
        for arm in profile["quantization_arms"].values():
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
    assert (
        provenance["artifact_report_sha256"]
        == "120dfabdc328bb7f2adceffd534c651edef57d6dfb9f5dbf0add627f1364b194"
    )
    assert len(provenance["q4_k_m_sha256"]) == 64
    assert len(provenance["q4_k_s_sha256"]) == 64


def test_qwen_historical_provenance_binds_valid_primary_value() -> None:
    provenance = _load(QWEN_PROVENANCE)
    assert provenance["workflow_run_id"] == 32959707029
    assert provenance["workflow_run_conclusion"] == "success"
    assert provenance["material_job_id"] == 98149126772
    assert provenance["material_job_conclusion"] == "success"
    assert provenance["artifact_id"] == 9603552151
    assert (
        provenance["artifact_archive_digest"]
        == "sha256:69a78e2185337b58940b2dc3ab993d182fa9be9f3eaad95fa43a5bf682f9e4a3"
    )
    assert (
        provenance["artifact_report_sha256"]
        == "aad35a2f4db1aff3f2a436a7b98d03a92def063067fc9f294d4a0fcabd8f5d61"
    )
    assert provenance["q4_k_s_sha256"] == (
        "a6fe3727940dde3382e2f2a353a51bc2e6970d4e660260428899c29c8e4583e9"
    )
    assert provenance["q4_k_s_sha256_length"] == 64
    assert provenance["primary_artifact_verdict"] == "Q4_PROFILE_READY"
    assert provenance["reconciliation_negative_run"] == 33964325389
