# MSTR-000 Plan

## Objective

Empirically freeze the smallest interaction/runtime contract that can support a best-in-class local software-engineering experience on ordinary laptops before expensive training begins.

## Phase A — measurement contract

1. Define reference laptop classes:
   - 8 GB RAM CPU-only baseline;
   - 16 GB RAM CPU-only secondary;
   - Apple Silicon reference;
   - Windows x86_64 reference;
   - Linux x86_64 reference.
2. Define measurement fields for:
   - artifact size;
   - peak RSS/working set;
   - cold model load;
   - warm TTFA;
   - tokens/sec and source-code characters/sec;
   - TTVC;
   - Q4 correctness regressions.
3. Freeze a versioned benchmark manifest before candidate scoring.

## Phase B — interaction contract bake-offs

### Prompt/cache contract

Compare prompt orderings and tool-result serializers for cache stability, minimal token overhead, and model reliability.

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
- final correctness.

Select deterministic apply semantics before agent SFT/RL.

## Phase C — universal-laptop base tournament

Run the same bounded protocol for each admitted candidate.

Initial set:

1. Qwen3.5-2B-Base;
2. Qwen3.5-4B-Base;
3. Ministral-3-3B-Base-2512;
4. Qwen3-4B-Base;
5. Qwen2.5-Coder-3B control.

Tournament stages:

```text
STATIC QUALIFICATION
-> LOCAL Q4 QUALIFICATION
-> RAW EVAL
-> TOOL/EDIT CONTRACT EVAL
-> SMALL REPO TASK EVAL
-> BOUNDED MICRO-ADAPTATION
-> RE-EVAL
-> TOP-2 DECISION
```

Do not select a winner from vendor-reported benchmark numbers.

## Phase D — context tournament

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
- index time;
- incremental update latency;
- TTVC.

The shipped default must be the smallest arm on the Pareto frontier.

## Phase E — environment factory MVP

Before agentic RL planning, prototype a small executable-task factory.

Required properties:

- known-good base environment;
- reproducible dependency state;
- reference patch/test proof;
- no-op failure proof;
- reward-shortcut battery;
- task metadata/provenance;
- fast reset/snapshot path.

This phase measures CPU/storage/environment throughput before GPU RL budgets are committed.

## Phase F — pre-training decision package

Produce a final decision artifact containing:

- supported universal-laptop floor;
- top-two base candidates and why;
- selected local runtime baseline;
- Q4 acceptance thresholds;
- frozen interaction contract;
- selected edit format/apply semantics;
- minimal context engine;
- TTVC budget;
- environment-factory throughput estimate;
- bounded MSTR-001 training proposal;
- explicit unresolved risks.

## Hard boundaries

During MSTR-000 planning and qualification:

```text
NO LONG FULL-PARAMETER TRAINING
NO LARGE-SCALE RL
NO LARGE CORPUS INGESTION
NO FINAL MODEL RELEASE
NO CLAIM OF BEATING CURSOR OR FABLE
NO SILENT HARDWARE-FLOOR INCREASE
```

Any experiment requiring model-weight download, paid API usage, or non-trivial rented compute must be executed as an explicit task with recorded cost and evidence.
