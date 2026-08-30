# T029 Runner Recovery Evidence

**Task:** `T029`  
**Scope:** runner hardening and historical result reconciliation  
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`  
**State:** `RUNNER_RECOVERY_PROVEN / T029_GOVERNANCE_PENDING`

## Historical Failure

The final historical T029 batch used:

```text
HEAD = 406de41d132fa6d24d55814f3f6dd4fced5f12bd
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
```

Seven candidates produced durable `Q4_PROFILE_READY` reports. Ministral run `32959718688` entered `llama-quantize` but the Python wrapper failed while decoding captured stderr:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4 ...
```

That failure was in `subprocess.run(..., text=True)` output decoding. It did not prove model conversion or Q4 incompatibility.

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

Regression tests require invalid subprocess bytes to be preserved as diagnostic text with replacement characters and require ordinary UTF-8 output to remain unchanged.

## Recovery Execution

Hosted runners recovered on 2026-08-30. Workflow run `33263175072` executed the exact pending Ministral T029 cell under the existing T027/T028/T029 authority envelope:

```text
TARGET_CODE_HEAD = f0f0210a43fb0c70839259d29f9b8a24d7ca3f55
JOB = 99232907513
JOB_CONCLUSION = SUCCESS
ACTIONS_ARTIFACT_ID = 9729481097
ARTIFACT_NAME = t029-recovery-ministral-3-3b
MODEL_REVISION = 6f9c4b12a95b139af68670a6713616b757923735
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
RESOURCE_COST = USD 0.00
RESULT_CLASSIFICATION = Q4_PROFILE_READY
```

The report records both quantization arms as successful:

```text
Q4_K_M = OK / 2146489952 bytes
Q4_K_S = OK / 2053248608 bytes
```

The prior `UnicodeDecodeError` is therefore proven to have been a runner output-decoding defect, not a scientific Q4 rejection.

## Authority Boundary

The recovery stayed inside the existing T029 candidate envelope. It did not access or authorize B011 candidates and did not perform inference or training.

```text
B011_MODEL_WEIGHT_ACCESS = NONE
MODEL_INFERENCE = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```

## Current Boundary

All eight T029 Q4 profile cells now have durable `Q4_PROFILE_READY` evidence. The runner recovery loop is proven, but T029 itself remains open until the current reconciliation head passes fresh qualification, exact-head review, mandatory premerge, guarded merge, post-merge proof, and canonical task closeout.

```text
RUNNER_RECOVERY = PASS
T029_Q4_PROFILE_SET = READY_8_OF_8
T029_COMPLETE_CANONICAL = NO
```
