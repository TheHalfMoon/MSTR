# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T007 = 4ef6ff936061aeab1f04a4e346e25dcd3735475d
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
```

Latest canonical merge before T007: `4ef6ff936061aeab1f04a4e346e25dcd3735475d`.

## Active work

```text
ACTIVE_TASK = T007
ACTIVE_BRANCH = task/000-t007-evidence-serialization
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T007_CANONICAL = T008
```

T007 implements deterministic canonical evidence bytes, content-addressed SHA-256 identity, create-exclusive immutable persistence, idempotent same-content retries, and explicit supersession chains. Corrections create new evidence and reference the prior immutable SHA-256 rather than mutating finalized evidence.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T007-immutable-evidence-serialization.md`.

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

MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_T007
MODEL_EXECUTION = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED_IN_MSTR-000
PRODUCTION_MODEL_RELEASE = NONE
```

The first possible model-weight acquisition remains T028 and requires separate exact authorization after all prerequisites are canonical. T053 remains the only MSTR-000 bounded micro-adaptation gate and also requires separate exact authorization.

## Evidence rule

Finalized evidence is immutable. The authoritative representation is canonical UTF-8 JSON plus its SHA-256 content identity. A correction must create a new record with explicit `supersedes` and `supersession_reason`; overwrite of finalized evidence is prohibited.

## Next gate

If T007 is reviewed and merged without scope expansion, proceed to T008: task/benchmark/candidate manifest loaders and validation. T008 does not authorize model-weight access.
