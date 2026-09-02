from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
RESEARCH = ROOT / "schemas/mstr-research-experiment-v2.schema.json"
SPEC_RESEARCH = ROOT / "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json"
CONFIG = ROOT / "configs/research/mstr-research-ladder-v0.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
DATA_MODEL = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
README = ROOT / "specs/002-code-model-supremacy-foundation/contracts/README.md"
SCHEMAS_PY = ROOT / "src/mstr_qualify/schemas.py"
CLI_PY = ROOT / "src/mstr_qualify/cli.py"
TESTS = ROOT / "tests/contract/test_research_ladder_contract.py"
VALID_RESEARCH = ROOT / "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json"
INVALID_RESEARCH = ROOT / "tests/fixtures/schemas/invalid/mstr-research-experiment-v2.json"

GOVERNED_EFFECTS = [
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
]

LEVELS = [
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
]


def load(path: Path) -> dict[str, object]:
    """Read one JSON object or stop the guarded builder."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object in {path}")
    return value


def dump(path: Path, value: object) -> None:
    """Write deterministic repository JSON."""

    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_text(max_length: int = 1024) -> dict[str, object]:
    """Return the existing exact non-ambiguous text shape."""

    ambiguous = [
        "N/A",
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
    return {
        "type": "string",
        "minLength": 1,
        "maxLength": max_length,
        "pattern": ".*\\S.*",
        "not": {"enum": ambiguous},
    }


def exact_text_or_na(max_length: int = 1024) -> dict[str, object]:
    """Return explicit N/A or exact canonical text."""

    return {"oneOf": [{"const": "N/A"}, canonical_text(max_length)]}


def binding_id_schema() -> dict[str, object]:
    """Return a path-safe stable identifier contract."""

    return {
        "type": "string",
        "minLength": 1,
        "maxLength": 128,
        "pattern": "^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$",
    }


def update_research_schema() -> None:
    """Replace self-attested lineage/authority surfaces with canonical references."""

    research = load(RESEARCH)
    defs = research["$defs"]
    props = research["properties"]
    required = research["required"]
    all_of = research["allOf"]
    if not isinstance(defs, dict) or not isinstance(props, dict):
        raise SystemExit("research schema definitions/properties must be objects")
    if not isinstance(required, list) or not isinstance(all_of, list):
        raise SystemExit("research schema required/allOf must be arrays")

    defs["predecessor_promotion"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "experiment_id": binding_id_schema(),
            "experiment_record_sha256": {
                "type": "string",
                "pattern": "^[0-9a-fA-F]{64}$",
            },
        },
        "required": ["experiment_id", "experiment_record_sha256"],
    }
    defs["external_effect_authority"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "authority_id": binding_id_schema(),
            "authority_record_sha256": {
                "type": "string",
                "pattern": "^[0-9a-fA-F]{64}$",
            },
        },
        "required": ["authority_id", "authority_record_sha256"],
    }
    defs["governed_effects"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {effect: {"type": "boolean"} for effect in GOVERNED_EFFECTS},
        "required": GOVERNED_EFFECTS,
    }

    props["experiment_id"] = binding_id_schema()
    props["governing_task_id"] = {
        "type": "string",
        "pattern": "^[A-Z][0-9]{3}$",
    }
    props["promoted_result_id_or_na"] = exact_text_or_na(256)
    props["q4_promotion_record_identity_or_na"] = exact_text_or_na()
    props["governed_effects"] = {"$ref": "#/$defs/governed_effects"}
    props["predecessor_promotion"] = {
        "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/predecessor_promotion"},
        ]
    }
    props["external_effect_authority"] = {
        "oneOf": [
            {"type": "null"},
            {"$ref": "#/$defs/external_effect_authority"},
        ]
    }

    insert_after = {
        "experiment_id": ["governing_task_id"],
        "fidelity_level": ["promoted_result_id_or_na", "q4_promotion_record_identity_or_na"],
        "decision_reason": ["governed_effects"],
    }
    new_required: list[object] = []
    for item in required:
        new_required.append(item)
        if isinstance(item, str):
            new_required.extend(insert_after.get(item, []))
    for field in (
        "governing_task_id",
        "promoted_result_id_or_na",
        "q4_promotion_record_identity_or_na",
        "governed_effects",
    ):
        if field not in new_required:
            new_required.append(field)
    research["required"] = new_required

    all_of.append(
        {
            "if": {
                "properties": {"promotion_decision": {"const": "PROMOTE"}},
                "required": ["promotion_decision"],
            },
            "then": {
                "properties": {
                    "promoted_result_id_or_na": {"not": {"const": "N/A"}}
                }
            },
            "else": {
                "properties": {"promoted_result_id_or_na": {"const": "N/A"}}
            },
        }
    )
    all_of.append(
        {
            "if": {
                "allOf": [
                    {
                        "properties": {
                            "fidelity_level": {"const": "L4_Q4_UNIVERSAL_LAPTOP"}
                        },
                        "required": ["fidelity_level"],
                    },
                    {
                        "properties": {"promotion_decision": {"const": "PROMOTE"}},
                        "required": ["promotion_decision"],
                    },
                ]
            },
            "then": {
                "properties": {
                    "q4_promotion_record_identity_or_na": {"not": {"const": "N/A"}}
                }
            },
            "else": {
                "properties": {
                    "q4_promotion_record_identity_or_na": {"const": "N/A"}
                }
            },
        }
    )

    dump(RESEARCH, research)
    SPEC_RESEARCH.write_bytes(RESEARCH.read_bytes())


def false_effects() -> dict[str, bool]:
    """Return an explicit all-false governed-effect declaration."""

    return {effect: False for effect in GOVERNED_EFFECTS}


def update_fixtures() -> None:
    """Migrate L0 fixtures to the stronger v2 semantics."""

    for path in (VALID_RESEARCH, INVALID_RESEARCH):
        fixture = load(path)
        fixture["governing_task_id"] = "B026"
        results = fixture.get("material_results")
        if not isinstance(results, list) or not results or not isinstance(results[0], dict):
            raise SystemExit(f"{path}: expected material result fixture")
        result_id = results[0].get("result_id")
        if not isinstance(result_id, str):
            raise SystemExit(f"{path}: expected result_id")
        if fixture.get("promotion_decision") == "PROMOTE":
            fixture["promoted_result_id_or_na"] = result_id
        else:
            fixture["promoted_result_id_or_na"] = "N/A"
        fixture["q4_promotion_record_identity_or_na"] = "N/A"
        fixture["governed_effects"] = false_effects()
        fixture["external_effect_authority"] = None
        dump(path, fixture)


def replace_research_semantics() -> None:
    """Install repository-resolved lineage, authority, cost, and L4 semantics."""

    text = SCHEMAS_PY.read_text(encoding="utf-8")
    start = text.index("def _research_experiment_semantic_errors(")
    end = text.index("def _trajectory_manifest_semantic_errors(", start)

    replacement = r'''_B026_GOVERNED_EFFECTS = (
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
)
_B026_LEVEL_CONCRETE_FIELDS: Mapping[str, tuple[str, ...]] = {
    "L1_CODE_PROXY": (
        "sampling_config_id_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
    ),
    "L2_EXECUTABLE_REPO": (
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "verifier_health_id_or_na",
    ),
    "L3_DIRECTION_TO_DONE": (
        "interaction_contract_version_or_na",
        "loop_contract_version_or_na",
        "harness_profile_id_or_na",
        "verifier_health_id_or_na",
    ),
    "L4_Q4_UNIVERSAL_LAPTOP": (
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
    ),
}


def _b026_binding_id(value: object) -> bool:
    """Return whether *value* can safely address a canonical binding file."""

    return bool(
        isinstance(value, str)
        and 1 <= len(value) <= 128
        and value[0].isalnum()
        and all(character.isalnum() or character in "._-" for character in value)
    )


def _b026_repository_json(
    repository_root: Path,
    relative_path: Path,
) -> tuple[dict[str, Any], str] | None:
    """Load one repository-contained non-symlink JSON record and its SHA-256."""

    root = repository_root.resolve()
    candidate = root / relative_path
    cursor = root
    for part in relative_path.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            return None
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if not resolved.is_file():
        return None
    try:
        raw = resolved.read_bytes()
        decoded = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(decoded, dict):
        return None
    return decoded, hashlib.sha256(raw).hexdigest()


def _b026_authority_limits(record: Mapping[str, Any]) -> dict[str, float]:
    """Derive research ceilings only from the canonical authority artifact."""

    ceiling = record.get("cost_resource_ceiling")
    if not isinstance(ceiling, dict):
        return {}
    limits = ceiling.get("limits")
    if not isinstance(limits, list):
        return {}
    derived: dict[str, float] = {}
    for item in limits:
        if not isinstance(item, dict):
            continue
        resource = item.get("resource")
        unit = item.get("unit")
        maximum = item.get("max")
        if (
            not isinstance(resource, str)
            or not isinstance(unit, str)
            or isinstance(maximum, bool)
            or not isinstance(maximum, (int, float))
            or not math.isfinite(float(maximum))
            or maximum < 0
        ):
            continue
        normalized_resource = resource.strip().casefold()
        normalized_unit = unit.strip().casefold()
        numeric = float(maximum)
        if normalized_resource in {"paid_cost_usd", "paid_cost", "cost"}:
            if normalized_unit == "usd":
                derived["max_paid_cost_usd"] = numeric
        elif normalized_resource in {"wall_time_seconds", "wall_time"}:
            multipliers = {
                "second": 1.0,
                "seconds": 1.0,
                "minute": 60.0,
                "minutes": 60.0,
                "hour": 3600.0,
                "hours": 3600.0,
            }
            multiplier = multipliers.get(normalized_unit)
            if multiplier is not None:
                derived["max_wall_time_seconds"] = numeric * multiplier
        elif normalized_resource in {
            "material_results",
            "material_result_count",
            "result_count",
        }:
            if normalized_unit in {"count", "result", "results"}:
                derived["max_material_results"] = numeric
    return derived


def _b026_true_effects(instance: Mapping[str, Any]) -> set[str]:
    """Return explicitly declared governed external effects."""

    declared = instance.get("governed_effects")
    if not isinstance(declared, dict):
        return set()
    return {
        effect
        for effect in _B026_GOVERNED_EFFECTS
        if declared.get(effect) is True
    }


def _research_experiment_semantic_errors(
    instance: Any,
    *,
    repository_root: Path,
    visited_records: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    """Enforce B026 lineage, material identity, budgets, and canonical authority."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    level = instance.get("fidelity_level")
    governing_task_id = instance.get("governing_task_id")
    predecessor = instance.get("predecessor_promotion")
    promotion_decision = instance.get("promotion_decision")

    material_results = instance.get("material_results")
    result_by_id: dict[str, dict[str, Any]] = {}
    paid_result_total = 0.0
    paid_result_total_valid = True
    if isinstance(material_results, list):
        result_ids: list[str] = []
        for index, result in enumerate(material_results):
            if not isinstance(result, dict):
                continue
            result_id = result.get("result_id")
            if isinstance(result_id, str):
                result_ids.append(result_id)
                result_by_id[result_id] = result
            paid = result.get("paid_cost_usd")
            if isinstance(paid, (int, float)) and not isinstance(paid, bool):
                paid_result_total += float(paid)
            else:
                paid_result_total_valid = False
            for message in _material_result_identity_semantic_errors(result):
                suffix = message[1:] if message.startswith("$") else f".{message}"
                errors.append(f"$.material_results[{index}]{suffix}")
        if len(result_ids) != len(set(result_ids)):
            errors.append("$.material_results: result_id values must be unique")

    promoted_result_id = instance.get("promoted_result_id_or_na")
    promoted_result: dict[str, Any] | None = None
    if promotion_decision == "PROMOTE":
        if not isinstance(promoted_result_id, str) or promoted_result_id == "N/A":
            errors.append("$.promoted_result_id_or_na: PROMOTE requires one concrete result_id")
        else:
            promoted_result = result_by_id.get(promoted_result_id)
            if promoted_result is None:
                errors.append(
                    "$.promoted_result_id_or_na: must resolve to one material_results result_id"
                )
            elif promoted_result.get("result_classification") not in {"PASS", "PROMOTED"}:
                errors.append(
                    "$.promoted_result_id_or_na: promoted material result must be PASS or PROMOTED"
                )
    elif promoted_result_id != "N/A":
        errors.append("$.promoted_result_id_or_na: non-PROMOTE decisions require literal N/A")

    if level == _B026_FIDELITY_LEVELS[0]:
        if predecessor is not None:
            errors.append("$.predecessor_promotion: L0 must not claim a predecessor promotion")
    elif level in _B026_FIDELITY_LEVELS[1:]:
        expected_level = _B026_FIDELITY_LEVELS[_B026_FIDELITY_LEVELS.index(level) - 1]
        if not isinstance(predecessor, dict):
            errors.append(
                "$.predecessor_promotion: L1-L4 require immutable predecessor registry evidence"
            )
        else:
            predecessor_id = predecessor.get("experiment_id")
            predecessor_sha = predecessor.get("experiment_record_sha256")
            if not _b026_binding_id(predecessor_id):
                errors.append(
                    "$.predecessor_promotion.experiment_id: must be a path-safe stable binding id"
                )
            elif not isinstance(governing_task_id, str):
                errors.append("$.governing_task_id: required to resolve predecessor registry")
            else:
                relative = (
                    Path("artifacts")
                    / "results"
                    / "research"
                    / governing_task_id
                    / "registry"
                    / f"{predecessor_id}.json"
                )
                registry_key = relative.as_posix()
                if registry_key in visited_records:
                    errors.append("$.predecessor_promotion: predecessor registry cycle detected")
                else:
                    loaded = _b026_repository_json(repository_root, relative)
                    if loaded is None:
                        errors.append(
                            "$.predecessor_promotion: immutable predecessor registry record missing"
                        )
                    else:
                        predecessor_record, observed_sha = loaded
                        if predecessor_sha != observed_sha:
                            errors.append(
                                "$.predecessor_promotion.experiment_record_sha256: "
                                "does not match immutable predecessor record"
                            )
                        nested_errors = validation_errors(
                            "mstr-research-experiment-v2",
                            predecessor_record,
                            repository_root=repository_root,
                            _research_visited=visited_records | {registry_key},
                        )
                        if nested_errors:
                            errors.append(
                                "$.predecessor_promotion: referenced predecessor record is invalid"
                            )
                        if predecessor_record.get("experiment_id") != predecessor_id:
                            errors.append(
                                "$.predecessor_promotion.experiment_id: registry record identity mismatch"
                            )
                        if predecessor_record.get("governing_task_id") != governing_task_id:
                            errors.append(
                                "$.predecessor_promotion: predecessor governing task must match"
                            )
                        if predecessor_record.get("campaign_id") != instance.get("campaign_id"):
                            errors.append(
                                "$.predecessor_promotion: predecessor campaign_id must match"
                            )
                        if predecessor_record.get("fidelity_level") != expected_level:
                            errors.append(
                                "$.predecessor_promotion: registry record must be immediate predecessor level"
                            )
                        if predecessor_record.get("promotion_decision") != "PROMOTE":
                            errors.append(
                                "$.predecessor_promotion: registry predecessor must have PROMOTE decision"
                            )
                        if predecessor_record.get("frozen_evaluation_identity") != instance.get(
                            "frozen_evaluation_identity"
                        ):
                            errors.append(
                                "$.predecessor_promotion: frozen evaluation identity must match"
                            )
                        predecessor_result = predecessor_record.get("promoted_result_id_or_na")
                        if predecessor_result == "N/A" or predecessor_result != instance.get(
                            "parent_identity"
                        ):
                            errors.append(
                                "$.parent_identity: must equal registry predecessor promoted result"
                            )

    hard_gates = instance.get("hard_gate_results")
    gate_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(hard_gates, list):
        gate_ids = [
            gate.get("gate_id")
            for gate in hard_gates
            if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str)
        ]
        for gate in hard_gates:
            if isinstance(gate, dict) and isinstance(gate.get("gate_id"), str):
                gate_by_id[str(gate["gate_id"])] = gate
        if len(gate_ids) != len(set(gate_ids)):
            errors.append("$.hard_gate_results: gate_id values must be unique")
        if (
            promotion_decision == "PROMOTE"
            and isinstance(level, str)
            and level in _B026_REQUIRED_GATE_IDS
        ):
            expected_gate_ids = _B026_REQUIRED_GATE_IDS[level]
            if set(gate_ids) != set(expected_gate_ids) or len(gate_ids) != len(expected_gate_ids):
                errors.append(
                    "$.hard_gate_results: PROMOTE requires exact per-level required gate coverage"
                )

    if promotion_decision == "PROMOTE" and isinstance(level, str) and promoted_result is not None:
        for field in _B026_LEVEL_CONCRETE_FIELDS.get(level, ()):
            value = promoted_result.get(field)
            if value == "N/A" or value is None:
                errors.append(
                    f"$.material_results[{promoted_result_id}].{field}: "
                    f"{level} promotion requires concrete identity"
                )
        if level == "L4_Q4_UNIVERSAL_LAPTOP":
            for field in (
                "total_ram_bytes_or_na",
                "thread_count_or_na",
                "context_length_or_na",
            ):
                value = promoted_result.get(field)
                if isinstance(value, bool) or not isinstance(value, int):
                    errors.append(
                        f"$.material_results[{promoted_result_id}].{field}: "
                        "L4 promotion requires a concrete integer identity"
                    )
            q4_record = instance.get("q4_promotion_record_identity_or_na")
            if not isinstance(q4_record, str) or q4_record == "N/A":
                errors.append(
                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires concrete Q4 promotion evidence"
                )
            artifact_sha = promoted_result.get("model_artifact_sha256_or_na")
            artifact_gate = gate_by_id.get("q4_artifact_identity")
            if (
                isinstance(artifact_sha, str)
                and artifact_sha != "N/A"
                and isinstance(artifact_gate, dict)
                and artifact_gate.get("evidence_identity") != f"sha256:{artifact_sha.lower()}"
            ):
                errors.append(
                    "$.hard_gate_results[q4_artifact_identity].evidence_identity: "
                    "must bind the promoted Q4 artifact SHA-256"
                )
            promotion_gate = gate_by_id.get("q4_promotion_record_promoted")
            if (
                isinstance(q4_record, str)
                and q4_record != "N/A"
                and isinstance(promotion_gate, dict)
                and promotion_gate.get("evidence_identity") != q4_record
            ):
                errors.append(
                    "$.hard_gate_results[q4_promotion_record_promoted].evidence_identity: "
                    "must bind q4_promotion_record_identity_or_na"
                )
    elif instance.get("q4_promotion_record_identity_or_na") != "N/A":
        errors.append(
            "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"
        )

    budget = instance.get("budget")
    aggregate = instance.get("aggregate_resource_cost")
    if isinstance(material_results, list) and isinstance(budget, dict):
        maximum = budget.get("max_material_results")
        if (
            isinstance(maximum, int)
            and not isinstance(maximum, bool)
            and len(material_results) > maximum
        ):
            errors.append("$.material_results: count exceeds budget.max_material_results")

    if isinstance(material_results, list) and isinstance(aggregate, dict):
        count = aggregate.get("material_result_count")
        if (
            isinstance(count, int)
            and not isinstance(count, bool)
            and count != len(material_results)
        ):
            errors.append(
                "$.aggregate_resource_cost.material_result_count: must equal material_results length"
            )
        aggregate_paid = aggregate.get("paid_cost_usd")
        if (
            paid_result_total_valid
            and isinstance(aggregate_paid, (int, float))
            and not isinstance(aggregate_paid, bool)
            and not math.isclose(
                paid_result_total,
                float(aggregate_paid),
                rel_tol=0.0,
                abs_tol=1e-9,
            )
        ):
            errors.append(
                "$.aggregate_resource_cost.paid_cost_usd: "
                "must equal sum(material_results[*].paid_cost_usd)"
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
                "$.aggregate_resource_cost.resource_class: "
                "CONTRACT_ONLY budget requires CONTRACT_ONLY aggregate"
            )
        if budget_class == "LOCAL_BOUNDED" and aggregate_class == "AUTHORIZED_EXTERNAL_EFFECT":
            errors.append(
                "$.aggregate_resource_cost.resource_class: "
                "LOCAL_BOUNDED budget cannot record authorized external effect"
            )

    declared_effects = _b026_true_effects(instance)
    if isinstance(material_results, list):
        for result in material_results:
            if not isinstance(result, dict):
                continue
            if (
                result.get("evidence_kind") == "TRAINING_EVIDENCE"
                and "WEIGHT_CHANGING_TRAINING" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.WEIGHT_CHANGING_TRAINING: "
                    "TRAINING_EVIDENCE requires explicit true declaration"
                )
            resource_cost = result.get("resource_cost")
            if isinstance(resource_cost, dict) and (
                resource_cost.get("cost_class") == "AUTHORIZED_REMOTE_COMPUTE"
                and "RENTED_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.RENTED_COMPUTE: "
                    "AUTHORIZED_REMOTE_COMPUTE requires explicit true declaration"
                )
            paid = result.get("paid_cost_usd")
            if (
                isinstance(paid, (int, float))
                and not isinstance(paid, bool)
                and paid > 0
                and "PAID_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.PAID_COMPUTE: positive paid cost requires explicit true declaration"
                )

    external_resource_class = bool(
        isinstance(budget, dict)
        and budget.get("resource_class") == "EXTERNAL_EFFECT_REQUIRES_SEPARATE_AUTHORITY"
    ) or bool(
        isinstance(aggregate, dict)
        and aggregate.get("resource_class") == "AUTHORIZED_EXTERNAL_EFFECT"
    )
    if external_resource_class and not declared_effects:
        errors.append(
            "$.governed_effects: external-effect resource class requires at least one true governed effect"
        )

    authority = instance.get("external_effect_authority")
    if declared_effects:
        if not isinstance(authority, dict):
            errors.append(
                "$.external_effect_authority: required when any governed effect is true"
            )
        else:
            authority_id = authority.get("authority_id")
            authority_sha = authority.get("authority_record_sha256")
            if not _b026_binding_id(authority_id):
                errors.append(
                    "$.external_effect_authority.authority_id: must be a path-safe canonical binding id"
                )
            else:
                relative = Path("artifacts") / "authorities" / f"{authority_id}.json"
                loaded = _b026_repository_json(repository_root, relative)
                if loaded is None:
                    errors.append(
                        "$.external_effect_authority: canonical authority record missing or invalid"
                    )
                else:
                    authority_record, observed_sha = loaded
                    if authority_sha != observed_sha:
                        errors.append(
                            "$.external_effect_authority.authority_record_sha256: "
                            "does not match canonical authority record"
                        )
                    if authority_record.get("authority_id") != authority_id:
                        errors.append(
                            "$.external_effect_authority.authority_id: canonical record identity mismatch"
                        )
                    if authority_record.get("status") != "AUTHORIZED_CANONICAL":
                        errors.append(
                            "$.external_effect_authority: canonical authority status must be AUTHORIZED_CANONICAL"
                        )
                    if authority_record.get("task_id") != governing_task_id:
                        errors.append(
                            "$.external_effect_authority: canonical authority task_id must match governing_task_id"
                        )
                    if authority_record.get("external_effect_class") not in declared_effects:
                        errors.append(
                            "$.external_effect_authority: canonical strongest effect must be declared true"
                        )
                    scope = authority_record.get("scope")
                    if not isinstance(scope, dict):
                        errors.append("$.external_effect_authority: canonical authority scope is invalid")
                    else:
                        if scope.get("campaign_id") != instance.get("campaign_id"):
                            errors.append(
                                "$.external_effect_authority: canonical authority campaign scope mismatch"
                            )
                        if scope.get("research_ladder_id") != "mstr-research-ladder-v0":
                            errors.append(
                                "$.external_effect_authority: canonical authority ladder scope mismatch"
                            )
                        research_effects = scope.get("research_effects")
                        if (
                            not isinstance(research_effects, list)
                            or not declared_effects.issubset(set(research_effects))
                        ):
                            errors.append(
                                "$.external_effect_authority: canonical authority scope misses declared effect"
                            )
                    ceilings = _b026_authority_limits(authority_record)
                    required_ceilings = {
                        "max_paid_cost_usd",
                        "max_wall_time_seconds",
                        "max_material_results",
                    }
                    if not required_ceilings.issubset(ceilings):
                        errors.append(
                            "$.external_effect_authority: canonical authority lacks research resource ceilings"
                        )
                    else:
                        if isinstance(budget, dict):
                            for field in sorted(required_ceilings):
                                declared = budget.get(field)
                                if (
                                    isinstance(declared, (int, float))
                                    and not isinstance(declared, bool)
                                    and float(declared) > ceilings[field]
                                ):
                                    errors.append(
                                        f"$.budget.{field}: exceeds resolved canonical authority ceiling"
                                    )
                        if isinstance(aggregate, dict):
                            for field in sorted(required_ceilings):
                                aggregate_field = (
                                    "paid_cost_usd"
                                    if field == "max_paid_cost_usd"
                                    else "wall_time_seconds"
                                    if field == "max_wall_time_seconds"
                                    else "material_result_count"
                                )
                                actual = aggregate.get(aggregate_field)
                                if (
                                    isinstance(actual, (int, float))
                                    and not isinstance(actual, bool)
                                    and float(actual) > ceilings[field]
                                ):
                                    errors.append(
                                        f"$.aggregate_resource_cost.{aggregate_field}: "
                                        "exceeds resolved canonical authority ceiling"
                                    )
    elif authority is not None:
        errors.append(
            "$.external_effect_authority: must be null when all governed effects are false"
        )

    return tuple(sorted(errors))


'''
    SCHEMAS_PY.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def update_validation_context() -> None:
    """Thread repository-local canonical resolution through public validation APIs."""

    text = SCHEMAS_PY.read_text(encoding="utf-8")
    old = '''def validation_errors(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n) -> tuple[str, ...]:\n'''
    new = '''def validation_errors(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n    repository_root: Path | None = None,\n    _research_visited: frozenset[str] | None = None,\n) -> tuple[str, ...]:\n'''
    if text.count(old) != 1:
        raise SystemExit("expected one validation_errors signature")
    text = text.replace(old, new)
    old_call = '''    if name == "mstr-research-experiment-v2":\n        formatted.extend(_research_experiment_semantic_errors(instance))\n'''
    new_call = '''    if name == "mstr-research-experiment-v2":\n        formatted.extend(\n            _research_experiment_semantic_errors(\n                instance,\n                repository_root=(repository_root or _REPOSITORY_ROOT).resolve(),\n                visited_records=_research_visited or frozenset(),\n            )\n        )\n'''
    if text.count(old_call) != 1:
        raise SystemExit("expected one research semantic dispatch")
    text = text.replace(old_call, new_call)

    old = '''def validate_instance(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n) -> None:\n'''
    new = '''def validate_instance(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n    repository_root: Path | None = None,\n) -> None:\n'''
    if text.count(old) != 1:
        raise SystemExit("expected one validate_instance signature")
    text = text.replace(old, new)
    old = '''    errors = validation_errors(name, instance, schema_dir=schema_dir)\n'''
    new = '''    errors = validation_errors(\n        name,\n        instance,\n        schema_dir=schema_dir,\n        repository_root=repository_root,\n    )\n'''
    if text.count(old) != 1:
        raise SystemExit("expected one validate_instance dispatch")
    text = text.replace(old, new)
    SCHEMAS_PY.write_text(text, encoding="utf-8")

    cli = CLI_PY.read_text(encoding="utf-8")
    old_cli = '''            validate_instance(schema_name, data)\n'''
    new_cli = '''            validate_instance(schema_name, data, repository_root=_REPOSITORY_ROOT)\n'''
    if cli.count(old_cli) != 1:
        raise SystemExit("expected one CLI validate_instance dispatch")
    CLI_PY.write_text(cli.replace(old_cli, new_cli), encoding="utf-8")


def update_tests() -> None:
    """Replace self-attested tests with canonical registry and authority proofs."""

    text = TESTS.read_text(encoding="utf-8")
    text = text.replace("import json\n", "import hashlib\nimport json\n", 1)
    marker = "def _valid_research_experiment() -> dict[str, object]:\n"
    start = text.index(marker)
    prefix = text[:start].rstrip() + "\n\n\n"
    section = r'''def _valid_research_experiment() -> dict[str, object]:
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


def _write_promoted_chain(root: Path, through_index: int) -> tuple[list[dict[str, object]], list[str]]:
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
'''
    TESTS.write_text(prefix + section.rstrip() + "\n", encoding="utf-8")


def update_config_and_docs() -> None:
    """Freeze the repaired resolver semantics without widening authority."""

    config = load(CONFIG)
    policy = config.get("promotion_policy")
    if not isinstance(policy, dict):
        raise SystemExit("promotion_policy must be an object")
    policy.update(
        {
            "predecessor_registry_resolution_required": True,
            "canonical_authority_record_resolution_required": True,
            "governed_effect_declarations_complete": True,
            "aggregate_paid_cost_reconciliation_required": True,
            "per_level_material_identity_semantically_enforced": True,
            "l4_concrete_q4_identity_required": True,
            "q4_gate_evidence_identity_binding_required": True,
        }
    )
    config["canonical_resolution"] = {
        "experiment_registry_template": "artifacts/results/research/{governing_task_id}/registry/{experiment_id}.json",
        "authority_registry_template": "artifacts/authorities/{authority_id}.json",
        "record_integrity": "SHA-256 over exact repository file bytes",
        "authority_scope_source": "resolved canonical authority artifact only",
        "authority_copy_in_experiment": False,
        "governed_effects": GOVERNED_EFFECTS,
    }
    dump(CONFIG, config)

    evidence = EVIDENCE.read_text(encoding="utf-8")
    old = (
        "Codex review `PRR_kwDOUCYTYs8AAAABL1K_JQ` on historical head "
        "`a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` produced six actionable threads. "
        "The first repair at `45d9f9f0ded97ebd482c29d419d2ff41bd9e940a` closed predecessor adjacency, "
        "declared-budget enforcement, and SHA-256 identity semantics. This repair closes the remaining "
        "contract gaps by freezing exact per-level required gate IDs, binding any recorded external effect "
        "to an immutable separately canonical authority reference with scope/ceiling checks, and requiring "
        "concrete data/difficulty identity for `TRAINING_EVIDENCE`."
    )
    new = (
        "Codex review `PRR_kwDOUCYTYs8AAAABL1K_JQ` on historical head "
        "`a2414b1bf58a5bce3a69ee965e74d8ac9d0ba7a8` produced six actionable threads. "
        "The first repair at `45d9f9f0ded97ebd482c29d419d2ff41bd9e940a` addressed predecessor adjacency, "
        "declared-budget enforcement, and SHA-256 identity semantics. The later `08399fa64ed82f31feb5b5cff2f92420bde36308` "
        "candidate added exact gate coverage, an authority-reference shape, and training data/difficulty identity, "
        "but fresh exact-head review correctly found that predecessor and authority evidence were still self-attested."
    )
    if evidence.count(old) != 1:
        raise SystemExit("expected one stale evidence claim")
    evidence = evidence.replace(old, new)
    evidence += '''

## Fresh exact-head review findings on `08399fa64ed82f31feb5b5cff2f92420bde36308`

Codex review `PRR_kwDOUCYTYs8AAAABL2PpKg` produced five actionable findings on the exact qualified head:

1. L4 promotion did not require concrete Q4 artifact/quantizer/runtime/hardware identity or bind Q4 gate evidence to those identities.
2. `predecessor_promotion` remained self-attested instead of resolving an immutable predecessor experiment record.
3. `external_effect_authority` remained self-attested instead of resolving the canonical authority artifact and deriving scope/ceilings from it.
4. governed external-effect classes were not exhaustively declared, allowing local/zero-cost training evidence to remain unbound.
5. aggregate paid cost was not reconciled with the sum of per-result paid costs.

CodeRabbit run `2b1e0aeb-8ecf-449f-bb4e-3ca2faa33ac6` independently confirmed the predecessor/authority resolution gaps and also required this evidence record to stop describing unresolved gaps as closed.

This guarded candidate repair addresses those findings by deriving predecessor records from `artifacts/results/research/<governing_task_id>/registry/<experiment_id>.json`, deriving authority only from `artifacts/authorities/<authority_id>.json`, binding both files by SHA-256, requiring an explicit boolean declaration for every canonical governed effect class, reconciling per-result paid cost to the aggregate, and requiring concrete per-level material identity with strict L4 Q4 evidence binding. The experiment record carries no copied authority scopes or ceilings.

These findings are not considered resolved by implementation text. Resolution still requires successful guarded repair gates, fresh exact-head qualification, thread reconciliation, and a new independent exact-head review.
'''
    EVIDENCE.write_text(evidence.rstrip() + "\n", encoding="utf-8")

    data_model_append = '''

### B026 canonical research resolution

`mstr.research-experiment.v2` is fail-closed against self-attested promotion or authority. `governing_task_id` and `predecessor_promotion.experiment_id` derive the predecessor registry path `artifacts/results/research/<governing_task_id>/registry/<experiment_id>.json`; `experiment_record_sha256` binds the exact bytes. The resolved record must itself validate, belong to the same campaign/task/evaluator lineage, be the immediately preceding fidelity level, have decision `PROMOTE`, and expose the exact promoted result consumed as the current parent.

Every experiment explicitly declares every governed external-effect class as `true` or `false`. Any true class requires `external_effect_authority`, whose path is derived only as `artifacts/authorities/<authority_id>.json`. The experiment stores only `authority_id` plus the canonical file SHA-256. Scope, campaign binding, strongest effect, and resource ceilings are derived from the resolved `AUTHORIZED_CANONICAL` artifact and are never copied into a mutable experiment authority surface.

`PROMOTE` binds `promoted_result_id_or_na` to a material result. Per-level identity gates have concrete semantic requirements. L4 additionally requires exact model/Q4 artifact, tokenizer, quantizer, runtime/build, OS/CPU/RAM/thread/backend/context/cache identities and binds both `q4_artifact_identity` and `q4_promotion_record_promoted` gate evidence to the exact promoted artifact/Q4 record. Aggregate paid cost must equal the sum of per-result paid costs before budget or authority ceilings are evaluated.
'''
    DATA_MODEL.write_text(DATA_MODEL.read_text(encoding="utf-8").rstrip() + data_model_append, encoding="utf-8")

    readme_append = '''

B026 research records resolve lineage and authority from repository-local immutable artifacts rather than trusting inline claims. Predecessors are SHA-256-bound experiment-registry records under `artifacts/results/research/<task>/registry/`; external authority is a SHA-256-bound foreign key to `artifacts/authorities/<authority_id>.json`. Governed effects are exhaustively declared, canonical scope/ceilings are derived from the resolved authority artifact, and L4 promotion requires concrete Q4/runtime/hardware identity plus exact Q4 evidence bindings.
'''
    README.write_text(README.read_text(encoding="utf-8").rstrip() + readme_append, encoding="utf-8")


def main() -> None:
    update_research_schema()
    update_fixtures()
    replace_research_semantics()
    update_validation_context()
    update_tests()
    update_config_and_docs()


if __name__ == "__main__":
    main()
