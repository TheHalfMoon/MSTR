# Implementation Plan — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Spec:** `specs/001-agent-harness-verified-loop-foundation/spec.md`  
**Status:** ACTIVE_FOUNDATION / EARLY_SAFE_TASKS_MAY_EXECUTE / CONVERGENCE_GATED_BY_MSTR_000B  
**Implementation authority:** no new model weight access; no weight-changing training; no paid compute; no large dataset ingest

## 1. Objective

Build the smallest reproducible harness/training-signal foundation that lets a compact MSTR model learn and demonstrate this behavior:

```text
software direction
-> understand repository and constraints
-> use only the context/planning the task needs
-> act through bounded tools
-> verify independently
-> recover from failures
-> stop at verified completion
```

The implementation remains compatible with the universal-laptop product philosophy even though environment generation/training research may later use separately authorized cloud/ephemeral infrastructure.

## 2. Constitution Check

### Universal laptop
PASS by design. MSTR-000A does not raise the 8 GB / CPU / 8K / Q4 <= 3 GB product floor. Rich harness arms are experiments and cannot become the default without measured utility/resource evidence.

### Local/accountless/private
PASS by design. Standalone MSTR remains local/offline/accountless. User repository traces do not become training data by default. No hidden telemetry is introduced.

### Evidence before selection
PASS. Raw/neutral/MSTR/WePLD surfaces remain separate. No donor architecture becomes authority without MSTR evidence. Candidate-dependent convergence consumes the MSTR-000B stable product-aligned pool.

### Rights/provenance
PASS. External projects are research references only. Source/dependency/model/data/teacher admission is separate from conceptual reuse.

### Freeze coupled contracts before training
Strengthened. MSTR-000A freezes agent-loop/event/state/verifier/environment contracts; MSTR-000B adds data/curriculum/verifier-health/Q4 requirements before weight changes.

### TTVC/verified utility
Strengthened. DVCR is primary quality metric while TTVC remains primary speed metric.

### Smallest sufficient architecture
PASS. Neutral/minimal is the baseline; richer harnesses must earn measured value.

### Evaluation integrity
Strengthened. Builder cannot self-author terminal success; environment/verifier MVP and verifier-health requirements precede clean training admission.

### Reproducibility/failure evidence
Strengthened through append-oriented events, replay, failure taxonomy, exact identities and experiment ledger.

### Bounded authority
PASS. This workstream grants no new model weight access, weight-changing training, paid compute, large ingest, or production release authority.

## 3. Corrected Sequence

The old all-or-nothing `T034 -> MSTR-000A` sequence is superseded by exact dependencies. MSTR-000 T030-T034 is a parallel candidate/runtime branch and gates convergence, not the early-safe foundation globally.

```text
+--------------------------+   +--------------------------+   +--------------------------+
| MSTR-000                 |   | MSTR-000A EARLY_SAFE    |   | MSTR-000B EARLY_SAFE    |
| T030-T034 candidate/Q4   |   | A001-A018 loop/event/   |   | governance / metadata /|
| runtime qualification    |   | state/env/verifier/traj |   | data/curriculum contracts|
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

Rules:
- A001-A018 may proceed when exact task prerequisites hold and no unqualified candidate/external authority is consumed.
- A019-A024 wait for the exact stable-candidate/verifier-health/research-ladder requirements defined in `tasks.md` and MSTR-000B.
- Existing T030-T034 work is not reopened by MSTR-000A.
- Before B002 is canonical, manually enforce exact prerequisites; there is no validator command to satisfy yet.
- Once B002 is `COMPLETE_CANONICAL`, any material B-task governed by B002 requires exact-main `eligible=true` before execution and again before merge; ineligible/error is fail-closed.

## 4. Architecture

### 4.1 Contract layer

Framework-neutral contracts include:

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

MSTR-000B adds Data Constitution, software-evolution, verifier-health, difficulty/frontier, candidate-pool, exact material-result identity, Q4-promotion, and research-fidelity contracts. Decision-relevant serialization must be deterministic.

### 4.2 Build Loop

`MSTR-BUILD-LOOP-v0` is a bounded state graph:

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

The loop may skip unnecessary states. A trivial task can follow `GOAL -> ACT -> VERIFY -> STOP`; difficult tasks may revisit localization/planning/recovery. Event semantics remain observable. The model may propose stop, never author canonical success.

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

Events carry run/step identity, monotonic sequence and canonical integrity fields. Model-visible content must be reconstructable.

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
- selective context and explicit no-retrieval behavior;
- verifier/recovery cadence;
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
5. learned verifier only if later evidence proves enough value.

MSTR-000B verifier-health state determines whether a verifier is strong enough to create clean training/evaluation labels.

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
- reject unstable/broken environments.

### 4.8 Direction-to-Done Gauntlet v0

Private/fresh tasks span:
- terse feature directions;
- multi-file feature implementation;
- bug repair;
- repository/tooling/build-system work;
- bounded greenfield program construction;
- instruction/constraint adherence;
- WePLD spec/task implementation;
- failure/recovery scenarios;
- security-sensitive repository instructions.

MSTR-000B expands feature/greenfield/test-generation/repeated-repository-health requirements before headline convergence.

### 4.9 Trajectory factory

A training-ready trajectory is an ordered run-event stream plus exact identities, verifier-health state and terminal verifier result.

Classes include:
- `VERIFIED_SUCCESS`
- `FAILED_VALID`
- `TIMEOUT_VALID`
- `RECOVERED_SUCCESS`
- `INVALID_ENVIRONMENT`
- `INVALID_VERIFIER`
- `CONTAMINATED`
- `LEAKAGE_DETECTED`
- `AUTHORITY_VIOLATION`

Canonical evidence retains failures. Clean positive SFT requires independent verification plus downstream admission policy.

### 4.10 Research Loop

Campaign contract freezes:

```text
evaluation task set
hidden answers
verifier policy + health threshold
resource/cost ceilings
product constraints
rights/security/contamination policy
```

One declared experimental surface changes at a time where possible.

Lifecycle:

```text
BASELINE
-> HYPOTHESIS
-> MUTATE
-> RUN
-> EVALUATE
-> KEEP | DISCARD | CRASH | INVALID
-> LEDGER
-> NEXT
```

MSTR-000B supplies the multi-fidelity promotion ladder L0-L4. Initial campaigns are non-weight-changing; training-recipe experiments require exact training authority.

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
- Tool calls/tokens/context per verified completion
- Harness overhead
- Q4 artifact size/regression
- Whole-laptop resource evidence where applicable
- Repository Health Delta for long-horizon/multi-round claims after MSTR-000B defines it

No aggregate may hide zero-solve or invalid runs.

## 6. Cross-Harness Evaluation

Comparison identity pins:

```text
model artifact + hash
runtime + build
interaction contract
loop contract
task manifest
verifier manifest + health identity
sampling/seed
timeout
cache state
hardware class
context policy
candidate-pool identity
```

Required surfaces:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Not every task is meaningful for raw model; `N/A` is allowed and must not become zero. A019 cannot use a stale candidate pool when MSTR-000B B013 has established a newer canonical pool.

## 7. Data/Training Interface

MSTR-000A freezes what future training observes; MSTR-000B freezes what data/verifier/curriculum may be admitted.

```text
TRAINING EXAMPLE
= exact model-facing history derived from events
+ action/tool/edit output
+ external observation/tool result
+ verifier/reward labels + verifier-health
+ task/environment/provenance identities
+ downstream rights/contamination/difficulty/admission identity
```

Future objectives include:
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- test-aware/diff-aware variants where specified;
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

Research donors are not automatically dependencies. Any copied code/direct dependency/model/dataset later requires exact license/source/admission under repository policy.

## 10. Testing Strategy

Required contract tests include:
- deterministic serialization;
- monotonic event ordering;
- replay equivalence/integrity;
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
- research loop cannot mutate frozen evaluation surface;
- task eligibility/dependency/authority checks once MSTR-000B B002 is canonical.

## 11. Security

Repository content is untrusted data, not authority.

Required controls:
- repository prompt-injection fixtures;
- no hidden network expansion;
- deny/limit evaluator modification;
- protect hidden tests/answers;
- prevent future-history/public-solution lookup;
- record every effect required by environment/setup;
- no secrets in trajectory payloads;
- no user trace ingestion by default;
- verifier-health failure cannot silently become success authority.

## 12. Implementation Shape

Python may be used for research/evidence tooling where already canonical; end-user runtime dependencies remain separately governed.

Suggested surfaces:

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
- A019/A020 consume MSTR-000B stable candidate/verifier/research-ladder outputs;
- map T035-T052 assumptions to frozen A+B contracts;
- reconcile T065-T071 environment/verifier tasks to avoid duplication;
- update MSTR-001/002/003 entry contracts with MSTR-000B B032;
- confirm T053 or successor remains a separate founder training gate;
- re-run Constitution Check against final implemented package.
