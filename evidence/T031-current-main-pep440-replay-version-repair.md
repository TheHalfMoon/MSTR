# T031 Current-Main PEP 440 Replay Version Repair

**Task:** `T031`

**Canonical main at failed dispatch:** `f207ed9080fba1bb597a4091029dfd2a381eb346`

**Failed run:** `34065259852`

**Candidate:** `granite-4.1-3b`

**Result classification:** `T031_EXECUTION_FAILED_CLOSED`

## Immutable Failure Evidence

The owner-scoped canonical Issue #167 dispatch reached the canonical T031 executor on `main=f207ed9080fba1bb597a4091029dfd2a381eb346`. Dispatch resolution, canonical checkout, and pinned Python setup succeeded. The execution then failed inside the hash-bound 59-wheel producer-replay installation verifier before candidate model bytes were requested.

```text
RUN_ID = 34065259852
JOB_ID = 101572780873
ARTIFACT_ID = 9998741981
ARTIFACT_NAME = t031-granite-4.1-3b
ARTIFACT_ARCHIVE_SHA256 = d430a954a37f0e2f182f1ef3ea98a53fdd9ef924daf8109ff69e089b5ead4421
FAILURE_JSON_SHA256 = 22165fc42c064a5f7b9b3c98de9c88d71d154fa0133ec25df71f835f1556b9c3
MODEL_ACCESS = NONE
TRAINING = false
PAID_COST_USD = 0.0
```

The durable failure JSON is preserved at `artifacts/results/local/T031/failures/T031-granite-4.1-3b-run-34065259852.json`.

## Root Cause

The 59 replay wheels were selected from the canonical hash-bound pre-cutoff manifests and downloaded through the existing exact SHA-256 verification path. Installation used `--no-index --no-deps`. The failure occurred only after installation when `importlib.metadata.version()` was compared to the manifest version strings by raw text equality.

For the exact `cuda-toolkit` wheel, the canonical manifest records `13.0.3`, while the installed wheel metadata is normalized by Python package metadata tooling to `13.0.3.0`. These are PEP 440-equivalent release versions. All other observed package versions matched their manifest spellings.

Therefore the run proves a verifier false-negative. It does not prove package-byte drift, replay-closure drift, candidate failure, model-quality failure, or a T031 measurement result.

## Forward-Only Repair

The replay verifier is changed only at the post-install metadata consistency check:

1. Keep the exact package list, URLs, SHA-256 digests, host allowlist, pre-cutoff shard identities, package count, pinned pip installation, `--no-index`, and `--no-deps` semantics unchanged.
2. Keep the exact T029 F16/Q4 artifact-equivalence gate unchanged.
3. Compare installed and manifest package versions with `packaging.version.Version` PEP 440 semantics instead of raw string equality.
4. Keep the installed metadata spellings in the emitted replay identity; semantic comparison does not rewrite canonical manifests.
5. Reject any package whose installed version is not PEP 440-equivalent to the exact manifest version.

The repair does not expand T031 Founder authority, candidate identities, revisions, files, model access, T032/T033/T034 authority, training authority, paid compute/API authority, or production-release authority.

## Retry Boundary

This document does not authorize a retry by itself. A Granite retry is allowed only after this repair is canonical through fresh exact-head qualification, independent substantive review, mandatory premerge verification against exact live `main`, guarded expected-head merge, and postmerge canonical verification. The existing exact T031 Founder authority and Issue #167 dispatch boundary remain the only execution authority.
