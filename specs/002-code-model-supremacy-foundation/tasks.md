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

### Machine-gate bootstrap and enforcement

B001 and B002 are the only bootstrap exception because B002 does not exist before it is implemented. They MUST be executed under the manually verified prerequisites in this file and ordinary exact-head governance.

Once B002 is `COMPLETE_CANONICAL`, **every material B003+ task execution and every corresponding merge MUST have a successful exact-main task-eligibility result**. `eligible=false`, validator failure, unresolved prerequisite, supersession, missing authority, candidate-pool mismatch, or canonical-state drift is a hard stop. The validator verifies authority; it never creates authority.

MSTR-000A A001-A018 may proceed in parallel when model-independent. A019-A024 must consume the stable candidate/data/governance outputs required by this package.

---

# Phase G — Machine Governance and Drift Prevention

- [x] **B001 Freeze machine-readable TaskNode / TaskEligibilityResult contracts.**
  Define task state, prerequisites, outputs, supersession, external-effect class, authority mapping, candidate-pool requirements, and closeout rules. Include fixtures for every authority-gated external-effect class missing `required_authority_id`, and candidate-dependent tasks missing `candidate_pool_requirement_id`; each must fail closed.
  Outputs: `schemas/mstr-task-node-v0.schema.json`, `schemas/mstr-task-eligibility-v0.schema.json`, fixtures, `evidence/mstr-000b/B001-task-contract.md`.
  Canonical implementation: PR #40 / final head `5e81f5a572c6f8409e67ccde7cc1a4aa556b30ea` / merge `773555e9861d1c901c12718832821a98f472833f`.

- [x] **B002 Implement offline task eligibility validator.**
  Conceptual CLI: `python -m mstr_qualify task eligible <TASK_ID>`. Fail closed on missing predecessor, stale/superseded task, missing explicit authority, candidate-pool prerequisite, or canonical-state conflict. Validator performs no mutation. B001/B002 bootstrap uses manual exact-prerequisite verification; after B002 becomes canonical there is no general bypass.
  Outputs: `src/mstr_qualify/task_gate.py`, CLI wiring, unit/contract tests, `evidence/mstr-000b/B002-task-gate.md`.
  Canonical implementation: PR #48 / final head `9905237b0685b50059112d19e2708ba6357283b6` / merge `298a97e957fe98edec2c9fdd3f78f0f909ec09fa`.

- [x] **B003 Implement canonical drift detector.**
  Prerequisite: B002 `COMPLETE_CANONICAL` and an exact-main `eligible=true` result. Compare task checkboxes/state/evidence/PR merge records where machine-readable. Detect examples such as implementation merged while task remains active, or task executed before declared entry gate.
  Outputs: `src/mstr_qualify/task_drift.py`, tests/fixtures, `evidence/mstr-000b/B003-drift-detector.md`.
  Canonical implementation: PR #50 / final head `f3ccad9d49ea9d0460f82d7ecfe64b649bd997cf` / merge `8bea74269fb81a4c898b7a2864bf103d15fd98a9`.

- [x] **B004 Reconcile MSTR-000A entry semantics to live reality.**
  Prerequisite: B003 `COMPLETE_CANONICAL` and exact-main `eligible=true`. Mark canonical A001/A002/A003 accurately, including PR #38 head `41122ae8dee65b2a6b3c6b188cf335d74088b06f` and merge `2c02eb68a32264c86f69eb7ffc1c99ad87328376`; preserve A004+ live state; replace the blanket post-T034 entry rule with explicit `EARLY_SAFE` vs `CONVERGENCE` prerequisites. Do not rewrite history or claim incomplete work complete.
  Outputs: canonical task/state/roadmap amendments, `evidence/mstr-000b/B004-000a-sequence-reconciliation.md`.
  Canonical implementation: PR #52 / final head `9b8ad22e59e096409b753a6264e61ee59a966dc4` / merge `fa90726a6415cab0b655acae4768c7343cc6370c`.

**Checkpoint G:** repository tooling can prove whether a task is eligible rather than relying on prose memory.

---

# Phase B — Product-Aligned Backbone Rescan and Economics

- [x] **B005 Run mission-aligned compact backbone metadata rescan.**
  Search compact general and code-specialized base/foundation models without category exclusion. Revalidate exact current repositories, revisions, base/post-trained provenance, license/gating, context, parameter counts and intended use. `JetBrains/Mellum-4b-base` is mandatory to review.  
  No weight access.  
  Outputs: `evidence/mstr-000b/B005-code-backbone-rescan.md`, discovery manifest.
  Canonical implementation: PR #54 / final head `0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a` / merge `1e096f4d1f270b2803da6a6306e9e7f0cf8fb81b`.


- [x] **B006 Create/reconcile candidate records for newly relevant code-specialized models.**
  Explicitly classify each as primary-eligible candidate, control, reference-only, rejected, or needs-founder/legal clarification. Apply the same derivative redistribution and accountless-release rights gate as existing candidates.  
  Outputs: `artifacts/candidates/*.json`, `evidence/mstr-000b/candidates/*.md`.
  Canonical implementation: PR #57 / final head `98b549e9d8b2550725861e133ee8f909690dc9c8` / merge `c96e2fb228a7f3fb0399484a9e6bb1e1d1eb086c`.

- [x] **B007 Freeze tokenizer-economics benchmark corpus/protocol.**
  Include Python, TypeScript/JavaScript, Rust, Go, Java, C/C++, SQL, shell, JSON/YAML/TOML, diffs, stack traces, file paths and tool JSON. Pin bytes and source hashes.  
  Outputs: `benchmarks/manifests/B007-tokenizer-economics.json`, fixtures, `evidence/mstr-000b/B007-tokenizer-protocol.md`.
  Canonical implementation: PR #59 / final head `965fbdbf152272397ae6ef721260e806be5d251c` / merge `b9b0a8ca7b9b7528f5da518baa83b23e2348c6f6`.

- [x] **B008 Measure tokenizer code density for all serious candidates.**
  Record bytes/token, tokens/diff, tokens/stacktrace, tokens/tool call, per-language fragmentation and 8K effective code payload. Run any tokenizer acquisition/measurement in approved ephemeral research infrastructure when required; founder Mac remains zero-large-artifact. No model inference is authorized by this task.  
  Outputs: `artifacts/results/tokenizer/B008/*.json`, `evidence/mstr-000b/B008-tokenizer-economics.md`.
  Canonical implementation: PR #61 / final head `895983470f72128ad698023b3578553ed1cfe7c4` / merge `07762204ab126c0fccf9ca55a8b572bd6368d8bc`.

- [x] **B009 Freeze candidate trainability / conversion / runtime compatibility matrix.**
  Revalidate current Transformers/Unsloth/PEFT/TRL compatibility, llama.cpp/GGUF conversion/quantization support, tokenizer/export hazards, and architecture-specific restrictions. Metadata/code/docs validation only unless already-authorized artifacts are sufficient.  
  Outputs: `artifacts/decisions/B009-training-runtime-compatibility.json`, `evidence/mstr-000b/B009-compatibility.md`.
  Canonical implementation: PR #63 / final head `88ebc70e12dcc117ba99bb10bb687eed1a220a7b` / merge `4fdb6966c085819e69823136fb5e2cd8c56ba58f`.

- [x] **B010 Freeze exact new-candidate qualification/access envelope.**
  Distinguish `qualification_candidates[]` from `new_weight_access_required_candidates[]`. For every newly relevant candidate, state whether equivalent qualification is required and whether that qualification can use already-authorized/already-available artifacts. For candidates requiring new access, pin exact revisions/files/hashes where available, network hosts, expected bytes, rights, executor, retention, cleanup and USD ceiling. If no newly relevant candidate survives far enough to require qualification, record `NO_NEW_CANDIDATES_REQUIRING_QUALIFICATION`.  
  Outputs: `artifacts/manifests/B010-new-candidate-weight-access.json`, `evidence/mstr-000b/B010-weight-access-preflight.md`.
  Canonical implementation: PR #65 / final head `2047a3aa8b7063736a490d00d1fe10709aba23e2` / merge `215d52f4de772639c5e64193ff48deaafb6eb2d7`.

- [ ] **B011 EXPLICIT NEW WEIGHT ACCESS GATE — acquire/verify only founder-authorized B010 access-required candidates.**  
  Prerequisites: B002 `COMPLETE_CANONICAL`, exact-main `eligible=true`, B010 canonical, and separate exact founder authorization when `new_weight_access_required_candidates[]` is non-empty. Use approved ephemeral runners; founder Mac and Git receive no binaries. Verify exact integrity and emit T024-compatible manifests. If the access-required list is empty, close B011 as `NOT_REQUIRED_NO_NEW_ACCESS` with evidence and perform no model-weight access. This status says nothing about whether B012 qualification is still required.  
  Outputs: `artifacts/manifests/B011-acquired-candidates.json` or explicit no-access decision artifact, runner evidence where executed, `evidence/mstr-000b/B011-acquisition.md`.

- [ ] **B012 Run equivalent Q4/runtime/resource/raw-code qualification for every B010 qualification candidate.**  
  Prerequisites: B002 `COMPLETE_CANONICAL`, exact-main `eligible=true`, B010 canonical, and B011 complete or `NOT_REQUIRED_NO_NEW_ACCESS`. A candidate that needs no new acquisition but has already-authorized/already-available artifacts MUST still receive equivalent qualification. B012 may close `NOT_REQUIRED_NO_NEW_CANDIDATES` only when B010 explicitly records `qualification_candidates=[]` / `NO_NEW_CANDIDATES_REQUIRING_QUALIFICATION`. Reuse canonical T029-T034 protocols where compatible; if superseded, record migration.  
  Outputs: `artifacts/results/backbone/B012/` and candidate Q4 manifests where applicable, explicit N/A evidence only for the true empty-candidate case, `evidence/mstr-000b/B012-new-candidate-qualification.md`.

- [ ] **B013 Freeze stable product-aligned candidate pool for A019/tournament convergence.**  
  Prerequisite: B002 `COMPLETE_CANONICAL` with exact-main `eligible=true`; the existing candidate set has completed T034 or a canonical equivalent hard-gate qualification; every B010 qualification candidate has completed B012 or been explicitly rejected before admission. Require comparable hard-gate evidence or explicit rejection reasons. Do not select the final backbone merely from this task.  
  Outputs: `artifacts/decisions/B013-stable-candidate-pool.json`, `evidence/mstr-000b/B013-candidate-pool.md`.

**Checkpoint B:** candidate pool reflects MSTR's code-specialized mission and has equivalent deployment evidence.

---

# Phase D — Data Constitution and Software-Evolution Foundation

- [x] **B014 Freeze `MSTR-DATA-CONSTITUTION-v0`.**
  - Canonical implementation: PR #67 / final head `70d601c4fb1c0603b6e757969a3a97b8c77744d8` / merge `f6925f3e0d8378fedd6ec1d3aed30b725115e07e`
  Define allowed/prohibited source classes, software-role taxonomy, provenance/rights, contamination, dedup, benchmark exclusion, synthetic/student/teacher policy, difficulty policy, verifier-health thresholds, stage admission rules, and private-user-data default rejection.  
  Outputs: `docs/data/MSTR_DATA_CONSTITUTION.md`, schema/fixtures, `evidence/mstr-000b/B014-data-constitution.md`.

- [x] **B015 Freeze programming-language/tooling target policy.**
  Use target-user/product evidence, not marketing breadth. Define core/secondary/long-tail language tiers and replay minimums; include build/config/shell/SQL where relevant.  
  Outputs: `artifacts/decisions/B015-language-target-policy.json`, `evidence/mstr-000b/B015-language-mix.md`.
  Canonical implementation: PR #69 / final head `e6191fefc9b870f3376f6faead6149841fe7dd31` / merge `5104f7ef63ba37caa518868ad89d0f78fe70641f`.

- [x] **B016 Freeze `SoftwareEvolutionRecord` contract and future-history boundary.**
  Bind base revision, direction/issue, visible context, change/test/CI/review/recovery events and final verified revision while explicitly preventing future patches/results from leaking into earlier model-visible steps.  
  Outputs: schema, fixtures, `evidence/mstr-000b/B016-software-evolution.md`.
  Canonical implementation: PR #71 / final head `33eb53b7ae4c2fd43d639af9c6e67512fb883423` / merge `5ed34690dbc71db2359c927e96b511c32dffb2c4`.

- [x] **B017 Build a tiny fixture-only software-evolution extractor/projection proof.**
  No large corpus ingestion. Demonstrate deterministic projection of localization/edit/review-repair examples from synthetic or already-repository-owned fixtures.  
  Outputs: implementation/tests/fixtures, `evidence/mstr-000b/B017-evolution-fixture-pilot.md`.
  Canonical implementation: PR #73 / final head `6bab90d46fca0323fe9c1d66f37a69e8b13d8ae3` / merge `79e1b5ceca4ed39e10f53b0f85f93ffb7b02208c`.

- [x] **B018 Freeze execution-filtered student self-alignment contract.**
  Student-generated tasks/solutions/tests require seed and per-artifact provenance, compatible rights, sandbox execution, independent verifier health, contamination checks and difficulty records before training admission. Missing/unresolved provenance or rights fails closed.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B018-self-alignment-contract.md`.
  Canonical implementation: PR #76 / final head `23c83ebae95ca3f0d893840e9d994b33712f124f` / merge `7e4996e92128e4e02ec6dbcf6ed29eed2b753838`.

- [x] **B019 Freeze bounded teacher-rescue policy.**
  Teachers are optional frontier-rescue/reference sources. Record teacher identity/terms/cost plus concrete-output provenance, output-rights decisions and contamination status; independently execute/verify outputs; reject incompatible or unresolved rights. Paid/API teacher use is not authorized here.  
  Outputs: `docs/data/TEACHER_RESCUE_POLICY.md`, schema/fixtures, `evidence/mstr-000b/B019-teacher-policy.md`.
  Canonical implementation: PR #78 / final head `25907c32fb60e83a6b171192e8c12c8092bc9f5e` / merge `ac68e2ff9de9962807ab32ce983b2e808bf4fab9`.

- [x] **B020 Freeze checkpoint-relative difficulty calibration contract.**
  Define exact student/harness/sampling identity and classes `TOO_EASY`, `LEARNABLE_FRONTIER`, `HARD_FRONTIER`, `CURRENTLY_UNPRODUCTIVE`, `INVALID`.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B020-difficulty-contract.md`.
  Canonical implementation: PR #81 / final head `189509470eae10f1080938b0b2b873f375842f35` / merge `f5a4892bff6bc20e376efcaa8f554c15ac88bca8`.

- [x] **B021 Implement fixture-only frontier sampler/calibrator.**
  Demonstrate refreshable task difficulty and sampling decisions without training or large data. Preserve easier replay/regression anchors and harder frontier cells.  
  Outputs: `src/mstr_qualify/curriculum/`, tests, `evidence/mstr-000b/B021-frontier-sampler.md`.
  Canonical implementation: PR #83 / final head `6211a8f2ccf2613f2e988ce230c7d432877b1aff` / merge `613449e0f1b23eaef7dcb702ba2636a157816d26`.

**Checkpoint D:** downstream MSTR-001 can build a legally traceable software-evolution/data curriculum rather than an undifferentiated code corpus.

---

# Phase V — Verifier Health, Test Generation, and Training Signal Integrity

- [x] **B022 Freeze `VerifierHealthRecord` contract.**
  Require evaluator hashes, protected paths, oracle/no-op/known-bad behavior where applicable, mutation/shortcut tests, generated-test independence, leakage/disagreement signals, and health class.  
  Outputs: schema/fixtures, `evidence/mstr-000b/B022-verifier-health.md`.
  Canonical implementation: PR #85 / final head `ab3330afdef9c9329b1d2bb2a7e5aab09064f62b` / merge `97bf66a98bad51ff0d574d90a04fa47b802708ee`.

- [ ] **B023 Implement verifier-health evaluator on controlled fixtures.**  
  Exact prerequisites: A006 protected finalizer/verifier boundary `COMPLETE_CANONICAL`, A014 verifier runner/reward-shortcut battery `COMPLETE_CANONICAL`, B002 `COMPLETE_CANONICAL`, B022 `COMPLETE_CANONICAL`, and exact-main `eligible=true`. Prove `HEALTHY`, `PARTIAL`, `DISAGREEMENT`, `BROKEN`, `LEAKED`, and `TAMPERED` classifications; integrate with training trajectory admission as a blocking field, amending earlier trajectory plumbing if necessary rather than creating a parallel authority surface.  
  Outputs: verifier-health module/tests, `evidence/mstr-000b/B023-verifier-health-implementation.md`.

- [ ] **B024 Freeze test-generation curriculum and acceptance semantics.**  
  Prerequisite: B023 `COMPLETE_CANONICAL`. Include per-example provenance/rights/contamination requirements, reproduce-before-fix, targeted regression, boundary/error, property/metamorphic where appropriate, pre-fix fail/post-fix pass, and rejection of answer-encoding/test weakening.  
  Outputs: `docs/data/TEST_GENERATION_CURRICULUM.md`, fixtures, `evidence/mstr-000b/B024-test-curriculum.md`.

- [ ] **B025 Freeze greenfield/feature/synthesis curriculum.**  
  Define G0 function, G1 module+tests, G2 component/file, G3 multi-file feature, G4 bounded program, G5 multi-round evolution. Include feature-tree/semantic synthesis as experimental generator with independent verification.  
  Outputs: `docs/data/GREENFIELD_FEATURE_CURRICULUM.md`, task manifest schema/fixtures, `evidence/mstr-000b/B025-greenfield-curriculum.md`.

**Checkpoint V:** clean positive training signal requires healthy verification; building and testing are both explicit learned skills.

---

# Phase R — Research Efficiency, Q4, and Long-Horizon Quality

- [ ] **B026 Freeze multi-fidelity MSTR Research Ladder v0.**  
  L0 contract/smoke -> L1 code/FIM/edit/tool -> L2 executable repo -> L3 Direction-to-Done/feature/program -> L4 Q4 universal-laptop. Define per-level promotion/hard-reject criteria and exact material-result identity requirements.  
  Outputs: contract/config, `evidence/mstr-000b/B026-research-ladder.md`.

- [ ] **B027 Qualify the research ladder with one non-weight-changing campaign.**  
  Use a bounded harness/config experiment. Demonstrate early discard, promotion, immutable evaluator authority, complete `MaterialResultIdentity` records and full ledger.  
  Outputs: `artifacts/results/research/B027/`, `evidence/mstr-000b/B027-ladder-pilot.md`.

- [ ] **B028 Freeze Q4-in-the-loop promotion contract and training-method tournament preflight.**  
  Require release-relevant Q4 regression after every material weight-changing stage and a fail-closed `Q4PromotionRecord` before a checkpoint may become the parent of another material stage. Supported comparisons MUST include 16-bit LoRA, 16-bit LoRA+rsLoRA, 4-bit QLoRA, and 4-bit QLoRA+rsLoRA where current backbone/framework support permits; every unsupported arm requires an exact recorded reason. Revalidate backbone/Unsloth/Transformers guidance immediately before execution.  
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
  Exact prerequisites: A019 `COMPLETE_CANONICAL`, A020 `COMPLETE_CANONICAL`, B002/B003/B004 `COMPLETE_CANONICAL`, B015/B017/B019/B021/B023/B024/B025/B027/B028/B029/B030 `COMPLETE_CANONICAL`, plus exact-main `eligible=true`. A019 itself requires A001-A018 complete, B013 stable candidate pool, B023 verifier-health implementation, and B026 research ladder; A020 consumes B026. Legacy candidate/tournament/data tasks must be marked retained, superseded, or amended; no incompatible duplicate remains.  
  Outputs: task supersession/dependency map, canonical task updates, `evidence/mstr-000b/B031-tournament-reconciliation.md`.

- [ ] **B032 Amend MSTR-001/MSTR-002/MSTR-003 entry requirements.**  
  Prerequisite: B031 `COMPLETE_CANONICAL`. MSTR-001 consumes Data Constitution, language mix, software evolution, frontier curriculum and Q4 promotion. MSTR-002 consumes self-alignment, teacher policy, verifier health, test generation, greenfield/feature and same-loop trajectories. MSTR-003 consumes frontier curriculum, admitted environments, verifier health and multi-fidelity RL promotion.  
  Outputs: roadmap/training strategy/preplan amendments, `evidence/mstr-000b/B032-downstream-contracts.md`.

- [ ] **B033 Independent consistency/red-team review.**  
  Prerequisite: B032 `COMPLETE_CANONICAL`. Review candidate fairness, data leakage, rights, reward hacking, task-gate bypass, teacher contamination, tokenizer comparability, Q4 promotion, WePLD attribution, and 8GB product preservation. Resolve all material findings.  
  Outputs: `evidence/mstr-000b/B033-independent-review.md`.

- [ ] **B034 Close MSTR-000B canonical.**  
  Exact prerequisite: **every B001-B033 task is `COMPLETE_CANONICAL` or, only where the task contract explicitly permits it, a canonical `NOT_REQUIRED` terminal state with evidence**. Before closeout, machine validation MUST verify every predecessor state and every task's declared evidence artifact path, including governance B001-B004; backbone B005-B013; data/curriculum B014-B021; verifier/build-skill B022-B025; research/product B026-B030; and convergence B031-B033. Freeze exact contract versions, stable candidate pool state, unresolved risks, supersession map, training-readiness statement and next exact authority. This task MUST NOT authorize weight-changing training.  
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
BOOTSTRAP_MANUAL = B001 -> B002
B002_CANONICAL -> ALL_MATERIAL_B003_PLUS_EXECUTION_AND_MERGE_REQUIRE_ELIGIBLE_TRUE
B002 -> B003 -> B004

B005 -> B006 -> B007 -> B008 -> B009 -> B010
B002 + B010(non-empty access list) + SEPARATE_FOUNDER_AUTHORITY -> B011 -> B012
B002 + B010(empty access list but non-empty qualification list) -> B011(NOT_REQUIRED_NO_NEW_ACCESS) -> B012
B010(empty qualification list) -> B011(NOT_REQUIRED_NO_NEW_ACCESS) -> B012(NOT_REQUIRED_NO_NEW_CANDIDATES)
B002 + T034_OR_CANONICAL_EQUIVALENT + B012 -> B013

B014 -> B015
B014 -> B016 -> B017
B014 -> B018 -> B019
B014 -> B020 -> B021
B014 -> B022
A006 + A014 + B002 + B022 -> B023 -> B024
B014 -> B025

B022 + B024 + B025 -> B026 -> B027
B009 + B014 + B022 -> B028
B020 + MSTR-000A loop/context contracts -> B029
B024 + B025 + A019-ready harness surfaces -> B030

T034_OR_CANONICAL_EQUIVALENT
+ A001-A018
+ B013
+ B023
+ B026
-> A019
B026 + required A-loop/research contracts -> A020

A019 + A020 + B002 + B003 + B004 + B015 + B017 + B019 + B021 + B023 + B024 + B025 + B027 + B028 + B029 + B030 -> B031 -> B032 -> B033

B001-B033_COMPLETE_OR_EXPLICIT_CANONICAL_NOT_REQUIRED_WITH_EVIDENCE -> B034
B034 != TRAINING AUTHORIZATION
```
