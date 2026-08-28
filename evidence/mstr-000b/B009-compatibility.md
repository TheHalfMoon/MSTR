# B009 — Candidate Trainability / Conversion / Runtime Compatibility

**Workstream:** MSTR-000B
**Task:** B009
**State:** IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT
**Canonical main at execution:** `dd6c7a9b163f1f34e6cc3570da234078d39f4fce`
**Decision artifact:** `artifacts/decisions/B009-training-runtime-compatibility.json`

B009 is a metadata/code/docs compatibility freeze only. It does not access model weights, download tokenizer artifacts, execute models, run conversion or quantization, perform training, accept gated terms, use paid compute, or ingest a large dataset.

## Exact entry evidence

```text
ENTRY_GATE_TASK = B009
ENTRY_GATE_CANONICAL_MAIN = dd6c7a9b163f1f34e6cc3570da234078d39f4fce
ENTRY_GATE_RUN = 33156075625
ENTRY_GATE_JOB = 98799035575
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

## Exact framework source pins

```text
TRANSFORMERS = huggingface/transformers@a8e8d144f6b8e71b93678a274b65d3a319f71921
UNSLOTH      = unslothai/unsloth@411b40615ac88ac657497e5ca9e9da9b334d841e
PEFT         = huggingface/peft@13414e66235139fad4102dfd3c9502958dbdc92b
TRL          = huggingface/trl@89bfc6a54a263bee77fee55aba177a75c8aecf55
LLAMA_CPP    = ggml-org/llama.cpp@d077b4c21466cfad678b07b05b557599f4db3974
```

Every cited source path was re-fetched at the pinned SHA by the B009 builder before materialization.

## Interpretation policy

```text
SOURCE_REGISTERED != RUNTIME_PASS
GENERIC_PATH != EXACT_MODEL_PASS
CONVERTER_SOURCE != CONVERSION_PASS
CONVERTER_SOURCE != QUANTIZATION_PASS
TRAINER_SOURCE != TRAINABILITY_PASS
B009_SOURCE_EVIDENCE != CANDIDATE_PROMOTION_AUTHORITY
```

## Serious candidate matrix

| Candidate | Role | Transformers | Unsloth | PEFT default target | llama.cpp | Main qualification hazards |
|---|---|---|---|---|---|---|
| `granite-4.1-3b` | foundation | SOURCE_REGISTERED | DIRECT_FAMILY_SOURCE | none observed | CONVERTER_CLASS_REGISTERED | PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_GRANITE |
| `mellum-4b` | foundation | SOURCE_REGISTERED | SOURCE_AWARE_GENERIC_PATH | none observed | CONVERTER_CLASS_REGISTERED | FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED; PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_MELLUM |
| `ministral-3-3b` | foundation | SOURCE_REGISTERED | NO_DIRECT_SOURCE_HIT_IN_PINNED_REVIEW | none observed | CONVERTER_CLASS_REGISTERED | TEXT_VS_VISION_COMPONENT_SCOPE_REQUIRED; PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_MINISTRAL3 |
| `qwen2.5-coder-1.5b` | control | SOURCE_REGISTERED | DIRECT_FAMILY_SOURCE | q_proj,v_proj | CONVERTER_CLASS_REGISTERED | FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED |
| `qwen3-4b` | control | SOURCE_REGISTERED | DIRECT_FAMILY_SOURCE | q_proj,v_proj | CONVERTER_CLASS_REGISTERED | FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED |
| `qwen3.5-0.8b-control` | control | SOURCE_REGISTERED | SOURCE_AWARE_GENERIC_PATH | none observed | CONVERTER_CLASS_REGISTERED | HYBRID_ATTENTION_TARGET_MODULE_COVERAGE_REQUIRED; MULTIMODAL_COMPONENT_SCOPE_REQUIRED; FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED; PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_QWEN3_5 |
| `qwen3.5-2b` | foundation | SOURCE_REGISTERED | SOURCE_AWARE_GENERIC_PATH | none observed | CONVERTER_CLASS_REGISTERED | HYBRID_ATTENTION_TARGET_MODULE_COVERAGE_REQUIRED; MULTIMODAL_COMPONENT_SCOPE_REQUIRED; FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED; PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_QWEN3_5 |
| `qwen3.5-4b` | foundation | SOURCE_REGISTERED | SOURCE_AWARE_GENERIC_PATH | none observed | CONVERTER_CLASS_REGISTERED | HYBRID_ATTENTION_TARGET_MODULE_COVERAGE_REQUIRED; MULTIMODAL_COMPONENT_SCOPE_REQUIRED; FIM_SPECIAL_TOKEN_EXPORT_PRESERVATION_REQUIRED; PEFT_DEFAULT_TARGET_MAPPING_NOT_OBSERVED_FOR_QWEN3_5 |
| `smollm3-3b` | foundation | SOURCE_REGISTERED | NO_DIRECT_SOURCE_HIT_IN_PINNED_REVIEW | none observed | CONVERTER_CLASS_REGISTERED | UNSLOTH_DIRECT_FAMILY_SUPPORT_UNPROVEN |
| `yi-coder-1.5b` | control | SOURCE_REGISTERED | GENERIC_LLAMA_PATH | q_proj,v_proj | CONVERTER_CLASS_REGISTERED | GENERIC_LLAMA_PATH_REQUIRES_EXACT_MODEL_QUALIFICATION |

All ten rows remain execution-unqualified in B009. Source presence can schedule later qualification; it cannot replace it.

## Current source findings

- Transformers has pinned native source paths for all ten serious architecture families used here, including Mellum, Ministral3, Qwen3.5 and SmolLM3.
- Unsloth has direct family modules for Granite, Qwen2 and Qwen3; Qwen3.5-aware loader logic is present, while no direct dedicated module was established by this pinned review for Ministral3 or SmolLM3. No-source-hit is not treated as incompatibility.
- PEFT pinned defaults include `llama`, `qwen2`, and `qwen3` LoRA targets (`q_proj`, `v_proj`). No default mapping is promoted for Granite, Mellum, Ministral3, Qwen3.5 or SmolLM3; exact module coverage must be inspected later.
- TRL SFTTrainer accepts generic Transformers/PEFT model objects. That is orchestration capability, not candidate-specific trainability proof.
- llama.cpp pinned converter registry contains the model classes needed by the serious set. This is converter-source evidence only; conversion, quantization and runtime execution remain unexecuted.

## Architecture and export restrictions

- Qwen3.5: hybrid attention plus integrated multimodal components require explicit adapter-target coverage and text/vision training/export scope. Partial PEFT target matches cannot be interpreted as sufficient coverage.
- Ministral3: text-only versus integrated vision-component scope must be explicit before training/export claims.
- Mellum, Qwen2.5-Coder, Qwen3 and Qwen3.5: FIM/code-special-token preservation must be verified through save/export/conversion paths.
- Granite: source support exists, but the pinned PEFT default mapping does not establish exact Granite 4.1 target-module coverage.
- SmolLM3: Transformers and llama.cpp converter source are present; direct Unsloth family support was not established in this review and remains an execution-qualification question.
- Yi-Coder: current canonical record identifies a Llama-compatible text architecture; generic Llama paths remain generic and require exact-model qualification.

## Reference / non-serious records

The canonical inventory contains 9 additional records. They are retained in the decision artifact as `INFORMATIONAL_REFERENCE_ONLY`. B009 cannot promote them regardless of technical source evidence; canonical role/rights decisions remain authoritative.

The prior LFM2.5 identity blocker is obsolete: canonical B006 records now contain full immutable upstream revisions. Both LFM2.5 records remain reference-only because of their current rights decisions, not because identity is unresolved.

## B010 handoff

B009 does not create `qualification_candidates[]` or `new_weight_access_required_candidates[]`. B010 owns those lists after reconciling this source-level matrix with canonical B006 rights/provenance and B007/B008 evidence.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
CONVERSION_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
TRAINING_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B009 remains unchecked / not complete canonical until exact-head qualification, independent review, implementation merge, separate canonical closeout, and post-closeout exact-main verification.
