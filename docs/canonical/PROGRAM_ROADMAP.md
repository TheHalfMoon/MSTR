# MSTR Program Roadmap

**Status:** Program-level roadmap — active  
**Canonical authority:** This roadmap defines workstream sequencing and ownership. Each active Spec Kit package controls its own implementation details.  
**Primary product:** Universal-laptop local code-specialized software-engineering model/system.  
**Live state:** `docs/canonical/CURRENT_STATE.md`.

## Program Objective

Build the smallest practical openly downloadable code model/system that can reliably turn software direction into verified working software on ordinary laptops without a discrete GPU, cloud subscription, provider account, or API key.

MSTR is not primarily optimized for general assistant breadth.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DVCR
DVCR = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC
TTVC = TIME_TO_VERIFIED_COMPLETION
```

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
TELEMETRY_DEFAULT = OFF
```

Measured evidence may refine the exact support floor, but it may not be silently raised.

## Program Sequence

```text
MSTR-000
Qualification / Q4 / runtime / interaction / candidate evidence
        |
        | after T034
        v
MSTR-000A
Verified Agent Harness + Direction-to-Done Foundation
        |
        v
MSTR-000 remainder reconciliation / candidate tournament / bounded recipe preflight
        |
        | separate exact training authority
        v
MSTR-001
Data Engine + Bounded Code/FIM Mid-Training
        |
        v
MSTR-002
Execution-Grounded Coding SFT + Tool/Edit/Planning/Recovery
        |
        v
MSTR-003
Environment Factory Expansion + Agentic RL
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

## MSTR-000 — Qualification Harness + Universal Laptop / Interaction / Backbone Qualification

**Purpose:** determine what can actually be built, trained, and shipped before serious training spend.

**Builds and qualifies:** evidence/manifest engine; candidate-rights gate; local artifact/Q4 measurement path; runtime adapter boundary; deterministic edit/apply primitives; raw/neutral/full-system score surfaces; interaction candidates; candidate tournament inputs; context experiments; security/provenance/leakage contracts.

**Mandatory sequence amendment:** T029–T034 continue under MSTR-000. After T034 becomes canonical, MSTR-000A MUST close before any weight-changing agent adaptation/training gate is executed.

**Must close with:**
- measured hardware/OS floor and default context;
- distribution/install/privacy contract;
- portable local runtime/Q4 baseline;
- final interaction contract consuming MSTR-000A loop/state/verifier semantics;
- deterministic edit/apply contract;
- minimal context-engine decision;
- top backbone or controlled finalist decision according to the final task graph;
- bounded next-stage data/training proposal with cost, rights, checkpoint, and regression gates.

**Blocks:** all long training and release work.

## MSTR-000A — Verified Agent Harness + Direction-to-Done Foundation

**Purpose:** ensure future MSTR training optimizes the exact behavior the product needs rather than teaching agent behavior under an unrelated scaffold.

**Entry gate:** T034 `COMPLETE_CANONICAL`.

**Canonical package:** `specs/001-agent-harness-verified-loop-foundation/`.

**Builds and qualifies:**
- `MSTR-BUILD-LOOP-v0`;
- bounded loop contract and stop/recovery semantics;
- append-oriented typed event log and deterministic replay;
- compact `AgentState` projection for an 8K model;
- neutral-minimal harness;
- MSTR-native typed harness;
- WePLD-native adapter and evidence-derived capability profile;
- environment bootstrap/admission MVP;
- independent verifier/finalizer MVP and reward-shortcut battery;
- private/fresh Direction-to-Done v0 task surface;
- DVCR/TTVC plus first-pass/edit-survival/repair/tool-error metrics;
- failure taxonomy and training trajectory contract;
- bounded `MSTR-RESEARCH-LOOP-v0` inspired by keep/discard autonomous research loops;
- reconciliation of existing interaction/environment/training tasks.

**Default topology:**

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

Multi-agent/planner/checker designs are optional measured arms, not default complexity.

**Required score surfaces:**

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Harness-only gains MUST NOT be attributed to model weights.

**Event integrity:** every run event carries a non-null SHA-256 with optional predecessor binding; replay MUST reject missing hashes, duplicates, gaps, reordered/substituted events, and broken chains.

**Raw-model evidence:** closeout requires a pinned RAW_MODEL scorecard for every eligible tournament cell (or a recorded `N/A` reason) to distinguish model improvement from harness-only gains.

**Exit gate:** Build Loop, event/replay (with mandatory hash integrity), harness arms, environment/verifier MVP, Direction-to-Done v0, trajectory contract, research loop, and downstream sequence reconciliation are canonical and training-ready.

MSTR-000A grants NO weight-changing training authority.

## MSTR-001 — Data Engine + Bounded Code/FIM Mid-Training

**Purpose:** build the legally traceable, contamination-controlled data engine and determine whether code/repository mid-training materially improves the selected foundation without unacceptable forgetting or laptop regressions.

**Required inherited contracts:** MSTR-000A loop/event/trajectory/environment/verifier identities and MSTR-000 interaction contract.

**Expected outputs:**
- source/provenance ledger;
- license/terms and benchmark-exclusion filters;
- exact/fuzzy/AST-aware dedup and lineage;
- code/doc/test/diff/repository-window mixtures;
- ordinary FIM;
- instruction-aware FIM experiments;
- function/dependency-aware FIM experiments;
- cross-file/repository FIM experiments;
- experimental action/observation continuation only as a measured arm;
- general/software-reasoning replay sufficient to prevent damaging forgetting;
- quality sampling/audit tooling;
- bounded pilot recipe and measured pilot before any larger token run;
- resume-safe training manifests/checkpoints and post-pilot Q4 regression.

**Preferred accessible execution path:** Google Colab + Unsloth, subject to exact backbone support and task authority. Training logic remains repository code/config driven, not notebook-only.

**Exit gate:** bounded pilot demonstrates a positive code/agent/forgetting/quantized-deployment tradeoff and the admitted data chain is auditable and legally compatible.

## MSTR-002 — Execution-Grounded Coding SFT + Repository / Tool / Planning / Recovery

**Purpose:** teach the selected model the frozen MSTR interaction/build-loop contract and strong software-engineering behavior.

**Expected outputs:**
- high-quality coding/instruction SFT;
- persistent FIM replay;
- repository inspection/localization trajectories;
- tool-use and deterministic-edit trajectories;
- build/test/verifier trajectories;
- planning/decomposition examples;
- failure/rollback/recovery trajectories;
- simplicity-first and surgical-change preference data;
- invalid-tool/bad-edit/fake-completion negative examples;
- security-aware repository handling;
- regression suites for raw coding, FIM, tools, recovery, Direction-to-Done, Q4, and laptop deployment.

**Training policy:** use the same model-visible tool/edit/result/state semantics used for serving/evaluation, or require explicit migration evidence. Unsloth is a preferred compact-model implementation candidate, not a data/contract lock-in.

**Exit gate:** post-SFT MSTR improves DVCR and verified repository work without unacceptable regression in direct coding/FIM, quantized reliability, or universal-laptop deployment.

## MSTR-003 — Environment Factory Expansion + Agentic RL

**Purpose:** scale long-horizon software-engineering behavior in executable, adversarially verified environments after the MSTR-000A MVP proves the contracts.

**Expected outputs:**
- scalable environment factory based on MSTR-000A environment contracts;
- previous-MSTR-assisted environment bootstrap where it proves useful;
- solvability/frontier checks;
- reference/oracle-pass, no-op-fail, unsolved-state verifier validation;
- continuous reward-shortcut discovery;
- difficulty/frontier curriculum;
- long-horizon task-state/context compaction;
- deterministic terminal rewards and bounded process feedback where justified;
- RL framework qualification and bounded pilot before scaling.

Unsloth may support cheap notebook RL pilots. `slime`, `verl`, and alternatives remain candidates for scaled long-horizon RL; no framework is preselected.

**Exit gate:** bounded RL produces statistically credible DVCR/verified-task gains without reward hacking, evaluator leakage, or catastrophic core-capability/Q4 regression.

## MSTR-004 — Local Inference Speed Co-Design

**Purpose:** minimize end-to-end TTVC once the post-training target distribution is stable.

Tournament arms may include stable-prefix caching, speculation, quantization/KV profiles, context compaction, parallel tools where justified, warm environments, affected-test selection, incremental build/test, and runtime/kernel optimization.

**Exit gate:** selected changes improve DVCR/TTVC or whole-laptop utility while holding quality/security/regression gates.

## MSTR-005 — Packaging + Security + Privacy + Offline Release Engineering

**Purpose:** turn the qualified model/system into the ordinary-user laptop product.

**Expected outputs:** self-contained Windows/Linux/macOS packages, accountless artifact acquisition, offline basic use, no-silent-network and telemetry-off tests, malicious-repository hardening, secret/workspace/network boundaries, reproducible manifests, signed/checksummed update/rollback, uninstall/data-location behavior.

**Exit gate:** non-developer local use without cloud credentials or a development toolchain.

## MSTR-006 — MSTR Gauntlet + Release Candidate Qualification

**Purpose:** make a defensible release decision using fresh/private and public continuity evidence.

**Expected outputs:**
- private/fresh Direction-to-Done Gauntlet;
- whole-program/multi-file construction tasks;
- public continuity suite with limitations;
- quantized regression;
- security/evaluator integrity;
- competitive TTVC;
- raw/neutral/MSTR-native/WePLD scorecards;
- model/data cards;
- contamination/leakage audit.

**Exit gate:** every release-blocking/headline claim traces to exact evidence and the universal-laptop gate passes.

## MSTR-007 — MSTR v1 Release

Publish approved model/runtime/source artifacts, hashes/manifests, model/data cards, benchmark report, install docs, opt-out/contact process, and release/update/security policy.

**Exit gate:** downloadable, usable, reproducible, independently testable, and evidence-matched.

## MSTR-008 — Post-Release Evidence and Improvement Loop

Add rolling fresh tasks, reproducible bug/eval additions, regression-driven releases, runtime/model experiments, explicit opt-in evidence pathways, and separately specified editions without weakening v1 invariants.

Prior MSTR releases MAY help bootstrap future environments, task generation, run management, data preprocessing, or bounded research campaigns, but no self-improvement path may edit its own hidden evaluator or bypass governance.

## Training Execution Policy

Canonical detail: `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

Harness/loop detail: `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`.

Key principles:

```text
COLAB = ACCESSIBLE COMPUTE, NOT PRODUCT DEPENDENCY
UNSLOTH = PREFERRED FIRST TRAINING FRAMEWORK, NOT DATA/ARCHITECTURE LOCK-IN
TRAIN_AND_SERVE_LOOP_SEMANTICS = COMPATIBLE_OR_MIGRATION_PROVEN
EXECUTABLE_ENVIRONMENT_ADMISSION = REQUIRED_BEFORE_AGENT_RL
INDEPENDENT_VERIFIER = REQUIRED_FOR_SUCCESS_LABEL
INTERRUPTION_SAFE = REQUIRED
PINNED_ENVIRONMENT = REQUIRED
RUN MANIFEST + HASHES = REQUIRED
QUANTIZED_REGRESSION = REQUIRED_AFTER_MATERIAL_TRAINING
GGUF_Q4 = RELEASE_RELEVANT
PRODUCTION_TRACE_TRAINING_DEFAULT = OFF
```

## Workstream Planning Rule

Later workstreams are implementation-deferred until predecessor evidence is canonical. Their detailed Spec Kit packages MUST consume predecessor evidence rather than redefining incompatible model, loop, environment, verifier, data, or serving contracts.

Before each workstream begins:

```text
predecessor closeout canonical
-> exact founder/authority gate where required
-> create Spec Kit spec
-> clarify
-> research
-> plan + Constitution Check
-> data model/contracts/quickstart
-> tasks/analyze
-> implement
```

This roadmap prevents duplicated work while making MSTR's model, harness, verifier, training distribution, and WePLD integration one coherent evidence-driven system.
