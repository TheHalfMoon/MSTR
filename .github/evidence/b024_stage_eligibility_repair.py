from __future__ import annotations

import json
from pathlib import Path

SCHEMA_PATHS = (
    Path("schemas/mstr-test-generation-example-v0.schema.json"),
    Path("specs/002-code-model-supremacy-foundation/contracts/mstr-test-generation-example-v0.schema.json"),
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def patch_schema(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    binding = data["$defs"]["verifier_health_binding"]
    properties = binding["properties"]
    properties["stage_id"] = {"$ref": "#/$defs/identity"}
    properties["stage_admission_class"] = {
        "enum": [
            "CLEAN_POSITIVE_ELIGIBLE",
            "RESEARCH_DIAGNOSTIC_ONLY",
            "BLOCKED",
        ]
    }
    for required in ("stage_id", "stage_admission_class"):
        if required not in binding["required"]:
            binding["required"].append(required)

    binding["allOf"] = [
        {
            "if": {
                "properties": {
                    "health_class": {"enum": ["PARTIAL", "DISAGREEMENT"]}
                },
                "required": ["health_class"],
            },
            "then": {
                "properties": {
                    "stage_admission_class": {
                        "enum": ["RESEARCH_DIAGNOSTIC_ONLY", "BLOCKED"]
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "health_class": {
                        "enum": ["BROKEN", "LEAKED", "TAMPERED"]
                    }
                },
                "required": ["health_class"],
            },
            "then": {
                "properties": {
                    "stage_admission_class": {"const": "BLOCKED"}
                }
            },
        },
    ]

    admit_rule = None
    for rule in data["allOf"]:
        condition = rule.get("if", {}).get("properties", {}).get("admission_decision")
        if isinstance(condition, dict) and condition.get("const") == "ADMIT":
            admit_rule = rule
            break
    if admit_rule is None:
        raise SystemExit("ADMIT rule not found")
    admit_binding = admit_rule["then"]["properties"]["verifier_health_binding"]
    admit_properties = admit_binding.setdefault("properties", {})
    admit_properties["health_class"] = {"const": "HEALTHY"}
    admit_properties["stage_admission_class"] = {
        "const": "CLEAN_POSITIVE_ELIGIBLE"
    }

    write_json(path, data)


def patch_fixture() -> None:
    path = Path("tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    binding = value["verifier_health_binding"]
    binding["stage_id"] = "MSTR-002-SFT"
    binding["stage_admission_class"] = "CLEAN_POSITIVE_ELIGIBLE"
    write_json(path, value)


def patch_tests() -> None:
    path = Path("tests/contract/test_test_generation_example_contract.py")
    text = path.read_text(encoding="utf-8")
    marker = "\ndef test_b024_schema_has_no_remote_reference() -> None:\n"
    addition = '''

@pytest.mark.parametrize(
    "stage_class",
    ["RESEARCH_DIAGNOSTIC_ONLY", "BLOCKED"],
)
def test_b024_admit_requires_clean_positive_stage_eligibility(stage_class: str) -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "HEALTHY"
    binding["stage_admission_class"] = stage_class
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_verifier_health_binding_requires_exact_stage_identity() -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding.pop("stage_id")
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_nonhealthy_health_cannot_claim_clean_positive_stage() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    value["admission_reasons"] = ["VERIFIER_HEALTH_NOT_CLEAN_POSITIVE"]
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["health_class"] = "PARTIAL"
    binding["stage_admission_class"] = "CLEAN_POSITIVE_ELIGIBLE"
    assert validation_errors("mstr-test-generation-example-v0", value)
'''
    if "test_b024_admit_requires_clean_positive_stage_eligibility" not in text:
        if marker not in text:
            raise SystemExit("test insertion point not found")
        text = text.replace(marker, addition + marker, 1)
    path.write_text(text, encoding="utf-8")


def patch_docs() -> None:
    path = Path("docs/data/TEST_GENERATION_CURRICULUM.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "- exact verifier-health binding across health-record id, task identity, executed verifier manifest, and class;",
        "- exact verifier-health binding across health-record id, task identity, executed verifier manifest, health class, stage identity, and stage admission class;",
    )
    needle = "VERIFIER_HEALTH_CLASS = HEALTHY\n"
    if needle in text and "STAGE_ADMISSION_CLASS" not in text:
        text = text.replace(
            needle,
            needle + "STAGE_ADMISSION_CLASS = CLEAN_POSITIVE_ELIGIBLE\n",
            1,
        )
    relationship = (
        "Downstream admission must consume canonical verifier-health evidence and may not infer `HEALTHY` from a passing test process alone."
    )
    replacement = (
        "Downstream admission must consume canonical verifier-health evidence and may not infer `HEALTHY` from a passing test process alone. "
        "Clean-positive admission also requires the exact referenced stage to be `CLEAN_POSITIVE_ELIGIBLE`; global `HEALTHY` status cannot override a stage-specific diagnostic or blocked decision."
    )
    text = text.replace(relationship, replacement)
    path.write_text(text, encoding="utf-8")

    path = Path("evidence/mstr-000b/B024-test-curriculum.md")
    text = path.read_text(encoding="utf-8")
    needle = "VERIFIER_HEALTH_BINDING_TO_TASK_AND_EXECUTED_MANIFEST = required\n"
    if needle not in text:
        raise SystemExit("verifier binding evidence line not found")
    if "CLEAN_POSITIVE_STAGE_ELIGIBILITY" not in text:
        text = text.replace(
            needle,
            needle
            + "VERIFIER_HEALTH_STAGE_IDENTITY = required\n"
            + "CLEAN_POSITIVE_STAGE_ELIGIBILITY = CLEAN_POSITIVE_ELIGIBLE\n",
            1,
        )
    remediation = '''

### Stage-eligibility review remediation

Codex review `5081306167` on intermediate head `639c263b2c349f21dddc2539d46748f67e544a0e` identified that global `HEALTHY` verifier status could still be admitted when the referenced training stage was diagnostic-only or blocked. This repair mirrors the canonical trajectory binding: every verifier-health binding carries exact `stage_id` and `stage_admission_class`, and clean-positive `ADMIT` requires `CLEAN_POSITIVE_ELIGIBLE`. `PARTIAL`/`DISAGREEMENT` cannot claim clean-positive stage eligibility, while `BROKEN`/`LEAKED`/`TAMPERED` are stage-blocked. These fields record eligibility evidence only and grant no training or external-runtime authority.
'''
    if "### Stage-eligibility review remediation" not in text:
        text += remediation
    path.write_text(text, encoding="utf-8")


def main() -> None:
    for path in SCHEMA_PATHS:
        patch_schema(path)
    patch_fixture()
    patch_tests()
    patch_docs()
    if SCHEMA_PATHS[0].read_bytes() != SCHEMA_PATHS[1].read_bytes():
        raise SystemExit("runtime/design B024 schemas diverged")


if __name__ == "__main__":
    main()
