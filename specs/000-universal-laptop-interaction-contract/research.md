# MSTR-000 Research

**Purpose:** record research decisions that justify the MSTR-000 implementation plan. Upstream facts must be revalidated at execution time before irreversible or paid action.

## Decision 1 — Use Spec Kit as the Planning/Execution Backbone

MSTR uses constitution -> specification -> clarification -> research -> plan -> data model/contracts/quickstart -> tasks -> review/analyze -> implement -> converge/closeout. The official Spec Kit workflow makes `spec.md` requirements/user-story authority, `plan.md` technical execution authority, `tasks.md` the dependency-ordered implementation queue, and `.specify/memory/constitution.md` live governance.

Primary source: https://github.com/github/spec-kit

## Decision 2 — Universal-Laptop Primary, Not Sub-10B Marketing

The product search space is constrained by actual laptop usability: 8 GB total RAM, CPU-only, 8K reference context, OS + editor + medium repo + MSTR, Q4 artifact target <=3 GB, no mandatory cloud/account/API. Selecting the strongest <10B model first and optimizing deployment later is rejected.

## Decision 3 — Tournament Approximately 2B–4B Dense Foundations

Initial candidates: Qwen3.5 2B/4B, Ministral 3B, Qwen3 4B, Granite 4.1 3B, SmolLM3 3B, plus Qwen2.5-Coder 1.5B control. The set is rescanned before weight access. No model is selected by reputation.

## Decision 4 — Rights Gate Precedes Weight Access

Candidate qualification fails closed for commercial use, modification/fine-tuning, quantization/conversion, and derivative redistribution. Dataset, teacher/API-output, runtime, and tooling rights are independent checks. Qwen2.5-Coder-3B remains a reference-only/ineligible primary candidate while current restrictions remain.

## Decision 5 — Separate Research Harness From Product Runtime

Build MSTR-000 qualification tooling in Python for fast reproducible experiments; defer the final end-user runtime implementation. The eventual product should favor self-contained cross-platform packaging after model/backend constraints are known.

## Decision 6 — TTVC Is the North-Star Speed Metric

Optimize Time To Verified Completion with TTFI/TTFA/TTFCE, solve rate, whole-system memory, responsiveness, sustained throughput, and artifact/install burden. Tokens/sec is supporting evidence only.

## Decision 7 — Freeze Interaction Contract Before Material SFT/RL

Version prompt/chat prefix, FIM semantics, tool grammar, result serialization, edit grammar, stale-write behavior, context ordering, and serving/cache assumptions before material agent training.

## Decision 8 — Deterministic Apply v1

Start with deterministic stale-safe editing. A learned apply model is deferred unless experiments prove enough value.

## Decision 9 — Minimal Context Engine First

Tournament order: exact search -> Tree-sitter/RepoMap-style symbols -> sparse index -> embeddings/reranker -> SCIP -> Graphify -> Code-Graph-RAG. Heavy systems must earn RAM/disk/latency complexity.

Relevant projects: https://github.com/Graphify-Labs/graphify and https://github.com/vitali87/code-graph-rag plus Tree-sitter/SCIP/Aider-style RepoMap concepts.

## Decision 10 — Harness Diversity, Canonical Trajectory Schema Later

Future training may adapt multiple SWE harnesses (DeepSeek Harness, mini-swe-agent, SWE-agent, OpenHands, Harbor, SWE-smith/SWE-Next-like sources), but MSTR should preserve task/action/result/patch/verifier semantics rather than permanently bind to one syntax.

## Decision 11 — Environment/Verifier Quality Before RL Framework Selection

Prototype reference-pass/no-op-fail/unsolved checks, reward shortcuts, leakage controls, and reset/reproducibility metrics before committing to large-scale RL.

## Decision 12 — RL Direction Remains Provisional

`slime` is a leading future candidate for coding-agent long-horizon RL; `verl`/specialized speculative co-training and other frameworks remain comparison paths. MSTR-000 does not select the final RL framework.

## Decision 13 — Preserve FIM During Later Post-Training

FIM/code-completion remains a regression surface and later mixes should retain FIM replay as needed so agent training does not destroy direct coding ability.

## Decision 14 — Public Benchmarks Are Secondary Evidence

Use public coding/SWE/terminal benchmark families for continuity, but maintain a private/fresh MSTR Gauntlet. Exact benchmark validity is re-reviewed at release-candidate time.

## Decision 15 — Raw Model and System Quality Must Be Separated

Every material comparison has raw model, neutral minimal harness, and full MSTR system surfaces.

## Decision 16 — Vision Is Optional, Not a MSTR-000 Requirement

A multimodal base may retain vision if laptop artifact/RAM/runtime requirements still pass; text/code SWE remains the first release-critical path.

## Decision 17 — Program Uses Gated Workstreams

MSTR-000 does not pretend to know final token mix, teacher, RL scale, or speculative decoder. `docs/canonical/PROGRAM_ROADMAP.md` defines the sequence and each later workstream derives detail from predecessor evidence.

## Research Risks Remaining

1. A 2B model may deploy well but miss SWE quality.
2. A 4B model may exceed comfortable 8 GB behavior at 8K.
3. Hybrid architectures may have weaker local quantization/runtime support.
4. Q4 may hurt tool/FIM/JSON reliability.
5. Repository retrieval may be the quality bottleneck for small models.
6. CPU thermal limits may dominate perceived speed.
7. Model/data/teacher terms may block attractive paths.
8. Public benchmark scores may not correlate with laptop TTVC.
9. Environment/verifier throughput may dominate RL cost.
10. Agent optimization may degrade raw coding/FIM without replay gates.

## Primary Research Thesis

MSTR's strongest defensible path is to maximize **verified software-engineering utility per GB, per second, and per unit of training evidence** through a compact strong base, precise repository localization, deterministic editing, executable verification, stable interaction contracts, high-quality execution-grounded post-training, and local inference co-design.
