# T029 Q4 Profile Qualification Evidence

**Task:** `T029`
**State:** `PARTIAL_RECOVERY / NOT_COMPLETE_CANONICAL`
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`
**Recovery PR:** `#95`

## Contract

T029 requires quality-oriented and compatibility-oriented Q4 profiles where practical, with exact source identity, quantizer/tool identity, recipe, output SHA-256, and output byte size. Durable binaries are not committed; profiles are reproducible evidence for later portable-runtime qualification.

The recovered durable manifest is:

```text
artifacts/manifests/quantization/T029-q4-profiles.json
```

It intentionally uses `format_version`, not `schema_version`: no canonical quantization-manifest schema has been registered in `mstr-qualify`, so this evidence file does not manufacture a schema contract.

## Final Historical Execution Batch

```text
SOURCE_EXECUTION_HEAD = 406de41d132fa6d24d55814f3f6dd4fced5f12bd
LLAMA_CPP_COMMIT = fc35562ba46fbbf8e30cac85edbb39642c37d248
CONVERSION_RECIPE = convert_hf_to_gguf.py --outtype f16
RESOURCE_COST_PER_RECORDED_PROFILE = USD 0.00
```

Seven candidates have durable `Q4_PROFILE_READY` evidence. Each has both `Q4_K_M` and `Q4_K_S` arms with exact SHA-256 and byte size recorded in the manifest.

| Candidate | Actions run | Artifact | Result |
| --- | ---: | ---: | --- |
| `qwen3.5-2b` | `32959707029` | `9603552151` | `Q4_PROFILE_READY` |
| `qwen3.5-4b` | `32959712851` | `9603766969` | `Q4_PROFILE_READY` |
| `qwen3-4b` | `32959723760` | `9603722432` | `Q4_PROFILE_READY` |
| `granite-4.1-3b` | `32959729068` | `9603875247` | `Q4_PROFILE_READY` |
| `smollm3-3b` | `32959733977` | `9603684909` | `Q4_PROFILE_READY` |
| `qwen2.5-coder-1.5b` | `32959739245` | `9603602508` | `Q4_PROFILE_READY` |
| `yi-coder-1.5b` | `32959744422` | `9603583604` | `Q4_PROFILE_READY` |

These reports bind the exact model revisions, F16 conversion SHA-256/size, Q4 arm SHA-256/size, and llama.cpp commit. The original Actions artifacts remain the source evidence for the recovered numeric/hash values.

## Ministral Pending Cell

Historical final-batch run `32959718688` for `ministral-3-3b` reached `llama-quantize` but the Python wrapper raised a `UnicodeDecodeError` while decoding non-UTF-8 quantizer stderr before writing a durable report. That event does **not** prove conversion or Q4 incompatibility.

PR #95 hardens subprocess capture with deterministic UTF-8 replacement decoding and adds a regression that reproduces invalid stderr bytes.

Canonical interpretation remains:

```text
MINISTRAL_Q4_STATUS = PENDING_RETRY_AFTER_RUNNER_FIX
MINISTRAL_Q4_UNSUPPORTED = NOT_PROVEN
MINISTRAL_Q4_INTEGRITY_FAILURE = NOT_PROVEN
```

## Exact-Head Qualification Attempts

PR #95 exact-head recovery candidates have been submitted to repository-authorized evidence workflows. Hosted jobs currently fail before exposing any steps on this private repository.

Latest completed exact-head attempt before this evidence-file commit:

```text
RUN = 33261966713
TARGET_HEAD = 4398d59ce33fadb8547c15e87964ad425cade0ac
identity_scope = FAILURE / steps=null
quality = FAILURE / steps=null
ministral_retry = FAILURE / steps=null
complete = SKIPPED
```

Therefore that run executed no checkout, pytest, schema validation, ruff, mypy, weight acquisition, conversion, or quantization. It is infrastructure evidence only.

A local patch-level reproduction of the non-UTF-8 regression passed `2 passed` after disabling a host-specific Python startup hook unrelated to the repository. This is `LOCAL_PATCH_REGRESSION_PASS`, not CI or full qualification.

## Completion Boundary

T029 MUST remain unchecked and non-canonical until all of the following are true:

1. PR #95 final exact head passes the repository's required material-change gates;
2. `ministral-3-3b` receives a real post-fix durable result or an evidence-backed explicit T029 rejection;
3. the quantization manifest is reconciled to that final result;
4. required review/premerge governance succeeds;
5. the resulting implementation/evidence is guarded-merged and canonical closeout is proven.

No T030/T031/T032/T033/T034 execution is authorized by the existence of seven successful profiles alone.
