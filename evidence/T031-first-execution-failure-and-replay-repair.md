# T031 first execution failure and producer-replay repair

Date: 2026-09-06
Task: T031
Scope: exact authorized T029 candidates only

## Live failure evidence

The first governed T031 dispatch was the exact Issue #167 command:

```text
T031_RUN granite-4.1-3b
```

GitHub Actions run `33999224131` checked out canonical `main` at `119a9bcca1c97b9edbcacd6d8d457b31206bb162`, passed the owner/issue/candidate dispatch boundary, passed the pinned Python setup, acquired and verified the exact source identity, and failed closed during F16 regeneration.

Observed failure:

```text
EXPECTED_T029_F16_SHA256=b76f61cdf1a11375c734431f661fabe937b7214a54d6defda5f6683bd3473d4d
REGENERATED_F16_SHA256=b86ef357954d1b1e5b982cc76a830e8305cc86049ca1bc4e9fcc22c7ab91a5d7
RESULT=T031_EXECUTION_FAILED_CLOSED
```

Durable workflow artifact:

```text
RUN_ID=33999224131
ARTIFACT_ID=9979311948
ARTIFACT_ZIP_SHA256=48c7b071b3ae6dfcb3b36e7ddcbc890ee8206687f5c9570026d8f927d2ad935a
FAILURE_JSON_SHA256=b39b51ef17a2628854baa61991be0f1d074785b912a889a4b6c91365061d1f36
```

The exact failure JSON is materialized at `artifacts/results/local/T031/failures/T031-granite-4.1-3b-run-33999224131.json`.

## Producer-environment discrepancy

The canonical T029 producer workflow at `406de41d132fa6d24d55814f3f6dd4fced5f12bd` used Python `3.11` without a patch pin and installed conversion dependencies from live package indexes without version pins:

```text
pip install numpy torch --index-url https://pypi.org/simple/ --quiet 2>/dev/null || pip install numpy --quiet
pip install sentencepiece protobuf gguf safetensors transformers --quiet
```

The durable T029 Granite report records Python `3.11.16`. It does not record installed Python package versions.

The first canonical T031 binding instead used Python `3.11.9` and a dependency lock derived from the later pinned `llama.cpp` requirement surface (`torch==2.11.0`, `transformers==4.57.6`, `numpy~=1.26.4`, and bounded transitive wheels). That lock is deterministic, but the failed exact-artifact comparison proves that it is not sufficient to reproduce the historical Granite F16 identity.

This evidence does **not** claim that any one package difference is the proven root cause. The exact cause is unresolved until a bounded replay environment reproduces the frozen T029 F16 and Q4 identities.

## Evidence-bounded replay reconstruction

No-model dependency resolution run `34030381077` used Python `3.11.16` and reconstructed the direct package versions observable from the 2026-08-26 T029 execution boundary. In particular, the T029 run began before the 2026-08-26 publication times of `transformers` 5.16.0 and 5.16.1, so the replay selects the preceding 5.15.1 release.

The proposed deterministic overlay is frozen at `artifacts/manifests/T031-t029-producer-replay-overlay.json` and contains exact HTTPS wheel URLs and SHA-256 identities for:

```text
gguf==0.19.0
numpy==2.4.6
protobuf==7.36.0
safetensors==0.8.0
sentencepiece==0.2.2
torch==2.13.0+cpu
transformers==5.15.1
```

`torch==2.13.0+cpu` is intentionally a CPU-only distribution from the same 2.13.0 code line. This avoids unrelated current CUDA dependency drift on a CPU-only T031 lane. It is not asserted to be byte-identical to the historical PyPI distribution. The only permitted equivalence proof remains reproduction of the exact frozen T029 F16 and Q4 SHA-256 identities.

Dependency-resolution evidence:

```text
RUN_ID=34030381077
ARTIFACT_ID=9988393963
ARTIFACT_ZIP_SHA256=ef446704d9194693187adb0f96d8dcb8d3e734e1308b04c8c785f09fd04fea2d
RESOLUTION_REPORT_SHA256=46c80945038240ef7eff4ebc20bb476361d24640fd386aae0be7270f523762ab
PIP_REPORT_SHA256=a929a2b1f704be75bd9413dc61d1ade8ddbd755d83ae44502c595cb802e918b8
CPU_TORCH_REPORT_SHA256=aaf1b38d0939c10e5c32e2cb293652d8917a09d781b986924b3dcb8c7d664df2
MODEL_ACCESS=NONE
TRAINING=false
PAID_COST_USD=0.0
```

## Repair boundary

The repair may only:

- switch the T031 execution Python identity to the evidence-observed T029 Python `3.11.16`;
- install the exact hash-pinned producer-replay overlay before conversion;
- keep the existing source, candidate, revision, file, llama.cpp, runtime, measurement, dispatch, concurrency, cost, and retention boundaries unchanged;
- require the exact canonical T029 F16, Q4_K_M, and Q4_K_S identities before any T031 measurement is accepted.

The repair does not authorize B012, T032, T033, T034, training, weight changes, paid compute/API use, new candidates, new revisions, Git model binaries, or founder-machine model binaries.

A repaired Granite retry is prohibited until the repair is canonical after fresh exact-head qualification, independent substantive semantic/security/governance review, mandatory premerge verification, guarded merge, and exact-main postmerge verification.
