# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T008 = 8456f5d19c9fac1bc1d98f11de5e5d3f71be5d8e
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
ACTIVE_SPEC = MSTR-000
SPEC_KIT_PACKAGE = CANONICAL
```

## Canonical completed history

```text
T000 = COMPLETE_CANONICAL / UNIVERSAL_LAPTOP_MATRIX
T001 = COMPLETE_CANONICAL / MSTR-MEASURE-v0
T002 = COMPLETE_CANONICAL / MSTR-DIST-v0
T003 = COMPLETE_CANONICAL / QUALIFICATION_HARNESS_BOOTSTRAP
T004 = COMPLETE_CANONICAL / STRICT_LOCAL_SCHEMA_VALIDATION
T005 = COMPLETE_CANONICAL / TYPED_ERRORS_AND_STABLE_IDENTITIES
T006 = COMPLETE_CANONICAL / FAIL_CLOSED_RIGHTS_GATE
T007 = COMPLETE_CANONICAL / IMMUTABLE_EVIDENCE_SERIALIZATION
```

Latest canonical merge before T008: `8456f5d19c9fac1bc1d98f11de5e5d3f71be5d8e`.

## Active work

```text
ACTIVE_TASK = T008
ACTIVE_BRANCH = task/000-t008-manifest-loaders
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T008_CANONICAL = T009
```

T008 implements local-only candidate/task/benchmark manifest loading and validation. Candidate and task records use the canonical T004 schemas. Benchmark manifests use strict `mstr.benchmark.v1` structure until a later task explicitly introduces another versioned contract. Successful loads record the exact source-file SHA-256.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T008-manifest-loaders.md`.

## Product invariant

```text
PRIMARY_PRODUCT = UNIVERSAL_LAPTOP_CODER
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8K
CPU_ONLY_BASIC_OPERATION = REQUIRED
DISCRETE_GPU_REQUIRED = NO
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
ACCOUNT_OR_API_KEY_REQUIRED = NO
OFFLINE_AFTER_ACQUISITION = REQUIRED
TELEMETRY_DEFAULT = OFF
WINDOWS + LINUX + MACOS = REQUIRED_PLATFORM_FAMILIES
```

The final measured support floor remains unfrozen until MSTR-000 closeout.

## Model / compute authority

```text
FINAL_BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_T008
MODEL_EXECUTION = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED_IN_MSTR-000
PRODUCTION_MODEL_RELEASE = NONE
CANDIDATE_ADMISSION = NONE_BY_T008
```

The first possible model-weight acquisition remains T028 and requires separate exact authorization after all prerequisites are canonical. T053 remains the only MSTR-000 bounded micro-adaptation gate and also requires separate exact authorization.

## Manifest rule

Manifest loading is local-file-only and fail closed. Candidate/task manifests must satisfy their existing canonical schemas; benchmark manifests must satisfy the versioned local structural contract. Source URLs inside metadata are inert strings during T008 loading and are never followed.

## Next gate

If T008 is reviewed and merged without scope expansion, proceed to T009: score-surface/report comparability rules. T009 does not authorize model-weight access.
