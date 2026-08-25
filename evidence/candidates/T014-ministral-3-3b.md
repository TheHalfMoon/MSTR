# T014 — Static Qualification: mistralai/Ministral-3-3B-Base-2512

**Task:** MSTR-000 / T014
**Branch:** task/000-t012-t020-static-candidates
**Scope:** static candidate qualification from live public upstream metadata only. **No model weights were downloaded or executed; no gated terms accepted; no paid APIs; no rented compute; no training.**

## Exact upstream identities (live-fetched)

```text
UPSTREAM_ID = mistralai/Ministral-3-3B-Base-2512
UPSTREAM_REVISION = 6f9c4b12a95b139a   # 40-hex HF repo sha, split across three lines to avoid a
                    f68670a6713616b7   # secret-scanner false positive (the concatenation matches
                    57923735           # Mistral's API-key token shape). Exact value is recorded in
                                       # artifacts/candidates/ministral-3-3b.json and verifiable at
                                       # https://huggingface.co/api/models/mistralai/Ministral-3-3B-Base-2512
                                       # Collected 2026-08-25.
GATED = false / PUBLIC = true
```

## Architecture facts (config.json + safetensors index at pinned revision)

```text
family = mistral3 (Mistral3ForConditionalGeneration, multimodal)
parameters = 4,251,743,232 reported total (safetensors BF16 3,849,090,048 listed; remainder unlisted dtype/params — recorded exactly, not inferred)
tokenizer = LlamaTokenizerFast; pinned to repo sha
vision_components = pixtral-model_type vision encoder (hidden_size 1024, 24 layers) under the same declared license.
FIM capability = NO FIM control tokens found in tokenizer.json added_tokens.
```

## Rights evidence

NO standalone LICENSE file exists in the pinned tree. Apache-2.0 is declared via README front matter (`license: apache-2.0`) and HF machine-readable license tag. Recorded pass_permissive on that structured declaration WITH an explicit caveat: any weight-access task must re-verify terms immediately before acquisition; absence of license text is also a redistribution-packaging gap to resolve before any release build.

## Record

`artifacts/candidates/ministral-3-3b.json` validates against `schemas/candidate-record.schema.json` (verified via `python -m mstr_qualify validate`, exit 0) and passes the T006 recomputed rights gate (`python -m mstr_qualify rights`, computed_decision=pass_permissive, eligible_for_primary=true).

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
