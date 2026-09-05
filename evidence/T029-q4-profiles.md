# T029 Q4 Profile Qualification Evidence

**Task:** `T029`
**State:** `Q4_PROFILE_SET_READY / QUALIFICATION_PENDING / NOT_COMPLETE_CANONICAL`
**Current reconciliation base:** `5cadbd754686ebff6f5327e9746f0b074b35e318`
**Historical recovery PR:** `#95` / current historical head `deac1ffd5a9ef4107ad3ad28e472d7d17c47033f`

## Contract

T029 requires quality-oriented and compatibility-oriented Q4 profiles where practical, with exact source identity, quantizer/tool identity, recipe, output SHA-256, and output byte size. Durable model binaries are not committed; reproducible manifests and evidence are retained for later portable-runtime qualification.

The reconciled manifest is:

```text
artifacts/manifests/quantization/T029-q4-profiles.json
```

It intentionally uses `format_version`, not `schema_version`: no canonical quantization-manifest schema is registered in `mstr-qualify`, so this evidence does not manufacture a schema contract.

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

The historical Ministral run `32959718688` reached the quantizer but the Python wrapper failed while decoding non-UTF-8 diagnostic bytes. That failure did not prove Q4 incompatibility.

Historical PR #95 repaired subprocess capture with deterministic UTF-8 replacement decoding. Actions run `33263175072` subsequently executed the pending Ministral cell. The run-level conclusion remained `failure` because the separate quality job stopped at Ruff formatting findings, but the material `ministral_retry` job itself completed successfully:

```text
RECOVERY_EXECUTION_HEAD = f0f0210a43fb0c70839259d29f9b8a24d7ca3f55
RUN = 33263175072
MINISTRAL_JOB = 99232907513 / SUCCESS
ACTIONS_ARTIFACT_ID = 9729481097
CANDIDATE = ministral-3-3b
MODEL = mistralai/Ministral-3-3B-Base-2512
MODEL_REVISION = 6f9c4b12a95b139af68670a6713616b757923735
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
RESULT = Q4_PROFILE_READY
RESOURCE_COST = USD 0.00
```

The durable report records:

```text
F16_SHA256 = 30b2f0f8cf5a0b0c5ac3599d3b3de777df74714d49375e43359bb4c1fddbc1de
F16_SIZE_BYTES = 6866212448

Q4_K_M_SHA256 = 31a399bb99a851698948b0d0db5178ac64d20c55048b71a87d3fc25d0b9f0291
Q4_K_M_SIZE_BYTES = 2146489952

Q4_K_S_SHA256 = 81575340aac45340dc947bcab07c1d25b5f02c10ad5fa32c69e45a48803ce4aa
Q4_K_S_SIZE_BYTES = 2053248608
```

Canonical scientific interpretation of the recovered execution evidence is therefore:

```text
T029_Q4_PROFILE_CELLS_READY = 8 / 8
MINISTRAL_Q4_STATUS = Q4_PROFILE_READY
MINISTRAL_Q4_UNSUPPORTED = NO
MINISTRAL_Q4_INTEGRITY_FAILURE = NO
```

This is execution evidence, not by itself task closeout.

## Historical Qualification Boundary

Run `33263175072` also established the following on the older recovery head:

```text
identity_scope = SUCCESS
focused recovery tests = PASS
mstr-qualify validate = PASS
full pytest = PASS
ruff = FAIL / formatting-only import-order findings
mypy = NOT_EXECUTED_AFTER_RUFF_FAILURE
```

Those partial quality results are historical evidence only and do not transfer to this current-main reconciliation candidate. Fresh exact-head qualification, independent substantive review, mandatory premerge verification, guarded merge, postmerge verification, and separate task closeout remain required.

## Authority Boundary

The recovered T029 result concerns only the pre-existing T027/T028 eight-candidate envelope. This reconciliation performs no model access or model execution. It does not authorize or consume the MSTR-000B B010/B011/B012 candidates.

```text
NEW_MODEL_WEIGHT_ACCESS = NONE
B012_AUTHORITY = NONE
K2_AUTHORITY = NONE
MODEL_EXECUTION_BY_THIS_RECONCILIATION = NONE
QUANTIZATION_EXECUTION_BY_THIS_RECONCILIATION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_COMPUTE = NONE
PAID_MODEL_API = NONE
GATED_TERMS_ACCEPTANCE = NONE
PRODUCTION_RELEASE = NONE
```

## Completion Boundary

```text
T029_EXECUTION_PROFILE_SET = READY_8_OF_8
T029_CURRENT_RECONCILIATION_QUALIFICATION = PENDING
T029_COMPLETE_CANONICAL = NO
```

T029 may become canonical only after this current-main reconciliation passes the complete governed lifecycle and a separate closeout proves the task/evidence state on exact canonical `main`.