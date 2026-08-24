# T001 — Canonical Universal-Laptop Measurement Procedures

**Task:** MSTR-000 / T001  
**Status:** COMPLETE_CANDIDATE  
**Protocol ID:** `MSTR-MEASURE-v0`  
**Canonical base:** `c0ab325f2d65007d26ec65ad22fec972d2ba62e5`  
**Authority:** Measurement definition only. No model performance claim is made by this document.

## 1. Purpose

T001 freezes how MSTR will measure installability, latency, throughput, memory pressure, paging, sustained thermal behavior, and optional energy use so later candidate comparisons cannot improve their headline numbers by changing definitions.

All later MSTR-000 hardware/runtime/model evidence must either use this protocol version or explicitly document and justify a versioned successor.

## 2. Clock and event recording

- Use a monotonic high-resolution clock for durations.
- Record UTC wall-clock timestamps only as metadata, never to compute latency.
- Every model/tool/edit/verifier event used in latency accounting must have a monotonic timestamp from the same measurement host.
- Runtime logs may add timestamps, but the canonical harness clock owns TTFA/TTFCE/TTVC.
- Clock resolution and measurement harness revision must be recorded.

## 3. Run-state vocabulary

Every latency result must identify its state.

### `INSTALL_LOCAL_COLD`

The MSTR installer/package and model artifact are already present on local storage, but MSTR is not installed/configured. Network download time is excluded and artifact size is reported separately.

### `PROCESS_COLD`

MSTR is installed, but no MSTR runtime process is running and the model is not mapped by MSTR. Do not manually flush the OS filesystem cache unless a separate experiment explicitly studies that condition.

### `SESSION_WARM`

The runtime/model is loaded, but the task-specific prompt has not been evaluated. Prefix cache state must be identified as empty or populated.

### `PREFIX_WARM`

The exact versioned canonical system/tool prefix required by the measurement has a valid reusable cache entry.

Cold and warm numbers must never be combined into one average.

## 4. TTFI — Time To First Local Interaction

`TTFI` measures installability rather than model intelligence.

```text
TTFI_LOCAL =
  timestamp(first complete locally generated smoke response)
  - timestamp(user starts local installer/package setup)
```

Rules:

1. Model/runtime artifacts are already downloaded locally before the clock starts; network speed must not contaminate TTFI.
2. The procedure includes installation/extraction, first launch, local model discovery, and any mandatory first-run initialization.
3. The smoke interaction uses a fixed tiny local repository fixture and a fixed non-destructive prompt.
4. No provider login, API key, or network call is allowed.
5. If the product is a portable no-install bundle, the clock starts when the user launches/executes that bundle for the first time.
6. Report installer/package bytes and on-disk installed footprint separately.

Optional `TTFI_NETWORK` may be reported for distribution UX, but it is never used to compare model/runtime efficiency because network conditions are external.

## 5. TTFA — Time To First Action

For software-engineering tasks:

```text
TTFA =
  timestamp(first externally observable task-relevant action is accepted/starts)
  - timestamp(task submission is accepted by MSTR)
```

A qualifying action is the first task-relevant:

- repository search accepted by the search runtime;
- file/symbol read accepted by the tool runtime;
- shell/build/test process start;
- edit transaction start;
- or, for a task that genuinely requires no tool, first user-visible output token.

A model merely emitting malformed/rejected tool syntax does not stop TTFA. The action must cross the model/runtime boundary into an accepted externally observable operation.

Internal reasoning tokens, hidden planning, logging, or speculative work that produces no accepted task-relevant action do **not** stop TTFA.

Record separately:

- `TTFA_PROCESS_COLD`;
- `TTFA_SESSION_WARM`;
- `TTFA_PREFIX_WARM` where applicable.

## 6. TTFCE — Time To First Correct Edit

`TTFCE` is retrospective and only defined for tasks requiring a repository mutation.

```text
TTFCE =
  timestamp(first durable edit transaction successfully COMMITS to the workspace)
  - timestamp(task submission is accepted)
```

An edit is **durable/correct** only if:

1. the apply engine successfully completes the write/transaction and records the resulting file hash/state;
2. at least one resulting changed region is present in the final verified repository state;
3. that contribution is not fully reverted before successful completion; and
4. the final required verifier set passes with that contribution present.

Starting an edit operation does not stop TTFCE; parsing, conflict handling, stale-checking, and apply latency remain inside the metric until the successful workspace mutation is externally visible.

The apply engine must record file hashes before/after each edit so the harness can trace edit lineage. An early wrong edit that is later reverted does not count.

If the task is solved without a repository edit, `TTFCE = N/A` rather than zero.

## 7. TTVC — Time To Verified Completion

`TTVC` is MSTR's primary task-speed metric.

```text
TTVC =
  max(timestamp(last REQUIRED verifier returns PASS),
      timestamp(task enters completed state))
  - timestamp(task submission is accepted)
```

Rules:

1. Every task manifest declares its `REQUIRED_VERIFIER_SET` before execution.
2. The agent saying "done" is not completion.
3. A verifier started after the agent's answer still counts if it is in the required set.
4. Optional background/full-regression checks not declared required before execution do not count toward TTVC; their latency is reported separately as `TTVFR` (Time To Verified Full Regression).
5. If any required verifier fails and the agent repairs the work, all repair time remains inside TTVC.
6. A task that times out or never reaches all required PASS results is a **failed/censored task**, not a successful TTVC sample.
7. The timeout budget is frozen in the task manifest before the run.

Never publish median TTVC without the matching verified-completion rate and timeout budget.

## 8. Verification tiers

Task manifests may select from these versioned tiers:

- `V0_STATIC`: parse/format/lint/type/compile checks sufficient for the task type;
- `V1_TARGETED`: task-specific visible and hidden targeted tests/checks;
- `V2_REQUIRED_REGRESSION`: targeted checks plus declared affected/regression suite;
- `V3_FULL_REGRESSION`: full repository canonical suite where practical.

The exact commands and versions are part of the task manifest. A lower verifier tier must never be substituted after seeing model output.

## 9. Artifact and installed-footprint measurement

Report exact bytes, not rounded marketing units, for:

- `MODEL_ARTIFACT_BYTES` — the primary model file(s) required for inference;
- `RUNTIME_PACKAGE_BYTES` — runtime binaries/libraries excluding model;
- `INSTALLED_MSTR_BYTES` — model + required runtime after installation, excluding repositories;
- `FIRST_RUN_CACHE_BYTES` — persistent cache/index created by first launch;
- `REPO_INDEX_BYTES` — MSTR-created index/cache for the reference repository;
- `TEMPORARY_PEAK_DISK_BYTES` — maximum temporary storage during install/update where measurable.

The <=3 GB MSTR target applies to the primary model artifact unless a later canonical decision changes it. Total installed footprint must still be reported.

## 10. Memory measurement

Memory is measured at three attribution levels plus whole-system pressure.

### A. `MSTR_CORE_TREE`

Includes every process/service required to provide MSTR model inference and repository intelligence even when no task-specific external build/test command is running, including:

- model server/runtime;
- tokenizer/prompt service;
- context/retrieval/index helpers;
- apply engine helpers;
- local orchestration/IPC services;
- any daemon moved out-of-process by MSTR.

The <=4 GB U1 soft RSS target applies to this core attribution at the 8K reference context. MSTR cannot hide memory by moving model/retrieval work into a separate helper daemon.

### B. `TASK_TOOL_TREE`

Includes repository-specific external processes started because of the task, such as:

- compiler/linker;
- test runner;
- language package/build tool;
- shell commands;
- application process launched for verification.

These are reported separately because their memory belongs to the repository/toolchain rather than model footprint.

### C. `TOTAL_AGENT_TREE`

`MSTR_CORE_TREE + TASK_TOOL_TREE` where process lineage permits reliable aggregation.

### Required process metrics

Record, where the OS exposes them:

- core process-tree RSS / working set;
- core private/unique memory or private working set;
- peak `MSTR_CORE_TREE` RSS;
- peak `TASK_TOOL_TREE` RSS;
- peak `TOTAL_AGENT_TREE` RSS where available;
- model-mapping/file-backed memory where distinguishable;
- core peak during model load;
- core peak during 8K prefill;
- core peak during steady decode;
- core peak during repository indexing;
- task-tool peak during build/test verification.

Do not compare unlike OS memory concepts without labeling them. `MSTR_CORE_TREE_RSS` is the common model/system-footprint headline; task tools remain separately visible and whole-system pressure remains authoritative for laptop usability.

### Required whole-system metrics

Record:

- total physical RAM;
- available/free memory at baseline;
- minimum available memory during run;
- committed/used memory where exposed;
- swap/pagefile configured size;
- swap/pagefile used delta;
- major/hard page-fault counters;
- platform memory-pressure state where exposed.

All MSTR runtime/helper processes belong to `MSTR_CORE_TREE`; all MSTR-started task/tool subprocesses belong to `TASK_TOOL_TREE`. Neither category may be silently omitted. Whole-system measurements include both.

## 11. Paging / swap-thrashing classification

Raw OS metrics differ, so T001 defines a normalized decision rule plus platform-specific evidence.

A U1 run is classified `MEMORY_PRESSURE_FAIL` if any of these occurs:

1. OS OOM/forced process termination;
2. OS reports critical memory pressure for a sustained interval of >=10 seconds;
3. available physical memory remains below 5% of total RAM for >=10 consecutive seconds **and** active paging/pageout is observed;
4. combined swap/pagefile traffic attributable to the measurement interval exceeds 256 MiB during a 60-second steady-state inference window after initial model loading; or
5. repeated paging makes the reference editor responsiveness probe fail.

Initial one-time page-ins caused by model mapping/loading are not automatically swap thrashing; the steady-state window begins after the model/reference context is resident.

Platform evidence:

- Windows: hard faults/pagefile I/O and memory commit/available counters;
- Linux: `/proc`/`vmstat` major faults plus `si/so` or equivalent swap I/O;
- macOS: memory pressure, `vm_stat` pageouts/swap/compressor metrics where available.

T022 may tighten these thresholds with evidence, but may not loosen them merely to rescue a candidate without explicit review and a measurement-protocol revision.

## 12. Prefill and decode throughput

Report separately:

### Prefill

```text
PREFILL_TOKENS_PER_SECOND = prompt_tokens / prefill_duration
```

The prompt token count, tokenizer revision, context length, cache state, and prefix-cache hit/miss state are mandatory metadata.

### Decode

```text
DECODE_TOKENS_PER_SECOND = generated_tokens / decode_duration
```

Decode duration starts at the first generated model token and ends at the last generated token for the measured segment. Tool execution time is excluded from pure decode TPS but remains inside TTVC.

### Tokenizer-normalized output rate

Because tokenizer granularity differs across candidate models, also report:

- `OUTPUT_UTF8_BYTES_PER_SECOND`;
- `OUTPUT_UNICODE_CHARACTERS_PER_SECOND`;
- for fixed code-generation fixtures, `SOURCE_CODE_CHARACTERS_PER_SECOND` after removing protocol/tool-wrapper bytes.

No candidate may claim to be "faster" from tokens/sec alone.

## 13. Sustained CPU / thermal procedure

Burst throughput is insufficient for laptop qualification.

For every required U1 platform lane:

1. connect AC power;
2. use normal/balanced power mode, not a vendor turbo/overclock-only profile;
3. allow the machine to reach idle baseline before the run;
4. run a deterministic decode workload continuously for **10 minutes** after model load;
5. record throughput in at least 30-second windows;
6. compare median throughput from minute 1 with median throughput from minute 10;
7. record CPU frequency/temperature/thermal-pressure data where reliable platform interfaces expose it;
8. run the editor responsiveness probe throughout.

Report:

```text
SUSTAINED_RATIO = FINAL_MINUTE_TPS / FIRST_MINUTE_TPS
```

Classification:

- `THERMAL_OK`: sustained ratio >= 0.80 and responsiveness passes;
- `THERMAL_WARNING`: ratio 0.65–0.80 with responsiveness still passing;
- `THERMAL_FAIL`: ratio < 0.65, thermal shutdown/throttle instability, or responsiveness failure attributable to sustained inference.

The ratio is a usability gate, not a claim about why frequency changed; thermal interpretation must use available platform evidence.

## 14. Editor responsiveness procedure

The E1 VS Code workload from T000 remains open throughout U1 measurements.

The measurement harness must implement a repeatable UI responsiveness probe that performs a non-destructive editor operation at idle baseline and periodically during MSTR load, such as:

- opening a known file through Quick Open;
- moving focus and rendering a known location;
- entering/removing a fixed short text sequence in an unsaved scratch buffer.

Measure action-to-visible-update latency through a platform automation/instrumentation method pinned in the harness revision.

Until T022 provides evidence for stronger thresholds, the provisional U1 rule is:

```text
EDITOR_P95_UNDER_LOAD <= 500_MS
AND
EDITOR_P95_UNDER_LOAD <= 2.0 * EDITOR_P95_IDLE_BASELINE
```

Failure of either condition is `RESPONSIVENESS_FAIL`.

This probe is a laptop-usability guardrail; it is not a benchmark of VS Code itself.

## 15. Run repetition and statistics

### Deterministic microbenchmarks

For model load, prefill, decode, indexing, and apply-engine latency:

- 2 warm-up runs excluded from statistics where warm-up is applicable;
- at least 10 measured repetitions;
- report median, p90, minimum, maximum, and sample count;
- cold-process tests use independent process launches.

### Sustained thermal

- at least 2 independent 10-minute runs per required platform/candidate configuration during qualification;
- report each run plus aggregate median sustained ratio.

### Agent/repository tasks

Development qualification:

- at least 3 fixed seeds per stochastic task/model configuration where sampling is used.

Headline/release claims:

- at least 5 seeds per stochastic task/model configuration unless the model is configured deterministically;
- report verified-completion rate, median TTVC among successes, timeout rate, and confidence interval/dispersion method;
- never drop failed seeds from solve-rate calculations.

The task manifest freezes temperature, top-p/top-k, max tokens, seed list, tool budget, and timeout before execution.

## 16. Cold/warm cache fairness

Comparisons are valid only when cache states match.

Report independent surfaces for:

- cold process / natural OS cache;
- warm loaded model with cold canonical prefix;
- warm loaded model with warm canonical prefix.

Do not flush system caches for one candidate but not another. Do not report a warm-prefix number against a competitor's cold-prefix number as a direct speed comparison.

## 17. Reference system preparation

Before measured runs:

- install pending OS updates before the measurement session or record why not;
- disable unrelated scheduled scans/builds/sync jobs where possible while preserving ordinary OS services;
- use the T000 E1 editor workload;
- close unrelated heavyweight applications;
- record power mode and AC/battery state;
- record free disk and storage medium type;
- ensure no cloud coding assistant is active in the reference editor;
- record ambient temperature if a reliable measurement is available, otherwise mark it unknown rather than inventing a value.

The goal is reproducibility without creating an unrealistic stripped-down OS.

## 18. Optional energy measurement

Energy is secondary because trustworthy counters differ by platform.

Where a reliable interface exists, report:

```text
JOULES_PER_1000_DECODED_TOKENS
JOULES_PER_VERIFIED_TASK
AVERAGE_PACKAGE_POWER_WATTS_DURING_SUSTAINED_RUN
```

Record the measurement source/tool and privileges. Never synthesize energy values from TDP specifications.

## 19. Failure and timeout reporting

A failed run remains evidence.

Canonical task reporting must include counts for:

- verified pass;
- verifier fail;
- model/tool error;
- OOM/memory-pressure fail;
- timeout;
- infrastructure invalidation.

Only true infrastructure-invalid runs may be rerun without counting as model failures, and the invalidation reason must be logged before the result is discarded.

For time-bounded comparisons, publish both success rate and the fixed timeout budget. Do not compute a "fast average" from successful samples alone and omit failures.

## 20. Minimum result identity

Every result record must include:

```text
MEASUREMENT_PROTOCOL = MSTR-MEASURE-v0
HARNESS_COMMIT
TASK_MANIFEST_REVISION
TASK_ID
SEED
RUN_STATE
OS_NAME
OS_VERSION_BUILD
CPU_MODEL
CPU_ARCH
CPU_ISA_FEATURES
PHYSICAL_CORES
LOGICAL_THREADS
TOTAL_RAM_BYTES
POWER_MODE
GPU_NPU_USED
EDITOR_VERSION
REFERENCE_REPO_COMMIT
MODEL_ID
MODEL_REVISION
MODEL_ARTIFACT_SHA256
TOKENIZER_REVISION
QUANTIZATION_METHOD
QUANTIZER_VERSION
RUNTIME_VERSION_COMMIT
RUNTIME_BUILD_FLAGS
RUNTIME_THREADS
CONTEXT_LENGTH
KV_CACHE_CONFIG
INTERACTION_CONTRACT_VERSION
PREFIX_CACHE_STATE
MODEL_ARTIFACT_BYTES
MSTR_CORE_TREE_PEAK_RSS
TASK_TOOL_TREE_PEAK_RSS
TOTAL_AGENT_TREE_PEAK_RSS_IF_AVAILABLE
SYSTEM_MIN_AVAILABLE_MEMORY
SWAP_PAGEFILE_DELTA
PAGEFAULT_METRICS
COLD_LOAD_MS
TTFA_MS
TTFCE_MS_OR_NA
TTVC_MS_OR_FAILURE
PREFILL_TPS
DECODE_TPS
OUTPUT_BYTES_PER_SECOND
SOURCE_CODE_CHARACTERS_PER_SECOND
SUSTAINED_RATIO
EDITOR_RESPONSIVENESS_P95_MS
VERIFIER_SET_ID
FINAL_RESULT
```

## 21. Protocol change rule

After candidate scoring starts, a material change to metric definitions, cache state, timeout policy, verifier requirements, editor workload, memory attribution, or memory-pressure thresholds requires:

1. a new protocol version;
2. rationale;
3. remeasurement of all candidates affected by the change before direct comparison.

Historical results remain labeled with their original protocol.

## 22. T001 result

```text
T001_RESULT = PASS
MEASUREMENT_PROTOCOL = MSTR-MEASURE-v0
TTFI = DEFINED
TTFA = ACCEPTED_EXTERNAL_ACTION
TTFCE = SUCCESSFULLY_COMMITTED_DURABLE_VERIFIED_EDIT
TTVC = VERIFIED_TERMINAL_COMPLETION
MEMORY_PROTOCOL = MSTR_CORE_TREE + TASK_TOOL_TREE + WHOLE_SYSTEM
SWAP_THRASH_RULE = DEFINED
THROUGHPUT = PREFILL + DECODE + TOKENIZER_NORMALIZED_OUTPUT
SUSTAINED_CPU_TEST = 10_MINUTES
EDITOR_RESPONSIVENESS_GUARDRAIL = DEFINED
ENERGY = OPTIONAL_WHERE_RELIABLE
MODEL_WEIGHT_ACCESS = NONE
NEXT_TASK = T002_DISTRIBUTION_INSTALL_PRIVACY_CONTRACT
```
