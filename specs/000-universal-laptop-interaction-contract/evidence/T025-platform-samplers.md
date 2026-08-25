# T025 — Cross-Platform Memory / Paging Samplers

**Task:** MSTR-000 / T025 [P] [US1]
**Branch:** task/000-t025-platform-samplers
**Canonical base:** main `c593fce1655ee857f237b3fd476fc8e14cb836fe` (T024 canonical merge, verified live before branching)
**Scope:** OS sampling layer implementing the T023 PlatformSampler boundary for Windows x86_64, Linux x86_64, macOS arm64/M1-class. No model access, no network, no invented metrics.

## Delivered

```text
src/mstr_qualify/measurement/linux.py     LinuxPlatformSampler (/proc readers, injectable)
src/mstr_qualify/measurement/windows.py   WindowsPlatformSampler (Win32 collector doubles, injectable)
src/mstr_qualify/measurement/macos.py     MacOSPlatformSampler (Mach/proc collector doubles, injectable)
tests/unit/measurement/test_linux.py      11 tests (mocked /proc data; runs on any dev OS)
tests/unit/measurement/test_windows.py    8 tests (mocked collectors)
tests/unit/measurement/test_macos.py     10 tests (mocked collectors)
```

## Honest metric identity mapping (per MSTR-MEASURE-v0 §10)

| OS | RSS headline | Peak RSS | Private identity | Swap identity | Notes |
|---|---|---|---|---|---|
| Linux | VmRSS × 1 KiB→bytes | WITHHELD — summing per-process lifetime VmHWMs overstates concurrent tree peak; true peak needs harness-side sampling | `rss_anon_bytes` (RssAnon — own identity, never equated to private working set); aggregate withheld if any sampled pid lacks the field | VmSwap per process (withheld if any pid lacks it); SwapTotal−SwapFree system-wide | pswpin/pswpout cumulative byte totals surface in extra_metrics; PSI pressure UNKNOWN until thresholds frozen |
| Windows | Working set | WITHHELD (same concurrent-peak reasoning as Linux) | PrivateUsage (`private_bytes`) | UNSUPPORTED — MEMORYSTATUSEX pagefile fields are COMMIT limit/charge, reported under `commit_limit_bytes`/`commit_charge_bytes` extras instead | PageFaultCount is TOTAL faults — never relabeled hard faults (ETW needed → UNSUPPORTED); dwMemoryLoad reported raw, NOT mapped to a pressure state |
| macOS | ri_resident_size | UNSUPPORTED (proc_pid_rusage exposes current only) | `phys_footprint_bytes` (own identity) | kern.vm_swapusage parsed (total/used) | total RAM from hw.memsize sysctl (NEVER from summing page classes); default page size host-queried via SC_PAGE_SIZE; available labeled as (free+inactive) estimate; pageins/pageouts kept raw in extras |

## Scope distinctions preserved

`MSTR_CORE_TREE`, `TASK_TOOL_TREE`, and `TOTAL_AGENT_TREE` samples remain structurally distinct (separate pid attributions); `WHOLE_SYSTEM_PRESSURE` is rejected by `sample_process_tree` and served only via `sample_system_memory`.

## Unavailable/unsupported semantics

Every metric a platform does not reliably expose is returned as an explicit UNAVAILABLE/UNSUPPORTED `SampledMetric` with an explanatory note — never zero-filled, never synthesized from TDP/vendor claims. Examples: minimum-available tracking is harness-side everywhere; Windows hard faults; macOS peak RSS and pressure level; Linux single system-wide major-fault counter.

## Testability without weights or target OSes

All three samplers take injected data sources (proc text readers, collector callables returning API-shaped test doubles). The full suite passes on the development machine without requiring any of the three OS families at runtime.

## Evidence of quality gates (exact head)

```text
pytest -q                      -> 276 passed   (245 after T024 + 31 new incl. review-fix regressions)
ruff check src tests           -> All checks passed!
mypy (strict)                  -> Success: no issues found in 18 source files
```

CI note: repository deliberately has no GitHub Actions workflows (`configs/quality.toml`: `ci_workflows_added = false`). Gates were run locally on the exact head; no CI claim is made.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS     = NONE
MODEL_EXECUTION         = NONE
NETWORK                 = NONE
PAID_COMPUTE            = NONE
TRAINING                = NONE
```

## Result

```text
T025_RESULT = COMPLETE_CANONICAL_PENDING_REVIEW
NEXT_TASKS  = T026 [P] then T027 preflight
```
