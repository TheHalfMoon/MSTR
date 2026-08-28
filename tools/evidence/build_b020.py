from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SCHEMA_NAME = "mstr-difficulty-calibration-v0"
SCHEMA_VERSION = "mstr.difficulty-calibration.v0"
ENTRY_MAIN = "ef90e96ba3d4e2c253987d1d104e0de26ce93529"
ENTRY_RUN = "33198484632"
ENTRY_JOB = "98941644785"


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one replacement anchor in {path}: {old!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-difficulty-calibration-v0.json",
    "title": "MSTR Difficulty Calibration v0",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "student_model_identity": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "model_id": {"type": "string", "minLength": 1, "maxLength": 512},
                "checkpoint_id": {"type": "string", "minLength": 1, "maxLength": 512},
                "harness_profile_id": {"type": "string", "minLength": 1, "maxLength": 512},
                "sampling_identity": {"type": "string", "minLength": 1, "maxLength": 512},
            },
            "required": [
                "model_id",
                "checkpoint_id",
                "harness_profile_id",
                "sampling_identity",
            ],
        },
        "failure_bucket": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "failure_class": {"type": "string", "minLength": 1, "maxLength": 128},
                "count": {"type": "integer", "minimum": 1},
            },
            "required": ["failure_class", "count"],
        },
    },
    "properties": {
        "schema_version": {"const": SCHEMA_VERSION},
        "difficulty_record_identity": {"type": "string", "minLength": 1, "maxLength": 512},
        "task_or_family_id": {"type": "string", "minLength": 1, "maxLength": 512},
        "student_model_identity": {"$ref": "#/$defs/student_model_identity"},
        "harness_profile_id": {"type": "string", "minLength": 1, "maxLength": 512},
        "sampling_identity": {"type": "string", "minLength": 1, "maxLength": 512},
        "attempt_count": {"type": "integer", "minimum": 1},
        "success_count": {"type": "integer", "minimum": 0},
        "estimated_solve_probability": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "structural_features": {
            "type": "object",
            "minProperties": 1,
            "propertyNames": {"minLength": 1, "maxLength": 128},
            "additionalProperties": {"type": ["string", "number", "boolean"]},
        },
        "failure_distribution": {
            "type": "array",
            "items": {"$ref": "#/$defs/failure_bucket"},
            "uniqueItems": True,
        },
        "difficulty_class": {
            "enum": [
                "TOO_EASY",
                "LEARNABLE_FRONTIER",
                "HARD_FRONTIER",
                "CURRENTLY_UNPRODUCTIVE",
                "INVALID",
            ]
        },
        "calibration_time": {
            "type": "string",
            "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$",
        },
    },
    "required": [
        "schema_version",
        "difficulty_record_identity",
        "task_or_family_id",
        "student_model_identity",
        "harness_profile_id",
        "sampling_identity",
        "attempt_count",
        "success_count",
        "estimated_solve_probability",
        "structural_features",
        "failure_distribution",
        "difficulty_class",
        "calibration_time",
    ],
}

schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
write("schemas/mstr-difficulty-calibration-v0.schema.json", schema_text)
write(
    "specs/002-code-model-supremacy-foundation/contracts/mstr-difficulty-calibration-v0.schema.json",
    schema_text,
)

valid_fixture = {
    "schema_version": SCHEMA_VERSION,
    "difficulty_record_identity": "difficulty-fixture-001",
    "task_or_family_id": "fixture.task.family",
    "student_model_identity": {
        "model_id": "fixture/student",
        "checkpoint_id": "checkpoint-0001",
        "harness_profile_id": "h1-fixture",
        "sampling_identity": "sampling-fixture-v1",
    },
    "harness_profile_id": "h1-fixture",
    "sampling_identity": "sampling-fixture-v1",
    "attempt_count": 8,
    "success_count": 4,
    "estimated_solve_probability": 0.5,
    "structural_features": {
        "task_kind": "fixture",
        "files_touched_hint": 3,
        "requires_repository_context": True,
        "verification_steps_hint": 2,
    },
    "failure_distribution": [
        {"failure_class": "IMPLEMENTATION_FAILURE", "count": 2},
        {"failure_class": "VERIFIER_FAILURE", "count": 1},
        {"failure_class": "TIMEOUT", "count": 1},
    ],
    "difficulty_class": "LEARNABLE_FRONTIER",
    "calibration_time": "2026-08-28T18:15:43Z",
}
invalid_fixture = dict(valid_fixture)
invalid_fixture["difficulty_record_identity"] = "difficulty-fixture-invalid"
invalid_fixture["attempt_count"] = 4
invalid_fixture["success_count"] = 5
invalid_fixture["failure_distribution"] = []
write(
    "tests/fixtures/schemas/valid/mstr-difficulty-calibration-v0.json",
    json.dumps(valid_fixture, indent=2, sort_keys=True) + "\n",
)
write(
    "tests/fixtures/schemas/invalid/mstr-difficulty-calibration-v0.json",
    json.dumps(invalid_fixture, indent=2, sort_keys=True) + "\n",
)

replace_once(
    "src/mstr_qualify/schemas.py",
    "import json\n",
    "import json\nimport math\n",
)
replace_once(
    "src/mstr_qualify/schemas.py",
    '    "mstr-teacher-rescue-record-v0": "mstr-teacher-rescue-record-v0.schema.json",\n',
    '    "mstr-teacher-rescue-record-v0": "mstr-teacher-rescue-record-v0.schema.json",\n'
    '    # MSTR-000B B020: checkpoint-relative difficulty calibration contract.\n'
    '    "mstr-difficulty-calibration-v0": "mstr-difficulty-calibration-v0.schema.json",\n',
)
semantic_function = '''\n\ndef _difficulty_calibration_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B020 checkpoint-relative identity and attempt-accounting semantics."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    attempts = instance.get("attempt_count")
    successes = instance.get("success_count")
    if (
        isinstance(attempts, int)
        and not isinstance(attempts, bool)
        and isinstance(successes, int)
        and not isinstance(successes, bool)
        and successes > attempts
    ):
        errors.append("$.success_count: cannot exceed attempt_count")

    probability = instance.get("estimated_solve_probability")
    if (
        isinstance(probability, (int, float))
        and not isinstance(probability, bool)
        and not math.isfinite(float(probability))
    ):
        errors.append("$.estimated_solve_probability: must be finite")

    student = instance.get("student_model_identity")
    if isinstance(student, dict):
        if instance.get("harness_profile_id") != student.get("harness_profile_id"):
            errors.append(
                "$.harness_profile_id: must match student_model_identity.harness_profile_id"
            )
        if instance.get("sampling_identity") != student.get("sampling_identity"):
            errors.append(
                "$.sampling_identity: must match student_model_identity.sampling_identity"
            )

    failure_distribution = instance.get("failure_distribution")
    if isinstance(failure_distribution, list):
        seen: set[str] = set()
        failure_total = 0
        countable = True
        for index, bucket in enumerate(failure_distribution):
            if not isinstance(bucket, dict):
                countable = False
                continue
            failure_class = bucket.get("failure_class")
            count = bucket.get("count")
            if isinstance(failure_class, str):
                if failure_class in seen:
                    errors.append(
                        f"$.failure_distribution[{index}]: duplicate failure_class {failure_class!r}"
                    )
                seen.add(failure_class)
            if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
                failure_total += count
            else:
                countable = False
        if (
            countable
            and isinstance(attempts, int)
            and not isinstance(attempts, bool)
            and isinstance(successes, int)
            and not isinstance(successes, bool)
            and 0 <= successes <= attempts
            and failure_total != attempts - successes
        ):
            errors.append(
                "$.failure_distribution: counts must exactly cover attempt_count - success_count"
            )

    return tuple(sorted(errors))
'''
replace_once(
    "src/mstr_qualify/schemas.py",
    "    return tuple(sorted(errors))\ndef validation_errors(\n",
    "    return tuple(sorted(errors))\n" + semantic_function + "\ndef validation_errors(\n",
)
replace_once(
    "src/mstr_qualify/schemas.py",
    '    if name == "mstr-teacher-rescue-record-v0":\n        formatted.extend(_teacher_rescue_semantic_errors(instance))\n',
    '    if name == "mstr-teacher-rescue-record-v0":\n        formatted.extend(_teacher_rescue_semantic_errors(instance))\n'
    '    if name == "mstr-difficulty-calibration-v0":\n        formatted.extend(_difficulty_calibration_semantic_errors(instance))\n',
)

replace_once(
    "src/mstr_qualify/cli.py",
    '    "mstr.teacher-rescue-record.v0": "mstr-teacher-rescue-record-v0",\n',
    '    "mstr.teacher-rescue-record.v0": "mstr-teacher-rescue-record-v0",\n'
    '    # MSTR-000B B020 checkpoint-relative difficulty calibration contract.\n'
    '    "mstr.difficulty-calibration.v0": "mstr-difficulty-calibration-v0",\n',
)

replace_once(
    "tests/contract/test_schemas.py",
    '    "mstr-teacher-rescue-record-v0": (\n        ROOT\n        / "specs"\n        / "002-code-model-supremacy-foundation"\n        / "contracts"\n        / "mstr-teacher-rescue-record-v0.schema.json"\n    ),\n',
    '    "mstr-teacher-rescue-record-v0": (\n        ROOT\n        / "specs"\n        / "002-code-model-supremacy-foundation"\n        / "contracts"\n        / "mstr-teacher-rescue-record-v0.schema.json"\n    ),\n'
    '    "mstr-difficulty-calibration-v0": (\n        ROOT\n        / "specs"\n        / "002-code-model-supremacy-foundation"\n        / "contracts"\n        / "mstr-difficulty-calibration-v0.schema.json"\n    ),\n',
)

replace_once(
    "tests/integration/test_cli_offline.py",
    '        "mstr-data-constitution-v0",\n        "mstr-loop-contract-v0",\n',
    '        "mstr-data-constitution-v0",\n        "mstr-difficulty-calibration-v0",\n        "mstr-loop-contract-v0",\n',
)
replace_once(
    "tests/integration/test_cli_offline.py",
    'def test_validate_is_deterministic_across_runs(capsys: pytest.CaptureFixture[str]) -> None:\n',
    '''def test_validate_explicit_b020_difficulty_fixture_passes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = (
        Path(__file__).resolve().parents[2]
        / "tests"
        / "fixtures"
        / "schemas"
        / "valid"
        / "mstr-difficulty-calibration-v0.json"
    )
    assert main(["validate", str(path)]) == 0
    payload = parse_stdout(capsys)
    assert payload["status"] == "pass"
    assert payload["files"][0]["schema_version"] == "mstr.difficulty-calibration.v0"


def test_validate_is_deterministic_across_runs(capsys: pytest.CaptureFixture[str]) -> None:
''',
)

contract_test = '''from __future__ import annotations

import copy
import math
import json
from pathlib import Path

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / "mstr-difficulty-calibration-v0.json"
INVALID = ROOT / "tests" / "fixtures" / "schemas" / "invalid" / "mstr-difficulty-calibration-v0.json"


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def errors(value: object) -> tuple[str, ...]:
    return validation_errors("mstr-difficulty-calibration-v0", value)


def test_b020_valid_fixture_passes() -> None:
    validate_instance("mstr-difficulty-calibration-v0", fixture())


def test_b020_invalid_fixture_fails_closed() -> None:
    assert errors(json.loads(INVALID.read_text(encoding="utf-8")))


def test_b020_success_count_cannot_exceed_attempt_count() -> None:
    value = fixture()
    value["attempt_count"] = 3
    value["success_count"] = 4
    assert any("cannot exceed attempt_count" in item for item in errors(value))


def test_b020_failure_distribution_exactly_covers_failed_attempts() -> None:
    value = fixture()
    value["failure_distribution"][0]["count"] = 1
    assert any("exactly cover attempt_count - success_count" in item for item in errors(value))


def test_b020_duplicate_failure_class_fails_closed() -> None:
    value = fixture()
    duplicate = copy.deepcopy(value["failure_distribution"][0])
    duplicate["count"] = 1
    value["failure_distribution"].append(duplicate)
    value["failure_distribution"][1]["count"] = 0
    assert any("duplicate failure_class" in item for item in errors(value))


def test_b020_harness_identity_must_match_student_identity() -> None:
    value = fixture()
    value["harness_profile_id"] = "different-harness"
    assert any("must match student_model_identity.harness_profile_id" in item for item in errors(value))


def test_b020_sampling_identity_must_match_student_identity() -> None:
    value = fixture()
    value["sampling_identity"] = "different-sampling"
    assert any("must match student_model_identity.sampling_identity" in item for item in errors(value))


def test_b020_contract_does_not_freeze_probability_thresholds() -> None:
    for difficulty_class in (
        "TOO_EASY",
        "LEARNABLE_FRONTIER",
        "HARD_FRONTIER",
        "CURRENTLY_UNPRODUCTIVE",
        "INVALID",
    ):
        value = fixture()
        value["difficulty_class"] = difficulty_class
        value["estimated_solve_probability"] = 0.5
        assert not errors(value), difficulty_class


def test_b020_non_finite_probability_fails_closed() -> None:
    value = fixture()
    value["estimated_solve_probability"] = math.nan
    assert any("must be finite" in item for item in errors(value))


def test_b020_machine_readable_entry_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B020-difficulty-contract.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B020" in evidence
    assert "ENTRY_GATE_CANONICAL_MAIN = ef90e96ba3d4e2c253987d1d104e0de26ce93529" in evidence
    assert "ENTRY_GATE_RUN = 33198484632" in evidence
    assert "ENTRY_GATE_JOB = 98941644785" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B020_CALIBRATION_EXECUTION = NONE" in evidence
    assert "B021_FRONTIER_SAMPLER_EXECUTION = NONE" in evidence
'''
write("tests/contract/test_difficulty_calibration_contract.py", contract_test)

evidence = f'''# B020 — Checkpoint-Relative Difficulty Calibration Contract Evidence

**Task:** `B020`
**State:** `IMPLEMENTATION_ACTIVE`
**Contract:** `mstr.difficulty-calibration.v0`
**Canonical entry main:** `{ENTRY_MAIN}`

## Canonical Entry Provenance

```text
ENTRY_GATE_TASK = B020
ENTRY_GATE_CANONICAL_MAIN = {ENTRY_MAIN}
ENTRY_GATE_RUN = {ENTRY_RUN}
ENTRY_GATE_JOB = {ENTRY_JOB}
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

The entry run proved B020 `eligible=true` / `PENDING` on exact canonical main with no external authority required, canonical task drift clean, B011 still blocked by unsatisfied founder authority, and B021 still ineligible pending B020.

## Frozen Contract Semantics

`DifficultyCalibrationRecord` is checkpoint-relative. Every record binds the exact student model/checkpoint identity together with the exact harness profile and sampling identity used by the calibration evidence.

The contract freezes the canonical fields and five classes:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

Attempt accounting fails closed: `success_count` cannot exceed `attempt_count`, duplicate failure classes are rejected, and the failure-distribution counts must exactly cover `attempt_count - success_count`.

`estimated_solve_probability` is a finite value in `[0, 1]`, but B020 deliberately freezes **no probability threshold for any difficulty class**. The canonical plan reserves estimator behavior, frontier thresholds, refresh behavior, and sampling decisions for B021 fixture-only calibration/pilot evidence. This prevents a contract-only task from silently becoming training policy.

`structural_features` is a non-empty flat descriptor map. B020 records evidence shape only; it does not prescribe a learned feature extractor, execute a student model, or calibrate a real checkpoint.

## Cross-Contract Binding

B018 and B019 already consume `difficulty_record_identity` as a foreign-key-style evidence identity. B020 owns the canonical difficulty record shape behind that identity. A B020 record must bind its top-level `harness_profile_id` and `sampling_identity` exactly to the embedded student identity.

The design and runtime schemas are byte-identical:

```text
specs/002-code-model-supremacy-foundation/contracts/mstr-difficulty-calibration-v0.schema.json
schemas/mstr-difficulty-calibration-v0.schema.json
```

## Fixture Boundary

Fixtures are repository-owned synthetic records. They exercise structural and semantic validation only. They do not represent model execution, a real student checkpoint run, real benchmark measurements, or training-data admission.

## Authority

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
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
B020_CONTRACT_AUTHORITY = DIFFICULTY_CALIBRATION_RECORD_SHAPE_ONLY
B020_CALIBRATION_EXECUTION = NONE
B021_FRONTIER_SAMPLER_EXECUTION = NONE
```
'''
write("evidence/mstr-000b/B020-difficulty-contract.md", evidence)
