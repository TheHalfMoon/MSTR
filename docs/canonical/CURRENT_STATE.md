# MSTR Current State

**Checkpoint:** 2026-08-27 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_AT_LATEST_RECONCILIATION = d0e90740924f6991da361536e7f835eb55ae9145
CANONICAL_TREE = c602b5142a31abe55d3519913f5badfaa27469cc
PROJECT_PHASE = PRETRAINING_FOUNDATION / MSTR-000A_EARLY_SAFE + MSTR-000B_GOVERNANCE_EXECUTION
ACTIVE_IMPLEMENTATION_SPEC = MSTR-000B
ACTIVE_IMPLEMENTATION_TASK = B004_000A_SEQUENCE_RECONCILIATION / ENTRY_GATE_PROVEN
PLANNING_SPEC = NONE_SEPARATE / MSTR-000B_CANONICAL
MSTR_000B_PLANNING_PR = #39 / MERGED e1b3cbd74ae0a74a80e3f345faef56da13818149
LAST_COMPLETE_MSTR_000B_TASK = B003 / CLOSEOUT_MERGE d0e90740924f6991da361536e7f835eb55ae9145
CURRENT_ELIGIBLE_MSTR_000B_TASK = B004
```

Live GitHub truth overrides this snapshot.

## Founder Product Objective

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DVCR / DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC / TIME_TO_VERIFIED_COMPLETION
PRIMARY_EFFICIENCY_TARGET = VERIFIED_SOFTWARE_CAPABILITY_PER_GB
```

MSTR is a code-specialized builder as its primary optimization target. General reasoning is retained where it improves software planning, implementation, debugging, verification, and safe execution.

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
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Canonical History Through A004

```text
T000-T028 = COMPLETE_CANONICAL
T029 = IMPLEMENTATION_MERGED_PREVIOUSLY / CANONICAL_RECONCILIATION_STATUS MUST BE READ FROM LIVE MSTR-000 TASK EVIDENCE

A001 = COMPLETE_CANONICAL / LOOP_CONTRACT_V0
A002 = COMPLETE_CANONICAL / RUN_EVENT_V0
A003 = COMPLETE_CANONICAL / EVENT_LOG_AND_DETERMINISTIC_REPLAY
A004 = COMPLETE_CANONICAL / AGENT_STATE_PROJECTION_AND_BOUNDED_COMPACTION
A005-A018 = PENDING / EARLY_SAFE_ONLY_WHEN_EXACT_PREREQUISITES_PASS
A019-A024 = PENDING / CONVERGENCE_GATED
```

A001/A002 canonical implementation:

```text
PR #37
HEAD = b4547f9393644586f893f5cd7ddd420f82bc6f2a
MERGE = 5693749dd560979496efad488789ec35b2c2a84d
HISTORICAL_HEAD_GATES_REPORTED_BY_PR:
  pytest = 372 passed
  ruff = clean
  mypy strict = clean
  offline validate = exit 0 / 8 schemas
```

A003 canonical implementation:

```text
PR #38
HEAD = 41122ae8dee65b2a6b3c6b188cf335d74088b06f
MERGE = 2c02eb68a32264c86f69eb7ffc1c99ad87328376
SCOPE:
  integrity-chained append-oriented event log
  monotonic sequence validation
  deterministic replay
  model-visible history reconstruction
HISTORICAL_HEAD_GATES_REPORTED_BY_PR:
  pytest = 372 passed
  ruff = clean
  mypy strict = clean
  offline validate = exit 0
EXTERNAL_REVIEW_NOTE:
  Qodo high-level assessment was positive
  CodeRabbit review was rate-limited and is NOT claimed as PASS
```

Historical head gates do not transfer to later heads. No CI PASS is claimed for PR #38.

A004 canonical implementation and closeout:

```text
IMPLEMENTATION_PR = #45
FINAL_IMPLEMENTATION_HEAD = d0098548766232c9fa1a879941978d1735ef9e4a
IMPLEMENTATION_MERGE = 564096fc9e8ec3e2b0aa9505926e15f66b00ce74
CLOSEOUT_PR = #46
CLOSEOUT_HEAD = c91d603ab3175260348706b3f879b86900511510
CLOSEOUT_MERGE = c2d0ee8a6b9d47275c4d309cd187c1ed0d35fb02
STATE = COMPLETE_CANONICAL
```

## MSTR-000A Next State

A001-A004 are canonical. The next MSTR-000A early-safe task is A005, but B004 does not execute or authorize A005. A005-A018 remain individually gated by their exact prerequisites and the machine task validator where represented. Candidate-dependent A019-A024 remain convergence-gated and may not consume an incomplete or incomparable candidate pool.

## Governance Drift and Resolution

The earlier MSTR-000A package declared a blanket:

```text
ENTRY_GATE = T034_COMPLETE_CANONICAL
```

However A001-A003 were implemented and merged before that blanket gate was reconciled. The repository must not hide this fact.

The MSTR-000B planning amendment resolves the inconsistency by replacing the coarse gate with exact task classes:

```text
EARLY_SAFE_MSTR_000A = A001-A018 where exact prerequisites are satisfied, work is model-independent, and no unqualified candidate/external authority is consumed

CONVERGENCE_MSTR_000A = A019-A024 only after stable/equivalent candidate qualification and required MSTR-000B outputs
```

MSTR-000B also requires a machine task/dependency eligibility validator so future autonomous execution cannot rely on prose sequencing alone.

PR #39 merged as `e1b3cbd74ae0a74a80e3f345faef56da13818149`; the MSTR-000B sequence amendment is canonical. B004 records the later live reconciliation after A004 and the B001-B003 governance chain. It does not rewrite or reopen A001-A004.

## MSTR-000B Canonical Foundation

```text
PLANNING_PR = #39 / MERGED
PLANNING_MERGE = e1b3cbd74ae0a74a80e3f345faef56da13818149
WORKSTREAM = MSTR-000B
TITLE = Code Model Supremacy Pre-Training Foundation
B001 = COMPLETE_CANONICAL
B002 = COMPLETE_CANONICAL
B003 = COMPLETE_CANONICAL
B004 = ENTRY_GATE_PROVEN / IMPLEMENTATION_ACTIVE
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
NEW_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_PLANNING_ALONE
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
```

Primary gaps addressed:

1. machine task/dependency enforcement;
2. mission-aligned backbone rescan including code-specialized bases;
3. tokenizer/code-density economics;
4. Data Constitution;
5. software-evolution corpus contract;
6. execution-filtered student self-alignment;
7. bounded teacher rescue;
8. checkpoint-relative frontier curriculum;
9. verifier-health contract;
10. test-generation curriculum;
11. feature/greenfield curriculum;
12. multi-fidelity autoresearch ladder;
13. adaptive test-time compute/selective context;
14. Q4-in-the-loop promotion;
15. LoRA/rsLoRA/QLoRA method preflight;
16. Repository Health Delta;
17. cross-harness robustness.

## Backbone Rescan Finding

The historical T021 scan excluded many specialized variants while the current mission is explicitly code-specialized. Therefore the old search policy is no longer sufficient for final backbone selection.

MSTR-000B requires a new metadata rescan that treats code-specialized base/foundation models as first-class candidates.

`JetBrains/Mellum-4b-base` is a mandatory review candidate because it is a concrete compact code-specialized base that was absent from the existing pool. It is NOT preselected or authorized for weight access.

New candidate weight access outside the existing T027/T028 envelope requires a new exact founder authorization.

## Existing T022/T028 Candidate History

T022 admitted eight static-qualified records into the bounded weight-eligible set:

Foundations:
- Qwen3.5-2B
- Qwen3.5-4B
- Ministral-3-3B
- Granite-4.1-3B
- SmolLM3-3B

Controls:
- Qwen3-4B
- Qwen2.5-Coder-1.5B
- Yi-Coder-1.5B

T028 acquired/verified all eight under the canonical zero-large-artifact architecture, with no model binaries on the founder Mac or Git and USD 0.00 spend.

These records are not invalidated by MSTR-000B. They remain evidence candidates in the expanded product-aligned comparison.

## Storage Architecture

Canonical policy remains `docs/canonical/STORAGE_ARCHITECTURE.md`.

```text
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
MAC_RECEIVES = SOURCE_CODE | CONFIGS | MANIFESTS | HASHES | METRICS | EVIDENCE | REPORTS
MODEL_BINARIES_ON_MAC = PROHIBITED
GIT_TREE_BINARIES = PROHIBITED
PERSISTENCE_FOR_ORIGINALS = UPSTREAM_PINNED_REVISIONS
PERSISTENCE_FOR_DERIVED = NONE_BY_DEFAULT / REGENERATE_ON_DEMAND
```

Any new persistent large-artifact cloud store requires separate founder authority.

## Agent Harness / Training Strategy

Required score surfaces:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Default runtime topology:

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

MSTR-000B adds the principle that harness quality is necessary but insufficient. The model foundation, code prior, data distribution, student-frontier curriculum, verifier health and Q4 behavior are co-equal optimization targets.

## Planned Training Execution — Not Current Authority

```text
PRIMARY_ACCESSIBLE_COMPUTE_CANDIDATE = GOOGLE_COLAB
PRIMARY_EFFICIENT_TRAINING_FRAMEWORK_CANDIDATE = UNSLOTH
CODE_FOCUSED_CONTINUED_PRETRAINING = FIRST_CLASS_HYPOTHESIS
STUDENT_SELF_ALIGNMENT = PLANNED
SOFTWARE_EVOLUTION_DATA = PLANNED
FRONTIER_CURRICULUM = PLANNED
VERIFIER_HEALTH = REQUIRED_BEFORE_CLEAN_TRAINING_ADMISSION
TEST_GENERATION = PLANNED_CORE_SKILL
AGENTIC_RL = LATER_SEPARATELY_GATED
CHECKPOINT_RESUME = REQUIRED
TRAINING_RUN_MANIFEST = REQUIRED
Q4_REGRESSION = REQUIRED_AFTER_MATERIAL_WEIGHT_CHANGE
```

Training method is not preselected. MSTR-000B requires equivalent LoRA/rsLoRA/QLoRA preflight where current backbone/framework support permits.

## Model / Compute Authority

```text
FINAL_BACKBONE = UNSELECTED
STABLE_PRODUCT_ALIGNED_CANDIDATE_POOL = NOT_YET_FROZEN
INTERACTION_CONTRACT = UNFROZEN
BUILD_LOOP = PARTIALLY_IMPLEMENTED_MSTR_000A
DEFAULT_CONTEXT_ENGINE = UNSELECTED
LOCAL_RUNTIME_BASELINE = UNSELECTED

MODEL_WEIGHT_ACQUISITION_T028 = COMPLETE_VERIFIED
NEW_CANDIDATE_WEIGHT_ACCESS = NOT_AUTHORIZED
PAID_MODEL_API_EXECUTION = NONE
PAID_COLAB = NONE
RENTED_TRAINING_COMPUTE = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NOT_STARTED / PROHIBITED
LARGE_SCALE_RL = NOT_STARTED / PROHIBITED
PRODUCTION_MODEL_RELEASE = NONE
```

## Quality Gates

The repository's frozen quality gates remain authoritative for every material head:

```text
pytest full suite
ruff configured paths
strict mypy
offline CLI validate
```

Task-specific contract/security/evidence tests are additive.

Historical PASS results do not transfer to a new head. If no CI run exists, do not claim CI PASS.

## Resume / Read Gate

Before material mutation:

1. verify live main/open PRs/branches/exact heads/reviews/checks;
2. read `AGENTS.md`;
3. read constitution;
4. read this file;
5. read `PROGRAM_ROADMAP.md`;
6. read `AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`;
7. read `CODE_MODEL_SUPREMACY_STRATEGY.md` once canonical;
8. read `TRAINING_EXECUTION_STRATEGY.md`;
9. read the exact active Spec Kit/tasks;
10. run task eligibility validation once B002 exists;
11. never infer weight/training/paid authority from generic continuation.
