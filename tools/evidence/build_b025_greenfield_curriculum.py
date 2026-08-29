from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path.cwd()
DESIGN_SCHEMA = ROOT / "specs/002-code-model-supremacy-foundation/contracts/mstr-greenfield-task-v0.schema.json"
RUNTIME_SCHEMA = ROOT / "schemas/mstr-greenfield-task-v0.schema.json"
DOC = ROOT / "docs/data/GREENFIELD_FEATURE_CURRICULUM.md"
EVIDENCE = ROOT / "evidence/mstr-000b/B025-greenfield-curriculum.md"
VALID_FIXTURE = ROOT / "tests/fixtures/schemas/valid/mstr-greenfield-task-v0.json"
INVALID_FIXTURE = ROOT / "tests/fixtures/schemas/invalid/mstr-greenfield-task-v0.json"
CONTRACT_TEST = ROOT / "tests/contract/test_greenfield_task_contract.py"
SCHEMAS_PY = ROOT / "src/mstr_qualify/schemas.py"
CLI_PY = ROOT / "src/mstr_qualify/cli.py"
SCHEMA_TEST = ROOT / "tests/contract/test_schemas.py"
CLI_TEST = ROOT / "tests/integration/test_cli_offline.py"

ENTRY_MAIN = "cd3e3ba39c0e83548748275d08b7a3d0d2e6b15b"
ENTRY_RUN = "33246944029"
ENTRY_JOB = "99085947153"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}: {old!r}; found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


schema: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-greenfield-task-v0.json",
    "title": "MSTR Greenfield Task Manifest v0",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "identity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 512,
        },
        "provenance": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "source_class": {
                    "enum": [
                        "PUBLIC_OPEN_SOURCE_REPOSITORY",
                        "PUBLIC_DATASET_COMPATIBLE_RIGHTS",
                        "PUBLIC_DOCUMENTATION_COMPATIBLE_RIGHTS",
                        "REPOSITORY_OWNED_FIXTURE",
                        "SYNTHETIC_VERIFIED",
                        "STUDENT_GENERATED_VERIFIED",
                        "TEACHER_OUTPUT_VERIFIED",
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
                "terms_identity": {"$ref": "#/$defs/identity"},
                "decision": {
                    "enum": ["COMPATIBLE", "INCOMPATIBLE", "UNRESOLVED"]
                },
                "intended_use": {"const": "MSTR_TRAINING_OR_EVALUATION"},
                "reason_codes": {
                    "type": "array",
                    "items": {"type": "string", "minLength": 1, "maxLength": 128},
                    "uniqueItems": True,
                },
            },
            "required": ["terms_identity", "decision", "intended_use", "reason_codes"],
        },
        "contamination_boundary": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "benchmark_overlap": {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]},
                "hidden_answer_exposure": {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]},
                "future_history_exposure": {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]},
                "cross_split_duplicate": {"enum": ["CLEAR", "DETECTED", "UNRESOLVED"]},
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
        "hidden_behavior_manifest": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "manifest_id": {"$ref": "#/$defs/identity"},
                "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
                "hidden_from_model": {"const": True},
                "behavior_classes": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {
                        "enum": [
                            "FUNCTIONAL",
                            "BOUNDARY",
                            "ERROR_PATH",
                            "INTEGRATION",
                            "MIGRATION",
                            "PRESERVATION",
                            "BUILD_CI",
                            "TEST_QUALITY",
                        ]
                    },
                },
            },
            "required": ["manifest_id", "sha256", "hidden_from_model", "behavior_classes"],
        },
        "resource_budget": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "max_wall_time_seconds": {"type": "integer", "minimum": 1, "maximum": 86400},
                "max_tool_calls": {"type": "integer", "minimum": 0, "maximum": 10000},
                "max_output_bytes": {"type": "integer", "minimum": 1},
                "network_policy": {"enum": ["DISABLED", "FIXTURE_ONLY"]},
            },
            "required": [
                "max_wall_time_seconds",
                "max_tool_calls",
                "max_output_bytes",
                "network_policy",
            ],
        },
        "synthesis_evidence": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "generator_kind": {"enum": ["FEATURE_TREE", "SEMANTIC_COMPLEXITY"]},
                "generator_identity": {"$ref": "#/$defs/identity"},
                "generator_revision": {"$ref": "#/$defs/identity"},
                "proposal_only": {"const": True},
                "independent_verification_status": {
                    "enum": ["VERIFIED", "REJECTED", "NOT_RUN"]
                },
                "independent_verifier_identity": {
                    "anyOf": [{"$ref": "#/$defs/identity"}, {"type": "null"}]
                },
                "verification_evidence_identity": {
                    "anyOf": [{"$ref": "#/$defs/identity"}, {"type": "null"}]
                },
            },
            "required": [
                "generator_kind",
                "generator_identity",
                "generator_revision",
                "proposal_only",
                "independent_verification_status",
                "independent_verifier_identity",
                "verification_evidence_identity",
            ],
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "independent_verification_status": {"const": "VERIFIED"}
                        },
                        "required": ["independent_verification_status"],
                    },
                    "then": {
                        "properties": {
                            "independent_verifier_identity": {"$ref": "#/$defs/identity"},
                            "verification_evidence_identity": {"$ref": "#/$defs/identity"},
                        }
                    },
                    "else": {
                        "properties": {
                            "independent_verifier_identity": {"type": "null"},
                            "verification_evidence_identity": {"type": "null"},
                        }
                    },
                }
            ],
        },
    },
    "properties": {
        "schema_version": {"const": "mstr.greenfield-task.v0"},
        "task_id": {"$ref": "#/$defs/identity"},
        "complexity_band": {
            "enum": [
                "G0_FUNCTION",
                "G1_MODULE_TESTS",
                "G2_COMPONENT_FILE",
                "G3_MULTI_FILE_FEATURE",
                "G4_BOUNDED_PROGRAM",
                "G5_MULTI_ROUND_EVOLUTION",
            ]
        },
        "direction": {"type": "string", "minLength": 1, "maxLength": 8192},
        "task_archetypes": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "enum": [
                    "FEATURE_IMPLEMENTATION",
                    "GREENFIELD_PROGRAM",
                    "API_CLI_CONSTRUCTION",
                    "INTEGRATION",
                    "MIGRATION",
                    "BEHAVIOR_PRESERVING_REFACTOR",
                    "BUILD_CI_REPAIR",
                    "TEST_AUTHORING",
                    "BUG_REPAIR",
                ]
            },
        },
        "allowed_languages": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1, "maxLength": 64},
        },
        "environment_identity": {"$ref": "#/$defs/identity"},
        "hidden_behavior_manifest": {"$ref": "#/$defs/hidden_behavior_manifest"},
        "resource_budget": {"$ref": "#/$defs/resource_budget"},
        "verifier_manifest_id": {"$ref": "#/$defs/identity"},
        "verifier_health_requirement": {"const": "HEALTHY"},
        "contamination_boundary": {"$ref": "#/$defs/contamination_boundary"},
        "provenance": {"$ref": "#/$defs/provenance"},
        "rights_decision": {"$ref": "#/$defs/rights_decision"},
        "generation_method": {
            "enum": [
                "CURATED",
                "REPOSITORY_DERIVED",
                "FEATURE_TREE_SYNTHESIS",
                "SEMANTIC_SYNTHESIS",
            ]
        },
        "synthesis_evidence": {
            "anyOf": [{"$ref": "#/$defs/synthesis_evidence"}, {"type": "null"}]
        },
        "evolution_steps": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1, "maxLength": 512},
        },
        "admission_class": {
            "enum": ["CURRICULUM_ELIGIBLE", "EXPERIMENTAL_ONLY", "REJECTED"]
        },
        "admission_reasons": {
            "type": "array",
            "items": {"type": "string", "minLength": 1, "maxLength": 128},
            "uniqueItems": True,
        },
    },
    "required": [
        "schema_version",
        "task_id",
        "complexity_band",
        "direction",
        "task_archetypes",
        "allowed_languages",
        "environment_identity",
        "hidden_behavior_manifest",
        "resource_budget",
        "verifier_manifest_id",
        "verifier_health_requirement",
        "contamination_boundary",
        "provenance",
        "rights_decision",
        "generation_method",
        "synthesis_evidence",
        "evolution_steps",
        "admission_class",
        "admission_reasons",
    ],
    "allOf": [
        {
            "if": {
                "properties": {"complexity_band": {"const": "G5_MULTI_ROUND_EVOLUTION"}},
                "required": ["complexity_band"],
            },
            "then": {"properties": {"evolution_steps": {"minItems": 2}}},
            "else": {"properties": {"evolution_steps": {"maxItems": 0}}},
        },
        {
            "if": {
                "properties": {
                    "generation_method": {
                        "enum": ["FEATURE_TREE_SYNTHESIS", "SEMANTIC_SYNTHESIS"]
                    }
                },
                "required": ["generation_method"],
            },
            "then": {
                "properties": {
                    "synthesis_evidence": {"$ref": "#/$defs/synthesis_evidence"}
                },
                "allOf": [
                    {
                        "if": {
                            "properties": {
                                "synthesis_evidence": {
                                    "properties": {
                                        "independent_verification_status": {"const": "VERIFIED"}
                                    },
                                    "required": ["independent_verification_status"],
                                }
                            }
                        },
                        "else": {
                            "properties": {
                                "admission_class": {
                                    "enum": ["EXPERIMENTAL_ONLY", "REJECTED"]
                                }
                            }
                        },
                    }
                ],
            },
            "else": {"properties": {"synthesis_evidence": {"type": "null"}}},
        },
        {
            "if": {
                "properties": {"admission_class": {"const": "CURRICULUM_ELIGIBLE"}},
                "required": ["admission_class"],
            },
            "then": {
                "properties": {
                    "rights_decision": {
                        "properties": {"decision": {"const": "COMPATIBLE"}}
                    },
                    "contamination_boundary": {
                        "properties": {
                            "benchmark_overlap": {"const": "CLEAR"},
                            "hidden_answer_exposure": {"const": "CLEAR"},
                            "future_history_exposure": {"const": "CLEAR"},
                            "cross_split_duplicate": {"const": "CLEAR"},
                        }
                    },
                    "admission_reasons": {"maxItems": 0},
                }
            },
            "else": {"properties": {"admission_reasons": {"minItems": 1}}},
        },
    ],
}

schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
for path in (DESIGN_SCHEMA, RUNTIME_SCHEMA):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(schema_text, encoding="utf-8")

valid_fixture = {
    "schema_version": "mstr.greenfield-task.v0",
    "task_id": "b025-fixture-g3-feature",
    "complexity_band": "G3_MULTI_FILE_FEATURE",
    "direction": "Add a deterministic local configuration export feature with tests.",
    "task_archetypes": ["FEATURE_IMPLEMENTATION", "TEST_AUTHORING"],
    "allowed_languages": ["Python"],
    "environment_identity": "fixture-env:python-3.11-offline",
    "hidden_behavior_manifest": {
        "manifest_id": "fixture-hidden-behavior-v1",
        "sha256": "1" * 64,
        "hidden_from_model": True,
        "behavior_classes": ["FUNCTIONAL", "BOUNDARY", "ERROR_PATH"],
    },
    "resource_budget": {
        "max_wall_time_seconds": 300,
        "max_tool_calls": 40,
        "max_output_bytes": 1048576,
        "network_policy": "DISABLED",
    },
    "verifier_manifest_id": "fixture-verifier-manifest-v1",
    "verifier_health_requirement": "HEALTHY",
    "contamination_boundary": {
        "benchmark_overlap": "CLEAR",
        "hidden_answer_exposure": "CLEAR",
        "future_history_exposure": "CLEAR",
        "cross_split_duplicate": "CLEAR",
        "evidence_identity": "fixture-contamination-check-v1",
    },
    "provenance": {
        "source_class": "REPOSITORY_OWNED_FIXTURE",
        "source_identity": "TheHalfMoon/MSTR:fixture",
        "source_revision": ENTRY_MAIN,
        "lineage_identity": "fixture-lineage-v1",
        "generator_identity": None,
    },
    "rights_decision": {
        "terms_identity": "repository-owned-fixture-policy-v1",
        "decision": "COMPATIBLE",
        "intended_use": "MSTR_TRAINING_OR_EVALUATION",
        "reason_codes": [],
    },
    "generation_method": "CURATED",
    "synthesis_evidence": None,
    "evolution_steps": [],
    "admission_class": "CURRICULUM_ELIGIBLE",
    "admission_reasons": [],
}
write_json(VALID_FIXTURE, valid_fixture)

invalid_fixture = copy.deepcopy(valid_fixture)
invalid_fixture["task_id"] = "b025-invalid-unverified-synthesis"
invalid_fixture["generation_method"] = "FEATURE_TREE_SYNTHESIS"
invalid_fixture["provenance"]["source_class"] = "SYNTHETIC_VERIFIED"
invalid_fixture["provenance"]["generator_identity"] = "fixture-feature-tree-generator"
invalid_fixture["synthesis_evidence"] = {
    "generator_kind": "FEATURE_TREE",
    "generator_identity": "fixture-feature-tree-generator",
    "generator_revision": "fixture-revision-1",
    "proposal_only": True,
    "independent_verification_status": "NOT_RUN",
    "independent_verifier_identity": None,
    "verification_evidence_identity": None,
}
write_json(INVALID_FIXTURE, invalid_fixture)

DOC.parent.mkdir(parents=True, exist_ok=True)
DOC.write_text(
    """# MSTR Greenfield / Feature Curriculum v0

**Task:** `B025`  
**Contract:** `mstr.greenfield-task.v0`  
**Status:** implementation candidate — not canonical until governed merge and closeout

## Purpose

This curriculum prevents MSTR software evaluation and future training from collapsing into bug-patch-only work. It freezes a bounded Direction-to-Done progression for new functionality while preserving the MSTR Data Constitution, hidden-behavior integrity, verifier independence, universal-laptop constraints, and exact external-effect boundaries.

B025 is a contract-and-fixture task only. It does not generate real synthetic programs, execute a model, ingest a corpus, run a verifier-health classifier, acquire model weights, or authorize training.

## Complexity bands

| Band | Required shape | Representative scope |
|---|---|---|
| `G0_FUNCTION` | one bounded function or utility | pure transformation, parser helper, deterministic utility |
| `G1_MODULE_TESTS` | module plus tests | cohesive module/API with direct regression coverage |
| `G2_COMPONENT_FILE` | component or file-level behavior | CLI subcommand, adapter, component, config surface |
| `G3_MULTI_FILE_FEATURE` | coordinated multi-file feature | implementation + tests + config/docs where needed |
| `G4_BOUNDED_PROGRAM` | bounded service/CLI/library | self-contained local program with explicit resource budget |
| `G5_MULTI_ROUND_EVOLUTION` | at least two ordered feature-evolution steps | repeated changes with behavioral preservation across rounds |

The bands describe semantic and repository scope, not token count. Difficulty remains checkpoint-relative under B020/B021.

## Required task archetypes

A curriculum portfolio must materially cover:

```text
FEATURE_IMPLEMENTATION
GREENFIELD_PROGRAM
API_CLI_CONSTRUCTION
INTEGRATION
MIGRATION
BEHAVIOR_PRESERVING_REFACTOR
BUILD_CI_REPAIR
TEST_AUTHORING
BUG_REPAIR
```

`BUG_REPAIR` is retained but must not dominate the default product-evaluation mix. Stage-specific distribution manifests remain governed by `MSTR-DATA-CONSTITUTION-v0` and the B015 language/tooling policy.

## Manifest integrity

Every `mstr.greenfield-task.v0` record binds:

- exact task identity and one G0–G5 complexity band;
- a bounded natural-language direction;
- explicit task archetypes and allowed languages;
- exact environment identity and finite resource budget;
- hidden behavior manifest identity + SHA-256 with `hidden_from_model=true`;
- verifier manifest identity and required verifier-health class `HEALTHY`;
- contamination boundary evidence;
- source provenance and immutable source revision;
- concrete rights decision for MSTR training/evaluation use;
- generation method and, when synthetic, generator/verification evidence;
- admission class and deterministic rejection/diagnostic reasons.

No hidden behavior artifact may be model-visible. No unrestricted network policy exists in v0; executable tasks are `DISABLED` or `FIXTURE_ONLY` unless a later canonical contract explicitly changes the boundary.

## Data Constitution gate

`CURRICULUM_ELIGIBLE` is fail-closed. It requires:

```text
RIGHTS_DECISION = COMPATIBLE
BENCHMARK_OVERLAP = CLEAR
HIDDEN_ANSWER_EXPOSURE = CLEAR
FUTURE_HISTORY_EXPOSURE = CLEAR
CROSS_SPLIT_DUPLICATE = CLEAR
ADMISSION_REASONS = []
VERIFIER_HEALTH_REQUIREMENT = HEALTHY
```

The manifest records the requirement; B025 does not claim that B023 verifier-health execution exists. A downstream executable admission pipeline must bind actual verifier-health evidence before using a task as clean positive signal.

## Feature-tree and semantic synthesis

Feature-tree / semantic-complexity synthesis is an **experimental generator**, never an authority source.

```text
FEATURE_TREE_SYNTHESIS
SEMANTIC_SYNTHESIS
```

For either method:

1. `synthesis_evidence` is mandatory;
2. the generator identity and immutable revision are mandatory;
3. `proposal_only=true` is mandatory;
4. an unverified or rejected proposal cannot be `CURRICULUM_ELIGIBLE`;
5. `VERIFIED` requires an independent verifier identity and evidence identity;
6. independent verification does not bypass provenance, rights, contamination, hidden-behavior, Data Constitution, or later verifier-health gates.

Synthetic generation is therefore a task proposal mechanism. It is not self-certifying training data.

## G5 multi-round evolution

`G5_MULTI_ROUND_EVOLUTION` requires at least two unique ordered evolution-step identities. Earlier-step model-visible context must not contain later hidden behavior, later patches, future review outcomes, or final answers. The B016 future-history boundary remains authoritative.

## Evaluation posture

Public FEA-Bench/ProgramBench-style protocols may inform future evaluation design, but benchmark availability never grants training-data rights or contamination clearance. Repository-owned fixtures are sufficient for B025 contract qualification.

Metrics should ultimately preserve the program north stars:

```text
DVCR
TTVC
FPAR
ESR
RSR
TER
RHD
VC_PER_GB
```

Band-level reporting must keep raw task success separate from harness-only gains and from future checkpoint difficulty labels.

## Non-authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_HEALTH_EVALUATOR_EXECUTION = NONE
SYNTHESIS_EXECUTION = NONE
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

B025 freezes curriculum semantics only. It never converts a proposal, fixture, benchmark, or generator output into project authority.
""",
    encoding="utf-8",
)

EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
EVIDENCE.write_text(
    f"""# B025 — Greenfield / Feature / Synthesis Curriculum Evidence

**Task:** `B025`  
**State:** `IMPLEMENTATION_ACTIVE`  
**Canonical entry main:** `{ENTRY_MAIN}`  
**Entry gate run:** `{ENTRY_RUN}`  
**Entry gate job:** `{ENTRY_JOB}`

## Entry gate

Exact-main machine validation completed successfully before material B025 execution.

```text
TASK = B025
CANONICAL_MAIN = {ENTRY_MAIN}
TASK_DRIFT = clean
TASKS_CHECKED = 34
B025_STATE = PENDING
B025_ELIGIBLE = true
B025_REASONS = []
EXTERNAL_AUTHORITY_REQUIRED = false
FRONTIER_PENDING_ELIGIBLE = B025,B028
```

The same run proved B011 remained blocked by missing repository-specific external authority, B023 remained blocked by A006/A014, and no terminal task was reopened.

## Contract frozen by this implementation candidate

```text
SCHEMA_VERSION = mstr.greenfield-task.v0
COMPLEXITY_BANDS = G0_FUNCTION,G1_MODULE_TESTS,G2_COMPONENT_FILE,G3_MULTI_FILE_FEATURE,G4_BOUNDED_PROGRAM,G5_MULTI_ROUND_EVOLUTION
SYNTHESIS_METHODS = FEATURE_TREE_SYNTHESIS,SEMANTIC_SYNTHESIS
SYNTHESIS_DEFAULT = EXPERIMENTAL_PROPOSAL_ONLY
CURRICULUM_ELIGIBLE_REQUIRES_COMPATIBLE_RIGHTS = true
CURRICULUM_ELIGIBLE_REQUIRES_CLEAR_CONTAMINATION = true
HIDDEN_BEHAVIOR_MODEL_VISIBILITY = prohibited
VERIFIER_HEALTH_REQUIREMENT = HEALTHY
UNRESTRICTED_NETWORK_POLICY = prohibited
```

Runtime and design-source schemas are required to remain byte-identical. The valid fixture is repository-owned and performs no model or external execution. The invalid fixture proves that unverified feature-tree synthesis cannot self-admit as curriculum-eligible.

## Scope boundary

This implementation intentionally does not:

- execute feature-tree or semantic synthesis;
- implement B023 verifier-health evaluation;
- implement B024 test-generation curriculum;
- ingest any external dataset;
- access model weights or execute a model;
- use a teacher/API or paid compute;
- mutate task canonical state or mark B025 complete before post-merge closeout.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_HEALTH_EVALUATOR_EXECUTION = NONE
SYNTHESIS_EXECUTION = NONE
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
B025_AUTHORITY = GREENFIELD_FEATURE_CURRICULUM_CONTRACT_AND_FIXTURES_ONLY
```
""",
    encoding="utf-8",
)

CONTRACT_TEST.write_text(
    """from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests/fixtures/schemas/valid/mstr-greenfield-task-v0.json"


def fixture() -> dict[str, object]:
    return json.loads(VALID.read_text(encoding="utf-8"))


def test_b025_complexity_bands_are_exact_and_all_validate() -> None:
    expected = {
        "G0_FUNCTION",
        "G1_MODULE_TESTS",
        "G2_COMPONENT_FILE",
        "G3_MULTI_FILE_FEATURE",
        "G4_BOUNDED_PROGRAM",
        "G5_MULTI_ROUND_EVOLUTION",
    }
    for band in sorted(expected):
        value = fixture()
        value["complexity_band"] = band
        value["evolution_steps"] = ["round-1", "round-2"] if band == "G5_MULTI_ROUND_EVOLUTION" else []
        validate_instance("mstr-greenfield-task-v0", value)


def test_b025_g5_requires_multiple_evolution_steps() -> None:
    value = fixture()
    value["complexity_band"] = "G5_MULTI_ROUND_EVOLUTION"
    value["evolution_steps"] = ["round-1"]
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_non_g5_rejects_future_evolution_steps() -> None:
    value = fixture()
    value["evolution_steps"] = ["future-round"]
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_unverified_feature_tree_synthesis_cannot_self_admit() -> None:
    value = fixture()
    value["generation_method"] = "FEATURE_TREE_SYNTHESIS"
    value["provenance"]["source_class"] = "SYNTHETIC_VERIFIED"
    value["provenance"]["generator_identity"] = "generator:v1"
    value["synthesis_evidence"] = {
        "generator_kind": "FEATURE_TREE",
        "generator_identity": "generator:v1",
        "generator_revision": "revision:1",
        "proposal_only": True,
        "independent_verification_status": "NOT_RUN",
        "independent_verifier_identity": None,
        "verification_evidence_identity": None,
    }
    value["admission_class"] = "CURRICULUM_ELIGIBLE"
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_verified_feature_tree_proposal_may_pass_contract_gate() -> None:
    value = fixture()
    value["generation_method"] = "FEATURE_TREE_SYNTHESIS"
    value["provenance"]["source_class"] = "SYNTHETIC_VERIFIED"
    value["provenance"]["generator_identity"] = "generator:v1"
    value["synthesis_evidence"] = {
        "generator_kind": "FEATURE_TREE",
        "generator_identity": "generator:v1",
        "generator_revision": "revision:1",
        "proposal_only": True,
        "independent_verification_status": "VERIFIED",
        "independent_verifier_identity": "verifier:independent-v1",
        "verification_evidence_identity": "evidence:verification-v1",
    }
    validate_instance("mstr-greenfield-task-v0", value)


@pytest.mark.parametrize("status", ["INCOMPATIBLE", "UNRESOLVED"])
def test_b025_curriculum_eligible_fails_closed_on_rights(status: str) -> None:
    value = fixture()
    value["rights_decision"]["decision"] = status
    assert validation_errors("mstr-greenfield-task-v0", value)


@pytest.mark.parametrize(
    "field",
    [
        "benchmark_overlap",
        "hidden_answer_exposure",
        "future_history_exposure",
        "cross_split_duplicate",
    ],
)
def test_b025_curriculum_eligible_requires_clear_contamination(field: str) -> None:
    value = fixture()
    value["contamination_boundary"][field] = "UNRESOLVED"
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_hidden_behavior_must_remain_hidden() -> None:
    value = fixture()
    value["hidden_behavior_manifest"]["hidden_from_model"] = False
    assert validation_errors("mstr-greenfield-task-v0", value)


def test_b025_rejected_or_experimental_records_require_reasons() -> None:
    for admission in ("EXPERIMENTAL_ONLY", "REJECTED"):
        value = fixture()
        value["admission_class"] = admission
        assert validation_errors("mstr-greenfield-task-v0", value)
        value["admission_reasons"] = ["fixture.reason"]
        validate_instance("mstr-greenfield-task-v0", value)


def test_b025_schema_has_no_remote_reference() -> None:
    schema = json.loads((ROOT / "schemas/mstr-greenfield-task-v0.schema.json").read_text(encoding="utf-8"))
    encoded = json.dumps(schema, sort_keys=True)
    assert "http" not in encoded.replace("https://json-schema.org/draft/2020-12/schema", "").replace("https://mstr.local/schemas/mstr-greenfield-task-v0.json", "")


def test_b025_fixture_is_not_mutated_by_validation() -> None:
    value = fixture()
    before = copy.deepcopy(value)
    validate_instance("mstr-greenfield-task-v0", value)
    assert value == before
""",
    encoding="utf-8",
)

replace_once(
    SCHEMAS_PY,
    '    # MSTR-000B B022: verifier-health evidence contract.\n    "mstr-verifier-health-v0": "mstr-verifier-health-v0.schema.json",\n',
    '    # MSTR-000B B022: verifier-health evidence contract.\n'
    '    "mstr-verifier-health-v0": "mstr-verifier-health-v0.schema.json",\n'
    '    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.\n'
    '    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",\n',
)

replace_once(
    CLI_PY,
    '    # MSTR-000B B022 verifier-health evidence contract.\n    "mstr.verifier-health.v0": "mstr-verifier-health-v0",\n',
    '    # MSTR-000B B022 verifier-health evidence contract.\n'
    '    "mstr.verifier-health.v0": "mstr-verifier-health-v0",\n'
    '    # MSTR-000B B025 greenfield/feature/synthesis task manifest contract.\n'
    '    "mstr.greenfield-task.v0": "mstr-greenfield-task-v0",\n',
)

replace_once(
    SCHEMA_TEST,
    '    "mstr-verifier-health-v0": (\n        ROOT\n        / "specs"\n        / "002-code-model-supremacy-foundation"\n        / "contracts"\n        / "mstr-verifier-health-v0.schema.json"\n    ),\n',
    '    "mstr-verifier-health-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-verifier-health-v0.schema.json"\n'
    '    ),\n'
    '    "mstr-greenfield-task-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-greenfield-task-v0.schema.json"\n'
    '    ),\n',
)

replace_once(
    CLI_TEST,
    '        "mstr-difficulty-calibration-v0",\n        "mstr-loop-contract-v0",\n',
    '        "mstr-difficulty-calibration-v0",\n        "mstr-greenfield-task-v0",\n        "mstr-loop-contract-v0",\n',
)

with CLI_TEST.open("a", encoding="utf-8") as handle:
    handle.write(
        "\n\ndef test_validate_explicit_b025_greenfield_fixture_passes(\n"
        "    capsys: pytest.CaptureFixture[str],\n"
        ") -> None:\n"
        "    path = (\n"
        "        Path(__file__).resolve().parents[2]\n"
        "        / \"tests\"\n"
        "        / \"fixtures\"\n"
        "        / \"schemas\"\n"
        "        / \"valid\"\n"
        "        / \"mstr-greenfield-task-v0.json\"\n"
        "    )\n"
        "    assert main([\"validate\", str(path)]) == 0\n"
        "    payload = parse_stdout(capsys)\n"
        "    assert payload[\"status\"] == \"pass\"\n"
        "    assert payload[\"files\"][0][\"schema_version\"] == \"mstr.greenfield-task.v0\"\n"
    )
