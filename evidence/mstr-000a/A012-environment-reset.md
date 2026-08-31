# A012 — Clean-Checkout Environment Reset / Setup Abstraction

**Task:** `MSTR-000A / A012`
**State:** `IMPLEMENTATION_CANDIDATE`
**Canonical base:** `3cb9f44569a7469e785ed8ffc4ea88080663adda`

## Implemented boundary

A012 implements the smallest repository-local reset/setup layer that consumes the A011 `mstr.environment-manifest.v0` and `mstr.setup-manifest.v0` contracts without creating environment-admission or terminal-success authority.

The implementation:

- validates both frozen A011 schemas before execution;
- cross-binds environment ID, setup ID, health targets, effect policy, and resource ceilings;
- supports exact local `HARD_RESET_CLEAN` using only local Git reset/clean operations;
- requires `FRESH_CLONE` to be supplied by an injected driver and never opens network implicitly;
- proves repository origin, revision, tree, and clean state after reset;
- executes setup only through an injected executor whose declared enforcement envelope exactly equals the manifest effect/resource envelope;
- requires an exact runtime authority identity before any network allowlist or secret-access envelope can be consumed;
- contains setup working directories to the reset workspace;
- fails closed on setup timeout/failure and on protected-path modification;
- records setup steps, repository identity, health/checker identities, effects, and resource limits;
- returns `admission_status=NOT_EVALUATED_A013`; A013 remains the independent health-target/bootstrap admission authority.

## Authority boundary

```text
A012_CANONICAL_EXECUTION_PROFILE = LOCAL_RESET_AND_REPOSITORY_FIXTURES_ONLY
NETWORK_EXECUTION = NONE
SECRET_ACCESS = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PRODUCTION_RELEASE = NONE
ENVIRONMENT_ADMISSION_AUTHORITY = A013 / NOT_CREATED_BY_A012
TERMINAL_SUCCESS_AUTHORITY = A006_PROTECTED_FINALIZER
```

Any future caller that wishes to consume a network/secret-bearing setup manifest must independently supply the exact canonical authority referenced by that manifest and an executor enforcing the identical envelope. This implementation does not create or widen such authority.

## Qualification history

`33401051608` = `FAILURE` at `git diff --check` because the initial candidate evidence contained Markdown trailing whitespace. Quality jobs were skipped. The failure is preserved as negative evidence and is not represented as passing.

## Required qualification

This candidate is not canonical until exact-head hosted qualification, independent review, mandatory premerge verification, guarded expected-head merge, post-merge proof, canonical closeout, and post-closeout proof succeed. Failed or superseded runs remain evidence and must not be rewritten as passing.
