# MSTR Agent Harness + Research Loop Strategy

**Status:** CANONICAL STRATEGY / amended by MSTR-000B planning when merged  
**Date:** 2026-08-27  
**Purpose:** Make MSTR the smallest exceptional code-specialized builder: direction -> verified working software.

## Mission

```text
MSTR_IS_GENERAL_PURPOSE = NO_AS_PRIMARY_OPTIMIZATION_TARGET
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DVCR
PRIMARY_SPEED_METRIC = TTVC
```

MSTR should win because it builds software unusually well for its size, not because it is a broad assistant that happens to code.

## Product Boundary Unchanged

```text
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8K
CPU_ONLY_BASIC_OPERATION = REQUIRED
DISCRETE_GPU_REQUIRED = NO
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
OFFLINE_AFTER_ACQUISITION = REQUIRED
ACCOUNT_OR_API_KEY_REQUIRED = NO
TELEMETRY_DEFAULT = OFF
WINDOWS + LINUX + MACOS = REQUIRED
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Corrected Pre-Training Sequence

The old blanket statement that all MSTR-000A work starts only after T034 is superseded by exact dependencies. MSTR-000 T030-T034 is one parallel qualification branch; it gates candidate-dependent convergence, **not** all early-safe A/B work.

```text
+--------------------------+   +--------------------------+   +--------------------------+
| MSTR-000                 |   | MSTR-000A EARLY_SAFE    |   | MSTR-000B EARLY_SAFE    |
| T030-T034 candidate/Q4   |   | A001-A018 loop/event/   |   | task gates / backbone   |
| runtime qualification    |   | state/env/verifier/traj |   | metadata/data/contracts |
+------------+-------------+   +------------+-------------+   +------------+-------------+
             |                              |                              |
             +------------------------------+------------------------------+
                                            |
                                            v
                    STABLE/EQUIVALENT PRODUCT-ALIGNED CANDIDATE POOL
                    + REQUIRED LOOP/VERIFIER/DATA/RESEARCH CONTRACTS
                                            |
                                            v
                                A019-A024 CONVERGENCE
                                            |
                                            v
                     SEPARATE EXPLICIT WEIGHT-CHANGING TRAINING GATE
```

Therefore:

```text
A001-A018 = EARLY_SAFE WHEN EXACT PREREQUISITES HOLD
MSTR-000B_EARLY_SAFE = MAY_PROCEED WHEN EXACT PREREQUISITES HOLD
T030-T034 = REQUIRED FOR CANDIDATE-DEPENDENT CONVERGENCE, NOT GLOBAL EARLY-SAFE ENTRY
A019-A024 = CONVERGENCE_GATED
MSTR_000B_REQUIRED_OUTPUTS = MUST_NOT_BE_BYPASSED
WEIGHT_CHANGING_TRAINING = SEPARATELY_GATED
```

Packages:
- `specs/001-agent-harness-verified-loop-foundation/`
- `specs/002-code-model-supremacy-foundation/`

## Three Required Loops

### MSTR Build Loop

The Build Loop is a bounded state graph, not a ritual linear chain.

Conceptual states:

```text
ORIENT
GOAL
LOCALIZE
PLAN
ACT
OBSERVE
VERIFY
RECOVER
STOP
```

A trivial task may use:

```text
GOAL -> ACT -> VERIFY -> STOP
```

A difficult task may revisit localization/planning/recovery. The builder may propose stop. It cannot create canonical success without independent verifier evidence.

### MSTR Environment Loop

```text
CHECKOUT
-> DEFINE HEALTH TARGETS
-> SETUP
-> RESET/REPLAY
-> INDEPENDENT VERIFY
-> ADMIT OR REJECT ENVIRONMENT
```

Broken environments do not become training signal merely because a model can spend tokens repairing setup.

### MSTR Research Loop

```text
BASELINE
-> HYPOTHESIS
-> BOUNDED MUTATION
-> RUN
-> EVALUATE
-> KEEP | DISCARD | CRASH | INVALID
-> REPEAT
```

MSTR-000B adds a multi-fidelity promotion ladder:

```text
L0 contract/smoke
-> L1 code/FIM/edit/tool
-> L2 executable repo
-> L3 Direction-to-Done/feature/program
-> L4 Q4 universal-laptop
```

Evaluation, hidden answers, verifier authority, budget, rights, security, contamination and product constraints remain frozen during a campaign.

## Harness Surfaces

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Never attribute harness-only gain to model weights.

Default runtime topology:

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

Subagents/planner/checker models are optional measured arms, never free default complexity.

## WePLD Role

WePLD is the primary Half Moon orchestration partner for MSTR but is not required for standalone use.

MSTR exposes an evidence-derived `CapabilityProfile`; WePLD uses it to choose the smallest sufficient context/planning/verifier/recovery recipe.

The target flywheel is:

```text
WePLD structures better executable work
        ↓
MSTR receives higher-signal software trajectories
        ↓
MSTR becomes a better small builder
        ↓
better MSTR improves WePLD execution
        ↓
prior MSTR versions help bootstrap future environments/research/data calibration
```

WePLD full-system results remain distinct from raw model results.

## Training Consequence

Future training should increasingly follow:

```text
product-aligned code foundation
+
strong code/FIM prior
+
verified agent loop
+
runnable environments
+
independent healthy verifiers
+
software-evolution + self-aligned data
+
checkpoint-relative frontier curriculum
+
execution-grounded SFT/recovery data
+
bounded agent RL
+
export + integrity + Q4 product regression
```

A material weight-changing checkpoint may become the parent of a later material stage only after its merged-master and canonical-Q4 artifacts are identity-bound, integrity-verified, and pass the required Q4 promotion gate.

MSTR-000B owns data/curriculum/verifier-health prerequisites before weight-changing training.

Future MSTR-001 research must include measured arms for:
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- test-aware/diff-aware FIM where specified;
- action/observation continuation as an experimental arm only.

Future MSTR-002 must consume verified trajectories from the same loop semantics used for evaluation/serving and include tester/reviewer behavior, feature/greenfield work and failure recovery.

Future MSTR-003 must use admitted executable environments, checkpoint-relative difficulty and reward-shortcut-resistant/health-qualified verifiers.

## Selective Context

MSTR should learn what context is missing rather than blindly retrieve.

Where the frozen interaction contract supports them, context intents include:

```text
NO_RETRIEVAL
NEED_FILE
NEED_SYMBOL
NEED_HISTORY
NEED_TEST
NEED_CONFIG
NO_MORE_CONTEXT
```

The 8K product prioritizes compact AgentState, recent relevant evidence and the smallest sufficient repository slice.

## Adaptive Test-Time Compute

Default to one bounded attempt. Spend additional compute only when verifier evidence/uncertainty justifies it.

```text
attempt
-> verify
-> targeted repair
-> optional small bounded branch/best-of-K if measured expected value exceeds cost
```

Report marginal DVCR gain against extra TTVC/tokens/tool calls.

## Primary Metrics

```text
DVCR = Direction-to-Verified-Completion Rate
TTVC = Time to Verified Completion
FPAR = First-Pass Accept Rate
ESR  = Edit-Survival Rate
RSR  = Repair Success Rate
TER  = Tool Error Rate
RHD  = Repository Health Delta
```

Also report tokens/tool calls/context consumed per verified completion, harness overhead and artifact/laptop resource cost.

## Research Sources

MSTR-000A synthesis:
`specs/001-agent-harness-verified-loop-foundation/research.md`

MSTR-000B synthesis:
`specs/002-code-model-supremacy-foundation/research.md`

Research references are donors/evidence only. No source code, dependency, dataset, model, teacher/API or license enters MSTR authority by citation alone.

## Authority

These strategies do not themselves authorize:

```text
NEW_MODEL_WEIGHT_ACCESS
WEIGHT_CHANGING_TRAINING
PAID_COMPUTE
PAID_MODEL_API
LARGE_DATASET_INGESTION
LARGE_SCALE_RL
PRODUCTION_RELEASE
PRODUCTION_TRACE_INGESTION
```

Those remain subject to exact downstream tasks and founder gates.
