# MSTR Frontier Acceleration Strategy

**Status:** FOUNDER-DIRECTED PROGRAM PLANNING AMENDMENT / canonical only when merged
**Date:** 2026-09-04
**Purpose:** Keep MSTR on the strongest defensible path to record-setting verified local software-engineering capability as the model, training, quantization, and agent-runtime frontier changes.

## Authority Boundary

This document is planning and governance only.

```text
MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED_BY_THIS_DOCUMENT
MODEL_EXECUTION = NOT_AUTHORIZED_BY_THIS_DOCUMENT
QUANTIZATION_EXECUTION = NOT_AUTHORIZED_BY_THIS_DOCUMENT
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED_BY_THIS_DOCUMENT
LARGE_DATASET_INGESTION = NOT_AUTHORIZED_BY_THIS_DOCUMENT
PAID_COMPUTE = NOT_AUTHORIZED_BY_THIS_DOCUMENT
PAID_MODEL_API = NOT_AUTHORIZED_BY_THIS_DOCUMENT
LARGE_SCALE_RL = NOT_AUTHORIZED_BY_THIS_DOCUMENT
PRODUCTION_RELEASE = NOT_AUTHORIZED_BY_THIS_DOCUMENT
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

External releases, papers, model cards, vendor benchmark claims, and public leaderboards are research inputs only. They never create MSTR authority, candidate admission, qualification, benchmark truth, or release claims by themselves.

## 1. North Star — Verified Work, Not Leaderboard Theater

MSTR remains a universal-laptop code-specialized software-engineering model/system.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY = DVCR / DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED = TTVC / TIME_TO_VERIFIED_COMPLETION
PRIMARY_EFFICIENCY = VERIFIED_SOFTWARE_CAPABILITY_PER_GB
```

MSTR should pursue leadership in a scope that can be measured honestly:

> Highest verified software-engineering utility per GB and per second inside the fixed universal-laptop envelope.

Public coding benchmarks remain continuity evidence. They are not the release north star and may not override fresh/private Direction-to-Done evidence.

## 2. Product Envelope — Unchanged

The frontier does not justify silently raising the hardware floor.

```text
PRIMARY_RELEASE = UNIVERSAL_LAPTOP
REFERENCE_TOTAL_RAM = 8_GB
CPU_ONLY_BASIC_OPERATION = REQUIRED
DISCRETE_GPU_REQUIRED = NO
REFERENCE_CONTEXT = 8K
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
OFFLINE_AFTER_ACQUISITION = REQUIRED
ACCOUNT_OR_API_KEY_REQUIRED = NO
WINDOWS + LINUX + MACOS = REQUIRED
TELEMETRY_DEFAULT = OFF
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

Optional larger, accelerated, distributed, or research editions may exist later only as separately measured editions. They may not redefine the primary product.

## 3. Core System Thesis

MSTR should not be optimized as weights in isolation. The record target is a co-designed local coding stack:

```text
MSTR WEIGHTS
× CODE/REPOSITORY TRAINING
× SOFTWARE-EVOLUTION DATA
× EXECUTION-GROUNDED AGENT TRAINING
× ADAPTIVE CONTEXT/COMPUTE
× TYPED TOOL/EDIT SURFACES
× INDEPENDENT VERIFICATION
× QUANTIZATION
× CPU RUNTIME/KERNELS
```

The required score attribution remains separate:

```text
RAW_MODEL
NEUTRAL_MINIMAL_HARNESS
MSTR_NATIVE_HARNESS
MSTR_PLUS_WEPLD
```

A harness-only improvement is not a model-weight improvement. A tokens-per-second improvement that worsens verified completion is not a speed win.

## 4. September 2026 Frontier Evidence Update

This section records research inputs that appeared or materially changed after the 2026-08-27 MSTR-000B research snapshot.

### 4.1 IFM K2 Horizon

Primary public sources:

- `https://ifm.ai/k2/`
- `https://ifm.ai/blog/k2`
- `https://huggingface.co/collections/IFM/k2-horizon`

Research implications:

1. The K2 Horizon family spans compact dense models and much larger dense/sparse models under one training lifecycle.
2. IFM publishes unusually deep lifecycle material: model weights, intermediate checkpoints, training code/recipes, data/mixture material, and evaluation infrastructure.
3. The compact 0.9B, 3.7B, and 7B releases are material new evidence for the small coding/agentic frontier.
4. K2 Horizon 3.7B is a particularly relevant *research challenger* because its size is close to MSTR's likely dense-backbone sweet spot while remaining potentially compatible with the <=3 GB Q4 product target.
5. K2 Horizon 7B is a stretch/upper-bound candidate only if exact low-bit artifact, 8 GB whole-system, CPU runtime, and TTVC evidence can satisfy the primary product envelope.
6. K2 Horizon 0.9B is useful for tiny-model, draft, effort-routing, or future micro-edition research; it is not automatically a second runtime model.
7. K2 MoVA models are architecture/sparse-activation research inputs. Low active parameters do not erase total-weight storage/RAM requirements and therefore do not make a large MoVA model a universal-laptop candidate by default.
8. When upstream exposes base, intermediate, and post-trained checkpoints, MSTR should compare which checkpoint is the best *training substrate* rather than assuming the final assistant checkpoint is the best parent for MSTR-specific continued training.

No K2 model is preselected, admitted, authorized for weight access, or qualified by this strategy.

### 4.2 K2 Uno / Parallel-Generation Research

K2 Uno is a research input for a future MSTR-004 decoding tournament. Its public design explores a conditional adapter that changes the generation process while preserving a frozen autoregressive base.

MSTR consequence:

```text
AUTOREGRESSIVE_BASELINE
vs
SPECULATIVE_DECODING
vs
UNO_STYLE_OR_OTHER_PARALLEL_GENERATION
```

Only exact MSTR hardware/runtime evidence may select an arm. Cloud throughput or vendor tokens/second claims do not prove lower laptop TTVC.

### 4.3 Sherry / Structured Ternary Quantization

Primary public source:

- `https://aclanthology.org/2026.acl-long.513/`

Sherry demonstrates a 1.25-bit structured ternary design using 3:4 fine-grained sparsity and a training mechanism intended to avoid representation collapse.

MSTR consequence:

- extreme low-bit compression is now a serious research lane rather than a distant packaging idea;
- Sherry-class compression is not treated as a simple post-hoc file conversion;
- if a structured-ternary method requires weight-changing preparation, QAT, sparse training, distillation, or recovery training, that work belongs behind the exact training authority and must participate in checkpoint promotion;
- hardware-specific speed claims require exact kernel/runtime/CPU identity and must be remeasured on MSTR's reference lanes.

### 4.4 Tencent AngelSlim / Hy4

Primary public source:

- `https://github.com/Tencent/AngelSlim`

Hy4 itself is far outside the MSTR universal-laptop primary-backbone envelope. Its relevance is the surrounding systems research:

- extreme quantization;
- structured low-bit kernels;
- speculative decoding;
- compression-aware deployment;
- optional distributed execution.

MSTR consequence:

`Hy4 != MSTR candidate` by default.

AngelSlim techniques may become MSTR-004 research arms only after rights, architecture compatibility, runtime support, and exact local evidence are proven.

Distributed multi-machine execution may be an optional future acceleration mode, never a requirement for the primary release.

### 4.5 Cursor Composer 2 / Composer 2.5

Primary public sources:

- `https://prod.cursor.com/blog/composer-2-technical-report`
- `https://cursor.com/blog/composer-2-5`
- `https://cursor.com/blog/bootstrapping-composer-with-autoinstall`
- `https://cursor.com/blog/continually-improving-agent-harness`
- `https://prod.cursor.com/blog/how-cursor-router-works`
- `https://prod.cursor.com/blog/reward-hacking-coding-benchmarks`

No official Cursor Composer 3 release was verified for this planning update as of 2026-09-04. MSTR therefore does not invent Composer 3 specifications. The usable evidence is Composer 2/2.5 and Cursor's published engineering work.

MSTR consequences:

1. Strong code-focused continued pretraining before large agent RL remains a high-priority thesis.
2. Train/serve harness consistency matters: executable RL should resemble the actual MSTR software-building loop and tools.
3. Very long rollouts make terminal reward alone a weak credit-assignment signal; targeted local trajectory feedback/on-policy distillation is a serious measured arm.
4. Dynamic synthetic environment/task generation is high leverage only when environment health and shortcut resistance are independently verified.
5. Prior-generation MSTR may bootstrap future environments, but the generated environment cannot validate itself.
6. Agent/runtime complexity should be adaptive. MSTR should learn or deterministically estimate when FAST, NORMAL, or DEEP effort is justified instead of spending maximum compute on every task.
7. Public benchmark leakage, future Git history, internet solution lookup, evaluator access, cache recovery, and reward hacking are material threats to coding claims.

## 5. Frontier Freshness Gate Before Candidate-Pool Freeze

A stable candidate pool cannot be frozen from a stale scan merely because earlier scan tasks are terminal.

B013 must bind a **frontier snapshot** at exact B013 entry.

The snapshot must record at minimum:

```text
snapshot_time
canonical_main
last_canonical_backbone_scan_identity
last_canonical_access_envelope_identity
sources_checked
material_new_releases[]
per_release_disposition[]
```

A material new release is one that could plausibly change the primary MSTR backbone/finalist decision under the 8 GB / CPU / <=3 GB Q4 / rights / code-quality envelope.

Possible dispositions:

```text
NOT_MATERIAL_TO_PRIMARY_PRODUCT
REFERENCE_ONLY_PRODUCT_FLOOR_MISMATCH
RIGHTS_INCOMPATIBLE
RUNTIME_OR_EXPORT_INCOMPATIBLE
STATICALLY_REJECTED_WITH_EVIDENCE
REQUIRES_CANONICAL_REFRESH
EQUIVALENTLY_QUALIFIED
```

A candidate may not be rejected merely because it arrived after B010.

If `REQUIRES_CANONICAL_REFRESH` is present:

1. B013 remains `PENDING`.
2. Historical B005-B012 results remain historical truth and are not rewritten.
3. A separately governed task-graph/spec amendment must create the exact refresh path needed for metadata, rights, tokenizer, compatibility, access envelope, external authority, acquisition, and equivalent qualification.
4. New model-weight access remains separately founder-authorized.
5. B013 resumes only after the refresh evidence is canonical or the candidate receives an evidence-backed terminal rejection.

For the 2026-09-04 snapshot, K2 Horizon 3.7B is a mandatory material-release review input. This statement does not admit or authorize it.

## 6. Backbone Tournament Strategy

MSTR should prefer a small dense primary model unless evidence proves another topology dominates whole-laptop utility.

Current research hypothesis:

```text
PRIMARY_DENSE_RESEARCH_BAND ~= 3B_TO_4B
```

This is not a hard architectural law or final selection.

A future comparable tournament should include:

- the strongest already-qualified MSTR candidates;
- Mellum-4B if B012 evidence retains it;
- any later frontier candidate that survives the freshness gate and receives equivalent qualification;
- controls sufficient to detect whether apparent gains come from scale, post-training, tokenizer, or harness effects.

Hard gates precede Pareto ranking:

```text
RIGHTS
-> ARTIFACT / EXPORT / QUANTIZATION
-> <=3 GB Q4 TARGET
-> 8 GB WHOLE-SYSTEM VIABILITY
-> CPU RUNTIME
-> RAW CODE / FIM
-> REPOSITORY / DIRECTION-TO-DONE
-> TTVC
```

No scalar benchmark score selects the winner.

## 7. Checkpoint-Lineage Tournament

When an upstream family exposes true base, intermediate, mid-trained, or post-trained checkpoints under compatible rights, MSTR-001 planning should treat checkpoint identity as an experiment dimension.

Example:

```text
BASE_FINAL
vs
MID_CHECKPOINT_A
vs
MID_CHECKPOINT_B
vs
POST_TRAINED_FINAL
```

The question is not "which upstream checkpoint chats best?" The question is:

> Which immutable checkpoint is the best substrate for MSTR's code/repository training and later agent training after identical bounded adaptation/evaluation?

Every arm must preserve exact upstream revision, artifact hash, tokenizer identity, data/update budget, seed policy, export path, Q4 path, and evaluation identity.

## 8. MSTR-001 — Build the Code Brain

MSTR-001 remains the first material weight-changing capability stage after convergence and exact authority.

Required data/capability families remain:

```text
CODE
FIM
TESTS
DIFFS
BUILD_CI
TOOL_SHELL
ISSUE_DIRECTION
PR_REVIEW
SOFTWARE_EVOLUTION
REPAIR_RECOVERY
FEATURE_GREENFIELD
SECURITY
GENERAL_SOFTWARE_REASONING_REPLAY
```

Additional September requirements:

1. checkpoint-lineage substrate comparison when applicable;
2. direct-code/FIM/repository proxies before agentic optimization;
3. dynamic student-frontier sampling;
4. explicit replay sufficient to prevent destructive forgetting;
5. Q4 promotion after every material checkpoint;
6. low-bit-aware training compatibility recorded early so an otherwise strong checkpoint is not selected if its product quantization path is structurally poor.

## 9. MSTR-002 — Train a Software Engineer, Not a Chatbot

MSTR-002 should teach the same semantic build loop served in production:

```text
ORIENT / GOAL
-> LOCALIZE
-> PLAN_ONLY_AS_NEEDED
-> ACT
-> OBSERVE
-> VERIFY
-> RECOVER
-> STOP
```

Required behavior includes:

- repository inspection/localization;
- precise multi-file edits;
- tests and verifier use;
- build/CI/tool usage;
- feature and greenfield construction;
- reviewer/tester modes;
- failure recovery and rollback;
- minimal/surgical change preference;
- explicit negative examples for fake completion, tool misuse, test weakening, evaluator tampering, secret leakage, and unnecessary refactoring;
- persistent direct-code/FIM replay.

## 10. MSTR-003 — Executable Agent RL

MSTR-003 should become the main long-horizon software-engineering optimization stage, but only after admitted environments and healthy verifiers exist.

Required measured research arms:

### 10.1 Production-Compatible Executable RL

The model-visible loop, tool grammar, edit semantics, context ordering, and verifier boundary must match production or have an explicitly proven migration.

### 10.2 Dynamic Environment/Task Factory

Candidate generation modes may include:

```text
FEATURE_DELETION_AND_REBUILD
BUG_INJECTION
TYPE_ERROR_INJECTION
API_MIGRATION
DEPENDENCY_UPGRADE
BROKEN_BUILD
BROKEN_CI
PARTIAL_REFACTOR
CROSS_FILE_RENAME
TEST_REGRESSION
SECURITY_HARDENING
PERFORMANCE_REGRESSION
GREENFIELD_FEATURE
```

Generated environments require independent admission:

```text
BOOT
-> RESET/REPLAY
-> VERIFIER_HEALTH
-> NO_ANSWER_LEAKAGE
-> NO_FUTURE_HISTORY
-> SHORTCUT BATTERY
-> DIFFICULTY CALIBRATION
-> ADMIT | REJECT
```

### 10.3 Previous-MSTR Autoinstall / Bootstrap

A previous MSTR checkpoint may propose setup/bootstrap repairs for future training environments. It may not admit the environment it created. Independent deterministic environment/verifier checks remain authoritative.

### 10.4 Targeted Trajectory Feedback

For long trajectories, final reward alone may be insufficient.

MSTR-003 should evaluate a bounded arm that binds local feedback to the exact action/turn responsible for a known error while preserving on-policy identity and independent terminal verification.

Examples:

```text
wrong tool choice
invalid tool arguments
unnecessary broad edit
ignored verifier evidence
incorrect recovery decision
premature finish proposal
```

This is a measured training arm, not pre-authorized execution or a claim that one proprietary method is required.

### 10.5 Reward-Hacking Resistance

Training environments must test for shortcuts such as:

- modifying/deleting tests;
- weakening assertions;
- reading protected evaluator files;
- recovering future patches from Git history;
- internet/public-solution lookup;
- cached-solution recovery;
- spoofing command output;
- decompiling or otherwise extracting hidden answers from evaluator artifacts;
- exploiting environment bugs instead of solving the software task.

A shortcut-discovered success is not clean positive RL evidence.

## 11. Adaptive Effort Controller

MSTR should optimize end-to-end TTVC by spending only the compute needed for the task.

Conceptual modes:

```text
FAST
NORMAL
DEEP
```

These are not necessarily separate models.

They may vary bounded budgets for:

```text
repository retrieval
planning depth
reasoning tokens
branch/best-of-K use
repair depth
verification breadth
```

Promotion requires joint evidence:

```text
DVCR
TTVC
TOKENS_PER_VERIFIED_COMPLETION
TOOL_CALLS_PER_VERIFIED_COMPLETION
PEAK_RSS
WHOLE_LAPTOP_USABILITY
```

The controller may not trade correctness for superficial latency.

## 12. Q4 Anchor + Extreme Low-Bit Challenger Ladder

The existing Q4 promotion contract remains mandatory and unchanged in authority.

```text
Q4 = REQUIRED QUALITY / PRODUCT ANCHOR
```

Sub-Q4 research is additive:

```text
Q4_BASELINE
-> Q3_CANDIDATE
-> Q2_CANDIDATE
-> STRUCTURED_TERNARY_OR_SHERRY_CLASS_CANDIDATE
```

Rules:

1. No sub-Q4 artifact may replace the mandatory Q4 promotion record.
2. Every low-bit arm must bind exact source checkpoint, quantization/training method, tool revision, recipe, artifact hash, runtime/kernel identity, CPU/hardware, context, and cache state.
3. If the method changes weights or requires recovery/QAT/distillation/sparse training, it is a weight-changing stage and requires exact training authority plus the normal Q4 checkpoint lineage.
4. A smaller file is not a product win if DVCR, TTVC, stability, repository behavior, or whole-laptop usability regresses materially.
5. Hardware-specific kernels are optional research dependencies until cross-platform evidence justifies admission.

## 13. MSTR-004 — Local Inference Speed Co-Design

MSTR-004 should measure end-to-end speed as a system tournament.

Arms may include:

```text
Q4 / Q3 / Q2 / STRUCTURED_TERNARY
CPU_KERNEL_VARIANTS
STABLE_PREFIX_CACHE
KV_PROFILE_VARIANTS
SPECULATIVE_DECODING
UNO_STYLE_OR_OTHER_PARALLEL_GENERATION
CONTEXT_COMPACTION
SELECTIVE_RETRIEVAL
FAST_NORMAL_DEEP_EFFORT_CONTROL
AFFECTED_TEST_SELECTION
INCREMENTAL_BUILD_TEST
WARM_ENVIRONMENT
BOUNDED_PARALLEL_NON_MODEL_TOOLS
```

The primary result is TTVC with verified success, not raw decoder throughput.

A valid speed comparison must preserve model/checkpoint identity where intended, task order, verifier requirements, cache state, context, hardware, thread count, runtime build, and timeouts.

## 14. MSTR-006 — Sealed Record Gauntlet

Headline claims must survive three evidence surfaces.

### 14.1 Public Continuity

Use public coding/agentic benchmarks only as labeled continuity evidence. Publish relevant limitations and contamination/leakage controls.

### 14.2 Sealed Public-Derived

Where a public-derived task is used for stronger inference claims:

- remove or isolate future Git history;
- prohibit public-solution lookup;
- control outbound network access;
- protect evaluator/answer artifacts;
- clear caches that could contain solutions;
- record the exact sealing policy and verifier identity.

### 14.3 Fresh/Private MSTR Gauntlet

Maintain fresh tasks spanning:

```text
BUG_REPAIR
FEATURE_IMPLEMENTATION
GREENFIELD
MIGRATION
REFACTOR
TEST_GENERATION
BUILD_CI
SECURITY
RECOVERY
MULTI_ROUND_REPOSITORY_EVOLUTION
```

Required report fields include:

```text
DVCR
TTVC_P50
TTVC_P95
FPAR
ESR
RSR
TER
RHD
ARTIFACT_BYTES
PEAK_RSS
WHOLE_LAPTOP_USABILITY
TOKENS_PER_VERIFIED_COMPLETION
TOOL_CALLS_PER_VERIFIED_COMPLETION
ENERGY_PER_VERIFIED_COMPLETION_WHERE_REPRODUCIBLE
```

Any discovered benchmark leakage or reward shortcut must be preserved as negative evidence and the affected headline result must be invalidated or explicitly corrected.

## 15. Default Runtime Topology

The default remains deliberately small:

```text
ONE MSTR BUILDER
+
INDEPENDENT DETERMINISTIC VERIFIER
```

Do not ship a default model swarm merely because multi-agent research can solve larger tasks. Extra model copies must earn their RAM/TTVC/complexity cost.

Parallel deterministic tools may be evaluated where they improve TTVC without multiplying model memory, for example lint, type checking, affected tests, static analysis, or repository search.

## 16. B013 / B032 / B033 Integration

### B013

B013 owns candidate-pool freeze and therefore must enforce the frontier freshness gate before `stable_pool=true`.

### B032

When B032 becomes eligible, it must carry this strategy into downstream entry requirements:

- MSTR-001: checkpoint-lineage substrate experiments where applicable, direct-code/FIM foundation first, low-bit compatibility awareness, Q4 promotion unchanged;
- MSTR-002: production-compatible software-engineering trajectories and negative/failure examples;
- MSTR-003: executable RL, environment factory, previous-MSTR bootstrap, targeted trajectory feedback, shortcut resistance;
- roadmap consequences for MSTR-004: Q4 anchor plus low-bit/runtime/speculation/effort-controller tournament;
- roadmap consequences for MSTR-006: sealed anti-leakage headline qualification.

B032 does not execute any of those future external effects.

### B033

B033 must red-team:

- frontier freshness and candidate omission;
- benchmark/future-history/network leakage;
- reward hacking and evaluator extraction;
- low-bit quality claims;
- hardware-specific speed claims;
- model-vs-harness attribution;
- 8 GB product preservation;
- rights/provenance across models, datasets, quantizers, kernels, and teachers.

## 17. Decision / Kill Gates

MSTR should aggressively discard research arms that fail the product objective.

### Backbone kill gates

```text
RIGHTS_FAIL
PRIMARY_Q4_TARGET_FAIL_WITHOUT_CREDIBLE_LOW_BIT_PATH
8GB_WHOLE_SYSTEM_FAIL
CPU_RUNTIME_UNSUPPORTED_WITHOUT_CREDIBLE_PATH
RAW_CODE_OR_FIM_MATERIALLY_WEAK
TTVC_DOMINATED_WITHOUT_MATERIAL_DVCR_GAIN
```

### Training kill gates

```text
DIRECT_CODE_OR_FIM_REGRESSION
Q4_PROMOTION_REJECTED
VERIFIER_HEALTH_UNSATISFIED
REWARD_HACKING_UNRESOLVED
REPOSITORY_HEALTH_COLLAPSE
CATASTROPHIC_FORGETTING
COST_OR_REPRODUCIBILITY_OUTSIDE_AUTHORITY
```

### Runtime/quantization kill gates

```text
DVCR_REGRESSION_EXCEEDS_PREDECLARED_BOUND
TTVC_NO_IMPROVEMENT
PEAK_RSS_OR_SWAP_REGRESSION
CROSS_PLATFORM_PATH_NOT_CREDIBLE_FOR_PRIMARY_RELEASE
HARDWARE_SPECIFIC_CLAIM_NOT_REPRODUCIBLE
```

## 18. What MSTR Must Not Do

MSTR must not:

- chase one public leaderboard as the optimization target;
- select K2, Mellum, Qwen, or any other backbone from reputation alone;
- treat active-parameter count as storage/RAM equivalence;
- copy Hy4-scale deployment assumptions into the 8 GB product;
- replace the mandatory Q4 gate with an experimental lower-bit artifact;
- treat Sherry-class compression as a no-training post-processing promise;
- claim vendor speedups as MSTR speedups without exact local reproduction;
- make a second model, agent swarm, vector database, or distributed cluster a default dependency without measured value;
- use future Git history, public fixes, hidden evaluator details, or cached solutions in headline evaluation;
- let a student/teacher/generated environment certify itself;
- attribute harness/runtime gains to model weights;
- raise the primary hardware floor to make a preferred model fit.

## 19. Immediate Governance Consequence

This strategy does not interrupt the active dependency-ordered B011 closeout -> B012 path.

It changes what must be true **before B013 freezes the stable candidate pool** and what B032/B033 must later reconcile.

The immediate sequence remains:

```text
B011 CANONICAL CLOSEOUT
-> B012 EQUIVALENT QUALIFICATION
-> B013 FRONTIER FRESHNESS SNAPSHOT
-> if no material unresolved frontier candidate: freeze comparable stable pool
-> if material unresolved frontier candidate exists: STOP B013 and create canonical refresh task/spec amendment
-> resume B013 only after refresh/rejection evidence is canonical
```

This preserves historical truth, bounded authority, and task ordering while preventing MSTR from freezing a candidate pool that is already obsolete.

## 20. Success Definition

The target is not "another good 3B-4B coding model."

MSTR succeeds when it can defend a measured claim that, inside the universal-laptop envelope, it converts software direction into independently verified working software at an exceptional joint frontier of:

```text
QUALITY / DVCR
× SPEED / TTVC
× ARTIFACT SIZE
× RAM
× CPU USABILITY
× REPOSITORY HEALTH
× PRIVACY / OFFLINE OPERATION
```

The weights, training recipe, agent loop, verifier, quantization, and runtime are optimized together, but their gains remain separately attributable and reproducible.
