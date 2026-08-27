# A004 — AgentState Projection and Bounded Compaction

**Workstream:** MSTR-000A  
**Task:** A004  
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL  
**Canonical branch base:** `ead69ae26265b133c782ae8fd2795c126253a3b6`  
**Branch:** `feat/000a-a004-agent-state`

## Scope

A004 implements the model-independent `AgentState` working projection required by FR-A008/FR-A009.
The A003 append-oriented event log remains the sole authority. A004 does not create a second run-history
surface and performs no network, model, tokenizer, training, paid-compute, or dataset action.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_EXECUTION = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRIVATE_TRACE_INGESTION = NONE
```

## Canonical inputs

A004 was designed against canonical main and the already-canonical A003 implementation:

- `specs/001-agent-harness-verified-loop-foundation/spec.md`
- `specs/001-agent-harness-verified-loop-foundation/plan.md`
- `specs/001-agent-harness-verified-loop-foundation/data-model.md`
- `specs/001-agent-harness-verified-loop-foundation/tasks.md`
- `src/mstr_qualify/harness/event_log.py`
- `schemas/mstr-run-event-v0.schema.json`

A003 canonical merge identity remains:

```text
A003_PR = 38
A003_HEAD = 41122ae8dee65b2a6b3c6b188cf335d74088b06f
A003_MERGE = 2c02eb68a32264c86f69eb7ffc1c99ad87328376
```

## Implementation

New runtime surface:

```text
src/mstr_qualify/state/agent_state.py
```

The projector validates the original event chain through A003 `replay()` before deriving state. Every
retained fact/observation records `source_seq`, while `derived_through_seq` records the final replayed
sequence even when a `context.compacted` event contributes no new factual state.

Projected surfaces include:

```text
goal
acceptance_criteria
non_goals
constraints
current_plan
repo_map
files_inspected
changed_files
commands_run
verifier_results
known_failures
working_hypotheses
remaining_work
next_action
derived_through_seq
```

## Provenance and epistemic boundary

`working_hypotheses` are structurally labeled `UNCERTAIN`. A hypothesis is never promoted into a factual
context item, verifier PASS, or completion verdict.

Known projection keys are type-checked fail-closed. Unknown payload keys remain durable event-log evidence
but do not become AgentState facts merely because they exist.

Projection additionally enforces event-source authority for state-changing observations:

```text
run.goal_admitted -> user | harness | system
context.observed  -> user | harness | tool | environment | system
plan.updated      -> model | harness | system
tool.result       -> tool | harness | environment | system
edit.*            -> tool | harness | environment | system
verifier.result   -> verifier only
recovery.result   -> harness | tool | verifier | system
run.failed/escalated -> harness | verifier | system
```

A model-authored `verifier.result` or `edit.applied` therefore fails with
`state.source_not_authoritative` rather than becoming evidence.

`tool.requested` is intentionally **not** projected into `commands_run`: a request proves intent, while an
observed `tool.result` proves that an execution path actually returned a result.

`context.compacted` is deliberately ignored as a factual projection input. It may remain part of the
durable/model-visible event stream, but reprojecting facts from a summary would create circular state
authority. AgentState is reconstructed from the underlying original events instead.

Conflicting admitted goals are rejected instead of silently replacing the run goal.

## Failure preservation

A004 keeps verifier outcomes as observations and separately records non-PASS verifier outcomes in
`known_failures`. A later PASS from the same verifier does not delete earlier failure evidence.

The projector also records edit rejection, failed tool results, failed recovery, terminal failure and
escalation as failure evidence when authoritative events carry those observations.

## Bounded compaction

`CompactionPolicy` splits state into critical and compactable history.

Critical state is never truncated:

```text
goal
acceptance criteria
non-goals
constraints
current plan
changed files
all non-PASS verifier results
known failures
working hypotheses / uncertainty
remaining work
next action
```

If critical state exceeds `max_critical_items`, compaction fails closed with:

```text
state.critical_overflow
```

A004 therefore will not satisfy a context budget by erasing safety/recovery-relevant facts.

Compactable history is limited independently:

```text
repo_map
files_inspected
commands_run
historical PASS verifier results
```

When old compactable entries are omitted, the returned state includes an auditable `CompactionRecord`
containing field name, omitted count and deterministic SHA-256 over the omitted structured entries. The
most recent allowed entries remain visible.

## Adversarial fixture and tests

Fixture:

```text
tests/fixtures/harness/a004-adversarial-state.json
```

Test source:

```text
tests/unit/harness/test_agent_state.py
```

The current tests are written to check:

1. deterministic projection of required state;
2. explicit uncertainty retention;
3. verifier failure survival after later PASS;
4. changed-file/failure/remaining-work preservation through compaction;
5. deterministic omission digests;
6. critical-overflow rejection;
7. requested command is not misreported as a run command;
8. observed `tool.result` produces command history;
9. model-authored verifier evidence rejection;
10. model-authored applied-edit fact rejection;
11. `context.compacted` cannot reintroduce facts;
12. conflicting-goal rejection;
13. malformed projection payload rejection;
14. tampered A003 event-chain rejection;
15. edit/tool failure retention;
16. empty-log rejection.

## Static review reconciliation

Qodo's first exact-head review identified two material defects:

```text
FINDING_1 = tool.requested incorrectly populated commands_run
FINDING_2 = verifier.result lacked source provenance enforcement
```

Both were corrected before the next review head. A004 also proactively hardened `edit.applied` source
provenance and made `context.compacted` non-authoritative for factual reprojection. Ruff E501 candidates
noted by the reviewer were reformatted under the repository's 100-character line policy.

A new exact-head review is required after these mutations; the prior review is stale.

## Validation truth

The current environment cannot resolve `github.com` for an exact repository checkout. Therefore the
repository quality gates have **not** been executed on this feature head.

```text
A004_TARGETED_TEST = NOT_RUN
pytest -q = NOT_RUN
ruff check src tests = NOT_RUN
mypy = NOT_RUN
python -m mstr_qualify validate = NOT_RUN
GITHUB_ACTIONS = NOT_CLAIMED
```

No source inspection, reviewer statement, or reconstructed test is substituted for a frozen quality gate.
A004 must remain `NOT_COMPLETE_CANONICAL` and must not merge until exact-head gate evidence exists.

## Canonical boundary

```text
A004_IMPLEMENTATION = PRESENT_ON_FEATURE_BRANCH
A004_STATIC_REVIEW = PENDING_REVIEW_OF_CURRENT_HEAD
A004_QUALITY_GATES = NOT_RUN
A004_COMPLETE_CANONICAL = NO
TASK_CHECKBOX_UPDATED = NO
A005_AUTHORIZED_BY_THIS_BRANCH = NO
```
