# T026 — MSTR-MEASURE-v0 Monotonic Event Logic

**Task:** MSTR-000 / T026 [P] [US1]
**Branch:** task/000-t026-measure-protocol
**Canonical base:** main `89a48ba834eb9fa012b1515ec774dae68315ec49` (T025 canonical merge, verified live before branching)
**Scope:** canonical measurement/timing semantics per T001. No model execution, no network, no benchmark runs.

## Delivered

```text
src/mstr_qualify/measurement/protocol.py        session/event ledger + outcome record
tests/unit/measurement/test_protocol.py         20 tests
```

## Canonical semantics implemented (T001 cross-references)

| Rule | Implementation |
|---|---|
| §2 monotonic clock | All durations from `MonotonicClock.now_ns()` (`time.monotonic_ns` in production); wall-clock strings stored as metadata only and provably absent from latency math. |
| Events never move backward | Every recorded event validates against the last event timestamp; violation raises `measurement.event_backwards` fail-closed. |
| Required verifier set frozen before execution | Set captured at construction; post-construction mutation of the caller's list cannot add verifiers; unknown ids rejected; duplicates rejected. |
| TTFA = first ACCEPTED external action (§5) | `record_accepted_action` stops TTFA on the FIRST accepted action only; `record_rejected_tool_output` explicitly never stops it (counted for reporting). |
| Malformed/rejected output does not stop TTFA | Covered by explicit rejection counter test — TTFA measured only at the later accepted action. |
| TTFCE = durable committed edit (§6) | `record_edit_committed` records commit timestamp; N/A (None) for no-edit tasks, never zero; edit commits on no-edit tasks raise a protocol error. |
| TTVC = max(last required PASS, completed) − submitted (§7) | Exact formula in `finalize`; verified by test where completion is later than last pass (505 ms case). |
| Repair time inside TTVC | Failing→repairing→passing sequence keeps all repair time inside TTVC (700 ms case). |
| Timeout/failure ≠ successful sample | Timeout and failed terminals yield `MeasurementRecord(censored=True, final_result=TIMEOUT/VERIFIER_FAIL, ttvc_ms=None)` — never a successful TTVC sample. |
| Completed-but-unverified fails closed | Claiming completion with any required verifier not passed yields a censored VERIFIER_FAIL naming the missing verifier(s). |
| Duplicate/invalid terminal states fail closed | Second terminal of ANY kind raises `measurement.duplicate_terminal`; events after terminal rejected. |
| Finalize requires terminal state | Premature finalize prohibited. |

## Determinism

`ManualClock` gives tests exact nanosecond control; identical event schedules produce byte-identical `MeasurementRecord`s (equality-tested).

## Evidence of quality gates (exact head)

```text
pytest -q                      -> 296 passed   (276 after T025 + 20 new)
ruff check src tests           -> All checks passed!
mypy (strict)                  -> Success: no issues found in 19 source files
python -m mstr_qualify validate -> exit 0
```

CI note: repository deliberately has no GitHub Actions workflows (`configs/quality.toml`: `ci_workflows_added = false`). Gates were run locally on the exact head; no CI claim is made.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS   = NONE
MODEL_EXECUTION       = NONE
BENCHMARK_EXECUTION   = NONE
NETWORK               = NONE
PAID_COMPUTE          = NONE
TRAINING              = NONE
```

## Result

```text
T026_RESULT = COMPLETE_CANONICAL_PENDING_REVIEW
NEXT_TASKS  = T027 weight-access preflight (preparation only), then STOP before T028 gate
```
