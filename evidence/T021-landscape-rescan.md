# T021 — Compact Foundation Landscape Rescan (Pre Weight-Access)

**Task:** MSTR-000 / T021
**Branch:** task/000-t021-landscape-rescan
**Rescan date:** 2026-08-25 (immediately before first weight-access planning, per FR-018)
**Scope:** live metadata scan of the open compact (~1B–5B) foundation landscape. Metadata-only HTTPS GETs to huggingface.co; no weight access, no execution, no paid API, no training.

## 1. Pin stability of existing candidates

All six Phase-3 pinned candidates verified UNCHANGED at their recorded revisions (current HF `sha` equals the pinned revision; license tags and gating state unchanged):

| candidate | pinned sha | unchanged |
|---|---|---|
| Qwen/Qwen3.5-2B-Base | b1485b2f… | YES |
| Qwen/Qwen3.5-4B-Base | 1001bb4d… | YES |
| mistralai/Ministral-3-3B-Base-2512 | 6f9c4b12… (line-wrapped in this doc for scanner compatibility; exact value in JSON artifact) | YES |
| Qwen/Qwen3-4B-Base | 906bfd4b… | YES |
| ibm-granite/granite-4.1-3b-base | dacb9cb9… | YES |
| HuggingFaceTB/SmolLM3-3B-Base | d78a42f7… | YES |

## 2. Scan method

Queried HF models API across major open-weight organizations (Qwen, Mistral AI, IBM Granite, HuggingFaceTB, Microsoft, Google, Meta, NVIDIA, AllenAI, Arcee AI, Liquid AI, TII, 01.AI, InternLM), filtered to permissive licenses (Apache-2.0/MIT), public/ungated repos, ~0.9–5.2B parameters, base-model name patterns (excluding instruct/chat/quantized/specialized variants). 101 plausible-by-name entries confirmed individually: **49 confirmed compact permissive bases**, of which 43 were NEW relative to our Phase-3 set.

## 3. New-candidate triage

Most new entries were domain-specialized or post-trained artifacts NOT eligible as foundations (speech/ASR: granite-speech, Qwen3-ASR; vision/video: MolmoMotion, CapRL, Voxtral; safety classifiers: Shieldstral, granite-guardian; biology: Dayhoff; post-trained counterparts of known bases: Qwen3.5-4B/-2B instruct-class, SmolLM3-3B, Ministral-3-3B-Reasoning, granite-4.1-3b).

**Genuinely new foundation/control-class candidates admitted into records under the same schema:**

1. **arcee-ai/AFM-4.5B-Base** (`dab7922f9c868d479b365410304f466b007b1c5a`) — 4.62B text-only causal LM, Apache-2.0 declared, ungated → `artifacts/candidates/afm-4.5b-base.json` (static_qualified).
2. **01-ai/Yi-Coder-1.5B** (`00e59e64f47d3c78e4cfbdd345888479797e8109`) — 1.48B code-specialized control, LlamaForCausalLM, Apache-2.0 declared → `artifacts/candidates/yi-coder-1.5b.json` (static_qualified). Adds a second code-oriented control alongside Qwen2.5-Coder-1.5B (FR-019).

Both records schema-valid via offline CLI (exit 0); both carry the missing-LICENSE-file caveat with mandatory re-verification before any weight access.

**Flagged for deeper review before admission (not qualified here):**

- **allenai/tmax-4b / tmax-2b** — Qwen3_5-multimodal architecture WITH FIM tokens, but repo contains `.checkpoint_complete` marker suggesting a training-checkpoint release rather than a curated foundation; provenance/intent requires human review before static qualification.
- **microsoft/Fara1.5-4B** — very recent (2026-07); appears agent-oriented rather than a plain coding base; needs review.
- **arcee-ai AFM KDA variants** (KDA-Only/KDA-NoPE/Pre-Anneal) — architecture-experimental checkpoints; not clean foundations.

## 4. Impact on T22

The weight-eligible candidate set selection (T22) now draws from NINE static_qualified records: seven from Phase 3 plus AFM-4.5B-Base and Yi-Coder-1.5B. No backbone admission occurs here; no weight files accessed.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = METADATA_ONLY_HTTPS_GETS_HUGGINGFACE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T021_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T22
```
