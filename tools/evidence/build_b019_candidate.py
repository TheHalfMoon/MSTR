from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()


def path(relative: str) -> Path:
    return ROOT / relative


def write(relative: str, text: str) -> None:
    target = path(relative)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def write_json(relative: str, value: object) -> None:
    write(relative, json.dumps(value, indent=2, sort_keys=True) + "\n")


def replace_once(relative: str, old: str, new: str) -> None:
    target = path(relative)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"expected one replacement in {relative}; found {count}: {old!r}"
        )
    target.write_text(text.replace(old, new), encoding="utf-8")


string_id = {"type": "string", "minLength": 1, "maxLength": 512}
contamination = {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]}
schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-teacher-rescue-record-v0.json",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "student_model_identity": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "model_id": string_id,
                "checkpoint_id": string_id,
                "harness_profile_id": string_id,
                "sampling_identity": string_id,
            },
            "required": [
                "model_id",
                "checkpoint_id",
                "harness_profile_id",
                "sampling_identity",
            ],
        },
        "provenance": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source_identity": string_id,
                "source_revision": string_id,
                "lineage_status": {
                    "enum": ["COMPLETE", "INCOMPLETE", "UNRESOLVED"]
                },
            },
            "required": ["source_identity", "source_revision", "lineage_status"],
        },
        "rights": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "license_or_terms_identity": string_id,
                "decision": {
                    "enum": ["COMPATIBLE", "INCOMPATIBLE", "UNRESOLVED"]
                },
            },
            "required": ["license_or_terms_identity", "decision"],
        },
        "teacher_output": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output_id": string_id,
                "output_kind": {
                    "enum": ["SOLUTION", "TEST", "REVIEW", "REFERENCE"]
                },
                "content_identity": string_id,
                "contamination_status": contamination,
                "execution_required": {"type": "boolean"},
            },
            "required": [
                "output_id",
                "output_kind",
                "content_identity",
                "contamination_status",
                "execution_required",
            ],
        },
        "provenance_binding": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output_id": string_id,
                "provenance": {"$ref": "#/$defs/provenance"},
            },
            "required": ["output_id", "provenance"],
        },
        "rights_binding": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output_id": string_id,
                "rights_decision": {"$ref": "#/$defs/rights"},
            },
            "required": ["output_id", "rights_decision"],
        },
        "execution_binding": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "output_id": string_id,
                "environment_identity": string_id,
                "sandboxed": {"type": "boolean"},
                "result": {"enum": ["PASS", "FAIL", "ERROR"]},
                "evidence_identity": string_id,
            },
            "required": [
                "output_id",
                "environment_identity",
                "sandboxed",
                "result",
                "evidence_identity",
            ],
        },
    },
    "properties": {
        "schema_version": {"const": "mstr.teacher-rescue-record.v0"},
        "rescue_id": string_id,
        "task_identity": string_id,
        "student_failure_evidence": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "failure_evidence_identity": string_id,
                "student_model_identity": {"$ref": "#/$defs/student_model_identity"},
                "attempt_count": {"type": "integer", "minimum": 1},
                "failure_class": {
                    "enum": [
                        "UNSOLVED",
                        "VERIFIER_REJECTED",
                        "TIMEOUT",
                        "ERROR",
                        "FRONTIER_RESCUE_REQUESTED",
                    ]
                },
                "difficulty_record_identity": string_id,
            },
            "required": [
                "failure_evidence_identity",
                "student_model_identity",
                "attempt_count",
                "failure_class",
                "difficulty_record_identity",
            ],
        },
        "teacher_identity": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "teacher_id": string_id,
                "provider_identity": string_id,
                "model_or_service_id": string_id,
                "revision_or_version": string_id,
                "access_mode": {
                    "enum": ["REFERENCE_ONLY", "LOCAL_MODEL", "REMOTE_API"]
                },
            },
            "required": [
                "teacher_id",
                "provider_identity",
                "model_or_service_id",
                "revision_or_version",
                "access_mode",
            ],
        },
        "teacher_terms_identity": string_id,
        "cost_record": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "cost_record_identity": string_id,
                "currency": {"const": "USD"},
                "paid_cost_usd": {"type": "number", "minimum": 0},
                "network_used": {"type": "boolean"},
                "model_execution_occurred": {"type": "boolean"},
                "external_effect_authority_identity": {
                    "anyOf": [string_id, {"type": "null"}]
                },
            },
            "required": [
                "cost_record_identity",
                "currency",
                "paid_cost_usd",
                "network_used",
                "model_execution_occurred",
                "external_effect_authority_identity",
            ],
        },
        "teacher_outputs": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/teacher_output"},
        },
        "output_provenance": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"$ref": "#/$defs/provenance_binding"},
        },
        "output_rights_decisions": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"$ref": "#/$defs/rights_binding"},
        },
        "contamination_status": contamination,
        "independent_execution_results": {
            "type": "array",
            "uniqueItems": True,
            "items": {"$ref": "#/$defs/execution_binding"},
        },
        "verifier_health": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "verifier_health_record_identity": string_id,
                "verifier_identity": string_id,
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
                "independence": {
                    "enum": ["INDEPENDENT", "NOT_INDEPENDENT", "UNRESOLVED"]
                },
                "teacher_output_sole_authority": {"type": "boolean"},
            },
            "required": [
                "verifier_health_record_identity",
                "verifier_identity",
                "health_class",
                "independence",
                "teacher_output_sole_authority",
            ],
        },
        "admission_decision": {"enum": ["ADMIT", "REJECT"]},
        "admission_reasons": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1, "maxLength": 1024},
        },
    },
    "required": [
        "schema_version",
        "rescue_id",
        "task_identity",
        "student_failure_evidence",
        "teacher_identity",
        "teacher_terms_identity",
        "cost_record",
        "teacher_outputs",
        "output_provenance",
        "output_rights_decisions",
        "contamination_status",
        "independent_execution_results",
        "verifier_health",
        "admission_decision",
        "admission_reasons",
    ],
    "allOf": [
        {
            "if": {
                "properties": {"admission_decision": {"const": "ADMIT"}},
                "required": ["admission_decision"],
            },
            "then": {
                "properties": {
                    "admission_reasons": {"maxItems": 0},
                    "contamination_status": {"const": "CLEAR"},
                    "teacher_outputs": {
                        "items": {
                            "properties": {
                                "contamination_status": {"const": "CLEAR"}
                            }
                        }
                    },
                    "output_provenance": {
                        "items": {
                            "properties": {
                                "provenance": {
                                    "properties": {
                                        "lineage_status": {"const": "COMPLETE"}
                                    }
                                }
                            }
                        }
                    },
                    "output_rights_decisions": {
                        "items": {
                            "properties": {
                                "rights_decision": {
                                    "properties": {
                                        "decision": {"const": "COMPATIBLE"}
                                    }
                                }
                            }
                        }
                    },
                    "independent_execution_results": {
                        "items": {
                            "properties": {
                                "sandboxed": {"const": True},
                                "result": {"const": "PASS"},
                            }
                        }
                    },
                    "verifier_health": {
                        "properties": {
                            "health_class": {"const": "HEALTHY"},
                            "independence": {"const": "INDEPENDENT"},
                            "teacher_output_sole_authority": {"const": False},
                        }
                    },
                }
            },
        },
        {
            "if": {
                "properties": {"admission_decision": {"const": "REJECT"}},
                "required": ["admission_decision"],
            },
            "then": {"properties": {"admission_reasons": {"minItems": 1}}},
        },
    ],
}

runtime_schema = "schemas/mstr-teacher-rescue-record-v0.schema.json"
design_schema = (
    "specs/002-code-model-supremacy-foundation/contracts/"
    "mstr-teacher-rescue-record-v0.schema.json"
)
write_json(runtime_schema, schema)
write_json(design_schema, schema)

valid = {
    "schema_version": "mstr.teacher-rescue-record.v0",
    "rescue_id": "b019-fixture-rescue-001",
    "task_identity": "fixture-task-frontier-001",
    "student_failure_evidence": {
        "failure_evidence_identity": "fixture-student-failure-001",
        "student_model_identity": {
            "model_id": "fixture/student-model",
            "checkpoint_id": "fixture-checkpoint-001",
            "harness_profile_id": "fixture-harness-v0",
            "sampling_identity": "fixture-sampling-v0",
        },
        "attempt_count": 2,
        "failure_class": "FRONTIER_RESCUE_REQUESTED",
        "difficulty_record_identity": "fixture-difficulty-record-001",
    },
    "teacher_identity": {
        "teacher_id": "fixture-reference-teacher-001",
        "provider_identity": "repository-owned-fixture",
        "model_or_service_id": "fixture/reference-only",
        "revision_or_version": "fixture-v1",
        "access_mode": "REFERENCE_ONLY",
    },
    "teacher_terms_identity": "fixture-terms-compatible-v1",
    "cost_record": {
        "cost_record_identity": "fixture-cost-zero-001",
        "currency": "USD",
        "paid_cost_usd": 0,
        "network_used": False,
        "model_execution_occurred": False,
        "external_effect_authority_identity": None,
    },
    "teacher_outputs": [
        {
            "output_id": "teacher-output-solution-001",
            "output_kind": "SOLUTION",
            "content_identity": "sha256:fixture-solution-001",
            "contamination_status": "CLEAR",
            "execution_required": True,
        }
    ],
    "output_provenance": [
        {
            "output_id": "teacher-output-solution-001",
            "provenance": {
                "source_identity": "repository-owned-fixture",
                "source_revision": "fixture-v1",
                "lineage_status": "COMPLETE",
            },
        }
    ],
    "output_rights_decisions": [
        {
            "output_id": "teacher-output-solution-001",
            "rights_decision": {
                "license_or_terms_identity": "fixture-terms-compatible-v1",
                "decision": "COMPATIBLE",
            },
        }
    ],
    "contamination_status": "CLEAR",
    "independent_execution_results": [
        {
            "output_id": "teacher-output-solution-001",
            "environment_identity": "fixture-sandbox-env-v1",
            "sandboxed": True,
            "result": "PASS",
            "evidence_identity": "fixture-execution-evidence-001",
        }
    ],
    "verifier_health": {
        "verifier_health_record_identity": "fixture-verifier-health-001",
        "verifier_identity": "fixture-independent-verifier-v1",
        "health_class": "HEALTHY",
        "independence": "INDEPENDENT",
        "teacher_output_sole_authority": False,
    },
    "admission_decision": "ADMIT",
    "admission_reasons": [],
}
invalid = json.loads(json.dumps(valid))
invalid["output_rights_decisions"][0]["rights_decision"]["decision"] = "UNRESOLVED"
write_json("tests/fixtures/schemas/valid/mstr-teacher-rescue-record-v0.json", valid)
write_json("tests/fixtures/schemas/invalid/mstr-teacher-rescue-record-v0.json", invalid)

policy = """# MSTR Teacher Rescue Policy v0

**Task:** `B019`  
**Contract:** `mstr.teacher-rescue-record.v0`  
**Status:** IMPLEMENTATION_CANDIDATE

## Purpose

Teacher rescue is an optional, bounded frontier-rescue/reference path. A teacher is never a truth authority. B019 freezes evidence and admission semantics only; it does not call a teacher, execute a model, spend money, ingest a corpus, or authorize training.

## Trigger Boundary

A rescue record requires exact student failure evidence and an externally supplied `difficulty_record_identity`. B019 may bind that identity but MUST NOT create or calibrate difficulty; B020 owns checkpoint-relative difficulty calibration.

```text
STUDENT_FAILURE_EVIDENCE
+ DIFFICULTY_RECORD_IDENTITY
-> OPTIONAL_TEACHER_REFERENCE_OR_FUTURE_AUTHORIZED_RESCUE
-> CONCRETE_OUTPUT_PROVENANCE
-> CONCRETE_OUTPUT_RIGHTS
-> CONTAMINATION_CHECK
-> INDEPENDENT_EXECUTION_WHERE_REQUIRED
-> VERIFIER_HEALTH_IDENTITY
-> ADMIT | REJECT
```

## Required Evidence

Every record binds:

- exact task identity;
- exact student/checkpoint/harness/sampling failure identity;
- teacher identity and teacher terms identity;
- explicit cost/network/model-execution facts;
- every concrete teacher output identity;
- per-output provenance;
- per-output rights decision;
- contamination state;
- independent execution evidence for every execution-required output;
- verifier-health identity and independence state;
- deterministic admission decision and reasons.

Teacher identity or provider terms do not substitute for concrete-output rights. Output provenance/rights arrays must exactly cover all teacher outputs. Independent execution evidence must exactly cover outputs marked `execution_required=true`.

## Fail-Closed Admission

`ADMIT` requires all of the following:

```text
ALL_OUTPUT_PROVENANCE = COMPLETE
ALL_OUTPUT_RIGHTS = COMPATIBLE
CONTAMINATION = CLEAR
ALL_OUTPUT_CONTAMINATION = CLEAR
ALL_REQUIRED_EXECUTION = PASS + SANDBOXED
VERIFIER_HEALTH = HEALTHY
VERIFIER_INDEPENDENCE = INDEPENDENT
TEACHER_OUTPUT_SOLE_AUTHORITY = FALSE
ADMISSION_REASONS = []
```

Any unresolved/incompatible right, incomplete/unresolved provenance, contamination, missing execution evidence, failed execution, weak/unresolved verifier independence, or teacher-self-confirmation rejects clean-positive admission.

## External-Effect Authority

The contract may represent a future separately authorized teacher execution. It never creates that authority. If a record reports any paid cost, network use, or teacher-model execution, it MUST bind a non-null `external_effect_authority_identity` referencing already-canonical authority with the relevant scope/cost/network ceiling.

For `REFERENCE_ONLY`, paid cost, network use, and model execution must all be false/zero and the external-effect authority identity must be null.

```text
PAID_OR_API_TEACHER_AUTHORIZED_BY_B019 = FALSE
MODEL_EXECUTION_AUTHORIZED_BY_B019 = FALSE
NETWORK_TEACHER_CALL_AUTHORIZED_BY_B019 = FALSE
```

## Cross-Contract Authority

B019 consumes identities without stealing downstream authority:

```text
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
```

B022/B023 own verifier-health certification/evaluation semantics. B019 stores the health identity and fail-closed admission posture only.

## Non-Authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
```
"""
write("docs/data/TEACHER_RESCUE_POLICY.md", policy)

evidence = """# B019 — Bounded Teacher-Rescue Policy Evidence

**Task:** `B019`  
**State:** IMPLEMENTATION_CANDIDATE  
**Contract:** `mstr.teacher-rescue-record.v0`  
**Canonical entry main:** `2605846607fc98291ded4e53e9bb6bb6c3cf52a0`

## Entry Gate

B018 is `COMPLETE_CANONICAL`. Exact-main post-closeout run `33190906137` proved B019 `eligible=true`, `PENDING`, with no external-effect authority required; task drift was clean and B011 remained blocked.

## Frozen Semantics

The B019 candidate freezes a bounded teacher-rescue record that binds student failure, teacher/terms identity, concrete-output provenance and rights, contamination, execution-required output evidence, verifier-health identity, cost/network/model-execution facts, and admission.

Teacher identity is not truth. Teacher terms are not concrete-output rights. Missing/unresolved provenance, rights, contamination, required execution, or verifier independence fails closed.

B019 binds an external `difficulty_record_identity` only; it does not calibrate difficulty. It consumes verifier-health identity only; it does not certify verifier health.

## Fixture Boundary

Fixtures are repository-owned synthetic records. The valid fixture uses `REFERENCE_ONLY`, USD 0.00, no network, and no teacher-model execution. Its execution result is fixture evidence representing independent sandbox verification of a concrete output; this task performs no model or teacher execution.

## Authority

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE
B022_VERIFIER_HEALTH_AUTHORITY = NONE
```
"""
write("evidence/mstr-000b/B019-teacher-policy.md", evidence)

replace_once(
    "src/mstr_qualify/schemas.py",
    '    "mstr-self-alignment-generation-v0": "mstr-self-alignment-generation-v0.schema.json",\n',
    '    "mstr-self-alignment-generation-v0": "mstr-self-alignment-generation-v0.schema.json",\n'
    '    # MSTR-000B B019: bounded teacher-rescue record contract.\n'
    '    "mstr-teacher-rescue-record-v0": "mstr-teacher-rescue-record-v0.schema.json",\n',
)

semantic = r'''

def _teacher_rescue_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B019 output bindings and external-effect authority semantics."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    outputs: dict[str, dict[str, Any]] = {}
    raw_outputs = instance.get("teacher_outputs")
    if isinstance(raw_outputs, list):
        for index, output in enumerate(raw_outputs):
            if not isinstance(output, dict):
                continue
            output_id = output.get("output_id")
            if not isinstance(output_id, str):
                continue
            if output_id in outputs:
                errors.append(
                    f"$.teacher_outputs[{index}]: duplicate output_id {output_id!r}"
                )
                continue
            outputs[output_id] = output

    def collect_bindings(field: str) -> dict[str, dict[str, Any]]:
        bindings: dict[str, dict[str, Any]] = {}
        raw = instance.get(field)
        if not isinstance(raw, list):
            return bindings
        for index, binding in enumerate(raw):
            if not isinstance(binding, dict):
                continue
            output_id = binding.get("output_id")
            if not isinstance(output_id, str):
                continue
            if output_id in bindings:
                errors.append(
                    f"$.{field}[{index}]: duplicate output binding {output_id!r}"
                )
                continue
            bindings[output_id] = binding
        return bindings

    for field in ("output_provenance", "output_rights_decisions"):
        bindings = collect_bindings(field)
        if set(bindings) != set(outputs):
            errors.append(f"$.{field}: bindings must exactly cover teacher output ids")

    expected_execution = {
        output_id
        for output_id, output in outputs.items()
        if output.get("execution_required") is True
    }
    execution_bindings = collect_bindings("independent_execution_results")
    if set(execution_bindings) != expected_execution:
        errors.append(
            "$.independent_execution_results: bindings must exactly cover "
            "execution-required teacher output ids"
        )

    cost = instance.get("cost_record")
    teacher = instance.get("teacher_identity")
    if isinstance(cost, dict):
        paid = cost.get("paid_cost_usd")
        network_used = cost.get("network_used") is True
        model_executed = cost.get("model_execution_occurred") is True
        authority = cost.get("external_effect_authority_identity")
        external_effect = (
            isinstance(paid, (int, float)) and not isinstance(paid, bool) and paid > 0
        ) or network_used or model_executed
        if external_effect and not isinstance(authority, str):
            errors.append(
                "$.cost_record.external_effect_authority_identity: required when "
                "paid cost, network use, or model execution is recorded"
            )
        if not external_effect and authority is not None:
            errors.append(
                "$.cost_record.external_effect_authority_identity: must be null when "
                "no external effect is recorded"
            )
        if isinstance(teacher, dict):
            access_mode = teacher.get("access_mode")
            if access_mode == "REFERENCE_ONLY" and external_effect:
                errors.append(
                    "$.teacher_identity.access_mode: REFERENCE_ONLY cannot record "
                    "paid cost, network use, or model execution"
                )
            if access_mode == "REMOTE_API" and not (network_used and model_executed):
                errors.append(
                    "$.teacher_identity.access_mode: REMOTE_API requires recorded "
                    "network use and model execution"
                )
            if access_mode == "LOCAL_MODEL" and not model_executed:
                errors.append(
                    "$.teacher_identity.access_mode: LOCAL_MODEL requires recorded "
                    "model execution"
                )

    return tuple(sorted(errors))
'''
schemas_file = path("src/mstr_qualify/schemas.py")
schemas_text = schemas_file.read_text(encoding="utf-8")
marker = "\ndef validation_errors(\n"
if schemas_text.count(marker) != 1:
    raise SystemExit("validation_errors marker mismatch")
schemas_text = schemas_text.replace(marker, semantic + marker)
old_hook = (
    '    if name == "mstr-self-alignment-generation-v0":\n'
    '        formatted.extend(_self_alignment_semantic_errors(instance))\n'
)
new_hook = old_hook + (
    '    if name == "mstr-teacher-rescue-record-v0":\n'
    '        formatted.extend(_teacher_rescue_semantic_errors(instance))\n'
)
if schemas_text.count(old_hook) != 1:
    raise SystemExit("self-alignment semantic hook mismatch")
schemas_file.write_text(schemas_text.replace(old_hook, new_hook), encoding="utf-8")

replace_once(
    "src/mstr_qualify/cli.py",
    '    "mstr.self-alignment-generation.v0": "mstr-self-alignment-generation-v0",\n',
    '    "mstr.self-alignment-generation.v0": "mstr-self-alignment-generation-v0",\n'
    '    # MSTR-000B B019 bounded teacher-rescue contract.\n'
    '    "mstr.teacher-rescue-record.v0": "mstr-teacher-rescue-record-v0",\n',
)

override_anchor = '''    "mstr-self-alignment-generation-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-self-alignment-generation-v0.schema.json"
    ),
'''
override_new = override_anchor + '''    "mstr-teacher-rescue-record-v0": (
        ROOT
        / "specs"
        / "002-code-model-supremacy-foundation"
        / "contracts"
        / "mstr-teacher-rescue-record-v0.schema.json"
    ),
'''
replace_once("tests/contract/test_schemas.py", override_anchor, override_new)

replace_once(
    "tests/integration/test_cli_offline.py",
    '        "mstr-self-alignment-generation-v0",\n',
    '        "mstr-self-alignment-generation-v0",\n'
    '        "mstr-teacher-rescue-record-v0",\n',
)

test_text = r'''from __future__ import annotations

import copy
import json
from pathlib import Path

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-teacher-rescue-record-v0.json"
)
INVALID = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "invalid"
    / "mstr-teacher-rescue-record-v0.json"
)


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def errors(value: object) -> tuple[str, ...]:
    return validation_errors("mstr-teacher-rescue-record-v0", value)


def test_b019_valid_fixture_passes() -> None:
    validate_instance("mstr-teacher-rescue-record-v0", fixture())


def test_b019_invalid_unresolved_output_rights_fails_closed() -> None:
    assert errors(json.loads(INVALID.read_text(encoding="utf-8")))


def test_b019_provenance_must_exactly_cover_outputs() -> None:
    value = fixture()
    value["output_provenance"] = []
    assert any("exactly cover teacher output ids" in item for item in errors(value))


def test_b019_rights_must_exactly_cover_outputs() -> None:
    value = fixture()
    value["output_rights_decisions"] = []
    assert any("exactly cover teacher output ids" in item for item in errors(value))


def test_b019_duplicate_output_id_fails_closed() -> None:
    value = fixture()
    value["teacher_outputs"].append(copy.deepcopy(value["teacher_outputs"][0]))
    assert any("duplicate output_id" in item for item in errors(value))


def test_b019_required_execution_must_be_independently_bound() -> None:
    value = fixture()
    value["independent_execution_results"] = []
    assert any("execution-required teacher output ids" in item for item in errors(value))


def test_b019_admit_rejects_failed_execution() -> None:
    value = fixture()
    value["independent_execution_results"][0]["result"] = "FAIL"
    assert errors(value)


def test_b019_admit_rejects_non_sandboxed_execution() -> None:
    value = fixture()
    value["independent_execution_results"][0]["sandboxed"] = False
    assert errors(value)


def test_b019_admit_rejects_contamination() -> None:
    value = fixture()
    value["teacher_outputs"][0]["contamination_status"] = "DETECTED"
    assert errors(value)


def test_b019_admit_requires_healthy_independent_verifier() -> None:
    for field, invalid in (
        ("health_class", "PARTIAL"),
        ("independence", "UNRESOLVED"),
        ("teacher_output_sole_authority", True),
    ):
        value = fixture()
        value["verifier_health"][field] = invalid
        assert errors(value)


def test_b019_reject_requires_reason() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    assert errors(value)


def test_b019_external_effect_requires_existing_authority_identity() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "REMOTE_API"
    value["cost_record"]["network_used"] = True
    value["cost_record"]["model_execution_occurred"] = True
    assert any("external_effect_authority_identity" in item for item in errors(value))


def test_b019_reference_only_cannot_claim_external_effect() -> None:
    value = fixture()
    value["cost_record"]["paid_cost_usd"] = 0.01
    value["cost_record"]["external_effect_authority_identity"] = "authority-fixture"
    assert any("REFERENCE_ONLY" in item for item in errors(value))


def test_b019_remote_api_record_requires_network_and_execution_facts() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "REMOTE_API"
    assert any("REMOTE_API" in item for item in errors(value))


def test_b019_local_model_record_requires_model_execution_fact() -> None:
    value = fixture()
    value["teacher_identity"]["access_mode"] = "LOCAL_MODEL"
    assert any("LOCAL_MODEL" in item for item in errors(value))


def test_b019_zero_effect_record_rejects_spurious_authority_identity() -> None:
    value = fixture()
    value["cost_record"]["external_effect_authority_identity"] = "stale-authority"
    assert any("must be null" in item for item in errors(value))


def test_b019_difficulty_and_verifier_authority_remain_external() -> None:
    policy = (ROOT / "docs" / "data" / "TEACHER_RESCUE_POLICY.md").read_text(
        encoding="utf-8"
    )
    evidence = (
        ROOT / "evidence" / "mstr-000b" / "B019-teacher-policy.md"
    ).read_text(encoding="utf-8")
    for text in (policy, evidence):
        assert "B020_DIFFICULTY_CALIBRATION_AUTHORITY = NONE" in text
        assert "B022_VERIFIER_HEALTH_AUTHORITY = NONE" in text
        assert "MODEL_EXECUTION = NONE" in text
        assert "PAID_MODEL_API = NONE" in text
        assert "WEIGHT_CHANGING_TRAINING = NONE" in text
'''
write("tests/contract/test_teacher_rescue_contract.py", test_text)
