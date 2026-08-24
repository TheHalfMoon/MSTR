# MSTR-000 Plan

## Objective

Empirically freeze the smallest interaction/runtime/distribution contract that can support a best-in-class local software-engineering experience on ordinary laptops before expensive training begins.

## Phase A — universal-laptop measurement contract

1. Define the reference hardware/OS matrix rather than using a vague "any laptop" label.
2. Measure MSTR under **concurrent realistic use**: operating system + reference editor + model/runtime.
3. Use a fixed provisional context ladder:
   - 4K tokens;
   - 8K tokens (reference target);
   - 16K tokens.
4. Define measurement fields for:
   - model artifact size;
   - runtime package size;
   - process RSS/working set;
   - total-system free memory;
   - swap/page-fault behavior;
   - cold model load;
   - install-to-first-interaction (TTFI);
   - warm TTFA;
   - tokens/sec and source-code characters/sec;
   - TTFCE and TTVC;
   - sustained 10-minute throughput/thermal throttling;
   - energy per verified task where reliable platform counters exist;
   - Q4 correctness regressions.
5. Define acceptable editor/system responsiveness; "technically loads" is not sufficient if the laptop becomes unusable.
6. Freeze the benchmark/task manifest and seed policy before candidate scoring.

## Phase B — distribution and candidate admission contract

Before any MSTR candidate weight access:

1. Freeze the universal distribution contract:
   - no account/API key for local use;
   - offline after installation;
   - telemetry/network egress off by default;
   - no Docker/Python/Node.js requirement merely to launch basic coding assistance;
   - portable CPU runtime;
   - no build-from-source requirement for ordinary users.
2. Define the model-rights gate:
   - intended personal/commercial use;
   - modification/fine-tuning;
   - quantization/conversion;
   - derivative-weight/artifact redistribution;
   - end-user account/license obligations.
3. Define separate rights checks for:
   - datasets;
   - teacher/API outputs;
   - runtime libraries;
   - quantization/conversion tooling.
4. Pin every candidate by exact upstream revision before weight access.
5. Perform the current small-model landscape rescan immediately before the first download task.

## Phase C — base-model static qualification

Initial eligible static-qualification set:

1. `Qwen/Qwen3.5-2B-Base`;
2. `Qwen/Qwen3.5-4B-Base`;
3. `mistralai/Ministral-3-3B-Base-2512`;
4. `Qwen/Qwen3-4B-Base`;
5. `ibm-granite/granite-4.1-3b-base`;
6. `HuggingFaceTB/SmolLM3-3B-Base`.

Lower-bound code-specialized control:

7. `Qwen/Qwen2.5-Coder-1.5B`.

Explicitly exclude from primary-backbone admission:

- `Qwen/Qwen2.5-Coder-3B` because its current upstream Qwen Research License is non-commercial.

Static qualification records license/terms, architecture, total weight footprint, tokenizer, FIM suitability, vision components, CPU-runtime maturity, quantization maturity, and exact upstream revision before expensive testing.

## Phase D — task-scoped local artifact qualification

Only after Phase B/C evidence is canonical may an explicit task authorize bounded candidate weight access.

For each admitted candidate:

1. pin exact source revision and checksum;
2. build or obtain reproducibly identified Q4-class artifacts;
3. record quantization tool/revision/recipe;
4. test the portable CPU runtime path;
5. measure artifact size and whole-laptop memory pressure at 4K/8K/16K;
6. measure cold load, warm TTFA, sustained throughput, thermal behavior, and editor responsiveness;
7. measure Q4 degradation in coding, FIM, JSON/tool grammar, and edit grammar;
8. reject candidates that fail rights, footprint, runtime, or usability gates.

Where multiple Q4 variants are practical, compare at least one quality-oriented and one compatibility-oriented Q4 profile rather than treating all "Q4" artifacts as equivalent.

## Phase E — interaction contract bake-offs

Run interaction-contract experiments only on candidates that survived static/local qualification.

### Prompt/cache contract

Compare prompt orderings and tool-result serializers for:

- prefix-cache stability;
- minimal token overhead;
- model reliability;
- deterministic reconstruction;
- future compatibility with trained compaction/task state.

### Tool contract

Compare compact tool-call grammars and deterministic result serialization. Measure parse/schema failure rate, repair behavior, token overhead, and cache stability.

### Edit-format tournament

Compare at minimum:

- whole-file replacement;
- unified diff;
- search/replace blocks;
- patch-style anchored edits.

Measure:

- output token cost;
- parse/apply success;
- stale-edit recovery;
- formatting preservation;
- final correctness;
- behavior under concurrent/stale file modifications.

Select deterministic apply semantics before agent SFT/RL.

## Phase F — universal-laptop quality tournament

Run the same bounded protocol for each surviving candidate.

```text
STATIC + RIGHTS QUALIFICATION
-> LOCAL Q4 QUALIFICATION
-> INTERACTION CONTRACT V0
-> RAW EVAL
-> TOOL/EDIT EVAL
-> SMALL REPO EVAL
-> TTVC / WHOLE-LAPTOP EVAL
-> BOUNDED MICRO-ADAPTATION
-> RE-EVAL
-> TOP-1 OR TOP-2 DECISION
```

No winner may be selected from vendor-reported benchmark numbers or pre-adaptation ranking alone.

Measure both absolute capability and utility efficiency:

- verified completion rate;
- TTVC;
- verified completions/hour;
- verified completion per GB of process memory;
- quality loss from BF16/reference precision to Q4;
- whole-laptop responsiveness.

## Phase G — context tournament

Start from the cheapest system and add complexity only when measured value exists.

Arms:

1. ripgrep/exact search;
2. exact search + Tree-sitter RepoMap-style symbols;
3. + incremental sparse index;
4. + embeddings/reranker;
5. + SCIP where mature;
6. Graphify experimental arm;
7. Code-Graph-RAG experimental arm.

Metrics:

- localization recall;
- verified solve rate;
- context tokens;
- RAM overhead;
- disk/index footprint;
- startup/index time;
- incremental update latency;
- TTVC.

The shipped default must be the smallest arm on the solve-rate/token/latency/RAM/disk Pareto frontier. Index memory counts against the same 8 GB whole-laptop budget as the model.

## Phase H — environment factory MVP

Before agentic RL planning, prototype a small executable-task factory.

Required properties:

- known-good base environment;
- reproducible dependency state;
- reference patch/test proof;
- no-op failure proof;
- unsolved-state check;
- reward-shortcut battery;
- task metadata/provenance;
- fast reset/snapshot path;
- no future-history or public-solution leakage in the solver environment.

This phase measures CPU/storage/environment throughput before GPU RL budgets are committed.

## Phase I — privacy, security, and provenance

Before MSTR-001 planning is accepted:

- define repository-content trust boundaries and prompt-injection cases;
- define local network/telemetry defaults and secret-handling boundaries;
- define training-data provenance, opt-out, benchmark exclusion, and teacher-output rights records;
- define runtime benchmark-leakage controls;
- define evidence manifests binding model/runtime/artifact/config/hardware identities.

## Phase J — pre-training decision package

Produce a final decision artifact containing:

- supported universal-laptop hardware/OS floor;
- distribution/install/privacy contract;
- top backbone or top-two pilot candidates and why;
- selected local runtime baseline;
- Q4 artifact/acceptance thresholds;
- frozen Interaction Contract v1;
- selected edit format/apply semantics;
- minimal context engine and RAM/disk budget;
- TTFI/TTVC budget;
- environment-factory throughput estimate;
- bounded MSTR-001 training proposal;
- legal/provenance constraints for datasets and teacher outputs;
- explicit unresolved risks.

## Hard boundaries

During the MSTR-000 planning PR:

```text
NO MODEL WEIGHT DOWNLOAD
NO PAID MODEL API EXECUTION
NO RENTED TRAINING COMPUTE
```

After MSTR-000 planning is canonical, only an explicit task may authorize bounded pinned/checksummed weight access or paid/rented resources.

Throughout MSTR-000 qualification:

```text
NO LONG FULL-PARAMETER TRAINING
NO LARGE-SCALE RL
NO LARGE CORPUS INGESTION
NO FINAL BACKBONE ADMISSION BEFORE EVIDENCE
NO FINAL MODEL RELEASE
NO CLAIM OF BEATING CURSOR OR FABLE
NO SILENT HARDWARE-FLOOR INCREASE
```

Any experiment requiring paid API usage or non-trivial rented compute must state a cost ceiling before execution.
