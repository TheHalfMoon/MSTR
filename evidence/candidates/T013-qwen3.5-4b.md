# T013 — Static Qualification: Qwen/Qwen3.5-4B-Base

**Task:** MSTR-000 / T013
**Branch:** task/000-t012-t020-static-candidates
**Scope:** static candidate qualification from live public upstream metadata only. **No model weights were downloaded or executed; no gated terms accepted; no paid APIs; no rented compute; no training.**

## Exact upstream identities (live-fetched)

```text
UPSTREAM_ID = Qwen/Qwen3.5-4B-Base
UPSTREAM_REVISION = 1001bb4d826a52d1f399e183466143f4da7b741b   # HF repo sha at collection time (2026-08-25)
GATED = false / PUBLIC = true
```

## Architecture facts (config.json + safetensors index at pinned revision)

```text
family = qwen3_5 (multimodal ForConditionalGeneration)
parameters = 4,659,865,088 total (BF16)
tokenizer = Qwen2Tokenizer BPE; pinned to repo sha
vision_components = Integrated qwen3_5 vision encoder, same Apache-2.0 LICENSE file.
FIM capability = YES — FIM control tokens confirmed in tokenizer.json.
```

## Rights evidence

Apache-2.0 LICENSE file present at pinned revision; public, ungated.

## Record

`artifacts/candidates/qwen3.5-4b.json` validates against `schemas/candidate-record.schema.json` (verified via `python -m mstr_qualify validate`, exit 0) and passes the T006 recomputed rights gate (`python -m mstr_qualify rights`, computed_decision=pass_permissive, eligible_for_primary=true).

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
