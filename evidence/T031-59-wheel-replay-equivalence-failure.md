# T031 59-wheel replay artifact-equivalence failure

Date: 2026-09-07
Task: T031
Candidate: `granite-4.1-3b`

## Exact governed execution

The governed Issue #167 dispatch used the exact authorized command:

```text
T031_RUN granite-4.1-3b
```

GitHub Actions run `34067212730` checked out canonical `main` at `610bf7dacc5ee921d99a4fa2eb9023553021e84c` and executed the canonical 59-wheel historical producer replay bound by `T031_T029_HISTORICAL_59_WHEEL_REPLAY_2026_09_06` under Python `3.11.16`.

The execution failed closed before runtime measurement because regenerated F16 did not reproduce the frozen T029 artifact identity:

```text
EXPECTED_T029_F16_SHA256=b76f61cdf1a11375c734431f661fabe937b7214a54d6defda5f6683bd3473d4d
OBSERVED_REGENERATED_F16_SHA256=b86ef357954d1b1e5b982cc76a830e8305cc86049ca1bc4e9fcc22c7ab91a5d7
RESULT=T031_EXECUTION_FAILED_CLOSED
ERROR_TYPE=ToolchainError
```

Durable workflow evidence:

```text
RUN_ID=34067212730
JOB_ID=101577971224
ARTIFACT_ID=9999577687
ARTIFACT_ZIP_SHA256=328c8441041696d91f0aa7ba55b1899544c579592da112649acc772faa00bfeb
FAILURE_JSON_SHA256=5c22b31305e6aae047671a445bf0c44d0b89df39e6c8226ddb4476b1c78ccfa3
```

The exact durable failure JSON is materialized at `artifacts/results/local/T031/failures/T031-granite-4.1-3b-run-34067212730.json`.

## Stronger reproducibility finding

The observed regenerated F16 hash is exactly the same hash produced by the first governed Granite T031 execution, run `33999224131`:

```text
FIRST_T031_OBSERVED_F16_SHA256=b86ef357954d1b1e5b982cc76a830e8305cc86049ca1bc4e9fcc22c7ab91a5d7
59_WHEEL_REPLAY_OBSERVED_F16_SHA256=b86ef357954d1b1e5b982cc76a830e8305cc86049ca1bc4e9fcc22c7ab91a5d7
FROZEN_T029_F16_SHA256=b76f61cdf1a11375c734431f661fabe937b7214a54d6defda5f6683bd3473d4d
```

Therefore the canonical 59-wheel pre-cutoff reconstruction has now been empirically shown to be insufficient to reproduce the historical T029 Granite F16 identity. The reconstruction remains useful evidence about an installable pre-cutoff dependency set, but it cannot be treated as proof of the historical producer environment or as a successful artifact-equivalence repair.

This result does not identify a single package or system component as the root cause. The original T029 run did not record installed Python package versions. It also ran on a different GitHub-hosted runner image. Further diagnosis must distinguish Python dependency identity, sequential pip resolution behavior, runner-image/system-library identity, and any other producer-environment dimensions before another model-access execution is considered.

## Claim boundary

This failure is not a model-quality verdict and is not a runtime-performance result. The exact T029 artifact-equivalence gate rejected the regenerated artifact before T031 measurement.

```text
MODEL_QUALITY_VERDICT=NONE
RUNTIME_MEASUREMENT_ACCEPTED=false
T029_EXPECTED_HASH_REWRITTEN=false
TRAINING=false
PAID_COST_USD=0.0
T032_EXECUTION=false
T033_EXECUTION=false
T034_ADMISSION_DECISION=false
CANDIDATE_EXPANSION=false
```

The frozen T029 F16 and Q4 identities remain authoritative. The observed `b86ef357...` hash must not replace `b76f61cd...` merely because it reproduced twice.

## Recovery rule

No same-action Granite retry is authorized by this evidence. Canonical recovery must first produce new diagnostic or repair evidence and preserve the existing exact-candidate, zero-USD, no-training, no-downstream-authority boundaries. Any later model-access execution must again pass the canonical authority and exact-main gates.
