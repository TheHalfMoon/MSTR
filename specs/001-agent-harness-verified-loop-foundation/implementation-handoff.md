# Implementation Handoff — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

## Entry Boundary

Do not start implementation until:

```text
T034 = COMPLETE_CANONICAL
MSTR-000A SPEC KIT = CANONICAL
```

T029–T034 are deliberately not blocked by this planning package.

## What This Workstream Must Accomplish

MSTR-000A exists to make later training optimize the behavior the product actually needs:

> A very small coding model receives a software direction, understands the repository and constraints, makes minimal changes, executes the work, verifies it independently, recovers from failure, and stops at verified completion.

The workstream freezes/qualifies:
- Build Loop v0;
- loop/event/state/trajectory contracts;
- append-oriented replayable run log;
- neutral minimal harness;
- MSTR-native harness;
- WePLD-native adapter;
- environment bootstrap/admission MVP;
- independent verifier/finalizer MVP;
- Direction-to-Done v0;
- DVCR/TTVC diagnostic metrics;
- failure/recovery taxonomy;
- training trajectory admission;
- bounded MSTR Research Loop v0;
- downstream training/task reconciliation.

## Read First

1. `AGENTS.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. this package's `spec.md`
6. `clarification-closeout.md`
7. `research.md`
8. `plan.md`
9. `data-model.md`
10. `contracts/README.md` and schemas
11. `quickstart.md`
12. `checklists/implementation-readiness.md`
13. `tasks.md`
14. this handoff

## Standing Boundaries

```text
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
WEIGHT_CHANGING_TRAINING = NO
T053_OR_SUCCESSOR = SEPARATE_FOUNDER_GATE
PAID_API = NO
PAID_COMPUTE = NO
LARGE_DATASET_INGESTION = NO
PRODUCTION_TRACE_INGESTION = NO_BY_DEFAULT
DEFAULT_MULTI_AGENT = NO
```

## Implementation Philosophy

- Smallest sufficient harness wins.
- One MSTR builder + independent deterministic verifier is the default topology.
- Richer harness/context/subagent features must earn their cost through comparable DVCR/TTVC evidence.
- Model-visible facts must be replayable from typed events.
- Failure evidence is kept.
- User/private repository content is never training data by default.
- Research donors are references, not automatic dependencies.

## Required Final Founder Report

At MSTR-000A closeout, report:

```text
CANONICAL_MAIN
BUILD_LOOP_VERSION
EVENT_LOG_VERSION
AGENT_STATE_VERSION
NEUTRAL_HARNESS_ID
MSTR_HARNESS_ID
WEPLD_ADAPTER_ID
ENVIRONMENT_MVP_ID
VERIFIER_MVP_ID
DIRECTION_TO_DONE_V0_ID
HARNESS_TOURNAMENT_RESULTS
DVCR_BY_SURFACE
TTVC_BY_SURFACE
FIRST_PASS_ACCEPT_RATE
EDIT_SURVIVAL_RATE
REPAIR_SUCCESS_RATE
TOOL_ERROR_RATE
TRAJECTORY_CONTRACT_ID
RESEARCH_LOOP_ID
T035-T052_RECONCILIATION
T065-T071_RECONCILIATION
DOWNSTREAM_MSTR_001_002_003_ENTRY_STATUS
UNRESOLVED_RISKS
QUALITY_GATES
```

Finish with the exact training authority state. Unless separately changed by a later canonical founder gate, it must still say that weight-changing training awaits explicit authorization.
