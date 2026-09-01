from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()
SCHEMA_PATHS = (
    Path("schemas/mstr-test-generation-example-v0.schema.json"),
    Path("specs/002-code-model-supremacy-foundation/contracts/mstr-test-generation-example-v0.schema.json"),
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def patch_schema(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))

    provenance = data["$defs"]["provenance"]
    provenance["properties"]["provenance_status"] = {
        "enum": ["COMPLETE", "INCOMPLETE", "UNRESOLVED"]
    }
    if "provenance_status" not in provenance["required"]:
        provenance["required"].append("provenance_status")

    data["$defs"]["verifier_health_binding"] = {
        "additionalProperties": False,
        "properties": {
            "health_class": {
                "enum": [
                    "HEALTHY",
                    "PARTIAL",
                    "DISAGREEMENT",
                    "BROKEN",
                    "LEAKED",
                    "TAMPERED",
                ]
            },
            "schema_version": {"const": "mstr.verifier-health.v0"},
            "task_identity": {"$ref": "#/$defs/identity"},
            "verifier_health_id": {"$ref": "#/$defs/identity"},
            "verifier_manifest_id": {"$ref": "#/$defs/identity"},
        },
        "required": [
            "schema_version",
            "verifier_health_id",
            "task_identity",
            "verifier_manifest_id",
            "health_class",
        ],
        "type": "object",
    }

    admit_properties = data["allOf"][0]["then"]["properties"]
    admit_properties.pop("verifier_health_class", None)
    admit_properties["generated_test_provenance"] = {
        "properties": {"provenance_status": {"const": "COMPLETE"}}
    }
    admit_properties["verifier_health_binding"] = {
        "properties": {"health_class": {"const": "HEALTHY"}}
    }

    generated_provenance_gate = {
        "if": {
            "properties": {
                "generated_test_provenance": {
                    "properties": {
                        "source_class": {
                            "enum": [
                                "SYNTHETIC_VERIFIED",
                                "STUDENT_GENERATED",
                                "TEACHER_GENERATED",
                            ]
                        }
                    },
                    "required": ["source_class"],
                }
            },
            "required": ["generated_test_provenance"],
        },
        "then": {
            "properties": {
                "generated_test_provenance": {
                    "properties": {
                        "generator_identity": {"$ref": "#/$defs/identity"}
                    }
                }
            }
        },
    }
    adequate_mutation_gate = {
        "if": {
            "properties": {
                "mutation_strength": {
                    "properties": {"status": {"const": "ADEQUATE"}},
                    "required": ["status"],
                }
            },
            "required": ["mutation_strength"],
        },
        "then": {
            "properties": {
                "mutation_strength": {
                    "properties": {
                        "evidence_identity": {"$ref": "#/$defs/identity"},
                        "mutants_evaluated": {"minimum": 1},
                        "mutants_killed": {"minimum": 1},
                    }
                }
            }
        },
    }
    data["allOf"] = [
        rule
        for rule in data["allOf"]
        if rule not in (generated_provenance_gate, adequate_mutation_gate)
    ]
    data["allOf"].extend((generated_provenance_gate, adequate_mutation_gate))

    properties = data["properties"]
    properties.pop("verifier_health_id", None)
    properties.pop("verifier_health_class", None)
    properties["verifier_health_binding"] = {"$ref": "#/$defs/verifier_health_binding"}

    required = [
        item
        for item in data["required"]
        if item not in {"verifier_health_id", "verifier_health_class", "verifier_health_binding"}
    ]
    insert_at = required.index("admission_decision")
    required.insert(insert_at, "verifier_health_binding")
    data["required"] = required

    write_json(path, data)


def patch_semantic_validator() -> None:
    path = Path("src/mstr_qualify/schemas.py")
    text = path.read_text(encoding="utf-8")
    start = text.index("def _test_generation_semantic_errors")
    end = text.index("def _trajectory_manifest_semantic_errors", start)
    replacement = '''def _test_generation_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B024 cross-field behavioral and identity bindings."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    patch = instance.get("generated_test_patch")
    proof = instance.get("behavioral_proof")
    pre: dict[str, Any] | None = None
    post: dict[str, Any] | None = None
    if isinstance(patch, dict) and isinstance(proof, dict):
        artifact_sha = patch.get("test_artifact_sha256")
        raw_pre = proof.get("pre_fix_result")
        raw_post = proof.get("post_fix_result")
        if isinstance(raw_pre, dict) and isinstance(raw_post, dict):
            pre = raw_pre
            post = raw_post
            for label, result in (("pre_fix_result", pre), ("post_fix_result", post)):
                if result.get("task_identity") != instance.get("task_identity"):
                    errors.append(
                        f"$.behavioral_proof.{label}.task_identity: must match task_identity"
                    )
                if result.get("test_artifact_sha256") != artifact_sha:
                    errors.append(
                        f"$.behavioral_proof.{label}.test_artifact_sha256: "
                        "must match generated_test_patch.test_artifact_sha256"
                    )
            if pre.get("revision") != instance.get("base_revision"):
                errors.append(
                    "$.behavioral_proof.pre_fix_result.revision: must match base_revision"
                )
            if post.get("revision") != instance.get("fix_revision"):
                errors.append(
                    "$.behavioral_proof.post_fix_result.revision: must match fix_revision"
                )
            if pre.get("environment_identity") != post.get("environment_identity"):
                errors.append(
                    "$.behavioral_proof: pre/post environment_identity must match"
                )
            if pre.get("verifier_manifest_id") != post.get("verifier_manifest_id"):
                errors.append(
                    "$.behavioral_proof: pre/post verifier_manifest_id must match"
                )

    provenance = instance.get("generated_test_provenance")
    if isinstance(provenance, dict):
        if (
            instance.get("admission_decision") == "ADMIT"
            and provenance.get("provenance_status") != "COMPLETE"
        ):
            errors.append(
                "$.generated_test_provenance.provenance_status: ADMIT requires COMPLETE provenance"
            )
        if provenance.get("source_class") in {
            "SYNTHETIC_VERIFIED",
            "STUDENT_GENERATED",
            "TEACHER_GENERATED",
        }:
            generator_identity = provenance.get("generator_identity")
            if not isinstance(generator_identity, str) or not generator_identity:
                errors.append(
                    "$.generated_test_provenance.generator_identity: generated source classes "
                    "require generator identity"
                )

    verifier_health = instance.get("verifier_health_binding")
    if isinstance(verifier_health, dict):
        if verifier_health.get("task_identity") != instance.get("task_identity"):
            errors.append(
                "$.verifier_health_binding.task_identity: must match task_identity"
            )
        if pre is not None and verifier_health.get("verifier_manifest_id") != pre.get(
            "verifier_manifest_id"
        ):
            errors.append(
                "$.verifier_health_binding.verifier_manifest_id: must match executed verifier manifest"
            )
        if post is not None and verifier_health.get("verifier_manifest_id") != post.get(
            "verifier_manifest_id"
        ):
            errors.append(
                "$.verifier_health_binding.verifier_manifest_id: must match executed verifier manifest"
            )

    behavior = instance.get("behavior_contract")
    if isinstance(behavior, dict):
        classes = behavior.get("test_classes")
        class_set = (
            {item for item in classes if isinstance(item, str)}
            if isinstance(classes, list)
            else set()
        )
        if behavior.get("requires_reproduction") is True and "REPRODUCTION" not in class_set:
            errors.append(
                "$.behavior_contract.test_classes: REPRODUCTION required when "
                "requires_reproduction=true"
            )
        if behavior.get("property_or_metamorphic_applicable") is True and not (
            {"PROPERTY", "METAMORPHIC"} & class_set
        ):
            errors.append(
                "$.behavior_contract.test_classes: PROPERTY or METAMORPHIC required "
                "when property_or_metamorphic_applicable=true"
            )

    mutation = instance.get("mutation_strength")
    if isinstance(mutation, dict):
        evaluated = mutation.get("mutants_evaluated")
        killed = mutation.get("mutants_killed")
        if (
            isinstance(evaluated, int)
            and not isinstance(evaluated, bool)
            and isinstance(killed, int)
            and not isinstance(killed, bool)
            and killed > evaluated
        ):
            errors.append("$.mutation_strength.mutants_killed: cannot exceed mutants_evaluated")
        if mutation.get("status") == "ADEQUATE":
            if not isinstance(mutation.get("evidence_identity"), str) or not mutation.get(
                "evidence_identity"
            ):
                errors.append(
                    "$.mutation_strength.evidence_identity: ADEQUATE requires concrete evidence"
                )
            if not isinstance(evaluated, int) or isinstance(evaluated, bool) or evaluated < 1:
                errors.append(
                    "$.mutation_strength.mutants_evaluated: ADEQUATE requires at least one mutant"
                )
            if not isinstance(killed, int) or isinstance(killed, bool) or killed < 1:
                errors.append(
                    "$.mutation_strength.mutants_killed: ADEQUATE requires at least one killed mutant"
                )

    return tuple(sorted(errors))


'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def patch_fixture() -> None:
    path = Path("tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json")
    value = json.loads(path.read_text(encoding="utf-8"))
    value["generated_test_provenance"]["provenance_status"] = "COMPLETE"
    value.pop("verifier_health_id", None)
    value.pop("verifier_health_class", None)
    value["verifier_health_binding"] = {
        "health_class": "HEALTHY",
        "schema_version": "mstr.verifier-health.v0",
        "task_identity": value["task_identity"],
        "verifier_health_id": "fixture-verifier-health:healthy-v1",
        "verifier_manifest_id": "fixture-verifier-manifest-v1",
    }
    write_json(path, value)


def patch_tests() -> None:
    path = Path("tests/contract/test_test_generation_example_contract.py")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '    value["verifier_health_class"] = health\n',
        '    value["verifier_health_binding"]["health_class"] = health\n',
    )
    marker = "\ndef test_b024_schema_has_no_remote_reference() -> None:\n"
    additions = '''

def test_b024_admit_requires_complete_generated_test_provenance() -> None:
    value = fixture()
    value["generated_test_provenance"]["provenance_status"] = "UNRESOLVED"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_generated_sources_require_generator_identity() -> None:
    value = fixture()
    provenance = value["generated_test_provenance"]
    assert isinstance(provenance, dict)
    provenance["source_class"] = "STUDENT_GENERATED"
    provenance["generator_identity"] = None
    assert validation_errors("mstr-test-generation-example-v0", value)
    provenance["generator_identity"] = "student-generator:fixture-v1"
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_verifier_health_binding_matches_task_and_executed_verifier() -> None:
    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["task_identity"] = "other-task"
    assert any(
        "verifier_health_binding.task_identity" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )

    value = fixture()
    binding = value["verifier_health_binding"]
    assert isinstance(binding, dict)
    binding["verifier_manifest_id"] = "other-verifier"
    assert any(
        "must match executed verifier manifest" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_adequate_mutation_strength_requires_real_evidence() -> None:
    value = fixture()
    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": None,
        "mutants_evaluated": 0,
        "mutants_killed": 0,
    }
    assert validation_errors("mstr-test-generation-example-v0", value)

    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": "fixture-mutation:v1",
        "mutants_evaluated": 2,
        "mutants_killed": 1,
    }
    validate_instance("mstr-test-generation-example-v0", value)
'''
    if "test_b024_admit_requires_complete_generated_test_provenance" not in text:
        text = text.replace(marker, additions + marker)
    path.write_text(text, encoding="utf-8")


def patch_docs() -> None:
    curriculum = Path("docs/data/TEST_GENERATION_CURRICULUM.md")
    text = curriculum.read_text(encoding="utf-8")
    text = text.replace(
        "- generated-test provenance and immutable lineage;",
        "- generated-test provenance, explicit completeness state, immutable lineage, and generator identity for generated source classes;",
    )
    text = text.replace(
        "- exact verifier-health identity and class;",
        "- exact verifier-health binding across health-record id, task identity, executed verifier manifest, and class;",
    )
    text = text.replace(
        "B024 records an exact verifier-health identity/class but does not create a second health authority",
        "B024 records an exact verifier-health binding but does not create a second health authority",
    )
    curriculum.write_text(text, encoding="utf-8")

    evidence = Path("evidence/mstr-000b/B024-test-curriculum.md")
    text = evidence.read_text(encoding="utf-8")
    text = text.replace(
        "ADMIT_REQUIRES_HEALTHY_VERIFIER = true",
        "ADMIT_REQUIRES_COMPLETE_PROVENANCE = true\nGENERATED_SOURCE_REQUIRES_GENERATOR_IDENTITY = true\nADMIT_REQUIRES_HEALTHY_VERIFIER = true\nVERIFIER_HEALTH_BINDING_TO_TASK_AND_EXECUTED_MANIFEST = required\nADEQUATE_MUTATION_REQUIRES_NONZERO_EVIDENCE = true",
    )
    remediation = '''

## Independent review remediation

Codex independent review `5081151219` on reviewed commit `f052704cdb` identified three P1 fail-closed defects. This repair candidate addresses all three without changing task state or authority:

1. generated source classes now require a concrete generator identity, and clean-positive admission requires explicit `COMPLETE` provenance;
2. verifier health is represented as a canonical binding whose task identity and verifier manifest must match the exact executed proof;
3. `ADEQUATE` mutation strength now requires concrete evidence plus nonzero evaluated and killed mutation counts.

Regression tests reproduce each reviewed defect and require the repaired behavior. A new exact-head qualification and independent review are still required after this repair; the prior qualification and review do not transfer to the repaired head.
'''
    if "## Independent review remediation" not in text:
        text += remediation
    evidence.write_text(text, encoding="utf-8")


def main() -> None:
    for path in SCHEMA_PATHS:
        patch_schema(path)
    patch_semantic_validator()
    patch_fixture()
    patch_tests()
    patch_docs()

    runtime = SCHEMA_PATHS[0].read_bytes()
    design = SCHEMA_PATHS[1].read_bytes()
    if runtime != design:
        raise SystemExit("runtime/design B024 schemas diverged")


if __name__ == "__main__":
    main()
