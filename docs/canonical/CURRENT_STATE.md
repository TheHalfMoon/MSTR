# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_AT_PLAN_START = 318a797c42b976cd9c420a6e9303489bf852e6da
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
ACTIVE_SPEC = MSTR-000
```

The commit above includes a harmless empty `.specify/memory/.keep` bootstrap that was written directly to `main` while initializing the Spec Kit memory path. It changes no runtime or model behavior. The complete Spec Kit package is being prepared on a separate planning branch/PR.

## Canonical MSTR-000 Evidence

```text
T000 = COMPLETE_CANONICAL
T001 = COMPLETE_CANONICAL
T002 = COMPLETE_CANONICAL

T000 = UNIVERSAL_LAPTOP_MATRIX
T001 = MSTR-MEASURE-v0
T002 = MSTR-DIST-v0
```

Canonical evidence:
- `specs/000-universal-laptop-interaction-contract/evidence/T000-universal-laptop-hardware-matrix.md`
- `.../T001-measurement-procedures.md`
- `.../T002-distribution-install-privacy-contract.md`

## Product Direction

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

## Planning Reconciliation

The earlier MSTR-000 planning package is being upgraded into a complete Spec Kit implementation package.

The new package adds:

```text
.specify/memory/constitution.md
clarification-closeout.md
data-model.md
contracts/
quickstart.md
implementation-handoff.md
Spec Kit user stories / FR / SC traceability
dependency-ordered executable tasks with file paths
program roadmap
```

Only T000–T002 were canonical completed task IDs before this upgrade. The earlier incomplete T003+ draft task numbering had not become canonical evidence and is superseded by the new Spec Kit task graph.

## Active Planning Work

```text
ACTIVE_PLANNING_BRANCH = plan/000-speckit-complete-package
PLAN_PURPOSE = COMPLETE_IMPLEMENTATION_READY_SPEC_KIT_PACKAGE
NEXT_EXECUTABLE_TASK_AFTER_PLAN_MERGE = T003
```

The previously started `task/000-t003-primary-backbone-rights-gate` branch did not contain a committed canonical T003 implementation and is paused/superseded by the Spec Kit replan. It must not be treated as completed evidence.

## Model / Compute State

```text
FINAL_BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACCESS = NONE_IN_CURRENT_PLAN_PR
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
LONG_TRAINING = NOT_STARTED
LARGE_SCALE_RL = NOT_STARTED
PRODUCTION_MODEL_RELEASE = NONE
```

## Candidate Search Space

Initial static-qualification candidates remain:

- `Qwen/Qwen3.5-2B-Base`
- `Qwen/Qwen3.5-4B-Base`
- `mistralai/Ministral-3-3B-Base-2512`
- `Qwen/Qwen3-4B-Base`
- `ibm-granite/granite-4.1-3b-base`
- `HuggingFaceTB/SmolLM3-3B-Base`

Lower-bound coder control:
- `Qwen/Qwen2.5-Coder-1.5B`

Current explicit primary-backbone exclusion:
- `Qwen/Qwen2.5-Coder-3B` while its upstream licensing posture remains incompatible with MSTR's primary redistribution/commercial-use goal.

All upstream facts must be revalidated by the static qualification tasks.

## Next Gate

The next work is **not** model download or training.

After the Spec Kit package is reviewed/canonical, begin T003: bootstrap the qualification harness and repository implementation structure.

Long training remains blocked until MSTR-000 closeout + founder acceptance.
