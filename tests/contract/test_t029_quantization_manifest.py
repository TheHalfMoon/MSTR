from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-q4-profiles.json"
EXPECTED_READY = {
    "granite-4.1-3b",
    "ministral-3-3b",
    "qwen2.5-coder-1.5b",
    "qwen3-4b",
    "qwen3.5-2b",
    "qwen3.5-4b",
    "smollm3-3b",
    "yi-coder-1.5b",
}


def _manifest() -> dict[str, object]:
    decoded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def test_recovered_t029_manifest_binds_all_eight_ready_profiles() -> None:
    manifest = _manifest()

    assert manifest["format_version"] == "mstr.t029.quantization-manifest.v1"
    assert "schema_version" not in manifest
    assert manifest["task_id"] == "T029"
    assert (
        manifest["source_execution_head"]
        == "406de41d132fa6d24d55814f3f6dd4fced5f12bd"
    )
    assert (
        manifest["recovery_execution_head"]
        == "f0f0210a43fb0c70839259d29f9b8a24d7ca3f55"
    )
    assert (
        manifest["completion_state"]
        == "Q4_PROFILE_SET_READY_NOT_T029_COMPLETE_CANONICAL"
    )

    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    assert {profile["candidate_id"] for profile in profiles} == EXPECTED_READY
    assert manifest["pending"] == []


def test_ministral_recovery_profile_binds_exact_actions_artifact_and_hashes() -> None:
    manifest = _manifest()
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    ministral = next(
        profile for profile in profiles if profile["candidate_id"] == "ministral-3-3b"
    )

    assert (
        ministral["model_revision"]
        == "6f9c4b12a95b139af68670a6713616b757923735"
    )
    assert ministral["actions_run_id"] == 33263175072
    assert ministral["actions_artifact_id"] == 9729481097
    assert (
        ministral["f16_sha256"]
        == "30b2f0f8cf5a0b0c5ac3599d3b3de777df74714d49375e43359bb4c1fddbc1de"
    )
    assert ministral["f16_size_bytes"] == 6866212448
    assert ministral["quantization_arms"] == {
        "Q4_K_M": {
            "output_sha256": (
                "31a399bb99a851698948b0d0db5178ac64d20c55048b71a87d3fc25d0b9f0291"
            ),
            "output_size_bytes": 2146489952,
            "duration_s": 111.9,
        },
        "Q4_K_S": {
            "output_sha256": (
                "81575340aac45340dc947bcab07c1d25b5f02c10ad5fa32c69e45a48803ce4aa"
            ),
            "output_size_bytes": 2053248608,
            "duration_s": 120.3,
        },
    }


def test_recovered_profiles_bind_exact_q4_artifact_identity() -> None:
    manifest = _manifest()
    profiles = manifest["profiles"]
    assert isinstance(profiles, list)

    for profile in profiles:
        assert profile["result_classification"] == "Q4_PROFILE_READY"
        assert profile["resource_cost"] == "USD 0.00"
        assert len(profile["model_revision"]) == 40
        assert len(profile["llama_cpp_commit"]) == 40
        assert len(profile["f16_sha256"]) == 64
        assert profile["f16_size_bytes"] > 0
        assert profile["actions_run_id"] > 0
        assert profile["actions_artifact_id"] > 0

        arms = profile["quantization_arms"]
        assert set(arms) == {"Q4_K_M", "Q4_K_S"}
        for arm in arms.values():
            assert len(arm["output_sha256"]) == 64
            assert arm["output_size_bytes"] > 0
            assert arm["duration_s"] >= 0
