# MSTR-000 Research

**Purpose:** record research decisions that justify the MSTR-000 implementation plan. Upstream facts must be revalidated at execution time before irreversible, paid, or external-compute action.

## Decision 1 — Use Spec Kit as the Planning/Execution Backbone

MSTR uses constitution -> specification -> clarification -> research -> plan -> data model/contracts/quickstart -> tasks -> review/analyze -> implement -> converge/closeout.

Primary source: https://github.com/github/spec-kit

## Decision 2 — Universal-Laptop Primary, Not Sub-10B Marketing

The product search space is constrained by actual laptop usability: 8 GB total RAM, CPU-only, 8K reference context, OS + editor + medium repo + MSTR, Q4 artifact target <=3 GB, no mandatory cloud/account/API.

## Decision 3 — Tournament Approximately 2B–4B Dense Foundations

Initial candidates: Qwen3.5 2B/4B, Ministral 3B, Qwen3 4B, Granite 4.1 3B, SmolLM3 3B, plus Qwen2.5-Coder 1.5B control. The set is rescanned before weight access. No model is selected by reputation.

## Decision 4 — Rights Gate Precedes Weight Access

Candidate qualification fails closed for commercial use, modification/fine-tuning, quantization/conversion, and derivative redistribution. Dataset, teacher/API-output, runtime, and tooling rights are independent checks.

## Decision 5 — Separate Research Harness From Product Runtime

Build MSTR-000 qualification tooling in Python for fast reproducible experiments; defer the final end-user runtime implementation.

## Decision 6 — TTVC Is the North-Star Speed Metric

Optimize Time To Verified Completion with TTFI/TTFA/TTFCE, solve rate, whole-system memory, responsiveness, sustained throughput, and artifact/install burden. Tokens/sec is supporting evidence only.

## Decision 7 — Freeze Interaction Contract Before Material SFT/RL

Version prompt/chat prefix, FIM semantics, tool grammar, result serialization, edit grammar, stale-write behavior, context ordering, and serving/cache assumptions before material agent training.

## Decision 8 — Deterministic Apply v1

Start with deterministic stale-safe editing. A learned apply model is deferred unless experiments prove enough value.

## Decision 9 — Minimal Context Engine First

Tournament order: exact search -> Tree-sitter/RepoMap-style symbols -> sparse index -> embeddings/reranker -> SCIP -> Graphify -> Code-Graph-RAG. Heavy systems must earn RAM/disk/latency complexity.

Relevant projects:
- https://github.com/Graphify-Labs/graphify
- https://github.com/vitali87/code-graph-rag

## Decision 10 — Harness Diversity, Canonical Trajectory Semantics Later

Future training may adapt multiple SWE harnesses such as DeepSeek Harness, mini-swe-agent, SWE-agent, OpenHands, Harbor, SWE-smith/SWE-Next-like sources, but MSTR data/contracts must not bind permanently to one syntax.

## Decision 11 — Environment/Verifier Quality Before RL Framework Selection

Prototype reference-pass/no-op-fail/unsolved checks, reward shortcuts, leakage controls, and reset/reproducibility metrics before committing to large-scale RL.

## Decision 12 — RL Direction Remains Provisional

`slime` is a leading future candidate for coding-agent long-horizon RL; `verl` and other frameworks remain comparison paths. MSTR-000 does not select the final RL framework.

## Decision 13 — Preserve FIM During Later Post-Training

FIM/code-completion remains a regression surface and later mixes should retain FIM replay as needed so agent training does not destroy direct coding ability.

## Decision 14 — Public Benchmarks Are Secondary Evidence

Use public coding/SWE/terminal benchmark families for continuity, but maintain a private/fresh MSTR Gauntlet.

## Decision 15 — Raw Model and System Quality Must Be Separated

Every material comparison has raw model, neutral minimal harness, and full MSTR system surfaces.

## Decision 16 — Vision Is Optional, Not a MSTR-000 Requirement

A multimodal base may retain vision if laptop artifact/RAM/runtime requirements pass; text/code SWE remains the first release-critical path.

## Decision 17 — Program Uses Gated Workstreams

MSTR-000 does not pretend to know final token mix, teacher, RL scale, or speculative decoder. Each later workstream derives detail from predecessor evidence.

## Decision 18 — Google Colab + Unsloth Is the Preferred Accessible Training Lane

This is a training-execution decision, not a product dependency.

As of 2026-08-24, Unsloth documents Qwen3.5 fine-tuning support including compact 0.8B/2B/4B variants and provides Colab notebooks. It also documents LoRA/SFT/RL-oriented workflows and GGUF export.

Sources to revalidate before execution:
- https://unsloth.ai/docs/models/qwen3.5/fine-tune
- https://unsloth.ai/docs/get-started/fine-tuning-llms-guide
- https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf

The framework remains replaceable; MSTR training data, manifests, and evaluation contracts must remain framework-neutral.

## Decision 19 — Qwen3.5 QLoRA Is Not the Default Pilot

Current Unsloth guidance specifically advises against 4-bit QLoRA for Qwen3.5 due to higher-than-normal quantization differences. If Qwen3.5 2B/4B wins the MSTR tournament, the first pilot should therefore use 16-bit LoRA: bf16 where supported, with fp16 fallback on hardware that does not support bf16. QLoRA remains an experiment that must demonstrate equivalent or acceptable quality.

This rule is backbone-specific and must be revalidated if tooling/model support changes.

## Decision 20 — Colab Requires Resume-First Training Design

Google Colab resources, GPU type, quotas, idle timeouts, and runtime length are dynamic. Colab documentation says free notebooks may run up to about 12 hours depending on availability/usage and does not guarantee hardware.

Sources:
- https://research.google.com/colaboratory/faq.html
- https://research.google.com/colaboratory/runtime-version-faq.html

Therefore MSTR training must record the Colab runtime and package stack, checkpoint at bounded recipe-defined boundaries, hash durable checkpoints, and verify lineage before resuming.

## Decision 21 — Training Logic Lives in Repository Code, Not Only Notebooks

Future Colab notebooks are launch/control surfaces. The canonical implementation must live in versioned repository scripts/configs so the same run can be reproduced on another GPU environment.

## Decision 22 — Export Is Part of Training Qualification

A material checkpoint is not accepted merely because training loss improved.

Future stages must preserve:
- adapter artifact;
- merged master checkpoint;
- tokenizer/processor/chat/FIM semantics;
- GGUF/reference quantization path;
- Q8/Q6/Q5/Q4 regression surfaces as appropriate;
- universal-laptop Q4-class qualification.

Unsloth's documented GGUF export is useful, but exact exported artifacts must be independently hashed and evaluated.

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
11. Colab resource variability may invalidate runs without strict environment capture.
12. Unsloth/model compatibility may change between project phases.
13. An efficient training method may produce an artifact that regresses after local quantization.
14. Notebook-only logic would make evidence difficult to reproduce outside Colab.

## Primary Research Thesis

MSTR's strongest defensible path is to maximize **verified software-engineering utility per GB, per second, and per unit of training evidence** through a compact strong base, precise repository localization, deterministic editing, executable verification, stable interaction contracts, high-quality execution-grounded post-training, accessible but reproducible training infrastructure, and local inference co-design.
