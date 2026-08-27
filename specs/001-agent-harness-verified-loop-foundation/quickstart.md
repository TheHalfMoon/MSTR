# Quickstart — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

This quickstart describes the implementation workflow under the corrected MSTR-000A / MSTR-000B sequence.

## Preconditions

For an **early-safe A001-A018 task**:

```text
MSTR-000A_SPEC_KIT = CANONICAL
EXACT_TASK_PREREQUISITES = SATISFIED
TASK_DOES_NOT_REQUIRE_UNQUALIFIED_CANDIDATE_RESULT = TRUE
TASK_DOES_NOT_REQUIRE_UNAUTHORIZED_EXTERNAL_EFFECT = TRUE
WEIGHT_CHANGING_TRAINING = NO
PAID_COMPUTE = NO
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

For **A019-A024 convergence** additionally require the exact MSTR-000B/candidate prerequisites in `tasks.md`, including the stable product-aligned candidate pool and required verifier/research contracts.

Before each task, re-read live `main`, `AGENTS.md`, the constitution, `CURRENT_STATE.md`, MSTR-000A, MSTR-000B, and exact task prerequisites.

Task-gate bootstrap is explicit:

```text
before B002 is canonical:
  there is no machine validator requirement to execute;
  manually enforce exact prerequisites and authority.

after B002 is COMPLETE_CANONICAL:
  require exact-main eligible=true before every material B-task governed by B002 and again before merge;
  fail closed on validator error or ineligible result.
```

The absence of B002 before its implementation is never permission to bypass task prerequisites.

## Implementation Order

Early-safe foundation:

```text
contracts/serialization
-> event log + replay
-> AgentState projection/compaction
-> Build Loop state graph
-> protected verifier/finalizer boundary
-> neutral harness
-> MSTR native harness
-> WePLD adapter + CapabilityProfile
-> environment admission MVP
-> Direction-to-Done task/eval surface
-> failure taxonomy + trajectory recorder
```

Convergence only after MSTR-000B/candidate prerequisites:

```text
stable product-aligned candidate pool
+ verifier health
+ research ladder
+ required A001-A018 outputs
-> harness tournament
-> research loop campaign
-> downstream task reconciliation
-> closeout
```

The protected verifier/finalizer boundary is defined before harness implementations because every harness must invoke the same independent success-authority contract rather than inventing its own completion semantics.

## Baseline Run

Every harness/research campaign begins with a frozen baseline. Record:

```text
model/artifact identity
runtime/build identity
interaction + loop contract
harness profile
task manifest
verifier manifest + verifier-health identity
sampling/seed
timeout/cache
hardware class
```

Then execute without changing evaluation policy.

## Success

A builder cannot mark itself done.

```text
MODEL_PROPOSES_STOP
-> FINALIZER REQUESTS REQUIRED VERIFIERS
-> VERIFIERS RUN IN PROTECTED BOUNDARY
-> FINALIZER DERIVES VERIFIED_SUCCESS OR FAILURE/ESCALATION
```

## Direction-to-Done Example

Direction:

```text
Add an offline import command that validates a bundle before writing anything.
```

The benchmark/task manifest may hide exact accepted file paths and tests. The harness should let the model take only the states actually needed:

```text
goal
-> inspect/localize when needed
-> form minimal plan when needed
-> edit
-> run targeted verification
-> recover if needed
-> run final verifier set
```

The Build Loop is a bounded state graph, not a mandatory verbose ritual. The score is not based on the model saying the feature works.

## Research Loop Example

A non-weight-changing first campaign might compare two state-compaction policies using the MSTR-000B multi-fidelity ladder:

```text
FROZEN:
Direction task set
model
runtime
verifier
loop/tool/edit contract
budget
product/rights/contamination constraints

MUTABLE:
state compaction policy only
```

Run baseline and candidates, promote only when predeclared criteria pass, then record `keep`, `discard`, `crash`, or `invalid`.

## Hard Stops

Stop and escalate if implementation would require:
- new model weight access outside exact canonical authority;
- weight-changing training before the separate training gate;
- paid APIs/compute;
- hidden production telemetry;
- user repository ingestion as training data;
- arbitrary benchmark/hidden-verifier modification;
- bypass of MSTR-000B convergence prerequisites;
- a materially higher universal-laptop floor;
- donor code/dependency admission not already governed.
