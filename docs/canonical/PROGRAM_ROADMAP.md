# MSTR Program Roadmap

**Status:** Program-level roadmap  
**Canonical authority:** This roadmap defines workstream sequencing and ownership. Each active Spec Kit package controls its own implementation details.  
**Primary product:** Universal-laptop local software-engineering model/system.

## Program Objective

Build the strongest practical openly downloadable local software-engineering system that ordinary laptop owners can install and use without a discrete GPU, cloud subscription, provider account, or API key.

The program is split into independently reviewable Spec Kit workstreams so that expensive training and release decisions are made only after cheaper qualification questions have been answered with evidence.

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

### MSTR-000 — Qualification Harness + Universal Laptop / Interaction / Backbone Qualification

**Purpose:** determine what can actually be built, trained, and shipped before serious training spend.

**Builds and qualifies:** the reusable qualification harness; evidence/manifest engine; candidate-rights gate; local artifact/Q4 measurement path; runtime adapter boundary; deterministic edit/apply primitives; raw/neutral/full-system score surfaces; interaction-contract tournament; bounded equivalent finalist adaptation; context-engine tournament; environment/verifier MVP requirements; security/provenance/leakage contracts.

**Must close with:**
- measured hardware/OS floor and default context;
- distribution/install/privacy contract;
- portable local runtime/Q4 baseline;
- Interaction Contract v1;
- deterministic edit/apply contract;
- minimal context-engine decision;
- top backbone or top-two pilot decision;
- environment/verifier requirements for later training;
- bounded MSTR-001 data/mid-training proposal with cost, rights, and regression gates.

**Current state:** active. T000–T002 are canonical complete; the complete Spec Kit implementation package defines the remaining executable graph.

**Blocks:** all later long training.

### MSTR-001 — Data Engine + Bounded Code/FIM Mid-Training

**Purpose:** build the legally traceable, contamination-controlled data engine and determine whether code/repository mid-training materially improves the MSTR-000-selected foundation without unacceptable forgetting or laptop regressions.

**Expected build outputs:**
- source/provenance ledger;
- license/terms and benchmark-exclusion filters;
- exact/fuzzy/AST-aware dedup and lineage;
- code/doc/test/diff/repository-window mixtures;
- ordinary FIM plus structured/function/dependency-aware FIM experiments;
- general-reasoning replay;
- quality sampling/audit tooling;
- bounded pilot recipe and measured pilot before any larger token run.

**Exit gate:** a reproducible bounded pilot demonstrates a positive capability/forgetting/quantized-deployment tradeoff and the admitted data chain is auditable and legally compatible with the intended release.

### MSTR-002 — Coding SFT + Repository / Tool / Planning Behavior

**Purpose:** teach the selected model the frozen MSTR Interaction Contract and strong software-engineering behavior.

**Expected build outputs:**
- high-quality coding/instruction SFT;
- persistent FIM replay;
- repository inspection/localization trajectories;
- tool-use and deterministic-edit trajectories;
- build/test/recovery examples;
- planning/decomposition examples;
- failure/rollback/recovery trajectories;
- security-aware repository handling;
- regression suites for raw coding, FIM, schema/tool reliability, Q4 behavior, and laptop deployment.

**Exit gate:** post-SFT MSTR improves verified repository tasks without unacceptable regression in direct coding/FIM, quantized reliability, or universal-laptop deployment.

### MSTR-003 — Environment Factory + Agentic RL

**Purpose:** train long-horizon software-engineering behavior in executable, adversarially verified environments.

**Expected build outputs:**
- scalable environment factory based on the MSTR-000 contracts;
- solvability/frontier checks;
- reference/oracle-pass, no-op-fail, and unsolved-state verifier validation;
- continuous reward-shortcut discovery;
- difficulty/frontier curriculum;
- long-horizon task-state/context compaction;
- deterministic terminal rewards and localized process feedback where justified;
- RL framework qualification and bounded pilot before scaling.

`slime`, `verl`, and other frameworks remain candidates until this workstream qualifies the best fit for MSTR's environments and compute topology.

**Exit gate:** bounded RL produces statistically credible verified-task gains without reward hacking, evaluator leakage, or catastrophic core-capability regression.

### MSTR-004 — Local Inference Speed Co-Design

**Purpose:** minimize end-to-end TTVC once the post-training target distribution is stable enough for fair optimization.

**Tournament arms may include:**
- stable prompt/prefix caching;
- n-gram/suffix speculation;
- native MTP where supported;
- EAGLE/DFlash-class drafting where evidence warrants;
- quantization and KV/cache profiles;
- context compaction;
- tool parallelism/asynchrony;
- warm environment snapshots;
- affected-test selection;
- incremental build/test;
- serving/kernel/runtime optimization.

**Exit gate:** selected changes improve verified TTVC or whole-laptop utility while holding quality/security/regression gates, not merely tokens/sec.

### MSTR-005 — Packaging + Security + Privacy + Offline Release Engineering

**Purpose:** turn the qualified model/system into the ordinary-user laptop product.

**Expected build outputs:**
- self-contained Windows/Linux/macOS packages;
- accountless official artifact acquisition;
- offline first-run/basic-use qualification;
- no-silent-network and telemetry-default-off tests;
- prompt-injection and malicious-repository hardening;
- secret/workspace/network boundaries;
- reproducible model/runtime manifests;
- signed/checksummed update and rollback flows;
- uninstall/data-location behavior.

**Exit gate:** a non-developer can obtain, install, and use MSTR locally without cloud credentials or a development toolchain, while the security/privacy contract passes.

### MSTR-006 — MSTR Gauntlet + Release Candidate Qualification

**Purpose:** make a defensible release decision using fresh/private and public continuity evidence.

**Expected build outputs:**
- fresh/private post-cutoff MSTR Gauntlet;
- public benchmark continuity suite with limitations documented;
- quantized regression suite;
- security/evaluator-integrity suite;
- competitive TTVC protocol;
- raw vs neutral-harness vs full-system scorecards;
- candidate release model/data cards;
- reproducibility and contamination/leakage audit package.

**Exit gate:** every release-blocking and headline claim is traceable to exact evidence and the universal-laptop gate passes on required platform families.

### MSTR-007 — MSTR v1 Release

**Purpose:** publish the first stable MSTR model/runtime/source release.

**Expected build outputs:**
- approved model and runtime artifacts;
- source release;
- hashes/manifests;
- model card and data card;
- benchmark/qualification report;
- installation/package documentation;
- opt-out/contact process;
- release/update/security policy.

**Exit gate:** MSTR v1 is downloadable, usable, reproducible, independently testable, and its claims match the evidence package.

### MSTR-008 — Post-Release Evidence and Improvement Loop

**Purpose:** improve MSTR without destroying the evidence, compatibility, or universal-laptop properties that justified v1.

**Expected build outputs:**
- issue/telemetry-free opt-in feedback and reproducible bug/eval additions;
- rolling fresh benchmark/task additions;
- regression-driven point releases;
- model/runtime optimization experiments;
- optional distilled/larger editions only under separately specified gates;
- next-version Spec Kit workstreams based on observed failure modes.

**Exit gate:** each material change is backed by a new or amended specification and reproduces the relevant v1 product/security/evaluation invariants.

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

MSTR-004 and MSTR-005 may overlap only after the post-training distribution is stable enough to benchmark and package without repeatedly invalidating results.

## Workstream Planning Rule

Later workstreams are intentionally **program-complete but implementation-deferred**. Their detailed Spec Kit packages MUST consume predecessor evidence rather than pretending that the backbone, runtime, data mixture, teacher strategy, RL framework, speculative method, or release format is already known.

Before each workstream begins:

```text
predecessor closeout is canonical
-> founder/authority gate satisfied where required
-> create new Spec Kit spec
-> clarify
-> research
-> plan + Constitution Check
-> data model/contracts/quickstart
-> tasks/analyze
-> implement
```

This roadmap therefore prevents duplicated work while keeping later implementation evidence-driven.