# B009 — Candidate Trainability / Conversion / Runtime Compatibility

**Workstream:** MSTR-000B  
**Task:** B009  
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL  
**Canonical main at branch creation:** `ead69ae26265b133c782ae8fd2795c126253a3b6`  
**Decision artifact:** `artifacts/decisions/B009-training-runtime-compatibility.json`

B009 is a metadata/code/docs compatibility freeze only. It does not access model weights, download tokenizer artifacts, execute models, run conversion or quantization, perform training, accept gated terms, use paid compute, or ingest a large dataset.

## Provenance binding

The decision is bound to repository inputs without using a self-referential containing-commit field:

```text
B009_BRANCH_BASE_MAIN = ead69ae26265b133c782ae8fd2795c126253a3b6
B005_INPUT_PATH = artifacts/manifests/B005-code-backbone-discovery.json
B005_INPUT_BLOB = daf641bcd10af01a677a69a3a35e0d411ab6488b
B005_EMBEDDED_EXECUTION_BASE = e1b3cbd74ae0a74a80e3f345faef56da13818149
EXACT_REVIEW_HEAD_BINDING = EXTERNAL_GIT_PR_HEAD
```

The B005 embedded `canonical_main_sha` records when B005 itself executed. B009 consumes the exact B005 blob as present in canonical main `ead69ae...`; those identities have different provenance roles.

The exact review head is intentionally established by Git/PR state plus the B009 artifact blob at that head. Embedding the containing commit SHA inside the file would change that commit and become self-referential, so it is not used as a validity rule.

## Exact upstream pins

```text
TRANSFORMERS = huggingface/transformers@01846b52e4b9333577af7e4e19c6d3c0f815ff72
UNSLOTH      = unslothai/unsloth@e42405615e26f626232084b973976f61036e8b2e
PEFT         = huggingface/peft@5779b17b9a67d9b07b5be75053cb1932b939fd9f
TRL          = huggingface/trl@67dfbe211a07a8dd6ebc1a5af5b75152e10add8e
LLAMA_CPP    = ggml-org/llama.cpp@d7a2074112d27649303fa107eb8c94db1ee435f3
```

`SOURCE_REGISTERED` means only that the pinned source contains an implementation/converter/family path. It is not a runtime PASS. `GENERIC_PATH` means a framework may operate through a broad HF/CausalLM interface but the exact candidate was not executed. `UNVERIFIED` is intentionally fail-closed.

## Main findings

### 1. llama.cpp converter evidence is not runtime evidence

The pinned llama.cpp source contains converter-source paths for:

- Mellum;
- StarCoder2;
- StableLM / Stable Code;
- Falcon-H1;
- LFM2;
- BitNet;
- Granite;
- Mistral3 / Ministral-family conversion;
- Qwen-family models;
- Gemma-family models.

These `conversion/*.py` paths prove converter-source presence only. They do **not** prove runtime implementation, successful conversion, quantization quality, tokenizer preservation, or runtime fidelity.

SmolLM3 is separately supported by an explicitly observed runtime source path:

```text
src/models/smollm3.cpp
```

Even that source presence is not exact-revision runtime qualification.

### 2. Unsloth support must be candidate-specific

The pinned Unsloth source has direct family evidence for Falcon-H1, Granite, LFM2, and Qwen3.5-era paths. Direct source evidence was not established in this review for Mellum, StarCoder2, or Stable Code.

```text
UNSLOTH_SOURCE_PRESENT != EXACT_MODEL_TRAINING_PASS
NO_DIRECT_SOURCE_HIT != PROVEN_INCOMPATIBLE
```

Every serious candidate still needs exact-revision train/save/export qualification before B013 admission.

### 3. Hybrid architectures require adapter-target coverage checks

The pinned PEFT main explicitly documents a hybrid-architecture hazard: when some configured `target_modules` match and others do not, unmatched modules may be silently skipped rather than causing total failure.

This is material especially for:

- `tiiuae/Falcon-H1-3B-Base`;
- `LiquidAI/LFM2.5-2.6B-Base`;
- multimodal/mixed-component Ministral training scope.

Granite 4.1 3B is not in this hybrid-warning set: its public config identifies `GraniteForCausalLM` / `model_type=granite`, and its model card describes a dense decoder-only transformer.

Before adapter training, qualification must enumerate exact module names and prove intended adapter coverage. A run that merely starts is insufficient evidence.

## Candidate-specific restrictions

**Ministral-3-3B-Base-2512**
- Multimodal/mixed-component scope must be explicit.
- Text-only versus full-checkpoint training/export cannot be conflated.
- Parameter-accounting and component-cost issues from B005 remain unresolved.

**Granite 4.1 3B Base**
- Public config identifies `GraniteForCausalLM` / `model_type=granite`.
- Model card describes a dense decoder-only transformer; no hybrid PEFT warning is applied.
- Family source evidence exists in Unsloth and llama.cpp converter code.
- Exact 4.1-3B train/save/export/runtime path remains unexecuted.

**Qwen2.5-Coder-1.5B / Mellum / StarCoder2 / Stable Code / CodeGemma**
- FIM and code-special-token preservation is qualification-critical.
- GGUF converter source does not prove FIM-token/export equivalence.

**CodeGemma 2B**
- Exact full revision remains unresolved because public access requires login/clickthrough.
- B009 performs no terms acceptance and creates no access authority.

**Falcon-H1 3B Base**
- Hybrid Transformer/SSM architecture.
- Unsloth and llama.cpp have architecture/family source evidence, but only converter-source evidence is claimed from the cited llama.cpp path.
- PEFT target-module coverage and SSM runtime/export behavior require exact qualification.

**BitNet b1.58 2B4T BF16**
- Native context reported in B005 is 4096, below MSTR's 8192 reference.
- Public usage reports specialized/remote-code handling.
- Generic 4-bit/QLoRA assumptions must not be applied to native 1.58-bit semantics without proof.
- llama.cpp has BitNet converter source; B009 did not execute it or claim runtime support from that converter file.

**LFM2.5 2.6B Base**
- B005 has only a short revision; full immutable SHA remains required.
- Unsloth and llama.cpp have LFM2-family source evidence; the cited llama.cpp evidence is converter-source only.
- Exact LFM2.5 training/export/runtime remains unqualified.

## Framework interpretation policy

```text
TRANSFORMERS_NATIVE_SOURCE != exact candidate load PASS
UNSLOTH_SOURCE != exact train/save/export PASS
PEFT_GENERIC_PATH != correct adapter coverage
TRL_GENERIC_TRAINER != exact candidate trainability PASS
LLAMA_CPP_CONVERTER_SOURCE != runtime implementation PASS
LLAMA_CPP_CONVERTER_SOURCE != conversion PASS
LLAMA_CPP_CONVERTER_SOURCE != quantization PASS
LLAMA_CPP_CONVERTER_SOURCE != runtime-regression PASS
```

B012-equivalent artifact-backed execution is the proper place to turn source-level findings into hard deployment evidence.

## B010 handoff

B009 does not create either of these lists:

```text
qualification_candidates[]
new_weight_access_required_candidates[]
```

B010 owns those decisions after B006 rights/provenance and B007/B008 evidence are reconciled. Compatibility cannot override rights, provenance, exact-revision identity, tokenizer economics, or resource hard gates.

## Validation / authority state

Current decision artifact blob after provenance/runtime-claim hardening:

```text
B009_DECISION_BLOB = dbbac577e93141f20f2276c5b83ffbffe467548e
```

No repository quality gate or candidate execution is claimed:

```text
pytest -q = NOT_RUN
ruff check src tests = NOT_RUN
mypy = NOT_RUN
python -m mstr_qualify validate = NOT_RUN

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

B009 remains unchecked / `NOT_COMPLETE_CANONICAL` pending exact-head review and repository quality-gate closeout.
