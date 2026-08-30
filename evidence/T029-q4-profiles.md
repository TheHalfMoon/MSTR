# T029 Q4 Profile Qualification Evidence

**Task:** `T029`  
**State:** `Q4_PROFILE_SET_READY / QUALIFICATION_PENDING / NOT_COMPLETE_CANONICAL`  
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`  
**Recovery PR:** `#95`

## Contract

T029 requires quality-oriented and compatibility-oriented Q4 profiles where practical, with exact source identity, quantizer/tool identity, recipe, output SHA-256, and output byte size. Durable binaries are not committed; profiles are reproducible evidence for later portable-runtime qualification.

The durable reconciled manifest is:

```text
artifacts/manifests/quantization/T029-q4-profiles.json
```

It intentionally uses `format_version`, not `schema_version`: no canonical quantization-manifest schema has been registered in `mstr-qualify`, so this evidence does not manufacture a schema contract.

## Historical Seven-Profile Batch

```text
SOURCE_EXECUTION_HEAD = 406de41d132fa6d24d55814f3f6dd4fced5f12bd
LLAMA_CPP_COMMIT = fc35562ba46fbbf8e30cac85edbb39642c37d248
CONVERSION_RECIPE = convert_hf_to_gguf.py --outtype f16
RESOURCE_COST_PER_RECORDED_PROFILE = USD 0.00
```

Seven candidates produced durable `Q4_PROFILE_READY` reports with both `Q4_K_M` and `Q4_K_S` arms:

| Candidate | Actions run | Artifact | Result |
| --- | ---: | ---: | --- |
| `qwen3.5-2b` | `32959707029` | `9603552151` | `Q4_PROFILE_READY` |
| `qwen3.5-4b` | `32959712851` | `9603766969` | `Q4_PROFILE_READY` |
| `qwen3-4b` | `32959723760` | `9603722432` | `Q4_PROFILE_READY` |
| `granite-4.1-3b` | `32959729068` | `9603875247` | `Q4_PROFILE_READY` |
| `smollm3-3b` | `32959733977` | `9603684909` | `Q4_PROFILE_READY` |
| `qwen2.5-coder-1.5b` | `32959739245` | `9603602508` | `Q4_PROFILE_READY` |
| `yi-coder-1.5b` | `32959744422` | `9603583604` | `Q4_PROFILE_READY` |

## Ministral Recovery Result

The historical Ministral run `32959718688` failed in the Python wrapper while decoding non-UTF-8 quantizer stderr. It did not prove Q4 incompatibility. PR #95 repaired subprocess capture with deterministic UTF-8 replacement decoding.

After hosted runners recovered, exact T029 recovery workflow run `33263175072` executed the already-authorized Ministral cell using target code head:

```text
RECOVERY_EXECUTION_HEAD = f0f0210a43fb0c70839259d29f9b8a24d7ca3f55
JOB = 99232907513 / SUCCESS
ARTIFACT = 9729481097 / t029-recovery-ministral-3-3b
CANDIDATE = ministral-3-3b
MODEL = mistralai/Ministral-3-3B-Base-2512
MODEL_REVISION = 6f9c4b12a95b139af68670a6713616b757923735
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
RESULT = Q4_PROFILE_READY
RESOURCE_COST = USD 0.00
```

The durable report binds all source files as `ACQUIRED_VERIFIED` and records:

```text
F16_SHA256 = 30b2f0f8cf5a0b0c5ac3599d3b3de777df74714d49375e43359bb4c1fddbc1de
F16_SIZE_BYTES = 6866212448

Q4_K_M_STATUS = OK
Q4_K_M_SHA256 = 31a399bb99a851698948b0d0db5178ac64d20c55048b71a87d3fc25d0b9f0291
Q4_K_M_SIZE_BYTES = 2146489952

Q4_K_S_STATUS = OK
Q4_K_S_SHA256 = 81575340aac45340dc947bcab07c1d25b5f02c10ad5fa32c69e45a48803ce4aa
Q4_K_S_SIZE_BYTES = 2053248608
```

Canonical scientific interpretation is therefore:

```text
T029_Q4_PROFILE_CELLS_READY = 8 / 8
MINISTRAL_Q4_STATUS = Q4_PROFILE_READY
MINISTRAL_Q4_UNSUPPORTED = NO
MINISTRAL_Q4_INTEGRITY_FAILURE = NO
```

This is execution evidence, not by itself task closeout.

## Qualification History

On exact candidate `f0f0210a43fb0c70839259d29f9b8a24d7ca3f55`, workflow run `33263175072` also proved:

```text
identity_scope = SUCCESS
focused T029 recovery tests = 6 passed
mstr-qualify validate = PASS
full pytest = 876 passed
ruff = FAIL / 3 import-order I001 findings
mypy = NOT_EXECUTED_AFTER_RUFF_FAILURE
```

Those Ruff findings were formatting-only in three T029 test files and have since been repaired. The manifest and tests were also reconciled to the successful eighth profile, so the historical PASS portions do not transfer to the current head. Fresh exact-head qualification is required.

## Completion Boundary

T029 remains non-canonical until all of the following are true:

1. PR #95 final exact head passes the repository-required material-change gates;
2. review and mandatory premerge governance succeed on that exact head;
3. the implementation/evidence is guarded-merged;
4. post-merge evidence succeeds;
5. the T029 task/evidence closeout is canonical on `main`.

```text
T029_EXECUTION_PROFILE_SET = READY_8_OF_8
T029_CURRENT_HEAD_QUALIFICATION = PENDING
T029_COMPLETE_CANONICAL = NO
```
