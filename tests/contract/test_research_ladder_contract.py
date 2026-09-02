from __future__ import annotations

import hashlib
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
        "evidence_kind",
        "data_identity_or_na",
        "difficulty_identity_or_na",
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


def _valid_research_experiment() -> dict[str, object]:
    return _json(FIXTURES / "valid" / "mstr-research-experiment-v2.json")


def _governed_effects(*enabled: str) -> dict[str, bool]:
    effects = {
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
    for effect in enabled:
        effects[effect] = True
    return effects


def _required_gate_ids(level: str) -> list[str]:
    config = _json(CONFIG)
    levels = config["levels"]
    assert isinstance(levels, list)
    for item in levels:
        assert isinstance(item, dict)
        if item["level"] == level:
            gate_ids = item["required_gate_ids"]
            assert isinstance(gate_ids, list)
            return [str(value) for value in gate_ids]
    raise AssertionError(level)


def _set_required_gates(fixture: dict[str, object], level: str) -> None:
    fixture["hard_gate_results"] = [
        {
            "gate_id": gate_id,
            "status": "PASS",
            "evidence_identity": f"fixture:{gate_id}",
            "reason": "Required hard gate passed.",
        }
        for gate_id in _required_gate_ids(level)
    ]


def _write_json_with_sha(path: Path, value: dict[str, object]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + "\n").encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def _registry_path(root: Path, task_id: str, experiment_id: str) -> Path:
    return (
        root
        / "artifacts"
        / "results"
        / "research"
        / task_id
        / "registry"
        / f"{experiment_id}.json"
    )


def _make_level_record(
    level_index: int,
    *,
    task_id: str,
    campaign_id: str,
    predecessor_id: str | None = None,
    predecessor_sha: str | None = None,
    predecessor_result: str | None = None,
) -> dict[str, object]:
    fixture = _valid_research_experiment()
    level = LEVELS[level_index]
    fixture["experiment_id"] = f"fixture-l{level_index}"
    fixture["governing_task_id"] = task_id
    fixture["campaign_id"] = campaign_id
    fixture["fidelity_level"] = level
    fixture["governed_effects"] = _governed_effects()
    fixture["external_effect_authority"] = None
    results = fixture["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]
    result_id = f"result-l{level_index}"
    result["result_id"] = result_id
    fixture["promoted_result_id_or_na"] = result_id
    fixture["q4_promotion_record_identity_or_na"] = "N/A"
    _set_required_gates(fixture, level)

    if level_index == 0:
        fixture["predecessor_promotion"] = None
        fixture["parent_identity"] = "fixture-parent:N/A"
    else:
        assert predecessor_id is not None
        assert predecessor_sha is not None
        assert predecessor_result is not None
        fixture["predecessor_promotion"] = {
            "experiment_id": predecessor_id,
            "experiment_record_sha256": predecessor_sha,
        }
        fixture["parent_identity"] = predecessor_result

    if level == "L1_CODE_PROXY":
        result["sampling_config_id_or_na"] = "sampling:fixture-v1"
    elif level == "L2_EXECUTABLE_REPO":
        result["cpu_identity_or_na"] = "cpu:fixture"
        result["verifier_health_id_or_na"] = "verifier-health:fixture"
    elif level == "L3_DIRECTION_TO_DONE":
        result["interaction_contract_version_or_na"] = "interaction:fixture-v1"
        result["loop_contract_version_or_na"] = "loop:fixture-v1"
        result["harness_profile_id_or_na"] = "harness:fixture-v1"
        result["verifier_health_id_or_na"] = "verifier-health:fixture"
    elif level == "L4_Q4_UNIVERSAL_LAPTOP":
        result.update(
            {
                "model_id_or_na": "fixture/model",
                "model_revision_or_na": "revision-1",
                "model_artifact_sha256_or_na": "a" * 64,
                "tokenizer_id_or_na": "fixture/tokenizer",
                "tokenizer_revision_or_na": "tokenizer-revision-1",
                "quantization_method_or_na": "Q4_K_M",
                "quantizer_tool_revision_or_na": "llama.cpp:fixture-revision",
                "runtime_id_or_na": "llama.cpp",
                "runtime_version_or_commit_or_na": "runtime-revision-1",
                "runtime_build_flags_or_na": "CPU_ONLY=1",
                "os_identity_or_na": "macOS-fixture",
                "cpu_identity_or_na": "cpu:universal-laptop-fixture",
                "total_ram_bytes_or_na": 8 * 1024 * 1024 * 1024,
                "thread_count_or_na": 8,
                "acceleration_backend_or_na": "CPU",
                "context_length_or_na": 8192,
                "cache_state_or_na": "cold",
            }
        )
        q4_record = "q4-promotion:fixture-l4"
        fixture["q4_promotion_record_identity_or_na"] = q4_record
        gates = fixture["hard_gate_results"]
        assert isinstance(gates, list)
        for gate in gates:
            assert isinstance(gate, dict)
            if gate["gate_id"] == "q4_artifact_identity":
                gate["evidence_identity"] = f"sha256:{'a' * 64}"
            if gate["gate_id"] == "q4_promotion_record_promoted":
                gate["evidence_identity"] = q4_record
    return fixture


def _write_promoted_chain(
    root: Path, through_index: int
) -> tuple[list[dict[str, object]], list[str]]:
    task_id = "B027"
    campaign_id = "campaign-registry-fixture"
    records: list[dict[str, object]] = []
    shas: list[str] = []
    for index in range(through_index + 1):
        predecessor = records[index - 1] if index else None
        record = _make_level_record(
            index,
            task_id=task_id,
            campaign_id=campaign_id,
            predecessor_id=str(predecessor["experiment_id"]) if predecessor else None,
            predecessor_sha=shas[index - 1] if predecessor else None,
            predecessor_result=str(predecessor["promoted_result_id_or_na"])
            if predecessor
            else None,
        )
        validate_instance("mstr-research-experiment-v2", record, repository_root=root)
        sha = _write_json_with_sha(
            _registry_path(root, task_id, str(record["experiment_id"])),
            record,
        )
        records.append(record)
        shas.append(sha)
    return records, shas


def _write_authority(
    root: Path,
    *,
    authority_id: str,
    task_id: str,
    campaign_id: str,
    effects: list[str],
    max_paid: float = 2.0,
    max_wall: float = 60.0,
    max_results: int = 4,
) -> str:
    record: dict[str, object] = {
        "authority_id": authority_id,
        "task_id": task_id,
        "external_effect_class": effects[-1],
        "status": "AUTHORIZED_CANONICAL",
        "scope": {
            "campaign_id": campaign_id,
            "research_ladder_id": "mstr-research-ladder-v0",
            "research_effects": effects,
        },
        "cost_resource_ceiling": {
            "cost_model": "fixed-cap",
            "limits": [
                {"resource": "paid_cost_usd", "max": max_paid, "unit": "USD"},
                {"resource": "wall_time_seconds", "max": max_wall, "unit": "seconds"},
                {"resource": "material_results", "max": max_results, "unit": "count"},
            ],
        },
    }
    return _write_json_with_sha(
        root / "artifacts" / "authorities" / f"{authority_id}.json",
        record,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_id_or_na", "unknown"),
        ("tokenizer_revision_or_na", "TBD"),
        ("runtime_id_or_na", " latest "),
        ("task_manifest_id", "none"),
        ("verifier_manifest_id", "HEAD"),
    ],
)
def test_material_result_identity_rejects_opaque_identity_sentinels(
    field: str, value: str
) -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture[field] = value
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)


def test_material_result_identity_requires_real_sha256_when_applicable() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture["model_artifact_sha256_or_na"] = "unknown"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)
    fixture["model_artifact_sha256_or_na"] = "a" * 64
    validate_instance("mstr-material-result-identity-v0", fixture)


def test_research_experiment_l0_requires_null_predecessor() -> None:
    fixture = _valid_research_experiment()
    fixture["predecessor_promotion"] = {
        "experiment_id": "fake-l0",
        "experiment_record_sha256": "a" * 64,
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_l1_requires_real_immutable_predecessor_registry_record(tmp_path: Path) -> None:
    l0 = _make_level_record(0, task_id="B027", campaign_id="campaign-registry-fixture")
    l0_sha = _write_json_with_sha(_registry_path(tmp_path, "B027", "fixture-l0"), l0)
    l1 = _make_level_record(
        1,
        task_id="B027",
        campaign_id="campaign-registry-fixture",
        predecessor_id="fixture-l0",
        predecessor_sha=l0_sha,
        predecessor_result=str(l0["promoted_result_id_or_na"]),
    )
    validate_instance("mstr-research-experiment-v2", l1, repository_root=tmp_path)

    predecessor = l1["predecessor_promotion"]
    assert isinstance(predecessor, dict)
    predecessor["experiment_id"] = "fictional-predecessor"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", l1, repository_root=tmp_path)


def test_predecessor_registry_digest_and_sequential_level_fail_closed(tmp_path: Path) -> None:
    records, shas = _write_promoted_chain(tmp_path, 2)
    l3 = _make_level_record(
        3,
        task_id="B027",
        campaign_id="campaign-registry-fixture",
        predecessor_id=str(records[2]["experiment_id"]),
        predecessor_sha=shas[2],
        predecessor_result=str(records[2]["promoted_result_id_or_na"]),
    )
    validate_instance("mstr-research-experiment-v2", l3, repository_root=tmp_path)
    predecessor = l3["predecessor_promotion"]
    assert isinstance(predecessor, dict)
    predecessor["experiment_record_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", l3, repository_root=tmp_path)


def test_research_experiment_enforces_material_count_and_declared_budgets() -> None:
    fixture = _valid_research_experiment()
    aggregate = fixture["aggregate_resource_cost"]
    budget = fixture["budget"]
    assert isinstance(aggregate, dict)
    assert isinstance(budget, dict)
    aggregate["material_result_count"] = 2
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
    aggregate["material_result_count"] = 1
    aggregate["wall_time_seconds"] = 61
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
    aggregate["wall_time_seconds"] = 0.01
    results = fixture["material_results"]
    assert isinstance(results, list)
    second = json.loads(json.dumps(results[0]))
    assert isinstance(second, dict)
    second["result_id"] = "b026-l0-contract-smoke-002"
    results.append(second)
    budget["max_material_results"] = 1
    aggregate["material_result_count"] = 2
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_training_evidence_requires_data_difficulty_and_effect_declaration() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture["evidence_kind"] = "TRAINING_EVIDENCE"
    fixture["data_identity_or_na"] = "N/A"
    fixture["difficulty_identity_or_na"] = "N/A"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)
    fixture["data_identity_or_na"] = "data-manifest:fixture-v1"
    fixture["difficulty_identity_or_na"] = "difficulty-calibration:fixture-v1"
    validate_instance("mstr-material-result-identity-v0", fixture)

    experiment = _valid_research_experiment()
    results = experiment["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    results[0]["evidence_kind"] = "TRAINING_EVIDENCE"
    results[0]["data_identity_or_na"] = "data-manifest:fixture-v1"
    results[0]["difficulty_identity_or_na"] = "difficulty-calibration:fixture-v1"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", experiment)


def test_promotion_requires_exact_per_level_gate_coverage(tmp_path: Path) -> None:
    records, shas = _write_promoted_chain(tmp_path, 4)
    for index, record in enumerate(records):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)
        gates = record["hard_gate_results"]
        assert isinstance(gates, list)
        removed = gates.pop()
        with pytest.raises(ValueError, match="validation failed"):
            validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)
        gates.append(removed)
        gates.append(
            {
                "gate_id": "invented_gate",
                "status": "PASS",
                "evidence_identity": "fixture:invented",
                "reason": "Must not satisfy promotion.",
            }
        )
        with pytest.raises(ValueError, match="validation failed"):
            validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)
        gates.pop()
        assert record["fidelity_level"] == LEVELS[index]


def test_l4_requires_concrete_q4_identity_and_binds_gate_evidence(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    results = l4["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]
    result["model_artifact_sha256_or_na"] = "N/A"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
    result["model_artifact_sha256_or_na"] = "a" * 64
    gates = l4["hard_gate_results"]
    assert isinstance(gates, list)
    for gate in gates:
        assert isinstance(gate, dict)
        if gate["gate_id"] == "q4_artifact_identity":
            gate["evidence_identity"] = "sha256:" + "b" * 64
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)


def test_external_effect_resolves_canonical_authority_and_ceilings(tmp_path: Path) -> None:
    fixture = _valid_research_experiment()
    fixture["governing_task_id"] = "B027"
    fixture["campaign_id"] = "authority-campaign"
    fixture["governed_effects"] = _governed_effects("PAID_COMPUTE", "RENTED_COMPUTE")
    budget = fixture["budget"]
    aggregate = fixture["aggregate_resource_cost"]
    results = fixture["material_results"]
    assert isinstance(budget, dict)
    assert isinstance(aggregate, dict)
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]
    resource_cost = result["resource_cost"]
    assert isinstance(resource_cost, dict)
    budget["resource_class"] = "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    budget["max_paid_cost_usd"] = 2
    aggregate["resource_class"] = "AUTHORIZED_EXTERNAL_EFFECT"
    aggregate["paid_cost_usd"] = 1
    result["paid_cost_usd"] = 1
    resource_cost["cost_class"] = "AUTHORIZED_REMOTE_COMPUTE"
    authority_id = "AUTH-B027-RESEARCH"
    authority_sha = _write_authority(
        tmp_path,
        authority_id=authority_id,
        task_id="B027",
        campaign_id="authority-campaign",
        effects=["PAID_COMPUTE", "RENTED_COMPUTE"],
    )
    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)

    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": "f" * 64,
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)


def test_authority_scope_is_derived_not_self_attested(tmp_path: Path) -> None:
    fixture = _valid_research_experiment()
    fixture["governing_task_id"] = "B027"
    fixture["campaign_id"] = "authority-campaign"
    fixture["governed_effects"] = _governed_effects("PAID_COMPUTE")
    budget = fixture["budget"]
    aggregate = fixture["aggregate_resource_cost"]
    results = fixture["material_results"]
    assert isinstance(budget, dict) and isinstance(aggregate, dict)
    assert isinstance(results, list) and isinstance(results[0], dict)
    budget["resource_class"] = "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    budget["max_paid_cost_usd"] = 2
    aggregate["resource_class"] = "AUTHORIZED_EXTERNAL_EFFECT"
    aggregate["paid_cost_usd"] = 1
    results[0]["paid_cost_usd"] = 1
    authority_id = "AUTH-B027-NARROW"
    authority_sha = _write_authority(
        tmp_path,
        authority_id=authority_id,
        task_id="B027",
        campaign_id="authority-campaign",
        effects=["PAID_COMPUTE"],
        max_paid=0.5,
    )
    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)


def test_paid_result_cost_must_reconcile_to_aggregate() -> None:
    fixture = _valid_research_experiment()
    results = fixture["material_results"]
    aggregate = fixture["aggregate_resource_cost"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    assert isinstance(aggregate, dict)
    results[0]["paid_cost_usd"] = 100
    aggregate["paid_cost_usd"] = 0
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_non_external_record_rejects_authority_binding() -> None:
    fixture = _valid_research_experiment()
    fixture["external_effect_authority"] = {
        "authority_id": "AUTH-UNUSED",
        "authority_record_sha256": "b" * 64,
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
