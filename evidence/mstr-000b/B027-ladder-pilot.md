# B027 — Research Ladder Pilot Evidence

**Task:** `B027`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `312d40eee8400a0dab94633f891b206f66a82855`
**Campaign:** `b027-offline-ladder-pilot-v0`

## Entry gate

```text
TASK = B027
CANONICAL_MAIN = 312d40eee8400a0dab94633f891b206f66a82855
B026_STATE = COMPLETE_CANONICAL
B027_STATE = PENDING
B027_ELIGIBLE = true
EXTERNAL_AUTHORITY_REQUIRED = false
POST_B026_CLOSEOUT_PROOF = 33690094117
```

## Pilot result

The bounded repository-owned campaign exercised the frozen B026 ladder without model inference,
weight access, network model/teacher calls, paid compute, dataset ingestion, training, RL, Q4
execution, or release activity.

- L0 `b027-l0-contract-smoke`: `PROMOTE`
- L1 `b027-l1-controlled-stop`: `STOP`
- early-discard gate: `code_proxy_thresholds`
- L2/L3/L4: not executed after the L1 hard reject
- frozen evaluator: `sha256:3803e9ab85feed79523f3610b5e20e1cb286a20cf41db99de28e55475a2bcf5c`
- full ledger: `artifacts/results/research/B027/campaign-ledger.json`
- premerge canonical-history status: `PENDING_POST_MERGE_VALIDATION`
- premerge validation kind: `PROSPECTIVE_NO_CANONICAL_REF_REWRITE`
- L0 registry SHA-256: `578b478ff01110c8d4cb5fadbe85ba21df0afe62b442a64a4f31ba353ad0e692`
- L1 registry SHA-256: `1b99d5d3bdcb8ecbd7726f2da04730a150ce093b14a345583561c3739eebf671`

The L1 record consumes the exact L0 promoted result through the immutable predecessor registry
binding. Promotion policies precede their evidence commits, gate observations are derived from
content-addressed verifier results, and the same frozen evaluator identity is used across both
levels.

Premerge candidate validation never rewrites `refs/heads/main` or
`refs/remotes/origin/main` and does not claim that feature-only campaign commits are
already canonical. Full `mstr.research-experiment.v2` canonical-history semantic
validation is intentionally deferred to mandatory post-merge verification on real
`main`, where the campaign commits must actually be canonical ancestors.

## Campaign commit ledger

```text
L0_POLICY_FREEZE = a2b1b2e8faa5f9e42af0b260a3eaa6953288adad
L0_EVIDENCE = 500c3e144c4f7b504eb1bb721ff4dcd101147e07
L0_REGISTRY = 8e02b06320279ba5e4659d62456f60004f2b15f3
L1_POLICY_FREEZE = add2e228aa8326c90ff416fc90d03f360d987040
L1_EVIDENCE = 553565c8624341c165722dedc7d18eca614fb8a8
L1_REGISTRY = 3fcacd85baf8c8a2e947289db6130380ce39ff31
```

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
RESEARCH_CAMPAIGN_EXTERNAL_EFFECT = NONE
VERIFIER_EXTERNAL_EFFECT = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
Q4_EXECUTION = NONE
PRODUCTION_RELEASE = NONE
```

B027 remains `PENDING` in the canonical task ledger until this implementation is independently
qualified, reviewed, merged, post-merge verified, and separately closed out.
