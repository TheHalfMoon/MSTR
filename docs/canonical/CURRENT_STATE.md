# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
CANONICAL_MAIN = c0ab325f2d65007d26ec65ad22fec972d2ba62e5
BOOTSTRAP_COMMIT = 4efdc5779ba5b83df6d54b42b030ff912d138722
PR_1 = MERGED_CANONICAL
PR_2 = MERGED_CANONICAL
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
```

PR #1 canonicalized MSTR-000 planning. PR #2 canonicalized T000, the universal-laptop qualification matrix. Neither introduced model weights, model execution, paid model calls, rented compute, or dependency admission.

## Founder product direction

The primary MSTR model must be installable and useful on ordinary laptops so that people can use it locally without paying for or depending on a cloud coding model.

```text
PRIMARY_PRODUCT = UNIVERSAL_LAPTOP_CODER
LOCAL_OFFLINE_CAPABLE = REQUIRED
DISCRETE_GPU_REQUIRED = NO
ACCOUNT_OR_API_KEY_REQUIRED = NO
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8192_TOKENS_PROVISIONAL
CONTEXT_LADDER = 4096 / 8192 / 16384
PRIMARY_DOWNLOAD_TARGET = <= 3_GB_Q4_CLASS
MSTR_PROCESS_RSS_SOFT_TARGET = <= 4_GB_AT_REFERENCE_CONTEXT
WHOLE_LAPTOP_USABILITY = REQUIRED
TARGET_OS = WINDOWS + LINUX + MACOS
TELEMETRY_DEFAULT = OFF
```

## Canonical T000 matrix

```text
U0 = 4_GB / 4K / STRETCH_CHARACTERIZATION
U1 = 8_GB / 8K / CPU_ONLY / UNIVERSAL_PRIMARY_GATE
U2 = 16_GB / 16K / RECOMMENDED_HEADROOM
U3 = OPTIONAL_ACCELERATION / NON_BLOCKING

REQUIRED_PLATFORM_LANES =
  WINDOWS_X86_64
  + LINUX_X86_64
  + MACOS_ARM64_M1_CLASS

REFERENCE_CONCURRENT_LOAD = OS + VS_CODE_BASELINE + MEDIUM_REPOSITORY + MSTR
FINAL_SUPPORT_FLOOR = UNFROZEN_UNTIL_T060
```

Canonical evidence:
`specs/000-universal-laptop-interaction-contract/evidence/T000-universal-laptop-hardware-matrix.md`

## T001 measurement protocol candidate

T001 defines `MSTR-MEASURE-v0` so later candidates cannot be compared under shifting latency/memory definitions.

```text
TTFI = LOCAL_INSTALL_TO_FIRST_LOCAL_INTERACTION
TTFA = TASK_ACCEPTED_TO_FIRST_EXTERNALLY_OBSERVABLE_TASK_ACTION
TTFCE = TASK_ACCEPTED_TO_FIRST_DURABLE_VERIFIED_EDIT
TTVC = TASK_ACCEPTED_TO_LAST_REQUIRED_VERIFIER_PASS

MEMORY = MSTR_PROCESS_TREE + WHOLE_SYSTEM
CACHE_STATES = PROCESS_COLD / SESSION_WARM / PREFIX_WARM
SUSTAINED_CPU_TEST = 10_MINUTES
THROUGHPUT = PREFILL_TPS + DECODE_TPS + TOKENIZER_NORMALIZED_OUTPUT
EDITOR_RESPONSIVENESS = REQUIRED_U1_GUARDRAIL
ENERGY = OPTIONAL_WHERE_RELIABLE
```

Evidence candidate:
`specs/000-universal-laptop-interaction-contract/evidence/T001-measurement-procedures.md`

## Competitive ambition

```text
PRIMARY_QUALITY_GOAL = BEST_PRACTICAL_LOCAL_SMALL_SWE_MODEL_SYSTEM
PRIMARY_SPEED_GOAL = MINIMIZE_TTVC
GENERAL_FRONTIER_SUPERIORITY_CLAIM = NOT_AUTHORIZED
```

## Candidate policy

Primary candidates must pass both a universal-laptop deployment gate and a distribution-rights gate before task-scoped weight access.

### Initial eligible static-qualification set

- `Qwen/Qwen3.5-2B-Base`;
- `Qwen/Qwen3.5-4B-Base`;
- `mistralai/Ministral-3-3B-Base-2512`;
- `Qwen/Qwen3-4B-Base`;
- `ibm-granite/granite-4.1-3b-base`;
- `HuggingFaceTB/SmolLM3-3B-Base`.

### Lower-bound code-specialized control

- `Qwen/Qwen2.5-Coder-1.5B`.

### Explicitly not eligible as primary backbone

- `Qwen/Qwen2.5-Coder-3B` while its current upstream Qwen Research License remains non-commercial.

## Active workstream

```text
ACTIVE_SPEC = MSTR-000
SPEC_STATE = CANONICAL_ACTIVE
ACTIVE_TASK = T001
ACTIVE_BRANCH = task/000-t001-measurement-procedures
TASK_STATE = EVIDENCE_CANDIDATE
BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DISTRIBUTION_CONTRACT = UNFROZEN
MEASUREMENT_PROTOCOL = MSTR-MEASURE-v0_CANDIDATE
MODEL_WEIGHT_DOWNLOAD = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_TRAINING_COMPUTE = NONE
FINAL_BACKBONE_ADMISSION = NONE
TRAINING_RUN = NONE
```

The next task after T001 canonical closeout is T002, the universal distribution/install/privacy contract. T002 also requires no model-weight access.
