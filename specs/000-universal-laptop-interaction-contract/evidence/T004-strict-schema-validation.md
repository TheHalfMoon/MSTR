# T004 — Strict Local Schema Validation Evidence

**Task:** MSTR-000 / T004  
**Canonical base:** `4f16e1e5a8a515ecebb0750cbd0b93876c8ae3ea`  
**Branch:** `task/000-t004-schema-validation`  
**Scope:** local JSON Schema loading/validation only. No model access, model execution, network service, candidate scoring, training, paid API use, or rented compute.

## Implementation

T004 adds `jsonschema>=4.23,<5` as a dependency of the research qualification harness. The package is MIT-licensed in the locally validated environment (`jsonschema 4.26.0`). This dependency is not an end-user MSTR runtime decision.

The implementation:

- registers only the four canonical MSTR-000 schema names;
- loads schemas only from the repository-local `schemas/` directory;
- checks every schema with `Draft202012Validator.check_schema`;
- rejects unknown schema names rather than treating input as a path;
- rejects any non-fragment `$ref` before validator construction, preventing implicit remote schema resolution;
- returns deterministic validation-error ordering and paths;
- validates already-decoded JSON and UTF-8 JSON files;
- keeps typed project-wide error classes deferred to T005.

Runtime schema copies reuse the exact Git blob identities of the four design-source contracts, and contract tests also assert byte-for-byte equality:

- `candidate-record.schema.json`;
- `task-manifest.schema.json`;
- `run-evidence.schema.json`;
- `interaction-contract.schema.json`.

## Local validation

Validation of the exact T004 implementation prepared for this branch:

```text
Python = 3.13.5
jsonschema = 4.26.0
jsonschema license = MIT
pytest tests/contract/test_schemas.py = 18 passed
python -m compileall src = PASS
```

The 18 tests cover:

- all four schemas self-check as Draft 2020-12;
- all four runtime copies equal their design sources byte-for-byte;
- valid fixture for each schema passes;
- invalid fixture for each schema fails closed;
- unknown/path-like schema name fails closed;
- external `$ref` is rejected before validation.

Ruff and mypy were not available in the validation container, so no Ruff/mypy PASS is claimed. T011 remains the foundational quality-gate closeout.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T004_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T005
```
