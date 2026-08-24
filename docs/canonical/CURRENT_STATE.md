# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T009 = ccf15209e9ffce663eb27af21ca1e1ad9b914469
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
T008 = COMPLETE_CANONICAL / LOCAL_MANIFEST_LOADERS
```

Latest canonical merge before T009: `ccf15209e9ffce663eb27af21ca1e1ad9b914469`.

## Active work

```text
ACTIVE_TASK = T009
ACTIVE_BRANCH = task/000-t009-comparability
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T009_CANONICAL = T010
```

T009 implements deterministic direct-comparison eligibility for raw-model, neutral-harness, and full-system score surfaces. Direct comparisons require matching measurement protocol, task/revision, verifier, timeout, cache state, hardware class, context, Interaction Contract, and sampling configuration. Seed may differ as a repeated sample under the same frozen protocol.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T009-comparability.md`.

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

## Model / compute authority

```text
FINAL_BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_T009
MODEL_EXECUTION = NONE
BENCHMARK_EXECUTION = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED_IN_MSTR-000
PRODUCTION_MODEL_RELEASE = NONE
```

The first possible model-weight acquisition remains T028 and requires separate exact authorization after all prerequisites are canonical. T053 remains the only MSTR-000 bounded micro-adaptation gate and also requires separate exact authorization.

## Comparison rule

Cold/warm cache states, different hardware classes, different task/verifier/timeout conditions, different Interaction Contracts, and different raw/neutral/full-system surfaces are separate evidence surfaces. T009 rejects direct comparison rather than normalizing them silently. TTVC summaries must retain verified-completion rate and timeout context.

## Next gate

If T009 is reviewed and merged without scope expansion, proceed to T010: dependency-light offline CLI commands for validation/static qualification. T010 does not authorize model-weight access.
