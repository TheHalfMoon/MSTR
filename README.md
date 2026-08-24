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
- specification and independently testable user stories;
- clarification closeout;
- research decisions;
- technical implementation plan and Constitution Check;
- data model and machine-readable contracts;
- quickstart and implementation handoff;
- implementation-readiness checklist;
- dependency-ordered executable tasks with paths and external-effect gates.

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

MSTR-000 determines and implements the **qualification harness plus the model/runtime/distribution/interaction qualification program** before serious training compute is spent. It closes with the top backbone or top-two pilot decision and a bounded MSTR-001 data/mid-training proposal.

## Product Thesis

MSTR is not trying to win by parameter count alone.

The target is:

> **maximum verified software-engineering utility per GB, per second, and per unit of training evidence**

Model quality, repository localization, deterministic editing, tool reliability, executable verification, local inference, quantization, context management, and end-to-end TTVC are designed together.

## Program Roadmap

The program is split into gated Spec Kit workstreams:

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

The implementation details of later workstreams are intentionally deferred until predecessor evidence is canonical. See `docs/canonical/PROGRAM_ROADMAP.md`.

## First Executable Task After MSTR-000 Plan Approval

```text
T003 = BOOTSTRAP_QUALIFICATION_HARNESS
```

This is **not** a model-download or training task.

Within MSTR-000:

```text
T028 = first possible explicitly authorized candidate-weight acquisition
T053 = explicitly authorized bounded equivalent micro-adaptation only
```

No MSTR-000 task authorizes long training or large-scale RL.

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
