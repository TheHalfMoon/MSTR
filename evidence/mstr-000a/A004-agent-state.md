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

## Projection authority

The projector validates the event chain through A003 `replay()` before deriving state. Every retained
fact or observation records its `source_seq`; `derived_through_seq` records the final replayed sequence.

Projected surfaces are:

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

`working_hypotheses` are structurally `UNCERTAIN` and are never promoted into factual context, verifier
PASS, or completion authority. Known projection keys are type-checked fail-closed.

Source authority for state-changing observations is explicit:

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

A model-authored `verifier.result` or `edit.applied` fails with
`state.source_not_authoritative` rather than becoming evidence.

`tool.requested` does not populate `commands_run`; a request proves intent, while an observed
`tool.result` proves that an execution path returned a result.

`context.compacted` is deliberately ignored as factual projection input. It may remain durable/model-visible
event data, but summary text cannot become a second circular authority for reconstructed state.

Conflicting admitted goals are rejected instead of silently replacing the run goal.

## Failure preservation

Non-PASS verifier observations remain in `verifier_results` and are also represented in `known_failures`.
A later PASS from the same verifier does not delete the earlier failure evidence.

Authoritative edit rejection, failed tool result, failed recovery, terminal failure and escalation events
are retained as failure evidence when their payloads support those observations.

## Bounded compaction

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

Only the following non-critical history is bounded:

```text
repo_map
files_inspected
commands_run
historical PASS verifier results
```

### Bounded audit metadata

Compaction metadata is itself bounded. The state permits at most one cumulative `CompactionRecord` for
each compactable field:

```text
repo_map
files_inspected
commands_run
verifier_results.pass
```

Therefore repeated compaction cannot create an unbounded audit-log tail inside `AgentState`.

For the first omission of a field, the record contains the omitted count and deterministic SHA-256 of the
omitted structured entries. If the already-compacted state is compacted again with a tighter policy, the
record is updated in place conceptually:

```text
omitted_count = previous_count + newly_omitted_count
omitted_sha256 = sha256(canonical_json({
  "previous_sha256": previous_digest,
  "next_sha256": new_omission_digest
}))
```

Existing records are normalized through the same fixed field vocabulary. Unknown record fields or invalid
record shapes fail closed with `state.invalid_compaction_record`.

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
6. repeated compaction keeps a fixed maximum four-record vocabulary;
7. cumulative omitted counts survive tighter repeated compaction;
8. repeating the same final policy is idempotent;
9. critical-overflow rejection;
10. requested command is not misreported as a run command;
11. observed `tool.result` produces command history;
12. model-authored verifier evidence rejection;
13. model-authored applied-edit fact rejection;
14. `context.compacted` cannot reintroduce facts;
15. conflicting-goal rejection;
16. malformed projection payload rejection;
17. tampered A003 event-chain rejection;
18. edit/tool failure retention;
19. empty-log rejection.

## Static review reconciliation

Qodo exact-head review history to date:

```text
FINDING_1 = tool.requested incorrectly populated commands_run
FINDING_2 = verifier.result lacked source provenance enforcement
FINDING_3 = compaction_records could grow without bound across repeated compaction
```

Findings 1 and 2 were confirmed closed by Qodo on head
`336ed346d65edb9283c081634938954d834d5860`.

Finding 3 was then corrected by replacing append-only compaction metadata with the fixed field vocabulary
and cumulative hash-chain aggregation described above. Regression coverage was added. Because this changed
the head again, a new exact-head review is required before any static-review-clean claim.

## Validation truth

The current environment cannot resolve `github.com` for an exact repository checkout. Therefore the
repository quality gates have **not** been executed on the current feature head.

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
