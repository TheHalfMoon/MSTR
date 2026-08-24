# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T006 = 47b6f07449f92136336044b29f73c0a4e8a8a218
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
```

Latest canonical merge before T006: `47b6f07449f92136336044b29f73c0a4e8a8a218`.

## Active work

```text
ACTIVE_TASK = T006
ACTIVE_BRANCH = task/000-t006-rights-gate
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T006_CANONICAL = T007
```

T006 implements the generic fail-closed primary-backbone/component rights gate. It recomputes eligibility from rights facts and required component evidence instead of trusting a declared decision field. It does not qualify any named model by itself.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T006-primary-backbone-rights-gate.md`.

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

MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_T006
MODEL_EXECUTION = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED_IN_MSTR-000
PRODUCTION_MODEL_RELEASE = NONE
CANDIDATE_ADMISSION = NONE_BY_T006_ALONE
```

The first possible model-weight acquisition remains T028 and requires separate exact authorization after all prerequisites are canonical. T053 remains the only MSTR-000 bounded micro-adaptation gate and also requires separate exact authorization.

## Rights-gate rule

For primary admission, every required component must establish the intended personal/commercial use, modification, fine-tuning, quantization, and derivative redistribution rights, with no unresolved `unknown`, user-facing account/click-through/separate-license gate, or field/scale restriction. Source-specific legal/terms evidence is collected by later candidate tasks; T006 does not perform legal interpretation or external retrieval.

## Next gate

If T006 is reviewed and merged without scope expansion, proceed to T007: immutable/canonical evidence serialization and supersession semantics. T007 does not authorize model-weight access.
