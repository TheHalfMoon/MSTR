# A018 — Trajectory Recorder, Replay, and Admission

**Task:** `A018`
**State:** `COMPLETE_CANONICAL`
**Canonical base:** `f222df1b939fc5db792021d6883d977014502dba`
**Feature branch:** `feat/000a-a018-trajectory-factory`

## Scope

A018 implements the deterministic trajectory factory that consumes the already
canonical A003 event log/replay, A006 protected finalizer semantics, A017
`mstr.trajectory-manifest.v0` contract, and B022 verifier-health record contract.

A018 does not execute a model, execute a verifier evaluator, derive verifier-health
classes, access model weights, run training, use a network, ingest private-user
repositories, ingest production traces, or grant any external-effect authority.

## Recorder and replay

The recorder replays every event through the A003 hash-chain validator before
constructing a trajectory manifest. It binds:

```text
run identity
event count
canonical complete-event-log SHA-256
terminal class
verifier result identity
recovery evidence count
failure classes
authority violations
contamination state
provenance/privacy posture
verifier-health stage binding
training-admission decision
```

The complete event-log digest is SHA-256 over deterministic compact JSON of the
full replayed event sequence with sorted keys and `ensure_ascii=True`. Replay
recomputes that digest and rejects event tampering, sequence/hash-chain failure,
run-identity mismatch, terminal mismatch, verifier-result mismatch, recovery-count
mismatch, and manifest-contract failure.

Successful trajectories must end in a `run.completed` event authored by
`source=verifier`. The terminal class and verifier-result identity are taken from
that protected event; callers cannot override them.

Non-success trajectories must end in `run.failed` or `run.escalated` and carry an
explicit A017 non-success terminal classification. Failure semantics remain
validated by the frozen A017 schema.

## Recovery evidence

`recovery_count` is derived deterministically from replay evidence. It records the
maximum of:

```text
explicit recovery.started count
verifier identities that transitioned from an earlier non-PASS result to final PASS
```

This preserves recovered-success evidence whether recovery is represented by the
explicit recovery vocabulary or by the protected finalizer's verifier-history
recovery semantics.

## Verifier-health consumption

A018 validates the supplied full `mstr.verifier-health.v0` record offline and binds
exactly one requested training stage. The health record must match the trajectory's
task-manifest and verifier-manifest identities.

A018 does not manufacture or recalculate:

```text
health_class
training_stage_eligibility
stage admission class
evaluator health
leakage health
mutation-test health
```

Those remain B022/B023 evidence responsibilities.

## Training-admission policy

The A018 policy is fail-closed and labels evidence only; it grants no authority to
perform training.

Clean-positive SFT requires all of:

```text
terminal = VERIFIED_SUCCESS | RECOVERED_SUCCESS
protected verifier proof present
health_class = HEALTHY
stage_admission_class = CLEAN_POSITIVE_ELIGIBLE
provenance_status = COMPLETE
rights_status = COMPATIBLE | NOT_APPLICABLE
secret_scan_status = CLEAR | NOT_APPLICABLE
contamination_status = CLEAR
authority_violations = []
```

Valid failure/timeout evidence may enter an explicitly requested preference or
RL-evidence lane only when the selected verifier-health stage is not blocked and is
`CLEAN_POSITIVE_ELIGIBLE` or `RESEARCH_DIAGNOSTIC_ONLY`.

Hard rejection applies to invalid environment/verifier, contamination, leakage,
authority violation, unresolved/incompatible provenance or rights, detected
secrets, blocked verifier health, and private/production trace sources.

`EVAL_ONLY` remains an explicit no-training lane.

## Privacy boundary

`PRIVATE_USER_REPOSITORY` and `PRODUCTION_TRACE` are always labelled `REJECTED`
for training in v0. In addition, the bundle recorder refuses to persist those
sources at all:

```text
PRIVATE_USER_REPOSITORY -> REJECTED + NOT_INGESTED
PRODUCTION_TRACE        -> REJECTED + NOT_INGESTED
```

A future opt-in policy requires a governed contract migration; there is no inferred
exception.

## Deterministic bundle storage

Repository-owned/public/synthetic governed evidence may be stored as a stable JSON
bundle containing:

```text
manifest
events
```

Loading the bundle always re-runs schema validation, event replay, digest binding,
run identity, terminal binding, verifier-result binding, and recovery binding.
Round-trip serialization is deterministic.

## Candidate outputs

```text
src/mstr_qualify/trajectory/__init__.py
src/mstr_qualify/trajectory/admission.py
src/mstr_qualify/trajectory/recorder.py
tests/unit/trajectory/test_trajectory_factory.py
evidence/mstr-000a/A018-trajectory-factory.md
```

`specs/001-agent-harness-verified-loop-foundation/tasks.md` was intentionally
unchanged by the implementation PR. A018 is marked complete only through this
separate closeout after the governed implementation merge and successful
post-merge proof.

## Test intent

The focused tests cover:

```text
clean verifier-proven SFT admission
training rejection without verifier-health input
untrusted successful completion rejection
valid failure preference evidence
private-user trace rejected and not persisted
event tamper rejection
event-log digest mismatch rejection
verifier-health identity mismatch rejection
recovered-success replay/accounting
timeout semantic rejection
deterministic bundle round trip
```

## Authority containment

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_EVALUATOR_EXECUTION = NONE
VERIFIER_HEALTH_DERIVATION = NONE
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
A019_CONVERGENCE_EXECUTION = NOT_AUTHORIZED_BY_A018
B023_VERIFIER_HEALTH_EVALUATOR = NOT_IMPLEMENTED_BY_A018
```

## Canonical implementation lifecycle

The complete immutable A018 implementation evidence chain is:

```text
FINAL_FEATURE_HEAD = fc04967b2cbe874489f3b09a38fb80c1650f2461
FINAL_FEATURE_TREE = 047b1b36bd83ce6fbfd52de97e3e38fa52db7d32
IMPLEMENTATION_PR = 122
FAILED_QUALIFICATION_1 = 33490868295 / FAILURE / RUFF_UP035_IMPORT_LOCATION / PRESERVED
FAILED_QUALIFICATION_2 = 33491198294 / FAILURE / MYPY_NO_ANY_RETURN / PRESERVED
FINAL_QUALIFICATION = 33491507890 / SUCCESS
INDEPENDENT_REVIEW = 5076280749 / NO_BLOCKING_FINDING
MANDATORY_PREMERGE = 33491799986 / SUCCESS
IMPLEMENTATION_MERGE = b34a17441c24712144ce21b64c41ec18eeb12352
IMPLEMENTATION_MERGE_TREE = 047b1b36bd83ce6fbfd52de97e3e38fa52db7d32
IMPLEMENTATION_MERGE_PARENT_1 = f222df1b939fc5db792021d6883d977014502dba
IMPLEMENTATION_MERGE_PARENT_2 = fc04967b2cbe874489f3b09a38fb80c1650f2461
POST_MERGE_PROOF = 33492060094 / SUCCESS
A018_STATE = COMPLETE_CANONICAL
A019_STATE = PENDING_CONVERGENCE_GATED
```

The first failed qualification reached the A018 focused tests, offline schema
validation, and full pytest successfully before Ruff reported `UP035`. The second
failed qualification passed the focused tests, schema validation, full pytest, and
Ruff before strict mypy reported `no-any-return`. Neither failed run is reused as
PASS evidence.

The final exact-head qualification `33491507890` re-proved exact identity/scope,
11 focused A018 tests, offline schema validation, 1074 full tests, Ruff, strict
mypy, and the immutable candidate/main recheck. Independent exact-head review
`5076280749` found no blocking defect. Mandatory premerge run `33491799986` then
succeeded on the same implementation head.

The guarded implementation merge `b34a17441c24712144ce21b64c41ec18eeb12352`
has the exact final feature tree and parents shown above. Post-merge proof
`33492060094` re-proved merge identity/topology, PR/evidence identity, the focused
A018 tests, offline schema validation, the full test suite, Ruff, strict mypy, and
the final immutable canonical-main identity.

This closeout changes only A018 evidence/task state. It does not satisfy or bypass
A019/A020 convergence prerequisites, implement B023 verifier-health evaluation, or
grant any model-weight, training, paid-compute, data-ingestion, RL, or release
authority.

> `COMPLETE_CANONICAL` becomes canonical only if this exact two-file closeout head
> is itself freshly qualified, independently reviewed, mandatory-premerge verified,
> guarded-merged with the expected head SHA, and successfully post-closeout proven
> on canonical `main`.
