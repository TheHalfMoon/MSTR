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

The first canonical T031 binding instead used Python `3.11.9` and a later deterministic dependency lock. The failed exact-artifact comparison proves that environment is insufficient to reproduce the historical Granite F16 identity. This evidence does not claim that any one package difference is the proven root cause.

## First replay attempt and fail-closed qualification result

The first replay repair preserved the existing transitive dependency lock and overlaid seven reconstructed direct packages. Exact-head qualification run `34031723964` rejected that design before model access because `pip check` proved the mixed environment was inconsistent:

```text
transformers 5.15.1 requires typer, which is not installed.
transformers 5.15.1 has requirement huggingface-hub<2.0,>=1.5.0, but you have huggingface-hub 0.36.2.
```

Qualification status for that head is therefore `FAILED` and unusable. No review, premerge, merge, or model retry may inherit from it.

```text
QUALIFICATION_RUN=34031723964
REPLAY_INSTALL_SMOKE=FAILURE
MODEL_ACCESS=NONE
TRAINING=false
PAID_COST_USD=0.0
```

## Complete replay dependency closure

A second no-model resolver run rebuilt the complete compatible dependency closure for the replay direct requirements under Python `3.11.16` and CPU-only `torch==2.13.0+cpu`. The resolver selected 40 packages in total. Every selected wheel was downloaded during the evidence run and its SHA-256 was computed from the downloaded bytes; the resulting URLs and hashes are frozen in `artifacts/manifests/T031-t029-producer-replay-overlay.json`.

Direct replay requirements remain:

```text
gguf==0.19.0
numpy==2.4.6
protobuf==7.36.0
safetensors==0.8.0
sentencepiece==0.2.2
torch==2.13.0+cpu
transformers==5.15.1
```

The complete closure additionally includes all resolver-required dependencies, including `huggingface-hub==1.30.0`, `typer==0.27.2`, `tokenizers==0.22.2`, and their exact transitive requirements.

Complete-closure evidence:

```text
RUN_ID=34031883766
EVIDENCE_HEAD=64a341da5d2537c36fbca79ce8eed289f3578411
ARTIFACT_ID=9988881418
ARTIFACT_ZIP_SHA256=545625ad24094ca232ef72b2d214d286a4659d25850b4e8b2aa410cfa033ac06
RESOLUTION_REPORT_SHA256=680b6d6258c25edeb8ee53cc06e8c1b47922dd1ad7263bb4a3642a44ceaa65c6
PIP_REPORT_SHA256=58a431fa0386d4a97d04da53fea9d535115f27cbac3c0f082e0b5889ead7b912
PACKAGE_COUNT=40
MODEL_ACCESS=NONE
TRAINING=false
PAID_COST_USD=0.0
```

`torch==2.13.0+cpu` is a CPU-only distribution from the same 2.13.0 code line. It is not asserted to be byte-identical to the historical PyPI distribution. The complete replay closure is likewise not asserted to prove unknown historical transitive package identities. The only permitted equivalence proof remains reproduction of the exact frozen T029 F16, Q4_K_M, and Q4_K_S SHA-256 identities.

## Repair boundary

The repaired installer may only:

- require Python `3.11.16` and the existing frozen system build-tool identities;
- install the existing hash-pinned pip identity plus the complete 40-package replay closure using verified HTTPS wheels, `--no-index`, and `--no-deps`;
- verify every installed replay package version and require `pip check` to pass before model access;
- keep the existing source, candidate, revision, file, llama.cpp, runtime, measurement, dispatch, concurrency, cost, and retention boundaries unchanged;
- require the exact canonical T029 F16, Q4_K_M, and Q4_K_S identities before any T031 measurement is accepted.

The repair does not authorize B012, T032, T033, T034, training, weight changes, paid compute/API use, new candidates, new revisions, Git model binaries, or founder-machine model binaries.

A repaired Granite retry is prohibited until the final repair head is canonical after fresh exact-head qualification, independent substantive semantic/security/governance review, mandatory premerge verification, guarded merge, and exact-main postmerge verification.
