# A004 — AgentState Projection and Bounded Compaction

**Workstream:** MSTR-000A  
**Task:** A004  
**State:** COMPLETE_CANONICAL
**Canonical branch base:** `ead69ae26265b133c782ae8fd2795c126253a3b6`
**Branch:** `feat/000a-a004-agent-state`
**Implementation PR:** `#45`
**Final implementation head:** `d0098548766232c9fa1a879941978d1735ef9e4a`
**Canonical merge:** `564096fc9e8ec3e2b0aa9505926e15f66b00ce74`
**Final exact-head qualification run:** `33067884925`

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

## Final review reconciliation

Qodo review found and closed three material issues during A004 development:

```text
FINDING_1 = tool.requested incorrectly populated commands_run
FINDING_2 = verifier.result lacked source provenance enforcement
FINDING_3 = compaction_records could grow without bound across repeated compaction
```

The final implementation candidate additionally resolved repository quality-gate findings without changing
A004 semantics:

```text
RUFF_REMEDIATION = a4b81fb8fe147f8ea88e6bf1c654a39e81e187c8
STRICT_MYPY_REMEDIATION = d0098548766232c9fa1a879941978d1735ef9e4a
```

Qodo re-reviewed exact final head `d0098548766232c9fa1a879941978d1735ef9e4a` against the then-canonical
main and reported no material findings. The final strict-typing cast was confirmed as non-behavioral: it does
not alter projection semantics, compaction, replay, or event-source authority.

## Validation truth

A dedicated GitHub-hosted evidence run checked out the exact final implementation SHA itself in detached-head
mode, verified a clean working tree, installed the repository development tooling, and executed every frozen
quality gate. Historical or pre-push results were not substituted for this run.

```text
FINAL_HEAD = d0098548766232c9fa1a879941978d1735ef9e4a
FINAL_EXACT_HEAD_RUN = 33067884925
pytest -q = PASS (404 passed)
ruff check src tests = PASS
mypy = PASS (24 source files)
python -m mstr_qualify validate = PASS
VALID_FIXTURES_PASSED = 8
INVALID_FIXTURES_REJECTED = 8
```

PR #45 was then marked ready only after the exact-head review and quality gates were clean. Immediately before
merge, canonical `main`, the PR head, mergeability, and review-thread state were re-read. GitHub merged with an
`expected_head_sha` guard, and post-merge verification established:

```text
A004_PR = 45
A004_FINAL_HEAD = d0098548766232c9fa1a879941978d1735ef9e4a
A004_MERGE = 564096fc9e8ec3e2b0aa9505926e15f66b00ce74
POST_MERGE_MAIN = 564096fc9e8ec3e2b0aa9505926e15f66b00ce74
PR_45_MERGED = YES
```

## Canonical boundary

```text
A004_IMPLEMENTATION = CANONICAL_ON_MAIN
A004_STATIC_REVIEW = PASS / NO_MATERIAL_FINDINGS_AT_FINAL_HEAD
A004_QUALITY_GATES = PASS_AT_EXACT_FINAL_HEAD
A004_COMPLETE_CANONICAL = YES
TASK_CHECKBOX_UPDATED = YES
A005_ENTRY_PREREQUISITE_A004 = SATISFIED
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_EXECUTION = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRODUCTION_RELEASE = NONE
```

This closeout does not itself authorize any external effect. Subsequent task eligibility remains governed by
the live repository task graph, prerequisites, active-path ownership, and external-effect gates.
