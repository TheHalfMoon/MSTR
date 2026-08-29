from __future__ import annotations

import json
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPOSITORY_ROOT / "artifacts/manifests/quantization/T029-q4-profiles.json"
EXPECTED_READY = {
    "granite-4.1-3b",
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


def test_recovered_t029_manifest_is_explicitly_partial() -> None:
    manifest = _manifest()

    assert manifest["format_version"] == "mstr.t029.quantization-manifest.v1"
    assert "schema_version" not in manifest
    assert manifest["task_id"] == "T029"
    assert manifest["completion_state"] == "PARTIAL_RECOVERY_NOT_T029_COMPLETE_CANONICAL"

    profiles = manifest["profiles"]
    assert isinstance(profiles, list)
    assert {profile["candidate_id"] for profile in profiles} == EXPECTED_READY

    pending = manifest["pending"]
    assert pending == [
        {
            "candidate_id": "ministral-3-3b",
            "status": "PENDING_RETRY_AFTER_RUNNER_FIX",
            "failed_actions_run_id": 32959718688,
            "failure": "UnicodeDecodeError while decoding llama-quantize output",
            "runner_fix_branch": "fix/000-t029-nonutf8-quantizer-output",
        }
    ]


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
