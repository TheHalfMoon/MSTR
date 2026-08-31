# A015 — Direction-to-Done v0 Contract and Taxonomy

**Task:** `A015`
**State:** IMPLEMENTATION_CANDIDATE
**Canonical base:** `28a4a972182c0f58f7c6500239f625a0e2143d0a`
**Feature branch:** `feat/000a-a015-direction-to-done`

## Scope

A015 freezes the framework-neutral `mstr.direction-task.v0` record and the public
`MSTR-DIRECTION-TO-DONE-v0` taxonomy. It does not publish private/fresh benchmark
tasks, hidden acceptance payloads, model answers, future fixes, or verifier
implementation details.

The exact v0 task families are:

```text
TERSE_FEATURE_DIRECTION
MULTI_FILE_CONSTRUCTION
REPAIR
BUILD_TOOLING
BOUNDED_GREENFIELD
WEPLD_SPEC_DRIVEN
FAILURE_RECOVERY
SECURITY_SENSITIVE
```

## Contract boundary

Each direction task binds:

- exact task and repository revision;
- terse model-visible direction;
- environment and verifier manifest identities;
- allowed and prohibited effect classes;
- timeout and difficulty tags;
- task family;
- freshness/provenance state;
- a verifier-owned hidden acceptance identity/hash;
- B025 greenfield/feature extension identity where required;
- WePLD task identity for `WEPLD_SPEC_DRIVEN`;
- explicit recovery/security requirements.

The public repository contains contract fixtures and taxonomy metadata only.
`PRIVATE_FRESH` records are downstream-gated and cannot use the contract-fixture
execution posture.

## Offline validation integration

`mstr.direction-task.v0` is registered as a first-class local schema in
`SCHEMA_FILES` and the CLI schema-version map. Therefore both repository-wide
`python -m mstr_qualify validate` and explicit-file validation consume the same
runtime schema and canonical valid/invalid fixtures. The generic schema contract
tests bind the runtime schema byte-for-byte to the MSTR-000A design-source schema.

The first exact-head qualification run completed successfully for the earlier
seven-file candidate:

```text
33427721219 = SUCCESS / identity_scope + quality + complete
qualified_head = 8c3178156add4dff915a67427d1981f0996e894a
status_after_validation_integration = STALE_SUCCESS / NOT_REUSED_FOR_NEW_HEAD
```

That run remains valid historical evidence for its exact head, but it is not
reused as qualification evidence after the validation-integration repair.

The first qualification after validation integration then exposed one stale
full-suite expectation and is preserved as negative evidence:

```text
33428444420 = FAILURE / quality
identity_scope = SUCCESS
focused_contract_and_schema_tests = 111 PASSED
registered_offline_validate = PASS / 24 valid accepted / 24 invalid rejected
explicit_direction_task_validate = PASS
full_pytest = 1025 PASSED / 1 FAILED
failure = tests/integration/test_cli_offline.py::test_validate_self_checks_schemas_and_fixtures
reason = STALE_HARD_CODED_SCHEMA_INVENTORY_MISSING_MSTR_DIRECTION_TASK_V0
ruff = NOT_REACHED
mypy = NOT_REACHED
complete = SKIPPED
```

The failure was repaired by adding `mstr-direction-task-v0` to the expected
sorted offline schema inventory. No production behavior or authority boundary was
weakened. A fresh exact-head qualification is required after this repair.

## B025 reconciliation

A015 does not duplicate `mstr.greenfield-task.v0`.

For:

```text
TERSE_FEATURE_DIRECTION
MULTI_FILE_CONSTRUCTION
BOUNDED_GREENFIELD
```

the DirectionTaskManifest requires a B025 `mstr.greenfield-task.v0` identity for
headline convergence and retains `HEALTHY` as the verifier-health requirement.
B025 remains the curriculum authority for its G0-G5 complexity bands,
provenance/rights/contamination rules, synthesis semantics, and hidden behavior
contract.

## Verifier / privacy boundary

```text
ACCEPTANCE_OWNER = INDEPENDENT_VERIFIER
HIDDEN_FROM_MODEL = TRUE
PUBLIC_REPO_CONTAINS_HIDDEN_ACCEPTANCE_PAYLOAD = FALSE
PUBLIC_REPO_CONTAINS_PRIVATE_FRESH_TASKS = FALSE
PUBLIC_REPO_CONTAINS_MODEL_ANSWERS = FALSE
PUBLIC_REPO_CONTAINS_FUTURE_FIXES = FALSE
```

A015 records verifier identity; it does not implement B023 verifier-health
classification. Clean headline/training use remains blocked until the downstream
verifier-health gate is satisfied.

## Candidate outputs

```text
schemas/mstr-direction-task-v0.schema.json
specs/001-agent-harness-verified-loop-foundation/contracts/mstr-direction-task-v0.schema.json
src/mstr_qualify/schemas.py
src/mstr_qualify/cli.py
tests/contract/test_schemas.py
tests/integration/test_cli_offline.py
tests/fixtures/schemas/valid/mstr-direction-task-v0.json
tests/fixtures/schemas/invalid/mstr-direction-task-v0.json
tests/contract/test_direction_task_contract.py
benchmarks/direction-to-done/v0-taxonomy.json
evidence/mstr-000a/A015-direction-to-done.md
```

`tasks.md` is intentionally unchanged in the implementation candidate. A015 may
be marked complete only after governed merge and post-merge proof followed by a
separate canonical closeout.

## Authority containment

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
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
B023_VERIFIER_HEALTH_EXECUTION = NOT_IMPLEMENTED_BY_A015
A016_STATE = PENDING
```
