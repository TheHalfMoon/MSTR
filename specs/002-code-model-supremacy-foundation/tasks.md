# Tasks — MSTR-000B Code Model Supremacy Foundation

```text
WORKSTREAM = MSTR-000B
WEIGHT_CHANGING_TRAINING = PROHIBITED
PAID_COMPUTE = PROHIBITED
LARGE_DATASET_INGESTION = PROHIBITED
NEW_WEIGHT_ACCESS_OUTSIDE_EXISTING_ENVELOPE = EXPLICIT_GATE
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Execution Policy

MSTR-000B has early-safe tasks and convergence tasks.

```text
EARLY_SAFE:
B001-B009, B014-B025 may execute when their exact prerequisites are satisfied and they do not access new model weights or ingest large corpora.

CANDIDATE_EXTERNAL_EFFECT:
B010-B012 require their exact authority/inputs.

CONVERGENCE:
B013, B026-B030 require the stable evidence defined below.
```

MSTR-000A A001-A018 may proceed in parallel when model-independent. A019-A024 must consume the stable candidate/data/governance outputs required by this package.

---

# Phase G — Machine Governance and Drift Prevention

- [ ] **B001 Freeze machine-readable TaskNode / TaskEligibilityResult contracts.**  
  Define task state, prerequisites, outputs, supersession, external-effect class, required authority, candidate dependency, and closeout rules.  
  Outputs: `schemas/mstr-task-node-v0.schema.json`, `schemas/mstr-task-eligibility-v0.schema.json`, fixtures, `evidence/mstr-000b/B001-task-contract.md`.

- [ ] **B002 Implement offline task eligibility validator.**  
  Conceptual CLI: `python -m mstr_qualify task eligible <TASK_ID>`. Fail closed on missing predecessor, stale/superseded task, missing explicit authority, candidate-pool prerequisite, or canonical-state conflict. Validator performs no mutation.  
  Outputs: `src/mstr_qualify/task_gate.py`, CLI wiring, unit/contract tests, `evidence/mstr-000b/B002-task-gate.md`.

- [ ] **B003 Implement canonical drift detector.**  
  Compare task checkboxes/state/evidence/PR merge records where machine-readable. Detect examples such as implementation merged while task remains active, or task executed before declared entry gate.  
  Outputs: `src/mstr_qualify/task_drift.py`, tests/fixtures, `evidence/mstr-000b/B003-drift-detector.md`.

- [ ] **B004 Reconcile MSTR-000A entry semantics to live reality.**  
  Mark already canonical A001/A002 accurately; preserve A003+ live state; replace blanket post-T034 entry rule with explicit `EARLY_SAFE` vs `CONVERGENCE` prerequisites. Do not rewrite history or claim incomplete work complete.  
  Outputs: canonical task/state/roadmap amendments, `evidence/mstr-000b/B004-000a-sequence-reconciliation.md`.

**Checkpoint G:** repository tooling can prove whether a task is eligible rather than relying on prose memory.

---

# Phase B — Product-Aligned Backbone Rescan and Economics

- [ ] **B005 Run mission-aligned compact backbone metadata rescan.**  
  Search compact general and code-specialized base/foundation models without category exclusion. Revalidate exact current repositories, revisions, base/post-trained provenance, license/gating, context, parameter counts and intended use. `JetBrains/Mellum-4b-base` is mandatory to review.  
  No weight access.  
  Outputs: `evidence/mstr-000b/B005-code-backbone-rescan.md`, discovery manifest.

- [ ] **B006 Create/reconcile candidate records for newly relevant code-specialized models.**  
  Explicitly classify each as primary-eligible candidate, control, reference-only, rejected, or needs-founder/legal clarification. Apply the same derivative redistribution and accountless-release rights gate as existing candidates.  
  Outputs: `artifacts/candidates/*.json`, `evidence/mstr-000b/candidates/*.md`.

- [ ] **B007 Freeze tokenizer-economics benchmark corpus/protocol.**  
  Include Python, TypeScript/JavaScript, Rust, Go, Java, C/C++, SQL, shell, JSON/YAML/TOML, diffs, stack traces, file paths and tool JSON. Pin bytes and source hashes.  
  Outputs: `benchmarks/manifests/B007-tokenizer-economics.json`, fixtures, `evidence/mstr-000b/B007-tokenizer-protocol.md`.

- [ ] **B008 Measure tokenizer code density for all serious candidates.**  
  Record bytes/token, tokens/diff, tokens/stacktrace, tokens/tool call, per-language fragmentation and 8K effective code payload. No model inference required.  
  Outputs: `artifacts/results/tokenizer/B008/*.json`, `evidence/mstr-000b/B008-tokenizer-economics.md`.

- [ ] **B009 Freeze candidate trainability / conversion / runtime compatibility matrix.**  
  Revalidate current Transformers/Unsloth/PEFT/TRL compatibility, llama.cpp/GGUF conversion/quantization support, tokenizer/export hazards, and architecture-specific restrictions. Metadata/code/docs validation only unless already-authorized artifacts are sufficient.  
  Outputs: `artifacts/decisions/B009-training-runtime-compatibility.json`, `evidence/mstr-000b/B009-compatibility.md`.

- [ ] **B010 Freeze exact new-candidate weight-access envelope if any new artifact evidence is required.**  
  This is preflight only. Candidate IDs, exact revisions/files/hashes where available, network hosts, expected bytes, rights, executor, retention, cleanup and USD ceiling must be explicit.  
  Outputs: `artifacts/manifests/B010-new-candidate-weight-access.json`, `evidence/mstr-000b/B010-weight-access-preflight.md`.

- [ ] **B011 EXPLICIT NEW WEIGHT ACCESS GATE — acquire/verify only founder-authorized B010 candidates.**  
  Execute only after separate exact authorization if B010 is non-empty. Use approved ephemeral runners; founder Mac and Git receive no binaries. Verify exact integrity and emit T024-compatible manifests.  
  Outputs: `artifacts/manifests/B011-acquired-candidates.json`, runner evidence, `evidence/mstr-000b/B011-acquisition.md`.

- [ ] **B012 Run equivalent Q4/runtime/resource/raw-code qualification for new candidates.**  
  New candidates may not enter headline comparison with weaker evidence than existing candidates. Reuse canonical T029-T034 protocols where compatible; if superseded, record migration.  
  Outputs: `artifacts/results/backbone/B012/`, candidate Q4 manifests, `evidence/mstr-000b/B012-new-candidate-qualification.md`.

- [ ] **B013 Freeze stable product-aligned candidate pool for A019/tournament convergence.**  
  Require comparable hard-gate evidence or explicit N/A/rejection reasons. Do not select the final backbone merely from this task.  
  Outputs: `artifacts/decisions/B013-stable-candidate-pool.json`, `evidence/mstr-000b/B013-candidate-pool.md`.

**Checkpoint B:** candidate pool reflects MSTR's code-specialized mission and has equivalent deployment evidence.

---

# Phase D — Data Constitution and Software-Evolution Foundation

- [ ] **B014 Freeze `MSTR-DATA-CONSTITUTION-v0`.**  
  Define allowed/prohibited source classes, software-role taxonomy, provenance/rights, contamination, dedup, benchmark exclusion, synthetic/student/teacher policy, difficulty policy, verifier-health thresholds, stage admission rules, and private-user-data default rejection.  
  Outputs: `docs/data/MSTR_DATA_CONSTITUTION.md`, schema/fixtures, `evidence/mstr-000b/B014-data-constitution.md`.

- [ ] **B015 Freeze programming-language/tooling target policy.**  
  Use target-user/product evidence, not marketing breadth. Define core/secondary/long-tail language tiers and replay minimums; include build/config/shell/SQL where relevant.  
  Outputs: `artifacts/decisions/B015-language-target-policy.json`, `evidence/mstr-000b/B015-language-mix.md`.

- [ ] **B016 Freeze `SoftwareEvolutionRecord` contract and future-history boundary.**  
  Bind base revision, direction/issue, visible context, change/test/CI/review/recovery events and final verified revision while explicitly preventing future patches/results from leaking into earlier model-visible steps.  
  Outputs: schema, fixtures, `evidence/mstr-000b/B016-software-evolution.md`.

- [ ] **B017 Build a tiny fixture-only software-evolution extractor/projection proof.**  
  No large corpus ingestion. Demonstrate deterministic projection of localization/edit/review-repair examples from synthetic or already-repository-owned fixtures.  
  Outputs: implementation/tests/fixtures, `evidence/mstr-000b/B017-evolution-fixture-pilot.md`.

- [ ] **B018 Freeze execution-filtered student self-alignment contract.**  
  Student-generated tasks/solutions/tests require sandbox execution, independent verifier health, contamination/provenance and difficulty records before training admission.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B018-self-alignment-contract.md`.

- [ ] **B019 Freeze bounded teacher-rescue policy.**  
  Teachers are optional frontier-rescue/reference sources. Record teacher identity/terms/cost; independently execute/verify outputs; reject incompatible rights. Paid/API teacher use is not authorized here.  
  Outputs: `docs/data/TEACHER_RESCUE_POLICY.md`, schema/fixtures, `evidence/mstr-000b/B019-teacher-policy.md`.

- [ ] **B020 Freeze checkpoint-relative difficulty calibration contract.**  
  Define exact student/harness/sampling identity and classes `TOO_EASY`, `LEARNABLE_FRONTIER`, `HARD_FRONTIER`, `CURRENTLY_UNPRODUCTIVE`, `INVALID`.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B020-difficulty-contract.md`.

- [ ] **B021 Implement fixture-only frontier sampler/calibrator.**  
  Demonstrate refreshable task difficulty and sampling decisions without training or large data. Preserve easier replay/regression anchors and harder frontier cells.  
  Outputs: `src/mstr_qualify/curriculum/`, tests, `evidence/mstr-000b/B021-frontier-sampler.md`.

**Checkpoint D:** downstream MSTR-001 can build a legally traceable software-evolution/data curriculum rather than an undifferentiated code corpus.

---

# Phase V — Verifier Health, Test Generation, and Training Signal Integrity

- [ ] **B022 Freeze `VerifierHealthRecord` contract.**  
  Require evaluator hashes, protected paths, oracle/no-op/known-bad behavior where applicable, mutation/shortcut tests, generated-test independence, leakage/disagreement signals, and health class.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B022-verifier-health.md`.

- [ ] **B023 Implement verifier-health evaluator on controlled fixtures.**  
  Prove `HEALTHY`, `PARTIAL`, `DISAGREEMENT`, `BROKEN`, `LEAKED`, and `TAMPERED` classifications; integrate with training trajectory admission as a blocking field.  
  Outputs: verifier-health module/tests, `evidence/mstr-000b/B023-verifier-health-implementation.md`.

- [ ] **B024 Freeze test-generation curriculum and acceptance semantics.**  
  Include reproduce-before-fix, targeted regression, boundary/error, property/metamorphic where appropriate, pre-fix fail/post-fix pass, and rejection of answer-encoding/test weakening.  
  Outputs: `docs/data/TEST_GENERATION_CURRICULUM.md`, fixtures, `evidence/mstr-000b/B024-test-curriculum.md`.

- [ ] **B025 Freeze greenfield/feature/synthesis curriculum.**  
  Define G0 function, G1 module+tests, G2 component/file, G3 multi-file feature, G4 bounded program, G5 multi-round evolution. Include feature-tree/semantic synthesis as experimental generator with independent verification.  
  Outputs: `docs/data/GREENFIELD_FEATURE_CURRICULUM.md`, task manifest schema/fixtures, `evidence/mstr-000b/B025-greenfield-curriculum.md`.

**Checkpoint V:** clean positive training signal requires healthy verification; building and testing are both explicit learned skills.

---

# Phase R — Research Efficiency, Q4, and Long-Horizon Quality

- [ ] **B026 Freeze multi-fidelity MSTR Research Ladder v0.**  
  L0 contract/smoke -> L1 code/FIM/edit/tool -> L2 executable repo -> L3 Direction-to-Done/feature/program -> L4 Q4 universal-laptop. Define per-level promotion/hard-reject criteria.  
  Outputs: contract/config, `evidence/mstr-000b/B026-research-ladder.md`.

- [ ] **B027 Qualify the research ladder with one non-weight-changing campaign.**  
  Use a bounded harness/config experiment. Demonstrate early discard, promotion, immutable evaluator authority and full ledger.  
  Outputs: `artifacts/results/research/B027/`, `evidence/mstr-000b/B027-ladder-pilot.md`.

- [ ] **B028 Freeze Q4-in-the-loop promotion contract and training-method tournament preflight.**  
  Require release-relevant Q4 regression after material weight-changing stages. Preflight equivalent supported arms: 16-bit LoRA, 16-bit LoRA+rsLoRA, 4-bit QLoRA, 4-bit QLoRA+rsLoRA. Revalidate backbone/Unsloth/Transformers guidance immediately before execution.  
  Outputs: `artifacts/manifests/B028-method-tournament-preflight.json`, `docs/training/Q4_PROMOTION_CONTRACT.md`, `evidence/mstr-000b/B028-training-methods.md`.

- [ ] **B029 Freeze adaptive test-time compute + selective-context policy.**  
  One attempt by default; targeted repair/limited branching only when verifier/uncertainty evidence justifies cost. Define context intents including `NO_RETRIEVAL`, `NEED_FILE`, `NEED_SYMBOL`, `NEED_HISTORY`, `NEED_TEST`, `NEED_CONFIG`, `NO_MORE_CONTEXT`.  
  Outputs: policy/config schemas, `evidence/mstr-000b/B029-adaptive-inference.md`.

- [ ] **B030 Freeze Repository Health Delta + cross-harness robustness evaluation.**  
  Define multi-round codebase-health dimensions and require raw/H0/H1/H2 score attribution. Severe harness lock-in or accumulating technical debt is a blocking risk for claims.  
  Outputs: metric contracts, fixtures, `evidence/mstr-000b/B030-long-horizon-quality.md`.

**Checkpoint R:** research can cheaply reject bad ideas, and surviving model changes are judged on actual Q4/product behavior and long-run software quality.

---

# Phase C — Convergence and Training-Readiness Closeout

- [ ] **B031 Reconcile A019/A020 and legacy MSTR-000 tournament/preflight tasks with MSTR-000B.**  
  A019 requires B013 stable candidate pool, relevant A001-A018 contracts, and B022 verifier-health contract. A020 research loop must consume B026 fidelity ladder. Legacy candidate/tournament/data tasks must be marked retained, superseded, or amended; no incompatible duplicate remains.  
  Outputs: task supersession/dependency map, canonical task updates, `evidence/mstr-000b/B031-tournament-reconciliation.md`.

- [ ] **B032 Amend MSTR-001/MSTR-002/MSTR-003 entry requirements.**  
  MSTR-001 consumes Data Constitution, language mix, software evolution, frontier curriculum and Q4 promotion. MSTR-002 consumes self-alignment, teacher policy, verifier health, test generation, greenfield/feature and same-loop trajectories. MSTR-003 consumes frontier curriculum, admitted environments, verifier health and multi-fidelity RL promotion.  
  Outputs: roadmap/training strategy/preplan amendments, `evidence/mstr-000b/B032-downstream-contracts.md`.

- [ ] **B033 Independent consistency/red-team review.**  
  Review candidate fairness, data leakage, rights, reward hacking, task-gate bypass, teacher contamination, tokenizer comparability, Q4 promotion, WePLD attribution, and 8GB product preservation. Resolve all material findings.  
  Outputs: `evidence/mstr-000b/B033-independent-review.md`.

- [ ] **B034 Close MSTR-000B canonical.**  
  Freeze exact contract versions, stable candidate pool state, unresolved risks, supersession map, training-readiness statement and next exact authority. This task MUST NOT authorize weight-changing training.  
  Outputs: `artifacts/decisions/B034-mstr-000b-closeout.json`, `evidence/mstr-000b/B034-closeout.md`, canonical state updates.

**Checkpoint C:** MSTR can approach weight-changing training only with product-aligned candidates, high-signal data contracts, healthy verifiers, dynamic curriculum, Q4 promotion and machine-enforced governance.

---

## Hard Stops

MSTR-000B cannot close with any of:

```text
TASK_DEPENDENCY_GATE_UNENFORCED = YES
MISSION_ALIGNED_RESCAN_MISSING = YES
SERIOUS_CODE_BASE_OMITTED_WITHOUT_REASON = YES
CANDIDATE_EVIDENCE_NOT_COMPARABLE = YES
DATA_CONSTITUTION_MISSING = YES
SOFTWARE_EVOLUTION_FUTURE_LEAKAGE_UNCONTROLLED = YES
SELF_ALIGNMENT_CAN_ADMIT_UNVERIFIED_SUCCESS = YES
TEACHER_OUTPUT_TREATED_AS_TRUTH = YES
DIFFICULTY_NOT_BOUND_TO_STUDENT_IDENTITY = YES
VERIFIER_HEALTH_MISSING = YES
TEST_WEAKENING_CAN_CREATE_SUCCESS = YES
GREENFIELD_FEATURE_COVERAGE_MISSING = YES
RESEARCH_LOOP_CAN_SKIP_FROZEN_EVALUATION = YES
Q4_REGRESSION_NOT_BLOCKING = YES
REPOSITORY_HEALTH_UNMEASURED_FOR_LONG_HORIZON_CLAIMS = YES
HARNESS_GAIN_MISATTRIBUTED = YES
NEW_WEIGHT_ACCESS_WITHOUT_EXACT_AUTHORITY = YES
WEIGHT_CHANGING_TRAINING_AUTHORIZED_BY_THIS_WORKSTREAM = YES
```

## Dependency Summary

```text
B001 -> B002 -> B003 -> B004

B005 -> B006 -> B007 -> B008 -> B009 -> B010 -> [founder gate if non-empty] -> B011 -> B012 -> B013

B014 -> B015
B014 -> B016 -> B017
B014 -> B018 -> B019
B014 -> B020 -> B021
B014 -> B022 -> B023 -> B024
B014 -> B025

A006/A014-equivalent verifier foundation + B022 -> B023

B026 -> B027
B022 + B024 + B025 -> B026
B009 + B014 + B022 -> B028
B020 + MSTR-000A loop/context contracts -> B029
B024 + B025 + A019-ready harness surfaces -> B030

T034/equivalent candidate qualification
+ A001-A018 required outputs
+ B013
+ B023
+ B026
-> A019 convergence

A019/A020 + B027-B030 -> B031 -> B032 -> B033 -> B034

B034 != TRAINING AUTHORIZATION
```
