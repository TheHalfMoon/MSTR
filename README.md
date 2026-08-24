# MSTR

MSTR is an independent research and engineering project for building an **extremely capable software-engineering model and runtime that ordinary people can install and run locally on an ordinary laptop**.

## Primary Product Invariant

The universal-laptop release is the primary product, not a reduced afterthought.

```text
PRIMARY_MODE = LOCAL / OFFLINE-CAPABLE
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8K
CPU_ONLY_BASIC_OPERATION = REQUIRED
DISCRETE_GPU_REQUIRED = NO
PRIMARY_QUANT = Q4_CLASS
PRIMARY_MODEL_ARTIFACT_TARGET <= 3_GB
ACCOUNT_REQUIRED = NO
API_KEY_REQUIRED = NO
SUBSCRIPTION_REQUIRED = NO
BASIC_MODE_DOCKER_REQUIRED = NO
BASIC_MODE_PYTHON_OR_NODE_REQUIRED = NO
TELEMETRY_DEFAULT = OFF
WINDOWS + LINUX + MACOS = REQUIRED_PLATFORM_FAMILIES
```

These remain qualification targets until measured MSTR-000 closeout freezes the final support floor.

## Development Method

MSTR uses **Spec Kit / Spec-Driven Development**.

Start with:

1. `.specify/memory/constitution.md`
2. `docs/canonical/CURRENT_STATE.md`
3. `docs/canonical/PROGRAM_ROADMAP.md`
4. `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`
5. `specs/000-universal-laptop-interaction-contract/`
6. `docs/handoffs/MSTR-RESUME-AFTER-WEPLD.md`

The active MSTR-000 package contains the specification, clarification closeout, research, implementation plan, data model, machine-readable contracts, quickstart, implementation handoff, readiness checklists, evidence, and dependency-ordered tasks.

## Current State

```text
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
PROJECT_STATE = PAUSED_BY_FOUNDER_AFTER_PLAN_FINALIZATION
ACTIVE_SPEC = MSTR-000
T000-T009 = COMPLETE_CANONICAL
NEXT_TASK_ON_RESUME = T010
FINAL_BACKBONE = UNSELECTED
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TRAINING = NONE
LONG_TRAINING = NOT_STARTED
```

The pause is intentional: MSTR resumes only after the founder explicitly returns to it after completing the WePLD project. Live GitHub truth must be revalidated before any new mutation.

## Training Direction

MSTR's future training plan treats **Google Colab + Unsloth as the primary accessible execution path**, not as product dependencies:

```text
Google Colab = GPU execution environment
Unsloth     = preferred efficient training framework
MSTR runtime = separate local/offline end-user product
```

The program does **not** preselect a backbone or training precision. If a Qwen3.5 compact base wins the evidence tournament, the current default pilot is 16-bit LoRA with Unsloth (bf16 where supported, fp16 fallback where required); QLoRA is an experimental arm rather than the default for that family. Every later run must be resumable, pinned, hashed, and regression-tested. See `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

## Product Thesis

> **maximum verified software-engineering utility per GB, per second, and per unit of training evidence**

Model quality, repository localization, deterministic editing, tool reliability, executable verification, local inference, quantization, context management, and end-to-end TTVC are designed together.

## Program Roadmap

```text
MSTR-000  Qualification Harness + Universal Laptop / Interaction / Backbone Qualification
MSTR-001  Data Engine + Bounded Code/FIM Mid-Training
MSTR-002  Coding SFT + Repository / Tool / Planning Behavior
MSTR-003  Environment Factory + Agentic RL
MSTR-004  Local Inference Speed Co-Design
MSTR-005  Packaging + Security + Privacy + Offline Release Engineering
MSTR-006  MSTR Gauntlet + Release Candidate Qualification
MSTR-007  MSTR v1 Release
MSTR-008  Post-Release Evidence + Improvement Loop
```

Later workstreams remain implementation-deferred until predecessor evidence is canonical.

## External-Effect Gates Inside MSTR-000

```text
T028 = first possible explicitly authorized candidate-weight acquisition
T053 = explicitly authorized bounded equivalent micro-adaptation only
```

No MSTR-000 task authorizes long training or large-scale RL.

## Hard Boundaries

```text
NO FINAL BACKBONE SELECTION WITHOUT EVIDENCE
NO LONG TRAINING
NO LARGE DATASET INGESTION
NO LARGE-SCALE RL
NO PRODUCTION MODEL RELEASE
NO CLAIM OF GENERAL SUPERIORITY OVER CURSOR/FABLE
NO SILENT HARDWARE-FLOOR INCREASE
NO WORK DURING THE CURRENT PAUSE WITHOUT EXPLICIT FOUNDER RESUME
```

GitHub `main` is canonical. Branches, PRs, consultations, model outputs, notebooks, and benchmark results are evidence candidates until merged through the governed workflow.
