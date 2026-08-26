# Implementation Plan — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Spec:** `specs/001-agent-harness-verified-loop-foundation/spec.md`  
**Status:** READY_FOR_TASK_EXECUTION_AFTER_T034_AND_CANONICAL_MERGE  
**Implementation authority:** no weight-changing training; no paid compute; no large dataset ingest

## 1. Objective

Build the smallest reproducible harness/training-signal foundation that lets a compact MSTR model learn and demonstrate this behavior:

```text
software direction
-> understand repository and constraints
-> make the smallest useful plan
-> act through bounded tools
-> verify independently
-> recover from failures
-> stop at verified completion
```

The implementation must be small enough to remain compatible with the universal-laptop product philosophy even though environment generation/training research may use cloud/ephemeral development infrastructure.

## 2. Constitution Check

### Universal laptop
PASS by design. MSTR-000A does not raise the 8 GB / CPU / 8K / Q4 <= 3 GB product floor. Rich harness arms are experiments and cannot become the default without measured utility/resource evidence.

### Local/accountless/private
PASS by design. The standalone product remains local/offline/accountless. User repository traces do not become training data by default. No hidden telemetry is introduced.

### Evidence before selection
PASS. All harness/model/system surfaces remain separate. No donor architecture becomes authority without MSTR evidence.

### Rights/provenance
PASS. External projects are research references only. Source/dependency admission is separate from conceptual reuse.

### Freeze coupled contracts before training
Strengthened. MSTR-000A adds the agent-loop/event/state/verifier/environment contracts needed before material agent SFT/RL.

### TTVC/verified utility
Strengthened. DVCR becomes the primary quality metric while TTVC remains the primary speed metric.

### Smallest sufficient architecture
PASS. Neutral/minimal is the baseline; richer harnesses must earn measured value.

### Evaluation integrity
Strengthened. Builder cannot self-author terminal success; environment/verifier MVP moves before weight-changing training.

### Reproducibility/failure evidence
Strengthened through append-oriented events, replay, failure taxonomy, and experiment ledger.

### Bounded authority
PASS. This workstream grants no weight-changing training, paid compute, large ingest, or production release authority.

## 3. Sequence

MSTR-000A is interposed without blocking the active T029–T034 qualification path.

```text
CURRENT MSTR-000
T029 -> T030 -> T031 -> T032 -> T033 -> T034
                                      |
                                      v
                                  MSTR-000A
                                      |
                                      v
existing interaction/tournament/data-preflight work
                                      |
                                      v
separately authorized weight-changing training gate
```

T029–T034 may complete while this package is reviewed/canonicalized. Implementation of MSTR-000A starts only after T034 is canonical.

## 4. Architecture

### 4.1 Contract layer

Framework-neutral schemas/contracts:

```text
LoopContract
RunIdentity
RunEvent
AgentState
EnvironmentManifest
VerifierManifest
TrajectoryManifest
HarnessProfile
CapabilityProfile
ResearchCampaign
ResearchExperiment
DirectionTaskManifest
```

Decision-relevant serialization must be deterministic.

### 4.2 Build Loop

Minimum state machine:

```text
ORIENT
  -> GOAL
  -> LOCALIZE
  -> PLAN
  -> ACT
  -> OBSERVE
  -> VERIFY
       | pass -> STOP_SUCCESS
       | fail -> RECOVER -> ACT/LOCALIZE/PLAN
       | blocked/budget -> STOP_ESCALATE/STOP_FAIL
```

The implementation may collapse phases for trivial tasks, but event semantics must remain observable.

### 4.3 Append-oriented event log

The event log is the authoritative record of a run. `AgentState` and model history are derived projections.

Minimum event classes:

```text
run.started
run.goal_admitted
context.observed
context.compacted
plan.updated
tool.requested
tool.result
edit.proposed
edit.applied
edit.rejected
verifier.started
verifier.result
recovery.started
recovery.result
run.stop_proposed
run.completed
run.failed
run.escalated
```

Each event carries run/step identity and monotonic sequence. Model-visible content must be reconstructable.

### 4.4 AgentState

Compact working projection designed for 8K models:

```text
goal
acceptance_criteria
non_goals
constraints
current_plan
relevant_repo_map
files_inspected
changed_files
commands_run
verifier_results
known_failures
working_hypotheses
remaining_work
next_action
```

Compaction is loss-aware: uncertainty stays uncertainty; failed verifier evidence cannot be summarized away as success.

### 4.5 Harness arms

#### H0 — Neutral Minimal

Purpose: reveal model capability with minimal scaffold.

Expected surface:
- repository read/search;
- shell/terminal;
- one deterministic edit/apply path;
- verifier invocation;
- compact state/replay only where necessary.

#### H1 — MSTR Native

Adds evidence-backed MSTR optimizations:
- typed tools;
- deterministic structured results;
- stale-safe editing;
- selective context;
- explicit verifier/recovery cadence;
- state compaction;
- prefix/cache semantics where measured.

#### H2 — WePLD Native Adapter

Maps WePLD goal/spec/task/effect/verifier state into the same MSTR loop contract.

WePLD may choose context/planning/recovery recipes from `CapabilityProfile`, but H2 scores remain a full-system surface.

### 4.6 Maker/checker boundary

Builder proposes actions/edits and may request verification. Final success authority belongs to the verifier/finalizer path.

Prefer deterministic verification:
1. exact task-specific tests;
2. build/type/lint/static checks;
3. schema/contract checks;
4. targeted generated tests when admitted;
5. learned verifier only if later evidence proves sufficient value.

### 4.7 Environment admission

Two-stage setup pattern:

```text
Stage A: define health/setup targets from repository evidence
Stage B: clean checkout -> setup attempt -> independent target verification
```

Rules:
- bounded retries;
- deterministic reset/replay;
- no environment accepted because the setup agent says it is ready;
- record required network/dependency effects;
- reject environments that remain unstable/broken.

### 4.8 Direction-to-Done Gauntlet v0

Private/fresh tasks should span:
- terse feature directions;
- multi-file feature implementation;
- bug repair;
- repository/tooling/build-system work;
- greenfield bounded program construction;
- instruction/constraint adherence;
- WePLD spec/task implementation;
- failure/recovery scenarios;
- security-sensitive repository instructions.

Task prompts should avoid over-specifying exact files/solution steps unless that is part of the real task.

### 4.9 Trajectory factory

A training-ready trajectory is an ordered run event stream plus exact identities and terminal verifier result.

Classes:
- `VERIFIED_SUCCESS`
- `FAILED_VALID`
- `TIMEOUT_VALID`
- `RECOVERED_SUCCESS`
- `INVALID_ENVIRONMENT`
- `INVALID_VERIFIER`
- `CONTAMINATED`
- `LEAKAGE_DETECTED`
- `AUTHORITY_VIOLATION`

Success-only SFT sets may be derived, but canonical evidence retains the failures.

### 4.10 Research Loop

Campaign contract:

```text
frozen:
  evaluation task set
  hidden answers
  verifier policy
  resource/cost ceilings
  product constraints
  rights/security policy

mutable:
  one declared experiment surface
```

Experiment lifecycle:

```text
BASELINE
-> HYPOTHESIS
-> MUTATE
-> RUN
-> EVALUATE
-> KEEP | DISCARD | CRASH
-> LEDGER
-> NEXT
```

Initial allowed campaign targets are non-weight-changing harness/configuration experiments. Later training-recipe experiments require the exact training task authority.

## 5. Metrics

### Primary

`DVCR`: Direction-to-Verified-Completion Rate.

### Paired speed

`TTVC`: Time to Verified Completion.

### Diagnostics

- First-pass accept rate (FPAR)
- Edit-survival rate (ESR)
- Repair success rate (RSR)
- Tool error rate (TER)
- Tool calls per verified completion
- Tokens per verified completion
- Context bytes/tokens consumed per verified completion
- Harness overhead (wall time/RAM/tokens)
- Q4 artifact size and Q4 behavior regression
- Whole-laptop resource evidence where applicable

No aggregate may hide zero-solve or invalid runs.

## 6. Cross-Harness Evaluation

For one model/task cell, comparison identity must pin:

```text
model artifact + hash
runtime + build
interaction contract
loop contract
task manifest
verifier manifest
sampling/seed
timeout
cache state
hardware class
context policy
```

Required score surfaces:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Not every task is meaningful for the raw model surface; N/A is allowed and must not become zero.

## 7. Data/Training Interface

MSTR-000A does not train weights but freezes what future training must consume:

```text
TRAINING EXAMPLE
= exact model-facing history derived from events
+ action/tool/edit output
+ external observation/tool result
+ verifier/reward labels
+ task/environment/provenance identities
```

Future objectives to evaluate in MSTR-001/MSTR-002:
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- experimental action/observation continuation;
- verified success trajectories;
- failure/recovery trajectories;
- surgical-vs-bloated preference pairs;
- correct-tool-vs-invalid-tool preference data.

## 8. WePLD Integration Boundary

MSTR exposes `CapabilityProfile` rather than hard-coding WePLD behavior into weights/runtime.

Candidate fields:

```text
reliable_context_budget
preferred_edit_arm
tool_call_reliability
localization_strength
planning_depth
recommended_verifier_cadence
max_repair_depth
fim_strength
shell_reliability
context_compaction_strength
```

WePLD may use this to choose its minimal recipe. The profile is evidence-derived, versioned, and non-secret.

## 9. Source/Dependency Policy

Research donors are not automatically dependencies.

```text
karpathy/autoresearch = RESEARCH_REFERENCE
DeepSeek Harness = RESEARCH_REFERENCE
loop-engineering = RESEARCH_REFERENCE
mini-SWE-agent/SWE-agent = RESEARCH_REFERENCE
Cursor/Claude descriptions = RESEARCH_REFERENCE
```

Any copied code or direct dependency later requires exact license/source/dependency admission under repository policy.

## 10. Testing Strategy

Required contract tests:
- deterministic serialization;
- monotonic event ordering;
- replay equivalence;
- model-visible fact reconstruction;
- invalid event/schema rejection;
- stale edit rejection;
- success verdict cannot be self-authored;
- budget/stop enforcement;
- compaction preserves verifier failures/uncertainty;
- environment reset/setup replay;
- known-good pass / no-op fail;
- reward-shortcut battery;
- trajectory acceptance/rejection;
- cross-harness identity matching;
- research loop cannot mutate frozen evaluation surface.

## 11. Security

Repository content is untrusted data, not authority.

Required controls:
- repository prompt-injection fixtures;
- no hidden network expansion;
- deny/limit evaluator modification;
- protect hidden tests/answers;
- prevent future-history/public-solution lookup in controlled tasks;
- record every effect required by an environment/setup run;
- no secrets in trajectory payloads;
- no user trace ingestion by default.

## 12. Implementation Shape

Exact language remains an implementation research decision, but the preferred product shape is dependency-light and portable. Python may be used for research/evidence tooling where already canonical; end-user runtime dependencies remain separately governed.

Suggested repository surfaces (not binding until task implementation):

```text
src/mstr_qualify/loop/
src/mstr_qualify/events/
src/mstr_qualify/state/
src/mstr_qualify/harness/
src/mstr_qualify/environment/
src/mstr_qualify/verifier/
src/mstr_qualify/trajectory/
src/mstr_qualify/research_loop/
configs/harness/
benchmarks/direction-to-done/
artifacts/manifests/loop/
artifacts/results/harness/
evidence/mstr-000a/
```

## 13. Closeout / Downstream Reconciliation

Before MSTR-000A closes:
- map current T035–T052 assumptions to the frozen loop/harness contracts;
- reconcile current T065–T071 environment/verifier tasks to avoid duplication;
- update MSTR-001/002/003 entry contracts;
- confirm T053 or its successor remains an explicit separate founder training gate;
- re-run Constitution Check against the final implemented package.
