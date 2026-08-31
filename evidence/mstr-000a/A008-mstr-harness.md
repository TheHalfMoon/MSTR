# A008 — H1 MSTR-Native Typed Harness Evidence

**Task:** `A008`
**State:** `COMPLETE_CANONICAL`
**Canonical entry main:** `f1e94e9c754e89a3584a391841599c05ed050d3e`
**Implementation merge:** `d6a2c83227be09b8cd37f62de0d8e841eba9854d`

> This terminal state is a closeout candidate until the dedicated closeout PR is itself qualified, reviewed, mandatory-premerge verified, guarded-merged, and post-closeout verified on canonical `main`.

## Entry Gate

A008 was model-independent early-safe MSTR-000A work. Canonical entry truth proved:

```text
A001-A007 = COMPLETE_CANONICAL
A007_CLOSEOUT_MERGE = f1e94e9c754e89a3584a391841599c05ed050d3e
A007_POST_CLOSEOUT_RUN = 33356184840 / SUCCESS
A008_CONFLICTING_OPEN_PR = NONE_FOUND
UNQUALIFIED_CANDIDATE_RESULT_REQUIRED = NO
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

## H1 Surface

H1 extends the canonical H0/A003-A006 spine rather than replacing it. Its surface is:

```text
repository.read_typed
repository.search_typed
shell.argv_typed_no_shell
edit.stale_safe_whole_file
context.explicit_selective_or_none
verifier.callback
recovery.bounded_cadence
state.compact
prefix_cache.measured_observation
```

The inherited untyped H0 read/search/shell/edit methods are not H1 tool endpoints. H1 rejects unchecked edit application and requires a caller-observed exact SHA-256 identity (or `ABSENT` for a new file) before apply.

## Stale-Safe Edit Boundary

H1 performs compare-before-apply against the exact file identity observed by the caller. If the workspace file changes before apply, H1 records `edit.rejected`, preserves the newer workspace content, and fails closed with `h1.edit_stale`.

This is an in-harness stale-base protection contract. It does not claim a cross-process filesystem transaction or replace the later A011-A014 environment/sandbox boundaries.

## Selective Context Boundary

H1 exposes only explicit context modes:

```text
NO_RETRIEVAL
EXPLICIT_PATHS
```

There is no implicit ranking/retrieval claim. Explicit paths are deterministic, unique, sorted for returned context, and bounded by file/character ceilings. `NO_RETRIEVAL` is a first-class decision and consumes no repository tool call.

## Recovery Cadence

The implementation counts consecutive failed shell/edit/verifier outcomes. At the configured threshold, another mutating shell/edit action is rejected until a recovery step records failure evidence and consumes the shared repair budget. Diagnostic read/search/context selection and verifier observation remain available so recovery evidence can be gathered. Recovery remains inside the A005 state graph and does not create success authority.

## Compact State

H1 delegates compaction to canonical A004 `compact_agent_state()`. Critical failures, non-PASS verifier evidence, uncertainty, constraints, changed files, and remaining work retain A004 fail-closed semantics.

## Prefix/Cache Claim Boundary

Prefix/cache information remains `UNMEASURED` until an explicit `MEASURED_RUNTIME` observation is supplied. Estimated values are not admissible as measured evidence. H1 records measured token accounting only and does not claim runtime cache optimization from configuration or static inference.

## Protected Success Semantics

A008 does not alter A006. Builder/model/harness text cannot author canonical success. Required verifier observations, fresh post-stop evidence, and A006 finalization remain the only normal success path.

## Hardening History

```text
33356550240 = FAIL / 13 passed, 2 test exception-type mismatches / NO PUSH
33356648455 = FAIL / 15 passed, Ruff E501 / NO PUSH
33356706025 = SUCCESS / 15 focused tests + Ruff + mypy / pushed 410ee515...
33356792075 = SUCCESS / full exact-head qualification on 410ee515... / HISTORICAL ONLY
33356928801 = SUCCESS / recovery-contract focused tests + Ruff + mypy / pushed final head 79af1ad...
```

No older-head PASS was reused after the candidate changed.

## Canonical Lifecycle Evidence

```text
IMPLEMENTATION_PR = 100
FINAL_IMPLEMENTATION_HEAD = 79af1ad6c68bbd6026037e49851428be4e650e5c
FINAL_IMPLEMENTATION_TREE = 7db8903dbea76655dc529a33bd32624e18a5dbf6
FINAL_EXACT_HEAD_QUALIFICATION = 33356994052 / SUCCESS
EXACT_HEAD_REVIEW = 5063104321 / COMMENTED / NO_BLOCKING_FINDING
UNRESOLVED_REVIEW_THREADS = 0
MANDATORY_PREMERGE = 33357151346 / SUCCESS
IMPLEMENTATION_MERGE = d6a2c83227be09b8cd37f62de0d8e841eba9854d
POST_MERGE_VERIFICATION_RUN = 33357267885 / SUCCESS
```

The final exact-head qualification, mandatory premerge verification, and post-merge proof each executed the applicable repository gates including:

```text
pytest -q tests/unit/harness/test_native.py tests/security/test_native_harness_boundary.py
mstr-qualify validate
pytest -q
ruff check src tests
mypy src
```

The guarded implementation merge preserved the exact candidate tree and had parents:

```text
parent1 = f1e94e9c754e89a3584a391841599c05ed050d3e
parent2 = 79af1ad6c68bbd6026037e49851428be4e650e5c
```

## Authority Boundary

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

A009 remains independently gated and is not made complete by this A008 closeout.
