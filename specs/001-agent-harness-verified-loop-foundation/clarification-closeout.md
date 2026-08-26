# Clarification Closeout — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Status:** CLOSED_FOR_PLANNING  
**Date:** 2026-08-26

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
- Raw model, neutral harness, and full MSTR/WePLD system scores remain separate.

### C-003 — When must the harness/environment foundation exist relative to training?

Before weight-changing agent adaptation.

T029–T034 continue immediately. After T034, MSTR-000A is mandatory before T053 or any equivalent weight-changing training gate.

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

```text
ORIENT -> GOAL -> LOCALIZE -> PLAN -> ACT -> OBSERVE -> VERIFY
                                            ^              |
                                            |----RECOVER---|
                                                    |
                                                   STOP
```

Trivial tasks may fast-path PLAN, but successful STOP always requires verifier evidence.

### C-007 — What is persistent state?

The append-oriented event log is authoritative. `AgentState` is a reproducible projection/compact working state, not an independent truth database.

### C-008 — What is allowed to become training data?

Only explicitly admitted trajectories with provenance and verifier identity. User repositories and production traces are excluded by default. Future opt-in trace learning requires separate policy.

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
baseline -> hypothesis -> bounded mutation -> run -> measure -> keep/discard/crash
```

The evaluation harness, hidden answers, verifier rules, budget, rights, security, and product constraints remain immutable during a campaign.

### C-011 — What is the role of retrieval/context?

Selective retrieval. `NO_RETRIEVAL` is a valid action. The model/harness starts from the smallest useful slice and expands only when evidence requires it.

### C-012 — What is the target evaluation style?

Direction-to-Done tasks include terse directions, multi-file construction, feature work, repair, build-system/environment work, and WePLD-spec-driven tasks. Public benchmarks support continuity but do not control release/training decisions.

### C-013 — Does this package authorize training?

No.

```text
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
T053 = SEPARATE_FOUNDER_GATE
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
```

### C-014 — What happens to existing T065–T071 environment/verifier tasks?

They must be reconciled before MSTR-000A closes. MSTR-000A owns the pre-training MVP. Existing later tasks may become expansion/hardening tasks, be partially consumed, or be superseded; duplication is prohibited.

## No Remaining Planning Ambiguities

The following do not block Spec Kit planning and are deliberately left to evidence:

- exact implementation language of the lightweight harness;
- exact neutral harness tool set;
- exact context-compaction algorithm;
- exact verifier mix per task class;
- whether a learned verifier ever earns a place;
- exact environment isolation runtime;
- exact training framework after T052 revalidation;
- exact public benchmark continuity set at release time.

These are research/implementation decisions, not founder intent gaps.
