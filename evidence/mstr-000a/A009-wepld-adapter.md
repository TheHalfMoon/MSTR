# A009 — H2 WePLD-native adapter

**Task:** `MSTR-000A / A009`  
**Candidate state:** `IMPLEMENTED_PENDING_EXACT_HEAD_QUALIFICATION`  
**Base:** `5416494b60590c0b9a3f6178c58224f4edb01dd7`

## Scope

A009 adds a portable H2 adapter that maps WePLD goal/spec/task/effect/verifier state into the already-canonical MSTR H1/A005/A006 harness spine.

Implementation surfaces:

- `src/mstr_qualify/harness/wepld.py`
- `configs/harness/wepld-native-v0.json`
- `tests/fixtures/harness/a009-wepld-state.json`
- `tests/unit/harness/test_wepld.py`
- `tests/security/test_wepld_adapter_boundary.py`

## Contract

```text
ADAPTER_CONTRACT = mstr.wepld-adapter.v0
HARNESS_PROFILE = mstr.harness.h2-wepld-native.v0
EXTENDS = mstr.harness.h1-native.v0
WEPLD_RUNTIME_DEPENDENCY = NONE
CANONICAL_LOOP_AUTHORITY = mstr.loop-contract.v0
CANONICAL_SUCCESS_AUTHORITY = A006 protected finalizer only
```

The adapter accepts only the portable state sections:

```text
goal
spec
task
effects
verifier
```

Mapping is deterministic:

```text
goal.direction
-> MSTR goal

goal/spec/task acceptance criteria
-> MSTR acceptance criteria

goal/spec/task constraints
+ exact spec/task identities
+ effect restrictions
+ verifier policy identity
-> MSTR constraints

goal.non_goals
-> MSTR non-goals
```

## Fail-closed boundaries

- The WePLD effect envelope must exactly match the active MSTR loop contract envelope.
- Allowed and prohibited WePLD effect sets must be disjoint.
- The WePLD required-verifier set must exactly match the MSTR required-verifier set.
- Unknown fields are rejected, including any attempted `canonical_success` field.
- H2 inherits H1 typed tools, stale-safe edits, bounded recovery, compaction, and selective context.
- Builder STOP remains non-authoritative. Required verifiers are re-run through A006 before a terminal success event can exist.
- The adapter imports no WePLD runtime package and performs no network lookup.

## Qualification required

This implementation is not canonical merely because it is committed. Before A009 may be closed:

1. exact-head focused/integration/security tests must pass;
2. `mstr-qualify validate` must pass;
3. full `pytest -q`, `ruff check src tests`, and `mypy src` must pass;
4. exact-head review must report no blocking finding;
5. mandatory premerge verification must pass;
6. the exact expected head must be guarded-merged;
7. post-merge canonical proof must pass;
8. a separate canonical closeout must update the task ledger/evidence terminal state and itself pass the closeout lifecycle.

## External-effect boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```
