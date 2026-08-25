# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN_BEFORE_T021 = 1e8a5b1
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION / PHASE_3_COMPLETE + PRE_WEIGHT_ACCESS_RESCAN_DONE
ACTIVE_SPEC = MSTR-000
SPEC_KIT_PACKAGE = CANONICAL
ACTIVE_TASK = T021
ACTIVE_BRANCH = task/000-t021-landscape-rescan
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
NEXT_TASK_AFTER_T021_CANONICAL = T22
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
T010 = COMPLETE_CANONICAL / OFFLINE_CLI_COMMANDS
T011 = COMPLETE_CANONICAL / HARNESS_QUALITY_GATES
T012-T018 = COMPLETE_CANONICAL / SEVEN_STATIC_QUALIFIED_FOUNDATIONS_AND_CONTROLS
T019 = COMPLETE_CANONICAL / REFERENCE_ONLY_RECORD
T020 = COMPLETE_CANONICAL / POST_TRAINED_COMPARISONS
T021 = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION / LANDSCAPE_RESCAN
```

Phase-3 canonical merge: PR #19 as `fa647a3`.
```

Phase-3 static candidate records live-fetched from huggingface.co at exact pinned revisions (metadata-only HTTPS GETs; no weight files). Fail-closed rights recomputation verified live: the research-licensed Qwen2.5-Coder-3B is rejected by the T006 gate as expected.

T009 canonical merge: `7a1cea4c3462fb3d811e8b6c20303ab16cbfd94c`.
T010 canonical merge: `fe60646a3833d35e7b65db431e5094b704946e72`.
T011 canonical merge: PR #17 (exact head d0c33acba0f232b218a4eac66555536b1bc90cd0).

## Active work

```text
ACTIVE_TASK = T021
ACTIVE_BRANCH = task/000-t021-landscape-rescan
TASK_STATE = COMPLETE_CANDIDATE_PENDING_PR_CANONICALIZATION
```

T021 rescan result: all six Phase-3 pins stable/unchanged; landscape scanned org-wide (49 confirmed compact permissive bases); two new candidates admitted under the same schema (arcee-ai/AFM-4.5B-Base foundation; 01-ai/Yi-Coder-1.5B coder control); three flagged-for-review (allenai/tmax-4b checkpoint-style release, microsoft/Fara1.5-4B, arcee KDA experimental variants). Candidate evidence: `evidence/T021-landscape-rescan.md`.

## Prior checkpoint (consumed)

None. Phase-3 static candidate admission is canonical. Next dependency-satisfied task is **T021**: re-scan the current approximately 1B-5B open foundation landscape immediately before first weight-access planning (`evidence/T021-landscape-rescan.md`), then **T22** selects the bounded weight-eligible set. No weight access occurs before T28's exact authorization.

## Completed in this cycle

```text
COMPLETED_TASKS = T010, T011, T012-T020 (+T021 pending canonicalization)
CHECKPOINTS_REACHED = PHASE_2_FOUNDATIONAL_HARNESS_READY + PHASE_3_STATIC_ADMISSION_COMPLETE
REVIEW_FINDINGS_RESOLVED = qodo x4, coderabbitai x5, all on-head with evidence
PUSH_PROTECTION_BYPASS = one documented false_positive (public HF revision sha matching Mistral key shape)
```

Seven static-qualified foundation/control candidates (Qwen3.5-2B/4B, Ministral-3-3B, Qwen3-4B control, Granite-4.1-3B, SmolLM3-3B, Qwen2.5-Coder-1.5B control), one reference_only record (Qwen2.5-Coder-3B — Qwen Research License fails FR-015/FR-017), and three post-trained comparison points. Ministral/Granite/SmolLM3 carry an explicit missing-LICENSE-text caveat with mandatory re-verification before any weight access.

Candidate evidence: `evidence/candidates/T012..T020`.

## Prior checkpoint (consumed)

None. Phase-2 checkpoint reached: foundational harness ready. Next dependency-satisfied tasks are the Phase-3 parallel static candidate qualifications (T012–T020), each requiring exact upstream evidence and fail-closed rights recomputation without weight access.

```text
COMPLETED_IN_THIS_CYCLE = T010 + T011 + PHASE_2_CHECKPOINT
FROZEN_QUALITY_GATES = configs/quality.toml (pytest full suite, ruff src+tests, strict mypy, offline CLI validate; all required on every future task head)
```

T011 froze harness quality gates in `configs/quality.toml` (`mstr.quality-gates.v1`): full pytest suite, ruff over src and tests, strict mypy, and offline CLI schema self-check are all required on every future task head. Pre-existing lint debt deferred by T009 was repaired; `py.typed` + dev-only `types-jsonschema` enable strict typechecking; `uv.lock` pins the gate toolchain. CI remains deliberately absent per task definition.

Candidate evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T011-harness-foundation-qualification.md`.

## T010 record

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

MODEL_WEIGHT_ACCESS = NONE / STATIC_METADATA_ONLY_IN_MSTR-000
MODEL_EXECUTION = NONE
BENCHMARK_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = METADATA_ONLY_HTTPS_GETS_HUGGINGFACE (API + raw endpoints at pinned revisions; no weight files, no gated-term acceptance)
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
