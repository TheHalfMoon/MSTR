# T023 — Runtime / Platform Adapter Protocols

**Task:** MSTR-000 / T023 [P] [US1]
**Branch:** task/000-t023-runtime-platform-protocols
**Canonical base:** main `dd0ee9821ae09078c2b12e052321ed429a52b219` (T022 canonical)
**Scope:** protocol/interface infrastructure with dummy/test implementations only. No real model backend, no runtime download, no backend preselection, no network, no weight access.

## Delivered

```text
src/mstr_qualify/runtimes/__init__.py        package marker
src/mstr_qualify/runtimes/base.py            RuntimeAdapter protocol + lifecycle + dummy adapter
src/mstr_qualify/measurement/__init__.py     package marker
src/mstr_qualify/measurement/platform.py     PlatformSampler protocol + availability vocabulary + unavailable sampler
tests/unit/test_runtime_protocol.py          15 tests
tests/unit/test_platform_sampler.py          12 tests
```

## RuntimeAdapter boundary (`runtimes/base.py`)

- **Explicit lifecycle:** `LifecycleState = UNINITIALIZED -> READY -> TERMINATED`, validated fail-closed (`AdapterStateError`) on load-from-READY, inference-before-READY, and duplicate termination.
- **Capability discovery:** `RuntimeCapabilities` is a static frozen record (`supported_formats`, `max_context_length`, `supports_cpu_only`, `supports_prefix_cache`) queryable before any load; unsupported format/context raises `UnsupportedOperationError` explicitly instead of guessing at call time.
- **Deterministic structured results:** `LoadRequest` (identity-only: artifact_id, artifact_sha256, format_name, context_length — no paths, no bytes), `PrefillResult`, `DecodeResult`; identical call sequences always produce equal results.
- **Explicit unavailable/unsupported states:** unsupported operations raise `UnsupportedOperationError`; capability fields may be `None` ("not known yet") without implying support.
- **No hidden network / no model access:** `DummyRuntimeAdapter` performs zero I/O; nothing is fetched, executed, or downloaded anywhere in its path. The protocol contract documents the same prohibition for real adapters.
- **Clean teardown:** `terminate()` clears loaded identity/cache state; double termination fails closed.
- **No backend preselected:** llama.cpp or any other runtime is NOT chosen here; `RuntimeAdapter` is a pure boundary for later T030 adapters.

## PlatformSampler boundary (`measurement/platform.py`)

- **MSTR-MEASURE-v0 scope vocabulary preserved:** `MemoryScope` exposes exactly `MSTR_CORE_TREE`, `TASK_TOOL_TREE`, `TOTAL_AGENT_TREE`, `WHOLE_SYSTEM_PRESSURE`; whole-system pressure cannot masquerade as a process-tree sample (constructor rejects it).
- **Availability semantics are type-level enforced:** `SampledMetric` requires a concrete value AND unit when `AVAILABLE`, and forbids any value when `UNAVAILABLE`/`UNSUPPORTED`. It is structurally impossible to smuggle an invented zero into evidence.
- **Fail-closed consumption:** `require_available()` refuses to substitute defaults for missing/unsupported metrics.
- **Honest pressure state:** `SystemMemoryPressure.UNKNOWN` requires an explanatory note, preventing silent "unknown == normal" conflation.
- **Testability without weights/OSes:** `UnavailablePlatformSampler` returns deterministic explicit-unsupported samples on any host; per-OS samplers (T025) inject data sources so unit tests never require all three OS families.
- **No hidden network:** samplers read only local OS interfaces by contract; no imports of networking facilities exist in this module.

## Evidence of quality gates (exact head, run 2026-08-25)

```text
pytest -q                 -> 201 passed   (174 pre-existing + 27 new)
ruff check src tests      -> All checks passed!
mypy (strict)             -> Success: no issues found in 14 source files
python -m mstr_qualify validate -> exit 0 (schema self-check unchanged)
```

CI note: repository deliberately has no GitHub Actions workflows (`configs/quality.toml`: `ci_workflows_added = false`). Gates were run locally on the exact head; no CI claim is made.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION     = NONE
RUNTIME_DOWNLOAD    = NONE
NETWORK             = NONE
PAID_COMPUTE        = NONE
TRAINING            = NONE
BACKEND_PRESELECTION = NONE (boundary only)
```

## Result

```text
T023_RESULT = COMPLETE_CANONICAL_PENDING_REVIEW
NEXT_TASKS  = T024/T025/T026 [P] then T027 preflight
```
