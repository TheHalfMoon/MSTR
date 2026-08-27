# B002 — Offline Task Eligibility Validator Implementation Evidence

**Workstream:** MSTR-000B
**Task:** B002
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL
**Canonical implementation base:** `856a7993f64a7f17ead6f6c019c5668724444ed4`
**Branch:** `feat/000b-b002-task-gate`

This document records B002 implementation evidence only. The task remains unchecked until exact-head qualification, exact-head review, implementation merge, and a separate post-merge canonical closeout are complete.

## Manual bootstrap eligibility

B002 is the second and final explicit machine-gate bootstrap exception. Its exact predecessor is B001. Live canonical truth before B002 mutation established:

```text
CANONICAL_MAIN = 856a7993f64a7f17ead6f6c019c5668724444ed4
B001_STATE = COMPLETE_CANONICAL
B001_TASK_CHECKBOX = CHECKED
B001_IMPLEMENTATION_PR = 40
B001_IMPLEMENTATION_MERGE = 773555e9861d1c901c12718832821a98f472833f
B001_CLOSEOUT_PR = 47
B001_CLOSEOUT_MERGE = 856a7993f64a7f17ead6f6c019c5668724444ed4
B002_BOOTSTRAP_MANUAL_VERIFICATION = SATISFIED
```

B002 creates no external-effect authority.

## Implementation scope

B002 introduces:

- `configs/task-gate/mstr-000b.json`: repository-local MSTR-000B task catalog covering B001-B034;
- `src/mstr_qualify/task_gate.py`: deterministic offline catalog loading and eligibility evaluation;
- CLI wiring for `python -m mstr_qualify task eligible <TASK_ID>`;
- contract and integration tests for fail-closed dependency, state, authority, candidate-pool, supersession and CLI behavior.

The catalog is independently reconciled against every B-task checkbox/title in canonical `tasks.md`; coverage drift or duplicate/missing task identities is an error. Generated task records are validated against the frozen `mstr.task-node.v0` contract before use.

## Eligibility semantics

The evaluator binds every result to:

```text
TASK_NODE_SCHEMA = mstr.task-node.v0
RESULT_SCHEMA = mstr.task-eligibility.v0
CANONICAL_MAIN = exact checked-out Git HEAD
TASK_NODE_SHA256 = deterministic canonical JSON identity
```

It fails closed on:

- missing/unbound predecessor;
- predecessor not in a canonical terminal state;
- missing predecessor evidence/output required by its closeout rule;
- checkbox/catalog state conflict;
- blocked or already-terminal requested task;
- supersession;
- missing or invalid canonical authority envelope for authority-gated effects;
- missing or invalid stable candidate-pool decision for candidate-dependent tasks;
- unresolved catalog bindings intentionally left blocked for later exact reconciliation.

No eligibility result mutates the catalog, task markdown, evidence, authority records or candidate-pool decisions.

## Authority verification boundary

`required_authority_id` remains a foreign key; it never grants authority. For a gated task B002 only recognizes an exact repository-local canonical envelope at:

```text
artifacts/authorities/<required_authority_id>.json
```

The record must bind the same task and external-effect class, carry `status=AUTHORIZED_CANONICAL`, and contain a structured scope. B002 creates no such envelope. No identifier, branch file, CLI argument, or generic continuation instruction is treated as authority by itself.

Candidate-pool requirements similarly require a repository-local stable decision whose exact decision identity matches the TaskNode requirement. A missing decision remains `eligible=false`.

## Bootstrap catalog state

At B002 implementation time:

- B001 is `COMPLETE_CANONICAL`;
- B002 is `PENDING`;
- B003 is `PENDING` with B002 as its predecessor;
- tasks with known unresolved future bindings such as B011/B013/B029/B030/B031 are explicitly `BLOCKED` rather than receiving inferred authority or guessed cross-workstream prerequisites;
- B023/B031 preserve external prerequisite identities and fail closed while those bindings are absent from the MSTR-000B catalog.

B002 closeout must change B002 itself to `COMPLETE_CANONICAL` in both the catalog and canonical task checkbox. Only after that closeout may B003 execution begin, and it must first receive an exact-main `eligible=true` result.

## Required contract coverage

The tests include every authority-gated external-effect class with the required authority binding omitted and require a schema-valid `eligible=false` diagnostic. They also require `eligible=false` when `candidate_dependent=true` omits `candidate_pool_requirement_id`.

Additional coverage includes:

- B002 bootstrap eligibility from canonical B001;
- B003 ineligibility before B002 closeout;
- explicit BLOCKED task rejection;
- terminal task rejection for new execution;
- unknown task failure;
- canonical task catalog B001-B034 coverage;
- predecessor checkbox/state conflict;
- missing predecessor binding;
- catalog non-mutation;
- CLI exit contract: `0=eligible`, `1=ineligible`, `2=configuration/error`.

## Qualification state

```text
TARGETED_TESTS = NOT_RUN
pytest -q = NOT_RUN
ruff check src tests = NOT_RUN
mypy = NOT_RUN
python -m mstr_qualify validate = NOT_RUN
EXACT_HEAD_REVIEW = NOT_RUN
GITHUB_ACTIONS_EXACT_HEAD = NOT_CLAIMED
```

Historical or pre-commit results will not be reused after the final head changes.

## Authority / non-goals

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TOKENIZER_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
PRIVATE_USER_TRACE_INGESTION = NONE
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
B002_COMPLETE_CANONICAL = NO
```
