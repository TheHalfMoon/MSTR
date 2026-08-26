# MSTR Current State

**Checkpoint:** 2026-08-26 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_AT_MSTR_000A_PLANNING_BASE = e21d72df6d928310257ec15fcad26dbe780cb7e5
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION / T029_Q4_QUANTIZATION_ACTIVE
ACTIVE_SPEC = MSTR-000
SPEC_KIT_PACKAGE = CANONICAL
ACTIVE_TASK = T029_Q4_PROFILE_QUANTIZATION_QUALIFICATION
OPEN_PR_AT_CHECKPOINT = #35 feat(mstr-000): implement T029 ephemeral Q4 quantization runner
OPEN_PR_HEAD_AT_CHECKPOINT = 7ece09ca2b32f1a375382ce277978888e028f786
```

Live GitHub truth overrides this snapshot if any state moved after the checkpoint.

## Founder Product Objective

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DVCR / DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC / TIME_TO_VERIFIED_COMPLETION
```

MSTR is a code-specialized builder as its primary optimization target. General reasoning is retained where it improves software planning, implementation, debugging, verification, and safe execution.

## Mandatory Sequence Amendment

The founder-directed Agent Harness / Direction-to-Done package is:

`specs/001-agent-harness-verified-loop-foundation/`

Canonical strategy:

`docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`

The execution sequence is:

```text
T029 -> T030 -> T031 -> T032 -> T033 -> T034
                                      |
                                      v
MSTR-000A VERIFIED AGENT HARNESS + DIRECTION-TO-DONE FOUNDATION
                                      |
                                      v
reconcile/finalize interaction + tournament + data/training preflight
                                      |
                                      v
SEPARATE EXPLICIT WEIGHT-CHANGING TRAINING GATE
```

Therefore:

```text
T029-T034 = CONTINUE
MSTR_000A_IMPLEMENTATION_ENTRY = AFTER_T034_COMPLETE_CANONICAL
POST_T034_BYPASS_TO_TRAINING = PROHIBITED
WEIGHT_CHANGING_TRAINING = SEPARATELY_GATED
```

The package does not block completion of T029–T034.

## Canonical Completed History

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
T010 = COMPLETE_CANONICAL / OFFLINE_CLI_COMMANDS
T011 = COMPLETE_CANONICAL / HARNESS_QUALITY_GATES
T012-T018 = COMPLETE_CANONICAL / SEVEN_STATIC_QUALIFIED_FOUNDATIONS_AND_CONTROLS
T019 = COMPLETE_CANONICAL / REFERENCE_ONLY_RECORD
T020 = COMPLETE_CANONICAL / POST_TRAINED_COMPARISONS
T021 = COMPLETE_CANONICAL / LANDSCAPE_RESCAN
T022 = COMPLETE_CANONICAL / BOUNDED_WEIGHT_ELIGIBLE_SET
T023 = COMPLETE_CANONICAL / RUNTIME_PLATFORM_ADAPTER_PROTOCOLS
T024 = COMPLETE_CANONICAL / ARTIFACT_MANIFEST_HASH_VERIFICATION
T025 = COMPLETE_CANONICAL / CROSS_PLATFORM_MEMORY_PAGING_SAMPLERS
T026 = COMPLETE_CANONICAL / MEASURE_V0_MONOTONIC_EVENT_LOGIC
T027 = COMPLETE_CANONICAL / WEIGHT_ACCESS_ACQUISITION_PREFLIGHT
T028 = COMPLETE_CANONICAL / WEIGHT_ACQUISITION_ALL_EIGHT_ACQUIRED_VERIFIED
```

## Phase-4 / T028 Merge Record

```text
T023: PR #25 -> fece0f3382ce383ca8e68dd875b48a46d4cc7fba
T024: PR #26 -> c593fce1655ee857f237b3fd476fc8e14cb836fe
T025: PR #27 -> 89a48ba834eb9fa012b1515ec774dae68315ec49
T026: PR #28 -> 52d86f0c89bd0323d19aae776ae01aa4ebf5bc58
T027: PR #30 -> 15b691cdf27103a632c5d982b822563859cf0094
STORAGE_ARCHITECTURE: PR #33 -> zero-large-artifact policy canonical
T028: PR #34 -> e21d72df6d928310257ec15fcad26dbe780cb7e5 canonical state after acquisition
```

T028 acquisition result:

```text
qwen3.5-2b = ACQUIRED_VERIFIED
qwen3.5-4b = ACQUIRED_VERIFIED
ministral-3-3b = ACQUIRED_VERIFIED
qwen3-4b = ACQUIRED_VERIFIED
granite-4.1-3b = ACQUIRED_VERIFIED
smollm3-3b = ACQUIRED_VERIFIED
qwen2.5-coder-1.5b = ACQUIRED_VERIFIED
yi-coder-1.5b = ACQUIRED_VERIFIED
FOUNDER_MAC_MODEL_BINARIES = ZERO
GIT_MODEL_BINARIES = ZERO
T028_COST = USD_0_00
```

Aggregate T028 manifest: `artifacts/manifests/T028-acquired-artifacts.json`.

## Storage Architecture

Canonical policy: `docs/canonical/STORAGE_ARCHITECTURE.md`.

```text
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
MAC_RECEIVES = SOURCE_CODE | CONFIGS | MANIFESTS | HASHES | METRICS | EVIDENCE | REPORTS
MODEL_BINARIES_ON_MAC = PROHIBITED
GIT_TREE_BINARIES = PROHIBITED
ACQUISITION/CONVERSION_LARGE_ARTIFACT_EXECUTION = APPROVED_EPHEMERAL_RUNNERS_WITHIN_TASK_SCOPE
PERSISTENCE_FOR_ORIGINALS = UPSTREAM_PINNED_REVISIONS
PERSISTENCE_FOR_DERIVED = NONE_BY_DEFAULT / REGENERATE_ON_DEMAND
```

Any new persistent large-artifact cloud store requires a separate founder decision.

## Active Work — T029

T029 is the next dependency-satisfied MSTR-000 task.

Goal:

```text
Build/obtain quality-oriented and compatibility-oriented Q4 profiles
with exact source identity + quantizer/tool commit + recipe + output hash/size.
```

At this checkpoint PR #35 is open from branch `feat/000-t029-q4-quantization`, head `7ece09ca2b32f1a375382ce277978888e028f786`.

Do not mutate or supersede that PR from MSTR-000A planning work unless live repository truth establishes a real conflict.

## T022 Candidate Decision Summary

T022 admits eight static-qualified records into the bounded weight-eligible set:

Foundations:
- Qwen3.5-2B
- Qwen3.5-4B
- Ministral-3-3B
- Granite-4.1-3B
- SmolLM3-3B

Controls:
- Qwen3-4B architecture control
- Qwen2.5-Coder-1.5B code control
- Yi-Coder-1.5B code control

Qwen2.5-Coder-3B remains `reference_only` because its research license fails the primary rights gate. AFM-4.5B-Base remains a post-trained/reference comparison because upstream material documents post-training despite the name.

No candidate is final backbone authority yet.

## Product Invariant

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

## Agent Harness / Training Strategy

MSTR now explicitly co-designs model, harness, environments, verifier, and training signal.

Required score surfaces:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Default topology:

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

MSTR-000A must freeze/qualify before weight-changing agent training:
- Build Loop v0;
- append-oriented typed event log + replay;
- compact AgentState;
- neutral/MSTR/WePLD harness surfaces;
- environment setup/admission MVP;
- verifier/finalizer + reward-shortcut battery;
- private/fresh Direction-to-Done v0;
- DVCR/TTVC and failure-inclusive diagnostics;
- failure/recovery trajectory contract;
- bounded MSTR Research Loop v0;
- downstream task reconciliation.

## Planned Training Execution — Not Current Authority

```text
PRIMARY_ACCESSIBLE_COMPUTE_CANDIDATE = GOOGLE_COLAB
PRIMARY_EFFICIENT_TRAINING_FRAMEWORK_CANDIDATE = UNSLOTH
TRAIN_AND_SERVE_LOOP_SEMANTICS = COMPATIBLE_OR_MIGRATION_PROVEN
CODE_FIM_PRIOR = REQUIRED_TO_REMAIN_STRONG
EXECUTION_GROUNDED_SFT = PLANNED
FAILURE_RECOVERY_DATA = PLANNED
AGENTIC_RL = LATER_SEPARATELY_GATED
CHECKPOINT_RESUME = REQUIRED
TRAINING_RUN_MANIFEST = REQUIRED
QUANTIZED_REGRESSION = REQUIRED_AFTER_MATERIAL_TRAINING
```

This is a program plan, not weight-changing authority.

## Model / Compute Authority

```text
FINAL_BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
BUILD_LOOP = PLANNED_MSTR_000A
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACQUISITION_T028 = COMPLETE_VERIFIED
MODEL_ARTIFACT_PERSISTENCE_ON_FOUNDER_MAC = PROHIBITED
EPHEMERAL_ARTIFACT_REACQUISITION = TASK_SCOPED_ONLY
PAID_MODEL_API_EXECUTION = NONE
PAID_COLAB = NONE
RENTED_TRAINING_COMPUTE = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED
PRODUCTION_MODEL_RELEASE = NONE
```

The existing T053 bounded adaptation gate does not become authorized by this planning amendment. After MSTR-000A reconciliation, T053 may remain the gate or be superseded by an explicitly documented equivalent gate; either way a separate founder authorization remains required.

## Quality Gates

The repository's frozen quality gates remain authoritative for new material heads:

```text
pytest full suite
ruff src + tests (+ task surfaces where configured)
strict mypy
offline CLI validate
```

Historical PASS results do not transfer to a new head. If no GitHub Actions/CI run exists, do not claim CI PASS.

## Resume / Read Gate

Before any material mutation:

1. verify live `main`, open PRs, branches, exact heads, reviews, checks, and task graph;
2. read `AGENTS.md`;
3. read `.specify/memory/constitution.md`;
4. read this file;
5. read `docs/canonical/PROGRAM_ROADMAP.md`;
6. read `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`;
7. read `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`;
8. read the full active Spec Kit package;
9. if T029–T034 remain active, continue them in order;
10. once T034 is canonical, enter `specs/001-agent-harness-verified-loop-foundation/` before any weight-changing training path.

Live canonical GitHub truth always overrides stale handoffs.
