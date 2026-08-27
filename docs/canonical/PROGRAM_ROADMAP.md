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
PRIMARY_EFFICIENCY_TARGET = VERIFIED_SOFTWARE_CAPABILITY_PER_GB
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

MSTR-000A and MSTR-000B contain early-safe, model-independent work that may proceed before candidate convergence when exact dependencies allow. Candidate-dependent convergence remains gated.

```text
                    MSTR-000
       Q4 / runtime / candidate qualification
                     |
                     | parallel where independent
        +------------+-------------+
        |                          |
        v                          v
MSTR-000A EARLY FOUNDATION   MSTR-000B EARLY FOUNDATION
loop/event/state/env/        task gates + mission-aligned
verifier/trajectory          rescan + data/curriculum/verifier-health
        |                          |
        +------------+-------------+
                     |
                     v
       STABLE PRODUCT-ALIGNED CANDIDATE POOL
       + QUALIFIED LOOP/VERIFIER/DATA CONTRACTS
                     |
                     v
        MSTR-000A / MSTR-000B CONVERGENCE
        cross-harness + Direction-to-Done
        + multi-fidelity research + recipe preflight
                     |
                     | separate exact training authority
                     v
MSTR-001  Data Engine + Code/FIM Continued/Mid-Training
                     |
                     v
MSTR-002  Execution-Grounded Coding SFT + Recovery
                     |
                     v
MSTR-003  Environment Factory Expansion + Agentic RL
                     |
              +------+------+
              |             |
              v             v
           MSTR-004      MSTR-005
              |             |
              +------+------+ 
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

No old task number may bypass MSTR-000A/MSTR-000B convergence into weight-changing training.

## MSTR-000 — Qualification Harness + Universal Laptop / Interaction / Backbone Qualification

**Purpose:** determine what can actually be built, trained, and shipped before serious training spend.

**Builds and qualifies:** evidence/manifest engine; candidate-rights gate; local artifact/Q4 measurement path; runtime adapter boundary; deterministic edit/apply primitives; raw/neutral/full-system score surfaces; interaction candidates; context experiments; security/provenance/leakage contracts.

T030-T034 continue for the existing candidate pool according to their exact canonical state. MSTR-000B may add newly relevant code-specialized candidates, but they must receive equivalent qualification before joining headline comparison.

**Must close with:**
- measured hardware/OS floor and default context;
- distribution/install/privacy contract;
- portable local runtime/Q4 baseline;
- final interaction contract consuming MSTR-000A/MSTR-000B semantics;
- deterministic edit/apply contract;
- minimal context-engine decision;
- top backbone or controlled finalist decision from the stable product-aligned pool;
- bounded next-stage data/training proposal with cost, rights, checkpoint, curriculum, verifier-health, and regression gates.

**Blocks:** all long training and release work.

## MSTR-000A — Verified Agent Harness + Direction-to-Done Foundation

**Purpose:** ensure future MSTR training optimizes the exact behavior the product needs rather than teaching agent behavior under an unrelated scaffold.

**Canonical package:** `specs/001-agent-harness-verified-loop-foundation/`.

### Entry semantics

The old blanket `T034_COMPLETE_CANONICAL` entry gate is superseded by exact dependencies:

```text
A001-A018 = EARLY_SAFE where model-independent and exact prerequisites are satisfied
A019-A024 = CONVERGENCE_GATED
```

Convergence requires equivalent candidate qualification and the MSTR-000B stable candidate/verifier/research prerequisites.

**Builds and qualifies:**
- `MSTR-BUILD-LOOP-v0` as a bounded state graph;
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
- bounded `MSTR-RESEARCH-LOOP-v0`.

**Default topology:**

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

**Required score surfaces:**

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

Harness-only gains MUST NOT be attributed to model weights.

**Exit gate:** A024 can close only after MSTR-000B convergence dependencies are consumed or explicitly reconciled. MSTR-000A grants no weight-changing training authority.

## MSTR-000B — Code Model Supremacy Pre-Training Foundation

**Purpose:** maximize verified software-building capability per parameter/GB by correcting foundation search, data distribution, training-signal quality, difficulty, verifier health, research efficiency and Q4 promotion before training begins.

**Canonical package:** `specs/002-code-model-supremacy-foundation/`.

**Canonical strategy:** `docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md`.

### Major responsibilities

1. **Machine task/dependency enforcement** so autonomous agents cannot bypass canonical sequencing or external-effect gates.
2. **Mission-aligned compact backbone rescan** that includes code-specialized bases rather than excluding them by specialization. `JetBrains/Mellum-4b-base` is a mandatory review candidate, not a preselected winner.
3. **Tokenizer economics** because 8K effective code density is product capability.
4. **Data Constitution** governing source classes, provenance, contamination, dedup, benchmark exclusion, language mix, synthetic/student/teacher data and stage admission.
5. **Software-evolution corpus contract** for issue/feature -> changes -> CI/tests -> review -> repair -> verified final state.
6. **Execution-filtered student self-alignment** with independent verifier admission.
7. **Bounded teacher rescue** only when rights and verification permit.
8. **Checkpoint-relative frontier curriculum** so scarce training compute targets learnable hard tasks.
9. **Verifier Health Contract** so weak/broken/leaked tests cannot create clean rewards.
10. **Test-generation curriculum** including reproduce-before-fix and pre-fix-fail/post-fix-pass evidence.
11. **Feature/greenfield curriculum** spanning function -> module -> multi-file feature -> bounded program -> repeated evolution.
12. **Multi-fidelity research ladder** from cheap proxies to Q4 universal-laptop tests.
13. **Adaptive test-time compute/selective context** measured for marginal DVCR/TTVC value.
14. **Q4-in-the-loop promotion** after every material weight-changing stage.
15. **Equivalent training-method tournament preflight** for LoRA/rsLoRA/QLoRA arms where current backbone support permits.
16. **Repository Health Delta** so repeated task success cannot hide accumulating technical debt.
17. **Cross-harness robustness** to detect scaffold overfitting.

### New candidate authority

Metadata/static review may proceed normally. Any model weight access outside the existing T027/T028 envelope requires a new exact manifest and separate founder authorization. MSTR-000B itself authorizes no new weight access.

### Exit gate

MSTR-000B closes only after B034 proves that task-gate enforcement, stable candidate pool, Data Constitution, software-evolution/self-alignment/difficulty/verifier-health/test-generation/feature curricula, research ladder, Q4 promotion, method preflight, repository-health and downstream reconciliation are canonical.

B034 does NOT authorize training.

## MSTR-001 — Data Engine + Bounded Code/FIM Continued/Mid-Training

**Purpose:** build the legally traceable, contamination-controlled data engine and determine whether code/repository continued training materially improves the selected foundation without unacceptable forgetting or laptop regressions.

**Required inherited contracts:** MSTR-000A loop/event/trajectory/environment identities; MSTR-000B Data Constitution/software-evolution/frontier/verifier-health/Q4 contracts; final interaction contract.

**Expected outputs:**
- source/provenance ledger;
- license/terms and benchmark-exclusion filters;
- exact/fuzzy/AST-aware dedup and lineage;
- product-aligned programming-language/tooling mix;
- code/doc/test/diff/build/CI/repository/software-evolution mixtures;
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- test-aware/diff-aware FIM experiments where specified;
- experimental action/observation continuation only as a measured arm;
- general/software-reasoning replay sufficient to prevent damaging forgetting;
- dynamic student-frontier sampling;
- bounded pilot recipe and measured pilot before any larger token run;
- resume-safe training manifests/checkpoints and Q4 regression after each material stage.

**Preferred accessible execution path:** Google Colab + Unsloth subject to exact support/authority. Training logic remains repository code/config driven.

**Exit gate:** bounded pilot demonstrates positive direct-code/FIM/DVCR/forgetting/Q4 tradeoff and the admitted data chain is auditable and legally compatible.

## MSTR-002 — Execution-Grounded Coding SFT + Repository / Tool / Planning / Recovery

**Purpose:** teach the selected model the frozen MSTR interaction/build-loop contract and strong software-engineering behavior.

**Expected outputs:**
- high-quality coding/instruction SFT;
- persistent FIM replay;
- software-evolution trajectories;
- repository inspection/localization;
- tool-use and deterministic-edit trajectories;
- tester/reviewer mode examples;
- build/test/verifier trajectories;
- planning/decomposition examples;
- failure/rollback/recovery trajectories;
- simplicity/surgical-change preference data;
- student self-alignment and permitted teacher-rescue data;
- invalid-tool/bad-edit/fake-completion negative examples;
- feature/greenfield tasks;
- security-aware repository handling;
- Q4 and universal-laptop regression.

**Exit gate:** post-SFT MSTR improves DVCR and verified repository work without unacceptable regression in direct coding/FIM, quantized reliability, repository health, or universal-laptop deployment.

## MSTR-003 — Environment Factory Expansion + Agentic RL

**Purpose:** scale long-horizon software-engineering behavior in executable, adversarially verified environments after the pre-training foundations prove contracts.

**Expected outputs:**
- scalable environment factory;
- previous-MSTR-assisted environment bootstrap where useful;
- dynamic frontier/difficulty calibration;
- verifier-health checks and continuous reward-shortcut discovery;
- long-horizon task-state/context compaction;
- deterministic terminal rewards and bounded process feedback where justified;
- multi-fidelity promotion before expensive RL;
- RL framework qualification and bounded pilot before scaling.

Unsloth may support cheap notebook RL pilots. `slime`, `verl`, and alternatives remain candidates for scaled long-horizon RL; no framework is preselected.

**Exit gate:** bounded RL produces statistically credible DVCR/verified-task gains without reward hacking, evaluator leakage, catastrophic coding/FIM loss, repository-health collapse, or Q4 regression.

## MSTR-004 — Local Inference Speed Co-Design

**Purpose:** minimize end-to-end TTVC once the post-training target distribution is stable.

Tournament arms may include stable-prefix caching, speculation, quantization/KV profiles, context compaction, selective retrieval, adaptive test-time compute, parallel tools where justified, warm environments, affected-test selection, incremental build/test, and runtime/kernel optimization.

**Exit gate:** selected changes improve DVCR/TTVC or whole-laptop utility while holding quality/security/regression gates.

## MSTR-005 — Packaging + Security + Privacy + Offline Release Engineering

**Purpose:** turn the qualified model/system into the ordinary-user laptop product.

**Expected outputs:** self-contained Windows/Linux/macOS packages, accountless artifact acquisition, offline basic use, no-silent-network and telemetry-off tests, malicious-repository hardening, secret/workspace/network boundaries, reproducible manifests, signed/checksummed update/rollback, uninstall/data-location behavior.

## MSTR-006 — MSTR Gauntlet + Release Candidate Qualification

**Purpose:** make a defensible release decision using fresh/private and public continuity evidence.

**Expected outputs:**
- private/fresh Direction-to-Done Gauntlet;
- feature implementation and bounded greenfield/whole-program tasks;
- repeated repository-evolution/health tasks;
- public continuity suite with limitations;
- quantized regression;
- security/evaluator integrity;
- competitive TTVC;
- raw/neutral/MSTR-native/WePLD scorecards;
- model/data cards;
- contamination/leakage audit.

## MSTR-007 — MSTR v1 Release

Publish approved model/runtime/source artifacts, hashes/manifests, model/data cards, benchmark report, install docs, opt-out/contact process, and release/update/security policy.

## MSTR-008 — Post-Release Evidence and Improvement Loop

Add rolling fresh tasks, reproducible bug/eval additions, regression-driven releases, runtime/model experiments, explicit opt-in evidence pathways, and separately specified editions without weakening v1 invariants.

Prior MSTR releases MAY help bootstrap future environments, task generation, run management, data preprocessing, difficulty calibration or bounded research campaigns, but no self-improvement path may edit its own hidden evaluator or bypass governance.

## Training Execution Policy

Canonical detail: `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

Harness/loop detail: `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`.

Code-model optimization detail: `docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md`.

Key principles:

```text
COLAB = ACCESSIBLE COMPUTE, NOT PRODUCT DEPENDENCY
UNSLOTH = PREFERRED FIRST TRAINING FRAMEWORK, NOT DATA/ARCHITECTURE LOCK-IN
TRAIN_AND_SERVE_LOOP_SEMANTICS = COMPATIBLE_OR_MIGRATION_PROVEN
CODE_PRIOR = FIRST_CLASS
SOFTWARE_EVOLUTION_DATA = FIRST_CLASS
STUDENT_SELF_ALIGNMENT = FIRST_CLASS
DIFFICULTY_FRONTIER = CHECKPOINT_RELATIVE
VERIFIER_HEALTH = REQUIRED_FOR_TRAINING_ADMISSION
Q4_PROMOTION = REQUIRED_AFTER_MATERIAL_WEIGHT_CHANGE
EXECUTABLE_ENVIRONMENT_ADMISSION = REQUIRED_BEFORE_AGENT_RL
INDEPENDENT_VERIFIER = REQUIRED_FOR_SUCCESS_LABEL
INTERRUPTION_SAFE = REQUIRED
PINNED_ENVIRONMENT = REQUIRED
RUN MANIFEST + HASHES = REQUIRED
PRODUCTION_TRACE_TRAINING_DEFAULT = OFF
```

## Workstream Planning Rule

Later workstreams are implementation-deferred until predecessor evidence is canonical. Their detailed Spec Kit packages MUST consume predecessor evidence rather than redefine incompatible model, loop, environment, verifier, data, curriculum, or serving contracts.

Before each material workstream begins:

```text
predecessor/required convergence outputs canonical
-> exact founder/authority gate where required
-> create Spec Kit spec
-> clarify
-> research
-> plan + Constitution Check
-> data model/contracts/quickstart
-> tasks/analyze
-> implement
```

This roadmap is designed so MSTR wins through concentrated code capability and verified training signal rather than scale alone.
