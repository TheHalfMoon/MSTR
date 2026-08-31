# A017 — Failure Taxonomy and Training Trajectory Contract

**Task:** `A017`
**State:** IMPLEMENTATION_CANDIDATE
**Canonical base:** `0bd69861b987c616e1b9b25ef88a5d14f4762788`
**Feature branch:** `feat/000a-a017-trajectory-contract`

## Scope

A017 freezes `mstr.trajectory-manifest.v0`, `mstr.failure-taxonomy.v0`, and the
training-admission boundary consumed later by A018 and MSTR-000B B023. It does
not record trajectories, replay event logs, execute verifiers, derive verifier
health classes, run a model, or train weights.

The trajectory contract binds exact run identity, event-log schema/hash/count,
terminal class, verifier result identity, verifier-health input, failure taxonomy,
recovery count, authority violations, contamination state, admission label, and
provenance/privacy posture.

## Terminal classes

```text
VERIFIED_SUCCESS
RECOVERED_SUCCESS
FAILED_VALID
TIMEOUT_VALID
INVALID_ENVIRONMENT
INVALID_VERIFIER
CONTAMINATED
LEAKAGE_DETECTED
AUTHORITY_VIOLATION
```

Verified success cannot hide failure/recovery evidence. Recovered success requires
both a recorded failure class and at least one recovery. Timeout, invalid
environment, invalid verifier, and authority-violation terminal states bind their
corresponding failure evidence. Invalid/contaminated/leaked/authority-violating
runs are rejected from training admission.

## Failure taxonomy

`mstr.failure-taxonomy.v0` freezes the 18 classes required by FR-A024:

```text
WRONG_LOCALIZATION
BAD_ASSUMPTION
STALE_FILE
BAD_PATCH
SYNTAX_ERROR
TYPE_ERROR
BUILD_FAILURE
TEST_FAILURE
DEPENDENCY_FAILURE
TOOL_ERROR
TIMEOUT
INCOMPLETE_IMPLEMENTATION
OVEREDIT
REGRESSION
FAKE_COMPLETION
AUTHORITY_VIOLATION
ENVIRONMENT_FAILURE
VERIFIER_FAILURE
```

Failed and timeout trajectories remain representable as evidence and may enter
explicit preference/RL-evidence lanes only when the declared verifier-health stage
posture permits it. They cannot become clean-positive SFT examples.

## Verifier-health binding

A017 consumes the canonical B022 `mstr.verifier-health.v0` record boundary without
implementing the B023 evaluator/classifier.

```text
B022_STATE = COMPLETE_CANONICAL
B022_IMPLEMENTATION_MERGE = 97bf66a98bad51ff0d574d90a04fa47b802708ee
A017_DERIVES_HEALTH_CLASS = NO
B023_HEALTH_CLASSIFIER_AUTHORITY = PRESERVED
```

Any training-admitted trajectory requires a `verifier_health_binding` whose task
and verifier-manifest identities match the exact run identity. Clean-positive SFT
requires:

```text
health_class = HEALTHY
stage_admission_class = CLEAN_POSITIVE_ELIGIBLE
terminal_class = VERIFIED_SUCCESS | RECOVERED_SUCCESS
contamination_status = CLEAR
authority_violations = []
```

`PARTIAL` and `DISAGREEMENT` cannot claim clean-positive eligibility. `BROKEN`,
`LEAKED`, and `TAMPERED` are blocked from training admission. The binding records
B022/B023 output; A017 does not manufacture or recalculate it.

## Privacy, provenance, and authority

The v0 contract fails closed for incomplete/unresolved provenance, incompatible or
unresolved rights, detected secrets, contamination, and authority violations.
`PRIVATE_USER_REPOSITORY` and `PRODUCTION_TRACE` sources are rejected from training
admission in v0; a future governed opt-in policy would require an explicit contract
migration rather than an inferred exception.

## Candidate outputs

```text
schemas/mstr-trajectory-manifest-v0.schema.json
specs/001-agent-harness-verified-loop-foundation/contracts/trajectory-manifest.schema.json
artifacts/manifests/mstr-failure-taxonomy-v0.json
tests/fixtures/schemas/valid/mstr-trajectory-manifest-v0.json
tests/fixtures/schemas/invalid/mstr-trajectory-manifest-v0.json
tests/contract/test_trajectory_contract.py
src/mstr_qualify/schemas.py
tests/contract/test_schemas.py
tests/integration/test_cli_offline.py
evidence/mstr-000a/A017-trajectory-contract.md
```

`tasks.md` is intentionally unchanged in the implementation candidate. A017 may
be marked complete only after governed implementation merge, successful post-merge
proof, and a separate closeout.

## Prior canonical prerequisite

A016 is `COMPLETE_CANONICAL` on the entry main. Its first post-closeout proof run
`33438200600` failed because the evidence workflow asserted a stale text spelling;
that failure remains preserved. The repaired fresh proof run `33438264767` is
`SUCCESS` across identity, quality, and immutable complete recheck.

## Preserved A017 qualification failures

```text
33439438385 = FAILURE / syntax collection / generated indentation defect
33439766350 = FAILURE / full-suite frozen CLI schema list missing A017 registration
```

Both failures remain evidence and are not reused as PASS.

## Authority containment

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
VERIFIER_EVALUATOR_EXECUTION = NONE
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
A018_TRAJECTORY_RECORDER_REPLAY_ADMISSION = NOT_IMPLEMENTED_BY_A017
B023_VERIFIER_HEALTH_EVALUATOR = NOT_IMPLEMENTED_BY_A017
```
