# Quickstart — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

This quickstart describes the expected implementation workflow after T034 is canonical and this package is merged.

## Preconditions

```text
T034 = COMPLETE_CANONICAL
MSTR-000A_SPEC_KIT = CANONICAL
WEIGHT_CHANGING_TRAINING = NO
PAID_COMPUTE = NO
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

Before each task, re-read live `main`, `AGENTS.md`, the constitution, `CURRENT_STATE.md`, this package, and exact task prerequisites.

## Implementation Order

```text
contracts/serialization
-> event log + replay
-> AgentState projection/compaction
-> Build Loop state machine
-> neutral harness
-> MSTR native harness
-> verifier/finalizer boundary
-> environment admission MVP
-> Direction-to-Done task/eval surface
-> failure taxonomy + trajectory recorder
-> WePLD adapter
-> harness tournament
-> research loop
-> downstream task reconciliation
```

## Baseline Run

Every harness/research campaign begins with a frozen baseline. Record:

```text
model/artifact identity
runtime/build identity
interaction + loop contract
harness profile
task manifest
verifier manifest
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

The benchmark/task manifest may hide exact accepted file paths and tests. The harness should let the model:

```text
orient
-> inspect repo
-> identify constraints
-> localize
-> form small plan
-> edit
-> run targeted verification
-> recover if needed
-> run final verifier set
```

The score is not based on the model saying the feature works.

## Research Loop Example

A non-weight-changing first campaign might compare two state-compaction policies:

```text
FROZEN:
Direction task set
model
runtime
verifier
loop/tool/edit contract
budget

MUTABLE:
state compaction policy only
```

Run baseline and candidates, then record `keep`, `discard`, `crash`, or `invalid` from predeclared rules.

## Hard Stops

Stop and escalate if implementation would require:
- weight-changing training before the separate training gate;
- paid APIs/compute;
- hidden production telemetry;
- user repository ingestion as training data;
- arbitrary benchmark/hidden-verifier modification;
- a materially higher universal-laptop floor;
- donor code/dependency admission not already governed.
