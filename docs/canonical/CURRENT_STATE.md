# MSTR Current State

**Checkpoint:** 2026-08-24 Asia/Riyadh

## Repository

```text
REPOSITORY = TheHalfMoon/MSTR
CANONICAL_BRANCH = main
BOOTSTRAP_COMMIT = 4efdc5779ba5b83df6d54b42b030ff912d138722
PROJECT_PHASE = PRECONSTRUCTION
```

## Founder product direction

The primary MSTR model must be installable and useful on ordinary laptops so that people can use it locally without paying for a cloud coding model.

```text
PRIMARY_PRODUCT = UNIVERSAL_LAPTOP_CODER
LOCAL_OFFLINE_CAPABLE = REQUIRED
DISCRETE_GPU_REQUIRED = NO
REFERENCE_RAM = 8_GB
PRIMARY_DOWNLOAD_TARGET = <= 3_GB_Q4_CLASS
TARGET_OS = WINDOWS + LINUX + MACOS
```

The literal phrase "any laptop" is treated as a broad-availability product goal, not as a claim that obsolete or extremely memory-constrained hardware can run the same quality tier. MSTR-000 must define the exact supported hardware floor empirically.

## Competitive ambition

MSTR aims to maximize software-engineering intelligence per parameter, per GB, and per second. The project may compare against cloud systems such as Cursor Composer and frontier models, but claims must be workload-bounded and evidence-backed.

```text
PRIMARY_QUALITY_GOAL = BEST_PRACTICAL_LOCAL_SMALL_SWE_MODEL_SYSTEM
PRIMARY_SPEED_GOAL = MINIMIZE_TTVC
GENERAL_FRONTIER_SUPERIORITY_CLAIM = NOT_AUTHORIZED
```

## Current candidate class

The laptop constraint moves the primary tournament from ~7–9B to dense ~2–4B candidates. Larger models may be used only as teachers, upper bounds, or optional secondary editions.

Initial candidate families include:

- Qwen3.5-2B-Base;
- Qwen3.5-4B-Base;
- Ministral-3-3B-Base-2512;
- Qwen3-4B-Base;
- Qwen2.5-Coder-3B as a code-specialized control.

No candidate is selected.

## Active workstream

```text
ACTIVE_SPEC = MSTR-000
NAME = Universal Laptop Interaction Contract + Base/Local/Speed Qualification
STATE = PLANNING_CANDIDATE
BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
WEIGHT_DOWNLOAD = NOT_AUTHORIZED_BY_PLAN
TRAINING_RUN = NONE
```

MSTR-000 is preconstruction only. It defines qualification experiments and acceptance gates. Actual model downloads, training, benchmarking against external paid services, or significant compute spend require the relevant task to be separately executed after the planning PR is reviewed.
