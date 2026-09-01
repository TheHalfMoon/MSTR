from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path.cwd()
BASE_SHA = "1ffa71c94bda161ec7be7784de3a6a4be81570ad"
ENTRY_RUN = "33535987808"
ENTRY_JOB = "99950302502"


def write_text(path: str, content: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one anchor in {path}: {old!r}")
    target.write_text(text.replace(old, new), encoding="utf-8")


identity = {"type": "string", "minLength": 1, "maxLength": 512}
sha256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
clear_status = {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]}

schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-test-generation-example-v0.json",
    "title": "MSTR Test Generation Example v0",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "identity": identity,
        "sha256": sha256,
        "provenance": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source_class": {
                    "enum": [
                        "REPOSITORY_OWNED_FIXTURE",
                        "PUBLIC_SOURCE",
                        "SYNTHETIC_VERIFIED",
                        "STUDENT_GENERATED",
                        "TEACHER_GENERATED",
                    ]
                },
                "source_identity": {"$ref": "#/$defs/identity"},
                "source_revision": {"$ref": "#/$defs/identity"},
                "lineage_identity": {"$ref": "#/$defs/identity"},
                "generator_identity": {
                    "anyOf": [
                        {"$ref": "#/$defs/identity"},
                        {"type": "null"},
                    ]
                },
            },
            "required": [
                "source_class",
                "source_identity",
                "source_revision",
                "lineage_identity",
                "generator_identity",
            ],
        },
        "rights_decision": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "decision": {"enum": ["COMPATIBLE", "INCOMPATIBLE", "UNRESOLVED"]},
                "intended_use": {"const": "MSTR_TRAINING_OR_EVALUATION"},
                "terms_identity": {"$ref": "#/$defs/identity"},
                "reason_codes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/identity"},
                    "uniqueItems": True,
                },
            },
            "required": ["decision", "intended_use", "terms_identity", "reason_codes"],
        },
        "contamination_status": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "benchmark_overlap": copy.deepcopy(clear_status),
                "hidden_answer_exposure": copy.deepcopy(clear_status),
                "future_history_exposure": copy.deepcopy(clear_status),
                "cross_split_duplicate": copy.deepcopy(clear_status),
                "evidence_identity": {"$ref": "#/$defs/identity"},
            },
            "required": [
                "benchmark_overlap",
                "hidden_answer_exposure",
                "future_history_exposure",
                "cross_split_duplicate",
                "evidence_identity",
            ],
        },
        "execution_result": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "result_id": {"$ref": "#/$defs/identity"},
                "task_identity": {"$ref": "#/$defs/identity"},
                "revision": {"$ref": "#/$defs/identity"},
                "test_artifact_sha256": {"$ref": "#/$defs/sha256"},
                "status": {"enum": ["PASS", "FAIL", "ERROR", "NOT_RUN"]},
                "environment_identity": {"$ref": "#/$defs/identity"},
                "verifier_manifest_id": {"$ref": "#/$defs/identity"},
                "evidence_identity": {"$ref": "#/$defs/identity"},
            },
            "required": [
                "result_id",
                "task_identity",
                "revision",
                "test_artifact_sha256",
                "status",
                "environment_identity",
                "verifier_manifest_id",
                "evidence_identity",
            ],
        },
    },
    "properties": {
        "schema_version": {"const": "mstr.test-generation-example.v0"},
        "example_id": {"$ref": "#/$defs/identity"},
        "task_identity": {"$ref": "#/$defs/identity"},
        "base_revision": {"$ref": "#/$defs/identity"},
        "fix_revision": {"$ref": "#/$defs/identity"},
        "behavior_contract": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "behavior_id": {"$ref": "#/$defs/identity"},
                "description": {"$ref": "#/$defs/identity"},
                "test_classes": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "enum": [
                            "REPRODUCTION",
                            "TARGETED_REGRESSION",
                            "BOUNDARY_ERROR",
                            "PROPERTY",
                            "METAMORPHIC",
                        ]
                    },
                },
                "requires_reproduction": {"type": "boolean"},
                "property_or_metamorphic_applicable": {"type": "boolean"},
            },
            "required": [
                "behavior_id",
                "description",
                "test_classes",
                "requires_reproduction",
                "property_or_metamorphic_applicable",
            ],
        },
        "generated_test_patch": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "patch_sha256": {"$ref": "#/$defs/sha256"},
                "test_artifact_sha256": {"$ref": "#/$defs/sha256"},
                "changed_paths": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"$ref": "#/$defs/identity"},
                },
                "test_paths": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"$ref": "#/$defs/identity"},
                },
                "deleted_existing_test_paths": {
                    "type": "array",
                    "uniqueItems": True,
                    "items": {"$ref": "#/$defs/identity"},
                },
                "protected_path_changes": {
                    "type": "array",
                    "uniqueItems": True,
                    "items": {"$ref": "#/$defs/identity"},
                },
            },
            "required": [
                "patch_sha256",
                "test_artifact_sha256",
                "changed_paths",
                "test_paths",
                "deleted_existing_test_paths",
                "protected_path_changes",
            ],
        },
        "generated_test_provenance": {"$ref": "#/$defs/provenance"},
        "generated_test_rights_decision": {"$ref": "#/$defs/rights_decision"},
        "contamination_status": {"$ref": "#/$defs/contamination_status"},
        "behavioral_proof": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "proof_kind": {
                    "enum": ["FAIL_BEFORE_PASS_AFTER", "TASK_SPECIFIC_BEHAVIOR"]
                },
                "independent_acceptance_evidence_identity": {
                    "anyOf": [
                        {"$ref": "#/$defs/identity"},
                        {"type": "null"},
                    ]
                },
                "pre_fix_result": {"$ref": "#/$defs/execution_result"},
                "post_fix_result": {"$ref": "#/$defs/execution_result"},
            },
            "required": [
                "proof_kind",
                "independent_acceptance_evidence_identity",
                "pre_fix_result",
                "post_fix_result",
            ],
        },
        "integrity_checks": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "answer_encoding": copy.deepcopy(clear_status),
                "test_weakening": copy.deepcopy(clear_status),
                "evaluator_modification": copy.deepcopy(clear_status),
                "protected_path_status": {
                    "enum": ["INTACT", "TAMPERED", "UNRESOLVED"]
                },
            },
            "required": [
                "answer_encoding",
                "test_weakening",
                "evaluator_modification",
                "protected_path_status",
            ],
        },
        "mutation_strength": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "status": {"enum": ["ADEQUATE", "NOT_APPLICABLE", "WEAK", "UNRESOLVED"]},
                "evidence_identity": {
                    "anyOf": [
                        {"$ref": "#/$defs/identity"},
                        {"type": "null"},
                    ]
                },
                "mutants_evaluated": {"type": "integer", "minimum": 0},
                "mutants_killed": {"type": "integer", "minimum": 0},
            },
            "required": [
                "status",
                "evidence_identity",
                "mutants_evaluated",
                "mutants_killed",
            ],
        },
        "verifier_health_id": {"$ref": "#/$defs/identity"},
        "verifier_health_class": {
            "enum": ["HEALTHY", "PARTIAL", "DISAGREEMENT", "BROKEN", "LEAKED", "TAMPERED"]
        },
        "admission_decision": {"enum": ["ADMIT", "REJECT", "DIAGNOSTIC_ONLY"]},
        "admission_reasons": {
            "type": "array",
            "uniqueItems": True,
            "items": {"$ref": "#/$defs/identity"},
        },
    },
    "required": [
        "schema_version",
        "example_id",
        "task_identity",
        "base_revision",
        "fix_revision",
        "behavior_contract",
        "generated_test_patch",
        "generated_test_provenance",
        "generated_test_rights_decision",
        "contamination_status",
        "behavioral_proof",
        "integrity_checks",
        "mutation_strength",
        "verifier_health_id",
        "verifier_health_class",
        "admission_decision",
        "admission_reasons",
    ],
    "allOf": [
        {
            "if": {"properties": {"admission_decision": {"const": "ADMIT"}}, "required": ["admission_decision"]},
            "then": {
                "properties": {
                    "generated_test_rights_decision": {
                        "properties": {
                            "decision": {"const": "COMPATIBLE"},
                            "reason_codes": {"maxItems": 0},
                        }
                    },
                    "contamination_status": {
                        "properties": {
                            "benchmark_overlap": {"const": "CLEAR"},
                            "hidden_answer_exposure": {"const": "CLEAR"},
                            "future_history_exposure": {"const": "CLEAR"},
                            "cross_split_duplicate": {"const": "CLEAR"},
                        }
                    },
                    "generated_test_patch": {
                        "properties": {
                            "deleted_existing_test_paths": {"maxItems": 0},
                            "protected_path_changes": {"maxItems": 0},
                        }
                    },
                    "integrity_checks": {
                        "properties": {
                            "answer_encoding": {"const": "CLEAR"},
                            "test_weakening": {"const": "CLEAR"},
                            "evaluator_modification": {"const": "CLEAR"},
                            "protected_path_status": {"const": "INTACT"},
                        }
                    },
                    "mutation_strength": {
                        "properties": {
                            "status": {"enum": ["ADEQUATE", "NOT_APPLICABLE"]}
                        }
                    },
                    "verifier_health_class": {"const": "HEALTHY"},
                    "admission_reasons": {"maxItems": 0},
                }
            },
            "else": {"properties": {"admission_reasons": {"minItems": 1}}},
        },
        {
            "if": {
                "properties": {
                    "behavioral_proof": {
                        "properties": {"proof_kind": {"const": "FAIL_BEFORE_PASS_AFTER"}},
                        "required": ["proof_kind"],
                    }
                }
            },
            "then": {
                "properties": {
                    "behavioral_proof": {
                        "properties": {
                            "independent_acceptance_evidence_identity": {"type": "null"},
                            "pre_fix_result": {"properties": {"status": {"const": "FAIL"}}},
                            "post_fix_result": {"properties": {"status": {"const": "PASS"}}},
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "behavioral_proof": {
                        "properties": {"proof_kind": {"const": "TASK_SPECIFIC_BEHAVIOR"}},
                        "required": ["proof_kind"],
                    }
                }
            },
            "then": {
                "properties": {
                    "behavioral_proof": {
                        "properties": {
                            "independent_acceptance_evidence_identity": {"$ref": "#/$defs/identity"},
                            "post_fix_result": {"properties": {"status": {"const": "PASS"}}},
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "behavior_contract": {
                        "properties": {"requires_reproduction": {"const": True}},
                        "required": ["requires_reproduction"],
                    }
                }
            },
            "then": {
                "properties": {
                    "behavior_contract": {
                        "properties": {
                            "test_classes": {"contains": {"const": "REPRODUCTION"}}
                        }
                    }
                }
            },
        },
        {
            "if": {
                "properties": {
                    "behavior_contract": {
                        "properties": {"property_or_metamorphic_applicable": {"const": True}},
                        "required": ["property_or_metamorphic_applicable"],
                    }
                }
            },
            "then": {
                "properties": {
                    "behavior_contract": {
                        "properties": {
                            "test_classes": {
                                "contains": {"enum": ["PROPERTY", "METAMORPHIC"]}
                            }
                        }
                    }
                }
            },
        },
    ],
}

schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
write_text("schemas/mstr-test-generation-example-v0.schema.json", schema_text)
write_text(
    "specs/002-code-model-supremacy-foundation/contracts/mstr-test-generation-example-v0.schema.json",
    schema_text,
)

valid = {
    "schema_version": "mstr.test-generation-example.v0",
    "example_id": "b024-fixture-repro-regression",
    "task_identity": "fixture-task:config-export-bug",
    "base_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "fix_revision": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "behavior_contract": {
        "behavior_id": "config-export-empty-value",
        "description": "Export preserves an explicitly empty configuration value.",
        "test_classes": ["REPRODUCTION", "TARGETED_REGRESSION", "BOUNDARY_ERROR"],
        "requires_reproduction": True,
        "property_or_metamorphic_applicable": False,
    },
    "generated_test_patch": {
        "patch_sha256": "1" * 64,
        "test_artifact_sha256": "2" * 64,
        "changed_paths": ["tests/test_config_export.py"],
        "test_paths": ["tests/test_config_export.py"],
        "deleted_existing_test_paths": [],
        "protected_path_changes": [],
    },
    "generated_test_provenance": {
        "source_class": "REPOSITORY_OWNED_FIXTURE",
        "source_identity": "TheHalfMoon/MSTR:b024-fixture",
        "source_revision": BASE_SHA,
        "lineage_identity": "fixture-lineage:b024-test-generation-v1",
        "generator_identity": None,
    },
    "generated_test_rights_decision": {
        "decision": "COMPATIBLE",
        "intended_use": "MSTR_TRAINING_OR_EVALUATION",
        "terms_identity": "repository-owned-fixture-policy-v1",
        "reason_codes": [],
    },
    "contamination_status": {
        "benchmark_overlap": "CLEAR",
        "hidden_answer_exposure": "CLEAR",
        "future_history_exposure": "CLEAR",
        "cross_split_duplicate": "CLEAR",
        "evidence_identity": "fixture-contamination:b024-v1",
    },
    "behavioral_proof": {
        "proof_kind": "FAIL_BEFORE_PASS_AFTER",
        "independent_acceptance_evidence_identity": None,
        "pre_fix_result": {
            "result_id": "fixture-pre-fix",
            "task_identity": "fixture-task:config-export-bug",
            "revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "test_artifact_sha256": "2" * 64,
            "status": "FAIL",
            "environment_identity": "fixture-env:python-3.11-offline",
            "verifier_manifest_id": "fixture-verifier-manifest-v1",
            "evidence_identity": "fixture-evidence:pre-fix",
        },
        "post_fix_result": {
            "result_id": "fixture-post-fix",
            "task_identity": "fixture-task:config-export-bug",
            "revision": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "test_artifact_sha256": "2" * 64,
            "status": "PASS",
            "environment_identity": "fixture-env:python-3.11-offline",
            "verifier_manifest_id": "fixture-verifier-manifest-v1",
            "evidence_identity": "fixture-evidence:post-fix",
        },
    },
    "integrity_checks": {
        "answer_encoding": "CLEAR",
        "test_weakening": "CLEAR",
        "evaluator_modification": "CLEAR",
        "protected_path_status": "INTACT",
    },
    "mutation_strength": {
        "status": "NOT_APPLICABLE",
        "evidence_identity": None,
        "mutants_evaluated": 0,
        "mutants_killed": 0,
    },
    "verifier_health_id": "fixture-verifier-health:healthy-v1",
    "verifier_health_class": "HEALTHY",
    "admission_decision": "ADMIT",
    "admission_reasons": [],
}
invalid = copy.deepcopy(valid)
invalid["example_id"] = "b024-invalid-pass-before-pass-after"
invalid["behavioral_proof"]["pre_fix_result"]["status"] = "PASS"
write_text(
    "tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json",
    json.dumps(valid, indent=2, sort_keys=True),
)
write_text(
    "tests/fixtures/schemas/invalid/mstr-test-generation-example-v0.json",
    json.dumps(invalid, indent=2, sort_keys=True),
)

write_text(
    "docs/data/TEST_GENERATION_CURRICULUM.md",
    """# MSTR Test Generation Curriculum v0

**Task:** `B024`
**Contract:** `mstr.test-generation-example.v0`
**Status:** implementation candidate — not canonical until governed merge and closeout

## Purpose

This curriculum makes test generation a first-class software-building skill without allowing generated tests to certify themselves. An admitted example must bind the generated test artifact to exact provenance, rights, contamination, verifier-health, protected-path, and behavioral evidence. A green test command by itself is never sufficient.

B024 is contract-and-fixture work only. It does not generate tests with a model, execute an external verifier, ingest a corpus, access model weights, call a teacher/API, spend money, or authorize training.

## Required learning sequence

The default bug/repair sequence is:

```text
UNDERSTAND_EXPECTED_BEHAVIOR
-> CREATE_MINIMAL_REPRODUCTION
-> PROVE_CURRENT_FAILURE
-> IMPLEMENT_FIX
-> RUN_TARGETED_REGRESSION
-> EXPAND_BOUNDARY_PROPERTY_OR_METAMORPHIC_VERIFICATION_WHEN_RISK_JUSTIFIES_IT
-> PRESERVE_EXACT_TEST_ARTIFACT_IDENTITY_ACROSS_PRE_FIX_AND_POST_FIX_PROOF
```

The generated test is evidence only when the exact same test artifact is used for the before/after comparison.

## Test classes

Every example declares one or more semantic classes:

```text
REPRODUCTION
TARGETED_REGRESSION
BOUNDARY_ERROR
PROPERTY
METAMORPHIC
```

`requires_reproduction=true` requires `REPRODUCTION`. When property/metamorphic testing is applicable, at least one of `PROPERTY` or `METAMORPHIC` is required. These classes are semantic requirements, not file-name labels.

## Per-example integrity

Every `mstr.test-generation-example.v0` record binds:

- exact task identity, base revision, and fix revision;
- a behavior contract and declared test classes;
- generated test patch SHA-256 and test artifact SHA-256;
- changed/test paths plus any deleted-test or protected-path changes;
- generated-test provenance and immutable lineage;
- a concrete rights decision for MSTR training/evaluation use;
- benchmark/hidden-answer/future-history/cross-split contamination evidence;
- pre-fix and post-fix execution evidence;
- environment and verifier-manifest identity;
- answer-encoding, test-weakening, evaluator-modification, and protected-path checks;
- optional mutation-strength evidence;
- exact verifier-health identity and class;
- deterministic admission decision and reasons.

## Behavioral proof

### Default repair proof

`FAIL_BEFORE_PASS_AFTER` requires:

```text
PRE_FIX = FAIL
POST_FIX = PASS
SAME_TEST_ARTIFACT_SHA256 = true
SAME_ENVIRONMENT_IDENTITY = true
SAME_VERIFIER_MANIFEST_ID = true
PRE_FIX_REVISION = BASE_REVISION
POST_FIX_REVISION = FIX_REVISION
```

A test that passes before and after a claimed fix is not accepted under this proof mode.

### Task-specific proof

Some valid test-authoring work has no meaningful broken pre-fix state. `TASK_SPECIFIC_BEHAVIOR` is therefore allowed only when post-fix behavior passes and an independent acceptance-evidence identity is present. This exception cannot bypass rights, contamination, verifier health, protected paths, answer-encoding, or test-weakening gates.

## Fail-closed admission

`ADMIT` requires all of the following:

```text
RIGHTS_DECISION = COMPATIBLE
BENCHMARK_OVERLAP = CLEAR
HIDDEN_ANSWER_EXPOSURE = CLEAR
FUTURE_HISTORY_EXPOSURE = CLEAR
CROSS_SPLIT_DUPLICATE = CLEAR
VERIFIER_HEALTH_CLASS = HEALTHY
ANSWER_ENCODING = CLEAR
TEST_WEAKENING = CLEAR
EVALUATOR_MODIFICATION = CLEAR
PROTECTED_PATH_STATUS = INTACT
DELETED_EXISTING_TEST_PATHS = []
PROTECTED_PATH_CHANGES = []
MUTATION_STRENGTH = ADEQUATE | NOT_APPLICABLE
ADMISSION_REASONS = []
```

Any incompatible/unresolved right, contamination signal, unhealthy verifier, protected evaluator change, answer encoding, weakened/deleted tests, weak/unresolved mutation evidence, or invalid behavioral proof fails closed.

## Rejected shortcut patterns

The contract rejects clean-positive admission for examples that:

- hardcode or encode the expected answer into tests;
- delete or weaken existing tests to obtain green output;
- modify protected evaluator/verifier paths;
- use a different generated test before and after the fix;
- compare different execution environments or verifier manifests;
- claim a reproduction while never observing the pre-fix failure;
- pass both before and after under `FAIL_BEFORE_PASS_AFTER`;
- use task-specific proof without independent acceptance evidence;
- carry unresolved provenance, rights, contamination, or verifier health.

## Relationship to verifier health

B023 is canonical before B024 entry. B024 records an exact verifier-health identity/class but does not create a second health authority and does not execute the B023 evaluator. Downstream admission must consume canonical verifier-health evidence and may not infer `HEALTHY` from a passing test process alone.

## Non-authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
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
```

B024 freezes test-generation curriculum and acceptance semantics only. It never converts a generated test, passing command, fixture, or model output into project authority.
""",
)

write_text(
    "evidence/mstr-000b/B024-test-curriculum.md",
    f"""# B024 — Test Generation Curriculum Evidence

**Task:** `B024`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `{BASE_SHA}`
**Entry gate run:** `{ENTRY_RUN}`
**Entry gate job:** `{ENTRY_JOB}`

## Entry gate

Exact-main post-closeout validation proved B024 machine eligibility before material implementation.

```text
TASK = B024
CANONICAL_MAIN = {BASE_SHA}
TASK_DRIFT = clean
B023_STATE = COMPLETE_CANONICAL
B024_STATE = PENDING
B024_ELIGIBLE = true
B024_PREREQUISITE_B023 = satisfied
EXTERNAL_AUTHORITY_REQUIRED = false
B026 = blocked on B024
B011 = blocked on repository-specific external authority
```

Run `{ENTRY_RUN}` also re-proved the B023 closeout merge identity, exact provenance, full repository quality gates, B026 dependency ordering, and the unchanged B011 authority boundary.

## Contract frozen by this implementation candidate

```text
SCHEMA_VERSION = mstr.test-generation-example.v0
TEST_CLASSES = REPRODUCTION,TARGETED_REGRESSION,BOUNDARY_ERROR,PROPERTY,METAMORPHIC
DEFAULT_PROOF = FAIL_BEFORE_PASS_AFTER
TASK_SPECIFIC_PROOF_REQUIRES_INDEPENDENT_ACCEPTANCE_EVIDENCE = true
SAME_TEST_ARTIFACT_PRE_POST = required
SAME_ENVIRONMENT_PRE_POST = required
SAME_VERIFIER_MANIFEST_PRE_POST = required
ADMIT_REQUIRES_COMPATIBLE_RIGHTS = true
ADMIT_REQUIRES_CLEAR_CONTAMINATION = true
ADMIT_REQUIRES_HEALTHY_VERIFIER = true
ADMIT_REQUIRES_PROTECTED_PATH_INTEGRITY = true
ANSWER_ENCODING = prohibited
TEST_WEAKENING = prohibited
```

Runtime and design-source schemas are byte-identical. The valid repository-owned fixture demonstrates a reproduction/targeted/boundary test that fails on the base revision and passes on the fix revision with the exact same test artifact. The invalid fixture demonstrates that pass-before/pass-after cannot self-admit under the default repair proof.

## Scope boundary

This implementation intentionally does not:

- generate tests with any model;
- execute model inference or a teacher/API;
- execute an external verifier-health evaluator;
- ingest an external or large dataset;
- access model weights;
- mutate B024 canonical state or its task checkbox;
- authorize B026, B030, training, candidate-pool changes, or production release.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
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
B024_AUTHORITY = TEST_GENERATION_CONTRACT_AND_FIXTURES_ONLY
```

## Completion boundary

This is implementation evidence only. B024 remains `PENDING` and its checkbox remains open until governed implementation merge, post-merge verification, and a separate canonical closeout.
""",
)

semantic_function = '''\n\ndef _test_generation_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Enforce B024 cross-field behavioral and identity bindings."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    patch = instance.get("generated_test_patch")
    proof = instance.get("behavioral_proof")
    if isinstance(patch, dict) and isinstance(proof, dict):
        artifact_sha = patch.get("test_artifact_sha256")
        pre = proof.get("pre_fix_result")
        post = proof.get("post_fix_result")
        if isinstance(pre, dict) and isinstance(post, dict):
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

    behavior = instance.get("behavior_contract")
    if isinstance(behavior, dict):
        classes = behavior.get("test_classes")
        class_set = set(classes) if isinstance(classes, list) else set()
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

    return tuple(sorted(errors))
'''
replace_once(
    "src/mstr_qualify/schemas.py",
    "\ndef _trajectory_manifest_semantic_errors(instance: Any) -> tuple[str, ...]:\n",
    semantic_function + "\ndef _trajectory_manifest_semantic_errors(instance: Any) -> tuple[str, ...]:\n",
)
replace_once(
    "src/mstr_qualify/schemas.py",
    '    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.\n    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",\n',
    '    # MSTR-000B B024: test-generation example and acceptance contract.\n    "mstr-test-generation-example-v0": "mstr-test-generation-example-v0.schema.json",\n    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.\n    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",\n',
)
replace_once(
    "src/mstr_qualify/schemas.py",
    '    if name == "mstr-difficulty-calibration-v0":\n        formatted.extend(_difficulty_calibration_semantic_errors(instance))\n',
    '    if name == "mstr-difficulty-calibration-v0":\n        formatted.extend(_difficulty_calibration_semantic_errors(instance))\n    if name == "mstr-test-generation-example-v0":\n        formatted.extend(_test_generation_semantic_errors(instance))\n',
)
replace_once(
    "src/mstr_qualify/cli.py",
    '    # MSTR-000B B025 greenfield/feature/synthesis task manifest contract.\n    "mstr.greenfield-task.v0": "mstr-greenfield-task-v0",\n',
    '    # MSTR-000B B024 test-generation example and acceptance contract.\n    "mstr.test-generation-example.v0": "mstr-test-generation-example-v0",\n    # MSTR-000B B025 greenfield/feature/synthesis task manifest contract.\n    "mstr.greenfield-task.v0": "mstr-greenfield-task-v0",\n',
)
replace_once(
    "tests/contract/test_schemas.py",
    '    "mstr-greenfield-task-v0": (\n',
    '    "mstr-test-generation-example-v0": (\n        ROOT\n        / "specs"\n        / "002-code-model-supremacy-foundation"\n        / "contracts"\n        / "mstr-test-generation-example-v0.schema.json"\n    ),\n    "mstr-greenfield-task-v0": (\n',
)
replace_once(
    "tests/integration/test_cli_offline.py",
    '        "mstr-task-node-v0",\n        "mstr-teacher-rescue-record-v0",\n',
    '        "mstr-task-node-v0",\n        "mstr-test-generation-example-v0",\n        "mstr-teacher-rescue-record-v0",\n',
)
replace_once(
    "tests/integration/test_cli_offline.py",
    '\ndef test_validate_is_deterministic_across_runs(capsys: pytest.CaptureFixture[str]) -> None:\n',
    '''\ndef test_validate_explicit_b024_test_generation_fixture_passes(\n    capsys: pytest.CaptureFixture[str],\n) -> None:\n    path = (\n        Path(__file__).resolve().parents[2]\n        / "tests"\n        / "fixtures"\n        / "schemas"\n        / "valid"\n        / "mstr-test-generation-example-v0.json"\n    )\n    assert main(["validate", str(path)]) == 0\n    payload = parse_stdout(capsys)\n    assert payload["status"] == "pass"\n    assert payload["files"][0]["schema_version"] == "mstr.test-generation-example.v0"\n\n\ndef test_validate_is_deterministic_across_runs(capsys: pytest.CaptureFixture[str]) -> None:\n''',
)

write_text(
    "tests/contract/test_test_generation_example_contract.py",
    '''from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json"


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def test_b024_valid_reproduction_regression_fixture_passes() -> None:
    validate_instance("mstr-test-generation-example-v0", fixture())


@pytest.mark.parametrize("decision", ["INCOMPATIBLE", "UNRESOLVED"])
def test_b024_admit_fails_closed_on_rights(decision: str) -> None:
    value = fixture()
    value["generated_test_rights_decision"]["decision"] = decision
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    "field",
    [
        "benchmark_overlap",
        "hidden_answer_exposure",
        "future_history_exposure",
        "cross_split_duplicate",
    ],
)
def test_b024_admit_requires_clear_contamination(field: str) -> None:
    value = fixture()
    value["contamination_status"][field] = "UNRESOLVED"
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    ("field", "bad"),
    [
        ("answer_encoding", "DETECTED"),
        ("test_weakening", "DETECTED"),
        ("evaluator_modification", "DETECTED"),
        ("protected_path_status", "TAMPERED"),
    ],
)
def test_b024_admit_rejects_integrity_shortcuts(field: str, bad: str) -> None:
    value = fixture()
    value["integrity_checks"][field] = bad
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_admit_rejects_deleted_or_protected_test_changes() -> None:
    value = fixture()
    value["generated_test_patch"]["deleted_existing_test_paths"] = ["tests/old_test.py"]
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["generated_test_patch"]["protected_path_changes"] = ["tests/hidden_oracle.py"]
    assert validation_errors("mstr-test-generation-example-v0", value)


@pytest.mark.parametrize(
    "health",
    ["PARTIAL", "DISAGREEMENT", "BROKEN", "LEAKED", "TAMPERED"],
)
def test_b024_clean_admit_requires_healthy_verifier(health: str) -> None:
    value = fixture()
    value["verifier_health_class"] = health
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_default_repair_proof_requires_fail_before_pass_after() -> None:
    value = fixture()
    value["behavioral_proof"]["pre_fix_result"]["status"] = "PASS"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["status"] = "FAIL"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_same_test_artifact_is_required_pre_and_post() -> None:
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["test_artifact_sha256"] = "3" * 64
    errors = validation_errors("mstr-test-generation-example-v0", value)
    assert any("must match generated_test_patch.test_artifact_sha256" in error for error in errors)


def test_b024_pre_post_revision_identity_is_bound() -> None:
    value = fixture()
    value["behavioral_proof"]["pre_fix_result"]["revision"] = "wrong-base"
    assert any(
        "must match base_revision" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["revision"] = "wrong-fix"
    assert any(
        "must match fix_revision" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_pre_post_environment_and_verifier_must_match() -> None:
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["environment_identity"] = "other-env"
    assert any(
        "environment_identity must match" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )
    value = fixture()
    value["behavioral_proof"]["post_fix_result"]["verifier_manifest_id"] = "other-verifier"
    assert any(
        "verifier_manifest_id must match" in error
        for error in validation_errors("mstr-test-generation-example-v0", value)
    )


def test_b024_reproduction_requirement_is_semantically_bound() -> None:
    value = fixture()
    value["behavior_contract"]["test_classes"] = ["TARGETED_REGRESSION"]
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_property_or_metamorphic_requirement_is_semantically_bound() -> None:
    value = fixture()
    value["behavior_contract"]["property_or_metamorphic_applicable"] = True
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["behavior_contract"]["test_classes"].append("PROPERTY")
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_task_specific_proof_requires_independent_evidence() -> None:
    value = fixture()
    value["behavioral_proof"]["proof_kind"] = "TASK_SPECIFIC_BEHAVIOR"
    value["behavioral_proof"]["pre_fix_result"]["status"] = "PASS"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["behavioral_proof"]["independent_acceptance_evidence_identity"] = (
        "fixture-independent-acceptance-v1"
    )
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_mutation_accounting_and_strength_fail_closed() -> None:
    value = fixture()
    value["mutation_strength"] = {
        "status": "ADEQUATE",
        "evidence_identity": "fixture-mutation-v1",
        "mutants_evaluated": 2,
        "mutants_killed": 3,
    }
    assert validation_errors("mstr-test-generation-example-v0", value)
    value = fixture()
    value["mutation_strength"]["status"] = "WEAK"
    assert validation_errors("mstr-test-generation-example-v0", value)


def test_b024_rejected_records_require_reasons() -> None:
    value = fixture()
    value["admission_decision"] = "REJECT"
    assert validation_errors("mstr-test-generation-example-v0", value)
    value["admission_reasons"] = ["fixture.reject"]
    validate_instance("mstr-test-generation-example-v0", value)


def test_b024_schema_has_no_remote_reference() -> None:
    schema = json.loads(
        (ROOT / "schemas/mstr-test-generation-example-v0.schema.json").read_text(
            encoding="utf-8"
        )
    )
    encoded = json.dumps(schema, sort_keys=True)
    assert "http" not in encoded.replace(
        "https://json-schema.org/draft/2020-12/schema", ""
    ).replace("https://mstr.local/schemas/mstr-test-generation-example-v0.json", "")


def test_b024_fixture_is_not_mutated_by_validation() -> None:
    value = fixture()
    before = copy.deepcopy(value)
    validate_instance("mstr-test-generation-example-v0", value)
    assert value == before
''',
)

expected = {
    "docs/data/TEST_GENERATION_CURRICULUM.md",
    "evidence/mstr-000b/B024-test-curriculum.md",
    "schemas/mstr-test-generation-example-v0.schema.json",
    "specs/002-code-model-supremacy-foundation/contracts/mstr-test-generation-example-v0.schema.json",
    "src/mstr_qualify/cli.py",
    "src/mstr_qualify/schemas.py",
    "tests/contract/test_schemas.py",
    "tests/contract/test_test_generation_example_contract.py",
    "tests/fixtures/schemas/invalid/mstr-test-generation-example-v0.json",
    "tests/fixtures/schemas/valid/mstr-test-generation-example-v0.json",
    "tests/integration/test_cli_offline.py",
}
changed = {
    line.strip()
    for line in __import__("subprocess")
    .check_output(["git", "diff", "--name-only"], text=True)
    .splitlines()
    if line.strip()
}
if changed != expected:
    raise RuntimeError(f"unexpected B024 scope: {sorted(changed)}")

runtime = (ROOT / "schemas/mstr-test-generation-example-v0.schema.json").read_bytes()
design = (
    ROOT
    / "specs/002-code-model-supremacy-foundation/contracts/mstr-test-generation-example-v0.schema.json"
).read_bytes()
if runtime != design:
    raise RuntimeError("B024 runtime/design schemas are not byte-identical")
