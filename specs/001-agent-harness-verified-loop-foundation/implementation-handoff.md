# Implementation Handoff — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

## Entry Boundary

Do not use a blanket T034 gate for all MSTR-000A work.

For early-safe A001-A018 implementation:

```text
MSTR-000A SPEC KIT = CANONICAL
EXACT TASK PREREQUISITES = SATISFIED
NO UNQUALIFIED CANDIDATE RESULT REQUIRED
NO UNAUTHORIZED EXTERNAL EFFECT REQUIRED
```

For A019-A024 convergence additionally require the stable/equivalent candidate and MSTR-000B prerequisites named by live `tasks.md`.

Existing MSTR-000 candidate qualification continues under its own task graph and is not reopened by this package.

## What This Workstream Must Accomplish

MSTR-000A exists to make later training optimize the behavior the product actually needs:

> A very small coding model receives a software direction, understands the repository and constraints, makes only the planning/context moves the task needs, executes the work, verifies it independently, recovers from failure, and stops at verified completion.

The workstream freezes/qualifies:
- Build Loop v0 as a bounded state graph;
- loop/event/state/trajectory contracts;
- append-oriented replayable run log;
- neutral minimal harness;
- MSTR-native harness;
- WePLD-native adapter or an explicit governed deferral with evidence;
- environment bootstrap/admission MVP;
- independent verifier/finalizer MVP;
- Direction-to-Done v0;
- DVCR/TTVC diagnostic metrics;
- failure/recovery taxonomy;
- training trajectory admission;
- bounded MSTR Research Loop v0;
- downstream training/task reconciliation with MSTR-000B.

## Read First

1. `AGENTS.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`
6. `docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md`
7. this package's `spec.md`
8. `clarification-closeout.md`
9. `research.md`
10. `plan.md`
11. `data-model.md`
12. `contracts/README.md` and schemas
13. `quickstart.md`
14. `checklists/implementation-readiness.md`
15. `tasks.md`
16. this handoff

## Standing Boundaries

```text
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
NEW_WEIGHT_ACCESS = ONLY_UNDER_EXACT_CANONICAL_AUTHORITY
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
- Build Loop is a state graph with a trivial-task fast path, not forced chain-of-thought ceremony.
- Richer harness/context/subagent features must earn their cost through comparable DVCR/TTVC evidence.
- Model-visible facts must be replayable from typed events.
- Failure evidence is kept.
- User/private repository content is never training data by default.
- Research donors are references, not automatic dependencies.
- MSTR-000B supplies product-aligned candidate, data/curriculum, verifier-health, Q4 and research-promotion requirements before convergence/training.

## WePLD Adapter Reporting Rule

A valid governed deferral MUST NOT invent an adapter ID.

At closeout report:

```text
WEPLD_ADAPTER_STATUS = QUALIFIED | DEFERRED

if QUALIFIED:
  WEPLD_ADAPTER_ID = <exact adapter id/version>
  WEPLD_ADAPTER_DEFERRAL_EVIDENCE = N/A

if DEFERRED:
  WEPLD_ADAPTER_ID = N/A
  WEPLD_ADAPTER_DEFERRAL_EVIDENCE = <exact canonical evidence path/id>
```

A deferral is valid only where the active task/spec explicitly permits it and the evidence records the blocking reason and downstream effect.

## Required Final Founder Report

At MSTR-000A closeout, report:

```text
CANONICAL_MAIN
BUILD_LOOP_VERSION
EVENT_LOG_VERSION
AGENT_STATE_VERSION
NEUTRAL_HARNESS_ID
MSTR_HARNESS_ID
WEPLD_ADAPTER_STATUS
WEPLD_ADAPTER_ID
WEPLD_ADAPTER_DEFERRAL_EVIDENCE
ENVIRONMENT_MVP_ID
VERIFIER_MVP_ID
VERIFIER_HEALTH_ID
DIRECTION_TO_DONE_V0_ID
STABLE_CANDIDATE_POOL_ID
HARNESS_TOURNAMENT_RESULTS
DVCR_BY_SURFACE
TTVC_BY_SURFACE
FIRST_PASS_ACCEPT_RATE
EDIT_SURVIVAL_RATE
REPAIR_SUCCESS_RATE
TOOL_ERROR_RATE
TRAJECTORY_CONTRACT_ID
RESEARCH_LOOP_ID
RESEARCH_LADDER_ID
T035-T052_RECONCILIATION
T065-T071_RECONCILIATION
MSTR_000B_CONVERGENCE_STATUS
DOWNSTREAM_MSTR_001_002_003_ENTRY_STATUS
UNRESOLVED_RISKS
QUALITY_GATES
```

Finish with the exact training authority state. Unless separately changed by a later canonical founder gate, it must still say that weight-changing training awaits explicit authorization.
