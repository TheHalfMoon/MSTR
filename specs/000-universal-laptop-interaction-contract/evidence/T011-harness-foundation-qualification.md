# T011 — Harness Foundation Quality Gates and Baseline Evidence

**Task:** MSTR-000 / T011  
**Canonical base:** `63eeaa395dfbddc11fc1a210a34a879ed1725948` (post-T010 canonical main)  
**Branch:** `task/000-t011-quality-gates`  
**Canonical base (full SHA):** `63eeaa395dfbddc11fc1a210a34a879ed1725948`  
**Scope:** freeze harness quality gates (`configs/quality.toml`), repair pre-existing lint debt deferred to this task by T009 evidence, add the PEP 561 typed-package marker and mypy stub dependency for dev tooling, and record baseline gate runs. No model weights, no execution, no benchmark execution, no paid API, no rented compute, no network service access, and no training.

## Frozen gates (`configs/quality.toml`, `mstr.quality-gates.v1`)

From T011 onward, a task may be marked COMPLETE_CANONICAL only with these gates passing on its exact head:

```text
gates.test_suite       = pytest -q                       (required)
gates.lint             = ruff check src tests            (required)
gates.typecheck        = mypy (strict over mstr_qualify)  (required)
gates.schema_selfcheck = python -m mstr_qualify validate (required, exit 0)
environment.offline_required = true
```

The configuration also freezes policy declarations: runtime-dependency additions require task authority; dev tooling may not become a runtime dependency; model binaries never enter Git; CI workflows remain deliberately absent. Contract tests in `tests/contract/test_quality_config.py` keep these declarations from silently drifting.

## Lint/typecheck repairs enabling the freeze

T009 evidence explicitly deferred repository-wide ruff/mypy closeout to T011. The following minimal repairs were made:

- `rights.py`: import `Mapping` from `collections.abc` (UP035).
- `schemas.py`, `tests/contract/test_schemas.py`: line-length wraps only; no behavior change.
- `tests/unit/test_evidence.py`: noncanonical-JSON fixture now built via `json.dumps`; still rejected by the loader as intended.
- `tests/unit/test_rights.py`: local variable extraction for line length; no behavior change.
- `evidence.py`: B904 — the immutable-conflict raise is now explicit `from None` (context is not meaningful there).
- Added `src/mstr_qualify/py.typed` (PEP 561) so mypy can type-check the installed editable package.
- Added `types-jsonschema` to dev extras and committed `uv.lock` so the exact gate toolchain is reproducible. Dev tooling does not become a runtime dependency: runtime deps remain exactly `jsonschema>=4.23,<5`.

## CI decision

No GitHub Actions workflow was added. The repository has no `.github/workflows/` directory; absence is recorded here rather than silently assumed. Per task definition, CI may be added later only if explicitly chosen.

## Baseline gate runs on prepared source

```text
Python = 3.14.0 (.venv via uv)
pytest = 9.1.1        → full suite: 174 passed (168 prior + 6 contract/quality-config tests)
ruff = 0.16.4         → All checks passed (zero errors in src and tests, matching the frozen gate scope)
mypy = 1.20.2         → Success: no issues found in 10 source files (strict)
python -m mstr_qualify validate → exit 0 (4 schemas self-checked, 4 valid fixtures passed, 4 invalid fixtures rejected)
jsonschema = 4.26.0 (runtime dep unchanged)
types-jsonschema = 4.26.0.20260518 (dev-only)
uv.lock = committed, pins the gate toolchain

CI = NO_RUN / NOT_PRESENT (no workflows exist; none claimed)
```

## Review finding resolution

qodo-code-review raised one High finding on PR #17: the gate contract tests did not assert `exit_code_zero_required`, did not verify gate-tool runnability, and did not verify the CLI subcommand wiring. Resolved on the same head by extending `tests/contract/test_quality_config.py`: explicit `exit_code_zero_required is True` assertion, importability checks for pytest/ruff/mypy in the active environment, and `build_parser().parse_args` probes for all four command families. Re-run after fix: full suite 175 passed; ruff clean (src + tests); mypy strict clean.

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
T011_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T012 (first Phase-3 static candidate qualification)
CHECKPOINT = FOUNDATIONAL_HARNESS_READY
```
