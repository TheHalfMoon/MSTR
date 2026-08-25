# T017 — Static Qualification: HuggingFaceTB/SmolLM3-3B-Base

**Task:** MSTR-000 / T017
**Branch:** task/000-t012-t020-static-candidates
**Scope:** static candidate qualification from live public upstream metadata only. **No model weights were downloaded or executed; no gated terms accepted; no paid APIs; no rented compute; no training.**

## Exact upstream identities (live-fetched)

```text
UPSTREAM_ID = HuggingFaceTB/SmolLM3-3B-Base
UPSTREAM_REVISION = d78a42f79198603e614095753484a04c10c2b940   # HF repo sha at collection time (2026-08-25)
GATED = false / PUBLIC = true
```

## Architecture facts (config.json + safetensors index at pinned revision)

```text
family = smollm3 (SmolLM3ForCausalLM, text-only)
parameters = 3,075,098,624 total (BF16)
tokenizer = PreTrainedTokenizerFast; vocab_size 128,256; max_position_embeddings 65,536
vision_components = None (text-only).
FIM capability = NO FIM control tokens found in tokenizer.json added_tokens.
```

## Rights evidence

No standalone LICENSE file in tree; Apache-2.0 declared via README front matter + HF license tags; same caveat policy as T014/T016.

## Record

`artifacts/candidates/smollm3-3b.json` validates against `schemas/candidate-record.schema.json` (verified via `python -m mstr_qualify validate`, exit 0) and passes the T006 recomputed rights gate (`python -m mstr_qualify rights`, computed_decision=pass_permissive, eligible_for_primary=true).

Status recorded: `static_qualified`. This is NOT backbone selection and NOT weight eligibility admission (that decision belongs to T22).

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = metadata-only HTTPS GETs to huggingface.co API/raw endpoints at exact pinned revisions
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```
