from __future__ import annotations

from pathlib import Path

PATH = Path("tests/contract/test_research_ladder_contract.py")
text = PATH.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    '''    effects = {
        "MODEL_WEIGHT_ACCESS": False,
        "GATED_TERMS_ACCEPTANCE": False,
        "PAID_MODEL_API_EXECUTION": False,
        "PAID_COMPUTE": False,
        "RENTED_COMPUTE": False,
        "LARGE_DATASET_INGESTION": False,
        "WEIGHT_CHANGING_TRAINING": False,
        "LONG_TRAINING": False,
        "LARGE_SCALE_RL": False,
        "PRODUCTION_RELEASE": False,
    }
''',
    '''    effects = {
        "MODEL_EXECUTION": False,
        "MODEL_WEIGHT_ACCESS": False,
        "GATED_TERMS_ACCEPTANCE": False,
        "PAID_MODEL_API_EXECUTION": False,
        "PAID_COMPUTE": False,
        "RENTED_COMPUTE": False,
        "NETWORK_MODEL_OR_TEACHER_CALL": False,
        "LARGE_DATASET_INGESTION": False,
        "WEIGHT_CHANGING_TRAINING": False,
        "LONG_TRAINING": False,
        "LARGE_SCALE_RL": False,
        "PRODUCTION_RELEASE": False,
    }
''',
    "governed effects fixture helper",
)

replace_once(
    '''    effects = record["governed_effects"]
    assert isinstance(effects, dict)

    enabled_effects = [name for name, enabled in effects.items() if enabled is True]
''',
    '''    effects = record["governed_effects"]
    assert isinstance(effects, dict)
    results = record["material_results"]
    assert isinstance(results, list) and results and isinstance(results[0], dict)
    if record.get("promoted_result_id_or_na") == "N/A":
        promoted_result_id = results[0].get("result_id")
        if not isinstance(promoted_result_id, str) or not promoted_result_id:
            raise AssertionError("synthetic campaign requires one concrete material result_id")
        record["promoted_result_id_or_na"] = promoted_result_id

    enabled_effects = [name for name, enabled in effects.items() if enabled is True]
''',
    "synthetic campaign promoted result selection",
)

replace_once(
    '''def test_promote_requires_every_required_gate_to_pass() -> None:
    config = _json(CONFIG)
    levels = config["levels"]
    assert isinstance(levels, list)
    for level in levels:
        assert isinstance(level, dict)
        requirements = level["promotion_requires"]
        assert isinstance(requirements, list)
        assert "every required hard gate has status PASS" in requirements

    fixture = _valid_research_experiment()
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gates[0]["status"] = "NOT_APPLICABLE"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
''',
    '''def test_promote_requires_every_required_gate_to_pass(tmp_path: Path) -> None:
    config = _json(CONFIG)
    levels = config["levels"]
    assert isinstance(levels, list)
    for level in levels:
        assert isinstance(level, dict)
        requirements = level["promotion_requires"]
        assert isinstance(requirements, list)
        assert "every required hard gate has status PASS" in requirements

    fixture = _make_level_record(0, task_id="B027", campaign_id="all-gates-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gates[0]["status"] = "NOT_APPLICABLE"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
''',
    "all hard gates promotion regression",
)

replace_once(
    'with pytest.raises(ValueError, match="predeclared policy record missing"):',
    'with pytest.raises(ValueError, match="policy missing from canonical campaign-freeze commit"):',
    "canonical policy missing wording",
)

replace_once(
    '''        "model_artifact_sha256_or_na",
        "evidence_kind",
''',
    '''        "model_artifact_sha256_or_na",
        "model_artifact_size_bytes_or_na",
        "model_execution_count_or_na",
        "network_model_or_teacher_call_count_or_na",
        "evidence_kind",
''',
    "material result required-field regression coverage",
)

PATH.write_text(text, encoding="utf-8")
