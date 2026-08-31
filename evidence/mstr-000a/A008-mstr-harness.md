# A008 — H1 MSTR-Native Typed Harness Evidence

**Task:** `A008`  
**State:** `IMPLEMENTATION_ACTIVE / QUALIFICATION_PENDING`  
**Canonical entry main:** `f1e94e9c754e89a3584a391841599c05ed050d3e`

## Entry Gate

A008 is model-independent early-safe MSTR-000A work. Canonical entry truth proves:

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

H1 extends the canonical H0/A003-A006 spine rather than replacing it. Its candidate surface is:

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

The candidate counts consecutive failed tool/edit/verifier outcomes. At the configured threshold, another mutating/tool action is rejected until a recovery step records failure evidence and consumes the shared repair budget. Recovery remains inside the A005 state graph and does not create success authority.

## Compact State

H1 delegates compaction to canonical A004 `compact_agent_state()`. Critical failures, non-PASS verifier evidence, uncertainty, constraints, changed files, and remaining work retain A004 fail-closed semantics.

## Prefix/Cache Claim Boundary

Prefix/cache information remains `UNMEASURED` until an explicit runtime measurement is supplied. Estimated values are not admissible as measured evidence. H1 records measured token accounting only and does not claim runtime cache optimization from configuration or static inference.

## Protected Success Semantics

A008 does not alter A006. Builder/model/harness text still cannot author canonical success. Required verifier observations, fresh post-stop evidence, and A006 finalization remain the only normal success path.

## Qualification State

No exact-head PASS is claimed yet.

```text
A008_FOCUSED_PYTEST = NOT_EXECUTED
MSTR_QUALIFY_VALIDATE = NOT_EXECUTED
FULL_PYTEST = NOT_EXECUTED
RUFF = NOT_EXECUTED
MYPY = NOT_EXECUTED
CI_PASS = NOT_CLAIMED
A008_COMPLETE_CANONICAL = NO
MERGE_AUTHORITY = ABSENT
```

A008 remains unchecked in `tasks.md` until exact-head qualification, review, mandatory premerge verification, guarded merge, post-merge proof, and separate canonical closeout all succeed.
