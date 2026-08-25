# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T010 = e042b3397af30156a243dc8a981f4f2bda6fa438
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
ACTIVE_SPEC = MSTR-000
SPEC_KIT_PACKAGE = CANONICAL
ACTIVE_TASK = T010
ACTIVE_BRANCH = task/000-t010-offline-cli
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T010_CANONICAL = T011
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
T009 = COMPLETE_CANONICAL / SCORE_COMPARABILITY
T010 = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION / OFFLINE_CLI_COMMANDS
```

T009 canonical merge: `7a1cea4c3462fb3d811e8b6c20303ab16cbfd94c`.

## Active work

```text
ACTIVE_TASK = T010
ACTIVE_BRANCH = task/000-t010-offline-cli
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
```

T010 implements the dependency-light offline CLI families `validate`, `rights`, `candidate static`, and `manifest validate` in `src/mstr_qualify/cli.py`. All commands are local-filesystem-only, deterministic JSON output, with a documented 0/1/2 exit-code contract. Offline discipline is enforced by socket-blocking integration tests. No weights, no execution, no network, no paid compute.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T010-offline-cli.md`.

## Resume boundary (consumed 2026-08-24)

The founder explicitly resumed MSTR after WePLD via direct founder direction. Live GitHub main was revalidated at `e042b3397af30156a243dc8a981f4f2bda6fa438` before any mutation; open PRs were empty; no checks were pending. T010 was confirmed as the next dependency-satisfied task and started under the governed workflow.

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

## Planned training execution strategy — not current authority

```text
PRIMARY_ACCESSIBLE_COMPUTE_CANDIDATE = GOOGLE_COLAB
PRIMARY_EFFICIENT_TRAINING_FRAMEWORK_CANDIDATE = UNSLOTH
DEFAULT_QWEN3_5_PILOT_IF_SELECTED = LORA_16BIT_BF16_OR_FP16
QWEN3_5_QLORA = EXPERIMENT_ONLY_NOT_DEFAULT
CHECKPOINT_RESUME = REQUIRED
TRAINING_RUN_MANIFEST = REQUIRED
POST_TRAIN_EXPORT = LORA + MERGED_MASTER + GGUF_TOURNAMENT
```

This is a program plan, not authority to access weights, install training stacks, allocate GPUs, or train.

## Model / compute authority

```text
FINAL_BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACCESS = NONE / NOT_AUTHORIZED_BY_T010
MODEL_EXECUTION = NONE
BENCHMARK_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE_BY_T010
PAID_MODEL_API_EXECUTION = NONE
GOOGLE_COLAB_EXECUTION = NONE
UNSLOTH_INSTALL_OR_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
TRAINING = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED_IN_MSTR-000
PRODUCTION_MODEL_RELEASE = NONE
```

Within MSTR-000, T028 remains the first possible model-weight acquisition and requires separate exact authorization after prerequisites are canonical. T053 remains the only bounded micro-adaptation gate and also requires separate exact authorization.

## Resume gate

When the founder returns after WePLD:

1. verify live `main`, open PRs, reviews, checks, and task graph;
2. read `.specify/memory/constitution.md`;
3. read this file;
4. read `docs/canonical/PROGRAM_ROADMAP.md`;
5. read `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`;
6. read the full MSTR-000 Spec Kit package;
7. confirm T010 is still the correct next task;
8. start only the exact authorized task on a fresh branch.

Canonical resume handoff: `docs/handoffs/MSTR-RESUME-AFTER-WEPLD.md`.
