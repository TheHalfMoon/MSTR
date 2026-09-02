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
- frozen evaluator: `sha256:7555257171e97989a007248a7ef90c77e8cd7f0cec230d36c7ded14d824fb1ab`
- full ledger: `artifacts/results/research/B027/campaign-ledger.json`
- L0 registry SHA-256: `156bd0c384e7aa288a418873dc3f3dfdea17d71574d54c443760b266cd948c32`
- L1 registry SHA-256: `87dcf83813203a960d7ba482409264baba27328d77622c61f13aa36bd9673633`

The L1 record consumes the exact L0 promoted result through the immutable predecessor registry
binding. Promotion policies precede their evidence commits, gate observations are derived from
content-addressed verifier results, and the same frozen evaluator identity is used across both
levels.

## Campaign commit ledger

```text
L0_POLICY_FREEZE = 361779333904362e456d99389dd64ec78306643b
L0_EVIDENCE = b644f07801cd46439a7fc2844429a62c7ace6058
L0_REGISTRY = 752886267bc25f67c9fb7aaf1d2b6f4a5383ee5d
L1_POLICY_FREEZE = 77f328f5eadbe7a3e2bcabf5485a82c961a61148
L1_EVIDENCE = ab091ef59e98e5e18b823acaec39b03bd94e662c
L1_REGISTRY = a9428c0e34a44169a8b7b5898f8dbb1f961a9a52
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
