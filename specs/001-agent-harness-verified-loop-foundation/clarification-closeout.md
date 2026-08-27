# Clarification Closeout — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Status:** CLOSED_FOR_PLANNING / sequence amended by MSTR-000B convergence model  
**Date:** 2026-08-27

## Founder Decisions Frozen by This Package

### C-001 — What is MSTR optimizing for?

MSTR is a code-specialized builder, not a general-purpose assistant.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION -> VERIFIED_WORKING_CODE
PRIMARY_QUALITY = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED = TTVC
```

General capabilities are guardrails/replay only when they support software engineering.

### C-002 — Is the harness part of the product or only evaluation infrastructure?

Both, but with explicit score separation.

- MSTR must remain usable with a neutral minimal harness.
- MSTR may ship with an optimized native harness.
- WePLD is a privileged Half Moon integration target, not a mandatory MSTR dependency.
- Raw model, neutral harness, MSTR-native and WePLD full-system scores remain separate.

### C-003 — When may MSTR-000A execute relative to candidate qualification and training?

The original blanket `after T034` entry interpretation is superseded by exact dependencies.

```text
A001-A018 = EARLY_SAFE
```

They may proceed when their exact prerequisites are satisfied, the work is model-independent, and no unqualified candidate result or unauthorized external effect is consumed.

```text
A019-A024 = CONVERGENCE_GATED
```

They require equivalent/stable candidate qualification and the MSTR-000B candidate/verifier/research prerequisites named in canonical tasks.

All required harness/environment/data/verifier convergence must exist before any weight-changing agent adaptation. T053 or a canonical successor remains a separate founder gate.

### C-004 — What is the default agent topology?

Single builder model + deterministic/independent verification.

```text
DEFAULT_MULTI_AGENT = NO
DEFAULT_MODEL_INSTANCES = 1
INDEPENDENT_VERIFIER = REQUIRED_FOR_SUCCESS
```

Planner/checker/subagent arms are optional experiments only when measured value exceeds cost.

### C-005 — Does MSTR copy DeepSeek Harness / Cursor / Loop Engineering?

No.

They are research donors. MSTR adopts evidence-backed concepts behind its own small, portable contracts. No donor becomes a runtime dependency without separate source/dependency admission.

### C-006 — What is the minimum Build Loop?

The Build Loop is a bounded state graph with conceptual states:

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

It is not a mandatory linear ritual. Trivial tasks may fast-path unnecessary planning/localization states, but successful STOP always requires verifier evidence.

### C-007 — What is persistent state?

The append-oriented event log is authoritative. `AgentState` is a reproducible projection/compact working state, not an independent truth database.

### C-008 — What is allowed to become training data?

Only explicitly admitted trajectories with provenance and verifier identity/health satisfying downstream admission policy. User repositories and production traces are excluded by default. Future opt-in trace learning requires separate policy.

### C-009 — How is environment bootstrapping handled?

A bounded two-role pattern is preferred:

1. goal/setup-definition stage identifies reproducible health targets;
2. setup executor starts from a clean checkout and attempts the setup;
3. an independent verifier checks selected target commands;
4. repeated failure beyond the attempt ceiling rejects the environment.

This is inspired by Cursor Autoinstall but is not tied to Cursor infrastructure.

### C-010 — What is the role of autoresearch?

MSTR will have a bounded research loop inspired by Karpathy autoresearch:

```text
baseline -> hypothesis -> bounded mutation -> run -> measure -> keep/discard/crash/invalid
```

MSTR-000B adds a multi-fidelity promotion ladder so weak ideas are discarded before expensive Direction-to-Done/Q4 evaluation. Evaluation authority, hidden answers, verifier rules, budget, rights, security, contamination, and product constraints remain immutable during a campaign.

### C-011 — What is the role of retrieval/context?

Selective retrieval. `NO_RETRIEVAL` is a valid action. The model/harness starts from the smallest useful slice and expands only when evidence requires it. MSTR-000B may add typed context intents through the frozen interaction contract.

### C-012 — What is the target evaluation style?

Direction-to-Done tasks include terse directions, multi-file construction, feature work, bounded greenfield work, repair, build-system/environment work, repeated repository maintenance, and WePLD-spec-driven tasks. Public benchmarks support continuity but do not control release/training decisions.

### C-013 — Does this package authorize training or new model access?

No.

```text
NEW_MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_MSTR_000A
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
T053_OR_SUCCESSOR = SEPARATE_FOUNDER_GATE
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
```

### C-014 — What happens to existing T065-T071 environment/verifier tasks?

They must be reconciled before MSTR-000A closes. MSTR-000A owns the pre-training MVP; MSTR-000B adds verifier-health/training-signal requirements. Existing later tasks may become expansion/hardening tasks, be partially consumed, or be superseded; duplication is prohibited.

### C-015 — What does MSTR-000B own relative to this package?

MSTR-000A owns model-visible loop/harness/event/state/environment/verifier/trajectory behavior. MSTR-000B owns product-aligned backbone rescan, machine task gates, Data Constitution, software-evolution/self-alignment/frontier curriculum, verifier health, test/feature curriculum, research-fidelity promotion and Q4/method preflight. Convergence consumes both.

## No Remaining Planning Ambiguities

The following do not block Spec Kit planning and are deliberately left to evidence:

- exact implementation language of the lightweight harness;
- exact neutral harness tool set;
- exact context-compaction algorithm;
- exact verifier mix per task class;
- whether a learned verifier ever earns a place;
- exact environment isolation runtime;
- exact training framework/method after current documentation and selected backbone are revalidated;
- exact public benchmark continuity set at release time.

These are research/implementation decisions, not founder intent gaps.
