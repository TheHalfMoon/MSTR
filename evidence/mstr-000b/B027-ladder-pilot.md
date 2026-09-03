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
- frozen evaluator: `sha256:b6f3d060a7cb48a7d34d5d98fb1e3687df1dd2becc7dcee29ea71de2cc5dc398`
- full ledger: `artifacts/results/research/B027/campaign-ledger.json`
- premerge canonical-history status: `PENDING_POST_MERGE_VALIDATION`
- premerge validation kind: `PROSPECTIVE_NO_CANONICAL_REF_REWRITE`
- L0 registry SHA-256: `dbc5f477ebd96d282ecdbd9ca1048e336c8289bcd9941d549656459ff155da90`
- L1 registry SHA-256: `ea9a28f53b68fd8a89898675f4f04c0843a7c4438aae955ded7c85c039645f79`

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
L0_POLICY_FREEZE = 743c9c6ba1d77f709ed3f039fa9703c82957c0a7
L0_EVIDENCE = 9ed2d0c16d96d912a07e3b2b11c9b04217a0e417
L0_REGISTRY = fda0e1cbd5436da8056a09252bc504722fa58ea1
L1_POLICY_FREEZE = 5ff7853c16eb789214b8aaa0d5d43d6d21b9fd68
L1_EVIDENCE = 3e7d7dcae5dd83f1b0d6aef862d9cb7773c921c0
L1_REGISTRY = b86b058936e5556397e74e1c38aa29df34e39225
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
