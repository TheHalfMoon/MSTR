# T016 — Static Qualification: ibm-granite/granite-4.1-3b-base

**Task:** MSTR-000 / T016
**Branch:** task/000-t012-t020-static-candidates
**Scope:** static candidate qualification from live public upstream metadata only. **No model weights were downloaded or executed; no gated terms accepted; no paid APIs; no rented compute; no training.**

## Exact upstream identities (live-fetched)

```text
UPSTREAM_ID = ibm-granite/granite-4.1-3b-base
UPSTREAM_REVISION = dacb9cb9157bec98e99b09f285c92a4d58405c96   # HF repo sha at collection time (2026-08-25)
GATED = false / PUBLIC = true
```

## Architecture facts (config.json + safetensors index at pinned revision)

```text
family = granite (GraniteForCausalLM, text-only)
parameters = 3,402,836,480 total (BF16)
tokenizer = GPT2Tokenizer/BPE; vocab_size 100,352; max_position_embeddings 131,072; includes model.sig provenance signature
vision_components = None (text-only).
FIM capability = YES — <|fim_prefix|>, <|fim_suffix|>, <|fim_middle|>, <|fim_pad|> confirmed in tokenizer.json.
```

## Rights evidence

No standalone LICENSE file in tree; Apache-2.0 declared via README front matter + HF license tags. Pass recorded on structured declaration with mandatory re-verification caveat at weight access (same policy as Ministral). Component rights: tokenizer files ship in-repo under same declared license.

## Record

`artifacts/candidates/granite-4.1-3b.json` validates against `schemas/candidate-record.schema.json` (verified via `python -m mstr_qualify validate`, exit 0) and passes the T006 recomputed rights gate (`python -m mstr_qualify rights`, computed_decision=pass_permissive, eligible_for_primary=true).

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
