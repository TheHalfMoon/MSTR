# B012 PR #174 Merge-Race Reconciliation

**Task:** `B012`

**Reconciliation base:** `a2b2788dd5a8a8d5f301359586f6b2019615b4a9`

**Historical repair PR:** `#174`

**Historical repair head:** `6290127080459879aa494efdb91aa44bc629a9fc`

**Historical repair tree / merged tree:** `2013b367c3163ab37170b28f611999b54e2dad1f`

**State:** `FORWARD_ONLY_GOVERNANCE_RECONCILIATION_CANDIDATE`

## Purpose

This artifact records a governance sequencing race around PR #174 without rewriting or upgrading historical evidence. The repair content was independently qualified and reviewed on its exact head, but the PR merged before its mandatory premerge workflow reached the final live-ref guard.

The failed final premerge guard remains a failure. It is not converted into a retrospective pass.

## Immutable Historical Truth

```text
PR = 174
REPAIR_BASE = 4d9e423f7fa2aa6d4f706d5c9ad61dafb24b2513
REPAIR_HEAD = 6290127080459879aa494efdb91aa44bc629a9fc
REPAIR_TREE = 2013b367c3163ab37170b28f611999b54e2dad1f
MERGE_COMMIT = a2b2788dd5a8a8d5f301359586f6b2019615b4a9
MERGED_AT = 2026-09-06T16:34:22Z
```

The merge commit has parent 1 equal to the expected repair base and parent 2 equal to the exact reviewed repair head. Its tree is exactly the reviewed repair tree.

## Premerge Evidence

The exact repair head had completed qualification and substantive review before merge:

```text
FINAL_EXACT_HEAD_QUALIFICATION_RUN = 34045379758
FINAL_EXACT_HEAD_QUALIFICATION = PASS
INDEPENDENT_REVIEW_RUN = 34045539668
INDEPENDENT_REVIEW = PASS
REVIEW_ID = 5125938059
REVIEW_FINDINGS = NONE
MODEL_ACCESS = NONE
TRAINING = false
PAID_COST_USD = 0.0
```

The mandatory premerge workflow was run `34045842975`.

Its immutable job conclusions are:

```text
canonical_eligibility = success
exact_head_gates = success
final_premerge = failure
workflow_conclusion = failure
```

The final job failed because `main` had already advanced to the PR #174 merge commit before the final expected-base guard completed. Therefore:

```text
PR174_MANDATORY_PREMERGE_FINAL_GUARD = FAILURE
RETROACTIVE_PREMERGE_PASS = PROHIBITED
```

This reconciliation does not claim that the merge complied with the intended ordering. It records that the merge happened first and preserves that ordering defect as historical governance evidence.

## Postmerge Canonical Verification

Postmerge run `34045909273` verified the merged repair on canonical `main` at `a2b2788dd5a8a8d5f301359586f6b2019615b4a9`.

The run established:

```text
EXACT_MERGE_TOPOLOGY = PASS
MERGED_TREE_EQUALS_REVIEWED_TREE = PASS
B012_SOURCE_SCRIPT_SHA256 = 890c9d1536ae4046a827789530c186dd02afca80bae8930ef22c2cb6e9ddcf26
B012_CANONICAL_ELIGIBILITY = PASS
B012_FOCUSED_TESTS = 7 passed
REPOSITORY_VALIDATION = PASS
FULL_PYTEST = 1374 passed
RUFF = PASS
FORMAT_CHECK = PASS
MYPY = PASS
FINAL_CANONICAL_MAIN_GUARD = PASS
MODEL_ACCESS = NONE
TRAINING = false
PAID_COST_USD = 0.0
```

The postmerge verifier explicitly materialized a local `main` ref at the exact canonical merge before running `mstr_qualify task eligible B012`, because the task gate requires canonical `refs/heads/main` semantics even when Actions initially checks out an immutable SHA in detached-HEAD mode.

A later diagnostic verifier, run `34046087930`, failed at `mstr_qualify task eligible B012` only because it invoked the task gate from detached HEAD without first materializing local `refs/heads/main`. That diagnostic does not contradict run `34045909273`; its topology and merge-race assertions had already passed, and it is retained as negative verifier-invocation evidence.

## Drift-Window B012 Execution Evidence

After PR #174 merged but before this reconciliation became canonical, an owner issue-comment dispatch started run `34046125440` for `mellum-4b` on canonical `main=a2b2788dd5a8a8d5f301359586f6b2019615b4a9`.

The run is historical drift-window evidence. It is not promoted to canonical B012 qualification evidence and it does not establish any model-quality verdict.

```text
RUN_ID = 34046125440
CANDIDATE = mellum-4b
WORKFLOW_CONCLUSION = failure
RESULT_CLASSIFICATION = B012_EXECUTION_FAILED_CLOSED
ERROR_TYPE = ExecutionError
ERROR = llama-bench timed out after 900s
STARTED_UTC = 2026-09-06T16:39:04Z
FAILED_UTC = 2026-09-06T17:14:10Z
CANONICAL_MAIN_AT_START = a2b2788dd5a8a8d5f301359586f6b2019615b4a9
ARTIFACT_ID = 9993670738
ARTIFACT_NAME = b012-mellum-4b-34046125440
ARTIFACT_ARCHIVE_SHA256 = d86c27d3d59d2903c3def289a21dedc2ac5625fe1db39542e27ea89be4f96999
MODEL_QUALITY_VERDICT = NONE
CANONICAL_B012_RESULT = false
TRAINING = false
PAID_COST_USD = 0.0
```

The durable failure artifact proves a bounded runtime timeout, not candidate quality. No score, promotion, admission, or rejection inference may be drawn from this run. A canonical retry is permitted only after this reconciliation becomes canonical, exact current-main B012 eligibility is re-established, and the existing Founder dispatch authority still binds the exact candidate/revision/file envelope.

## Governance Disposition

The safe forward-only disposition is:

1. Preserve mandatory premerge run `34045842975` as failed historical evidence.
2. Preserve PR #174 and merge `a2b2788...` as the immutable historical merge.
3. Bind the merged content to the successful exact-head qualification and independent review that preceded the merge.
4. Bind canonical postmerge correctness and current B012 eligibility to run `34045909273`.
5. Preserve drift-window Mellum run `34046125440` as `B012_EXECUTION_FAILED_CLOSED` timeout evidence and prohibit its use as canonical model-quality evidence.
6. Canonicalize this reconciliation through a new independently qualified and reviewed PR before any new B012 external-effect dispatch.
7. After this reconciliation is canonical, re-run `mstr_qualify task eligible B012` on exact current `main` immediately before each authorized B012 dispatch.
8. Do not transfer B012 authority to T031, B013, training, paid compute/model APIs, production release, new candidates, new revisions, or expanded files.

## Authority Boundary

This artifact creates no new Founder authority and authorizes no external effect by itself.

The only B012 execution authority remains the already-canonical exact Founder authorization for the exact B010 candidates and the canonical issue-comment dispatch boundary. This reconciliation neither expands that scope nor changes candidate/revision/file identities.

```text
NEW_CANDIDATES = false
REVISION_EXPANSION = false
FILE_EXPANSION = false
AUTHORITY_TRANSFER = false
TRAINING = false
WEIGHT_CHANGING_TRAINING = false
PAID_COMPUTE = false
PAID_MODEL_API = false
PRODUCTION_RELEASE = false
GIT_MODEL_BINARIES = 0
FOUNDER_MACHINE_MODEL_BINARIES = 0
```

## Required Closeout Gate

This reconciliation is not canonical merely because this file exists on a branch. It requires exact-head qualification, independent substantive governance review, review-thread reconciliation, mandatory premerge verification against exact live `main`, guarded expected-head merge, and postmerge verification before B012 execution resumes.
