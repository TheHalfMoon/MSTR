from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
CONFIG = ROOT / "configs/research/mstr-research-ladder-v0.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
RESEARCH_SCHEMA = ROOT / "schemas/mstr-research-experiment-v2.schema.json"
SPEC_RESEARCH_SCHEMA = ROOT / "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json"
DATA_MODEL = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
SCHEMAS_PY = ROOT / "src/mstr_qualify/schemas.py"
CONTRACT_TESTS = ROOT / "tests/contract/test_research_ladder_contract.py"
VALID_EXPERIMENT = ROOT / "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json"
CONTRACT_README = ROOT / "specs/002-code-model-supremacy-foundation/contracts/README.md"

LEVELS = [
    "L0_CONTRACT_SMOKE",
    "L1_CODE_PROXY",
    "L2_EXECUTABLE_REPO",
    "L3_DIRECTION_TO_DONE",
    "L4_Q4_UNIVERSAL_LAPTOP",
]


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_content_addressed(directory: Path, value: dict[str, Any]) -> str:
    raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    digest = sha256_bytes(raw)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{digest}.json").write_bytes(raw)
    return f"sha256:{digest}"


def required_gate_ids(level: str) -> list[str]:
    config = load_json(CONFIG)
    levels = config.get("levels")
    if not isinstance(levels, list):
        raise SystemExit("levels missing")
    for item in levels:
        if isinstance(item, dict) and item.get("level") == level:
            ids = item.get("required_gate_ids")
            if isinstance(ids, list) and all(isinstance(v, str) for v in ids):
                return list(ids)
    raise SystemExit(f"required gate ids missing for {level}")


def update_config() -> None:
    config = load_json(CONFIG)
    resolution = config.get("canonical_resolution")
    if not isinstance(resolution, dict):
        raise SystemExit("canonical_resolution missing")
    resolution["promotion_policy_registry_template"] = (
        "artifacts/results/research/{governing_task_id}/promotion-policies/{sha256}.json"
    )
    resolution["gate_evidence_registry_template"] = (
        "artifacts/results/research/{governing_task_id}/gate-evidence/{sha256}.json"
    )
    resolution["q4_promotion_registry_template"] = (
        "artifacts/results/q4-promotion/registry/{sha256}.json"
    )
    resolution["promotion_policy_binding"] = (
        "promotion_policy_identity is sha256:<digest> of a predeclared policy record; "
        "each hard-gate evidence_identity is sha256:<digest> of an immutable observed-value record"
    )
    resolution["promotion_policy_record_contract"] = {
        "schema_version": "mstr.research-promotion-policy.v0",
        "required_fields": [
            "governing_task_id",
            "campaign_id",
            "fidelity_level",
            "frozen_evaluation_identity",
            "criteria",
        ],
        "criterion_fields": ["gate_id", "operator", "expected_value"],
        "operators": ["EQ", "GTE", "LTE", "NOT_APPLICABLE"],
        "criteria_must_exactly_cover_required_gate_ids": True,
    }
    resolution["gate_evidence_record_contract"] = {
        "schema_version": "mstr.research-gate-evidence.v0",
        "required_fields": [
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "observed_value",
        ],
        "status_is_computed_from_predeclared_policy": True,
    }
    dump_json(CONFIG, config)


def update_schema() -> None:
    schema = load_json(RESEARCH_SCHEMA)
    defs = schema.get("$defs")
    props = schema.get("properties")
    required = schema.get("required")
    if not isinstance(defs, dict) or not isinstance(props, dict) or not isinstance(required, list):
        raise SystemExit("research schema shape unexpected")

    hard_gate = defs.get("hard_gate_result")
    if not isinstance(hard_gate, dict):
        raise SystemExit("hard_gate_result missing")
    hard_props = hard_gate.get("properties")
    if not isinstance(hard_props, dict):
        raise SystemExit("hard_gate properties missing")
    evidence = hard_props.get("evidence_identity")
    if not isinstance(evidence, dict):
        raise SystemExit("hard gate evidence_identity missing")
    evidence.clear()
    evidence.update(
        {
            "type": "string",
            "pattern": "^sha256:[0-9a-f]{64}$",
            "description": (
                "Content address of an immutable gate-evidence record. The submitted status is "
                "recomputed from that record under the predeclared promotion policy."
            ),
        }
    )

    props["promotion_policy_identity"] = {
        "type": "string",
        "pattern": "^sha256:[0-9a-f]{64}$",
        "description": "Content address of the immutable predeclared promotion-policy record.",
    }
    q4 = props.get("q4_promotion_record_identity_or_na")
    if not isinstance(q4, dict):
        raise SystemExit("q4 promotion identity missing")
    q4.clear()
    q4.update(
        {
            "oneOf": [
                {"const": "N/A"},
                {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
            ],
            "description": (
                "For L4 PROMOTE, content address of an immutable mstr.q4-promotion.v0 record; "
                "literal N/A everywhere else."
            ),
        }
    )
    if "promotion_policy_identity" not in required:
        insert_at = required.index("fidelity_level") + 1
        required.insert(insert_at, "promotion_policy_identity")
    dump_json(RESEARCH_SCHEMA, schema)
    SPEC_RESEARCH_SCHEMA.write_bytes(RESEARCH_SCHEMA.read_bytes())


def update_semantic_validator() -> None:
    helper_anchor = '''def _research_experiment_semantic_errors(\n    instance: Any,\n'''
    helper_code = r'''def _b026_sha256_identity(value: Any) -> str | None:
    """Return the hex digest from one canonical sha256:<digest> identity."""

    if not isinstance(value, str) or not value.startswith("sha256:"):
        return None
    digest = value.removeprefix("sha256:")
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return None
    return digest


def _b026_compare_gate_value(operator: Any, observed: Any, expected: Any) -> str | None:
    """Compute a gate status from one predeclared policy criterion."""

    if operator == "NOT_APPLICABLE":
        return "NOT_APPLICABLE" if observed is None else "FAIL"
    if operator == "EQ":
        return "PASS" if type(observed) is type(expected) and observed == expected else "FAIL"
    if operator in {"GTE", "LTE"}:
        if (
            isinstance(observed, bool)
            or isinstance(expected, bool)
            or not isinstance(observed, (int, float))
            or not isinstance(expected, (int, float))
            or not math.isfinite(float(observed))
            or not math.isfinite(float(expected))
        ):
            return None
        if operator == "GTE":
            return "PASS" if float(observed) >= float(expected) else "FAIL"
        return "PASS" if float(observed) <= float(expected) else "FAIL"
    return None


def _b026_promotion_policy_errors(
    instance: Mapping[str, Any],
    *,
    repository_root: Path,
) -> tuple[str, ...]:
    """Resolve predeclared policy and immutable gate evidence, then recompute statuses."""

    errors: list[str] = []
    task_id = instance.get("governing_task_id")
    level = instance.get("fidelity_level")
    campaign_id = instance.get("campaign_id")
    experiment_id = instance.get("experiment_id")
    evaluation_id = instance.get("frozen_evaluation_identity")
    policy_identity = instance.get("promotion_policy_identity")
    digest = _b026_sha256_identity(policy_identity)
    if not isinstance(task_id, str) or digest is None:
        return ("$.promotion_policy_identity: must bind a canonical predeclared policy",)

    policy_path = (
        Path("artifacts") / "results" / "research" / task_id / "promotion-policies" / f"{digest}.json"
    )
    loaded = _b026_repository_json(repository_root, policy_path)
    if loaded is None:
        return ("$.promotion_policy_identity: immutable predeclared policy record missing",)
    policy, observed_sha = loaded
    if observed_sha != digest:
        errors.append("$.promotion_policy_identity: policy content address mismatch")

    expected_policy_keys = {
        "schema_version",
        "governing_task_id",
        "campaign_id",
        "fidelity_level",
        "frozen_evaluation_identity",
        "criteria",
    }
    if set(policy) != expected_policy_keys:
        errors.append("$.promotion_policy_identity: policy record fields are not canonical")
    if policy.get("schema_version") != "mstr.research-promotion-policy.v0":
        errors.append("$.promotion_policy_identity: unsupported policy schema_version")
    for field, expected in (
        ("governing_task_id", task_id),
        ("campaign_id", campaign_id),
        ("fidelity_level", level),
        ("frozen_evaluation_identity", evaluation_id),
    ):
        if policy.get(field) != expected:
            errors.append(f"$.promotion_policy_identity: policy {field} must match experiment")

    criteria_raw = policy.get("criteria")
    criteria: dict[str, dict[str, Any]] = {}
    if not isinstance(criteria_raw, list):
        errors.append("$.promotion_policy_identity: policy criteria must be an array")
    else:
        for criterion in criteria_raw:
            if not isinstance(criterion, dict) or set(criterion) != {
                "gate_id",
                "operator",
                "expected_value",
            }:
                errors.append("$.promotion_policy_identity: malformed policy criterion")
                continue
            gate_id = criterion.get("gate_id")
            if not isinstance(gate_id, str) or gate_id in criteria:
                errors.append("$.promotion_policy_identity: duplicate or invalid policy gate_id")
                continue
            if criterion.get("operator") not in {"EQ", "GTE", "LTE", "NOT_APPLICABLE"}:
                errors.append("$.promotion_policy_identity: unsupported policy operator")
                continue
            criteria[gate_id] = criterion

    if isinstance(level, str) and level in _B026_REQUIRED_GATE_IDS:
        required = _B026_REQUIRED_GATE_IDS[level]
        if set(criteria) != set(required) or len(criteria) != len(required):
            errors.append("$.promotion_policy_identity: policy must exactly cover required gate ids")

    gates = instance.get("hard_gate_results")
    if not isinstance(gates, list):
        return tuple(sorted(errors))
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("gate_id")
        criterion = criteria.get(gate_id) if isinstance(gate_id, str) else None
        if criterion is None:
            errors.append(f"$.hard_gate_results[{index}]: no predeclared criterion for gate")
            continue
        evidence_identity = gate.get("evidence_identity")
        evidence_digest = _b026_sha256_identity(evidence_identity)
        if evidence_digest is None:
            errors.append(f"$.hard_gate_results[{index}].evidence_identity: must be sha256 content address")
            continue
        evidence_path = (
            Path("artifacts") / "results" / "research" / task_id / "gate-evidence" / f"{evidence_digest}.json"
        )
        loaded_evidence = _b026_repository_json(repository_root, evidence_path)
        if loaded_evidence is None:
            errors.append(f"$.hard_gate_results[{index}].evidence_identity: canonical evidence missing")
            continue
        evidence_record, evidence_sha = loaded_evidence
        if evidence_sha != evidence_digest:
            errors.append(f"$.hard_gate_results[{index}].evidence_identity: evidence content address mismatch")
        expected_evidence_keys = {
            "schema_version",
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "observed_value",
        }
        if set(evidence_record) != expected_evidence_keys:
            errors.append(f"$.hard_gate_results[{index}]: gate evidence fields are not canonical")
        if evidence_record.get("schema_version") != "mstr.research-gate-evidence.v0":
            errors.append(f"$.hard_gate_results[{index}]: unsupported gate evidence schema_version")
        for field, expected in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
        ):
            if evidence_record.get(field) != expected:
                errors.append(f"$.hard_gate_results[{index}]: gate evidence {field} must match experiment")
        computed = _b026_compare_gate_value(
            criterion.get("operator"),
            evidence_record.get("observed_value"),
            criterion.get("expected_value"),
        )
        if computed is None:
            errors.append(f"$.hard_gate_results[{index}]: policy criterion cannot be evaluated")
        elif gate.get("status") != computed:
            errors.append(
                f"$.hard_gate_results[{index}].status: submitted status does not match predeclared criterion"
            )
    return tuple(sorted(errors))


'''
    replace_once(SCHEMAS_PY, helper_anchor, helper_code + helper_anchor)

    call_anchor = '''    hard_gates = instance.get("hard_gate_results")\n'''
    call_code = '''    errors.extend(\n        _b026_promotion_policy_errors(instance, repository_root=repository_root)\n    )\n\n'''
    replace_once(SCHEMAS_PY, call_anchor, call_code + call_anchor)

    old_q4 = '''            q4_record = instance.get("q4_promotion_record_identity_or_na")
            if not isinstance(q4_record, str) or q4_record == "N/A":
                errors.append(
                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires "
                    "concrete Q4 promotion evidence"
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
'''
    new_q4 = '''            q4_record_identity = instance.get("q4_promotion_record_identity_or_na")
            q4_digest = _b026_sha256_identity(q4_record_identity)
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
            if q4_digest is None:
                errors.append(
                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires a sha256-bound Q4 record"
                )
            else:
                q4_path = (
                    Path("artifacts") / "results" / "q4-promotion" / "registry" / f"{q4_digest}.json"
                )
                loaded_q4 = _b026_repository_json(repository_root, q4_path)
                if loaded_q4 is None:
                    errors.append(
                        "$.q4_promotion_record_identity_or_na: immutable Q4 promotion record missing"
                    )
                else:
                    q4_record, observed_q4_sha = loaded_q4
                    if observed_q4_sha != q4_digest:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record content address mismatch"
                        )
                    q4_errors = validation_errors(
                        "mstr-q4-promotion-v0",
                        q4_record,
                        schema_dir=schema_dir,
                        repository_root=repository_root,
                    )
                    if q4_errors:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 promotion record is invalid"
                        )
                    if q4_record.get("promotion_status") != "PROMOTED":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 record must be PROMOTED"
                        )
                    if q4_record.get("canonical_q4_artifact_sha256") != artifact_sha:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record artifact must match promoted result"
                        )
                    if q4_record.get("universal_laptop_gate_result") != "PASS":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: L4 requires universal-laptop gate PASS"
                        )
                    laptop_gate = gate_by_id.get("universal_laptop_product_gates")
                    if (
                        isinstance(laptop_gate, dict)
                        and q4_record.get("universal_laptop_gate_evidence_identity")
                        != laptop_gate.get("evidence_identity")
                    ):
                        errors.append(
                            "$.hard_gate_results[universal_laptop_product_gates].evidence_identity: "
                            "must match resolved Q4 universal-laptop evidence"
                        )
                    promotion_gate = gate_by_id.get("q4_promotion_record_promoted")
                    if (
                        isinstance(promotion_gate, dict)
                        and q4_record.get("promotion_decision_evidence_identity")
                        != promotion_gate.get("evidence_identity")
                    ):
                        errors.append(
                            "$.hard_gate_results[q4_promotion_record_promoted].evidence_identity: "
                            "must match resolved Q4 promotion-decision evidence"
                        )
'''
    replace_once(SCHEMAS_PY, old_q4, new_q4)


def update_data_model_and_readme() -> None:
    replace_once(
        DATA_MODEL,
        "- fidelity_level\n- predecessor_promotion\n",
        "- fidelity_level\n- promotion_policy_identity\n- predecessor_promotion\n",
    )
    old = (
        "`PROMOTE` binds `promoted_result_id_or_na` to a material result. Per-level identity gates "
        "have concrete semantic requirements. L4 additionally requires exact model/Q4 artifact, "
        "tokenizer, quantizer, runtime/build, OS/CPU/RAM/thread/backend/context/cache identities and "
        "binds both `q4_artifact_identity` and `q4_promotion_record_promoted` gate evidence to the exact "
        "promoted artifact/Q4 record."
    )
    new = (
        "Every research record binds `promotion_policy_identity` to the SHA-256 content address of a "
        "predeclared policy artifact. Each policy criterion exactly covers one required gate and freezes "
        "its comparison operator and expected value. Each hard-gate `evidence_identity` is the SHA-256 "
        "content address of an immutable observed-value record; validation recomputes PASS/FAIL from "
        "the predeclared criterion instead of trusting the submitted status. `PROMOTE` binds "
        "`promoted_result_id_or_na` to a material result. Per-level identity gates have concrete semantic "
        "requirements. L4 additionally resolves `q4_promotion_record_identity_or_na` as an immutable "
        "`mstr.q4-promotion.v0` record, requires `promotion_status=PROMOTED`, exact Q4 artifact identity, "
        "and an applicable universal-laptop PASS, with the Q4 record evidence identities bound back to "
        "the corresponding hard gates."
    )
    replace_once(DATA_MODEL, old, new)
    appendix = (
        "\n\n### B026 content-addressed promotion policy and gate evidence\n\n"
        "Research promotion is not self-attested. `promotion_policy_identity` and every hard-gate "
        "`evidence_identity` are lowercase `sha256:<digest>` content addresses resolved from the "
        "canonical registry templates frozen in `configs/research/mstr-research-ladder-v0.json`. "
        "A policy must bind the same governing task, campaign, fidelity level and frozen evaluator, "
        "must exactly cover the required gate IDs, and must predeclare `EQ`, `GTE`, `LTE`, or "
        "`NOT_APPLICABLE` criteria. Gate evidence binds task/campaign/experiment/gate and an observed "
        "value. The validator computes the gate status and rejects a submitted status that disagrees.\n\n"
        "For L4, `q4_promotion_record_identity_or_na` is a content address into the Q4 promotion "
        "registry. The resolved existing `mstr.q4-promotion.v0` contract remains authoritative; B026 "
        "does not create Q4 execution, training, model, network, paid-compute, or release authority.\n"
    )
    text = CONTRACT_README.read_text(encoding="utf-8").rstrip()
    if "### B026 content-addressed promotion policy and gate evidence" in text:
        raise SystemExit("README repair already present")
    CONTRACT_README.write_text(text + appendix, encoding="utf-8")


def prepare_fixture_registry() -> None:
    fixture = load_json(VALID_EXPERIMENT)
    task_id = str(fixture["governing_task_id"])
    campaign = str(fixture["campaign_id"])
    level = str(fixture["fidelity_level"])
    experiment_id = str(fixture["experiment_id"])
    evaluation = str(fixture["frozen_evaluation_identity"])
    gates = fixture.get("hard_gate_results")
    if not isinstance(gates, list):
        raise SystemExit("valid fixture hard gates missing")
    policy = {
        "schema_version": "mstr.research-promotion-policy.v0",
        "governing_task_id": task_id,
        "campaign_id": campaign,
        "fidelity_level": level,
        "frozen_evaluation_identity": evaluation,
        "criteria": [
            {"gate_id": gate_id, "operator": "EQ", "expected_value": True}
            for gate_id in required_gate_ids(level)
        ],
    }
    policy_identity = write_content_addressed(
        ROOT / "artifacts/results/research" / task_id / "promotion-policies",
        policy,
    )
    fixture["promotion_policy_identity"] = policy_identity
    for gate in gates:
        if not isinstance(gate, dict) or not isinstance(gate.get("gate_id"), str):
            raise SystemExit("valid fixture gate malformed")
        evidence = {
            "schema_version": "mstr.research-gate-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign,
            "experiment_id": experiment_id,
            "gate_id": gate["gate_id"],
            "observed_value": True,
        }
        gate["evidence_identity"] = write_content_addressed(
            ROOT / "artifacts/results/research" / task_id / "gate-evidence",
            evidence,
        )
    dump_json(VALID_EXPERIMENT, fixture)


def update_tests() -> None:
    insert_after = '''def _write_json_with_sha(path: Path, value: dict[str, object]) -> str:\n    path.parent.mkdir(parents=True, exist_ok=True)\n    raw = (json.dumps(value, indent=2) + "\\n").encode()\n    path.write_bytes(raw)\n    return hashlib.sha256(raw).hexdigest()\n\n\n'''
    helper = r'''def _write_content_addressed(path: Path, value: dict[str, object]) -> str:
    path.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    (path / f"{digest}.json").write_bytes(raw)
    return f"sha256:{digest}"


def _prepare_policy_and_gate_evidence(root: Path, record: dict[str, object]) -> None:
    task_id = str(record["governing_task_id"])
    campaign_id = str(record["campaign_id"])
    experiment_id = str(record["experiment_id"])
    level = str(record["fidelity_level"])
    policy = {
        "schema_version": "mstr.research-promotion-policy.v0",
        "governing_task_id": task_id,
        "campaign_id": campaign_id,
        "fidelity_level": level,
        "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
        "criteria": [
            {"gate_id": gate_id, "operator": "EQ", "expected_value": True}
            for gate_id in _required_gate_ids(level)
        ],
    }
    record["promotion_policy_identity"] = _write_content_addressed(
        root / "artifacts/results/research" / task_id / "promotion-policies",
        policy,
    )
    gates = record["hard_gate_results"]
    assert isinstance(gates, list)
    for gate in gates:
        assert isinstance(gate, dict)
        gate_id = str(gate["gate_id"])
        evidence = {
            "schema_version": "mstr.research-gate-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "observed_value": True,
        }
        gate["evidence_identity"] = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "gate-evidence",
            evidence,
        )

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
        record["q4_promotion_record_identity_or_na"] = _write_content_addressed(
            root / "artifacts/results/q4-promotion/registry",
            q4_record,
        )


'''
    replace_once(CONTRACT_TESTS, insert_after, insert_after + helper)

    old_l4 = '''        q4_record = "q4-promotion:fixture-l4"
        fixture["q4_promotion_record_identity_or_na"] = q4_record
        gates = fixture["hard_gate_results"]
        assert isinstance(gates, list)
        for gate in gates:
            assert isinstance(gate, dict)
            if gate["gate_id"] == "q4_artifact_identity":
                gate["evidence_identity"] = f"sha256:{'a' * 64}"
            if gate["gate_id"] == "q4_promotion_record_promoted":
                gate["evidence_identity"] = q4_record
'''
    replace_once(CONTRACT_TESTS, old_l4, "")

    replace_once(
        CONTRACT_TESTS,
        '''        validate_instance("mstr-research-experiment-v2", record, repository_root=root)\n        sha = _write_json_with_sha(\n''',
        '''        _prepare_policy_and_gate_evidence(root, record)\n        validate_instance("mstr-research-experiment-v2", record, repository_root=root)\n        sha = _write_json_with_sha(\n''',
    )

    # Direct-record tests outside _write_promoted_chain need their own policy/evidence registry.
    replace_once(
        CONTRACT_TESTS,
        '''    validate_instance("mstr-research-experiment-v2", l1, repository_root=tmp_path)\n\n    predecessor = l1["predecessor_promotion"]\n''',
        '''    _prepare_policy_and_gate_evidence(tmp_path, l1)\n    validate_instance("mstr-research-experiment-v2", l1, repository_root=tmp_path)\n\n    predecessor = l1["predecessor_promotion"]\n''',
    )
    replace_once(
        CONTRACT_TESTS,
        '''    validate_instance("mstr-research-experiment-v2", l3, repository_root=tmp_path)\n    predecessor = l3["predecessor_promotion"]\n''',
        '''    _prepare_policy_and_gate_evidence(tmp_path, l3)\n    validate_instance("mstr-research-experiment-v2", l3, repository_root=tmp_path)\n    predecessor = l3["predecessor_promotion"]\n''',
    )

    addition = r'''


def test_promotion_status_is_computed_from_predeclared_policy_and_content_bound_evidence(
    tmp_path: Path,
) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="policy-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    gates = record["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gate = gates[0]
    digest = str(gate["evidence_identity"]).removeprefix("sha256:")
    evidence_path = (
        tmp_path
        / "artifacts/results/research/B027/gate-evidence"
        / f"{digest}.json"
    )
    evidence = _json(evidence_path)
    evidence["observed_value"] = False
    replacement_identity = _write_content_addressed(evidence_path.parent, evidence)
    gate["evidence_identity"] = replacement_identity
    with pytest.raises(ValueError, match="submitted status does not match predeclared criterion"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_promotion_policy_missing_or_tampered_fails_closed(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="policy-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    record["promotion_policy_identity"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="predeclared policy record missing"):
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
    with pytest.raises(ValueError, match="Q4 record artifact must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
'''
    text = CONTRACT_TESTS.read_text(encoding="utf-8")
    if "test_promotion_status_is_computed_from_predeclared_policy" in text:
        raise SystemExit("new B026 repair tests already present")
    CONTRACT_TESTS.write_text(text.rstrip() + addition + "\n", encoding="utf-8")


def update_evidence() -> None:
    text = EVIDENCE.read_text(encoding="utf-8").rstrip()
    heading = "## Fresh exact-head Codex review findings on `633a8a4ed8717eeeee2c1c42d3045e5658d5fb25`"
    if heading in text:
        raise SystemExit("Codex repair evidence already present")
    appendix = f'''\n\n{heading}\n\nCodex review `PRR_kwDOUCYTYs8AAAABL3vKoQ` reviewed exact head `633a8a4ed8717eeeee2c1c42d3045e5658d5fb25` after qualification run `33646862191` and produced two P1 findings: Q4 promotion evidence was not resolved to an immutable `mstr.q4-promotion.v0` record, and submitted hard-gate `PASS` values were not recomputed against a content-bound predeclared decision policy.\n\nThis bounded repair introduces no research execution. It freezes content-addressed registry semantics for predeclared promotion policies and gate-observation evidence, makes every gate evidence identity a lowercase `sha256:<digest>` of exact repository bytes, recomputes the submitted gate status from the predeclared criterion, and rejects missing/tampered/mismatched policy or evidence records. L4 now resolves the existing B028 `mstr.q4-promotion.v0` contract by content address, requires `PROMOTED`, binds the canonical Q4 artifact SHA-256 to the promoted material result, requires an actual universal-laptop `PASS`, and binds the Q4 record's laptop and promotion-decision evidence identities to the corresponding B026 hard gates.\n\nThe B026 repository records added under `artifacts/results/research/B026/` are contract fixtures for the existing valid schema fixture only. They are not a B027 campaign, model run, Q4 execution, training result, paid-compute result, or authority grant. No actual Q4 promotion artifact is added.\n\nThese findings are not considered resolved by prose. Resolution requires guarded publication, fresh exact-head qualification, explicit thread reconciliation, and a new independent exact-head review.\n'''
    EVIDENCE.write_text(text + appendix, encoding="utf-8")


def main() -> None:
    update_config()
    update_schema()
    update_semantic_validator()
    update_data_model_and_readme()
    prepare_fixture_registry()
    update_tests()
    update_evidence()


if __name__ == "__main__":
    main()
