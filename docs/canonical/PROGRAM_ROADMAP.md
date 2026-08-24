# MSTR Program Roadmap

**Status:** Program-level roadmap — plan finalized, execution paused after T009.  
**Canonical authority:** This roadmap defines workstream sequencing and ownership. Each active Spec Kit package controls its own implementation details.  
**Primary product:** Universal-laptop local software-engineering model/system.

## Program Objective

Build the strongest practical openly downloadable local software-engineering system that ordinary laptop owners can install and use without a discrete GPU, cloud subscription, provider account, or API key.

Expensive training and release decisions occur only after cheaper qualification questions are answered with evidence.

## Non-Negotiable Product Envelope

```text
PRIMARY_RELEASE = UNIVERSAL_LAPTOP
REFERENCE_RAM = 8_GB
DISCRETE_GPU_REQUIRED = NO
CPU_ONLY_BASIC_OPERATION = REQUIRED
REFERENCE_CONTEXT = 8K
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
OFFLINE_AFTER_ACQUISITION = REQUIRED
ACCOUNT_OR_API_KEY_REQUIRED = NO
WINDOWS + LINUX + MACOS = REQUIRED_PLATFORM_FAMILIES
```

Measured evidence may refine the exact support floor, but it may not be silently raised.

## Current program state

```text
MSTR-000 = ACTIVE_SPEC_BUT_EXECUTION_PAUSED
T000-T009 = COMPLETE_CANONICAL
NEXT_TASK_ON_RESUME = T010
PAUSE_REASON = FINISH_WEPLD_FIRST
FINAL_BACKBONE = UNSELECTED
TRAINING = NONE
```

The pause requires explicit founder resume plus live GitHub reconciliation. See `docs/handoffs/MSTR-RESUME-AFTER-WEPLD.md`.

## Workstream Sequence

### MSTR-000 — Qualification Harness + Universal Laptop / Interaction / Backbone Qualification

**Purpose:** determine what can actually be built, trained, and shipped before serious training spend.

**Builds and qualifies:** reusable qualification harness; evidence/manifest engine; candidate-rights gate; local artifact/Q4 measurement path; runtime adapter boundary; deterministic edit/apply primitives; raw/neutral/full-system score surfaces; interaction-contract tournament; bounded equivalent finalist adaptation; context-engine tournament; environment/verifier MVP requirements; security/provenance/leakage contracts.

**Must close with:**
- measured hardware/OS floor and default context;
- distribution/install/privacy contract;
- portable local runtime/Q4 baseline;
- Interaction Contract v1;
- deterministic edit/apply contract;
- minimal context-engine decision;
- top backbone or top-two pilot decision;
- environment/verifier requirements;
- bounded MSTR-001 data/mid-training proposal with cost, rights, checkpoint, and regression gates.

**Current state:** T000-T009 canonical, paused before T010.

**Blocks:** all later long training.

### MSTR-001 — Data Engine + Bounded Code/FIM Mid-Training

**Purpose:** build the legally traceable, contamination-controlled data engine and determine whether code/repository mid-training materially improves the selected foundation without unacceptable forgetting or laptop regressions.

**Expected outputs:**
- source/provenance ledger;
- license/terms and benchmark-exclusion filters;
- exact/fuzzy/AST-aware dedup and lineage;
- code/doc/test/diff/repository-window mixtures;
- ordinary FIM plus structured/function/dependency-aware FIM experiments;
- general-reasoning replay;
- quality sampling/audit tooling;
- bounded pilot recipe and measured pilot before any larger token run;
- resume-safe training manifests/checkpoints and post-pilot quantized regression.

**Preferred accessible execution path:** Google Colab + Unsloth, subject to exact backbone support and task authority. The workstream must support interruption/resume, pin dependencies, and keep training logic in repository code/configs rather than notebook-only cells.

**Exit gate:** bounded pilot demonstrates a positive capability/forgetting/quantized-deployment tradeoff and the admitted data chain is auditable and legally compatible.

### MSTR-002 — Coding SFT + Repository / Tool / Planning Behavior

**Purpose:** teach the selected model the frozen MSTR Interaction Contract and strong software-engineering behavior.

**Expected outputs:**
- high-quality coding/instruction SFT;
- persistent FIM replay;
- repository inspection/localization trajectories;
- tool-use and deterministic-edit trajectories;
- build/test/recovery examples;
- planning/decomposition examples;
- failure/rollback/recovery trajectories;
- security-aware repository handling;
- regression suites for raw coding, FIM, tool reliability, Q4 behavior, and laptop deployment.

**Training policy:** Unsloth is the preferred first compact-model SFT/LoRA implementation if still supported and reproducible. The data/contract format must remain framework-neutral. For Qwen3.5, current planning starts with bf16 LoRA and treats QLoRA as an experimental arm unless newer evidence changes that decision.

**Exit gate:** post-SFT MSTR improves verified repository tasks without unacceptable regression in direct coding/FIM, quantized reliability, or universal-laptop deployment.

### MSTR-003 — Environment Factory + Agentic RL

**Purpose:** train long-horizon software-engineering behavior in executable, adversarially verified environments.

**Expected outputs:**
- scalable environment factory based on MSTR-000 contracts;
- solvability/frontier checks;
- reference/oracle-pass, no-op-fail, unsolved-state verifier validation;
- continuous reward-shortcut discovery;
- difficulty/frontier curriculum;
- long-horizon task-state/context compaction;
- deterministic terminal rewards and localized process feedback where justified;
- RL framework qualification and bounded pilot before scaling.

Unsloth may support cheap notebook RL pilots. `slime`, `verl`, and alternatives remain candidates for scaled long-horizon RL; no framework is preselected.

**Exit gate:** bounded RL produces statistically credible verified-task gains without reward hacking, evaluator leakage, or catastrophic core-capability regression.

### MSTR-004 — Local Inference Speed Co-Design

**Purpose:** minimize end-to-end TTVC once the post-training target distribution is stable.

Tournament arms may include stable prefix caching, n-gram/suffix speculation, native MTP, evidence-backed draft methods, quantization/KV profiles, context compaction, parallel tools, warm environments, affected-test selection, incremental build/test, and runtime/kernel optimization.

**Exit gate:** selected changes improve verified TTVC or whole-laptop utility while holding quality/security/regression gates.

### MSTR-005 — Packaging + Security + Privacy + Offline Release Engineering

**Purpose:** turn the qualified model/system into the ordinary-user laptop product.

**Expected outputs:** self-contained Windows/Linux/macOS packages, accountless artifact acquisition, offline basic use, no-silent-network and telemetry-off tests, malicious-repository hardening, secret/workspace/network boundaries, reproducible manifests, signed/checksummed update/rollback, uninstall/data-location behavior.

**Exit gate:** non-developer local use without cloud credentials or a development toolchain.

### MSTR-006 — MSTR Gauntlet + Release Candidate Qualification

**Purpose:** make a defensible release decision using fresh/private and public continuity evidence.

**Expected outputs:** private post-cutoff Gauntlet, public continuity suite with limitations, quantized regression, security/evaluator integrity, competitive TTVC, raw/neutral/full-system scorecards, model/data cards, contamination/leakage audit.

**Exit gate:** every release-blocking/headline claim traces to exact evidence and the universal-laptop gate passes.

### MSTR-007 — MSTR v1 Release

Publish approved model/runtime/source artifacts, hashes/manifests, model/data cards, benchmark report, install docs, opt-out/contact process, and release/update/security policy.

**Exit gate:** downloadable, usable, reproducible, independently testable, and evidence-matched.

### MSTR-008 — Post-Release Evidence and Improvement Loop

Add rolling fresh tasks, reproducible bug/eval additions, regression-driven releases, runtime/model experiments, and separately specified distilled/larger editions without weakening v1 invariants.

## Training execution policy

Canonical detail: `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

Key principles:

```text
COLAB = ACCESSIBLE COMPUTE, NOT PRODUCT DEPENDENCY
UNSLOTH = PREFERRED FIRST TRAINING FRAMEWORK, NOT DATA/ARCHITECTURE LOCK-IN
INTERRUPTION_SAFE = REQUIRED
PINNED ENVIRONMENT = REQUIRED
RUN MANIFEST + HASHES = REQUIRED
BF16_LORA_FOR_QWEN3_5 = CURRENT FIRST PILOT IF SELECTED
QWEN3_5_QLORA = EXPERIMENTAL
QUANTIZED_REGRESSION = REQUIRED AFTER MATERIAL TRAINING
GGUF_LOCAL_EXPORT = RELEASE-RELEVANT
```

## Dependency Graph

```text
MSTR-000
   |
   v
MSTR-001
   |
   v
MSTR-002
   |
   v
MSTR-003
   |
   +----------+
   |          |
   v          v
MSTR-004   MSTR-005
   |          |
   +-----+----+
         |
         v
      MSTR-006
         |
         v
      MSTR-007
         |
         v
      MSTR-008
```

MSTR-004 and MSTR-005 may overlap only after the post-training distribution is stable enough to benchmark/package without repeatedly invalidating results.

## Workstream Planning Rule

Later workstreams are program-complete but implementation-deferred. Their detailed Spec Kit packages MUST consume predecessor evidence rather than pretending the backbone, runtime, data mixture, teacher strategy, RL framework, or speculative method is already known.

Before each workstream begins:

```text
predecessor closeout canonical
-> founder/authority gate
-> create Spec Kit spec
-> clarify
-> research
-> plan + Constitution Check
-> data model/contracts/quickstart
-> tasks/analyze
-> implement
```

This roadmap prevents duplicated work while keeping later implementation evidence-driven.
