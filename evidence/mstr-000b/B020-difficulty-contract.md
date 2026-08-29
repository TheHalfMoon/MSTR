# B020 — Checkpoint-Relative Difficulty Calibration Contract Evidence

**Task:** `B020`
**Implementation PR:** #81
**Final implementation head:** `189509470eae10f1080938b0b2b873f375842f35`
**Canonical implementation merge:** `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`
**State:** COMPLETE_CANONICAL
**Contract:** `mstr.difficulty-calibration.v0`
**Canonical entry main:** `ef90e96ba3d4e2c253987d1d104e0de26ce93529`

## Canonical Entry Provenance

```text
ENTRY_GATE_TASK = B020
ENTRY_GATE_CANONICAL_MAIN = ef90e96ba3d4e2c253987d1d104e0de26ce93529
ENTRY_GATE_RUN = 33198484632
ENTRY_GATE_JOB = 98941644785
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

The entry run proved B020 `eligible=true` / `PENDING` on exact canonical main with no external authority required, canonical task drift clean, B011 still blocked by unsatisfied founder authority, and B021 still ineligible pending B020.

## Frozen Contract Semantics

`DifficultyCalibrationRecord` is checkpoint-relative. Every record binds the exact student model/checkpoint identity together with the exact harness profile and sampling identity used by the calibration evidence.

The contract freezes the canonical fields and five classes:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

Attempt accounting fails closed: `success_count` cannot exceed `attempt_count`, duplicate failure classes are rejected, and the failure-distribution counts must exactly cover `attempt_count - success_count`.

`estimated_solve_probability` is a finite value in `[0, 1]`, but B020 deliberately freezes **no probability threshold for any difficulty class**. The canonical plan reserves estimator behavior, frontier thresholds, refresh behavior, and sampling decisions for B021 fixture-only calibration/pilot evidence. This prevents a contract-only task from silently becoming training policy.

`structural_features` is a non-empty flat descriptor map. Numeric feature values must be finite; `NaN` and infinities fail closed. B020 records evidence shape only; it does not prescribe a learned feature extractor, execute a student model, or calibrate a real checkpoint.

## Cross-Contract Binding

B018 and B019 already consume `difficulty_record_identity` as a foreign-key-style evidence identity. B020 owns the canonical difficulty record shape behind that identity. A B020 record must bind its top-level `harness_profile_id` and `sampling_identity` exactly to the embedded student identity.

The design and runtime schemas are byte-identical:

```text
specs/002-code-model-supremacy-foundation/contracts/mstr-difficulty-calibration-v0.schema.json
schemas/mstr-difficulty-calibration-v0.schema.json
```

## Fixture Boundary

Fixtures are repository-owned synthetic records. They exercise structural and semantic validation only. They do not represent model execution, a real student checkpoint run, real benchmark measurements, or training-data admission.

## Authority

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B020_CONTRACT_AUTHORITY = DIFFICULTY_CALIBRATION_RECORD_SHAPE_ONLY
B020_CALIBRATION_EXECUTION = NONE
B021_FRONTIER_SAMPLER_EXECUTION = NONE
```

## Canonical Implementation Closeout

The checkpoint-relative difficulty calibration contract was merged and verified on canonical main without executing a model, calibrating a real checkpoint, or widening any external-effect authority.

- implementation PR: `#81`
- final implementation head: `189509470eae10f1080938b0b2b873f375842f35`
- canonical implementation merge: `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`
- atomic implementation build: run `33199352285` — SUCCESS
- finite-structural-feature hardening: run `33200021831` — SUCCESS
- exact hardened-head qualification: run `33234320679` — SUCCESS
- independent adversarial review: run `33234412303` — SUCCESS
- mandatory pre-merge verification: run `33234492918` — SUCCESS
- post-merge implementation verification: run `33234636531` — SUCCESS

This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It grants no model-weight access, model execution, real calibration execution, teacher/API use, paid compute, network model calls, large/private/production data ingestion, weight-changing training, B021 frontier-sampler execution, large-scale RL, or production release authority. B011 remains blocked.
