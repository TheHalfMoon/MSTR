# MSTR-000 Specification — Universal Laptop Interaction Contract + Base/Local/Speed Qualification

## 1. Purpose

MSTR-000 must determine the smallest technically credible model/runtime contract capable of becoming a best-in-class local software-engineering system while remaining practical on ordinary laptops.

This specification does **not** authorize long training, final backbone selection, or a production model release.

## 2. Primary user outcome

A user with an ordinary laptop should be able to install MSTR, open a real repository, ask for a coding task, and receive useful local assistance without a cloud subscription or discrete GPU.

## 3. Universal Laptop Gate

The primary MSTR release must be designed around the following provisional qualification envelope:

```text
REFERENCE_RAM = 8_GB
DISCRETE_GPU = ABSENT
CPU_ONLY_OPERATION = REQUIRED
CPU_ARCH = X86_64_OR_ARM64
PRIMARY_QUANT = Q4_CLASS
DOWNLOAD_SIZE_TARGET = <= 3_GB
BOUNDED_CONTEXT_WORKING_SET_TARGET = <= 6_GB
WINDOWS = REQUIRED
LINUX = REQUIRED
MACOS = REQUIRED
OFFLINE_OPERATION = REQUIRED
```

MSTR-000 must replace provisional values with measured limits. A candidate that cannot satisfy the universal-laptop envelope cannot become the primary flagship, regardless of benchmark quality.

## 4. Quality goals

The primary model must be optimized for:

- code generation and completion;
- repository localization and understanding;
- debugging and repair;
- tool use;
- build/test iteration;
- FIM and surgical editing;
- concise planning;
- security-aware behavior;
- recovery from failed attempts.

MSTR may use a lightweight runtime to improve repository intelligence and verification, but raw model quality must remain independently measurable.

## 5. Speed goals

MSTR must optimize end-to-end software-engineering latency, not only decoding throughput.

Required metrics:

```text
TTFA = TIME_TO_FIRST_ACTION
TTFCE = TIME_TO_FIRST_CORRECT_EDIT
TTVC = TIME_TO_VERIFIED_COMPLETION
```

`TTVC` is the primary speed metric.

The qualification suite must separately account for:

- model load/start latency;
- prompt/prefix prefill;
- decoding;
- repository search;
- edit application;
- tool round trips;
- build/test time;
- retries and recovery.

## 6. Interaction Contract

Before expensive training, MSTR must freeze a versioned interaction contract covering:

- backbone family and tokenizer;
- chat/prompt template;
- stable prefix-cache layout;
- FIM control tokens;
- tool-call grammar;
- edit grammar;
- tool-result serialization;
- context ordering;
- filesystem version/stale-write semantics;
- baseline local inference backend;
- cache semantics.

Changing this contract after agent SFT/RL begins requires explicit migration evidence.

## 7. Primary base-model tournament

The initial primary candidate class is dense models approximately 2B–4B parameters.

Required initial candidates:

- `Qwen/Qwen3.5-2B-Base`;
- `Qwen/Qwen3.5-4B-Base`;
- `mistralai/Ministral-3-3B-Base-2512`;
- `Qwen/Qwen3-4B-Base`;
- `Qwen/Qwen2.5-Coder-3B` or its appropriate base/control form.

Additional candidates may enter only if they meet redistribution and laptop-deployment requirements.

Models with low active parameters but very large total weight storage are not automatically laptop candidates. Total memory/storage footprint is part of the gate.

## 8. Tournament dimensions

No candidate may win from a single benchmark score.

Measure at minimum:

### Raw model
- fresh coding;
- FIM;
- code reasoning;
- multilingual code;
- tool/schema reliability.

### Local deployment
- Q4 artifact size;
- peak resident memory;
- cold load time;
- warm TTFA;
- code characters/second and tokens/second;
- long-context memory growth;
- CPU-only behavior;
- Windows/Linux/macOS runtime maturity.

### Repository work
- file localization;
- symbol localization;
- edit validity;
- small real-repository repair tasks;
- verified completion rate;
- TTVC.

The top candidates must survive a bounded micro-SFT or equivalent adaptation experiment before final backbone selection. Pre-adaptation ranking alone is insufficient.

## 9. Runtime constraints

The v1 runtime should remain minimal:

```text
REQUIRED:
- exact/ripgrep-style search
- Tree-sitter symbol outline
- incremental lightweight index if proven useful
- deterministic stale-safe apply engine
- shell/test/build tools inside bounded workspace
- deterministic verifier path

OPTIONAL / TOURNAMENT:
- SCIP
- embeddings
- Graphify
- Code-Graph-RAG

NOT_V1_DEFAULT:
- mandatory graph database
- multi-agent swarm
- learned apply model
- cloud dependency
```

Every optional context component must prove additional verified solve rate relative to its latency, memory, and token cost.

## 10. Evaluation integrity

MSTR must maintain three separate score surfaces:

1. raw model;
2. model + neutral minimal harness;
3. full MSTR system.

Public benchmarks are supporting evidence, not project truth. MSTR must develop a private, post-cutoff, hidden-test `MSTR Gauntlet` before major training decisions are finalized.

Training-time contamination and runtime answer leakage are separate failure modes and must be controlled independently.

## 11. Non-goals for MSTR-000

MSTR-000 does not:

- select a final backbone;
- download or admit model weights;
- ingest large corpora;
- run long SFT/RL;
- build a production GUI;
- add subagent swarms;
- build a graph database;
- claim superiority over Cursor, Fable, or any other system.

## 12. Exit criteria

MSTR-000 may close only when evidence is sufficient to freeze:

1. the universal laptop hardware floor;
2. the top backbone choice or top-two pilot set;
3. the Q4/local inference baseline;
4. the prompt/tool/edit interaction contract;
5. the deterministic apply semantics;
6. the minimal context engine;
7. the TTVC measurement harness;
8. the environment-factory MVP requirements;
9. the first bounded training experiment.

If no 2–4B candidate can meet both the quality and laptop gates, the project must explicitly choose between reducing quality ambitions or creating a tiered MSTR family. It must not silently raise the primary hardware requirement.
