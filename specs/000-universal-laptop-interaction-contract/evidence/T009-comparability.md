# T009 — Score-Surface and Report Comparability Rules

**Task:** MSTR-000 / T009  
**Canonical base:** `ccf15209e9ffce663eb27af21ca1e1ad9b914469`  
**Branch:** `task/000-t009-comparability`  
**Scope:** deterministic direct-comparison eligibility and TTVC-summary guardrails only. No benchmark execution, model access, paid API, rented compute, or training.

## Comparability contract

T009 implements `ComparisonConditions` and requires direct score comparisons to match on:

- score surface (`raw_model`, `neutral_harness`, or `full_system`);
- measurement protocol;
- task ID;
- exact task-manifest revision;
- verifier set;
- timeout budget;
- cache state;
- normalized hardware class;
- context length;
- Interaction Contract version;
- sampling configuration.

Seed is intentionally excluded from the comparability key because different frozen seeds are repeated samples under the same protocol rather than protocol changes.

Any mismatch produces a stable `comparison.mismatch` failure instead of silently averaging unlike results. Comparison groups use a stable ID over canonicalized conditions so mapping key order cannot change identity.

The contract follows `MSTR-MEASURE-v0`: cold/warm cache surfaces are separate, verifier/timeout conditions are frozen, and raw/neutral/full-system results are not conflated.

## TTVC summary guardrail

`validate_ttvc_summary` requires a finite verified-completion rate in `[0,1]`, a positive timeout, and a finite non-negative median TTVC when present. Median TTVC is rejected when verified-completion rate is zero. This prevents publishing a speed number detached from solve rate and timeout.

## Exact prepared-source validation

```text
T009 focused tests = 35 passed
python -m compileall -q src = PASS
```

Focused coverage includes every material comparison field, seed invariance, sampling-key-order invariance, partitioning, missing/unknown conditions, non-finite sampling/summary values, timeout/solve-rate checks, and a fixture proving `process_cold` and `prefix_warm` are not directly comparable.

The complete repository suite was not reconstructed in the local tool container, so no T009 full-suite PASS is claimed. No GitHub Actions/CI PASS is claimed unless an exact-head run appears. Ruff/mypy remain part of T011 closeout.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
BENCHMARK_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T009_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T010
```
