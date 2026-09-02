from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path.cwd()
MATERIAL = ROOT / "schemas/mstr-material-result-identity-v0.schema.json"
RESEARCH = ROOT / "schemas/mstr-research-experiment-v2.schema.json"
SPEC_MATERIAL = ROOT / "specs/002-code-model-supremacy-foundation/contracts/mstr-material-result-identity-v0.schema.json"
SPEC_RESEARCH = ROOT / "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json"
CONFIG = ROOT / "configs/research/mstr-research-ladder-v0.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
DATA_MODEL = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
README = ROOT / "specs/002-code-model-supremacy-foundation/contracts/README.md"
SCHEMAS_PY = ROOT / "src/mstr_qualify/schemas.py"
TESTS = ROOT / "tests/contract/test_research_ladder_contract.py"
VALID_MATERIAL = ROOT / "tests/fixtures/schemas/valid/mstr-material-result-identity-v0.json"
INVALID_MATERIAL = ROOT / "tests/fixtures/schemas/invalid/mstr-material-result-identity-v0.json"
VALID_RESEARCH = ROOT / "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json"
INVALID_RESEARCH = ROOT / "tests/fixtures/schemas/invalid/mstr-research-experiment-v2.json"

LEVEL_GATE_IDS: dict[str, list[str]] = {
    "L0_CONTRACT_SMOKE": [
        "contracts_config_valid",
        "l0_smoke_checks",
        "frozen_evaluation_pinned",
        "material_identity_complete",
        "authority_boundary_intact",
    ],
    "L1_CODE_PROXY": [
        "predecessor_promoted",
        "code_proxy_thresholds",
        "frozen_eval_tolerance",
        "material_identity_complete",
        "task_verifier_sampling_runtime_identity",
    ],
    "L2_EXECUTABLE_REPO": [
        "predecessor_promoted",
        "executable_repo_acceptance",
        "verifier_health",
        "shortcut_leakage_protection",
        "environment_runtime_task_verifier_identity",
    ],
    "L3_DIRECTION_TO_DONE": [
        "predecessor_promoted",
        "direction_to_done_acceptance",
        "hidden_acceptance_immutable",
        "product_regression_clear",
        "contract_harness_task_verifier_identity",
    ],
    "L4_Q4_UNIVERSAL_LAPTOP": [
        "predecessor_promoted",
        "q4_artifact_identity",
        "quantizer_runtime_hardware_identity",
        "universal_laptop_product_gates",
        "q4_promotion_record_promoted",
    ],
}

AMBIGUOUS_ENUM = [
    "N/A", "?", "HEAD", "Head", "LATEST", "Latest", "MAIN", "MASTER", "Main",
    "Master", "NA", "NONE", "NULL", "Na", "None", "Null", "TBD", "Tbd",
    "UNKNOWN", "UNSET", "Unknown", "Unset", "head", "latest", "main", "master",
    "n/a", "na", "none", "null", "tbd", "unknown", "unset",
]


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected object in {path}")
    return value


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement target, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def exact_text_or_na() -> dict[str, object]:
    return {
        "oneOf": [
            {"const": "N/A"},
            {
                "type": "string",
                "minLength": 1,
                "maxLength": 1024,
                "pattern": ".*\\S.*",
                "not": {"enum": AMBIGUOUS_ENUM},
            },
        ]
    }


def canonical_text(max_length: int = 1024) -> dict[str, object]:
    return {
        "type": "string",
        "minLength": 1,
        "maxLength": max_length,
        "pattern": ".*\\S.*",
        "not": {"enum": AMBIGUOUS_ENUM},
    }


def add_material_identity_fields(material: dict[str, object]) -> None:
    props = material["properties"]
    required = material["required"]
    all_of = material["allOf"]
    assert isinstance(props, dict)
    assert isinstance(required, list)
    assert isinstance(all_of, list)
    for field in ("evidence_kind", "data_identity_or_na", "difficulty_identity_or_na"):
        if field in props or field in required:
            raise SystemExit(f"material identity already contains {field}")
    props["evidence_kind"] = {
        "enum": ["CONTRACT_ONLY", "EVALUATION", "TRAINING_EVIDENCE"]
    }
    props["data_identity_or_na"] = exact_text_or_na()
    props["difficulty_identity_or_na"] = exact_text_or_na()
    result_index = required.index("result_id") + 1
    required[result_index:result_index] = [
        "evidence_kind",
        "data_identity_or_na",
        "difficulty_identity_or_na",
    ]
    all_of.append(
        {
            "if": {
                "properties": {"evidence_kind": {"const": "TRAINING_EVIDENCE"}},
                "required": ["evidence_kind"],
            },
            "then": {
                "properties": {
                    "data_identity_or_na": {"not": {"const": "N/A"}},
                    "difficulty_identity_or_na": {"not": {"const": "N/A"}},
                }
            },
        }
    )


def add_authority_contract(research: dict[str, object]) -> None:
    defs = research["$defs"]
    props = research["properties"]
    required = research["required"]
    assert isinstance(defs, dict)
    assert isinstance(props, dict)
    assert isinstance(required, list)
    if "external_effect_authority" in defs or "external_effect_authority" in props:
        raise SystemExit("external effect authority already present")
    defs["external_effect_authority"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "authority_id": canonical_text(256),
            "authority_record_sha256": {"type": "string", "pattern": "^[0-9a-fA-F]{64}$"},
            "canonical_evidence_identity": canonical_text(),
            "authorized_scopes": {
                "type": "array",
                "minItems": 1,
                "maxItems": 8,
                "uniqueItems": True,
                "items": {
                    "enum": ["MODEL_EXECUTION", "PAID_COMPUTE", "REMOTE_COMPUTE", "NETWORK"]
                },
            },
            "max_paid_cost_usd": {"type": "number", "minimum": 0},
            "max_wall_time_seconds": {"type": "number", "exclusiveMinimum": 0},
            "max_material_results": {"type": "integer", "minimum": 1, "maximum": 10000},
            "resource_class": {"const": "AUTHORIZED_EXTERNAL_EFFECT"},
        },
        "required": [
            "authority_id",
            "authority_record_sha256",
            "canonical_evidence_identity",
            "authorized_scopes",
            "max_paid_cost_usd",
            "max_wall_time_seconds",
            "max_material_results",
            "resource_class",
        ],
    }
    props["external_effect_authority"] = {
        "oneOf": [{"type": "null"}, {"$ref": "#/$defs/external_effect_authority"}]
    }
    aggregate_index = required.index("aggregate_resource_cost")
    required.insert(aggregate_index, "external_effect_authority")


def update_config() -> None:
    config = load(CONFIG)
    policy = config["promotion_policy"]
    levels = config["levels"]
    assert isinstance(policy, dict)
    assert isinstance(levels, list)
    policy["required_gate_coverage_semantically_enforced"] = True
    policy["external_effect_authority_binding_required"] = True
    policy["training_evidence_data_difficulty_identity_required"] = True
    for level in levels:
        assert isinstance(level, dict)
        level_id = level["level"]
        assert isinstance(level_id, str)
        level["required_gate_ids"] = LEVEL_GATE_IDS[level_id]
    dump(CONFIG, config)


def update_fixtures() -> None:
    for path in (VALID_MATERIAL, INVALID_MATERIAL):
        fixture = load(path)
        fixture["evidence_kind"] = "CONTRACT_ONLY"
        fixture["data_identity_or_na"] = "N/A"
        fixture["difficulty_identity_or_na"] = "N/A"
        dump(path, fixture)

    for path in (VALID_RESEARCH, INVALID_RESEARCH):
        fixture = load(path)
        fixture["external_effect_authority"] = None
        results = fixture.get("material_results")
        assert isinstance(results, list)
        for result in results:
            assert isinstance(result, dict)
            result["evidence_kind"] = "CONTRACT_ONLY"
            result["data_identity_or_na"] = "N/A"
            result["difficulty_identity_or_na"] = "N/A"
        gate_ids = LEVEL_GATE_IDS["L0_CONTRACT_SMOKE"]
        fixture["hard_gate_results"] = [
            {
                "gate_id": gate_id,
                "status": "FAIL" if path == INVALID_RESEARCH and index == 0 else "PASS",
                "evidence_identity": f"fixture:{gate_id}",
                "reason": "Intentional invalid fixture gate failure."
                if path == INVALID_RESEARCH and index == 0
                else "Required L0 hard gate passed.",
            }
            for index, gate_id in enumerate(gate_ids)
        ]
        dump(path, fixture)


def update_python_semantics() -> None:
    replace_once(
        SCHEMAS_PY,
        ')\n_B026_IDENTITY_OR_NA_FIELDS = (\n',
        ')\n_B026_REQUIRED_GATE_IDS: Mapping[str, tuple[str, ...]] = {\n'
        '    "L0_CONTRACT_SMOKE": (\n'
        '        "contracts_config_valid",\n'
        '        "l0_smoke_checks",\n'
        '        "frozen_evaluation_pinned",\n'
        '        "material_identity_complete",\n'
        '        "authority_boundary_intact",\n'
        '    ),\n'
        '    "L1_CODE_PROXY": (\n'
        '        "predecessor_promoted",\n'
        '        "code_proxy_thresholds",\n'
        '        "frozen_eval_tolerance",\n'
        '        "material_identity_complete",\n'
        '        "task_verifier_sampling_runtime_identity",\n'
        '    ),\n'
        '    "L2_EXECUTABLE_REPO": (\n'
        '        "predecessor_promoted",\n'
        '        "executable_repo_acceptance",\n'
        '        "verifier_health",\n'
        '        "shortcut_leakage_protection",\n'
        '        "environment_runtime_task_verifier_identity",\n'
        '    ),\n'
        '    "L3_DIRECTION_TO_DONE": (\n'
        '        "predecessor_promoted",\n'
        '        "direction_to_done_acceptance",\n'
        '        "hidden_acceptance_immutable",\n'
        '        "product_regression_clear",\n'
        '        "contract_harness_task_verifier_identity",\n'
        '    ),\n'
        '    "L4_Q4_UNIVERSAL_LAPTOP": (\n'
        '        "predecessor_promoted",\n'
        '        "q4_artifact_identity",\n'
        '        "quantizer_runtime_hardware_identity",\n'
        '        "universal_laptop_product_gates",\n'
        '        "q4_promotion_record_promoted",\n'
        '    ),\n'
        '}\n_B026_IDENTITY_OR_NA_FIELDS = (\n',
    )
    replace_once(
        SCHEMAS_PY,
        '    "sampling_config_id_or_na",\n    "invalidation_reason_or_na",\n',
        '    "sampling_config_id_or_na",\n'
        '    "data_identity_or_na",\n'
        '    "difficulty_identity_or_na",\n'
        '    "invalidation_reason_or_na",\n',
    )
    replace_once(
        SCHEMAS_PY,
        '        if len(gate_ids) != len(set(gate_ids)):\n'
        '            errors.append("$.hard_gate_results: gate_id values must be unique")\n',
        '        if len(gate_ids) != len(set(gate_ids)):\n'
        '            errors.append("$.hard_gate_results: gate_id values must be unique")\n'
        '        if instance.get("promotion_decision") == "PROMOTE" and level in _B026_REQUIRED_GATE_IDS:\n'
        '            expected_gate_ids = _B026_REQUIRED_GATE_IDS[level]\n'
        '            if set(gate_ids) != set(expected_gate_ids) or len(gate_ids) != len(expected_gate_ids):\n'
        '                errors.append(\n'
        '                    "$.hard_gate_results: PROMOTE requires exact per-level required gate coverage"\n'
        '                )\n',
    )
    replace_once(
        SCHEMAS_PY,
        '            errors.append(\n'
        '                "$.aggregate_resource_cost.resource_class: "\n'
        '                "LOCAL_BOUNDED budget cannot record authorized external effect"\n'
        '            )\n\n'
        '    return tuple(sorted(errors))\n',
        '            errors.append(\n'
        '                "$.aggregate_resource_cost.resource_class: "\n'
        '                "LOCAL_BOUNDED budget cannot record authorized external effect"\n'
        '            )\n\n'
        '    authority = instance.get("external_effect_authority")\n'
        '    external_effect = False\n'
        '    required_scopes: set[str] = set()\n'
        '    if isinstance(budget, dict) and budget.get("resource_class") == (\n'
        '        "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"\n'
        '    ):\n'
        '        external_effect = True\n'
        '    if isinstance(aggregate, dict):\n'
        '        if aggregate.get("resource_class") == "AUTHORIZED_EXTERNAL_EFFECT":\n'
        '            external_effect = True\n'
        '        aggregate_paid = aggregate.get("paid_cost_usd")\n'
        '        if (\n'
        '            isinstance(aggregate_paid, (int, float))\n'
        '            and not isinstance(aggregate_paid, bool)\n'
        '            and aggregate_paid > 0\n'
        '        ):\n'
        '            external_effect = True\n'
        '            required_scopes.add("PAID_COMPUTE")\n'
        '    if isinstance(material_results, list):\n'
        '        for result in material_results:\n'
        '            if not isinstance(result, dict):\n'
        '                continue\n'
        '            resource_cost = result.get("resource_cost")\n'
        '            if isinstance(resource_cost, dict):\n'
        '                if resource_cost.get("cost_class") == "AUTHORIZED_REMOTE_COMPUTE":\n'
        '                    external_effect = True\n'
        '                    required_scopes.add("REMOTE_COMPUTE")\n'
        '                    if result.get("model_id_or_na") != "N/A":\n'
        '                        required_scopes.add("MODEL_EXECUTION")\n'
        '                network_bytes = resource_cost.get("network_bytes_or_na")\n'
        '                if (\n'
        '                    isinstance(network_bytes, int)\n'
        '                    and not isinstance(network_bytes, bool)\n'
        '                    and network_bytes > 0\n'
        '                ):\n'
        '                    external_effect = True\n'
        '                    required_scopes.add("NETWORK")\n'
        '            result_paid = result.get("paid_cost_usd")\n'
        '            if (\n'
        '                isinstance(result_paid, (int, float))\n'
        '                and not isinstance(result_paid, bool)\n'
        '                and result_paid > 0\n'
        '            ):\n'
        '                external_effect = True\n'
        '                required_scopes.add("PAID_COMPUTE")\n\n'
        '    if external_effect:\n'
        '        if not isinstance(authority, dict):\n'
        '            errors.append(\n'
        '                "$.external_effect_authority: required for any external-effect resource class or cost"\n'
        '            )\n'
        '        else:\n'
        '            for field in ("authority_id", "canonical_evidence_identity"):\n'
        '                if _is_ambiguous_identity(authority.get(field)):\n'
        '                    errors.append(\n'
        '                        f"$.external_effect_authority.{field}: must bind concrete canonical authority"\n'
        '                    )\n'
        '            scopes = authority.get("authorized_scopes")\n'
        '            if isinstance(scopes, list) and not required_scopes.issubset(set(scopes)):\n'
        '                errors.append(\n'
        '                    "$.external_effect_authority.authorized_scopes: missing scope required by recorded effect"\n'
        '                )\n'
        '            if isinstance(budget, dict):\n'
        '                for field, authority_field in (\n'
        '                    ("max_wall_time_seconds", "max_wall_time_seconds"),\n'
        '                    ("max_material_results", "max_material_results"),\n'
        '                    ("max_paid_cost_usd", "max_paid_cost_usd"),\n'
        '                ):\n'
        '                    declared = budget.get(field)\n'
        '                    ceiling = authority.get(authority_field)\n'
        '                    if (\n'
        '                        isinstance(declared, (int, float))\n'
        '                        and not isinstance(declared, bool)\n'
        '                        and isinstance(ceiling, (int, float))\n'
        '                        and not isinstance(ceiling, bool)\n'
        '                        and declared > ceiling\n'
        '                    ):\n'
        '                        errors.append(\n'
        '                            f"$.budget.{field}: exceeds canonical external-effect authority ceiling"\n'
        '                        )\n'
        '            if isinstance(aggregate, dict):\n'
        '                for field, authority_field in (\n'
        '                    ("wall_time_seconds", "max_wall_time_seconds"),\n'
        '                    ("material_result_count", "max_material_results"),\n'
        '                    ("paid_cost_usd", "max_paid_cost_usd"),\n'
        '                ):\n'
        '                    actual = aggregate.get(field)\n'
        '                    ceiling = authority.get(authority_field)\n'
        '                    if (\n'
        '                        isinstance(actual, (int, float))\n'
        '                        and not isinstance(actual, bool)\n'
        '                        and isinstance(ceiling, (int, float))\n'
        '                        and not isinstance(ceiling, bool)\n'
        '                        and actual > ceiling\n'
        '                    ):\n'
        '                        errors.append(\n'
        '                            f"$.aggregate_resource_cost.{field}: exceeds canonical authority ceiling"\n'
        '                        )\n'
        '    elif authority is not None:\n'
        '        errors.append(\n'
        '            "$.external_effect_authority: must be null when no external effect is recorded"\n'
        '        )\n\n'
        '    return tuple(sorted(errors))\n',
    )


def update_tests() -> None:
    replace_once(
        TESTS,
        '        "model_artifact_sha256_or_na",\n        "tokenizer_id_or_na",\n',
        '        "model_artifact_sha256_or_na",\n'
        '        "evidence_kind",\n'
        '        "data_identity_or_na",\n'
        '        "difficulty_identity_or_na",\n'
        '        "tokenizer_id_or_na",\n',
    )
    append = r'''


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


def test_training_evidence_requires_data_and_difficulty_identity() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-material-result-identity-v0.json")
    fixture["evidence_kind"] = "TRAINING_EVIDENCE"
    fixture["data_identity_or_na"] = "N/A"
    fixture["difficulty_identity_or_na"] = "N/A"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-material-result-identity-v0", fixture)

    fixture["data_identity_or_na"] = "data-manifest:fixture-v1"
    fixture["difficulty_identity_or_na"] = "difficulty-calibration:fixture-v1"
    validate_instance("mstr-material-result-identity-v0", fixture)


def test_promotion_requires_exact_per_level_gate_coverage() -> None:
    for index, level in enumerate(LEVELS):
        fixture = _valid_research_experiment()
        fixture["fidelity_level"] = level
        if index == 0:
            fixture["predecessor_promotion"] = None
        else:
            fixture["parent_identity"] = "result:predecessor-promoted"
            fixture["predecessor_promotion"] = _predecessor(LEVELS[index - 1], current=fixture)
        _set_required_gates(fixture, level)
        validate_instance("mstr-research-experiment-v2", fixture)

        gates = fixture["hard_gate_results"]
        assert isinstance(gates, list)
        removed = gates.pop()
        with pytest.raises(ValueError, match="validation failed"):
            validate_instance("mstr-research-experiment-v2", fixture)
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
            validate_instance("mstr-research-experiment-v2", fixture)


def test_external_effect_records_require_canonical_authority_binding_and_ceilings() -> None:
    fixture = _valid_research_experiment()
    budget = fixture["budget"]
    aggregate = fixture["aggregate_resource_cost"]
    results = fixture["material_results"]
    assert isinstance(budget, dict)
    assert isinstance(aggregate, dict)
    assert isinstance(results, list)
    result = results[0]
    assert isinstance(result, dict)
    resource_cost = result["resource_cost"]
    assert isinstance(resource_cost, dict)

    budget["resource_class"] = "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    budget["max_paid_cost_usd"] = 2
    aggregate["resource_class"] = "AUTHORIZED_EXTERNAL_EFFECT"
    aggregate["paid_cost_usd"] = 1
    result["paid_cost_usd"] = 1
    resource_cost["cost_class"] = "AUTHORIZED_REMOTE_COMPUTE"
    resource_cost["network_bytes_or_na"] = 128
    fixture["external_effect_authority"] = {
        "authority_id": "authority:fixture-external-effect",
        "authority_record_sha256": "a" * 64,
        "canonical_evidence_identity": "evidence:fixture-authority",
        "authorized_scopes": ["PAID_COMPUTE", "REMOTE_COMPUTE", "NETWORK"],
        "max_paid_cost_usd": 2,
        "max_wall_time_seconds": 60,
        "max_material_results": 4,
        "resource_class": "AUTHORIZED_EXTERNAL_EFFECT",
    }
    validate_instance("mstr-research-experiment-v2", fixture)

    fixture["external_effect_authority"] = None
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)

    authority = {
        "authority_id": "authority:fixture-external-effect",
        "authority_record_sha256": "a" * 64,
        "canonical_evidence_identity": "evidence:fixture-authority",
        "authorized_scopes": ["REMOTE_COMPUTE", "NETWORK"],
        "max_paid_cost_usd": 0.5,
        "max_wall_time_seconds": 60,
        "max_material_results": 4,
        "resource_class": "AUTHORIZED_EXTERNAL_EFFECT",
    }
    fixture["external_effect_authority"] = authority
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_non_external_record_rejects_self_asserted_authority() -> None:
    fixture = _valid_research_experiment()
    fixture["external_effect_authority"] = {
        "authority_id": "authority:unused",
        "authority_record_sha256": "b" * 64,
        "canonical_evidence_identity": "evidence:unused",
        "authorized_scopes": ["PAID_COMPUTE"],
        "max_paid_cost_usd": 1,
        "max_wall_time_seconds": 60,
        "max_material_results": 4,
        "resource_class": "AUTHORIZED_EXTERNAL_EFFECT",
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
'''
    text = TESTS.read_text(encoding="utf-8")
    if "test_training_evidence_requires_data_and_difficulty_identity" in text:
        raise SystemExit("new Codex review tests already present")
    TESTS.write_text(text.rstrip() + append + "\n", encoding="utf-8")


def update_docs() -> None:
    replace_once(
        DATA_MODEL,
        "- sampling_config_id_or_na\n- seed_or_na\n",
        "- sampling_config_id_or_na\n- data_identity_or_na\n- difficulty_identity_or_na\n- evidence_kind\n- seed_or_na\n",
    )
    replace_once(
        DATA_MODEL,
        "- aggregate_resource_cost\n```\n\nFidelity:\n",
        "- aggregate_resource_cost\n- external_effect_authority\n```\n\nFidelity:\n",
    )
    replace_once(
        DATA_MODEL,
        "Missing or contradictory predecessor/budget evidence fails closed.\n",
        "Missing or contradictory predecessor/budget evidence fails closed. `PROMOTE` also requires exact machine-readable gate coverage for the selected fidelity level. Training evidence requires concrete data and checkpoint-relative difficulty identities. Any external-effect resource class or cost requires an immutable reference to a separately canonical authority record plus scope and ceiling checks; the research record never creates that authority.\n",
    )
    replace_once(
        README,
        "Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise; ambiguous sentinels are invalid and a material artifact hash, when applicable, is an actual SHA-256. A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, predeclared budget, and only passing hard gates. L1-L4 records require explicit immediate-predecessor `PROMOTE` evidence from the same campaign and frozen evaluation identity, and `parent_identity` must bind the predecessor's promoted result. Semantic validation enforces material-result count and declared wall-time/material-count/paid-cost ceilings in addition to JSON Schema shape validation. B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority.\n",
        "Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise; training evidence additionally requires concrete data and checkpoint-relative difficulty identities. Ambiguous sentinels are invalid and a material artifact hash, when applicable, is an actual SHA-256. A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, a predeclared budget, and the exact machine-readable hard-gate set for that fidelity level with every required gate passing. L1-L4 records require explicit immediate-predecessor `PROMOTE` evidence from the same campaign and frozen evaluation identity, and `parent_identity` must bind the predecessor's promoted result. Semantic validation enforces material-result count, declared wall-time/material-count/paid-cost ceilings, exact gate coverage, and external-effect authority references. Any external-effect resource class or cost must bind an immutable separately canonical authority record and remain within its declared scopes and ceilings; validation never creates or widens that authority. B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority.\n",
    )
    evidence = EVIDENCE.read_text(encoding="utf-8")
    marker = "## Codex review reconciliation — exact old head"
    if marker in evidence:
        raise SystemExit("Codex reconciliation already present")
    evidence += f'''\n\n{marker}\n\nCodex review `PRR_kwDOUCYTYs8AAAABL1K_JQ` on historical head `a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` produced six actionable threads. The first repair at `45d9f9f0ded97ebd482c29d419d2ff41bd9e940a` closed predecessor adjacency, declared-budget enforcement, and SHA-256 identity semantics. This repair closes the remaining contract gaps by freezing exact per-level required gate IDs, binding any recorded external effect to an immutable separately canonical authority reference with scope/ceiling checks, and requiring concrete data/difficulty identity for `TRAINING_EVIDENCE`.\n\nThe external-effect authority object is evidence about authority granted elsewhere. It is not an authority grant. B026 remains contract/configuration only.\n'''
    EVIDENCE.write_text(evidence, encoding="utf-8")


def main() -> None:
    material = load(MATERIAL)
    add_material_identity_fields(material)
    dump(MATERIAL, material)
    dump(SPEC_MATERIAL, material)

    research = load(RESEARCH)
    defs = research["$defs"]
    assert isinstance(defs, dict)
    embedded = deepcopy(material)
    for key in ("$schema", "$id", "title"):
        embedded.pop(key, None)
    defs["material_result_identity"] = embedded
    add_authority_contract(research)
    dump(RESEARCH, research)
    dump(SPEC_RESEARCH, research)

    update_config()
    update_fixtures()
    update_python_semantics()
    update_tests()
    update_docs()


if __name__ == "__main__":
    main()
