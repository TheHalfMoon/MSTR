from __future__ import annotations

import hashlib
import json
import subprocess
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
        "model_artifact_size_bytes_or_na",
        "model_execution_count_or_na",
        "network_model_or_teacher_call_count_or_na",
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


def test_research_experiment_promotion_requires_all_hard_gates_pass(tmp_path: Path) -> None:
    fixture = _make_level_record(0, task_id="B027", campaign_id="gate-status-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list)
    assert isinstance(gates[0], dict)
    gates[0]["status"] = "FAIL"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)


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


def _write_content_addressed(path: Path, value: dict[str, object]) -> str:
    path.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    (path / f"{digest}.json").write_bytes(raw)
    return f"sha256:{digest}"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def _ensure_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
        _git(root, "config", "user.name", "MSTR Contract Test")
        _git(root, "config", "user.email", "mstr-contract@example.invalid")


def _commit_all(root: Path, message: str) -> str:
    _ensure_git_repo(root)
    _git(root, "add", "-A")
    if not _git(root, "status", "--porcelain"):
        raise AssertionError(f"expected changes before commit: {message}")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


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


def _prepare_policy_and_gate_evidence(root: Path, record: dict[str, object]) -> None:
    _ensure_git_repo(root)
    record["record_mode"] = "CAMPAIGN_RESULT"
    record["promotion_decision"] = "PROMOTE"
    record["decision_reason"] = "Synthetic contract test campaign satisfies all required gates."
    task_id = str(record["governing_task_id"])
    campaign_id = str(record["campaign_id"])
    experiment_id = str(record["experiment_id"])
    level = str(record["fidelity_level"])
    effects = record["governed_effects"]
    assert isinstance(effects, dict)
    results = record["material_results"]
    assert isinstance(results, list) and results and isinstance(results[0], dict)
    if record.get("promoted_result_id_or_na") == "N/A":
        promoted_result_id = results[0].get("result_id")
        if not isinstance(promoted_result_id, str) or not promoted_result_id:
            raise AssertionError("synthetic campaign requires one concrete material result_id")
        record["promoted_result_id_or_na"] = promoted_result_id

    enabled_effects = [name for name, enabled in effects.items() if enabled is True]
    if enabled_effects and record.get("external_effect_authority") is None:
        authority_id = f"AUTH-{task_id}-{experiment_id}"
        authority_sha = _write_authority(
            root,
            authority_id=authority_id,
            task_id=task_id,
            campaign_id=campaign_id,
            effects=enabled_effects,
            max_paid=100.0,
            max_wall=3600.0,
            max_results=100,
        )
        record["external_effect_authority"] = {
            "authority_id": authority_id,
            "authority_record_sha256": authority_sha,
        }

    policy = {
        "schema_version": "mstr.research-promotion-policy.v0",
        "governing_task_id": task_id,
        "campaign_id": campaign_id,
        "fidelity_level": level,
        "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
        "criteria": [
            (
                {
                    "gate_id": gate_id,
                    "operator": "EQ_PROMOTED_ARTIFACT",
                    "expected_value": "PROMOTED_RESULT_ARTIFACT",
                }
                if gate_id == "q4_artifact_identity"
                else {"gate_id": gate_id, "operator": "EQ", "expected_value": True}
            )
            for gate_id in _required_gate_ids(level)
        ],
    }
    record["promotion_policy_identity"] = _write_content_addressed(
        root / "artifacts/results/research" / task_id / "promotion-policies",
        policy,
    )
    freeze_sha = _commit_all(root, f"freeze {experiment_id}")
    record["campaign_freeze_commit_sha_or_na"] = freeze_sha

    gates = record["hard_gate_results"]
    assert isinstance(gates, list)
    for gate in gates:
        assert isinstance(gate, dict)
        gate_id = str(gate["gate_id"])
        observed_value: object = True
        if gate_id == "q4_artifact_identity":
            results = record["material_results"]
            promoted_id = record["promoted_result_id_or_na"]
            assert isinstance(results, list)
            promoted = next(
                result
                for result in results
                if isinstance(result, dict) and result.get("result_id") == promoted_id
            )
            observed_value = promoted["model_artifact_sha256_or_na"]
        material_results = record["material_results"]
        promoted_id = record["promoted_result_id_or_na"]
        assert isinstance(material_results, list)
        subject_material = next(
            result
            for result in material_results
            if isinstance(result, dict) and result.get("result_id") == promoted_id
        )
        subject_identity = str(promoted_id)
        subject_evidence_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "subject-evidence",
            {
                "schema_version": "mstr.research-subject-evidence.v0",
                "governing_task_id": task_id,
                "campaign_id": campaign_id,
                "experiment_id": experiment_id,
                "subject_identity": subject_identity,
                "material_result": json.loads(json.dumps(subject_material)),
            },
        )
        verifier_manifest_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-manifests",
            {
                "schema_version": "mstr.research-verifier-manifest.v0",
                "verifier_manifest_id": f"fixture-verifier-manifest:{gate_id}",
                "gate_id": gate_id,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            },
        )
        verifier_health_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-health",
            {
                "schema_version": "mstr.research-verifier-health.v0",
                "verifier_health_id": f"fixture-verifier-health:{gate_id}",
                "verifier_manifest_identity": verifier_manifest_identity,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
                "status": "HEALTHY",
            },
        )
        verifier_result_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-results",
            {
                "schema_version": "mstr.research-verifier-result.v0",
                "governing_task_id": task_id,
                "campaign_id": campaign_id,
                "experiment_id": experiment_id,
                "gate_id": gate_id,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
                "verifier_manifest_identity": verifier_manifest_identity,
                "verifier_health_identity": verifier_health_identity,
                "subject_identity": subject_identity,
                "subject_evidence_identity": subject_evidence_identity,
                "observed_value": observed_value,
            },
        )
        source = {
            "schema_version": "mstr.research-verifier-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            "verifier_manifest_identity": verifier_manifest_identity,
            "verifier_health_identity": verifier_health_identity,
            "subject_identity": subject_identity,
            "subject_evidence_identity": subject_evidence_identity,
            "verifier_result_identity": verifier_result_identity,
            "verifier_result_json_pointer": "/observed_value",
        }
        source_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-evidence",
            source,
        )
        evidence = {
            "schema_version": "mstr.research-gate-evidence.v1",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            "campaign_freeze_commit_sha": freeze_sha,
            "source_evidence_identity": source_identity,
            "source_json_pointer": "/observed_value",
        }
        gate["evidence_identity"] = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "gate-evidence",
            evidence,
        )

    record["q4_promotion_record_identity_or_na"] = "N/A"
    record["q4_candidate_binding_identity_or_na"] = "N/A"
    if level == "L4_Q4_UNIVERSAL_LAPTOP":
        results = record["material_results"]
        assert isinstance(results, list) and isinstance(results[0], dict)
        result = results[0]
        gate_map = {str(gate["gate_id"]): gate for gate in gates if isinstance(gate, dict)}
        q4_record: dict[str, object] = {
            "schema_version": "mstr.q4-promotion.v0",
            "source_training_run_id": "fixture-training-run",
            "source_checkpoint_sha256": "b" * 64,
            "merged_master_sha256": "c" * 64,
            "export_tool_id": "fixture-export",
            "export_tool_revision": "fixture-export-revision",
            "export_recipe_hash": "d" * 64,
            "quantizer_tool_id": "fixture-quantizer",
            "quantizer_tool_revision": "fixture-quantizer-revision",
            "quantization_recipe_hash": "e" * 64,
            "canonical_q4_artifact_sha256": str(result["model_artifact_sha256_or_na"]),
            "artifact_integrity_status": "PASS",
            "q4_regression_manifest_id": "fixture-q4-regression",
            "q4_regression_result": "PASS",
            "universal_laptop_gate_result": "PASS",
            "universal_laptop_gate_evidence_identity": str(
                gate_map["universal_laptop_product_gates"]["evidence_identity"]
            ),
            "universal_laptop_gate_not_required_reason": None,
            "promotion_status": "PROMOTED",
            "rejection_reasons": [],
            "promotion_decision_evidence_identity": str(
                gate_map["q4_promotion_record_promoted"]["evidence_identity"]
            ),
        }
        q4_identity = _write_content_addressed(
            root / "artifacts/results/q4-promotion/registry",
            q4_record,
        )
        record["q4_promotion_record_identity_or_na"] = q4_identity
        binding = {
            "schema_version": "mstr.research-q4-candidate-binding.v0",
            "q4_promotion_record_identity": q4_identity,
            "model_id": str(result["model_id_or_na"]),
            "model_revision": str(result["model_revision_or_na"]),
            "source_checkpoint_sha256": str(q4_record["source_checkpoint_sha256"]),
            "canonical_q4_artifact_sha256": str(result["model_artifact_sha256_or_na"]),
        }
        record["q4_candidate_binding_identity_or_na"] = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "q4-bindings",
            binding,
        )

    evidence_sha = _commit_all(root, f"evidence {experiment_id}")
    record["canonical_evidence_commit_sha_or_na"] = evidence_sha


def _registry_path(root: Path, task_id: str, experiment_id: str) -> Path:
    return (
        root / "artifacts" / "results" / "research" / task_id / "registry" / f"{experiment_id}.json"
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
    fixture["record_mode"] = "CAMPAIGN_RESULT"
    fixture["experiment_id"] = f"fixture-l{level_index}"
    fixture["governing_task_id"] = task_id
    fixture["campaign_id"] = campaign_id
    fixture["fidelity_level"] = level
    fixture["promotion_decision"] = "PROMOTE"
    fixture["decision_reason"] = "Synthetic campaign result promoted for contract testing."
    fixture["campaign_freeze_commit_sha_or_na"] = "N/A"
    fixture["canonical_evidence_commit_sha_or_na"] = "N/A"
    fixture["promotion_policy_identity"] = "N/A"
    fixture["q4_candidate_binding_identity_or_na"] = "N/A"
    fixture["governed_effects"] = _governed_effects()
    fixture["external_effect_authority"] = None
    results = fixture["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]
    result_id = f"result-l{level_index}"
    result["result_id"] = result_id
    result["model_execution_count_or_na"] = 0
    result["network_model_or_teacher_call_count_or_na"] = 0
    result["model_artifact_size_bytes_or_na"] = "N/A"
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
        effects = fixture["governed_effects"]
        assert isinstance(effects, dict)
        effects["MODEL_EXECUTION"] = True
        result.update(
            {
                "model_id_or_na": "fixture/model",
                "model_revision_or_na": "revision-1",
                "model_artifact_sha256_or_na": "a" * 64,
                "model_artifact_size_bytes_or_na": 2 * 1024**3,
                "model_execution_count_or_na": 1,
                "network_model_or_teacher_call_count_or_na": 0,
                "tokenizer_id_or_na": "fixture/tokenizer",
                "tokenizer_revision_or_na": "tokenizer-revision-1",
                "quantization_method_or_na": "Q4_K_M",
                "quantizer_tool_revision_or_na": "llama.cpp:fixture-revision",
                "runtime_id_or_na": "llama.cpp",
                "runtime_version_or_commit_or_na": "runtime-revision-1",
                "runtime_build_flags_or_na": "CPU_ONLY=1",
                "os_identity_or_na": "macOS-fixture",
                "cpu_identity_or_na": "cpu:universal-laptop-fixture",
                "total_ram_bytes_or_na": 8 * 1024**3,
                "thread_count_or_na": 8,
                "acceleration_backend_or_na": "CPU",
                "context_length_or_na": 8192,
                "cache_state_or_na": "cold",
            }
        )
    return fixture


def _write_promoted_chain(
    root: Path, through_index: int
) -> tuple[list[dict[str, object]], list[str]]:
    _ensure_git_repo(root)
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
        _prepare_policy_and_gate_evidence(root, record)
        validate_instance("mstr-research-experiment-v2", record, repository_root=root)
        sha = _write_json_with_sha(
            _registry_path(root, task_id, str(record["experiment_id"])),
            record,
        )
        records.append(record)
        shas.append(sha)
    return records, shas


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
def test_material_result_identity_rejects_opaque_identity_sentinels(field: str, value: str) -> None:
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
    _prepare_policy_and_gate_evidence(tmp_path, l0)
    l0_sha = _write_json_with_sha(_registry_path(tmp_path, "B027", "fixture-l0"), l0)
    l1 = _make_level_record(
        1,
        task_id="B027",
        campaign_id="campaign-registry-fixture",
        predecessor_id="fixture-l0",
        predecessor_sha=l0_sha,
        predecessor_result=str(l0["promoted_result_id_or_na"]),
    )
    _prepare_policy_and_gate_evidence(tmp_path, l1)
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
    _prepare_policy_and_gate_evidence(tmp_path, l3)
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
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
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
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
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


def test_b026_runtime_and_spec_schema_pairs_are_byte_identical() -> None:
    pairs = (
        (
            ROOT / "schemas/mstr-material-result-identity-v0.schema.json",
            ROOT / "specs/002-code-model-supremacy-foundation/contracts/"
            "mstr-material-result-identity-v0.schema.json",
        ),
        (
            ROOT / "schemas/mstr-research-experiment-v2.schema.json",
            ROOT / "specs/002-code-model-supremacy-foundation/contracts/"
            "mstr-research-experiment-v2.schema.json",
        ),
    )
    for runtime, design in pairs:
        assert runtime.read_bytes() == design.read_bytes()


def test_promote_requires_every_required_gate_to_pass(tmp_path: Path) -> None:
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


def test_non_l4_promote_rejects_q4_promotion_evidence() -> None:
    fixture = _valid_research_experiment()
    fixture["q4_promotion_record_identity_or_na"] = "q4-promotion:out-of-scope"
    with pytest.raises(
        ValueError,
        match="only L4 PROMOTE may bind Q4 promotion evidence",
    ):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_research_nested_validation_preserves_custom_schema_dir(tmp_path: Path) -> None:
    records, shas = _write_promoted_chain(tmp_path, 0)
    predecessor = records[0]
    current = _make_level_record(
        1,
        task_id="B027",
        campaign_id=str(predecessor["campaign_id"]),
        predecessor_id=str(predecessor["experiment_id"]),
        predecessor_sha=shas[0],
        predecessor_result=str(predecessor["promoted_result_id_or_na"]),
    )
    _prepare_policy_and_gate_evidence(tmp_path, current)

    custom_dir = tmp_path / "custom-schemas"
    custom_dir.mkdir()
    schema = _json(ROOT / "schemas/mstr-research-experiment-v2.schema.json")
    all_of = schema["allOf"]
    assert isinstance(all_of, list)
    all_of.append(
        {
            "if": {
                "properties": {"fidelity_level": {"const": "L0_CONTRACT_SMOKE"}},
                "required": ["fidelity_level"],
            },
            "then": {
                "properties": {"decision_reason": {"const": "CUSTOM_SCHEMA_PREDECESSOR_SENTINEL"}}
            },
        }
    )
    (custom_dir / "mstr-research-experiment-v2.schema.json").write_text(
        json.dumps(schema, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="referenced predecessor record is invalid"):
        validate_instance(
            "mstr-research-experiment-v2",
            current,
            schema_dir=custom_dir,
            repository_root=tmp_path,
        )


def test_data_model_research_record_block_lists_all_required_b026_fields() -> None:
    text = (ROOT / "specs/002-code-model-supremacy-foundation/data-model.md").read_text(
        encoding="utf-8"
    )
    start = text.index("```text\nResearchExperimentRecordV2\n")
    end = text.index("\n```", start)
    block = text[start:end]
    for field in (
        "governing_task_id",
        "promoted_result_id_or_na",
        "q4_promotion_record_identity_or_na",
        "governed_effects",
    ):
        assert f"- {field}" in block


def test_promotion_status_is_computed_from_predeclared_policy_and_content_bound_evidence(
    tmp_path: Path,
) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="policy-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    gates = record["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gate = gates[0]
    gate_digest = str(gate["evidence_identity"]).removeprefix("sha256:")
    gate_path = tmp_path / "artifacts/results/research/B027/gate-evidence" / f"{gate_digest}.json"
    gate_evidence = _json(gate_path)
    source_digest = str(gate_evidence["source_evidence_identity"]).removeprefix("sha256:")
    source_path = (
        tmp_path / "artifacts/results/research/B027/verifier-evidence" / f"{source_digest}.json"
    )
    source = _json(source_path)
    result_digest = str(source["verifier_result_identity"]).removeprefix("sha256:")
    result_path = (
        tmp_path / "artifacts/results/research/B027/verifier-results" / f"{result_digest}.json"
    )
    verifier_result = _json(result_path)
    verifier_result["observed_value"] = False
    source["verifier_result_identity"] = _write_content_addressed(
        result_path.parent,
        verifier_result,
    )
    replacement_source = _write_content_addressed(source_path.parent, source)
    gate_evidence["source_evidence_identity"] = replacement_source
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path, "tamper canonical verifier observation for rejection test"
    )
    with pytest.raises(ValueError, match="submitted status does not match predeclared criterion"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_promotion_policy_missing_or_tampered_fails_closed(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="policy-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    record["promotion_policy_identity"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="policy missing from canonical campaign-freeze commit"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_l4_resolves_promoted_q4_record_and_binds_artifact_and_laptop_evidence(
    tmp_path: Path,
) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)

    l4["q4_promotion_record_identity_or_na"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="immutable Q4 promotion record missing"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)


def test_l4_rejects_q4_record_with_mismatched_artifact(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    q4_digest = str(l4["q4_promotion_record_identity_or_na"]).removeprefix("sha256:")
    q4_path = tmp_path / "artifacts/results/q4-promotion/registry" / f"{q4_digest}.json"
    q4 = _json(q4_path)
    q4["canonical_q4_artifact_sha256"] = "9" * 64
    l4["q4_promotion_record_identity_or_na"] = _write_content_addressed(q4_path.parent, q4)
    l4["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path, "replace Q4 artifact for mismatch test"
    )
    with pytest.raises(ValueError, match="Q4 record artifact must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)


def test_campaign_registry_rejects_worktree_only_records(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="history-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    digest = str(record["promotion_policy_identity"]).removeprefix("sha256:")
    policy_path = tmp_path / "artifacts/results/research/B027/promotion-policies" / f"{digest}.json"
    policy = _json(policy_path)
    policy["criteria"][0]["expected_value"] = False
    record["promotion_policy_identity"] = _write_content_addressed(policy_path.parent, policy)
    with pytest.raises(ValueError, match="policy missing from canonical campaign-freeze commit"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_campaign_policy_freeze_must_strictly_precede_evidence(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="ordering-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    record["campaign_freeze_commit_sha_or_na"] = record["canonical_evidence_commit_sha_or_na"]
    with pytest.raises(ValueError, match="strict canonical-main ancestor"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_model_and_network_execution_require_explicit_governed_effects(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="effects-fixture")
    results = record["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    results[0]["model_execution_count_or_na"] = 1
    results[0]["network_model_or_teacher_call_count_or_na"] = 1
    _prepare_policy_and_gate_evidence(tmp_path, record)
    with pytest.raises(ValueError, match="MODEL_EXECUTION"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    effects = record["governed_effects"]
    assert isinstance(effects, dict)
    effects["MODEL_EXECUTION"] = True
    with pytest.raises(ValueError, match="NETWORK_MODEL_OR_TEACHER_CALL"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_positive_network_bytes_require_network_effect_declaration(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="network-bytes-fixture")
    results = record["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    resource_cost = results[0]["resource_cost"]
    assert isinstance(resource_cost, dict)
    resource_cost["network_bytes_or_na"] = 1
    results[0]["network_model_or_teacher_call_count_or_na"] = 0
    _prepare_policy_and_gate_evidence(tmp_path, record)

    with pytest.raises(ValueError, match="positive network byte evidence"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_verifier_evidence_rejects_unresolvable_underlying_result(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="verifier-result-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    gates = record["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gate = gates[0]
    gate_digest = str(gate["evidence_identity"]).removeprefix("sha256:")
    gate_path = tmp_path / "artifacts/results/research/B027/gate-evidence" / f"{gate_digest}.json"
    gate_evidence = _json(gate_path)
    source_digest = str(gate_evidence["source_evidence_identity"]).removeprefix("sha256:")
    source_path = (
        tmp_path / "artifacts/results/research/B027/verifier-evidence" / f"{source_digest}.json"
    )
    source = _json(source_path)
    source["verifier_result_identity"] = "sha256:" + "f" * 64
    gate_evidence["source_evidence_identity"] = _write_content_addressed(
        source_path.parent,
        source,
    )
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path,
        "point verifier evidence at missing underlying result",
    )

    with pytest.raises(ValueError, match="canonical verifier result missing"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_verifier_subject_evidence_must_match_material_result(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="subject-evidence-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    gates = record["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gate = gates[0]
    gate_digest = str(gate["evidence_identity"]).removeprefix("sha256:")
    gate_path = tmp_path / "artifacts/results/research/B027/gate-evidence" / f"{gate_digest}.json"
    gate_evidence = _json(gate_path)
    source_digest = str(gate_evidence["source_evidence_identity"]).removeprefix("sha256:")
    source_path = (
        tmp_path / "artifacts/results/research/B027/verifier-evidence" / f"{source_digest}.json"
    )
    source = _json(source_path)
    subject_digest = str(source["subject_evidence_identity"]).removeprefix("sha256:")
    subject_path = (
        tmp_path / "artifacts/results/research/B027/subject-evidence" / f"{subject_digest}.json"
    )
    subject = _json(subject_path)
    material_result = subject["material_result"]
    assert isinstance(material_result, dict)
    material_result["decision_reason"] = "not-part-of-material-result"
    replacement_subject = _write_content_addressed(subject_path.parent, subject)
    source["subject_evidence_identity"] = replacement_subject
    result_digest = str(source["verifier_result_identity"]).removeprefix("sha256:")
    result_path = (
        tmp_path / "artifacts/results/research/B027/verifier-results" / f"{result_digest}.json"
    )
    verifier_result = _json(result_path)
    verifier_result["subject_evidence_identity"] = replacement_subject
    source["verifier_result_identity"] = _write_content_addressed(
        result_path.parent,
        verifier_result,
    )
    gate_evidence["source_evidence_identity"] = _write_content_addressed(
        source_path.parent,
        source,
    )
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path,
        "replace subject material evidence with a mismatch",
    )

    with pytest.raises(ValueError, match="subject material evidence must exactly match"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_l4_enforces_exact_universal_laptop_envelope(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    results = l4["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]

    mutations = (
        ("total_ram_bytes_or_na", 64 * 1024**3, "8 GB reference RAM"),
        ("thread_count_or_na", 0, "positive thread count"),
        ("context_length_or_na", 32768, "8K reference context"),
        ("acceleration_backend_or_na", "CUDA", "CPU-only execution"),
        ("model_artifact_size_bytes_or_na", 4 * 1024**3, "at or below 3 GB"),
    )
    for field, bad_value, message in mutations:
        original = result[field]
        result[field] = bad_value
        with pytest.raises(ValueError, match=message):
            validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
        result[field] = original


def test_l4_q4_candidate_binding_rejects_model_identity_relabel(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    results = l4["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    results[0]["model_id_or_na"] = "different/model"
    with pytest.raises(ValueError, match="model_id must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
