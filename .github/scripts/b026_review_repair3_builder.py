from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
CONFIG = ROOT / "configs/research/mstr-research-ladder-v0.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
RESEARCH_SCHEMA = ROOT / "schemas/mstr-research-experiment-v2.schema.json"
SPEC_RESEARCH_SCHEMA = (
    ROOT
    / "specs/002-code-model-supremacy-foundation/contracts/"
    "mstr-research-experiment-v2.schema.json"
)
DATA_MODEL = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
SCHEMAS_PY = ROOT / "src/mstr_qualify/schemas.py"
CONTRACT_TESTS = ROOT / "tests/contract/test_research_ladder_contract.py"
CLI_TESTS = ROOT / "tests/integration/test_cli_offline.py"


def load_json(path: Path) -> dict[str, object]:
    """Read one repository JSON object or fail closed."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def dump_json(path: Path, value: object) -> None:
    """Write deterministic repository JSON."""

    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    """Replace one exact text fragment and reject stale builder assumptions."""

    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one replacement, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def update_promotion_semantics() -> None:
    """Make the chosen required-gate PASS semantics explicit everywhere."""

    config = load_json(CONFIG)
    levels = config.get("levels")
    if not isinstance(levels, list) or len(levels) != 5:
        raise SystemExit("research ladder must contain exactly five levels")
    changed = 0
    for level in levels:
        if not isinstance(level, dict):
            raise SystemExit("research ladder level must be an object")
        requirements = level.get("promotion_requires")
        if not isinstance(requirements, list):
            raise SystemExit("promotion_requires must be an array")
        for index, requirement in enumerate(requirements):
            if requirement == "no hard gate is failed":
                requirements[index] = "every required hard gate has status PASS"
                changed += 1
    if changed != 5:
        raise SystemExit(f"expected five promotion wording updates, found {changed}")
    dump_json(CONFIG, config)

    schema = load_json(RESEARCH_SCHEMA)
    defs = schema.get("$defs")
    if not isinstance(defs, dict):
        raise SystemExit("research schema $defs missing")
    hard_gate = defs.get("hard_gate_result")
    if not isinstance(hard_gate, dict):
        raise SystemExit("hard_gate_result missing")
    properties = hard_gate.get("properties")
    if not isinstance(properties, dict):
        raise SystemExit("hard_gate_result properties missing")
    status = properties.get("status")
    if not isinstance(status, dict):
        raise SystemExit("hard_gate_result.status missing")
    expected_enum = ["PASS", "FAIL", "NOT_APPLICABLE"]
    if status.get("enum") != expected_enum:
        raise SystemExit("unexpected hard-gate status enum")
    status["description"] = (
        "NOT_APPLICABLE is valid only for non-PROMOTE records; every required "
        "hard gate must be PASS when promotion_decision is PROMOTE."
    )
    dump_json(RESEARCH_SCHEMA, schema)
    SPEC_RESEARCH_SCHEMA.write_bytes(RESEARCH_SCHEMA.read_bytes())


def update_data_model() -> None:
    """Synchronize the canonical reading-order field block with the frozen schema."""

    old = """ResearchExperimentRecordV2
- experiment_id
- campaign_id
- parent_identity
- hypothesis
- mutable_surface
- mutation_identity
- frozen_evaluation_identity
- fidelity_level
- predecessor_promotion
- budget
- material_results[] : MaterialResultIdentity
- hard_gate_results
- promotion_decision
- decision_reason
- aggregate_resource_cost
- external_effect_authority
"""
    new = """ResearchExperimentRecordV2
- experiment_id
- governing_task_id
- campaign_id
- parent_identity
- hypothesis
- mutable_surface
- mutation_identity
- frozen_evaluation_identity
- fidelity_level
- predecessor_promotion
- budget
- material_results[] : MaterialResultIdentity
- hard_gate_results
- promotion_decision
- decision_reason
- promoted_result_id_or_na
- q4_promotion_record_identity_or_na
- governed_effects
- aggregate_resource_cost
- external_effect_authority
"""
    replace_once(DATA_MODEL, old, new)

    marker = (
        "Aggregate paid cost must equal the sum of per-result paid costs before budget "
        "or authority ceilings are evaluated."
    )
    addition = (
        marker
        + " B026 validates an authority ceiling for one research record only; it does not "
        "create a cumulative-consumption ledger or authorize repeated use of an authority. "
        "Any future external-effect executor must prove cumulative authority consumption "
        "under its own canonical execution contract before relying on these records to act."
    )
    replace_once(DATA_MODEL, marker, addition)


def update_semantic_validator() -> None:
    """Close the non-L4 Q4 fallthrough and preserve custom schema resolution."""

    replace_once(
        SCHEMAS_PY,
        """def _research_experiment_semantic_errors(
    instance: Any,
    *,
    repository_root: Path,
    visited_records: frozenset[str] = frozenset(),
) -> tuple[str, ...]:""",
        """def _research_experiment_semantic_errors(
    instance: Any,
    *,
    repository_root: Path,
    schema_dir: Path | None = None,
    visited_records: frozenset[str] = frozenset(),
) -> tuple[str, ...]:""",
    )
    replace_once(
        SCHEMAS_PY,
        """                        nested_errors = validation_errors(
                            \"mstr-research-experiment-v2\",
                            predecessor_record,
                            repository_root=repository_root,
                            _research_visited=visited_records | {registry_key},
                        )""",
        """                        nested_errors = validation_errors(
                            \"mstr-research-experiment-v2\",
                            predecessor_record,
                            schema_dir=schema_dir,
                            repository_root=repository_root,
                            _research_visited=visited_records | {registry_key},
                        )""",
    )
    replace_once(
        SCHEMAS_PY,
        """            _research_experiment_semantic_errors(
                instance,
                repository_root=(repository_root or _REPOSITORY_ROOT).resolve(),
                visited_records=_research_visited or frozenset(),
            )""",
        """            _research_experiment_semantic_errors(
                instance,
                repository_root=(repository_root or _REPOSITORY_ROOT).resolve(),
                schema_dir=schema_dir,
                visited_records=_research_visited or frozenset(),
            )""",
    )
    replace_once(
        SCHEMAS_PY,
        """    elif instance.get(\"q4_promotion_record_identity_or_na\") != \"N/A\":
        errors.append(
            \"$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence\"
        )""",
        """    if not (
        promotion_decision == \"PROMOTE\"
        and level == \"L4_Q4_UNIVERSAL_LAPTOP\"
        and promoted_result is not None
    ) and instance.get(\"q4_promotion_record_identity_or_na\") != \"N/A\":
        errors.append(
            \"$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence\"
        )""",
    )


def update_tests() -> None:
    """Add regression coverage for the fresh exact-head review findings."""

    contract_addition = r'''


def test_b026_runtime_and_spec_schema_pairs_are_byte_identical() -> None:
    pairs = (
        (
            ROOT / "schemas/mstr-material-result-identity-v0.schema.json",
            ROOT
            / "specs/002-code-model-supremacy-foundation/contracts/"
            "mstr-material-result-identity-v0.schema.json",
        ),
        (
            ROOT / "schemas/mstr-research-experiment-v2.schema.json",
            ROOT
            / "specs/002-code-model-supremacy-foundation/contracts/"
            "mstr-research-experiment-v2.schema.json",
        ),
    )
    for runtime, design in pairs:
        assert runtime.read_bytes() == design.read_bytes()


def test_promote_requires_every_required_gate_to_pass() -> None:
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
                "properties": {
                    "decision_reason": {"const": "CUSTOM_SCHEMA_PREDECESSOR_SENTINEL"}
                }
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
    text = (
        ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
    ).read_text(encoding="utf-8")
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
'''
    text = CONTRACT_TESTS.read_text(encoding="utf-8")
    marker = "def test_b026_runtime_and_spec_schema_pairs_are_byte_identical() -> None:"
    if marker in text:
        raise SystemExit("contract review-repair tests already present")
    CONTRACT_TESTS.write_text(text.rstrip() + contract_addition, encoding="utf-8")

    replace_once(
        CLI_TESTS,
        """    assert payload[\"status\"] == \"fail\"
    assert payload[\"files\"][0][\"status\"] == \"fail\"""",
        """    assert payload[\"status\"] == \"fail\"
    assert payload[\"files\"][0][\"status\"] == \"fail\"
    assert payload[\"files\"][0][\"code\"] == \"schema.instance_invalid\"""",
    )


def update_evidence() -> None:
    """Record the fresh exact-head findings without claiming premature closure."""

    text = EVIDENCE.read_text(encoding="utf-8").rstrip()
    heading = "## Fresh exact-head CodeRabbit review findings on `87d31a1c6488c80d8c6e35a4aadaf84a42fa20ac`"
    if heading in text:
        raise SystemExit("fresh review evidence already present")
    appendix = f'''\n\n{heading}\n\nCodeRabbit review `PRR_kwDOUCYTYs8AAAABL3Tj7A` / run `2914d85c-a8dd-4db3-8d5c-3aef880343e0` reviewed the exact qualified 17-file head and completed with status `53388944096`. It produced three actionable findings:\n\n1. the contract text said only that no hard gate failed while the schema correctly required every required gate to be `PASS` for `PROMOTE`;\n2. the canonical `ResearchExperimentRecordV2` reading-order block omitted four schema-required fields;\n3. semantic validation could fail to reject concrete Q4 promotion evidence on a non-L4 `PROMOTE` record because of an `elif` fallthrough.\n\nThis candidate chooses the stricter existing promotion semantics: every required gate must be `PASS`; `NOT_APPLICABLE` remains legal only for non-`PROMOTE` records. It synchronizes the ladder text and schema description, fixes the canonical data-model block, makes the Q4 restriction explicit at every non-L4/non-promote boundary, preserves caller-selected `schema_dir` for recursively resolved predecessor validation, adds byte-identity coverage for both B026 schema pairs, and binds the explicit CLI negative-fixture test to `schema.instance_invalid`.\n\nThe review also noted that canonical authority ceilings must not be treated as indefinitely reusable execution budget. B026 performs per-record ceiling validation only and grants no execution authority; cumulative authority-consumption accounting remains a mandatory responsibility of any future separately authorized external-effect executor. No cumulative authority or execution right is created here.\n\nThe broad sentinel-schema deduplication and wholesale rewriting of every historical generic negative-test assertion were maintainability nitpicks, not correctness findings, and are not claimed as part of this bounded repair.\n\nThese exact-head findings are not considered resolved by this evidence text. Resolution still requires guarded publication, fresh exact-head qualification, review-thread reconciliation, and a new independent exact-head substantive review.\n'''
    EVIDENCE.write_text(text + appendix, encoding="utf-8")


def main() -> None:
    update_promotion_semantics()
    update_data_model()
    update_semantic_validator()
    update_tests()
    update_evidence()


if __name__ == "__main__":
    main()
