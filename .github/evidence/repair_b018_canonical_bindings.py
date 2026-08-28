from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path.cwd()
RUNTIME_SCHEMA = ROOT / "schemas" / "mstr-self-alignment-generation-v0.schema.json"
DESIGN_SCHEMA = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "mstr-self-alignment-generation-v0.schema.json"
)
VALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-self-alignment-generation-v0.json"
)
INVALID_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "invalid"
    / "mstr-self-alignment-generation-v0.json"
)
SCHEMAS_PY = ROOT / "src" / "mstr_qualify" / "schemas.py"
TEST_FILE = ROOT / "tests" / "contract" / "test_self_alignment_contract.py"
EVIDENCE_FILE = ROOT / "evidence" / "mstr-000b" / "B018-self-alignment-contract.md"


def _string_schema() -> dict[str, object]:
    return {"type": "string", "minLength": 1, "maxLength": 512}


def _repair_schema() -> None:
    schema = json.loads(RUNTIME_SCHEMA.read_text(encoding="utf-8"))
    defs = schema["$defs"]
    properties = schema["properties"]

    student_identity = copy.deepcopy(properties["student_model_identity"])
    defs["student_model_identity"] = student_identity
    properties["student_model_identity"] = {"$ref": "#/$defs/student_model_identity"}

    defs["artifact_provenance_binding"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "artifact_id": _string_schema(),
            "provenance": {"$ref": "#/$defs/provenance"},
        },
        "required": ["artifact_id", "provenance"],
    }
    defs["artifact_rights_binding"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "artifact_id": _string_schema(),
            "rights_decision": {"$ref": "#/$defs/rights"},
        },
        "required": ["artifact_id", "rights_decision"],
    }
    defs["execution_binding"] = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "artifact_id": _string_schema(),
            "environment_identity": _string_schema(),
            "execution_result": {"$ref": "#/$defs/execution_result"},
        },
        "required": ["artifact_id", "environment_identity", "execution_result"],
    }

    difficulty = properties["difficulty_record"]
    difficulty_properties = difficulty["properties"]
    difficulty_properties["student_model_identity"] = {
        "$ref": "#/$defs/student_model_identity"
    }
    difficulty_properties["harness_profile_id"] = _string_schema()
    difficulty_properties["sampling_identity"] = _string_schema()
    difficulty["required"] = [
        "difficulty_record_identity",
        "difficulty_class",
        "student_model_identity",
        "harness_profile_id",
        "sampling_identity",
    ]

    properties["generated_artifact_provenance"] = {
        "type": "array",
        "minItems": 3,
        "uniqueItems": True,
        "items": {"$ref": "#/$defs/artifact_provenance_binding"},
    }
    properties["generated_artifact_rights_decisions"] = {
        "type": "array",
        "minItems": 3,
        "uniqueItems": True,
        "items": {"$ref": "#/$defs/artifact_rights_binding"},
    }
    properties["execution_results"] = {
        "type": "array",
        "minItems": 2,
        "uniqueItems": True,
        "items": {"$ref": "#/$defs/execution_binding"},
    }

    required = schema["required"]
    for field in (
        "generated_artifact_provenance",
        "generated_artifact_rights_decisions",
        "execution_results",
    ):
        if field not in required:
            required.append(field)

    rendered = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    RUNTIME_SCHEMA.write_text(rendered, encoding="utf-8")
    DESIGN_SCHEMA.write_text(rendered, encoding="utf-8")


def _generated_artifacts(record: dict[str, object]) -> list[dict[str, object]]:
    task = record["generated_task"]
    solutions = record["generated_solutions"]
    tests = record["generated_tests"]
    assert isinstance(task, dict)
    assert isinstance(solutions, list)
    assert isinstance(tests, list)
    artifacts = [task]
    artifacts.extend(item for item in solutions if isinstance(item, dict))
    artifacts.extend(item for item in tests if isinstance(item, dict))
    return artifacts


def _repair_fixture(path: Path) -> None:
    record = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(record, dict)
    student = record["student_model_identity"]
    difficulty = record["difficulty_record"]
    assert isinstance(student, dict)
    assert isinstance(difficulty, dict)
    difficulty["student_model_identity"] = copy.deepcopy(student)
    difficulty["harness_profile_id"] = student["harness_profile_id"]
    difficulty["sampling_identity"] = student["sampling_identity"]

    artifacts = _generated_artifacts(record)
    record["generated_artifact_provenance"] = [
        {
            "artifact_id": artifact["artifact_id"],
            "provenance": copy.deepcopy(artifact["provenance"]),
        }
        for artifact in artifacts
    ]
    record["generated_artifact_rights_decisions"] = [
        {
            "artifact_id": artifact["artifact_id"],
            "rights_decision": copy.deepcopy(artifact["rights_decision"]),
        }
        for artifact in artifacts
    ]
    record["execution_results"] = [
        {
            "artifact_id": artifact["artifact_id"],
            "environment_identity": record["environment_identity"],
            "execution_result": copy.deepcopy(artifact["execution_result"]),
        }
        for artifact in artifacts
        if artifact.get("artifact_kind") in {"SOLUTION", "TEST"}
    ]
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repair_semantic_validator() -> None:
    text = SCHEMAS_PY.read_text(encoding="utf-8")
    anchor = '''def validation_errors(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n) -> tuple[str, ...]:\n    """Return deterministic, human-readable validation errors."""\n\n    schema = load_schema(name, schema_dir=schema_dir)\n    validator = Draft202012Validator(schema)\n    errors = sorted(\n        validator.iter_errors(instance),\n        key=lambda error: (\n            tuple(str(part) for part in error.absolute_path),\n            tuple(str(part) for part in error.absolute_schema_path),\n            error.message,\n        ),\n    )\n    return tuple(_format_validation_error(error) for error in errors)\n'''
    if text.count(anchor) != 1:
        raise SystemExit("schemas.py validation_errors anchor mismatch")

    replacement = '''def _self_alignment_semantic_errors(instance: Any) -> tuple[str, ...]:\n    """Enforce B018 cross-field evidence bindings that JSON Schema cannot express."""\n\n    if not isinstance(instance, dict):\n        return ()\n\n    errors: list[str] = []\n    artifacts: dict[str, dict[str, Any]] = {}\n\n    def register_artifact(value: Any) -> None:\n        if not isinstance(value, dict):\n            return\n        artifact_id = value.get("artifact_id")\n        if not isinstance(artifact_id, str):\n            return\n        if artifact_id in artifacts:\n            errors.append(f"$.generated_artifacts: duplicate artifact_id {artifact_id!r}")\n            return\n        artifacts[artifact_id] = value\n\n    register_artifact(instance.get("generated_task"))\n    for collection in ("generated_solutions", "generated_tests"):\n        values = instance.get(collection)\n        if isinstance(values, list):\n            for value in values:\n                register_artifact(value)\n\n    def check_artifact_bindings(field: str, nested_field: str) -> None:\n        raw_bindings = instance.get(field)\n        if not isinstance(raw_bindings, list):\n            return\n        bindings: dict[str, dict[str, Any]] = {}\n        for index, binding in enumerate(raw_bindings):\n            if not isinstance(binding, dict):\n                continue\n            artifact_id = binding.get("artifact_id")\n            if not isinstance(artifact_id, str):\n                continue\n            if artifact_id in bindings:\n                errors.append(f"$.{field}[{index}].artifact_id: duplicate binding for {artifact_id!r}")\n                continue\n            bindings[artifact_id] = binding\n        if set(bindings) != set(artifacts):\n            errors.append(f"$.{field}: bindings must exactly cover generated artifact ids")\n        for artifact_id in sorted(set(bindings) & set(artifacts)):\n            if bindings[artifact_id].get(nested_field) != artifacts[artifact_id].get(nested_field):\n                errors.append(\n                    f"$.{field}: binding for {artifact_id!r} does not match artifact {nested_field}"\n                )\n\n    check_artifact_bindings("generated_artifact_provenance", "provenance")\n    check_artifact_bindings("generated_artifact_rights_decisions", "rights_decision")\n\n    raw_execution = instance.get("execution_results")\n    expected_execution = {\n        artifact_id: artifact\n        for artifact_id, artifact in artifacts.items()\n        if artifact.get("artifact_kind") in {"SOLUTION", "TEST"}\n    }\n    if isinstance(raw_execution, list):\n        bindings: dict[str, dict[str, Any]] = {}\n        for index, binding in enumerate(raw_execution):\n            if not isinstance(binding, dict):\n                continue\n            artifact_id = binding.get("artifact_id")\n            if not isinstance(artifact_id, str):\n                continue\n            if artifact_id in bindings:\n                errors.append(\n                    f"$.execution_results[{index}].artifact_id: duplicate binding for {artifact_id!r}"\n                )\n                continue\n            bindings[artifact_id] = binding\n        if set(bindings) != set(expected_execution):\n            errors.append("$.execution_results: bindings must exactly cover executable artifact ids")\n        environment_identity = instance.get("environment_identity")\n        for artifact_id in sorted(set(bindings) & set(expected_execution)):\n            binding = bindings[artifact_id]\n            artifact = expected_execution[artifact_id]\n            if binding.get("execution_result") != artifact.get("execution_result"):\n                errors.append(\n                    f"$.execution_results: binding for {artifact_id!r} does not match artifact execution_result"\n                )\n            if binding.get("environment_identity") != environment_identity:\n                errors.append(\n                    f"$.execution_results: binding for {artifact_id!r} does not match environment_identity"\n                )\n\n    student = instance.get("student_model_identity")\n    difficulty = instance.get("difficulty_record")\n    if isinstance(student, dict) and isinstance(difficulty, dict):\n        if difficulty.get("student_model_identity") != student:\n            errors.append(\n                "$.difficulty_record.student_model_identity: must exactly match student_model_identity"\n            )\n        if difficulty.get("harness_profile_id") != student.get("harness_profile_id"):\n            errors.append(\n                "$.difficulty_record.harness_profile_id: must match exact student harness_profile_id"\n            )\n        if difficulty.get("sampling_identity") != student.get("sampling_identity"):\n            errors.append(\n                "$.difficulty_record.sampling_identity: must match exact student sampling_identity"\n            )\n\n    return tuple(sorted(errors))\n\n\ndef validation_errors(\n    name: str,\n    instance: Any,\n    *,\n    schema_dir: Path | None = None,\n) -> tuple[str, ...]:\n    """Return deterministic, human-readable validation errors."""\n\n    schema = load_schema(name, schema_dir=schema_dir)\n    validator = Draft202012Validator(schema)\n    errors = sorted(\n        validator.iter_errors(instance),\n        key=lambda error: (\n            tuple(str(part) for part in error.absolute_path),\n            tuple(str(part) for part in error.absolute_schema_path),\n            error.message,\n        ),\n    )\n    formatted = [_format_validation_error(error) for error in errors]\n    if name == "mstr-self-alignment-generation-v0":\n        formatted.extend(_self_alignment_semantic_errors(instance))\n    return tuple(sorted(formatted))\n'''
    SCHEMAS_PY.write_text(text.replace(anchor, replacement), encoding="utf-8")


def _repair_tests() -> None:
    text = TEST_FILE.read_text(encoding="utf-8")
    reject_anchor = '''    rights["decision"] = "UNRESOLVED"\n    health = record["verifier_health"]\n'''
    if text.count(reject_anchor) != 1:
        raise SystemExit("reject-record test anchor mismatch")
    reject_replacement = '''    rights["decision"] = "UNRESOLVED"\n    rights_bindings = record["generated_artifact_rights_decisions"]\n    assert isinstance(rights_bindings, list)\n    test_rights_binding = next(\n        binding\n        for binding in rights_bindings\n        if isinstance(binding, dict) and binding.get("artifact_id") == "test"\n    )\n    bound_rights = test_rights_binding["rights_decision"]\n    assert isinstance(bound_rights, dict)\n    bound_rights["decision"] = "UNRESOLVED"\n    health = record["verifier_health"]\n'''
    text = text.replace(reject_anchor, reject_replacement)

    appendix = '''\n\n@pytest.mark.parametrize(\n    "field",\n    [\n        "generated_artifact_provenance",\n        "generated_artifact_rights_decisions",\n        "execution_results",\n    ],\n)\ndef test_canonical_generated_evidence_arrays_are_required(field: str) -> None:\n    record = _valid_record()\n    del record[field]\n    assert validation_errors(SCHEMA_NAME, record)\n\n\ndef test_generated_provenance_bindings_must_exactly_cover_artifacts() -> None:\n    record = _valid_record()\n    bindings = record["generated_artifact_provenance"]\n    assert isinstance(bindings, list)\n    bindings.pop()\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("exactly cover generated artifact ids" in error for error in errors)\n\n\ndef test_generated_provenance_binding_must_match_artifact() -> None:\n    record = _valid_record()\n    bindings = record["generated_artifact_provenance"]\n    assert isinstance(bindings, list)\n    binding = bindings[0]\n    assert isinstance(binding, dict)\n    provenance = binding["provenance"]\n    assert isinstance(provenance, dict)\n    provenance["source_revision"] = "mismatched-revision"\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("does not match artifact provenance" in error for error in errors)\n\n\ndef test_generated_rights_binding_must_match_artifact() -> None:\n    record = _valid_record()\n    bindings = record["generated_artifact_rights_decisions"]\n    assert isinstance(bindings, list)\n    binding = bindings[0]\n    assert isinstance(binding, dict)\n    rights = binding["rights_decision"]\n    assert isinstance(rights, dict)\n    rights["license_or_terms_identity"] = "mismatched-rights"\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("does not match artifact rights_decision" in error for error in errors)\n\n\ndef test_execution_bindings_must_exactly_cover_executable_artifacts() -> None:\n    record = _valid_record()\n    bindings = record["execution_results"]\n    assert isinstance(bindings, list)\n    bindings.pop()\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("exactly cover executable artifact ids" in error for error in errors)\n\n\ndef test_execution_binding_must_match_artifact_result() -> None:\n    record = _valid_record()\n    bindings = record["execution_results"]\n    assert isinstance(bindings, list)\n    binding = bindings[0]\n    assert isinstance(binding, dict)\n    result = binding["execution_result"]\n    assert isinstance(result, dict)\n    result["evidence_identity"] = "mismatched-execution"\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("does not match artifact execution_result" in error for error in errors)\n\n\ndef test_execution_binding_must_match_environment_identity() -> None:\n    record = _valid_record()\n    bindings = record["execution_results"]\n    assert isinstance(bindings, list)\n    binding = bindings[0]\n    assert isinstance(binding, dict)\n    binding["environment_identity"] = "other-sandbox"\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("does not match environment_identity" in error for error in errors)\n\n\n@pytest.mark.parametrize(\n    ("field", "value"),\n    [\n        ("student_model_identity", {\n            "model_id": "other-model",\n            "checkpoint_id": "other-checkpoint",\n            "harness_profile_id": "fixture-harness",\n            "sampling_identity": "fixture-sampling",\n        }),\n        ("harness_profile_id", "other-harness"),\n        ("sampling_identity", "other-sampling"),\n    ],\n)\ndef test_difficulty_binding_must_match_exact_student_harness_sampling_identity(\n    field: str, value: object\n) -> None:\n    record = _valid_record()\n    difficulty = record["difficulty_record"]\n    assert isinstance(difficulty, dict)\n    difficulty[field] = value\n    errors = validation_errors(SCHEMA_NAME, record)\n    assert any("difficulty_record" in error and "match" in error for error in errors)\n\n\ndef test_schema_exposes_exact_canonical_self_alignment_evidence_fields() -> None:\n    schema = json.loads(\n        (ROOT / "schemas" / "mstr-self-alignment-generation-v0.schema.json").read_text(\n            encoding="utf-8"\n        )\n    )\n    required = set(schema["required"])\n    assert {\n        "generated_artifact_provenance",\n        "generated_artifact_rights_decisions",\n        "execution_results",\n    } <= required\n\n\ndef test_b018_does_not_claim_b020_or_b022_authority() -> None:\n    evidence = (ROOT / "evidence" / "mstr-000b" / "B018-self-alignment-contract.md").read_text(\n        encoding="utf-8"\n    )\n    assert "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE" in evidence\n    assert "B022_VERIFIER_HEALTH_AUTHORITY = NONE" in evidence\n'''
    if "test_canonical_generated_evidence_arrays_are_required" in text:
        raise SystemExit("canonical binding tests already present")
    TEST_FILE.write_text(text + appendix, encoding="utf-8")


def _repair_evidence() -> None:
    text = EVIDENCE_FILE.read_text(encoding="utf-8")
    marker = "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE"
    if marker in text:
        raise SystemExit("B018 evidence canonical-binding repair already present")
    addition = '''\n\n## Canonical Field-Shape and Cross-Binding Repair\n\nThe contract exposes the canonical `SelfAlignmentGeneration` evidence surfaces as first-class fields rather than relying only on nested convenience copies:\n\n- `generated_artifact_provenance[]`\n- `generated_artifact_rights_decisions[]`\n- `execution_results[]`\n\nThe offline validator fails closed unless those arrays exactly cover the generated artifact identities and exactly match the nested provenance, rights, execution result, and environment bindings. It also fails closed unless the embedded `difficulty_record` binds the exact student model/checkpoint, harness profile, and sampling identity used by the generation.\n\nThese are evidence bindings only. B018 does not perform difficulty calibration and does not create or certify verifier-health authority; those remain owned by their canonical tasks.\n\n```text\nB020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE\nB022_VERIFIER_HEALTH_AUTHORITY = NONE\nB020_BINDING_SURFACE = difficulty_record_identity + exact student/harness/sampling identity\nB022_BINDING_SURFACE = verifier_health_record_identity + verifier identity/health snapshot\n```\n'''
    EVIDENCE_FILE.write_text(text + addition, encoding="utf-8")


def main() -> None:
    _repair_schema()
    _repair_fixture(VALID_FIXTURE)
    _repair_fixture(INVALID_FIXTURE)
    _repair_semantic_validator()
    _repair_tests()
    _repair_evidence()


if __name__ == "__main__":
    main()
