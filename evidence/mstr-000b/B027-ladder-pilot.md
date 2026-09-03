# B027 — Research Ladder Pilot Evidence

**Task:** `B027`
**Implementation PR:** #141
**Final implementation head:** `b5e152552f3b840fd74f2fe9b092eca17b56a91d`
**Canonical implementation merge:** `f667226dbf6cd380fefef5ff90fbc14eb1de3630`
**State:** COMPLETE_CANONICAL
**Canonical entry main:** `312d40eee8400a0dab94633f891b206f66a82855`
**Campaign:** `b027-offline-ladder-pilot-v0`

## Entry gate

```text
ENTRY_GATE_TASK = B027
ENTRY_GATE_CANONICAL_MAIN = 312d40eee8400a0dab94633f891b206f66a82855
ENTRY_GATE_ELIGIBLE = true
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

## Canonical Implementation Closeout

Within this closeout candidate, `COMPLETE_CANONICAL` is a prospective terminal state and B027 becomes canonical only when this exact closeout head is merged into canonical `main` through the required expected-head guard.
This closeout records terminal task/provenance state only. It does not rerun or mutate the frozen
campaign, evaluator, schemas, promotion policies, material-result records, model/runtime surfaces,
or any authority artifact.

- implementation PR: `#141`
- final implementation head: `b5e152552f3b840fd74f2fe9b092eca17b56a91d`
- canonical implementation merge: `f667226dbf6cd380fefef5ff90fbc14eb1de3630`
- evaluator-affecting regeneration: run `33757330474` — SUCCESS
- exact-head qualification: run `33758435956` — SUCCESS
- exact-range independent review: CodeRabbit reviewed base `312d40eee8400a0dab94633f891b206f66a82855`, head `b5e152552f3b840fd74f2fe9b092eca17b56a91d`, tree `20e60c673a203e3fc7f09da817ffc6ad64ac5f76`, 32 commits, and 60 changed files — NO ACTIONABLE COMMENTS
- mandatory exact-head pre-merge verification: run `33760082781` — SUCCESS
- real-main post-merge canonical verification: run `33761211923` — SUCCESS

Post-merge verification validated both B027 experiment records with full
`mstr.research-experiment.v2` semantics against real merged `main`, proved the campaign commits are
canonical ancestors, re-proved clean task drift and the pre-closeout B027 frontier, reran focused
and full quality gates, and preserved the zero-external-effect boundary. L0 remains the exact
`PROMOTE` result and L1 remains the exact controlled `STOP` on `code_proxy_thresholds`; L2/L3/L4
remain unexecuted. The premerge ledger fields such as `PENDING_POST_MERGE_VALIDATION` are immutable
historical candidate metadata and are not rewritten post hoc. Canonical implementation acceptance
is established by the guarded implementation merge and real-main post-merge proof. Terminal B027
closeout acceptance is recorded only when this exact closeout head is merged into canonical `main`
through the required expected-head guard.

This closeout grants no model-weight access, model execution, teacher/API execution, paid compute,
network model/teacher calls, data ingestion, verifier external effects, training/RL, Q4 execution,
or production release authority. B011, B013, B029, B030, and B031 remain governed by their own
canonical states and unresolved bindings.
