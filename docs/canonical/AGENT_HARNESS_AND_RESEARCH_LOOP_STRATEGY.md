# MSTR Agent Harness + Research Loop Strategy

**Status:** FOUNDER-DIRECTED_SEQUENCE_AMENDMENT / becomes canonical only when merged  
**Date:** 2026-08-26  
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

## Mandatory Sequence Amendment

T029–T034 continue exactly as already authorized/planned.

After T034:

```text
T034 COMPLETE_CANONICAL
        ↓
MSTR-000A VERIFIED AGENT HARNESS + DIRECTION-TO-DONE FOUNDATION
        ↓
final interaction/tournament/data-recipe reconciliation
        ↓
SEPARATE EXPLICIT WEIGHT-CHANGING TRAINING GATE
```

Therefore:

```text
T029-T034 = CONTINUE
T035+ = MAY NOT BYPASS MSTR-000A CLOSEOUT
T053_OR_EQUIVALENT_WEIGHT_CHANGE = BLOCKED_UNTIL_MSTR-000A_CLOSEOUT + SEPARATE_FOUNDER_AUTHORIZATION
```

The implementation package is:

`specs/001-agent-harness-verified-loop-foundation/`

## Three Required Loops

### MSTR Build Loop

```text
DIRECTION
-> ORIENT
-> GOAL
-> LOCALIZE
-> PLAN
-> ACT
-> OBSERVE
-> VERIFY
-> RECOVER when needed
-> VERIFIED STOP
```

The builder may propose stop. It cannot create canonical success without independent verifier evidence.

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
-> KEEP | DISCARD | CRASH
-> REPEAT
```

Evaluation, hidden answers, verifier policy, budget, rights, security, and product constraints remain frozen during a campaign.

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
WePLD creates/structures better executable work
        ↓
MSTR receives higher-signal software trajectories
        ↓
MSTR becomes a better small builder
        ↓
better MSTR improves WePLD execution
        ↓
prior MSTR versions help bootstrap future environments/research
```

## Training Consequence

Future training should increasingly follow:

```text
strong code/FIM prior
+
verified agent loop
+
runnable environments
+
independent verifiers
+
execution-grounded SFT/recovery data
+
bounded agent RL
```

Future MSTR-001 research must include measured arms for:
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- action/observation continuation as an experimental arm only.

Future MSTR-002 must consume verified trajectories from the same loop semantics used for evaluation/serving.

Future MSTR-003 must use admitted executable environments and reward-shortcut-resistant verifiers.

## Primary Metrics

```text
DVCR = Direction-to-Verified-Completion Rate
TTVC = Time to Verified Completion
FPAR = First-Pass Accept Rate
ESR  = Edit-Survival Rate
RSR  = Repair Success Rate
TER  = Tool Error Rate
```

Also report tokens/tool calls/context consumed per verified completion and harness overhead.

## Research Sources

Full synthesis and source list:
`specs/001-agent-harness-verified-loop-foundation/research.md`

Key external references include:
- Karpathy autoresearch
- DeepSeek Harness architecture
- Cursor Composer / Composer 2 / Composer 2.5, Autoinstall, real-time RL
- Claude Loops
- Loop Engineering
- SWE-agent / mini-SWE-agent
- SWE-Gym and executable-environment research
- function-/instruction-aware FIM research
- selective repository retrieval research

These are research donors. None is automatically a product dependency.

## Authority

This document does not itself authorize:

```text
WEIGHT_CHANGING_TRAINING
PAID_COMPUTE
PAID_MODEL_API
LARGE_DATASET_INGESTION
LARGE_SCALE_RL
PRODUCTION_RELEASE
PRODUCTION_TRACE_INGESTION
```

Those remain subject to exact downstream task/founder gates.
