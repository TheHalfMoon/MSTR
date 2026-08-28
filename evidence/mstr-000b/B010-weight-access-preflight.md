# B010 — New-candidate qualification / weight-access preflight

**Task:** `B010`
**State:** COMPLETE_CANONICAL
**Canonical main at execution:** `e3ee155a7e0ed491984908998546900e594bda9a`
**Manifest:** `artifacts/manifests/B010-new-candidate-weight-access.json`
**Public metadata evidence:** run `33161954193` / job `98818272943`
**Implementation PR:** `#65`
**Final implementation head:** `2047a3aa8b7063736a490d00d1fe10709aba23e2`
**Canonical implementation merge:** `215d52f4de772639c5e64193ff48deaafb6eb2d7`
**Exact-head qualification:** run `33163285099` / job `98822614111`
**Independent adversarial review:** run `33163317056` / job `98822713286`
**Post-implementation verification:** run `33163418160` / job `98823047750`

## Exact entry evidence

```text
ENTRY_GATE_TASK = B010
ENTRY_GATE_CANONICAL_MAIN = e3ee155a7e0ed491984908998546900e594bda9a
ENTRY_GATE_RUN = 33161954193
ENTRY_GATE_JOB = 98818272943
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

## Decision

`qualification_candidates[]` is frozen to:

- `mellum-4b`
- `qwen3.5-0.8b-control`

`new_weight_access_required_candidates[]` is frozen to the same two candidates.

The lists are intentionally distinct fields even though their current members are equal. B006 admitted these two newly relevant candidates into the serious/static-qualified set. The seven other newly reviewed B006 candidates remain reference-only or fail-closed and do not enter equivalent qualification. The eight pre-existing serious T022 candidates are already represented by the prior T027/T028 acquisition/qualification lineage and are not new B010 candidates.

## Why new access is required

T028 acquired and verified model artifacts only for the prior eight candidates; neither B010 candidate appears in `artifacts/manifests/T028-acquired-artifacts.json`.

B008 accessed only `tokenizer.json` on ephemeral runners for tokenizer economics, retained no tokenizer body, and explicitly kept `MODEL_WEIGHT_ACCESS = NONE`. Therefore B008 is not reusable model-weight availability for B011/B012.

Both B010 candidates remain subject to artifact-backed equivalent qualification under B009. No model-weight body is present in Git, and no current authority permits obtaining one.

## Frozen artifact envelope

### `mellum-4b`

- Upstream: `JetBrains/Mellum-4b-base`
- Revision: `83cce2605fbdf6a3868627e9b0a5924e0072b94d`
- Weight files: two safetensor shards
- Frozen weight bytes: `8,038,527,904`
- Frozen required download bytes: `8,048,099,065`
- Rights: Apache-2.0 / permissive / public / non-gated
- USD ceiling: `0.00`

### `qwen3.5-0.8b-control`

- Upstream: `Qwen/Qwen3.5-0.8B-Base`
- Revision: `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`
- Weight files: one safetensor shard
- Frozen weight bytes: `1,746,942,600`
- Frozen required download bytes: `1,769,897,109`
- Rights: Apache-2.0 / permissive / public / non-gated
- USD ceiling: `0.00`

The JSON manifest carries per-file byte counts and upstream SHA-256 values wherever the public model metadata exposed them. Missing upstream SHA-256 values for ordinary Git metadata files are explicitly marked unavailable rather than guessed.

## Executor, storage, retention, cleanup

Any future B011 access is restricted to an approved ephemeral cloud runner after exact separate founder authorization. Large artifacts must never be committed to Git or stored on the founder machine. Partial/failed downloads must be deleted immediately. Successful verified artifacts may be retained only in the canonical external-artifact location for the minimum period required by B012/downstream closeout. Any authentication, gated terms, payment, unexpected redirect host, or cost above USD 0.00 must fail closed.

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
CONVERSION_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
TRAINING_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B010 freezes an access plan only. The `COMPLETE_CANONICAL` record is valid only when this closeout is present on canonical `main` and the required post-closeout exact-main verification has passed. Because `new_weight_access_required_candidates[]` is non-empty, B011 remains explicitly blocked and still requires separate exact founder authorization before any model-weight access. Continuation authority or completion of B010 is not that authorization.
