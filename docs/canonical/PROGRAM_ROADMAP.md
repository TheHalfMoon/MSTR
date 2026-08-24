# MSTR Program Roadmap

**Status:** Program-level roadmap  
**Canonical authority:** This roadmap describes sequencing and workstream boundaries. The active Spec Kit package controls implementation details.  
**Primary product:** Universal-laptop local software-engineering model/system.

## Program Objective

Build the strongest practical openly downloadable local software-engineering system that ordinary laptop owners can install and use without a discrete GPU, cloud subscription, provider account, or API key.

The program is deliberately split into independently reviewable Spec Kit workstreams so that expensive training decisions are made only after cheaper questions have been answered.

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

## Workstream Sequence

### MSTR-000 — Universal Laptop Qualification + Interaction Contract

**Purpose:** determine what can actually be built and shipped before serious training spend.

**Must close with:** measured hardware/OS floor; distribution/install/privacy contract; admissible backbone shortlist; selected portable inference/Q4 baseline; Interaction Contract v1; deterministic edit/apply contract; minimal context-engine decision; evaluation/measurement harness; executable environment-factory MVP requirements; top backbone or top-two pilot set; bounded MSTR-001 compute/data proposal.

**Current state:** active. T000–T002 are canonical complete.

**Blocks:** all later long training.

### MSTR-001 — Qualification Harness + Runtime Skeleton + Backbone Pilot

**Purpose:** turn the MSTR-000 contracts into the first reusable executable system and run the bounded top-one/top-two backbone pilot.

**Expected build outputs:** portable MSTR CLI/runtime skeleton; runtime adapter abstraction; evidence/manifest engine; deterministic apply engine; baseline exact search + symbol map; task/verifier runner; local Q4 candidate integration; reproducible raw/neutral/full-system scoring; top-one backbone decision if evidence is decisive.

**Exit gate:** a single reproducible codebase can run the canonical local qualification suite end-to-end on required hardware lanes.

### MSTR-002 — Data Engine + Code/FIM Mid-Training

**Purpose:** construct a legally traceable, decontaminated data engine and determine whether bounded code/repository mid-training materially improves the selected base.

**Expected outputs:** source/provenance ledger; license and benchmark-exclusion filters; exact/fuzzy/AST dedup; code/doc/test/diff/repository-window mixtures; ordinary + structured/function-aware FIM generation; general-reasoning replay; data-quality sampling and audit tooling; small pilot before any large token run.

**Exit gate:** measured pilot proves a positive capability/forgetting tradeoff and the corpus chain is distributable/auditable.

### MSTR-003 — Coding SFT + Repository/Tool Behavior

**Purpose:** teach the model the frozen MSTR Interaction Contract and strong software-engineering behavior.

**Expected outputs:** instruction SFT; FIM replay; repository inspection/localization; tool-use trajectories; deterministic edit protocol; build/test/recovery examples; planning/decomposition examples; security-aware repository handling; negative/failure trajectories.

**Exit gate:** post-SFT model improves verified repository tasks without unacceptable FIM, raw coding, local memory, or tool-schema regressions.

### MSTR-004 — Environment Factory + Agentic RL

**Purpose:** train long-horizon software-engineering behavior in executable, adversarially verified environments.

**Expected outputs:** environment factory; solvability checks; reference/no-op/unsolved verifier validation; reward-shortcut battery; frontier/difficulty curriculum; long-horizon context compaction; deterministic terminal rewards plus localized process feedback where useful; RL framework qualification; bounded pilot before scaling.

**Exit gate:** RL produces statistically credible verified-task gains without reward hacking or catastrophic regression.

### MSTR-005 — Local Inference Speed Co-Design

**Purpose:** reduce end-to-end TTVC after the target distribution is stable.

**Tournament arms may include:** prefix/prompt caching; n-gram/suffix speculation; native MTP; EAGLE/DFlash-class drafting where supported; quantization profiles; KV/cache policies; context compaction; tool parallelism; warm environment snapshots; affected-test selection; incremental build/test; serving/kernel optimizations.

**Exit gate:** improvements are measured on TTVC/quality/laptop responsiveness, not tokens/sec alone.

### MSTR-006 — Packaging, Security, Privacy, and Offline Release Engineering

**Purpose:** produce the actual ordinary-user laptop product.

**Expected outputs:** signed/self-contained platform packages; accountless artifact acquisition; offline smoke tests; no-silent-network tests; prompt-injection and malicious-repository tests; secret/network boundaries; reproducible model/runtime manifests; update/rollback; uninstall/data-location behavior; Windows/Linux/macOS release paths.

**Exit gate:** a non-developer can install and use MSTR locally without cloud credentials or a development toolchain.

### MSTR-007 — MSTR Gauntlet + Release Candidate Qualification

**Purpose:** make a defensible release decision.

**Expected outputs:** private/fresh post-cutoff Gauntlet; public benchmark continuity suite; quantized regression suite; security/evaluator-integrity suite; competitive TTVC protocol; raw vs neutral-harness vs full-system scorecards; release model/data cards; reproducibility package.

**Exit gate:** all headline claims are traceable to exact evidence and the universal-laptop product gate passes.

### MSTR-008 — v1 Release + Post-Release Evidence Loop

**Purpose:** publish the first stable MSTR release and establish a clean improvement loop.

**Expected outputs:** model/runtime artifacts; source release; checksums/manifests; model card/data card; benchmark reports; opt-out process; issue-driven evaluation additions; release/update policy.

**Exit gate:** MSTR v1 is downloadable, usable, reproducible, and independently testable.

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
   v
MSTR-004
   |
   +----------+
   |          |
   v          v
MSTR-005   MSTR-006
   |          |
   +-----+----+
         |
         v
      MSTR-007
         |
         v
      MSTR-008
```

MSTR-005 and MSTR-006 may overlap after the post-training model distribution is stable enough to benchmark.

## Planning Rule

Later workstreams are intentionally not fully implementation-specified yet. Their detailed Spec Kit packages MUST use the evidence and frozen decisions produced by their predecessors rather than pretending the backbone, runtime, data mix, or RL recipe is already known.

This roadmap is therefore complete in sequencing and ownership while remaining evidence-driven in implementation detail.
