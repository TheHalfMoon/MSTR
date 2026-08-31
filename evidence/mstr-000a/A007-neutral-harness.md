# A007 — H0 Neutral-Minimal Harness Evidence

**Task:** `A007`  
**State:** `IMPLEMENTATION_ACTIVE / QUALIFICATION_PENDING`  
**Canonical entry main:** `93bfb94d6b8f5949ea5ce125d780ef7f2b739c01`

## Entry Gate

A007 is model-independent early-safe MSTR-000A work. Canonical entry truth proves:

```text
A001 = COMPLETE_CANONICAL
A002 = COMPLETE_CANONICAL
A003 = COMPLETE_CANONICAL
A004 = COMPLETE_CANONICAL
A005 = COMPLETE_CANONICAL
A006 = COMPLETE_CANONICAL
A006_CLOSEOUT_MERGE = 93bfb94d6b8f5949ea5ce125d780ef7f2b739c01
A006_POST_CLOSEOUT_RUN = 33307274029 / SUCCESS
A007_CONFLICTING_OPEN_PR = NONE_FOUND
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

MSTR-000A has no machine-readable A-task gate catalog. A007 therefore follows the canonical manual exact-prerequisite rule already used for A005/A006. The live Spec001 ledger places A007 immediately after canonical A006.

## Minimal H0 Surface

The implementation deliberately exposes only:

```text
repository.read_utf8
repository.search_literal
shell.argv_no_shell
edit.whole_file_utf8
verifier.callback
```

It composes the existing canonical boundaries instead of creating replacements:

```text
A004 AgentState projection
+ A005 BuildLoop bounded state/budget control
+ A003 hash-chained run events
+ A006 protected finalizer
```

H0 does not implement model-specific scaffolding, context ranking, stale-safe edit transactions, prefix-cache optimization, autonomous recovery cadence, or WePLD routing. Those belong to later H1/H2 work.

## Repository Boundary

Read/search/edit paths are resolved relative to one configured workspace. Absolute paths, parent traversal that resolves outside the workspace, and symlink read/edit targets are rejected. Literal search is deterministic, sorted, bounded by an explicit match ceiling, and skips non-UTF-8 files.

The shell surface accepts argv only and never uses `shell=True`. The working directory is fixed to the workspace. A command runner can be injected for deterministic testing. A007 does not claim that this minimal shell API is a complete sandbox or environment admission boundary; A011-A014 own those later controls.

## Success Authority

H0 cannot turn model or harness text into canonical success.

A pre-stop verifier callback provides an actual observation so A005 may permit `run.stop_proposed`. That evidence is not reused for success. After STOP, H0 invokes the exact required verifier set again, appends fresh `source=verifier` lifecycle events, and delegates the terminal decision to A006 `finalize_run()`.

```text
PRE_STOP_VERIFIER_OBSERVATION
-> run.stop_proposed / canonical_success=false
-> FRESH_POST_STOP_VERIFIER_STARTED
-> FRESH_POST_STOP_VERIFIER_RESULT
-> A006 finalize_run
-> verifier-authored run.completed only if protected requirements pass
```

A post-stop FAIL/ERROR/UNKNOWN therefore cannot be overridden by a pre-stop PASS or by a completion claim in model text.

## Focused Coverage

Candidate tests cover:

```text
workspace-bounded UTF-8 read
literal deterministic search
path traversal rejection
symlink boundary rejection
argv-only shell runner identity
whole-file deterministic apply
AgentState projection from H0 events
hash-chain replay
pre-stop required-verifier observation
fresh post-stop verifier rerun
A006-only VERIFIED_SUCCESS
missing required verifier rejection
post-stop FAIL cannot reuse pre-stop PASS
verifier identity whitespace rejection
required verifier canonical/unique configuration
```

## Qualification State

No candidate-head quality result is claimed yet.

```text
A007_FOCUSED_PYTEST = NOT_EXECUTED
MSTR_QUALIFY_VALIDATE = NOT_EXECUTED
FULL_PYTEST = NOT_EXECUTED
RUFF = NOT_EXECUTED
MYPY = NOT_EXECUTED
CI_PASS = NOT_CLAIMED
A007_COMPLETE_CANONICAL = NO
MERGE_AUTHORITY = ABSENT
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

A007 remains unchecked in `tasks.md` until exact-head qualification, review, mandatory premerge verification, guarded merge, post-merge proof, and separate canonical closeout all succeed.
