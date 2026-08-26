# MSTR

MSTR is an independent research and engineering project for building an **extremely capable code-specialized software-engineering model and runtime that ordinary people can install and run locally on an ordinary laptop**.

The primary goal is not general chat breadth. MSTR is being optimized to take a software direction, understand the repository and constraints, build the requested change, verify it, recover from failures, and finish with working code.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC
```

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

## What MSTR Is Trying to Be Best At

MSTR is optimized for the software-building loop:

```text
DIRECTION
-> ORIENT
-> UNDERSTAND REPOSITORY + CONSTRAINTS
-> LOCALIZE
-> PLAN MINIMALLY
-> ACT
-> OBSERVE
-> VERIFY
-> RECOVER WHEN WRONG
-> VERIFIED DONE
```

The builder cannot make its own unverified `done` statement project truth. Successful completion is derived from independent verification.

General reasoning is preserved where it improves planning, implementation, debugging, verification, and safe execution. It is not the primary optimization target.

## Development Method

MSTR uses **Spec Kit / Spec-Driven Development**.

Start with:

1. `.specify/memory/constitution.md`
2. `docs/canonical/CURRENT_STATE.md`
3. `docs/canonical/PROGRAM_ROADMAP.md`
4. `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`
5. `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`
6. `specs/000-universal-laptop-interaction-contract/`
7. `specs/001-agent-harness-verified-loop-foundation/`
8. `docs/handoffs/MSTR-RESUME-AFTER-WEPLD.md`

MSTR workstreams use full Spec Kit packages: specification, clarification closeout, research, plan, data model/contracts, quickstart, implementation handoff, readiness checklist, evidence, and dependency-ordered tasks.

## Current State

Live `docs/canonical/CURRENT_STATE.md` is authoritative. At the time the MSTR-000A planning package was authored:

```text
MSTR-000 = ACTIVE
T000-T028 = COMPLETE_CANONICAL
T029 = ACTIVE/NEXT Q4 QUANTIZATION QUALIFICATION
FINAL_BACKBONE = UNSELECTED
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
```

The founder-directed sequence amendment preserves T029–T034, then requires MSTR-000A before any weight-changing agent training:

```text
T029 -> T030 -> T031 -> T032 -> T033 -> T034
                                      |
                                      v
                     MSTR-000A VERIFIED AGENT HARNESS
                                      |
                                      v
                  interaction/tournament/data preflight
                                      |
                                      v
                  separate explicit training authorization
```

## Agent Harness Strategy

MSTR co-designs model, harness, environments, verification, and training signal.

Required score surfaces remain separate:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

The default architecture is intentionally small:

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

Multi-agent/planner/checker designs are experimental arms that must earn their additional latency, tokens, RAM, and complexity.

MSTR-000A also establishes three bounded loops:

```text
BUILD LOOP        = direction -> verified completion
ENVIRONMENT LOOP  = checkout -> runnable/reproducible task environment
RESEARCH LOOP     = baseline -> bounded experiment -> keep/discard/crash
```

See `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md` and `specs/001-agent-harness-verified-loop-foundation/`.

## WePLD Integration

WePLD is the primary Half Moon orchestration partner for MSTR, but standalone MSTR must remain useful without WePLD.

MSTR exposes an evidence-derived capability profile; WePLD can use it to choose the smallest effective context, planning, verifier-cadence, and recovery recipe.

Results with WePLD are full-system results and must not be presented as raw model scores.

## Training Direction

MSTR's future training plan treats **Google Colab + Unsloth as the primary accessible execution path**, not as product dependencies:

```text
Google Colab = GPU execution environment
Unsloth     = preferred efficient training framework candidate
MSTR runtime = separate local/offline end-user product
```

The program does **not** preselect a final backbone or precision. Training must consume the frozen MSTR loop/tool/edit/state/verifier semantics rather than use an unrelated scaffold and hope the behavior transfers later.

The intended learning sequence is evidence-driven:

```text
strong code/FIM prior
-> verified execution-grounded trajectories
-> coding/repository/tool/edit/recovery SFT
-> preference/recovery training where justified
-> bounded executable agent RL where authorized
-> Q4 regression
-> same Direction-to-Done / neutral / MSTR / WePLD evaluation surfaces
```

Future code/FIM research should include ordinary FIM, instruction-aware FIM, function/dependency-aware FIM, cross-file/repository FIM, and an experimental action/observation continuation arm where evidence supports it.

Every later run must be resumable, pinned, hashed, and regression-tested. See `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

## Product Thesis

> **the smallest model that can reliably turn software direction into verified working code**

MSTR optimizes maximum verified software-engineering utility per GB, per second, per token/tool action, and per unit of training evidence.

Mandatory product metrics include:

```text
DVCR = Direction-to-Verified-Completion Rate
TTVC = Time to Verified Completion
FPAR = First-Pass Accept Rate
ESR  = Edit-Survival Rate
RSR  = Repair Success Rate
TER  = Tool Error Rate
```

Model quality, repository localization, deterministic editing, tool reliability, executable verification, local inference, quantization, context management, end-to-end TTVC, and failure recovery are designed together.

## Program Roadmap

```text
MSTR-000   Qualification Harness + Universal Laptop / Interaction / Backbone Qualification
MSTR-000A  Verified Agent Harness + Direction-to-Done Foundation
MSTR-001   Data Engine + Bounded Code/FIM Mid-Training
MSTR-002   Coding SFT + Repository / Tool / Planning / Recovery Behavior
MSTR-003   Environment Factory Expansion + Agentic RL
MSTR-004   Local Inference Speed Co-Design
MSTR-005   Packaging + Security + Privacy + Offline Release Engineering
MSTR-006   MSTR Gauntlet + Release Candidate Qualification
MSTR-007   MSTR v1 Release
MSTR-008   Post-Release Evidence + Improvement Loop
```

Later workstreams remain implementation-deferred until predecessor evidence is canonical.

## External-Effect Gates

```text
T028 = explicitly authorized/canonical candidate-weight acquisition path
T053_OR_SUCCESSOR = separately authorized bounded weight-changing adaptation gate
```

MSTR-000A does not authorize training, paid compute, large dataset ingestion, or production trace ingestion.

## Hard Boundaries

```text
NO FINAL BACKBONE SELECTION WITHOUT EVIDENCE
NO LONG TRAINING WITHOUT EXACT AUTHORITY
NO LARGE DATASET INGESTION WITHOUT EXACT AUTHORITY
NO LARGE-SCALE RL WITHOUT EXACT AUTHORITY
NO PRODUCTION MODEL RELEASE WITHOUT EXACT AUTHORITY
NO HARNESS GAIN REPORTED AS RAW MODEL GAIN
NO SILENT HARDWARE-FLOOR INCREASE
NO PRIVATE USER REPOSITORY TRAINING INGEST BY DEFAULT
NO HIDDEN TELEMETRY
```

GitHub `main` is canonical. Branches, PRs, consultations, model outputs, notebooks, and benchmark results are evidence candidates until merged through the governed workflow.
