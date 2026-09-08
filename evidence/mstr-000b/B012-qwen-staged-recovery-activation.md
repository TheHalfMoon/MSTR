# B012 Qwen Staged Raw-Code Recovery Activation

## Exact repository identity

```text
ACTIVATION_BASE_MAIN = 0cff2d57ab78c0189c8557f3e2ec59300bd8082d
REPAIR_PACKAGE_MERGE_COMMIT = 0cff2d57ab78c0189c8557f3e2ec59300bd8082d
REPAIR_PACKAGE_POSTMERGE_RUN = 34177394009 / SUCCESS
REPAIR_PACKAGE_POSTMERGE_EVIDENCE_HEAD = 6e26a1bcaf844cd9a4ff100de54f116cdca77853
REPAIR_ID = B012_QWEN_RAW_CODE_STAGED_DURABILITY_REPAIR_2026_09_08
CANDIDATE_ID = qwen3.5-0.8b-control
PRIOR_QUALIFICATION_RUN_ID = 34155931982
```

## Activation change

The separately reviewed staged durability workflow is materialized byte-for-byte at `.github/workflows/b012-qwen-raw-code-recovery.yml`. The executor binding is restored to `SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL` and binds the exact repair manifest, staged executor, and active workflow SHA-256 identities.

The staged repair manifest intentionally remains `READY_FOR_SEPARATE_CANONICAL_ACTIVATION` because the staged executor requires that exact repair-package state while independently verifying canonical binding activation.

## Authority boundary

This repository-only activation performs no model access or model execution and creates no new dispatch/retry authority. It does not expand candidate identity, revision, files, network hosts, cost, retention, or output classes.

```text
MODEL_ACCESS_DURING_ACTIVATION = NONE
MODEL_EXECUTION_DURING_ACTIVATION = NONE
TRAINING = FALSE
WEIGHT_CHANGING_TRAINING = FALSE
PAID_COMPUTE = FALSE
PAID_MODEL_API = FALSE
CANDIDATE_EXPANSION = FALSE
REVISION_OR_FILE_EXPANSION = FALSE
RETRY_AUTHORITY_CREATED = FALSE
EXTERNAL_DISPATCH_AUTHORITY_CREATED = FALSE
PRODUCTION_RELEASE = FALSE
```

The exact issue-comment dispatch remains a later postmerge action under the existing canonical `B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION` envelope.
