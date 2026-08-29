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
- accepts `verifier.result` authority only from `source=verifier`;
- requires every configured verifier id to be non-empty, unique, and present;
- requires a fresh result for every required verifier after the latest stop proposal, preventing stale PASS reuse after new edits;
- requires the latest result for every required verifier to be `PASS`;
- rejects malformed verifier statuses through the stable finalizer error boundary, including non-string/unhashable JSON values;
- derives `VERIFIED_SUCCESS` or `RECOVERED_SUCCESS` mechanically rather than accepting a caller-selected terminal class;
- computes a deterministic aggregate `verifier_result_identity` from the exact final required result identities;
- emits the canonical `run.completed` event as `source=verifier`, `model_visible=false`, chained to the exact final input event;
- provides no API by which model text, repository text, harness text, or a pre-existing completion event can self-author success.

## Security Regressions

The candidate includes explicit tests for:

```text
MODEL_FAKE_COMPLETION -> REJECT / NO_VERIFIER_AUTHORITY
HARNESS_OR_MODEL_SPOOFED_VERIFIER_RESULT -> REJECT
STALE_PRE_STOP_PASS_REUSE -> REJECT
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

The previous A005 post-closeout history showed two different facts that must remain separate:

1. substantive merge-identity and canonical quality/frontier jobs completed successfully on the A005 post-closeout run;
2. a redundant final aggregation job, and then a later retry job, failed before exposing any steps after repository visibility had changed to private.

Those historical runs do not prove either PASS or current runner blockage for this A006 head. Repository visibility remains a hosting fact, not implementation evidence. A006 therefore requires a fresh exact-head qualification attempt and may update this section only from the resulting run/job/step truth.

```text
A006_FOCUSED_PYTEST = NOT_YET_RUN_ON_FINAL_EXACT_HEAD
A006_FULL_PYTEST = NOT_YET_RUN_ON_FINAL_EXACT_HEAD
A006_SCHEMA_VALIDATE = NOT_YET_RUN_ON_FINAL_EXACT_HEAD
A006_RUFF = NOT_YET_RUN_ON_FINAL_EXACT_HEAD
A006_MYPY = NOT_YET_RUN_ON_FINAL_EXACT_HEAD
CI_STATUS = QUALIFICATION_PENDING
```

If a fresh exact-head hosted job fails before any step, that result is infrastructure-block evidence, not a test failure and not merge authority. If the repository-authorized qualification steps execute, only their exact results may be recorded as PASS/FAIL.

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

A006 remains unchecked in `tasks.md`. It cannot become `COMPLETE_CANONICAL`, unblock B023, or authorize dependent work merely because the implementation exists on a branch. Exact-head qualification, review, mandatory premerge verification, guarded merge, post-merge proof, and separate closeout remain required.
