# T029 Runner Recovery Evidence

**Task:** `T029`
**Scope:** subprocess-decoding repair and historical result reconciliation
**Current reconciliation base:** `5cadbd754686ebff6f5327e9746f0b074b35e318`
**State:** `RUNNER_RECOVERY_PROVEN / T029_GOVERNANCE_PENDING`

## Historical Defect

The historical T029 batch used:

```text
HEAD = 406de41d132fa6d24d55814f3f6dd4fced5f12bd
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
```

Seven candidates produced durable `Q4_PROFILE_READY` reports. Ministral run `32959718688` reached `llama-quantize`, but the Python wrapper failed while decoding captured diagnostic bytes with strict UTF-8. That wrapper failure was not evidence of model conversion or Q4 incompatibility.

## Repair

`colab/mstr_t029_quantize.py` now requests deterministic UTF-8 replacement decoding:

```python
subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    ...,
)
```

Regression tests require invalid subprocess bytes to remain bounded diagnostic text using replacement characters and require ordinary UTF-8 output to remain unchanged.

## Recovery Execution

Actions run `33263175072` later executed the exact pending Ministral T029 cell under the pre-existing T027/T028/T029 candidate envelope. The run-level conclusion was `failure` because a separate quality job stopped at Ruff formatting findings. The execution job itself is independently observable and completed successfully:

```text
TARGET_CODE_HEAD = f0f0210a43fb0c70839259d29f9b8a24d7ca3f55
RUN = 33263175072
JOB = 99232907513
JOB_CONCLUSION = SUCCESS
ACTIONS_ARTIFACT_ID = 9729481097
ARTIFACT_NAME = t029-recovery-ministral-3-3b
MODEL_REVISION = 6f9c4b12a95b139af68670a6713616b757923735
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
RESOURCE_COST = USD 0.00
RESULT_CLASSIFICATION = Q4_PROFILE_READY
```

The durable recovered identity records both quantization arms as successful:

```text
Q4_K_M = 2146489952 bytes / SHA-256 31a399bb99a851698948b0d0db5178ac64d20c55048b71a87d3fc25d0b9f0291
Q4_K_S = 2053248608 bytes / SHA-256 81575340aac45340dc947bcab07c1d25b5f02c10ad5fa32c69e45a48803ce4aa
```

The prior `UnicodeDecodeError` is therefore proven to have been a runner-output decoding defect, not a scientific Q4 rejection.

## Reconciliation Choice

Historical PR #95 also carried a Colab fallback notebook created while hosted runner jobs were unavailable. That fallback became unnecessary after the successful hosted `ministral_retry` job. This current-main successor intentionally does not carry that stale fallback surface or its obsolete `NOT_EXECUTED` evidence. It preserves the proven runner repair and durable eight-profile result only.

## Authority Boundary

The historical recovery remained inside the existing T027/T028/T029 eight-candidate envelope. This reconciliation itself performs no acquisition, conversion, quantization, runtime execution, or model inference.

```text
B012_MODEL_WEIGHT_ACCESS = NONE
B012_AUTHORITY = NONE
K2_AUTHORITY = NONE
MODEL_INFERENCE_BY_THIS_RECONCILIATION = NONE
QUANTIZATION_EXECUTION_BY_THIS_RECONCILIATION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```

## Current Boundary

All eight T029 candidates retain byte-verified historical Q4 profile evidence. Fresh exact-head qualification re-downloaded the primary `qwen3.5-2b` artifact and proved that its Q4_K_S SHA-256 is the valid 64-hex value recorded in the corrected manifest; the earlier 65-hex value was a reconciliation transcription error caught before merge, not a historical execution defect. The Ministral runner-decoding recovery remains scientifically resolved. T029 remains open until the current-main reconciliation passes fresh qualification, independent review, mandatory premerge, guarded merge, postmerge proof, and separate canonical task closeout.

```text
RUNNER_RECOVERY = PASS
T029_Q4_PROFILE_SET = 8_FULLY_VERIFIED
T029_COMPLETE_CANONICAL = NO
```
