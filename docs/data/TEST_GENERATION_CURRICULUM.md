# MSTR Test Generation Curriculum v0

**Task:** `B024`
**Contract:** `mstr.test-generation-example.v0`
**Status:** implementation candidate — not canonical until governed merge and closeout

## Purpose

This curriculum makes test generation a first-class software-building skill without allowing generated tests to certify themselves. An admitted example must bind the generated test artifact to exact provenance, rights, contamination, verifier-health, protected-path, and behavioral evidence. A green test command by itself is never sufficient.

B024 is contract-and-fixture work only. It does not generate tests with a model, execute an external verifier, ingest a corpus, access model weights, call a teacher/API, spend money, or authorize training.

## Required learning sequence

The default bug/repair sequence is:

```text
UNDERSTAND_EXPECTED_BEHAVIOR
-> CREATE_MINIMAL_REPRODUCTION
-> PROVE_CURRENT_FAILURE
-> IMPLEMENT_FIX
-> RUN_TARGETED_REGRESSION
-> EXPAND_BOUNDARY_PROPERTY_OR_METAMORPHIC_VERIFICATION_WHEN_RISK_JUSTIFIES_IT
-> PRESERVE_EXACT_TEST_ARTIFACT_IDENTITY_ACROSS_PRE_FIX_AND_POST_FIX_PROOF
```

The generated test is evidence only when the exact same test artifact is used for the before/after comparison.

## Test classes

Every example declares one or more semantic classes:

```text
REPRODUCTION
TARGETED_REGRESSION
BOUNDARY_ERROR
PROPERTY
METAMORPHIC
```

`requires_reproduction=true` requires `REPRODUCTION`. When property/metamorphic testing is applicable, at least one of `PROPERTY` or `METAMORPHIC` is required. These classes are semantic requirements, not file-name labels.

## Per-example integrity

Every `mstr.test-generation-example.v0` record binds:

- exact task identity, base revision, and fix revision;
- a behavior contract and declared test classes;
- generated test patch SHA-256 and test artifact SHA-256;
- changed/test paths plus any deleted-test or protected-path changes;
- generated-test provenance, explicit completeness state, immutable lineage, and generator identity for generated source classes;
- a concrete rights decision for MSTR training/evaluation use;
- benchmark/hidden-answer/future-history/cross-split contamination evidence;
- pre-fix and post-fix execution evidence;
- environment and verifier-manifest identity;
- answer-encoding, test-weakening, evaluator-modification, and protected-path checks;
- optional mutation-strength evidence;
- exact verifier-health binding across health-record id, task identity, executed verifier manifest, and class;
- deterministic admission decision and reasons.

## Behavioral proof

### Default repair proof

`FAIL_BEFORE_PASS_AFTER` requires:

```text
PRE_FIX = FAIL
POST_FIX = PASS
SAME_TEST_ARTIFACT_SHA256 = true
SAME_ENVIRONMENT_IDENTITY = true
SAME_VERIFIER_MANIFEST_ID = true
PRE_FIX_REVISION = BASE_REVISION
POST_FIX_REVISION = FIX_REVISION
BASE_REVISION != FIX_REVISION
```

A test that passes before and after a claimed fix is not accepted under this proof mode.

### Task-specific proof

Some valid test-authoring work has no meaningful broken pre-fix state. `TASK_SPECIFIC_BEHAVIOR` is therefore allowed only when post-fix behavior passes and an independent acceptance-evidence identity is present. This exception cannot bypass rights, contamination, verifier health, protected paths, answer-encoding, or test-weakening gates.

## Fail-closed admission

`ADMIT` requires all of the following:

```text
RIGHTS_DECISION = COMPATIBLE
BENCHMARK_OVERLAP = CLEAR
HIDDEN_ANSWER_EXPOSURE = CLEAR
FUTURE_HISTORY_EXPOSURE = CLEAR
CROSS_SPLIT_DUPLICATE = CLEAR
VERIFIER_HEALTH_CLASS = HEALTHY
ANSWER_ENCODING = CLEAR
TEST_WEAKENING = CLEAR
EVALUATOR_MODIFICATION = CLEAR
PROTECTED_PATH_STATUS = INTACT
DELETED_EXISTING_TEST_PATHS = []
PROTECTED_PATH_CHANGES = []
MUTATION_STRENGTH = ADEQUATE | NOT_APPLICABLE
ADMISSION_REASONS = []
```

Any incompatible/unresolved right, contamination signal, unhealthy verifier, protected evaluator change, answer encoding, weakened/deleted tests, weak/unresolved mutation evidence, or invalid behavioral proof fails closed.

## Rejected shortcut patterns

The contract rejects clean-positive admission for examples that:

- hardcode or encode the expected answer into tests;
- delete or weaken existing tests to obtain green output;
- modify protected evaluator/verifier paths;
- use a different generated test before and after the fix;
- compare different execution environments or verifier manifests;
- claim a reproduction while never observing the pre-fix failure;
- pass both before and after under `FAIL_BEFORE_PASS_AFTER`;
- claim a repair while `base_revision` and `fix_revision` are identical;
- use task-specific proof without independent acceptance evidence;
- carry unresolved provenance, rights, contamination, or verifier health.

## Relationship to verifier health

B023 is canonical before B024 entry. B024 records an exact verifier-health binding but does not create a second health authority and does not execute the B023 evaluator. Downstream admission must consume canonical verifier-health evidence and may not infer `HEALTHY` from a passing test process alone.

## Non-authorities

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TEST_GENERATION_EXECUTION = NONE
VERIFIER_EXECUTION = NONE
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
```

B024 freezes test-generation curriculum and acceptance semantics only. It never converts a generated test, passing command, fixture, or model output into project authority.
