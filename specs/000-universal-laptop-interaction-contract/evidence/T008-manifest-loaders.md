# T008 — Local Manifest Loaders and Validation

**Task:** MSTR-000 / T008  
**Canonical base:** `8456f5d19c9fac1bc1d98f11de5e5d3f71be5d8e`  
**Branch:** `task/000-t008-manifest-loaders`  
**Scope:** local JSON loading/validation for candidate, task, and benchmark manifests. No remote retrieval, model access, candidate execution, paid API, rented compute, or training.

## Implementation

T008 adds `src/mstr_qualify/manifests.py` with three local-only loaders:

- candidate records delegate to the canonical `candidate-record` JSON Schema;
- task manifests delegate to the canonical `task-manifest` JSON Schema;
- benchmark manifests use the strict `mstr.benchmark.v1` structural contract documented in `benchmarks/manifests/README.md` because MSTR-000 does not yet define a separate benchmark JSON Schema file.

Every successfully loaded manifest records the SHA-256 of the exact source file. Only `.json` files are accepted. Invalid JSON, non-object roots, unknown manifest kinds, missing/unknown benchmark fields, duplicate task/candidate identities, invalid seeds/timeouts, and unsupported network policy fail closed with stable `ConfigurationError` codes.

Candidate/task loading performs validation only. Loading a candidate does not invoke T006 rights admission, download artifacts, execute a model, or contact any source URL.

## Exact prepared-source validation

```text
T008 focused tests = 35 passed
python -m compileall -q src = PASS
```

The first prototype used reduced schema stubs to exercise dispatch. Before Git content was prepared, the candidate/task positive fixtures were replaced with complete records matching the canonical T004 schemas so the repository tests do not depend on those stubs.

The complete repository suite was not reconstructed in the local tool container, so no T008 full-suite PASS is claimed. No GitHub Actions/CI PASS is claimed unless an exact-head run appears during PR qualification. Ruff/mypy remain deferred to T011.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
CANDIDATE_ADMISSION = NONE_BY_T008
```

## Result candidate

```text
T008_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T009
```
