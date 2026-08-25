# T012 — Static Qualification: Qwen/Qwen3.5-2B-Base

**Task:** MSTR-000 / T012
**Branch:** task/000-t012-t020-static-candidates
**Scope:** static candidate qualification from live public upstream metadata only. **No model weights were downloaded or executed; no gated terms accepted; no paid APIs; no rented compute; no training.**

## Exact upstream identities (live-fetched)

```text
UPSTREAM_ID = Qwen/Qwen3.5-2B-Base
UPSTREAM_REVISION = b1485b2fa6dfa1287294f269f5fb618e03d52d7c   # HF repo sha at collection time (2026-08-25)
GATED = false / PUBLIC = true
```

## Architecture facts (config.json + safetensors index at pinned revision)

```text
family = qwen3_5 (multimodal ForConditionalGeneration)
parameters = 2,274,069,824 total (BF16 2,274,067,232 + F32 2,592)
tokenizer = Qwen2Tokenizer BPE; tokenizer_revision pinned to repo sha
vision_components = Integrated qwen3_5 vision encoder inside same repository/LICENSE (Apache-2.0); text-only serving path must be validated later.
FIM capability = YES — <|fim_prefix|>, <|fim_suffix|>, <|fim_middle|>, <|fim_pad|> present in tokenizer.json added_tokens.
```

## Rights evidence

Verbatim Apache-2.0 LICENSE file present at pinned revision; HF tags license:apache-2.0; ungated=false-gated public repo.

## Record

`artifacts/candidates/qwen3.5-2b.json` validates against `schemas/candidate-record.schema.json` (verified via `python -m mstr_qualify validate`, exit 0) and passes the T006 recomputed rights gate (`python -m mstr_qualify rights`, computed_decision=pass_permissive, eligible_for_primary=true).

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
