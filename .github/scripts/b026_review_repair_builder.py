from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
REVIEW_COMMENT_ID = "5508683112"

AMBIGUOUS_SENTINELS = [
    "?",
    "HEAD",
    "Head",
    "LATEST",
    "Latest",
    "MAIN",
    "MASTER",
    "Main",
    "Master",
    "NA",
    "NONE",
    "NULL",
    "Na",
    "None",
    "Null",
    "TBD",
    "Tbd",
    "UNKNOWN",
    "UNSET",
    "Unknown",
    "Unset",
    "head",
    "latest",
    "main",
    "master",
    "n/a",
    "na",
    "none",
    "null",
    "tbd",
    "unknown",
    "unset",
]

IDENTITY_OR_NA_FIELDS = (
    "model_id_or_na",
    "model_revision_or_na",
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
)

LEVELS = (
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
)


def load_json(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: str, value: object) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one match in {path}, found {count}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


def append_once(path: str, marker: str, text: str) -> None:
    target = ROOT / path
    current = target.read_text(encoding="utf-8")
    if marker in current:
        raise RuntimeError(f"marker already present in {path}: {marker}")
    target.write_text(current.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


def insert_after(mapping: dict[str, Any], after: str, key: str, value: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    inserted = False
    for current_key, current_value in mapping.items():
        result[current_key] = current_value
        if current_key == after:
            result[key] = value
            inserted = True
    if not inserted:
        raise RuntimeError(f"unable to insert {key!r} after missing key {after!r}")
    return result


def concrete_string_or_na(*, max_length: int = 1024) -> dict[str, Any]:
    return {
        "oneOf": [
            {"const": "N/A"},
            {
                "type": "string",
                "minLength": 1,
                "maxLength": max_length,
                "pattern": ".*\\S.*",
                "not": {"enum": ["N/A", *AMBIGUOUS_SENTINELS]},
            },
        ]
    }


def concrete_required_string(*, max_length: int) -> dict[str, Any]:
    return {
        "type": "string",
        "minLength": 1,
        "maxLength": max_length,
        "pattern": ".*\\S.*",
        "not": {"enum": ["N/A", *AMBIGUOUS_SENTINELS]},
    }


def strengthen_material_schema() -> dict[str, Any]:
    path = "schemas/mstr-material-result-identity-v0.schema.json"
    schema = load_json(path)
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise RuntimeError("material-result schema properties missing")

    for field in IDENTITY_OR_NA_FIELDS:
        if field not in properties:
            raise RuntimeError(f"missing identity field in material schema: {field}")
        properties[field] = concrete_string_or_na()

    properties["model_artifact_sha256_or_na"] = {
        "oneOf": [
            {"const": "N/A"},
            {"type": "string", "pattern": "^[0-9a-fA-F]{64}$"},
        ]
    }
    for field in ("task_manifest_id", "verifier_manifest_id"):
        properties[field] = concrete_required_string(max_length=512)

    write_json(path, schema)
    write_json(
        "specs/002-code-model-supremacy-foundation/contracts/mstr-material-result-identity-v0.schema.json",
        schema,
    )
    return schema


def predecessor_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "experiment_id": concrete_required_string(max_length=256),
            "campaign_id": concrete_required_string(max_length=256),
            "fidelity_level": {"enum": list(LEVELS[:-1])},
            "promotion_decision": {"const": "PROMOTE"},
            "frozen_evaluation_identity": concrete_required_string(max_length=1024),
            "promoted_result_identity": concrete_required_string(max_length=1024),
            "evidence_identity": concrete_required_string(max_length=1024),
        },
        "required": [
            "experiment_id",
            "campaign_id",
            "fidelity_level",
            "promotion_decision",
            "frozen_evaluation_identity",
            "promoted_result_identity",
            "evidence_identity",
        ],
    }


def strengthen_research_schema(material_schema: dict[str, Any]) -> None:
    path = "schemas/mstr-research-experiment-v2.schema.json"
    schema = load_json(path)
    definitions = schema.get("$defs")
    properties = schema.get("properties")
    required = schema.get("required")
    rules = schema.get("allOf")
    if not isinstance(definitions, dict) or not isinstance(properties, dict):
        raise RuntimeError("research schema definitions/properties missing")
    if not isinstance(required, list) or not isinstance(rules, list):
        raise RuntimeError("research schema required/allOf missing")

    definitions["material_result_identity"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": deepcopy(material_schema["properties"]),
        "required": deepcopy(material_schema["required"]),
        "allOf": deepcopy(material_schema["allOf"]),
    }
    definitions["predecessor_promotion"] = predecessor_schema()

    if "predecessor_promotion" in properties:
        raise RuntimeError("predecessor_promotion already exists unexpectedly")
    schema["properties"] = insert_after(
        properties,
        "fidelity_level",
        "predecessor_promotion",
        {
            "oneOf": [
                {"type": "null"},
                {"$ref": "#/$defs/predecessor_promotion"},
            ]
        },
    )
    fidelity_index = required.index("fidelity_level")
    required.insert(fidelity_index + 1, "predecessor_promotion")

    predecessor_rules = [
        {
            "if": {
                "properties": {"fidelity_level": {"const": "L0_CONTRACT_SMOKE"}},
                "required": ["fidelity_level"],
            },
            "then": {"properties": {"predecessor_promotion": {"type": "null"}}},
        },
        {
            "if": {
                "properties": {"fidelity_level": {"enum": list(LEVELS[1:])}},
                "required": ["fidelity_level"],
            },
            "then": {
                "properties": {
                    "predecessor_promotion": {"$ref": "#/$defs/predecessor_promotion"}
                }
            },
        },
    ]
    schema["allOf"] = predecessor_rules + rules

    write_json(path, schema)
    write_json(
        "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json",
        schema,
    )


def update_fixtures() -> None:
    for path in (
        "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json",
        "tests/fixtures/schemas/invalid/mstr-research-experiment-v2.json",
    ):
        record = load_json(path)
        if "predecessor_promotion" in record:
            raise RuntimeError(f"predecessor already present in {path}")
        record = insert_after(record, "fidelity_level", "predecessor_promotion", None)
        write_json(path, record)


def update_config() -> None:
    path = "configs/research/mstr-research-ladder-v0.json"
    config = load_json(path)
    policy = config.get("promotion_policy")
    if not isinstance(policy, dict):
        raise RuntimeError("research ladder promotion_policy missing")
    if "predecessor_promotion_evidence_required" in policy:
        raise RuntimeError("predecessor policy already present")
    policy["predecessor_promotion_evidence_required"] = True
    policy["declared_budgets_semantically_enforced"] = True
    write_json(path, config)


def update_cli_dispatch() -> None:
    old = '''    # MSTR-000B B025 greenfield/feature/synthesis task manifest contract.\n    "mstr.greenfield-task.v0": "mstr-greenfield-task-v0",\n}\n'''
    new = '''    # MSTR-000B B025 greenfield/feature/synthesis task manifest contract.\n    "mstr.greenfield-task.v0": "mstr-greenfield-task-v0",\n    # MSTR-000B B026 exact material-result and research-experiment contracts.\n    "mstr.material-result-identity.v0": "mstr-material-result-identity-v0",\n    "mstr.research-experiment.v2": "mstr-research-experiment-v2",\n}\n'''
    replace_once("src/mstr_qualify/cli.py", old, new)


def update_semantic_validation() -> None:
    semantic_block = r'''

_AMBIGUOUS_IDENTITY_SENTINELS = frozenset(
    {"unknown", "tbd", "unset", "none", "null", "na", "n/a", "?", "latest", "main", "master", "head"}
)
_B026_FIDELITY_LEVELS = (
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
)
_B026_IDENTITY_OR_NA_FIELDS = (
    "model_id_or_na",
    "model_revision_or_na",
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
)


def _is_ambiguous_identity(value: object) -> bool:
    if not isinstance(value, str) or value == "N/A":
        return False
    return value != value.strip() or value.strip().casefold() in _AMBIGUOUS_IDENTITY_SENTINELS


def _material_result_identity_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Reject opaque B026 identity values that cannot support material comparison."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    for field in _B026_IDENTITY_OR_NA_FIELDS:
        value = instance.get(field)
        if _is_ambiguous_identity(value):
            errors.append(f"$.{field}: must be exact identity text or the literal 'N/A'")

    for field in ("task_manifest_id", "verifier_manifest_id"):
        value = instance.get(field)
        if _is_ambiguous_identity(value) or value == "N/A":
            errors.append(f"$.{field}: must be a concrete non-ambiguous identity")

    return tuple(sorted(errors))


def _research_experiment_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B026 predecessor lineage and declared-budget hard gates."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    level = instance.get("fidelity_level")
    predecessor = instance.get("predecessor_promotion")

    if level == _B026_FIDELITY_LEVELS[0]:
        if predecessor is not None:
            errors.append("$.predecessor_promotion: L0 must not claim a predecessor promotion")
    elif level in _B026_FIDELITY_LEVELS[1:]:
        expected_level = _B026_FIDELITY_LEVELS[_B026_FIDELITY_LEVELS.index(level) - 1]
        if not isinstance(predecessor, dict):
            errors.append(
                "$.predecessor_promotion: L1-L4 require immediate-predecessor PROMOTE evidence"
            )
        else:
            if predecessor.get("fidelity_level") != expected_level:
                errors.append(
                    "$.predecessor_promotion.fidelity_level: must be the immediate predecessor level"
                )
            if predecessor.get("promotion_decision") != "PROMOTE":
                errors.append(
                    "$.predecessor_promotion.promotion_decision: predecessor must be PROMOTE"
                )
            if predecessor.get("campaign_id") != instance.get("campaign_id"):
                errors.append(
                    "$.predecessor_promotion.campaign_id: must match current campaign_id"
                )
            if predecessor.get("frozen_evaluation_identity") != instance.get(
                "frozen_evaluation_identity"
            ):
                errors.append(
                    "$.predecessor_promotion.frozen_evaluation_identity: must match current frozen evaluation identity"
                )
            if predecessor.get("experiment_id") == instance.get("experiment_id"):
                errors.append(
                    "$.predecessor_promotion.experiment_id: predecessor must be a distinct experiment"
                )
            if predecessor.get("promoted_result_identity") != instance.get("parent_identity"):
                errors.append(
                    "$.parent_identity: must equal predecessor promoted_result_identity"
                )
            for field in (
                "experiment_id",
                "campaign_id",
                "frozen_evaluation_identity",
                "promoted_result_identity",
                "evidence_identity",
            ):
                if _is_ambiguous_identity(predecessor.get(field)):
                    errors.append(
                        f"$.predecessor_promotion.{field}: must be a concrete non-ambiguous identity"
                    )

    material_results = instance.get("material_results")
    if isinstance(material_results, list):
        result_ids: list[str] = []
        for index, result in enumerate(material_results):
            if isinstance(result, dict):
                result_id = result.get("result_id")
                if isinstance(result_id, str):
                    result_ids.append(result_id)
                for message in _material_result_identity_semantic_errors(result):
                    suffix = message[1:] if message.startswith("$") else f".{message}"
                    errors.append(f"$.material_results[{index}]{suffix}")
        if len(result_ids) != len(set(result_ids)):
            errors.append("$.material_results: result_id values must be unique")

    hard_gates = instance.get("hard_gate_results")
    if isinstance(hard_gates, list):
        gate_ids = [
            gate.get("gate_id")
            for gate in hard_gates
            if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str)
        ]
        if len(gate_ids) != len(set(gate_ids)):
            errors.append("$.hard_gate_results: gate_id values must be unique")

    budget = instance.get("budget")
    aggregate = instance.get("aggregate_resource_cost")
    if isinstance(material_results, list) and isinstance(budget, dict):
        maximum = budget.get("max_material_results")
        if isinstance(maximum, int) and not isinstance(maximum, bool) and len(material_results) > maximum:
            errors.append("$.material_results: count exceeds budget.max_material_results")

    if isinstance(material_results, list) and isinstance(aggregate, dict):
        count = aggregate.get("material_result_count")
        if isinstance(count, int) and not isinstance(count, bool) and count != len(material_results):
            errors.append(
                "$.aggregate_resource_cost.material_result_count: must equal material_results length"
            )

    if isinstance(budget, dict) and isinstance(aggregate, dict):
        wall = aggregate.get("wall_time_seconds")
        max_wall = budget.get("max_wall_time_seconds")
        if (
            isinstance(wall, (int, float))
            and not isinstance(wall, bool)
            and isinstance(max_wall, (int, float))
            and not isinstance(max_wall, bool)
            and wall > max_wall
        ):
            errors.append(
                "$.aggregate_resource_cost.wall_time_seconds: exceeds budget.max_wall_time_seconds"
            )
        paid = aggregate.get("paid_cost_usd")
        max_paid = budget.get("max_paid_cost_usd")
        if (
            isinstance(paid, (int, float))
            and not isinstance(paid, bool)
            and isinstance(max_paid, (int, float))
            and not isinstance(max_paid, bool)
            and paid > max_paid
        ):
            errors.append(
                "$.aggregate_resource_cost.paid_cost_usd: exceeds budget.max_paid_cost_usd"
            )

        budget_class = budget.get("resource_class")
        aggregate_class = aggregate.get("resource_class")
        if budget_class == "CONTRACT_ONLY" and aggregate_class != "CONTRACT_ONLY":
            errors.append(
                "$.aggregate_resource_cost.resource_class: CONTRACT_ONLY budget requires CONTRACT_ONLY aggregate"
            )
        if budget_class == "LOCAL_BOUNDED" and aggregate_class == "AUTHORIZED_EXTERNAL_EFFECT":
            errors.append(
                "$.aggregate_resource_cost.resource_class: LOCAL_BOUNDED budget cannot record authorized external effect"
            )

    return tuple(sorted(errors))
'''
    marker = "\ndef _trajectory_manifest_semantic_errors(instance: Any) -> tuple[str, ...]:\n"
    replace_once("src/mstr_qualify/schemas.py", marker, semantic_block + marker)

    dispatch_old = '''    if name == "mstr-test-generation-example-v0":\n        formatted.extend(_test_generation_semantic_errors(instance))\n    if name == "mstr-trajectory-manifest-v0":\n        formatted.extend(_trajectory_manifest_semantic_errors(instance))\n'''
    dispatch_new = '''    if name == "mstr-test-generation-example-v0":\n        formatted.extend(_test_generation_semantic_errors(instance))\n    if name == "mstr-material-result-identity-v0":\n        formatted.extend(_material_result_identity_semantic_errors(instance))\n    if name == "mstr-research-experiment-v2":\n        formatted.extend(_research_experiment_semantic_errors(instance))\n    if name == "mstr-trajectory-manifest-v0":\n        formatted.extend(_trajectory_manifest_semantic_errors(instance))\n'''
    replace_once("src/mstr_qualify/schemas.py", dispatch_old, dispatch_new)


def update_contract_tests() -> None:
    block = r'''


def _valid_research_experiment() -> dict[str, object]:
    return _json(FIXTURES / "valid" / "mstr-research-experiment-v2.json")


def _predecessor(level: str, *, current: dict[str, object]) -> dict[str, object]:
    return {
        "experiment_id": "b026-predecessor-experiment",
        "campaign_id": current["campaign_id"],
        "fidelity_level": level,
        "promotion_decision": "PROMOTE",
        "frozen_evaluation_identity": current["frozen_evaluation_identity"],
        "promoted_result_identity": "result:predecessor-promoted",
        "evidence_identity": "evidence:predecessor-promotion",
    }


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
    fixture["predecessor_promotion"] = _predecessor("L0_CONTRACT_SMOKE", current=fixture)
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_research_experiment_l1_requires_immediate_same_lineage_predecessor() -> None:
    fixture = _valid_research_experiment()
    fixture["fidelity_level"] = "L1_CODE_PROXY"
    fixture["parent_identity"] = "result:predecessor-promoted"
    fixture["predecessor_promotion"] = None
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)

    predecessor = _predecessor("L0_CONTRACT_SMOKE", current=fixture)
    fixture["predecessor_promotion"] = predecessor
    validate_instance("mstr-research-experiment-v2", fixture)

    predecessor["campaign_id"] = "other-campaign"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


def test_research_experiment_l4_cannot_skip_predecessor_level_or_parent_binding() -> None:
    fixture = _valid_research_experiment()
    fixture["fidelity_level"] = "L4_Q4_UNIVERSAL_LAPTOP"
    fixture["parent_identity"] = "result:predecessor-promoted"
    predecessor = _predecessor("L2_EXECUTABLE_REPO", current=fixture)
    fixture["predecessor_promotion"] = predecessor
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)

    predecessor["fidelity_level"] = "L3_DIRECTION_TO_DONE"
    predecessor["promoted_result_identity"] = "result:different-parent"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)


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

    aggregate["paid_cost_usd"] = 0.01
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
    aggregate["paid_cost_usd"] = 0

    results = fixture["material_results"]
    assert isinstance(results, list)
    second = deepcopy(results[0])
    assert isinstance(second, dict)
    second["result_id"] = "b026-l0-contract-smoke-002"
    results.append(second)
    budget["max_material_results"] = 1
    aggregate["material_result_count"] = 2
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
'''
    append_once(
        "tests/contract/test_research_ladder_contract.py",
        "test_research_experiment_l1_requires_immediate_same_lineage_predecessor",
        block,
    )
    replace_once(
        "tests/contract/test_research_ladder_contract.py",
        "import json\nfrom pathlib import Path\n",
        "import json\nfrom copy import deepcopy\nfrom pathlib import Path\n",
    )


def update_cli_tests() -> None:
    block = r'''


@pytest.mark.parametrize(
    ("fixture_name", "schema_version"),
    [
        ("mstr-material-result-identity-v0.json", "mstr.material-result-identity.v0"),
        ("mstr-research-experiment-v2.json", "mstr.research-experiment.v2"),
    ],
)
def test_validate_explicit_b026_valid_fixtures_pass(
    fixture_name: str,
    schema_version: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "schemas" / "valid" / fixture_name
    assert main(["validate", str(path)]) == 0
    payload = parse_stdout(capsys)
    assert payload["status"] == "pass"
    assert payload["files"][0]["schema_version"] == schema_version


@pytest.mark.parametrize(
    "fixture_name",
    [
        "mstr-material-result-identity-v0.json",
        "mstr-research-experiment-v2.json",
    ],
)
def test_validate_explicit_b026_invalid_fixtures_fail(
    fixture_name: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "schemas" / "invalid" / fixture_name
    assert main(["validate", str(path)]) == 1
    payload = parse_stdout(capsys)
    assert payload["status"] == "fail"
    assert payload["files"][0]["status"] == "fail"
'''
    append_once(
        "tests/integration/test_cli_offline.py",
        "test_validate_explicit_b026_valid_fixtures_pass",
        block,
    )


def update_docs() -> None:
    readme_old = (
        "B026 freezes exact material-result identity and a single-fidelity research-experiment record for the L0 -> L4 research ladder. "
        "Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise. "
        "A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, predeclared budget, and only passing hard gates. "
        "B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority."
    )
    readme_new = (
        "B026 freezes exact material-result identity and a single-fidelity research-experiment record for the L0 -> L4 research ladder. "
        "Every material result carries exact model/artifact/tokenizer/quantizer/runtime/hardware/context/contracts/task/verifier/sampling/classification/cost identity where applicable and explicit `N/A` otherwise; ambiguous sentinels are invalid and a material artifact hash, when applicable, is an actual SHA-256. "
        "A promoted experiment binds one frozen evaluation identity, one fidelity level, complete material results, predeclared budget, and only passing hard gates. L1-L4 records require explicit immediate-predecessor `PROMOTE` evidence from the same campaign and frozen evaluation identity, and `parent_identity` must bind the predecessor's promoted result. "
        "Semantic validation enforces material-result count and declared wall-time/material-count/paid-cost ceilings in addition to JSON Schema shape validation. "
        "B026 also freezes `configs/research/mstr-research-ladder-v0.json`; it grants no campaign, model, weight, paid-compute, data-ingestion, training, RL, or release authority."
    )
    replace_once(
        "specs/002-code-model-supremacy-foundation/contracts/README.md",
        readme_old,
        readme_new,
    )

    model_old = '''ResearchExperimentRecordV2\n- experiment_id\n- campaign_id\n- parent_identity\n- hypothesis\n- mutable_surface\n- mutation_identity\n- frozen_evaluation_identity\n- fidelity_level\n- budget\n'''
    model_new = '''ResearchExperimentRecordV2\n- experiment_id\n- campaign_id\n- parent_identity\n- hypothesis\n- mutable_surface\n- mutation_identity\n- frozen_evaluation_identity\n- fidelity_level\n- predecessor_promotion\n- budget\n'''
    replace_once("specs/002-code-model-supremacy-foundation/data-model.md", model_old, model_new)

    fidelity_old = '''L4_Q4_UNIVERSAL_LAPTOP\n```\n\n## 15. TrainingMethodCell\n'''
    fidelity_new = '''L4_Q4_UNIVERSAL_LAPTOP\n```\n\n`predecessor_promotion` is `null` only at L0. L1-L4 MUST bind an immediate-predecessor `PROMOTE` record from the same campaign and frozen evaluation identity, including the promoted result identity and immutable evidence identity; the current `parent_identity` MUST equal that promoted result identity. Material-result count and aggregate wall-time/paid-cost MUST remain within the predeclared budget. Missing or contradictory predecessor/budget evidence fails closed.\n\n## 15. TrainingMethodCell\n'''
    replace_once("specs/002-code-model-supremacy-foundation/data-model.md", fidelity_old, fidelity_new)

    evidence_block = f'''## Independent review findings and repair\n\nFresh independent CodeRabbit review comment `{REVIEW_COMMENT_ID}` reviewed exact implementation head `a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` and found three High issues:\n\n1. explicit offline CLI validation did not dispatch either B026 schema version;\n2. exact-or-`N/A` identity fields admitted ambiguous sentinel values and the material-artifact SHA field did not require SHA-256 shape;\n3. predecessor promotion and declared-budget hard-reject semantics were prose-only rather than machine-enforced.\n\nThe repair adds explicit CLI dispatch/tests, concrete identity rejection, SHA-256 shape enforcement, an explicit `predecessor_promotion` binding, immediate-predecessor/same-campaign/frozen-evaluation/parent-result semantic validation, material-result count checks, and declared budget ceilings. The task ledger and task-gate canonical state remain unchanged while B026 is implementation-active.\n\nNo review finding is considered resolved merely by this text. Resolution requires a successful guarded repair build, fresh exact-head qualification, and a fresh independent review of the repaired head. The authority boundary below remains unchanged.\n'''
    append_once(
        "evidence/mstr-000b/B026-research-ladder.md",
        "## Independent review findings and repair",
        evidence_block,
    )


def main() -> None:
    material = strengthen_material_schema()
    strengthen_research_schema(material)
    update_fixtures()
    update_config()
    update_cli_dispatch()
    update_semantic_validation()
    update_contract_tests()
    update_cli_tests()
    update_docs()


if __name__ == "__main__":
    main()
