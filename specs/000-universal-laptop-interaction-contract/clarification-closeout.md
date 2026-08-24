# MSTR-000 Clarification Closeout

**Feature:** Universal Laptop Qualification + Interaction Contract  
**Status:** CLARIFIED / READY_FOR_PLAN  
**Date:** 2026-08-24

This document closes scope ambiguities before implementation planning. It records decisions already made by the founder and the MSTR-000 canonical evidence chain. It does not expand execution authority.

## Closed Decisions

### C-001 — Meaning of "everyone can use it"

The product goal is broad ordinary-laptop availability, not literal support for every historical computer.

The primary qualification tier is:

```text
U1 = 8 GB total RAM
CPU-only operation
8K reference context
no discrete GPU
OS + reference editor + medium repository + MSTR concurrently
```

Additional tiers: U0 = 4 GB / 4K characterization, non-blocking; U2 = 16 GB / 16K recommended-headroom characterization; U3 = optional acceleration, non-blocking.

The final measured support floor remains a closeout decision, not an assumption.

### C-002 — Universal release versus larger optional editions

The universal-laptop release is the primary MSTR product. Larger models may later exist as teachers, upper-bound controls, or optional editions, but they may not silently replace the universal product or raise its hardware floor.

### C-003 — Cloud/account requirements

Primary local use requires no provider account, API key, subscription, activation server, mandatory cloud inference, or remote-model fallback; offline operation is required after required artifacts are local. At least one official complete artifact-acquisition path must be accountless and not gated by separate model-access acceptance when redistribution rights permit it.

### C-004 — Privacy defaults

Telemetry and outbound network use are off by default. User code is not uploaded and is not used for training by default. Optional network features require explicit opt-in and documented data flow.

### C-005 — Basic installation experience

Basic MSTR coding assistance must not require Docker, Python, Node.js, a development toolchain, or building MSTR from source. Repository-specific verification may require the toolchain that the repository itself requires.

### C-006 — Primary model size search space

MSTR-000 begins with dense approximately 2B–4B foundation candidates plus a deliberately smaller code-specialized lower-bound control. This is a tournament boundary, not a final backbone choice. Large-total-weight MoE models are not universal-laptop candidates merely because their active parameter count is small.

### C-007 — Candidate set

Initial static-qualification candidates: `Qwen/Qwen3.5-2B-Base`, `Qwen/Qwen3.5-4B-Base`, `mistralai/Ministral-3-3B-Base-2512`, `Qwen/Qwen3-4B-Base`, `ibm-granite/granite-4.1-3b-base`, and `HuggingFaceTB/SmolLM3-3B-Base`.

Lower-bound control: `Qwen/Qwen2.5-Coder-1.5B`.

The landscape must be rescanned immediately before first weight access.

### C-008 — Qwen2.5-Coder-3B status

`Qwen/Qwen2.5-Coder-3B` is not eligible as the primary backbone under its current upstream research/non-commercial license posture. Revisit only if upstream terms materially change.

### C-009 — Rights gate

Before candidate-weight access, fail closed on intended personal/commercial use, modification/fine-tuning, quantization/conversion, derivative redistribution, end-user obligations, and account/gating requirements. Dataset, teacher/API-output, runtime, and tooling rights are separate checks.

### C-010 — Performance north star

`TTVC` is the primary task-speed metric. Required supporting metrics include TTFI, TTFA, TTFCE, verified completion rate, artifact/install footprint, memory, paging, editor responsiveness, sustained CPU behavior, and tokenizer-normalized output rate. Tokens/second alone is never sufficient.

### C-011 — Evaluation surfaces

Every material result is separated into raw model, neutral minimal harness, and full MSTR optimized system. Harness-only gains may not be reported as model gains.

### C-012 — Public benchmarks

Public benchmarks are supporting evidence, not project truth. MSTR must develop a fresh/private hidden-test Gauntlet before major training/release decisions. Training contamination and runtime answer leakage are distinct controls.

### C-013 — Interaction contract timing

Prompt/chat template, FIM semantics, tool grammar, result serialization, edit grammar, stale-write behavior, context ordering, and serving/cache assumptions must be frozen before material agent SFT/RL. A late material change requires migration evidence.

### C-014 — Edit application

MSTR v1 begins with deterministic stale-safe edit application. A learned Apply model is out of scope unless a later controlled experiment proves a meaningful advantage.

### C-015 — Repository intelligence

Default path starts with exact search, Tree-sitter symbols, and lightweight indexing if useful. Embeddings, SCIP, Graphify, Code-Graph-RAG, graph databases, or heavier systems are tournament arms and must earn their cost.

### C-016 — Multi-agent behavior

Subagent swarms are not a v1 default. Prove a strong single-agent local loop first.

### C-017 — Vision

Vision may be retained if the selected base/runtime carries it without violating laptop budgets, but a full visual-agent environment program is not required for MSTR-000.

### C-018 — Training authority

MSTR-000 does not authorize long full-parameter training, large corpus ingestion, large-scale RL, or production release. Bounded model access, paid APIs, rented compute, or micro-adaptation must be explicitly task-scoped.

### C-019 — Final selection rule

No final backbone may be selected from vendor scores or raw pre-adaptation results alone. Surviving candidates must be tested under common local Q4, interaction, repository, and bounded equivalent-adaptation protocols.

### C-020 — Later program structure

MSTR uses a sequence of Spec Kit workstreams. `docs/canonical/PROGRAM_ROADMAP.md` defines program sequence; later specs derive from predecessor evidence.

## Open Clarifications

None block MSTR-000 implementation.

Future decisions intentionally deferred to evidence: final backbone, final portable inference backend, exact Q4 profile, final support floor, final default context, final context engine, exact mid-training token budget, and exact SFT/RL framework/scale.

## Closeout

```text
SPEC_SCOPE = CLOSED
NEEDS_CLARIFICATION = 0
PLAN_AUTHORITY = READY
LONG_TRAINING_AUTHORITY = NOT_GRANTED
MODEL_WEIGHT_ACCESS = TASK_SCOPED_ONLY
```
