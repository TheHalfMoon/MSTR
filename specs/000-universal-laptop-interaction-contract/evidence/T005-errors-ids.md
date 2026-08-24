# T005 — Typed Errors and Stable Identity Helpers Evidence

**Task:** MSTR-000 / T005  
**Canonical base:** `bc3d37803434fcad15c92683705d61cf68477846`  
**Branch:** `task/000-t005-errors-ids`  
**Scope:** deterministic error and identity primitives only; no model/runtime selection, network service, model access, paid API, rented compute, or training.

## Implementation

T005 adds:

- `QualificationError`, a `ValueError`-compatible base carrying a stable code and deterministic sorted details;
- typed subclasses for configuration, schema validation, identity, rights, artifact integrity, comparison, and policy failures;
- canonical lowercase SHA-256 validation;
- SHA-256 helpers for bytes, UTF-8 text, and streamed files;
- domain-separated, length-framed stable IDs to avoid ambiguous component concatenation;
- ordered SHA-256 combination for composite evidence identities.

T004 schema validation is refactored to use `SchemaValidationError` with stable failure codes while remaining compatible with existing `ValueError` assertions. No T004 validation semantics are loosened.

## Local validation

```text
Python = 3.13.5
pytest full prepared harness suite = 41 passed
python -m compileall src = PASS
```

Prototype defects caught before Git write:

1. the fresh local sandbox initially omitted `__init__.py`, causing import failures; corrected before branch content was created;
2. `default_code` was initially annotated `Final`, which would conflict with subclass overrides under mypy; removed before branch content;
3. an empty explicit error code initially fell through to the default code; changed so explicit empty/whitespace codes fail closed.

Ruff and mypy remain unavailable in the validation container, so no Ruff/mypy PASS is claimed. T011 remains the foundational quality closeout.

## Safety / authority

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
T005_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T006
```
