# A006 — Protected Finalizer / Verifier Boundary Evidence

**Task:** `A006`  
**State:** `COMPLETE_CANONICAL`  
**Canonical entry main:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`  
**Implementation PR:** `#94`  
**Final implementation head:** `3efd9f902746a1e6248f8bfee21bbe4a4f4db76b`  
**Canonical implementation merge:** `1fc07252dcad95c7f1377c76fa8ab9f9da3dd7f2`

## Entry Gate

A006 is model-independent early-safe MSTR-000A work. Its canonical entry state proved:

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

## Canonical Implementation

The protected finalizer:

- replays and validates the complete `mstr.run-event.v0` schema/hash/predecessor chain before making a decision;
- rejects mixed run identities and pre-existing terminal history;
- requires the latest `run.stop_proposed` to be authored by `model` or `harness`;
- allows only verifier lifecycle events after the latest stop proposal, so any later edit/tool/context/recovery/state mutation requires a new stop proposal;
- accepts `verifier.result` authority only from `source=verifier`;
- requires configured verifier ids to be non-empty, unique, canonical, and present;
- rejects surrounding whitespace in configured verifier ids, event verifier ids, and result identities rather than silently rewriting exact evidence identities;
- requires a fresh post-stop result from every required verifier and requires each latest status to be `PASS`;
- rejects malformed statuses, missing/stale verifier evidence, spoofed sources, hash-chain tamper, and duplicate verifier configuration;
- derives `VERIFIED_SUCCESS` or `RECOVERED_SUCCESS` mechanically rather than accepting a caller-selected terminal class;
- computes the terminal aggregate identity from the exact final required verifier result identities;
- emits `run.completed` only as a verifier-authored, non-model-visible, hash-chained event;
- exposes no model/harness/caller path that can self-author canonical success.

## Security Hardening Proven

Two independent review findings were repaired before merge.

### Post-stop freshness

Schema-valid state mutation after the latest stop proposal is rejected even if a PASS result follows or precedes the mutation:

```text
run.stop_proposed -> edit.applied -> verifier.result PASS -> REJECT
run.stop_proposed -> verifier.result PASS -> edit.applied -> REJECT
```

Stable error:

```text
finalizer.post_stop_event_invalid
```

### Exact verifier identity

The earlier implementation normalized opaque verifier identities with `.strip()`. The final implementation uses canonical-or-reject semantics:

```text
REQUIRED_VERIFIER_ID_SURROUNDING_WHITESPACE -> REJECT
EVENT_VERIFIER_ID_SURROUNDING_WHITESPACE -> REJECT
RESULT_IDENTITY_SURROUNDING_WHITESPACE -> REJECT
EXACT_CANONICAL_IDENTITY -> PRESERVE_UNCHANGED
```

Dedicated security coverage is retained in:

```text
tests/security/test_finalizer_boundary.py
tests/security/test_finalizer_post_stop_boundary.py
tests/security/test_finalizer_identity_boundary.py
```

## Canonical Lifecycle Evidence

```text
IMPLEMENTATION_PR = 94
FINAL_IMPLEMENTATION_HEAD = 3efd9f902746a1e6248f8bfee21bbe4a4f4db76b
IMPLEMENTATION_TREE = 8ee03f71fbd632628dc6069fee842c146f9e753e
EXACT_HEAD_QUALIFICATION_RUN = 33306551501 / SUCCESS
EXACT_HEAD_REVIEW = 5060548795 / NO_BLOCKING_FINDINGS
MANDATORY_PREMERGE_RUN = 33306722605 / SUCCESS
CANONICAL_IMPLEMENTATION_MERGE = 1fc07252dcad95c7f1377c76fa8ab9f9da3dd7f2
POST_MERGE_VERIFICATION_RUN = 33306819921 / SUCCESS
```

The final exact-head qualification proved:

```text
FOCUSED_FINALIZER_SECURITY_TESTS = 30 passed
MSTR_QUALIFY_VALIDATE = PASS / 19 valid fixtures + 19 invalid fixtures
FULL_PYTEST = 900 passed
RUFF = PASS
MYPY = PASS / 32 source files
IDENTITY_SCOPE = PASS
FINAL_IMMUTABLE_RECHECK = PASS
```

Mandatory premerge independently re-proved the exact PR/head/tree, successful qualification, exact-head review, zero unresolved review threads, exact seven-file scope, and the complete frozen quality suite.

The canonical merge is an exact two-parent GitHub merge:

```text
PARENT_1 = 97904ac5ad17e7142e88944ee83dbb304ecb197f
PARENT_2 = 3efd9f902746a1e6248f8bfee21bbe4a4f4db76b
TREE = 8ee03f71fbd632628dc6069fee842c146f9e753e
SIGNATURE = VERIFIED
```

Post-merge run `33306819921` re-proved canonical merge identity/tree/parents, focused A006 tests, schema validation, full pytest, Ruff, mypy, and the exact `main` identity before this closeout.

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

This closeout changes only canonical task/provenance state. It does not modify A006 runtime behavior, schemas, governance, or any external-effect authority. A007 and every later task remain independently gated by their exact live prerequisites.
