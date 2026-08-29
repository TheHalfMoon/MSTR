# B021 — Fixture-Only Frontier Sampler/Calibrator Evidence

**Task:** `B021`
**Implementation PR:** #83
**Final implementation head:** `6211a8f2ccf2613f2e988ce230c7d432877b1aff`
**Canonical implementation merge:** `613449e0f1b23eaef7dcb702ba2636a157816d26`
**State:** COMPLETE_CANONICAL
**Canonical entry main:** `641e13033b00451ea4b81063640e4066a8c7389d`

## Canonical Entry Provenance

```text
ENTRY_GATE_TASK = B021
ENTRY_GATE_CANONICAL_MAIN = 641e13033b00451ea4b81063640e4066a8c7389d
ENTRY_GATE_RUN = 33235627751
ENTRY_GATE_JOB = 99055993292
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

The entry gate proved B020 terminal `COMPLETE_CANONICAL`, B021 `PENDING` and `eligible=true` with no external authority required, canonical drift clean across all 34 MSTR-000B tasks, B011 still blocked, and the canonical baseline quality gates green.

## Fixture Frontier Semantics

B021 consumes records validated against `mstr.difficulty-calibration.v0`. It does not replace the B020 contract and it does not infer a universal difficulty class from solve probability.

The fixture sampler maps the already-calibrated classes into explicit curriculum lanes:

```text
INVALID                 -> REJECTED_INVALID / weight 0
CURRENTLY_UNPRODUCTIVE   -> DEFERRED / weight 0
TOO_EASY                 -> STABILITY_REPLAY
LEARNABLE_FRONTIER       -> PRIMARY_FRONTIER
HARD_FRONTIER            -> HARD_FRONTIER
```

Repository-owned regression, core FIM, and core direct-code anchors remain explicit replay anchors when otherwise sampleable. Sampling weights are provided by an explicit `FixtureSamplingPolicy`; the implementation encodes no default weights and no probability-to-class thresholds.

The deterministic sampler uses smooth weighted scheduling only over entries with positive fixture weights. `INVALID` and deferred currently-unproductive cells cannot enter its plan.

## Checkpoint Refresh Proof

The repository fixture contains the same task/family set at two synthetic checkpoint identities under the same frozen harness and sampling identity. Refresh requires:

- a new checkpoint identity;
- new difficulty-record identities;
- advancing calibration times;
- the same model, harness, sampling identity, task/family set, and curriculum roles.

The fixture demonstrates tasks moving from learnable frontier to replay, hard frontier to learnable frontier, and currently-unproductive to hard frontier after the synthetic checkpoint changes. This is a contract/policy demonstration only; no student model is executed.

A regression test also assigns the same `estimated_solve_probability=0.5` to two records with different frozen B020 classes and proves they route to different lanes. This prevents B021 from silently hard-coding a universal probability threshold that B020 deliberately left unfrozen.

## Fixture Boundary

Accepted source classes are restricted to:

```text
REPOSITORY_OWNED_FIXTURE
SYNTHETIC_VERIFIED
```

The pilot does not read a public repository, external dataset, model artifact, teacher service, production trace, private user data, or network model endpoint.

## Authority

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
REAL_CHECKPOINT_CALIBRATION = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
B021_AUTHORITY = REPOSITORY_OWNED_FIXTURE_FRONTIER_CALIBRATION_AND_SAMPLING_ONLY
```

## Canonical Implementation Closeout

The fixture-only frontier sampler/calibrator was merged and verified on canonical main without executing a model, calibrating a real checkpoint, accessing weights, or widening any external-effect authority.

- implementation PR: `#83`
- final implementation head: `6211a8f2ccf2613f2e988ce230c7d432877b1aff`
- canonical implementation merge: `613449e0f1b23eaef7dcb702ba2636a157816d26`
- atomic implementation build: run `33235980087` — SUCCESS
- exact-head qualification: run `33236137441` — SUCCESS
- exact-head formal review: review `5057065431` — NO BLOCKING FINDINGS
- mandatory pre-merge verification: run `33236949430` — SUCCESS
- post-merge implementation verification: run `33237180697` — SUCCESS

This closeout changes only canonical task/provenance state and terminal-behavior regression assertions. It grants no model-weight access, model execution, real checkpoint calibration, teacher/API use, paid compute, network model calls, large/private/production data ingestion, weight-changing training, large-scale RL, or production release authority. B011 remains blocked.
