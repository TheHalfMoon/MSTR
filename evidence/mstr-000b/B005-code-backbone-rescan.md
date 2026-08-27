# B005 — Mission-Aligned Compact Backbone Metadata Rescan

**Workstream:** MSTR-000B  
**Task:** B005  
**State:** IMPLEMENTATION_COMPLETE / NOT_COMPLETE_CANONICAL  
**Canonical main at execution:** `e1b3cbd74ae0a74a80e3f345faef56da13818149`  
**Branch:** `research/000b-b005-code-backbone-rescan`  
**Discovery manifest:** `artifacts/manifests/B005-code-backbone-discovery.json`

This is a metadata-only discovery result. It does not admit, acquire, execute, fine-tune, quantize, select, or authorize any model.

## Entry gate

The exact B005 readiness requirements were manually verified before execution:

```text
METADATA_ONLY_NETWORK_SCOPE = CONFIRMED
MODEL_WEIGHT_ACCESS_NEEDED = NO
CANDIDATE_SCHEMA_READ = YES
CURRENT_T022_CANDIDATE_DECISION_READ = YES
B002_REQUIRED_FOR_B005 = NO
```

The scan used public model-card/repository/tree/commit/config metadata only. It did not download model weights or tokenizer artifacts, accept gated terms, run inference, use paid compute, or ingest a large dataset.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

## Canonical inputs

B005 re-read the live candidate contract and the current T022 static admission result before searching:

- `schemas/candidate-record.schema.json`
- `artifacts/decisions/T022-static-candidate-admission.json`
- `specs/002-code-model-supremacy-foundation/plan.md`
- `specs/002-code-model-supremacy-foundation/tasks.md`

T022 currently carries eight candidate/control records. B005 treats those records as prior evidence, not immutable truth: current upstream metadata was revalidated and material drift/ambiguity is recorded below.

## Search method

The rescan deliberately did **not** exclude code-specialized foundations. It covered:

1. all eight T022 candidates/controls;
2. the mandatory `JetBrains/Mellum-4b-base` review;
3. compact code-specialized foundations omitted from the prior candidate set;
4. compact general/hybrid foundations with plausible universal-laptop relevance;
5. explicit rights/gating/runtime/context hazards that must survive later fail-closed gates.

For each row B005 sought current repository identity, revision, base/post-training provenance, license/gating observation, context, parameter observation, and intended use. A value that could not be established without gated acceptance or stronger evidence is marked unresolved rather than inferred.

## Existing T022 set — current observations

| Upstream | Revision status | Current metadata observation | B006 consequence |
|---|---|---|---|
| `Qwen/Qwen3.5-2B-Base` | exact full SHA preserved | Apache-2.0, 2B, 262K context; current card says `Pre-training & Post-training` despite `Base` repo name | revalidate clean-foundation provenance |
| `Qwen/Qwen3.5-4B-Base` | exact full SHA preserved | Apache-2.0, 4B, 262K context; same `Pre-training & Post-training` ambiguity | revalidate clean-foundation provenance |
| `mistralai/Ministral-3-3B-Base-2512` | exact full SHA preserved | base pre-trained; 3.4B language + 0.4B vision; 256K-class context | reverify exact license/access/component implications |
| `Qwen/Qwen3-4B-Base` | exact full SHA preserved | Apache-2.0, pretraining, 4B, 32K | no new B005 blocker |
| `ibm-granite/granite-4.1-3b-base` | exact full SHA preserved | Apache-2.0, 3B, 131K trained sequence; general + FIM/code use | keep extension claims separate from trained sequence |
| `HuggingFaceTB/SmolLM3-3B-Base` | exact full SHA preserved | Apache-2.0; explicit base after pretraining; 3B; config 65,536 with YaRN extension described separately | preserve native-vs-extrapolated context distinction |
| `Qwen/Qwen2.5-Coder-1.5B` | exact full SHA preserved | Apache-2.0; code pretraining checkpoint; 1.54B; current config 32K | retain as code-specialized control; do not treat optional long-context instructions as native config |
| `01-ai/Yi-Coder-1.5B` | exact full SHA preserved | Apache-2.0; code-specialized; 128K; repo/model-size metadata disagree on parameter labeling | revalidate parameter count and exact lineage |

### Material drift / ambiguity in the existing set

The most important existing-record finding is the Qwen3.5 provenance discrepancy. Both current `Base` cards describe their training stage as **Pre-training & Post-training**. B005 does not decide whether this makes either checkpoint ineligible; it does require B006 to reconcile the upstream statement before either is treated as a clean foundation candidate.

Yi-Coder likewise keeps its existing record but is flagged for parameter/provenance reconciliation rather than silently normalizing conflicting public metadata.

## Newly relevant B006 review set

### 1. `JetBrains/Mellum-4b-base` — mandatory and mission-aligned

Observed current revision:

```text
83cce2605fbdf6a3868627e9b0a5924e0072b94d
```

Public metadata describes Mellum as JetBrains' open-source **base code model**, Apache-2.0, approximately 4B parameters, with an 8,192-token context and software-development/code-completion intent.

This is the clearest B005 gap in T022: a compact, permissively licensed, directly code-specialized base was absent from the earlier serious candidate inventory. B005 therefore requires explicit B006 classification rather than continued category omission.

Sources:
- https://huggingface.co/JetBrains/Mellum-4b-base
- https://huggingface.co/JetBrains/Mellum-4b-base/tree/main

### 2. `bigcode/starcoder2-3b`

Observed current revision:

```text
733247c55e3f73af49ce8e9c7949bf14af205928
```

A compact code-pretrained 3B model with a 16K-class context. Its `bigcode-openrail-m` license is not equivalent to Apache/MIT and therefore requires the ordinary B006 rights decision rather than a discovery-time assumption.

Sources:
- https://huggingface.co/bigcode/starcoder2-3b
- https://huggingface.co/bigcode/starcoder2-3b/tree/main

### 3. `stabilityai/stable-code-3b`

Observed current revision:

```text
5cee3fa2905e7a03c4a1b0bc02f39da7ceaa6cb5
```

Public metadata identifies a foundational code model for completion/FIM and downstream fine-tuning, approximately 2.8B parameters with a 16K context. The Stability model-license terms are nonstandard for MSTR's primary redistribution gate, so B006 must make the exact rights classification.

Sources:
- https://huggingface.co/stabilityai/stable-code-3b
- https://huggingface.co/stabilityai/stable-code-3b/tree/main

### 4. `google/codegemma-2b`

CodeGemma 2B is directly mission-aligned: a pre-trained code model built on Gemma and further trained primarily on code/math/synthetic data for code completion/FIM-style tasks.

At the initial scan, the public Hugging Face page required login and acceptance of Gemma conditions, so B005 did **not** accept those terms and left the full revision unresolved. The canonical refresh below later resolved the exact repository SHA from the public metadata API without accepting terms; the access gate itself remains unchanged.

```text
ACCESS_GATE = CLICKTHROUGH_AND_LOGIN_REQUIRED
INITIAL_SCAN_FULL_REVISION = UNRESOLVED_WITHOUT_TERMS_ACCEPTANCE
REFRESHED_PUBLIC_METADATA_REVISION = e7583edabd3dd48a9c705974a9456852f1205ab1
```

This is a B006 rights/accountless-release issue, not authority to cross the gate.

Source:
- https://huggingface.co/google/codegemma-2b

### 5. `tiiuae/Falcon-H1-3B-Base`

Observed current revision:

```text
c096902c69be0eed2e5369d3420a8bb960d293e1
```

A compact general base using a hybrid Transformer/SSM architecture with 131K-class context. Its Falcon license and architecture/runtime path both require explicit later review. B005 records it because architecture efficiency may matter to the universal-laptop objective; it does not declare it primary-eligible.

Sources:
- https://huggingface.co/tiiuae/Falcon-H1-3B-Base
- https://huggingface.co/tiiuae/Falcon-H1-3B-Base/tree/main

### 6. `microsoft/bitnet-b1.58-2B-4T-bf16`

Observed current revision:

```text
9e5d75862231a20855f2fecdee031f9c2e961864
```

MIT-licensed and highly relevant to low-resource deployment research, but the BF16 training/fine-tuning master currently exposes a 4,096-token native context. That is **below MSTR's 8K reference context** and is therefore a material product mismatch unless a later task proves an acceptable extension. The native BitNet/custom runtime path is also a B009 compatibility risk.

Sources:
- https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-bf16
- https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-bf16/tree/main

### 7. `LiquidAI/LFM2.5-2.6B-Base`

Public metadata identifies a pre-trained, text-only 2.69B base checkpoint for fine-tuning, designed for on-device use with a 131,072-token context. This makes it relevant to the universal-laptop search even though it is not code-specialized.

The initial scan exposed only the short revision `c57bdae`. The canonical refresh below later resolved that same commit identity to full SHA `c57bdaed1ef166fe3095dda07f4a5e789ad5321e` through public metadata. This is identity resolution, not upstream revision drift.

The `lfm1.0` license is nonstandard and requires an exact B006 rights decision.

Sources:
- https://huggingface.co/LiquidAI/LFM2.5-2.6B-Base
- https://huggingface.co/LiquidAI/LFM2.5-2.6B-Base/tree/main

## Main conclusions

### Finding 1 — the previous scan was not sufficiently mission-aligned

`JetBrains/Mellum-4b-base` demonstrates a concrete omission: the existing static candidate set can contain general bases and lightweight code controls while still miss a serious compact code-specialized base. Future discovery must therefore search **code-specialized and general foundations under the same hard rights/product gates**.

### Finding 2 — discovery must not be confused with rights admission

StarCoder2, Stable Code, CodeGemma, Falcon-H1 and LFM2.5 are relevant enough to review, but their license/access terms are not automatically compatible with MSTR's worldwide/accountless derivative-release policy. B005 intentionally carries them forward as review obligations, not approved candidates.

### Finding 3 — existing records can become uncertain

The Qwen3.5 current-card training-stage statements and Yi-Coder metadata discrepancy show why upstream revalidation is required even for already-known candidates. A prior static admission record cannot overwrite current conflicting evidence.

### Finding 4 — universal-laptop constraints remain hard gates

BitNet is especially interesting for memory/compute efficiency, but its observed 4K native context currently misses the 8K reference requirement. Novel efficiency does not waive product constraints.

## B006 handoff

B006 must create/reconcile candidate records and classify every newly relevant model as one of the canonical allowed roles/statuses under the existing candidate/rights contract. At minimum B006 must:

1. explicitly classify Mellum rather than omit it;
2. perform exact rights decisions for StarCoder2, Stable Code, CodeGemma, Falcon-H1 and LFM2.5;
3. resolve the Qwen3.5 clean-foundation provenance ambiguity;
4. reconcile Yi-Coder parameter/provenance metadata;
5. preserve the full immutable LFM2.5 revision resolved by the canonical refresh and keep its nonstandard-license review fail-closed;
6. preserve CodeGemma's gated state without accepting terms absent explicit authority;
7. keep BitNet's 4K context mismatch visible unless later evidence proves an acceptable path.

B006 itself creates no weight-access authority. Any later model artifact access remains governed by B010/B011 and the exact canonical authority chain.

## Canonical current-state refresh — 2026-08-27

This refresh is executed only because the historical B005 implementation predates the canonical B002/B003 machine-gate enforcement and its canonical-input binding no longer matches current `main`. It does not replace the historical evidence; it rebinds B005 to current canonical repository inputs and current public upstream metadata before closeout.

### Exact-main entry gate

```text
ENTRY_GATE_TASK = B005
ENTRY_GATE_CANONICAL_MAIN = 986b174b2bf79ce53a3e67b9b02c55cbe6981303
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_RUN = 33103275261
ENTRY_GATE_JOB = 98626338825
```

The entry-gate run also proved B004 terminal, canonical task drift clean, and the frozen repository gates green on the same exact canonical main.

### Refresh boundary

```text
PUBLIC_METADATA_ENDPOINT_CLASS = huggingface.co/api/models/<repo>
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
NEW_AUTHORITY_CREATED = NO
```

The refresh queries only public model metadata and records exact upstream repository revisions. It never calls model-file `resolve` endpoints and never downloads model or tokenizer artifacts.

### Newly serious compact review cells

- `LiquidAI/LFM2.5-1.2B-Base` — exact current revision `7453bca97ca1e67754c4035a4b4c584e1c9dd725`; pre-trained text-only 1.17B base, 32,768 context, on-device-oriented; nonstandard Liquid license metadata requires fail-closed B006 rights review.
- `Qwen/Qwen3.5-0.8B-Base` — exact current revision `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`; 0.8B language model, 262,144 native context, Apache-2.0; the card simultaneously says pre-trained-only and `Pre-training & Post-training`, so B006 must reconcile provenance and vision-component cost before primary admission.

Both are added to `newly_relevant_for_b006`. Neither is admitted or authorized for weight access by B005.

### Frontier references screened out before B006 qualification

- `zai-org/GLM-5.3-Flash` — exact current revision `04c4e9e95c5da8862dced7e5056455116f83a7e0`; MIT; 320B total / 18B active; 1,048,576 configured context. Useful coding/agentic reference, but far outside the universal-laptop primary product scale.
- `moonshotai/Kimi-K2-Base` — exact current revision `ce72df012259dcc55d945e890f815fe7ef69159c`; modified MIT; 1T total / 32B active; 131,072 context. It is a foundation checkpoint but is likewise outside the primary product scale.

These rows are discovery references only and are intentionally **not** added to `newly_relevant_for_b006`; no B012 qualification burden or access implication is created for them.

### Existing-row exact-revision revalidation

The refresh re-queried current public metadata for every pre-existing B005 discovery row. It distinguishes actual upstream `main` movement from identity resolution when the initial scan had only an unresolved or short SHA.

- `google/codegemma-2b`: identity resolved from `UNRESOLVED` to `e7583edabd3dd48a9c705974a9456852f1205ab1` via public metadata; license tag `gemma`; gated `manual`; no terms accepted. This is not evidence of upstream revision drift.
- `microsoft/bitnet-b1.58-2B-4T-bf16`: actual upstream revision drift `9e5d75862231a20855f2fecdee031f9c2e961864` -> `276681394656abdadb8e80e5b2c3db5e5d7fcaff`; public metadata license tag `mit`; gated `false`.
- `LiquidAI/LFM2.5-2.6B-Base`: short SHA `c57bdae` resolved to the same commit identity `c57bdaed1ef166fe3095dda07f4a5e789ad5321e`; public metadata license tag `other`; gated `false`. This is not upstream revision drift.

The refreshed canonical-input binding pins the exact current Git blob SHA for every repository input consumed by B005. Any later drift before merge invalidates the branch and requires re-evaluation.

## Closeout state

B005 implementation artifacts now exist on the feature branch, but B005 is **not** marked `COMPLETE_CANONICAL` in `tasks.md` before governed review and merge.

```text
B005_IMPLEMENTATION = COMPLETE_ON_BRANCH
B005_COMPLETE_CANONICAL = NO
TASK_CHECKBOX_UPDATED = NO
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TRAINING_AUTHORITY_CREATED = NO
NEXT_DEPENDENT_TASK = B006_AFTER_B005_CANONICAL
```
