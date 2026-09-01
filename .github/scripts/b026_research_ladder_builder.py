from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_MAIN = "823cd7ec3b4c537876a0795d0f0f8d4bd75acd85"
POST_CLOSEOUT_RUN = "33564300212"
ROOT = Path.cwd()


def write_json(path: str, payload: object) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {path}, found {count}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def build_material_result_schema() -> dict[str, Any]:
    string_or_na: dict[str, Any] = {
        "type": "string",
        "minLength": 1,
        "maxLength": 1024,
    }
    integer_or_na: dict[str, Any] = {
        "oneOf": [
            {"type": "integer", "minimum": 0},
            {"const": "N/A"},
        ]
    }
    number_or_na: dict[str, Any] = {
        "oneOf": [
            {"type": "number", "minimum": 0},
            {"const": "N/A"},
        ]
    }

    properties: dict[str, Any] = {
        "schema_version": {"const": "mstr.material-result-identity.v0"},
        "result_id": {"type": "string", "minLength": 1, "maxLength": 256},
    }
    for field in (
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
        "acceleration_backend_or_na",
        "cache_state_or_na",
        "interaction_contract_version_or_na",
        "loop_contract_version_or_na",
        "harness_profile_id_or_na",
        "verifier_health_id_or_na",
        "sampling_config_id_or_na",
        "invalidation_reason_or_na",
    ):
        properties[field] = clone(string_or_na)
    for field in (
        "total_ram_bytes_or_na",
        "thread_count_or_na",
        "context_length_or_na",
        "seed_or_na",
    ):
        properties[field] = clone(integer_or_na)
    properties["wall_time_seconds_or_na"] = clone(number_or_na)
    for field in ("task_manifest_id", "verifier_manifest_id"):
        properties[field] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 512,
            "not": {"const": "N/A"},
        }
    properties["result_classification"] = {
        "enum": ["PASS", "FAIL", "INVALID", "CRASHED", "DISCARDED", "PROMOTED"]
    }
    properties["metrics"] = {
        "type": "object",
        "minProperties": 1,
        "maxProperties": 128,
        "additionalProperties": {"type": ["number", "string", "boolean", "null"]},
    }
    properties["resource_cost"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "cost_class": {
                "enum": [
                    "NO_EXTERNAL_EFFECT",
                    "LOCAL_COMPUTE",
                    "AUTHORIZED_REMOTE_COMPUTE",
                ]
            },
            "cpu_seconds_or_na": clone(number_or_na),
            "accelerator_seconds_or_na": clone(number_or_na),
            "network_bytes_or_na": clone(integer_or_na),
            "peak_ram_bytes_or_na": clone(integer_or_na),
        },
        "required": [
            "cost_class",
            "cpu_seconds_or_na",
            "accelerator_seconds_or_na",
            "network_bytes_or_na",
            "peak_ram_bytes_or_na",
        ],
    }
    properties["paid_cost_usd"] = {"type": "number", "minimum": 0}

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mstr.local/schemas/mstr-material-result-identity-v0.json",
        "title": "MSTR Material Result Identity v0",
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": list(properties),
        "allOf": [
            {
                "if": {
                    "properties": {"result_classification": {"const": "INVALID"}},
                    "required": ["result_classification"],
                },
                "then": {
                    "properties": {
                        "invalidation_reason_or_na": {"not": {"const": "N/A"}}
                    }
                },
            },
            {
                "if": {
                    "properties": {
                        "result_classification": {"enum": ["PASS", "PROMOTED"]}
                    },
                    "required": ["result_classification"],
                },
                "then": {
                    "properties": {"invalidation_reason_or_na": {"const": "N/A"}}
                },
            },
        ],
    }


def build_research_experiment_schema(material_schema: dict[str, Any]) -> dict[str, Any]:
    hard_gate_result: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "gate_id": {"type": "string", "minLength": 1, "maxLength": 256},
            "status": {"enum": ["PASS", "FAIL", "NOT_APPLICABLE"]},
            "evidence_identity": {
                "type": "string",
                "minLength": 1,
                "maxLength": 1024,
            },
            "reason": {"type": "string", "minLength": 1, "maxLength": 2048},
        },
        "required": ["gate_id", "status", "evidence_identity", "reason"],
    }
    budget: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "budget_id": {"type": "string", "minLength": 1, "maxLength": 256},
            "max_wall_time_seconds": {"type": "number", "exclusiveMinimum": 0},
            "max_material_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10000,
            },
            "max_paid_cost_usd": {"type": "number", "minimum": 0},
            "resource_class": {
                "enum": [
                    "CONTRACT_ONLY",
                    "LOCAL_BOUNDED",
                    "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY",
                ]
            },
        },
        "required": [
            "budget_id",
            "max_wall_time_seconds",
            "max_material_results",
            "max_paid_cost_usd",
            "resource_class",
        ],
    }
    aggregate_resource_cost: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "wall_time_seconds": {"type": "number", "minimum": 0},
            "material_result_count": {"type": "integer", "minimum": 1},
            "paid_cost_usd": {"type": "number", "minimum": 0},
            "resource_class": {
                "enum": [
                    "CONTRACT_ONLY",
                    "LOCAL_BOUNDED",
                    "AUTHORIZED_EXTERNAL_EFFECT",
                ]
            },
        },
        "required": [
            "wall_time_seconds",
            "material_result_count",
            "paid_cost_usd",
            "resource_class",
        ],
    }
    material_definition = {
        "type": "object",
        "additionalProperties": False,
        "properties": clone(material_schema["properties"]),
        "required": clone(material_schema["required"]),
        "allOf": clone(material_schema["allOf"]),
    }
    properties: dict[str, Any] = {
        "schema_version": {"const": "mstr.research-experiment.v2"},
        "experiment_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "campaign_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "parent_identity": {"type": "string", "minLength": 1, "maxLength": 1024},
        "hypothesis": {"type": "string", "minLength": 1, "maxLength": 4096},
        "mutable_surface": {"type": "string", "minLength": 1, "maxLength": 2048},
        "mutation_identity": {"type": "string", "minLength": 1, "maxLength": 1024},
        "frozen_evaluation_identity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024,
        },
        "fidelity_level": {
            "enum": [
                "L0_CONTRACT_SMOKE",
                "L1_CODE_PROXY",
                "L2_EXECUTABLE_REPO",
                "L3_DIRECTION_TO_DONE",
                "L4_Q4_UNIVERSAL_LAPTOP",
            ]
        },
        "budget": {"$ref": "#/$defs/budget"},
        "material_results": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10000,
            "items": {"$ref": "#/$defs/material_result_identity"},
        },
        "hard_gate_results": {
            "type": "array",
            "minItems": 1,
            "maxItems": 256,
            "items": {"$ref": "#/$defs/hard_gate_result"},
        },
        "promotion_decision": {"enum": ["PROMOTE", "REJECT", "STOP", "INVALID"]},
        "decision_reason": {"type": "string", "minLength": 1, "maxLength": 4096},
        "aggregate_resource_cost": {"$ref": "#/$defs/aggregate_resource_cost"},
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://mstr.local/schemas/mstr-research-experiment-v2.json",
        "title": "MSTR Research Experiment v2",
        "type": "object",
        "additionalProperties": False,
        "$defs": {
            "material_result_identity": material_definition,
            "hard_gate_result": hard_gate_result,
            "budget": budget,
            "aggregate_resource_cost": aggregate_resource_cost,
        },
        "properties": properties,
        "required": list(properties),
        "allOf": [
            {
                "if": {
                    "properties": {"promotion_decision": {"const": "PROMOTE"}},
                    "required": ["promotion_decision"],
                },
                "then": {
                    "properties": {
                        "hard_gate_results": {
                            "items": {
                                "allOf": [
                                    {"$ref": "#/$defs/hard_gate_result"},
                                    {"properties": {"status": {"const": "PASS"}}},
                                ]
                            }
                        }
                    }
                },
            },
            {
                "if": {
                    "properties": {"promotion_decision": {"const": "INVALID"}},
                    "required": ["promotion_decision"],
                },
                "then": {
                    "properties": {
                        "material_results": {
                            "contains": {
                                "properties": {
                                    "result_classification": {"const": "INVALID"}
                                },
                                "required": ["result_classification"],
                            },
                            "minContains": 1,
                        }
                    }
                },
            },
        ],
    }


def build_valid_material_result() -> dict[str, Any]:
    return {
        "schema_version": "mstr.material-result-identity.v0",
        "result_id": "b026-l0-contract-smoke-001",
        "model_id_or_na": "N/A",
        "model_revision_or_na": "N/A",
        "model_artifact_sha256_or_na": "N/A",
        "tokenizer_id_or_na": "N/A",
        "tokenizer_revision_or_na": "N/A",
        "quantization_method_or_na": "N/A",
        "quantizer_tool_revision_or_na": "N/A",
        "runtime_id_or_na": "python",
        "runtime_version_or_commit_or_na": "3.11",
        "runtime_build_flags_or_na": "N/A",
        "os_identity_or_na": "ubuntu-24.04",
        "cpu_identity_or_na": "N/A",
        "total_ram_bytes_or_na": "N/A",
        "thread_count_or_na": "N/A",
        "acceleration_backend_or_na": "N/A",
        "context_length_or_na": "N/A",
        "cache_state_or_na": "N/A",
        "interaction_contract_version_or_na": "N/A",
        "loop_contract_version_or_na": "N/A",
        "harness_profile_id_or_na": "N/A",
        "task_manifest_id": "B026-contract-smoke",
        "verifier_manifest_id": "mstr-local-json-schema-validator",
        "verifier_health_id_or_na": "N/A",
        "sampling_config_id_or_na": "N/A",
        "seed_or_na": "N/A",
        "result_classification": "PASS",
        "metrics": {"schema_checks": 2, "failed_checks": 0},
        "wall_time_seconds_or_na": 0.01,
        "resource_cost": {
            "cost_class": "NO_EXTERNAL_EFFECT",
            "cpu_seconds_or_na": 0.01,
            "accelerator_seconds_or_na": "N/A",
            "network_bytes_or_na": 0,
            "peak_ram_bytes_or_na": "N/A",
        },
        "paid_cost_usd": 0,
        "invalidation_reason_or_na": "N/A",
    }


def build_ladder_config() -> dict[str, Any]:
    levels = [
        {
            "level": "L0_CONTRACT_SMOKE",
            "ordinal": 0,
            "cost_class": "CHEAP",
            "scope": [
                "contract-validation",
                "schema-validation",
                "unit-smoke",
                "configuration-smoke",
            ],
            "promotion_requires": [
                "all required contracts/configs validate",
                "all L0 smoke checks pass",
                "frozen evaluation identity is pinned",
                "every material result has complete MaterialResultIdentity or explicit N/A fields",
                "no hard gate is failed",
            ],
            "hard_reject_conditions": [
                "schema or config invalid",
                "missing or opaque material-result identity",
                "evaluation identity missing or mutable",
                "protected evaluator or authority boundary violation",
                "declared budget exceeded",
            ],
        },
        {
            "level": "L1_CODE_PROXY",
            "ordinal": 1,
            "cost_class": "LOW",
            "scope": ["direct-code", "fim", "edit", "tool-schema"],
            "promotion_requires": [
                "L0 is PROMOTE for the same experiment lineage",
                "predeclared code/FIM/edit/tool proxy thresholds pass",
                "no frozen-evaluation regression exceeds its declared tolerance",
                "every material result binds exact task/verifier/sampling/runtime identity or explicit N/A",
                "no hard gate is failed",
            ],
            "hard_reject_conditions": [
                "L0 not promoted",
                "task or verifier identity mismatch",
                "frozen-evaluation regression beyond declared tolerance",
                "missing material-result identity",
                "declared budget exceeded",
            ],
        },
        {
            "level": "L2_EXECUTABLE_REPO",
            "ordinal": 2,
            "cost_class": "MODERATE",
            "scope": ["executable-small-repository", "build", "tests", "bounded-repair"],
            "promotion_requires": [
                "L1 is PROMOTE for the same experiment lineage",
                "predeclared executable-repository acceptance passes",
                "applicable verifier-health threshold is satisfied",
                "no shortcut, leakage, or protected-path violation is detected",
                "every material result preserves exact environment/runtime/task/verifier identity",
                "no hard gate is failed",
            ],
            "hard_reject_conditions": [
                "L1 not promoted",
                "repository cannot execute under the frozen environment",
                "verifier is broken, leaked, tampered, or below the declared threshold",
                "shortcut or protected-path violation",
                "missing material-result identity",
                "declared budget exceeded",
            ],
        },
        {
            "level": "L3_DIRECTION_TO_DONE",
            "ordinal": 3,
            "cost_class": "HIGH",
            "scope": ["direction-to-done", "feature", "bounded-program", "recovery"],
            "promotion_requires": [
                "L2 is PROMOTE for the same experiment lineage",
                "predeclared Direction-to-Done or feature/program acceptance passes",
                "hidden acceptance and evaluator authority remain immutable",
                "no unresolved product hard-gate regression exists",
                "every material result preserves exact contract/harness/task/verifier identity",
                "no hard gate is failed",
            ],
            "hard_reject_conditions": [
                "L2 not promoted",
                "hidden-evaluation leakage",
                "evaluator authority or protected acceptance mutated",
                "product hard gate regresses",
                "missing material-result identity",
                "declared budget exceeded",
            ],
        },
        {
            "level": "L4_Q4_UNIVERSAL_LAPTOP",
            "ordinal": 4,
            "cost_class": "MOST_EXPENSIVE",
            "scope": ["release-relevant-q4", "universal-laptop", "product-regression"],
            "promotion_requires": [
                "L3 is PROMOTE for the same experiment lineage",
                "release-relevant Q4 artifact identity is exact",
                "quantizer/runtime/hardware identities are exact or explicit N/A only when genuinely inapplicable",
                "required universal-laptop product gates pass",
                "a required Q4PromotionRecord is PROMOTED before any material weight-changing checkpoint may parent another material stage",
                "no hard gate is failed",
            ],
            "hard_reject_conditions": [
                "L3 not promoted",
                "Q4 artifact or quantizer identity missing",
                "required universal-laptop product gate fails",
                "8GB/CPU/8K/Q4<=3GB product floor is silently weakened",
                "required Q4PromotionRecord absent or not PROMOTED",
                "missing material-result identity",
                "declared budget exceeded",
            ],
        },
    ]
    return {
        "config_version": "mstr.research-ladder.v0",
        "task_id": "B026",
        "material_result_identity_schema": "mstr.material-result-identity.v0",
        "research_experiment_schema": "mstr.research-experiment.v2",
        "promotion_policy": {
            "sequential_only": True,
            "promotion_criteria_predeclared": True,
            "hard_reject_is_terminal_for_current_experiment": True,
            "weak_experiments_must_not_run_expensive_levels": True,
            "missing_material_identity_invalidates_promotion": True,
            "frozen_evaluation_identity_required": True,
            "task_eligibility_never_grants_external_effect_authority": True,
        },
        "levels": levels,
        "promotion_edges": [
            {"from": "L0_CONTRACT_SMOKE", "to": "L1_CODE_PROXY"},
            {"from": "L1_CODE_PROXY", "to": "L2_EXECUTABLE_REPO"},
            {"from": "L2_EXECUTABLE_REPO", "to": "L3_DIRECTION_TO_DONE"},
            {"from": "L3_DIRECTION_TO_DONE", "to": "L4_Q4_UNIVERSAL_LAPTOP"},
        ],
        "authority_boundary": {
            "contract_freeze_only": True,
            "research_campaign_execution_authorized": False,
            "model_execution_authorized": False,
            "model_weight_access_authorized": False,
            "paid_compute_authorized": False,
            "network_model_calls_authorized": False,
            "large_dataset_ingestion_authorized": False,
            "private_or_production_data_ingestion_authorized": False,
            "weight_changing_training_authorized": False,
            "large_scale_rl_authorized": False,
            "production_release_authorized": False,
        },
    }


def update_registry() -> None:
    marker = (
        "    # MSTR-000B B028: training-method preflight and fail-closed Q4 promotion.\n"
    )
    insertion = (
        "    # MSTR-000B B026: exact material-result identity and multi-fidelity research record.\n"
        "    \"mstr-material-result-identity-v0\": \"mstr-material-result-identity-v0.schema.json\",\n"
        "    \"mstr-research-experiment-v2\": \"mstr-research-experiment-v2.schema.json\",\n"
        + marker
    )
    replace_once("src/mstr_qualify/schemas.py", marker, insertion)


def update_schema_tests() -> None:
    marker = "    \"mstr-training-method-cell-v0\": (\n"
    insertion = (
        "    \"mstr-material-result-identity-v0\": (\n"
        "        ROOT\n"
        "        / \"specs\"\n"
        "        / \"002-code-model-supremacy-foundation\"\n"
        "        / \"contracts\"\n"
        "        / \"mstr-material-result-identity-v0.schema.json\"\n"
        "    ),\n"
        "    \"mstr-research-experiment-v2\": (\n"
        "        ROOT\n"
        "        / \"specs\"\n"
        "        / \"002-code-model-supremacy-foundation\"\n"
        "        / \"contracts\"\n"
        "        / \"mstr-research-experiment-v2.schema.json\"\n"
        "    ),\n"
        + marker
    )
    replace_once("tests/contract/test_schemas.py", marker, insertion)


def update_contract_readme() -> None:
    marker = "\n## Frozen by B028\n"
    section = """

## Frozen by B026

```text
mstr.material-result-identity.v0
mstr.research-experiment.v2
```

B026 freezes exact material-result identity and a single-fidelity research-experiment record for the L0 -> L4 research ladder. Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise. A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, predeclared budget, and only passing hard gates. B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority.
"""
    replace_once(
        "specs/002-code-model-supremacy-foundation/contracts/README.md",
        marker,
        section + marker,
    )
    for line in (
        "mstr.material-result-identity.v0\n",
        "mstr.research-experiment.v2\n",
    ):
        replace_once(
            "specs/002-code-model-supremacy-foundation/contracts/README.md",
            line,
            "",
        )


def write_contract_test() -> None:
    content = '''from __future__ import annotations

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
'''
    write_text("tests/contract/test_research_ladder_contract.py", content)


def write_evidence() -> None:
    content = f'''# B026 — Multi-Fidelity Research Ladder v0 Evidence

**Task:** `B026`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `{BASE_MAIN}`
**Entry proof:** post-B024-closeout run `{POST_CLOSEOUT_RUN}` — SUCCESS

## Entry gate

```text
TASK = B026
CANONICAL_MAIN = {BASE_MAIN}
TASK_DRIFT = clean
B022_STATE = COMPLETE_CANONICAL
B024_STATE = COMPLETE_CANONICAL
B025_STATE = COMPLETE_CANONICAL
B026_STATE = PENDING
B026_ELIGIBLE = true
EXTERNAL_AUTHORITY_REQUIRED = false
B027 = blocked on B026
B011 = blocked on repository-specific external authority
```

## Frozen contract/config candidate

```text
MATERIAL_RESULT_SCHEMA = mstr.material-result-identity.v0
RESEARCH_EXPERIMENT_SCHEMA = mstr.research-experiment.v2
LADDER_CONFIG = configs/research/mstr-research-ladder-v0.json
FIDELITY = L0_CONTRACT_SMOKE -> L1_CODE_PROXY -> L2_EXECUTABLE_REPO -> L3_DIRECTION_TO_DONE -> L4_Q4_UNIVERSAL_LAPTOP
PROMOTION_CRITERIA_PREDECLARED = true
SEQUENTIAL_PROMOTION_ONLY = true
EARLY_HARD_REJECT = required
OPAQUE_MATERIAL_RESULT = invalid
MISSING_REQUIRED_IDENTITY = invalid
FROZEN_EVALUATION_IDENTITY = required
```

Every material result carries the full `MaterialResultIdentity` surface from the canonical data model. Fields that genuinely do not apply remain present with explicit `N/A`; required task/verifier identities cannot be `N/A`. `mstr.research-experiment.v2` binds one frozen evaluation identity and one fidelity level, records predeclared budget and hard-gate results, and rejects `PROMOTE` when any represented hard gate is not `PASS`.

The ladder config declares promotion and hard-reject conditions for every L0-L4 level and permits only sequential promotion. Weak experiments must be discarded before expensive levels. L4 preserves release-relevant Q4 identity, universal-laptop gates, and the B028 `Q4PromotionRecord` dependency for material weight-changing parentage.

## Authority boundary

This B026 work freezes contracts and configuration only. It does not execute B027 or any research campaign and grants no new execution or training authority.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
RESEARCH_CAMPAIGN_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

B027 remains a separate canonical task. Any external effect required by a later campaign must pass its own exact-main eligibility and already-canonical authority gates; B026 task eligibility never creates or widens such authority.
'''
    write_text("evidence/mstr-000b/B026-research-ladder.md", content)


def main() -> None:
    material_schema = build_material_result_schema()
    experiment_schema = build_research_experiment_schema(material_schema)
    for path in (
        "schemas/mstr-material-result-identity-v0.schema.json",
        "specs/002-code-model-supremacy-foundation/contracts/mstr-material-result-identity-v0.schema.json",
    ):
        write_json(path, material_schema)
    for path in (
        "schemas/mstr-research-experiment-v2.schema.json",
        "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json",
    ):
        write_json(path, experiment_schema)

    valid_material = build_valid_material_result()
    invalid_material = clone(valid_material)
    invalid_material["result_classification"] = "INVALID"
    write_json(
        "tests/fixtures/schemas/valid/mstr-material-result-identity-v0.json",
        valid_material,
    )
    write_json(
        "tests/fixtures/schemas/invalid/mstr-material-result-identity-v0.json",
        invalid_material,
    )

    valid_experiment = {
        "schema_version": "mstr.research-experiment.v2",
        "experiment_id": "b026-fixture-experiment",
        "campaign_id": "b026-fixture-campaign",
        "parent_identity": "fixture-parent:N/A",
        "hypothesis": "Contract-only L0 smoke preserves exact identity and gates.",
        "mutable_surface": "schema-and-config-only",
        "mutation_identity": "fixture-mutation:none",
        "frozen_evaluation_identity": "fixture-evaluator:mstr-local-json-schema-validator",
        "fidelity_level": "L0_CONTRACT_SMOKE",
        "budget": {
            "budget_id": "b026-contract-only",
            "max_wall_time_seconds": 60,
            "max_material_results": 4,
            "max_paid_cost_usd": 0,
            "resource_class": "CONTRACT_ONLY",
        },
        "material_results": [valid_material],
        "hard_gate_results": [
            {
                "gate_id": "identity-complete",
                "status": "PASS",
                "evidence_identity": "fixture:identity-complete",
                "reason": "All required identities are present or explicit N/A.",
            }
        ],
        "promotion_decision": "PROMOTE",
        "decision_reason": "All L0 contract-only hard gates pass.",
        "aggregate_resource_cost": {
            "wall_time_seconds": 0.01,
            "material_result_count": 1,
            "paid_cost_usd": 0,
            "resource_class": "CONTRACT_ONLY",
        },
    }
    invalid_experiment = clone(valid_experiment)
    invalid_experiment["hard_gate_results"][0]["status"] = "FAIL"
    write_json(
        "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json",
        valid_experiment,
    )
    write_json(
        "tests/fixtures/schemas/invalid/mstr-research-experiment-v2.json",
        invalid_experiment,
    )

    write_json("configs/research/mstr-research-ladder-v0.json", build_ladder_config())
    update_registry()
    update_schema_tests()
    update_contract_readme()
    write_contract_test()
    write_evidence()


if __name__ == "__main__":
    main()
