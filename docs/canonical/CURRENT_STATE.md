# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
BOOTSTRAP_COMMIT = 4efdc5779ba5b83df6d54b42b030ff912d138722
PROJECT_PHASE = PRECONSTRUCTION
ACTIVE_PR = #1 DRAFT
```

## Founder product direction

The primary MSTR model must be installable and useful on ordinary laptops so that people can use it locally without paying for or depending on a cloud coding model.

```text
PRIMARY_PRODUCT = UNIVERSAL_LAPTOP_CODER
LOCAL_OFFLINE_CAPABLE = REQUIRED
DISCRETE_GPU_REQUIRED = NO
ACCOUNT_OR_API_KEY_REQUIRED = NO
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8192_TOKENS_PROVISIONAL
PRIMARY_DOWNLOAD_TARGET = <= 3_GB_Q4_CLASS
MSTR_PROCESS_RSS_SOFT_TARGET = <= 4_GB_AT_REFERENCE_CONTEXT
WHOLE_LAPTOP_USABILITY = REQUIRED
TARGET_OS = WINDOWS + LINUX + MACOS
TELEMETRY_DEFAULT = OFF
```

The literal phrase "any laptop" is treated as a broad-availability product goal, not as a claim that every historical machine can run the same quality tier. MSTR-000 must define the exact supported CPU/OS floor empirically, characterize 4 GB and older-hardware behavior, and measure the model while a realistic editor/OS workload is active.

## Competitive ambition

MSTR aims to maximize software-engineering intelligence per parameter, per GB, and per second. The project may compare against cloud systems such as Cursor Composer and frontier models, but claims must be workload-bounded and evidence-backed.

```text
PRIMARY_QUALITY_GOAL = BEST_PRACTICAL_LOCAL_SMALL_SWE_MODEL_SYSTEM
PRIMARY_SPEED_GOAL = MINIMIZE_TTVC
GENERAL_FRONTIER_SUPERIORITY_CLAIM = NOT_AUTHORIZED
```

## Candidate policy

Primary candidates must pass both a universal-laptop deployment gate and a distribution-rights gate before task-scoped weight access. Required rights include intended personal/commercial use, modification/fine-tuning, quantization/conversion, and redistribution of derivative MSTR artifacts.

### Initial eligible static-qualification set

- `Qwen/Qwen3.5-2B-Base`;
- `Qwen/Qwen3.5-4B-Base`;
- `mistralai/Ministral-3-3B-Base-2512`;
- `Qwen/Qwen3-4B-Base`;
- `ibm-granite/granite-4.1-3b-base`;
- `HuggingFaceTB/SmolLM3-3B-Base`.

### Lower-bound code-specialized control

- `Qwen/Qwen2.5-Coder-1.5B` — Apache-2.0, deliberately below the primary 2B–4B range to test whether a very small code-specialized base offers superior universal-laptop utility.

### Explicitly not eligible as primary backbone

- `Qwen/Qwen2.5-Coder-3B` — current upstream license is the Qwen Research License with non-commercial restrictions. It may not become the primary MSTR backbone under the universal distribution goal.

Additional candidates may be admitted only through the static qualification/rescan task. A low active-parameter count does not override a large total-weight footprint or incompatible license.

## Active workstream

```text
ACTIVE_SPEC = MSTR-000
NAME = Universal Laptop Interaction Contract + Base/Local/Speed Qualification
STATE = PLANNING_CANDIDATE
BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DISTRIBUTION_CONTRACT = UNFROZEN
MODEL_WEIGHT_DOWNLOAD = NOT_AUTHORIZED_BEFORE_CANONICAL_TASK
FINAL_BACKBONE_ADMISSION = NONE
TRAINING_RUN = NONE
```

MSTR-000 is preconstruction qualification. Once its planning package is canonical, only explicit bounded tasks may authorize pinned/checksummed candidate weight access, paid APIs, or rented compute. Such access is qualification evidence, not final model admission.
