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

These are qualification targets until measured closeout freezes the final support floor.

## Development Method

MSTR uses **Spec Kit / Spec-Driven Development**.

Start with:

1. `.specify/memory/constitution.md`
2. `docs/canonical/CURRENT_STATE.md`
3. `docs/canonical/PROGRAM_ROADMAP.md`
4. `specs/000-universal-laptop-interaction-contract/`

The active MSTR-000 package contains:
- specification and user stories;
- clarification closeout;
- research decisions;
- technical implementation plan;
- data model and machine-readable contracts;
- quickstart and implementation handoff;
- implementation-readiness checklist;
- dependency-ordered executable tasks.

## Current Phase

```text
PROJECT_PHASE = PRECONSTRUCTION_QUALIFICATION
ACTIVE_SPEC = MSTR-000
T000 = COMPLETE_CANONICAL
T001 = COMPLETE_CANONICAL
T002 = COMPLETE_CANONICAL
FINAL_BACKBONE = UNSELECTED
LONG_TRAINING = NOT_STARTED
```

MSTR-000 exists to determine the correct model/runtime/distribution/interaction contract before serious training compute is spent.

## Product Thesis

MSTR is not trying to win by parameter count alone.

The target is:

> **maximum verified software-engineering utility per GB, per second, and per unit of training evidence**

That means model quality, repository localization, deterministic editing, tool reliability, executable verification, local inference, quantization, context management, and end-to-end TTVC are designed together.

## Program Roadmap

The program is split into gated workstreams:

```text
MSTR-000  Qualification + Interaction Contract
MSTR-001  Harness/Runtime Skeleton + Backbone Pilot
MSTR-002  Data Engine + Code/FIM Mid-Training
MSTR-003  Coding SFT + Repository/Tool Behavior
MSTR-004  Environment Factory + Agentic RL
MSTR-005  Local Inference Speed Co-Design
MSTR-006  Packaging + Security + Privacy
MSTR-007  Gauntlet + Release Candidate Qualification
MSTR-008  v1 Release + Evidence Loop
```

See `docs/canonical/PROGRAM_ROADMAP.md`.

## Hard Boundaries During MSTR-000

```text
NO FINAL BACKBONE SELECTION WITHOUT EVIDENCE
NO LONG TRAINING
NO LARGE DATASET INGESTION
NO LARGE-SCALE RL
NO PRODUCTION MODEL RELEASE
NO CLAIM OF GENERAL SUPERIORITY OVER CURSOR/FABLE
NO SILENT HARDWARE-FLOOR INCREASE
```

Any model-weight acquisition, paid API use, rented compute, or bounded micro-adaptation must be explicitly authorized by the exact canonical task that performs it.

## Repository Authority

GitHub `main` is canonical. Branches, PRs, consultations, model outputs, and benchmark results are evidence candidates until merged through the governed workflow.
