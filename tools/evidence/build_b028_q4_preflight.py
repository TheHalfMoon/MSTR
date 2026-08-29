from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.cwd()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one match in {path}: {old!r}; found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


training_method_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-training-method-cell-v0.json",
    "title": "MSTR Training Method Cell v0",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "backbone_identity": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "candidate_id": {"type": "string", "minLength": 1, "maxLength": 256},
                "model_id": {"type": "string", "minLength": 1, "maxLength": 512},
                "immutable_revision": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "required": ["candidate_id", "model_id", "immutable_revision"],
        },
        "quantization": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "base_bits": {"const": 4},
                "scheme": {"enum": ["NF4", "FP4", "OTHER"]},
                "tool_id": {"type": "string", "minLength": 1, "maxLength": 256},
                "tool_revision": {"type": "string", "minLength": 1, "maxLength": 256},
            },
            "required": ["base_bits", "scheme", "tool_id", "tool_revision"],
        },
        "token_update_budget": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "unit": {"enum": ["TOKENS", "UPDATES"]},
                "value": {"type": "integer", "minimum": 1},
            },
            "required": ["unit", "value"],
        },
    },
    "properties": {
        "schema_version": {"const": "mstr.training-method-cell.v0"},
        "cell_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "backbone_identity": {"$ref": "#/$defs/backbone_identity"},
        "method": {
            "enum": [
                "LORA_16BIT",
                "LORA_16BIT_RSLORA",
                "QLORA_4BIT",
                "QLORA_4BIT_RSLORA",
            ]
        },
        "precision": {"enum": ["SIXTEEN_BIT", "FOUR_BIT_BASE"]},
        "lora_rank": {"type": "integer", "minimum": 1, "maximum": 4096},
        "rslora": {"type": "boolean"},
        "quantization": {"oneOf": [{"type": "null"}, {"$ref": "#/$defs/quantization"}]},
        "dataset_manifest_id": {"type": "string", "minLength": 1, "maxLength": 512},
        "token_update_budget": {"$ref": "#/$defs/token_update_budget"},
        "seed_policy": {"type": "string", "minLength": 1, "maxLength": 512},
        "environment_identity": {"type": "string", "minLength": 1, "maxLength": 512},
        "eval_identity": {"type": "string", "minLength": 1, "maxLength": 512},
        "export_recipe": {"type": "string", "minLength": 1, "maxLength": 512},
        "q4_recipe": {"type": "string", "minLength": 1, "maxLength": 512},
        "support_status": {"enum": ["SUPPORTED", "UNSUPPORTED", "REVALIDATION_REQUIRED"]},
        "support_evidence_identity": {"type": "string", "minLength": 1, "maxLength": 1024},
        "unsupported_reason": {"type": ["string", "null"], "minLength": 1, "maxLength": 1024},
        "status": {
            "enum": [
                "PREFLIGHT_ONLY",
                "READY_FOR_AUTHORIZED_EXECUTION",
                "EXECUTED",
                "UNSUPPORTED",
                "INVALID",
            ]
        },
    },
    "required": [
        "schema_version",
        "cell_id",
        "backbone_identity",
        "method",
        "precision",
        "lora_rank",
        "rslora",
        "quantization",
        "dataset_manifest_id",
        "token_update_budget",
        "seed_policy",
        "environment_identity",
        "eval_identity",
        "export_recipe",
        "q4_recipe",
        "support_status",
        "support_evidence_identity",
        "unsupported_reason",
        "status",
    ],
    "allOf": [
        {
            "if": {"properties": {"method": {"const": "LORA_16BIT"}}, "required": ["method"]},
            "then": {
                "properties": {
                    "precision": {"const": "SIXTEEN_BIT"},
                    "rslora": {"const": False},
                    "quantization": {"type": "null"},
                }
            },
        },
        {
            "if": {
                "properties": {"method": {"const": "LORA_16BIT_RSLORA"}},
                "required": ["method"],
            },
            "then": {
                "properties": {
                    "precision": {"const": "SIXTEEN_BIT"},
                    "rslora": {"const": True},
                    "quantization": {"type": "null"},
                }
            },
        },
        {
            "if": {"properties": {"method": {"const": "QLORA_4BIT"}}, "required": ["method"]},
            "then": {
                "properties": {
                    "precision": {"const": "FOUR_BIT_BASE"},
                    "rslora": {"const": False},
                    "quantization": {"$ref": "#/$defs/quantization"},
                }
            },
        },
        {
            "if": {
                "properties": {"method": {"const": "QLORA_4BIT_RSLORA"}},
                "required": ["method"],
            },
            "then": {
                "properties": {
                    "precision": {"const": "FOUR_BIT_BASE"},
                    "rslora": {"const": True},
                    "quantization": {"$ref": "#/$defs/quantization"},
                }
            },
        },
        {
            "if": {
                "properties": {"support_status": {"const": "UNSUPPORTED"}},
                "required": ["support_status"],
            },
            "then": {
                "properties": {
                    "unsupported_reason": {"type": "string", "minLength": 1},
                    "status": {"const": "UNSUPPORTED"},
                }
            },
            "else": {"properties": {"unsupported_reason": {"type": "null"}}},
        },
        {
            "if": {
                "properties": {
                    "status": {"enum": ["READY_FOR_AUTHORIZED_EXECUTION", "EXECUTED"]}
                },
                "required": ["status"],
            },
            "then": {"properties": {"support_status": {"const": "SUPPORTED"}}},
        },
    ],
}

q4_promotion_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://mstr.local/schemas/mstr-q4-promotion-v0.json",
    "title": "MSTR Q4 Promotion Record v0",
    "type": "object",
    "additionalProperties": False,
    "$defs": {
        "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    },
    "properties": {
        "schema_version": {"const": "mstr.q4-promotion.v0"},
        "source_training_run_id": {"type": "string", "minLength": 1, "maxLength": 512},
        "source_checkpoint_sha256": {"$ref": "#/$defs/sha256"},
        "merged_master_sha256": {"$ref": "#/$defs/sha256"},
        "export_tool_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "export_tool_revision": {"type": "string", "minLength": 1, "maxLength": 256},
        "export_recipe_hash": {"$ref": "#/$defs/sha256"},
        "quantizer_tool_id": {"type": "string", "minLength": 1, "maxLength": 256},
        "quantizer_tool_revision": {"type": "string", "minLength": 1, "maxLength": 256},
        "quantization_recipe_hash": {"$ref": "#/$defs/sha256"},
        "canonical_q4_artifact_sha256": {"$ref": "#/$defs/sha256"},
        "artifact_integrity_status": {"enum": ["PASS", "FAIL"]},
        "q4_regression_manifest_id": {"type": "string", "minLength": 1, "maxLength": 512},
        "q4_regression_result": {"enum": ["PASS", "FAIL"]},
        "universal_laptop_gate_result": {"enum": ["PASS", "FAIL", "NOT_REQUIRED"]},
        "universal_laptop_gate_evidence_identity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024,
        },
        "universal_laptop_gate_not_required_reason": {
            "type": ["string", "null"],
            "minLength": 1,
            "maxLength": 1024,
        },
        "promotion_status": {"enum": ["PROMOTED", "REJECTED"]},
        "rejection_reasons": {
            "type": "array",
            "items": {"type": "string", "minLength": 1, "maxLength": 256},
            "uniqueItems": True,
        },
        "promotion_decision_evidence_identity": {
            "type": "string",
            "minLength": 1,
            "maxLength": 1024,
        },
    },
    "required": [
        "schema_version",
        "source_training_run_id",
        "source_checkpoint_sha256",
        "merged_master_sha256",
        "export_tool_id",
        "export_tool_revision",
        "export_recipe_hash",
        "quantizer_tool_id",
        "quantizer_tool_revision",
        "quantization_recipe_hash",
        "canonical_q4_artifact_sha256",
        "artifact_integrity_status",
        "q4_regression_manifest_id",
        "q4_regression_result",
        "universal_laptop_gate_result",
        "universal_laptop_gate_evidence_identity",
        "universal_laptop_gate_not_required_reason",
        "promotion_status",
        "rejection_reasons",
        "promotion_decision_evidence_identity",
    ],
    "allOf": [
        {
            "if": {
                "properties": {"promotion_status": {"const": "PROMOTED"}},
                "required": ["promotion_status"],
            },
            "then": {
                "properties": {
                    "artifact_integrity_status": {"const": "PASS"},
                    "q4_regression_result": {"const": "PASS"},
                    "universal_laptop_gate_result": {"enum": ["PASS", "NOT_REQUIRED"]},
                    "rejection_reasons": {"maxItems": 0},
                }
            },
            "else": {"properties": {"rejection_reasons": {"minItems": 1}}},
        },
        {
            "if": {
                "properties": {"universal_laptop_gate_result": {"const": "NOT_REQUIRED"}},
                "required": ["universal_laptop_gate_result"],
            },
            "then": {
                "properties": {
                    "universal_laptop_gate_not_required_reason": {
                        "type": "string",
                        "minLength": 1,
                    }
                }
            },
            "else": {
                "properties": {"universal_laptop_gate_not_required_reason": {"type": "null"}}
            },
        },
    ],
}

for filename, schema in (
    ("mstr-training-method-cell-v0.schema.json", training_method_schema),
    ("mstr-q4-promotion-v0.schema.json", q4_promotion_schema),
):
    write_json(ROOT / "schemas" / filename, schema)
    write_json(
        ROOT / "specs" / "002-code-model-supremacy-foundation" / "contracts" / filename,
        schema,
    )

valid_training = {
    "schema_version": "mstr.training-method-cell.v0",
    "cell_id": "fixture-q4-rslora",
    "backbone_identity": {
        "candidate_id": "fixture-backbone",
        "model_id": "example/fixture-backbone",
        "immutable_revision": "0123456789abcdef",
    },
    "method": "QLORA_4BIT_RSLORA",
    "precision": "FOUR_BIT_BASE",
    "lora_rank": 16,
    "rslora": True,
    "quantization": {
        "base_bits": 4,
        "scheme": "NF4",
        "tool_id": "bitsandbytes",
        "tool_revision": "fixture-revision",
    },
    "dataset_manifest_id": "fixture-dataset-v1",
    "token_update_budget": {"unit": "UPDATES", "value": 32},
    "seed_policy": "fixture-seed-policy-v1",
    "environment_identity": "fixture-environment-v1",
    "eval_identity": "fixture-eval-v1",
    "export_recipe": "fixture-export-v1",
    "q4_recipe": "fixture-q4-v1",
    "support_status": "REVALIDATION_REQUIRED",
    "support_evidence_identity": "fixture-generic-framework-guidance-only",
    "unsupported_reason": None,
    "status": "PREFLIGHT_ONLY",
}
invalid_training = dict(valid_training)
invalid_training.update(
    {
        "method": "QLORA_4BIT",
        "precision": "SIXTEEN_BIT",
        "rslora": False,
        "quantization": None,
    }
)

hex_a = "a" * 64
hex_b = "b" * 64
hex_c = "c" * 64
hex_d = "d" * 64
hex_e = "e" * 64
valid_q4 = {
    "schema_version": "mstr.q4-promotion.v0",
    "source_training_run_id": "fixture-training-run",
    "source_checkpoint_sha256": hex_a,
    "merged_master_sha256": hex_b,
    "export_tool_id": "fixture-exporter",
    "export_tool_revision": "fixture-exporter-rev",
    "export_recipe_hash": hex_c,
    "quantizer_tool_id": "fixture-quantizer",
    "quantizer_tool_revision": "fixture-quantizer-rev",
    "quantization_recipe_hash": hex_d,
    "canonical_q4_artifact_sha256": hex_e,
    "artifact_integrity_status": "PASS",
    "q4_regression_manifest_id": "fixture-q4-regression-v1",
    "q4_regression_result": "PASS",
    "universal_laptop_gate_result": "PASS",
    "universal_laptop_gate_evidence_identity": "fixture-u1-evidence",
    "universal_laptop_gate_not_required_reason": None,
    "promotion_status": "PROMOTED",
    "rejection_reasons": [],
    "promotion_decision_evidence_identity": "fixture-promotion-evidence",
}
invalid_q4 = dict(valid_q4)
invalid_q4["q4_regression_result"] = "FAIL"

write_json(ROOT / "tests/fixtures/schemas/valid/mstr-training-method-cell-v0.json", valid_training)
write_json(ROOT / "tests/fixtures/schemas/invalid/mstr-training-method-cell-v0.json", invalid_training)
write_json(ROOT / "tests/fixtures/schemas/valid/mstr-q4-promotion-v0.json", valid_q4)
write_json(ROOT / "tests/fixtures/schemas/invalid/mstr-q4-promotion-v0.json", invalid_q4)

schemas_py = ROOT / "src/mstr_qualify/schemas.py"
replace_once(
    schemas_py,
    '    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.\n'
    '    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",\n',
    '    # MSTR-000B B025: greenfield/feature/synthesis task manifest contract.\n'
    '    "mstr-greenfield-task-v0": "mstr-greenfield-task-v0.schema.json",\n'
    '    # MSTR-000B B028: training-method preflight and fail-closed Q4 promotion.\n'
    '    "mstr-training-method-cell-v0": "mstr-training-method-cell-v0.schema.json",\n'
    '    "mstr-q4-promotion-v0": "mstr-q4-promotion-v0.schema.json",\n',
)

test_schemas = ROOT / "tests/contract/test_schemas.py"
replace_once(
    test_schemas,
    '    "mstr-greenfield-task-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-greenfield-task-v0.schema.json"\n'
    '    ),\n',
    '    "mstr-greenfield-task-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-greenfield-task-v0.schema.json"\n'
    '    ),\n'
    '    "mstr-training-method-cell-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-training-method-cell-v0.schema.json"\n'
    '    ),\n'
    '    "mstr-q4-promotion-v0": (\n'
    '        ROOT\n'
    '        / "specs"\n'
    '        / "002-code-model-supremacy-foundation"\n'
    '        / "contracts"\n'
    '        / "mstr-q4-promotion-v0.schema.json"\n'
    '    ),\n',
)

contracts_readme = ROOT / "specs/002-code-model-supremacy-foundation/contracts/README.md"
replace_once(
    contracts_readme,
    "Remaining planned contracts:\n\n```text\n",
    "## Frozen by B028\n\n```text\n"
    "mstr.training-method-cell.v0\n"
    "mstr.q4-promotion.v0\n"
    "```\n\n"
    "B028 freezes the equivalent-method tournament cell and fail-closed Q4 checkpoint-promotion contracts. Generic framework documentation is never candidate-specific arm support evidence: every concrete finalist/method cell must bind exact backbone/framework support evidence or an exact unsupported reason before execution. A later material checkpoint may parent another material weight-changing stage only when its `mstr.q4-promotion.v0` record is `PROMOTED`. B028 itself grants no training, model-weight access, paid compute, or model-execution authority.\n\n"
    "Remaining planned contracts:\n\n```text\n",
)
replace_once(contracts_readme, "mstr.training-method-cell.v0\n", "",)
replace_once(contracts_readme, "mstr.q4-promotion.v0\n", "",)

manifest = {
    "artifact_version": "mstr.b028.method-tournament-preflight.v1",
    "task_id": "B028",
    "canonical_main_at_entry": "9d5908016b2b8775eaf86dbcebb89683f52e1f90",
    "entry_gate": {
        "run_id": 33250934988,
        "job_id": 99096373017,
        "eligible": True,
        "authority_required": False,
        "reasons": [],
    },
    "b009_compatibility_source": {
        "artifact": "artifacts/decisions/B009-training-runtime-compatibility.json",
        "artifact_version": "mstr.b009.training-runtime-compatibility.v1",
        "interpretation": "GENERIC_OR_SOURCE_LEVEL_COMPATIBILITY_IS_NOT_CANDIDATE_SPECIFIC_TRAINING_SUPPORT",
    },
    "guidance_revalidation": {
        "retrieved_date": "2026-08-29",
        "peft": {
            "repository": "huggingface/peft",
            "main_revision": "9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe",
            "documentation": "https://huggingface.co/docs/peft/main/package_reference/lora",
            "observations": [
                "LoraConfig exposes use_rslora.",
                "QLoRA-style PEFT guidance uses target_modules=all-linear.",
            ],
        },
        "transformers": {
            "repository": "huggingface/transformers",
            "main_revision": "42ca97014c85d71a88ad60d55f08cb9fb4d26e2c",
            "documentation": "https://huggingface.co/docs/transformers/main/quantization/bitsandbytes",
            "observations": [
                "Current bitsandbytes integration describes QLoRA as 4-bit quantization with trainable LoRA weights.",
                "Current guidance recommends explicit 4-bit quantization configuration; generic availability does not prove one MSTR finalist is supported.",
            ],
        },
        "unsloth": {
            "repository": "unslothai/unsloth",
            "main_revision": "e1653bcd1da874466da48ee5360ff60fc10d7973",
            "documentation": "https://www.unsloth.ai/pricing",
            "observations": [
                "Current public product guidance advertises 4-bit and 16-bit LoRA support.",
                "This generic statement is not exact-backbone support evidence.",
            ],
        },
    },
    "required_method_arms": [
        {
            "method": "LORA_16BIT",
            "precision": "SIXTEEN_BIT",
            "rslora": False,
            "base_quantization_bits": None,
            "preflight_status": "REVALIDATION_REQUIRED",
        },
        {
            "method": "LORA_16BIT_RSLORA",
            "precision": "SIXTEEN_BIT",
            "rslora": True,
            "base_quantization_bits": None,
            "preflight_status": "REVALIDATION_REQUIRED",
        },
        {
            "method": "QLORA_4BIT",
            "precision": "FOUR_BIT_BASE",
            "rslora": False,
            "base_quantization_bits": 4,
            "preflight_status": "REVALIDATION_REQUIRED",
        },
        {
            "method": "QLORA_4BIT_RSLORA",
            "precision": "FOUR_BIT_BASE",
            "rslora": True,
            "base_quantization_bits": 4,
            "preflight_status": "REVALIDATION_REQUIRED",
        },
    ],
    "candidate_support_rule": {
        "default": "REVALIDATION_REQUIRED",
        "supported_requires": [
            "exact finalist immutable backbone revision",
            "exact adapter target-module compatibility",
            "exact PEFT/Transformers/Unsloth revisions used for the cell",
            "exact quantization/backend compatibility for 4-bit arms",
            "exact execution environment and hardware compatibility",
        ],
        "unsupported_requires": [
            "exact unsupported reason",
            "support evidence identity",
            "framework/backbone revision identity",
        ],
    },
    "comparability_requirements": [
        "same immutable base revision",
        "same admitted dataset manifest",
        "same token/update budget",
        "same seed policy",
        "same context and environment identity",
        "same evaluation identity and checkpoints",
        "same export and canonical-Q4 regression path",
        "DVCR and TTVC reported together where applicable",
        "direct coding/FIM, Q4 regression, stability, cost, and reproducibility retained",
    ],
    "method_selection": "UNSELECTED",
    "execution_status": "NOT_EXECUTED",
    "authority_boundary": {
        "model_weight_access": False,
        "model_execution": False,
        "training_execution": False,
        "weight_changing_training": False,
        "paid_compute": False,
        "paid_model_api": False,
        "large_dataset_ingestion": False,
        "quantization_execution": False,
        "production_release": False,
    },
}
write_json(ROOT / "artifacts/manifests/B028-method-tournament-preflight.json", manifest)

write_text(
    ROOT / "docs/training/Q4_PROMOTION_CONTRACT.md",
    """# MSTR Q4 Promotion Contract v0

## Scope

This contract freezes the release-relevant Q4 checkpoint-promotion rule and the training-method tournament preflight required by MSTR-000B B028. It is a contract/preflight artifact only. It does not execute a model, acquire model weights, quantize a model, train a model, spend paid compute, or authorize any later external effect.

## Product Rule

Q4 behavior is product behavior. After every material weight-changing stage, the checkpoint MUST be exported and evaluated through the canonical release-relevant Q4 path before it may become the parent of another material weight-changing stage.

```text
SOURCE CHECKPOINT
-> VERIFY SOURCE CHECKPOINT SHA-256
-> MERGE / EXPORT MASTER
-> VERIFY MERGED-MASTER SHA-256
-> PIN EXPORT TOOL + REVISION + RECIPE HASH
-> BUILD CANONICAL Q4
-> VERIFY CANONICAL-Q4 SHA-256
-> PIN QUANTIZER + REVISION + RECIPE HASH
-> RUN REQUIRED Q4 REGRESSION
-> RUN APPLICABLE UNIVERSAL-LAPTOP HARD GATE
-> Q4PromotionRecord = PROMOTED | REJECTED
```

A BF16/FP16/master-only improvement is never sufficient promotion evidence.

## Fail-Closed Promotion

`mstr.q4-promotion.v0` is `PROMOTED` only when all required identity and integrity fields are present, artifact integrity is `PASS`, Q4 regression is `PASS`, and the universal-laptop gate is either `PASS` or explicitly `NOT_REQUIRED` with an auditable reason and evidence identity. A promoted record has no rejection reasons.

Any failed or ambiguous mandatory gate produces `REJECTED` with at least one exact rejection reason. Missing hashes, missing tool revisions, missing recipe hashes, failed integrity, failed Q4 regression, or an applicable failed laptop gate cannot be overridden by a master-checkpoint score.

Consumers MUST determine parent eligibility by requiring `promotion_status == PROMOTED`. This contract does not create training authority; it only constrains a later separately authorized training sequence.

## Equivalent Method Tournament Preflight

Every concrete finalist tournament MUST include every technically supported arm from this exact set:

1. `LORA_16BIT`
2. `LORA_16BIT_RSLORA`
3. `QLORA_4BIT`
4. `QLORA_4BIT_RSLORA`

Equivalent cells bind the same immutable base revision, admitted dataset manifest, token/update budget, seed policy, context/environment identity, evaluation identity/checkpoints, export recipe, and canonical-Q4 regression path.

A method is not selected by framework convenience. Method selection later consumes DVCR, TTVC, direct coding/FIM, Q4 regression, stability, cost, and reproducibility evidence.

## Candidate-Specific Support Is Not Inferred

Generic framework documentation is not sufficient proof that a concrete MSTR finalist supports one arm. Before execution, every finalist/arm cell MUST be revalidated against the exact backbone revision and exact framework/tool revisions. A supported cell records exact support evidence. An unsupported cell records an exact incompatibility reason and evidence identity. If support is unresolved, the cell remains `REVALIDATION_REQUIRED` and cannot execute.

B009 remains source-level compatibility evidence only; it explicitly does not convert generic trainer/converter presence into an executed candidate-specific pass.

## Guidance Snapshot — 2026-08-29

The B028 preflight revalidated current public guidance immediately before implementation:

- PEFT `main` revision `9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe`; current LoRA documentation exposes `use_rslora` and documents QLoRA-style `target_modules=all-linear`.
- Transformers `main` revision `42ca97014c85d71a88ad60d55f08cb9fb4d26e2c`; current bitsandbytes documentation describes QLoRA as 4-bit quantization with trainable LoRA weights.
- Unsloth `main` revision `e1653bcd1da874466da48ee5360ff60fc10d7973`; current public guidance advertises 4-bit and 16-bit LoRA support.

These observations justify preserving all four tournament arms in the preflight. They do not prove any specific MSTR candidate supports a given arm.

## Authority Boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
TRAINING_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_COMPUTE = NONE
PAID_MODEL_API = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
B028_AUTHORITY = CONTRACT_AND_PREFLIGHT_ONLY
```
""",
)

write_text(
    ROOT / "evidence/mstr-000b/B028-training-methods.md",
    """# B028 — Q4 Promotion and Training-Method Preflight Evidence

**Task:** `B028`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `9d5908016b2b8775eaf86dbcebb89683f52e1f90`
**Entry gate run:** `33250934988`
**Entry gate job:** `99096373017`

## Entry Gate

The post-B025 canonical frontier proof verified clean task drift across 34 MSTR-000B nodes and evaluated B028 against exact canonical main. B028 was `PENDING`, `eligible=true`, required no external-effect authority, and had no failure reasons. Its exact prerequisites B009, B014, and B022 were canonical.

```text
ENTRY_GATE_TASK = B028
ENTRY_GATE_CANONICAL_MAIN = 9d5908016b2b8775eaf86dbcebb89683f52e1f90
ENTRY_GATE_ELIGIBLE = true
```

## Frozen Outputs

B028 freezes two runtime/design contracts plus the requested preflight artifacts:

- `mstr.training-method-cell.v0`
- `mstr.q4-promotion.v0`
- `artifacts/manifests/B028-method-tournament-preflight.json`
- `docs/training/Q4_PROMOTION_CONTRACT.md`

The training-method contract encodes the four mandatory tournament arms and binds method identity to 16-bit versus 4-bit base precision, rsLoRA state, and quantization metadata. An `UNSUPPORTED` cell requires an exact unsupported reason; a cell may become ready for later authorized execution only after candidate-specific support is proven.

The Q4-promotion contract fails closed: `PROMOTED` requires verified artifact integrity, passing Q4 regression, a passing or explicitly not-required universal-laptop gate, complete hashes/tool/recipe identity, and zero rejection reasons. A rejected record requires at least one reason.

## Current Guidance Revalidation

Revalidated on 2026-08-29 immediately before B028 implementation:

- PEFT LoRA documentation and repository `main` revision `9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe`.
- Transformers bitsandbytes documentation and repository `main` revision `42ca97014c85d71a88ad60d55f08cb9fb4d26e2c`.
- Unsloth public 4-bit/16-bit LoRA guidance and repository `main` revision `e1653bcd1da874466da48ee5360ff60fc10d7973`.

The guidance confirms that rsLoRA and 4-bit/16-bit adapter paths remain live framework concepts. It does not establish candidate-specific support. B009 already records architecture-specific unresolved cells, so every concrete finalist/arm remains `REVALIDATION_REQUIRED` until exact later evidence proves support or an exact unsupported reason.

## Non-Execution Evidence

No training-method arm was executed. No model was loaded. No model artifact was acquired, converted, quantized, or inferred. No dataset was ingested. No paid service or GPU compute was used by B028 implementation.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
TRAINING_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_COMPUTE = NONE
PAID_MODEL_API = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
B028_AUTHORITY = CONTRACT_AND_PREFLIGHT_ONLY
```

B028 is not `COMPLETE_CANONICAL` at implementation time. Canonical completion requires the normal exact-head review/merge and separate closeout lifecycle.
""",
)

write_text(
    ROOT / "tests/contract/test_training_promotion_contract.py",
    """from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"


def _fixture(kind: str, name: str) -> dict[str, object]:
    return json.loads((FIXTURES / kind / f"{name}.json").read_text(encoding="utf-8"))


def test_training_method_cell_freezes_exact_four_method_semantics() -> None:
    base = _fixture("valid", "mstr-training-method-cell-v0")
    cases = (
        ("LORA_16BIT", "SIXTEEN_BIT", False, None),
        ("LORA_16BIT_RSLORA", "SIXTEEN_BIT", True, None),
        (
            "QLORA_4BIT",
            "FOUR_BIT_BASE",
            False,
            {"base_bits": 4, "scheme": "NF4", "tool_id": "bnb", "tool_revision": "fixture"},
        ),
        (
            "QLORA_4BIT_RSLORA",
            "FOUR_BIT_BASE",
            True,
            {"base_bits": 4, "scheme": "NF4", "tool_id": "bnb", "tool_revision": "fixture"},
        ),
    )
    for method, precision, rslora, quantization in cases:
        value = copy.deepcopy(base)
        value["method"] = method
        value["precision"] = precision
        value["rslora"] = rslora
        value["quantization"] = quantization
        validate_instance("mstr-training-method-cell-v0", value)


def test_training_method_cross_binding_fails_closed() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["method"] = "LORA_16BIT"
    assert validation_errors("mstr-training-method-cell-v0", value)


def test_unsupported_method_requires_exact_reason_and_terminal_status() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["support_status"] = "UNSUPPORTED"
    value["unsupported_reason"] = "exact fixture incompatibility"
    value["status"] = "UNSUPPORTED"
    validate_instance("mstr-training-method-cell-v0", value)

    value["unsupported_reason"] = None
    assert validation_errors("mstr-training-method-cell-v0", value)


def test_execution_ready_requires_candidate_specific_support() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["status"] = "READY_FOR_AUTHORIZED_EXECUTION"
    assert validation_errors("mstr-training-method-cell-v0", value)
    value["support_status"] = "SUPPORTED"
    validate_instance("mstr-training-method-cell-v0", value)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    (
        ("artifact_integrity_status", "FAIL"),
        ("q4_regression_result", "FAIL"),
        ("universal_laptop_gate_result", "FAIL"),
    ),
)
def test_q4_promotion_hard_gates_fail_closed(field: str, bad_value: str) -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value[field] = bad_value
    assert validation_errors("mstr-q4-promotion-v0", value)


def test_q4_not_required_laptop_gate_requires_reason() -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value["universal_laptop_gate_result"] = "NOT_REQUIRED"
    value["universal_laptop_gate_not_required_reason"] = "not applicable to this frozen stage"
    validate_instance("mstr-q4-promotion-v0", value)
    value["universal_laptop_gate_not_required_reason"] = None
    assert validation_errors("mstr-q4-promotion-v0", value)


def test_rejected_q4_record_requires_reason() -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value["promotion_status"] = "REJECTED"
    assert validation_errors("mstr-q4-promotion-v0", value)
    value["rejection_reasons"] = ["q4.regression_failed"]
    validate_instance("mstr-q4-promotion-v0", value)


def test_b028_manifest_contains_exact_required_arms_without_selection() -> None:
    manifest = json.loads(
        (ROOT / "artifacts" / "manifests" / "B028-method-tournament-preflight.json").read_text(
            encoding="utf-8"
        )
    )
    arms = manifest["required_method_arms"]
    assert {arm["method"] for arm in arms} == {
        "LORA_16BIT",
        "LORA_16BIT_RSLORA",
        "QLORA_4BIT",
        "QLORA_4BIT_RSLORA",
    }
    assert len(arms) == 4
    assert all(arm["preflight_status"] == "REVALIDATION_REQUIRED" for arm in arms)
    assert manifest["method_selection"] == "UNSELECTED"
    assert manifest["execution_status"] == "NOT_EXECUTED"
    assert manifest["authority_boundary"]["model_weight_access"] is False
    assert manifest["authority_boundary"]["training_execution"] is False
    assert manifest["authority_boundary"]["weight_changing_training"] is False


def test_b028_guidance_snapshot_is_exact_and_not_candidate_support() -> None:
    manifest = json.loads(
        (ROOT / "artifacts" / "manifests" / "B028-method-tournament-preflight.json").read_text(
            encoding="utf-8"
        )
    )
    guidance = manifest["guidance_revalidation"]
    assert guidance["retrieved_date"] == "2026-08-29"
    assert guidance["peft"]["main_revision"] == "9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe"
    assert guidance["transformers"]["main_revision"] == "42ca97014c85d71a88ad60d55f08cb9fb4d26e2c"
    assert guidance["unsloth"]["main_revision"] == "e1653bcd1da874466da48ee5360ff60fc10d7973"
    assert manifest["candidate_support_rule"]["default"] == "REVALIDATION_REQUIRED"


def test_b028_evidence_preserves_non_execution_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B028-training-methods.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B028" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "QUANTIZATION_EXECUTION = NONE" in evidence
    assert "TRAINING_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B028_AUTHORITY = CONTRACT_AND_PREFLIGHT_ONLY" in evidence
""",
)
