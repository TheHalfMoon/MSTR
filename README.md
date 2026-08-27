# MSTR

MSTR is an independent research and engineering project for building an **extremely capable code-specialized software-engineering model and runtime that ordinary people can install and run locally on an ordinary laptop**.

The primary goal is not general chat breadth. MSTR is optimized to take a software direction, understand the repository and constraints, build the requested change, verify it, recover from failures, and finish with working code.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC
PRIMARY_EFFICIENCY_TARGET = VERIFIED_SOFTWARE_CAPABILITY_PER_GB
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

## What MSTR Is Trying to Be Best At

```text
DIRECTION
-> UNDERSTAND REPOSITORY + CONSTRAINTS
-> LOCALIZE
-> PLAN ONLY AS MUCH AS NEEDED
-> ACT
-> TEST / VERIFY
-> RECOVER WHEN WRONG
-> VERIFIED DONE
```

The builder cannot make its own unverified `done` statement project truth. Successful completion is derived from independent verification.

General reasoning is preserved where it improves software planning, implementation, debugging, verification, and safe execution. It is not the primary optimization target.

## Code Model Supremacy Thesis

MSTR does not try to beat larger models by imitating their scale. It concentrates model capacity and training signal on software building.

```text
CODE-SPECIALIZED FOUNDATION
× CODE/SOFTWARE CONTINUED TRAINING
× SOFTWARE-EVOLUTION DATA
× EXECUTION-FILTERED STUDENT SELF-ALIGNMENT
× STUDENT-FRONTIER CURRICULUM
× HEALTHY VERIFIERS
× TRAIN/SERVE HARNESS CONSISTENCY
× Q4 PRODUCT REGRESSION
```

The durable Half Moon advantage is intended to be the combined system of model weights, data/evolution factory, verifier health, Direction-to-Done evaluation, MSTR harness, bounded autoresearch, and WePLD integration.

## Development Method

MSTR uses **Spec Kit / Spec-Driven Development**.

Start with:

1. `.specify/memory/constitution.md`
2. `docs/canonical/CURRENT_STATE.md`
3. `docs/canonical/PROGRAM_ROADMAP.md`
4. `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`
5. `docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md`
6. `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`
7. the exact active Spec Kit package(s)

Current pre-training foundation packages:

```text
specs/001-agent-harness-verified-loop-foundation/
specs/002-code-model-supremacy-foundation/
```

## Pre-Training Architecture

MSTR co-designs model, harness, environments, verification, data, curriculum and deployment.

The early foundations are parallel when their exact prerequisites hold. MSTR-000 T030-T034 gates candidate-dependent convergence only; it does not globally gate model-independent A/B work.

```text
+--------------------------+   +--------------------------+   +--------------------------+
| MSTR-000                 |   | MSTR-000A EARLY_SAFE    |   | MSTR-000B EARLY_SAFE    |
| T030-T034 candidate/Q4   |   | A001-A018 loop/harness  |   | task gates / metadata / |
| runtime qualification    |   | env/verifier/trajectory |   | data/curriculum contracts|
+------------+-------------+   +------------+-------------+   +------------+-------------+
             |                              |                              |
             +------------------------------+------------------------------+
                                            |
                                            v
                    STABLE / EQUIVALENT PRODUCT-ALIGNED CANDIDATE POOL
                    + REQUIRED LOOP / VERIFIER / DATA / RESEARCH CONTRACTS
                                            |
                                            v
                               A019-A024 / B-CONVERGENCE
                                            |
                                            v
                              SEPARATE EXPLICIT TRAINING GATE
```

Candidate-dependent tournament/training convergence is explicitly gated; model-independent early work is not.

## Agent Harness Strategy

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

Multi-agent/planner/checker designs are optional measured arms, not default laptop complexity.

MSTR uses three bounded loops:

```text
BUILD LOOP        = direction -> verified completion
ENVIRONMENT LOOP  = checkout -> runnable/reproducible task environment
RESEARCH LOOP     = baseline -> bounded experiment -> keep/discard/crash
```

## MSTR-000B: What It Adds Before Training

MSTR-000B makes the plan materially stronger by requiring:

- machine task/dependency eligibility enforcement;
- a new mission-aligned compact-backbone rescan that includes code-specialized bases;
- tokenizer/code-density economics for the 8K product;
- a Data Constitution;
- software-evolution records;
- execution-filtered student self-alignment;
- bounded teacher rescue under rights/verifier gates;
- checkpoint-relative difficulty/frontier curriculum;
- verifier-health records;
- test-generation curriculum;
- feature/greenfield curriculum;
- multi-fidelity autoresearch promotion;
- adaptive test-time compute/selective context;
- fail-closed Q4-in-the-loop checkpoint promotion;
- equivalent LoRA/rsLoRA/QLoRA method preflight where supported;
- Repository Health Delta over repeated work;
- cross-harness robustness.

`JetBrains/Mellum-4b-base` is a mandatory rescan candidate because it demonstrates a gap in the older search policy; it is not preselected as a winner or authorized for weight access.

## WePLD Integration

WePLD is the primary Half Moon orchestration partner for MSTR, but standalone MSTR must remain useful without WePLD.

MSTR exposes an evidence-derived capability profile; WePLD can use it to choose the smallest effective context, planning, verifier-cadence, and recovery recipe.

Results with WePLD are full-system results and must not be presented as raw model scores.

## Training Direction

MSTR's future training plan treats **Google Colab + Unsloth as the primary accessible execution path**, not as product dependencies:

```text
Google Colab = GPU execution environment
Unsloth = preferred efficient training framework candidate
MSTR runtime = separate local/offline end-user product
```

The training sequence is evidence-driven:

```text
strong product-aligned code prior
-> code/FIM continued training
-> execution-filtered self-alignment
-> software-evolution + Direction-to-Done SFT
-> failure/recovery/preference training
-> bounded executable RL
-> export + integrity + Q4 regression after each material stage
-> only Q4-qualified checkpoint may parent the next material stage
```

Training method is not preselected. Where supported, equivalent 16-bit LoRA, 16-bit LoRA+rsLoRA, 4-bit QLoRA, and 4-bit QLoRA+rsLoRA cells must be compared before committing to a method; every unsupported arm requires an exact recorded reason. Full fine-tuning is non-default.

## Product Metrics

```text
DVCR = Direction-to-Verified-Completion Rate
TTVC = Time to Verified Completion
FPAR = First-Pass Accept Rate
ESR  = Edit-Survival Rate
RSR  = Repair Success Rate
TER  = Tool Error Rate
RHD  = Repository Health Delta
```

MSTR also tracks tokens/tool calls/context consumed per verified completion, artifact size, RAM/whole-laptop pressure, and harness overhead.

## Program Roadmap

```text
MSTR-000   Qualification Harness + Universal Laptop / Interaction / Backbone Qualification
MSTR-000A  Verified Agent Harness + Direction-to-Done Foundation
MSTR-000B  Code Model Supremacy Pre-Training Foundation
MSTR-001   Data Engine + Code/FIM Continued/Mid-Training
MSTR-002   Execution-Grounded Coding SFT + Recovery
MSTR-003   Environment Factory Expansion + Agentic RL
MSTR-004   Local Inference Speed Co-Design
MSTR-005   Packaging + Security + Privacy + Offline Release Engineering
MSTR-006   MSTR Gauntlet + Release Candidate Qualification
MSTR-007   MSTR v1 Release
MSTR-008   Post-Release Evidence + Improvement Loop
```

## Hard Boundaries

```text
NO FINAL BACKBONE SELECTION WITHOUT EVIDENCE
NO NEW MODEL WEIGHT ACCESS WITHOUT EXACT AUTHORITY
NO WEIGHT-CHANGING TRAINING WITHOUT EXACT AUTHORITY
NO LONG TRAINING WITHOUT EXACT AUTHORITY
NO LARGE DATASET INGESTION WITHOUT EXACT AUTHORITY
NO LARGE-SCALE RL WITHOUT EXACT AUTHORITY
NO PRODUCTION MODEL RELEASE WITHOUT EXACT AUTHORITY
NO HARNESS GAIN REPORTED AS RAW MODEL GAIN
NO TEACHER OUTPUT TREATED AS VERIFIED TRUTH
NO WEAK/BROKEN VERIFIER USED AS CLEAN TRAINING AUTHORITY
NO MASTER-ONLY CHECKPOINT PROMOTED PAST REQUIRED Q4 GATE
NO SILENT HARDWARE-FLOOR INCREASE
NO PRIVATE USER REPOSITORY TRAINING INGEST BY DEFAULT
NO HIDDEN TELEMETRY
```

GitHub `main` is canonical. Branches, PRs, consultations, model outputs, notebooks, and benchmark results are evidence candidates until merged through the governed workflow.
