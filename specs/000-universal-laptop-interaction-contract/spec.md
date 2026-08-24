# MSTR-000 Specification — Universal Laptop Interaction Contract + Base/Local/Speed Qualification

## 1. Purpose

MSTR-000 must determine the smallest technically credible model/runtime/distribution contract capable of becoming a best-in-class local software-engineering system while remaining practical on ordinary laptops.

This specification does **not** authorize long training, final backbone selection, or a production model release.

## 2. Primary user outcome

A user with an ordinary laptop should be able to install MSTR, open a real repository, ask for a coding task, and receive useful local assistance without a cloud subscription, provider account, API key, or discrete GPU.

## 3. Universal Laptop Gate

The primary MSTR release must be designed around the following provisional qualification envelope:

```text
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONCURRENT_LOAD = OS + REFERENCE_EDITOR + MSTR
DISCRETE_GPU = ABSENT
CPU_ONLY_OPERATION = REQUIRED
CPU_ARCH = X86_64_OR_ARM64
PRIMARY_QUANT = Q4_CLASS
DOWNLOAD_SIZE_TARGET = <= 3_GB
REFERENCE_CONTEXT = 8192_TOKENS
CONTEXT_LADDER = 4096 / 8192 / 16384
MSTR_PROCESS_RSS_SOFT_TARGET = <= 4_GB_AT_REFERENCE_CONTEXT
NO_SUSTAINED_SWAP_THRASHING = REQUIRED
BASIC_MODE_DOCKER_REQUIRED = NO
ACCOUNT_REQUIRED = NO
API_KEY_REQUIRED = NO
OFFLINE_AFTER_INSTALL = REQUIRED
TELEMETRY_DEFAULT = OFF
WINDOWS = REQUIRED
LINUX = REQUIRED
MACOS = REQUIRED
```

MSTR-000 must replace provisional values with measured limits. A candidate that cannot satisfy the whole-laptop envelope cannot become the primary flagship, regardless of benchmark quality.

The reference context is intentionally far below vendor maximum-context claims. MSTR must prefer retrieval/compaction over unusable KV-cache growth on low-memory systems. The 4K/8K/16K ladder must be measured separately.

The final OS/CPU matrix must distinguish, rather than blur together, at least Windows x86_64, Linux x86_64, macOS arm64, and any additional ARM64/legacy paths actually proven.

## 4. Universal Distribution and Install Gate

The primary MSTR release must be distributable and usable by ordinary users.

At minimum, MSTR-000 must freeze requirements for:

- no provider login or API key for local use;
- offline operation after the artifact/runtime are installed;
- telemetry/network egress off by default;
- no Docker/Python/Node.js requirement merely to launch basic coding assistance;
- a portable CPU runtime path for the primary artifact;
- reproducible artifact checksums and build/quantization provenance;
- a simple installation/first-run path that does not require building MSTR from source;
- model/backbone rights compatible with intended use, fine-tuning, quantization, and redistribution of derivative MSTR weights/artifacts;
- compatible runtime/tool dependency licenses;
- teacher/API-output and dataset terms checked independently before their data can enter MSTR training.

A research-only, non-commercial-only, or otherwise incompatible backbone cannot become the primary MSTR model.

## 5. Quality goals

The primary model must be optimized for:

- code generation and completion;
- repository localization and understanding;
- debugging and repair;
- tool use;
- build/test iteration;
- FIM and surgical editing;
- concise planning;
- security-aware behavior;
- recovery from failed attempts;
- multilingual developer instructions without sacrificing code quality.

MSTR may use a lightweight runtime to improve repository intelligence and verification, but raw model quality must remain independently measurable.

## 6. Speed and Laptop-Experience Goals

MSTR must optimize end-to-end software-engineering latency, not only decoding throughput.

Required metrics:

```text
TTFI = TIME_FROM_INSTALL_START_TO_FIRST_LOCAL_INTERACTION
TTFA = TIME_TO_FIRST_ACTION
TTFCE = TIME_TO_FIRST_CORRECT_EDIT
TTVC = TIME_TO_VERIFIED_COMPLETION
```

`TTVC` is the primary task-speed metric; `TTFI` is the primary installability metric.

The qualification suite must separately account for:

- artifact/runtime installation and first launch;
- model load/start latency;
- prompt/prefix prefill;
- decoding;
- repository search/indexing;
- edit application;
- tool round trips;
- build/test time;
- retries and recovery;
- model-process RSS and total-system available memory;
- page faults/swap behavior;
- sustained CPU performance/thermal throttling;
- energy per task where the platform exposes a reliable measurement.

CPU throughput must be reported both in tokens/second and source-code characters/second because tokenizer efficiency changes perceived speed.

## 7. Interaction Contract

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
- cache semantics;
- network/privacy semantics visible to the model;
- deterministic task-state/compaction schema if used.

Changing this contract after agent SFT/RL begins requires explicit migration evidence.

## 8. Candidate Admission Gate

Before any candidate weight is downloaded for MSTR qualification, static evidence must record:

- exact upstream repository/model ID and revision;
- model license and any linked terms;
- permission for intended personal and commercial use;
- permission for modification/fine-tuning;
- permission for quantization/conversion;
- permission for redistribution of derivative weights/artifacts;
- whether end users would need a separate provider account/license;
- architecture/tokenizer/vision components and total parameter/weight footprint;
- portable CPU-runtime maturity;
- known quantization and local-backend constraints.

Failing the rights gate makes a model ineligible as the primary backbone even if it remains useful as a separately labeled research reference.

## 9. Primary Base-Model Tournament

The initial primary candidate class is dense models approximately 2B–4B parameters, plus a deliberately smaller code-specialized lower-bound control.

Required initial static-qualification candidates:

- `Qwen/Qwen3.5-2B-Base`;
- `Qwen/Qwen3.5-4B-Base`;
- `mistralai/Ministral-3-3B-Base-2512`;
- `Qwen/Qwen3-4B-Base`;
- `ibm-granite/granite-4.1-3b-base`;
- `HuggingFaceTB/SmolLM3-3B-Base`;
- `Qwen/Qwen2.5-Coder-1.5B` as a lower-bound code-specialized control.

`Qwen/Qwen2.5-Coder-3B` is not an eligible primary candidate because the current upstream license is the Qwen Research License with non-commercial restrictions.

Additional candidates may enter only if they pass the same rights and laptop-deployment gate. Models with low active parameters but very large total weight storage are not automatically laptop candidates.

Post-trained small models such as `microsoft/Phi-4-mini-instruct` may be used as ready-made local comparison points, but they are not substitutes for a clean foundation-candidate evaluation unless a suitable base checkpoint and rights are separately qualified.

## 10. Tournament Dimensions

No candidate may win from a single benchmark score.

Measure at minimum:

### Raw model
- fresh coding;
- FIM;
- code reasoning;
- multilingual code;
- multilingual natural-language task instructions;
- tool/schema reliability.

### Local deployment
- reproducible Q4 artifact size and exact quantization recipe;
- peak process RSS and total-system memory pressure;
- 4K/8K/16K context memory growth;
- cold load time;
- warm TTFA;
- code characters/second and tokens/second;
- CPU-only behavior;
- sustained performance/thermal throttling;
- optional hardware acceleration as a bonus, never a requirement;
- Windows/Linux/macOS runtime maturity;
- install/first-run friction.

### Repository work
- file localization;
- symbol localization;
- edit validity;
- small real-repository repair tasks;
- verified completion rate;
- TTVC;
- whole-system responsiveness while a reference editor is open.

The top candidates must survive an equivalent bounded micro-SFT or adaptation experiment before final backbone selection. Pre-adaptation ranking alone is insufficient.

## 11. Runtime Constraints

The v1 runtime should remain minimal:

```text
REQUIRED:
- portable CPU inference backend
- exact/ripgrep-style search
- Tree-sitter symbol outline
- incremental lightweight index if proven useful
- deterministic stale-safe apply engine
- bounded workspace tools
- deterministic verifier path
- offline/basic mode without Docker
- no telemetry/network egress by default

OPTIONAL / TOURNAMENT:
- hardware acceleration
- SCIP
- embeddings/reranker
- Graphify
- Code-Graph-RAG

NOT_V1_DEFAULT:
- mandatory graph database
- multi-agent swarm
- learned apply model
- cloud dependency
```

Every optional context component must prove additional verified solve rate relative to its latency, memory, disk/index cost, and token cost. Context-engine RAM is part of the whole-laptop budget, not free overhead.

## 12. Evaluation Integrity and Reproducibility

MSTR must maintain three separate score surfaces:

1. raw model;
2. model + neutral minimal harness;
3. full MSTR system.

Every published material result must bind to exact model/artifact hashes, tokenizer revision, quantization recipe/tool version, runtime version/build flags, hardware, context/cache settings, interaction-contract version, task manifest, and seed where applicable.

Public benchmarks are supporting evidence, not project truth. MSTR must develop a private, post-cutoff, hidden-test `MSTR Gauntlet` before major training decisions are finalized.

Training-time contamination and runtime answer leakage are separate failure modes and must be controlled independently.

## 13. Non-goals for MSTR-000

MSTR-000 does not:

- select a final backbone before qualification evidence;
- authorize candidate weights before an explicit canonical task;
- ingest large corpora;
- run long SFT/RL;
- build a production GUI;
- add subagent swarms;
- build a graph database;
- require Docker for basic local assistance;
- claim superiority over Cursor, Fable, or any other system.

## 14. Exit Criteria

MSTR-000 may close only when evidence is sufficient to freeze:

1. the universal laptop hardware/OS floor;
2. the distribution/install/privacy contract;
3. the top backbone choice or top-two pilot set;
4. the Q4/local inference baseline and artifact provenance contract;
5. the prompt/tool/edit interaction contract;
6. the deterministic apply semantics;
7. the minimal context engine and its RAM/disk budget;
8. the TTVC/TTFI measurement harness;
9. the environment-factory MVP requirements;
10. the first bounded training experiment;
11. the legal/provenance requirements for training data and any teacher outputs.

If no approximately 2B–4B candidate can meet both the quality and laptop gates, the project must explicitly choose between reducing quality ambitions or creating a tiered MSTR family. It must not silently raise the primary hardware requirement.
