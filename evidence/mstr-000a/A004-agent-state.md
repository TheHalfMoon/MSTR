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

The projector validates the original event chain through A003 `replay()` before deriving state. The
projection records `source_seq` for every retained fact/observation and sets `derived_through_seq` to the
last replayed event sequence.

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

## Epistemic boundary

`working_hypotheses` are structurally labeled `UNCERTAIN`. A hypothesis is never promoted into:

- a factual context item;
- a verifier PASS;
- a completion verdict.

Known projection keys are type-checked fail-closed. Unknown event payload keys remain event-log evidence
but do not become AgentState facts merely because they exist.

Conflicting admitted goals are rejected instead of silently replacing the run goal.

## Failure preservation

A004 keeps verifier outcomes as observations and separately records non-PASS verifier outcomes in
`known_failures`. A later PASS from the same verifier does not delete the earlier failure evidence.

The projector also records edit rejection, failed tool results, failed recovery and terminal failure or
escalation as failure evidence where the corresponding events carry those observations.

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

This is deliberate: A004 will not meet a context budget by erasing safety/recovery-relevant facts.

Compactable history is limited independently:

```text
repo_map
files_inspected
commands_run
historical PASS verifier results
```

When old compactable entries are omitted, the returned state includes an auditable `CompactionRecord`
containing field name, omitted count and deterministic SHA-256 over the omitted structured entries.
The most recent allowed entries remain visible.

## Adversarial fixture and tests

Fixture:

```text
tests/fixtures/harness/a004-adversarial-state.json
```

The fixture intentionally contains:

- a failed tool command;
- a verifier FAIL followed later by PASS;
- changed files;
- context volume exceeding a small test compaction budget;
- hypotheses that sound like success but remain unverified;
- remaining work after targeted verification.

Test source:

```text
tests/unit/harness/test_agent_state.py
```

The tests are written to check:

1. deterministic projection of required state;
2. explicit uncertainty retention;
3. verifier failure survival after later PASS;
4. changed-file/failure/remaining-work preservation through compaction;
5. deterministic omission digests;
6. critical-overflow rejection;
7. conflicting-goal rejection;
8. malformed projection payload rejection;
9. tampered A003 event-chain rejection;
10. edit/tool failure retention;
11. empty-log rejection.

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
A004_STATIC_REVIEW = PENDING
A004_QUALITY_GATES = NOT_RUN
A004_COMPLETE_CANONICAL = NO
TASK_CHECKBOX_UPDATED = NO
A005_AUTHORIZED_BY_THIS_BRANCH = NO
```
