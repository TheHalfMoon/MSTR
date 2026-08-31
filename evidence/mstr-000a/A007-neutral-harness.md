# A007 — H0 Neutral-Minimal Harness Evidence

**Task:** `A007`  
**State:** `COMPLETE_CANONICAL`  
**Canonical entry main:** `93bfb94d6b8f5949ea5ce125d780ef7f2b739c01`  
**Implementation PR:** `#98`  
**Final implementation head:** `65071b8469bc759d0951dc9b853c571013f6c295`  
**Canonical implementation merge:** `e28fea9132bc65fc6ba0cfdf13afc645d9fdd441`

## Canonical Scope

A007 provides the H0 neutral-minimal repository harness required by Spec001. Its surface is intentionally limited to:

```text
repository.read_utf8
repository.search_literal
shell.argv_no_shell
edit.whole_file_utf8
verifier.callback
```

It composes the existing canonical foundation rather than creating alternate authority:

```text
A003 hash-chained run events
+ A004 deterministic AgentState projection
+ A005 bounded BuildLoop state/tool control
+ A006 protected finalizer
```

H0 does not implement model-specific prompting, ranked/selective context, stale-safe edit transactions, prefix-cache optimization, autonomous recovery cadence, or WePLD routing. Those remain later H1/H2 responsibilities.

## Repository and Execution Boundary

Read/search/edit paths are workspace-relative and canonical-or-reject. Absolute paths, workspace escape, non-canonical aliases such as `a/../b`, and symlink read/edit rewrites are rejected rather than silently normalized.

Literal search is deterministic, sorted, explicitly bounded, and skips non-UTF-8 files. Shell execution accepts argv only, uses `shell=False`, fixes cwd to the configured workspace, and supports an injected deterministic runner for tests.

A007 does not claim that this minimal shell surface is the later environment/sandbox boundary. A011-A014 retain responsibility for environment reset/admission, verifier factory, reward-shortcut resistance, and effect-boundary hardening.

## Protected Success Semantics

H0 cannot convert model or harness text into canonical success.

A required verifier is observed before A005 may propose STOP, but that observation is not reused as terminal proof. After `run.stop_proposed`, H0 reruns the exact required verifier set, records fresh verifier-authored evidence, and delegates the terminal decision to A006 `finalize_run()`.

```text
PRE_STOP_VERIFIER_OBSERVATION
-> run.stop_proposed / canonical_success=false
-> FRESH_POST_STOP_VERIFIER_STARTED
-> FRESH_POST_STOP_VERIFIER_RESULT
-> A006 finalize_run
-> verifier-authored run.completed only when protected requirements pass
```

A fresh post-stop FAIL/ERROR/UNKNOWN therefore cannot be overridden by a pre-stop PASS or a model/harness completion claim.

## Security Hardening

The first qualified implementation head accepted an in-workspace path alias such as `a/../b`. It could not escape the workspace, but it could create more than one textual evidence identity for one file. The final candidate repaired this with canonical-or-reject path identity semantics and a dedicated regression before merge.

Historical qualification run `33353062949` applies only to pre-hardening head `0a55d5af972f51109c09dbad6d8cb5a373be0fbe` and is not reused as final-head evidence.

## Canonical Lifecycle Evidence

```text
IMPLEMENTATION_PR = 98
FINAL_IMPLEMENTATION_HEAD = 65071b8469bc759d0951dc9b853c571013f6c295
IMPLEMENTATION_TREE = 6f800c5a06deb72de79f147112c8446c149a1c5f
EXACT_HEAD_QUALIFICATION_RUN = 33353228503 / SUCCESS
EXACT_HEAD_REVIEW = 5062854172 / NO_BLOCKING_FINDINGS
MANDATORY_PREMERGE_RUN = 33353383561 / SUCCESS
CANONICAL_IMPLEMENTATION_MERGE = e28fea9132bc65fc6ba0cfdf13afc645d9fdd441
POST_MERGE_VERIFICATION_RUN = 33353512807 / SUCCESS
```

The implementation merge is an exact two-parent GitHub merge:

```text
PARENT_1 = 93bfb94d6b8f5949ea5ce125d780ef7f2b739c01
PARENT_2 = 65071b8469bc759d0951dc9b853c571013f6c295
TREE = 6f800c5a06deb72de79f147112c8446c149a1c5f
SIGNATURE = VERIFIED
```

Final-head qualification, mandatory premerge, and post-merge verification all executed the applicable frozen repository gates:

```text
pytest -q tests/unit/harness/test_neutral.py tests/security/test_neutral_harness_boundary.py
mstr-qualify validate
pytest -q
ruff check src tests
mypy src
```

Post-merge verification additionally re-proved exact merge identity, parents, tree, five-file implementation scope, and the implementation-only ledger state before this closeout.

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

This closeout changes only canonical task/provenance state. It does not modify A007 runtime behavior, schemas, governance, or any external-effect authority. A008 and every later task remain independently gated by live canonical prerequisites.
