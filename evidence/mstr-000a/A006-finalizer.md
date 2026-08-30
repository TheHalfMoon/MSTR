# A006 — Protected Finalizer / Verifier Boundary Evidence

**Task:** `A006`  
**State:** `IMPLEMENTATION_ACTIVE / QUALIFICATION_PENDING`  
**Canonical entry main:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`

## Entry Gate

A006 is model-independent early-safe MSTR-000A work. The canonical entry state proves:

```text
A001 = COMPLETE_CANONICAL
A002 = COMPLETE_CANONICAL
A003 = COMPLETE_CANONICAL
A004 = COMPLETE_CANONICAL
A005 = COMPLETE_CANONICAL
UNQUALIFIED_CANDIDATE_RESULT_REQUIRED = NO
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```

The repository has no machine-readable MSTR-000A task catalog, so A006 uses the canonical Spec001 manual exact-prerequisite rule. A006 consumes the canonical A002/A003 event integrity chain and the A005 bounded Build Loop stop-proposal boundary; it introduces no competing event or task authority.

## Implementation Scope

A006 introduces a small protected finalizer package under `src/mstr_qualify/verifier/` plus unit/security regressions.

The finalizer:

- replays and validates the complete `mstr.run-event.v0` hash/predecessor chain before making a decision;
- rejects mixed run identities;
- rejects any pre-existing `run.completed`, `run.failed`, or `run.escalated` event rather than rewriting terminal history;
- requires the latest `run.stop_proposed` to be authored by `model` or `harness`;
- allows only `verifier.started` / `verifier.result` events after the latest stop proposal; any edit/tool/context/recovery or other state-changing event requires a new stop proposal before finalization;
- accepts `verifier.result` authority only from `source=verifier`;
- requires every configured verifier id to be non-empty, unique, and present;
- requires a fresh result for every required verifier after the latest stop proposal, preventing stale PASS reuse;
- requires the latest result for every required verifier to be `PASS`;
- rejects malformed verifier statuses through the stable finalizer error boundary, including non-string/unhashable JSON values;
- derives `VERIFIED_SUCCESS` or `RECOVERED_SUCCESS` mechanically rather than accepting a caller-selected terminal class;
- computes a deterministic aggregate `verifier_result_identity` from the exact final required result identities;
- emits the canonical `run.completed` event as `source=verifier`, `model_visible=false`, chained to the exact final input event;
- provides no API by which model text, repository text, harness text, or a pre-existing completion event can self-author success.

## Post-Stop Freshness Hardening

A later security review identified an event-order freshness gap. The prior candidate required verifier PASS results after the latest `run.stop_proposed`, but it did not reject a valid state-changing event inserted after that stop. Therefore an event sequence such as either of these was not explicitly rejected by the finalizer boundary itself:

```text
run.stop_proposed
-> edit.applied
-> verifier.result PASS
-> finalize
```

```text
run.stop_proposed
-> verifier.result PASS
-> edit.applied
-> finalize
```

A005's `BuildLoop` makes STOP terminal for the builder, but A006 is the protected event-log success boundary and must fail closed even if an invalid producer appends a schema-valid post-stop mutation. The candidate now restricts the post-stop interval to verifier lifecycle events only. Any other event requires a fresh stop proposal before success can be derived.

Dedicated security regression:

```text
tests/security/test_finalizer_post_stop_boundary.py
```

covers mutation before and after the fresh verifier PASS and requires:

```text
finalizer.post_stop_event_invalid
```

## Security Regressions

The candidate includes explicit tests for:

```text
MODEL_FAKE_COMPLETION -> REJECT / NO_VERIFIER_AUTHORITY
HARNESS_OR_MODEL_SPOOFED_VERIFIER_RESULT -> REJECT
STALE_PRE_STOP_PASS_REUSE -> REJECT
POST_STOP_STATE_MUTATION_BEFORE_PASS -> REJECT / NEW_STOP_REQUIRED
POST_STOP_STATE_MUTATION_AFTER_PASS -> REJECT / NEW_STOP_REQUIRED
MISSING_REQUIRED_VERIFIER -> REJECT
REQUIRED_FAIL_ERROR_UNKNOWN -> REJECT
MALFORMED_NON_STRING_VERIFIER_STATUS -> REJECT
PREEXISTING_COMPLETION_FAILURE_ESCALATION -> REJECT
MIXED_RUN_IDENTITY -> REJECT
TAMPERED_EVENT_HASH_CHAIN -> REJECT
EMPTY_OR_DUPLICATE_REQUIRED_VERIFIER_CONFIG -> REJECT
UNTRUSTED_STOP_SOURCE -> REJECT
ALL_FRESH_REQUIRED_PASS -> VERIFIED_SUCCESS
RECOVERY_OR_PRIOR_FAILURE_THEN_FRESH_PASS -> RECOVERED_SUCCESS
```

## Qualification State

Historical focused evidence exists for the earlier exact candidate `d6de54c685622ad0d230c11d7173b3559676b37c`:

```text
PYTHONPATH=src python -m pytest -q tests/unit/test_finalizer.py tests/security/test_finalizer_boundary.py
25 passed in 1.64s
```

The exact Git blobs used by that earlier reconstruction were identity-matched before execution. That PASS is historical evidence for the unchanged earlier behavior only; it does **not** transfer to the current post-stop-hardening head.

Hosted qualification attempts on the earlier candidate repeatedly failed before exposing any runner step. The 2026-08-30 retry of run `33260494525` again produced:

```text
quality_semantics = 99230613964 / FAILURE / steps=null / logs_url=null
identity_scope     = 99230614091 / FAILURE / steps=null / logs_url=null
complete           = 99230621327 / SKIPPED
```

No checkout or quality command executed in that retry. A fresh qualification must be pinned to the current final candidate after this hardening.

```text
A006_CURRENT_HEAD_FOCUSED_PYTEST = NOT_EXECUTED
A006_CURRENT_HEAD_FULL_PYTEST = NOT_EXECUTED
A006_CURRENT_HEAD_SCHEMA_VALIDATE = NOT_EXECUTED
A006_CURRENT_HEAD_RUFF = NOT_EXECUTED
A006_CURRENT_HEAD_MYPY = NOT_EXECUTED
CI_PASS = NOT_CLAIMED
A006_COMPLETE_CANONICAL = NO
MERGE_AUTHORITY = ABSENT
```

A hosted job that fails before any step is infrastructure-block evidence, not a test failure and not merge authority. Only exact-head executed commands may be recorded as PASS/FAIL.

## Authority Boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```

A006 remains unchecked in `tasks.md`. It cannot become `COMPLETE_CANONICAL`, unblock A007/B023, or authorize dependent work merely because the implementation exists on a branch. Exact-head qualification, review, mandatory premerge verification, guarded merge, post-merge proof, and separate closeout remain required.
