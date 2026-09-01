from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "research" / "mstr-research-ladder-v0.json"
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"
LEVELS = [
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
]


def _json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_material_result_identity_requires_every_exact_or_na_field() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    validate_instance("mstr-material-result-identity-v0", fixture)

    required = [
        "model_id_or_na",
        "model_revision_or_na",
        "model_artifact_sha256_or_na",
        "tokenizer_id_or_na",
        "tokenizer_revision_or_na",
        "quantization_method_or_na",
        "quantizer_tool_revision_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "runtime_build_flags_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "total_ram_bytes_or_na",
        "thread_count_or_na",
        "acceleration_backend_or_na",
        "context_length_or_na",
        "cache_state_or_na",
        "interaction_contract_version_or_na",
        "loop_contract_version_or_na",
        "harness_profile_id_or_na",
        "verifier_health_id_or_na",
        "sampling_config_id_or_na",
        "seed_or_na",
        "wall_time_seconds_or_na",
        "invalidation_reason_or_na",
    ]
    for field in required:
        mutated = dict(fixture)
        mutated.pop(field)
        with pytest.raises(ValueError, match="validation failed"):
            validate_instance("mstr-material-result-identity-v0", mutated)


def test_material_result_identity_rejects_null_for_explicit_na() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture["model_id_or_na"] = None
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)


def test_invalid_material_result_requires_concrete_invalidation_reason() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture["result_classification"] = "INVALID"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)

    fixture["invalidation_reason_or_na"] = "schema-invalid:fixture"
    validate_instance("mstr-material-result-identity-v0", fixture)


def test_research_experiment_promotion_requires_all_hard_gates_pass() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-research-experiment-v2.json")
    validate_instance("mstr-research-experiment-v2", fixture)
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list)
    assert isinstance(gates[0], dict)
    gates[0]["status"] = "FAIL"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_research_ladder_is_sequential_and_fail_closed() -> None:
    config = _json(CONFIG)
    levels = config["levels"]
    assert isinstance(levels, list)
    assert [level["level"] for level in levels] == LEVELS
    assert [level["ordinal"] for level in levels] == list(range(5))
    assert all(level["promotion_requires"] for level in levels)
    assert all(level["hard_reject_conditions"] for level in levels)

    assert config["promotion_edges"] == [
        {"from": LEVELS[index], "to": LEVELS[index + 1]} for index in range(4)
    ]
    policy = config["promotion_policy"]
    assert isinstance(policy, dict)
    assert policy["sequential_only"] is True
    assert policy["promotion_criteria_predeclared"] is True
    assert policy["weak_experiments_must_not_run_expensive_levels"] is True
    assert policy["missing_material_identity_invalidates_promotion"] is True
    assert policy["frozen_evaluation_identity_required"] is True
    assert policy["task_eligibility_never_grants_external_effect_authority"] is True


def test_l4_keeps_q4_and_universal_laptop_product_gates() -> None:
    config = _json(CONFIG)
    levels = config["levels"]
    assert isinstance(levels, list)
    l4 = levels[-1]
    serialized = json.dumps(l4, sort_keys=True)
    assert "release-relevant Q4 artifact identity is exact" in serialized
    assert "required universal-laptop product gates pass" in serialized
    assert "8GB/CPU/8K/Q4<=3GB product floor is silently weakened" in serialized
    assert "Q4PromotionRecord" in serialized


def test_b026_config_grants_no_external_effect_authority() -> None:
    config = _json(CONFIG)
    boundary = config["authority_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["contract_freeze_only"] is True
    assert all(value is False for key, value in boundary.items() if key != "contract_freeze_only")
