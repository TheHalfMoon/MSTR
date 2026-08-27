# B009 — Candidate Trainability / Conversion / Runtime Compatibility

**Workstream:** MSTR-000B  
**Task:** B009  
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL  
**Canonical main at execution:** `ead69ae26265b133c782ae8fd2795c126253a3b6`  
**Decision artifact:** `artifacts/decisions/B009-training-runtime-compatibility.json`

B009 is a metadata/code/docs compatibility freeze only. It does not access model weights, download tokenizer artifacts, execute models, run conversion or quantization, perform training, accept gated terms, use paid compute, or ingest a large dataset.

## Inputs and exact upstream pins

Canonical candidate input:

```text
artifacts/manifests/B005-code-backbone-discovery.json
CANDIDATES = 15
```

Pinned upstream source heads observed for this decision:

```text
TRANSFORMERS = huggingface/transformers@01846b52e4b9333577af7e4e19c6d3c0f815ff72
UNSLOTH      = unslothai/unsloth@e42405615e26f626232084b973976f61036e8b2e
PEFT         = huggingface/peft@5779b17b9a67d9b07b5be75053cb1932b939fd9f
TRL          = huggingface/trl@67dfbe211a07a8dd6ebc1a5af5b75152e10add8e
LLAMA_CPP    = ggml-org/llama.cpp@d7a2074112d27649303fa107eb8c94db1ee435f3
```

`SOURCE_REGISTERED` means only that the pinned source contains an implementation/converter/family path. It is **not** a runtime PASS. `GENERIC_PATH` means a framework may operate through a broad HF/CausalLM interface but the exact candidate was not executed. `UNVERIFIED` is intentionally fail-closed.

## Main findings

### 1. llama.cpp conversion/runtime coverage is broader than old assumptions

The pinned llama.cpp source contains explicit or family conversion/runtime paths for:

- Mellum;
- StarCoder2;
- StableLM / Stable Code;
- Falcon-H1;
- LFM2;
- BitNet;
- Granite;
- Mistral3 / Ministral-family conversion;
- Qwen-family models;
- Gemma-family models;
- SmolLM3 runtime support with a Llama-family conversion path.

This reduces the risk that these families are structurally impossible to export to GGUF. It does **not** prove exact-revision conversion, quantization quality, tokenizer preservation, or runtime fidelity.

### 2. Unsloth support must be candidate-specific, not inferred from marketing

The pinned Unsloth source has direct family evidence for Falcon-H1, Granite, LFM2, and Qwen3.5-era paths. Direct source evidence was not established in this review for Mellum, StarCoder2, or Stable Code.

Therefore:

```text
UNSLOTH_SOURCE_PRESENT != EXACT_MODEL_TRAINING_PASS
NO_DIRECT_SOURCE_HIT != PROVEN_INCOMPATIBLE
```

Every serious candidate still needs exact-revision training/export qualification before B013 admission.

### 3. Hybrid architectures require adapter-target coverage checks

The pinned PEFT main explicitly documents a hybrid-architecture hazard: when some configured `target_modules` match and others do not, unmatched modules may be silently skipped rather than causing a total failure.

This is material for hybrid or mixed architectures, especially:

- `tiiuae/Falcon-H1-3B-Base`;
- Granite hybrid-family candidates;
- `LiquidAI/LFM2.5-2.6B-Base`;
- any multimodal/mixed-component Ministral training scope.

Before adapter training, qualification must enumerate exact module names and prove intended adapter coverage. A training run that merely starts is insufficient evidence.

### 4. Candidate-specific restrictions

**Ministral-3-3B-Base-2512**
- Multimodal/mixed-component scope must be explicit.
- Text-only versus full-checkpoint training/export cannot be conflated.
- Parameter-accounting and component-cost issues from B005 remain unresolved.

**Granite 4.1 3B Base**
- Family support exists in both Unsloth and llama.cpp source.
- Exact 4.1-3B path remains unexecuted.
- Hybrid target-module coverage must be audited.

**Qwen2.5-Coder-1.5B / Mellum / StarCoder2 / Stable Code / CodeGemma**
- FIM and code-special-token preservation is qualification-critical.
- GGUF conversion source presence does not prove FIM-token/export equivalence.

**CodeGemma 2B**
- Exact full revision remains unresolved in B005 because public access requires login/clickthrough.
- B009 performs no terms acceptance and creates no access authority.

**Falcon-H1 3B Base**
- Hybrid Transformer/SSM architecture.
- Unsloth and llama.cpp have architecture-specific source paths.
- PEFT target-module coverage and SSM runtime/export behavior require exact qualification.

**BitNet b1.58 2B4T BF16**
- Native context reported in B005 is 4096, below MSTR's 8192 reference.
- Public model usage has reported specialized/remote-code handling.
- Generic 4-bit/QLoRA assumptions must not be applied to native 1.58-bit semantics without proof.
- llama.cpp has BitNet converter source, but B009 did not execute it.

**LFM2.5 2.6B Base**
- B005 has only a short revision; full immutable SHA remains required.
- Unsloth and llama.cpp have LFM2-family source evidence.
- Exact LFM2.5 training/export remains unqualified.

## Framework interpretation policy

For this task:

```text
TRANSFORMERS_NATIVE_SOURCE
    != exact candidate load PASS

UNSLOTH_SOURCE
    != exact train/save/export PASS

PEFT_GENERIC_PATH
    != correct adapter coverage

TRL_GENERIC_TRAINER
    != exact candidate trainability PASS

LLAMA_CPP_CONVERTER_SOURCE
    != conversion PASS
    != quantization PASS
    != runtime-regression PASS
```

B012-equivalent artifact-backed execution is the correct place to turn these source-level findings into hard deployment evidence.

## B010 handoff

B009 does not create either of these lists:

```text
qualification_candidates[]
new_weight_access_required_candidates[]
```

B010 owns those decisions after B006 rights/provenance and B007/B008 evidence are reconciled. Compatibility cannot override rights, provenance, exact-revision identity, tokenizer economics, or resource hard gates.

## Validation / authority state

Current decision artifact blob after source-evidence binding:

```text
B009_DECISION_BLOB = 82a537706b22f2daaa636da839e4fb0043735f80
```

No repository quality gate or candidate execution is claimed by this evidence:

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

B009 remains unchecked / `NOT_COMPLETE_CANONICAL` pending governed review and repository quality-gate closeout.
