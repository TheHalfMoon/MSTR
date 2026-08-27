# B003 — Canonical Drift Detector Implementation Evidence

**Workstream:** MSTR-000B
**Task:** B003
**State:** IMPLEMENTATION_ACTIVE
**Canonical base / entry-gate main:** `0754d552752c2f6c099df2b480de99028e2e26e5`
**Implementation branch:** `feat/000b-b003-drift-detector`
**Implementation PR:** NOT_YET_OPEN

B003 is not `COMPLETE_CANONICAL` in this implementation evidence. The canonical task checkbox and machine catalog remain `PENDING` until a separate post-merge closeout.

## Mandatory exact-main entry gate

B002 became `COMPLETE_CANONICAL` only after PR #49 merged and the resulting canonical main passed post-closeout verification. Run `33083687113`, job `98557431219`, checked out exact main `0754d552752c2f6c099df2b480de99028e2e26e5`, proved `HEAD == refs/heads/main == refs/remotes/origin/main`, and then exercised the production gates.

```text
ENTRY_GATE_TASK = B003
ENTRY_GATE_CANONICAL_MAIN = 0754d552752c2f6c099df2b480de99028e2e26e5
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_RUN = 33083687113
ENTRY_GATE_JOB = 98557431219
B002_PRODUCTION_TERMINAL = true
B003_PRODUCTION_ELIGIBLE = true
TARGETED_TASK_GATE_TESTS = PASS (43 passed in 8.71s)
pytest -q = PASS (487 passed in 15.23s)
ruff check src tests = PASS
mypy = PASS (25 source files)
python -m mstr_qualify validate = PASS
FINAL_MAIN_SHA = 0754d552752c2f6c099df2b480de99028e2e26e5
```

This exact gate authorizes only ordinary B003 repository work. It grants no model, data, training, compute, network, or release authority.

## Implementation scope

B003 adds a read-only canonical drift scanner that compares machine-readable repository facts without contacting GitHub or any provider at runtime. The intended detector covers:

- canonical task state vs task checkbox consistency;
- machine-readable evidence completion claims vs canonical task state;
- implementation PR merge records discoverable from local Git history;
- canonical task-markdown implementation identities when present;
- evidence/task implementation PR, final-head, and merge-SHA agreement;
- final implementation head ancestry into the recorded merge and merge ancestry on canonical main;
- B003+ entry-gate evidence presence and `eligible=true` state once an implementation is merged or canonically terminal;
- entry-gate main ancestry before the recorded final implementation head;
- deterministic, read-only `task drift` CLI status with exit `0=clean`, `1=drift`, `2=configuration/environment error`.

Synthetic fixture cases cover clean state, checkbox/state conflict, premature evidence completion, implementation merged while task remains active, a valid B003 terminal record, and an entry gate recorded after implementation.

## Authority boundary

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
```

## Completion rule

Do not check B003 or change `configs/task-gate/mstr-000b.json` to `COMPLETE_CANONICAL` in the implementation PR. Final exact-head gates and review must bind the final implementation head; the implementation PR must merge with an expected-head guard; canonical main must pass post-implementation verification; then a separate closeout may align evidence, task checkbox, machine catalog, and successor B004 expectations. Only after that closeout merges and post-closeout verification passes may B003 be called `COMPLETE_CANONICAL`.
