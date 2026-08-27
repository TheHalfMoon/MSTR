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

However, the public Hugging Face page requires login and acceptance of Gemma conditions. B005 did **not** accept those terms. Consequently the current full main revision remains intentionally unresolved in the discovery manifest rather than being guessed from another ref.

```text
ACCESS_GATE = CLICKTHROUGH_AND_LOGIN_REQUIRED
CURRENT_FULL_REVISION = UNRESOLVED_WITHOUT_TERMS_ACCEPTANCE
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

The public tree exposed the current short revision `c57bdae`, but B005 did not obtain a trustworthy full SHA from the metadata surface used here. The manifest therefore records `SHORT_SHA_ONLY`; B006 must pin an exact immutable full revision before any serious classification or later access envelope.

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
5. pin a full immutable LFM2.5 revision before any later serious admission/access decision;
6. preserve CodeGemma's gated state without accepting terms absent explicit authority;
7. keep BitNet's 4K context mismatch visible unless later evidence proves an acceptable path.

B006 itself creates no weight-access authority. Any later model artifact access remains governed by B010/B011 and the exact canonical authority chain.

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
