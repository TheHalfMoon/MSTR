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
