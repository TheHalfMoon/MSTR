# MSTR-000B Source Adoption and Capability Mining Research — 2026-09-08

Status: PLANNING_RESEARCH_CANDIDATE  
External effects: NONE  
Model access: NONE  
Training: false  
Paid cost: USD 0.00

## Research question

Given Founder-stated permission to use source code from the studied sources, which implementation primitives or methods should MSTR selectively adopt, which should remain baselines or research references, and which new contracts are required to prevent source reuse from weakening local-first, reproducibility, governance, evaluator isolation, or authority boundaries?

## Decision method

Each source was evaluated for:

- direct effect on verifier-correct task completion and TTVC;
- value on 8 GB-class local systems;
- offline determinism and privacy compatibility;
- minimal primitive extractability;
- dependency and binary footprint;
- evaluator-isolation compatibility;
- resumability/recovery value;
- upstream churn risk;
- transitive asset and data implications;
- whether MSTR already has a simpler native baseline.

Source-project claims are treated as research inputs, not as MSTR evidence. A source's current upstream license and any retained attribution/NOTICE obligations still apply to copied/adapted code. Founder-stated source-use permission does not authorize third-party data, model weights, training, paid compute, or other external effects.

## Snapshot

The machine-readable companion is:

`artifacts/manifests/MSTR-source-adoption-research-snapshot-2026-09-08.json`

The snapshot pins immutable revisions observed during this research pass. Future adoption MUST reverify the upstream revision and record the exact adopted revision independently.

## Findings

### Tencent/LoopForge

Observed revision: `09c765286f549624dd95434e1e6ef2249657cbeb`

Decision: `ADOPT_PRIMITIVE` for resumable workflow/checkpoint semantics.

MSTR should mine the durable handoff/checkpoint pattern and phase separation, not import a second orchestration stack wholesale. The useful invariant is that a long task can resume from explicit repository/evidence state after process loss while revalidating live truth and authority.

Required MSTR contract: `ResumableTaskCheckpoint`.

### Tencent/SkillHone

Observed revision: `7d565839fb4dc74f9c77f09ace660e1c0484e048`

Decision: `ADOPT_PRIMITIVE` for persistent improvement history and optimizer/evaluator separation.

The high-value idea is not self-modification by itself. It is bounded whole-skill improvement where candidate changes are recorded, protected evaluation remains hidden from the optimizer, regressions block promotion, and discarded/crashed attempts remain negative evidence.

Required MSTR contract: `ImprovementDecisionRecord`.

### deepseek-ai/deepseek-harness

Observed revision: `c389f96a06005300336904239c409258129812c9`

Decision: `STUDY_METHOD` and `REJECT_FOR_CORE` for wholesale dependency.

The project is useful for harness compatibility and fast-moving implementation patterns, but that same churn makes it inappropriate as a mutable product-core dependency. MSTR may mine bounded primitives only after an immutable revision, behavior tests, and footprint review are recorded.

### SWE-agent/mini-swe-agent

Observed revision: `d8563a7d213dd2472c18314992b9435527a11eaf`

Decision: `REFERENCE_BASELINE`.

Its small bash-oriented tool surface provides a strong anti-complexity control. Any richer MSTR harness should prove that additional state, tools, dependencies, or orchestration improve verifier-correct completion or TTVC enough to pay for their footprint and failure surface.

Required baseline: `MINIMAL_BASH_LINEAR_BASELINE`.

### SWE-agent/SWE-ReX

Observed revision: `a978f8924522bb72c0d5a876b3990d41d432decf`

Decision: `ADOPT_PRIMITIVE` for execution/session abstraction.

MSTR should extract the interface idea—execution backend identity, session lifecycle, streaming, timeouts, cancellation, reset/snapshot, and isolation—while keeping local subprocess execution as the default baseline. Docker/remote backends remain optional profiles rather than mandatory product dependencies.

Required MSTR contract: `ExecutionBackendProfile`.

### Aider-AI/aider

Observed revision: `2a8d8b739a7be305f570963240f8f96ba62c90d0`

Decision: `ADOPT_PRIMITIVE` for deterministic repository-context ranking ideas.

MSTR should benchmark a ladder from grep/find to syntax/symbol indexing to a token-budgeted ranked repository map. The index must be disposable, stale-aware, deterministic, offline-capable, and subordinate to the checked-out repository tree.

Required MSTR contract: `RepositoryContextIndexProfile`.

### IFM xLLM / horizon-post-train / Uno

Observed revisions:

- `ifm-ai/xllm`: `dbae8d5667c61f5f4b313b0169d8acd8f102373a`
- `ifm-ai/horizon-post-train`: `023c0f7b9de5da693d435a196b0fd436dddb0438`
- `ifm-ai/uno`: `46fbdb66f026bae9c68a1e5a3f97a17c7805c778`

Decision: `STUDY_METHOD`.

These sources are useful for local model lifecycle, post-training architecture, and parallel-generation research. They do not create candidate admission or training authority. Any method moved toward implementation must first fit the MSTR 8 GB/local-first boundary and be compared with the existing reference runtime.

### Tencent/AngelSlim

Observed revision: `ee8ddb2b43e20800bcfdda1e9ac34ea2aab5de5d`

Decision: `STUDY_METHOD`.

Compression and speculative-decoding techniques are relevant to TTVC and memory pressure, but the broader toolkit and speculative-draft training surface are too large to import into the baseline automatically. MSTR should first measure native capabilities in the already pinned inference runtime and only then justify a custom/source-derived path.

### ggml-org/llama.cpp

Observed revision: `67672dc5b76f8bc17785a19d3dc6d1463fc2902c`

Decision: `REFERENCE_BASELINE`.

Before MSTR adds custom speculative or parallel decoding, it should benchmark the compatible native llama.cpp path under the same model, prompts, resource limits, and correctness gates. Existing pinned runtime/toolchain governance remains authoritative; this observed revision does not replace current runtime locks.

### unslothai/unsloth

Observed revision: `132f1155a62f98cbb95f2d07b10a666599b7d7dc`

Decision: `REFERENCE_BASELINE` for accelerated training only after separate training authority.

Speed and memory savings are useful only if training semantics and resulting artifacts remain equivalent enough for MSTR's reproducibility contract. A reference Transformers + PEFT/TRL lane and accelerated lane need a bounded parity record before backend promotion.

Required MSTR contract: `TrainingBackendParityRecord`.

### bigcode-project/selfcodealign

Observed revision: `045354e1f60ed01b0652ff9716359bb73d246740`

Decision: `STUDY_METHOD`.

Useful concepts include synthetic instruction/task generation and execution filtering. MSTR keeps its stronger verifier separation, provenance ledger, data constitution, held-out evaluation, and contamination controls. No upstream dataset becomes admitted by this research.

### facebookresearch/swe-rl

Observed revision: `5aa10d67f1db07ecd3a20483d63fe2d5029ac9c9`

Decision: `STUDY_METHOD`.

The software-evolution task/reward framing is useful for curriculum and research-ladder design. The repository's mixed licensing and research-code caveats make method-level study preferable to wholesale code adoption. Any data or RL execution remains separately governed.

### facebookresearch/ProgramBench

Observed revision: `963063c9271cc40fa179977356782ea4582e0b0c`

Decision: `REFERENCE_BASELINE` for behavioral reconstruction evaluation.

The useful capability is whole-program behavioral reconstruction from permitted documentation and executable behavior rather than source visibility. MSTR can add a bounded hidden-test lane that evaluates observable behavior while maintaining evaluator secrecy.

### microsoft/FEA-Bench

Observed revision: `fb3c11274796f6057bf447410540fcf2fa1d90b1`

Decision: `STUDY_METHOD` only.

The feature-implementation benchmark design is useful, but the full evaluation dataset is not simply the repository source code; upstream documentation indicates additional repository content is acquired from GitHub. Therefore source-code permission MUST NOT be treated as permission to scrape or admit that evaluation/training data.

### CodeClash-ai/CodeClash

Observed revision: `f0694c64ecf6abfca2bc867bad2de9333fef5be8`

Decision: `STUDY_METHOD`.

Long-horizon goal-oriented software engineering is a useful direction for post-foundation evaluation. MSTR should first build deterministic local fixtures and avoid inheriting mandatory container/network/token assumptions into the baseline.

### karpathy/autoresearch

Observed revision: `228791fb499afffb54b46200aca536f79142f117`

Decision: `REFERENCE_BASELINE` for bounded research-controller semantics.

The useful pattern is propose → bounded run → measure → keep/discard/crash → durable log. MSTR strengthens it with immutable negative evidence, frozen evaluator ownership, authority checks before any external effect, and explicit stop conditions.

## Gaps found in the existing MSTR plan

1. No first-class contract distinguished source-code permission from data/model/training/external-effect authority.
2. No canonical record existed for copied/adapted source code, revision, license/NOTICE, transitive dependencies, behavior tests, update policy, and rollback.
3. Harness complexity had no explicit minimal-agent control baseline.
4. Execution backends were not normalized under a backend/session/reset/streaming/isolation contract.
5. Long-running task resumability depended too heavily on conversational/process continuity rather than a small durable checkpoint contract.
6. Self-improvement lacked a single immutable keep/discard/crash decision record with explicit optimizer/evaluator separation.
7. Repository-context indexing lacked an explicit staged ladder, token budget, stale invalidation, and fallback contract.
8. Accelerated training backends lacked an artifact/semantic parity gate against the reference path.
9. Runtime acceleration did not explicitly require native pinned-runtime acceleration to be measured before custom source-derived techniques.
10. Behavioral reconstruction was missing as a distinct whole-program evaluation lane.
11. Upstream source refresh/churn and rollback policy was not explicit enough for copied primitives.
12. Donor-project claims could be misread as evidence without a stronger research-signal/evidence boundary.

## Plan consequences

The canonical planning amendment SHOULD add:

- `SourceAdoptionRecord`
- `ExecutionBackendProfile`
- `ResumableTaskCheckpoint`
- `ImprovementDecisionRecord`
- `RepositoryContextIndexProfile`
- `TrainingBackendParityRecord`
- `MINIMAL_BASH_LINEAR_BASELINE`
- baseline-first runtime acceleration
- behavioral reconstruction evaluation
- immutable upstream revision/update/rollback governance

Completed B014–B030 work remains historical and is not reopened. B031 retains its existing dependency and authority semantics. B032 freezes these source-adoption interfaces and downstream MSTR-000A obligations. B033 red-teams them. B034 performs final MSTR-000B closeout only after those requirements are canonical and satisfied.
