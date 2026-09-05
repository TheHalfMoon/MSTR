# Tasks: MSTR-000 Universal Laptop Qualification + Interaction Contract

**Strict checklist format:** `- [ ] T### [P?] [US#?] Action → exact output path(s)`.

- Setup and Foundational tasks intentionally have **no** user-story label.
- User-story phases use `[US1]` through `[US8]`.
- `[P]` means safe to run in parallel only after the phase prerequisites are satisfied and only when the tasks do not mutate the same output.
- T000–T002 are canonical completed historical tasks; the executable Spec Kit queue continues at T003.
- Earlier incomplete/noncanonical T003+ draft IDs are superseded by this graph.

A checkbox becomes complete only when the stated output exists, required tests/evidence pass, identity fields are complete, external effects stayed within exact authority, and the result is canonical through repository governance.

## Phase 0 — Canonical Product Foundation — COMPLETE

- [x] T000 [US1] Define universal-laptop matrix → `evidence/T000-universal-laptop-hardware-matrix.md`.
- [x] T001 [US1] Freeze `MSTR-MEASURE-v0` → `evidence/T001-measurement-procedures.md`.
- [x] T002 [US1] Freeze `MSTR-DIST-v0` → `evidence/T002-distribution-install-privacy-contract.md`.

---

## Phase 1 — Setup

**Purpose:** create the implementation skeleton only. No model weights, candidate execution, or external service access.

- [x] T003 Bootstrap package/test/config/evidence layout → `pyproject.toml`, `.gitignore`, `src/mstr_qualify/__init__.py`, `src/mstr_qualify/__main__.py`, `tests/`, `configs/`, `schemas/`, `artifacts/{candidates,manifests,results,decisions}/`. Evidence: `evidence/T003-qualification-harness-bootstrap.md`.

**Checkpoint:** repository has an installable empty qualification package and ignored locations for external/large artifacts.

---

## Phase 2 — Foundational Infrastructure — COMPLETE

**Prerequisite:** T003.  
**Independent test:** from a clean Python 3.11+ environment with no model weights and external network blocked, `python -m mstr_qualify validate` validates schemas/fixtures and `pytest -q` passes.

- [x] T004 [P] Implement strict schema loading/validation and copy design schemas into runtime schema directory → `src/mstr_qualify/schemas.py`, `schemas/*.schema.json`, `tests/contract/test_schemas.py`, `tests/fixtures/schemas/{valid,invalid}/`. Evidence: `evidence/T004-strict-schema-validation.md`.
- [x] T005 [P] Implement typed qualification errors plus stable ID/SHA-256 helpers → `src/mstr_qualify/errors.py`, `src/mstr_qualify/ids.py`, `tests/unit/test_errors.py`, `tests/unit/test_ids.py`. Evidence: `evidence/T005-errors-ids.md`.
- [x] T006 Implement fail-closed component/backbone rights evaluation → `src/mstr_qualify/rights.py`, `tests/unit/test_rights.py`, `tests/fixtures/rights/`, `evidence/T006-primary-backbone-rights-gate.md`. Evidence: `evidence/T006-primary-backbone-rights-gate.md`.
- [x] T007 Implement immutable/canonical evidence serialization and supersession semantics → `src/mstr_qualify/evidence.py`, `tests/unit/test_evidence.py`, `tests/contract/test_evidence_roundtrip.py`, `tests/fixtures/evidence/`. Evidence: `evidence/T007-immutable-evidence-serialization.md`.
- [x] T008 Implement task/benchmark/candidate manifest loaders and validation → `src/mstr_qualify/manifests.py`, `tests/unit/test_manifests.py`, `benchmarks/manifests/README.md`, `configs/candidates/README.md`. Evidence: `evidence/T008-manifest-loaders.md`.
- [x] T009 Implement score-surface/report comparability rules that reject mismatched protocol/cache/hardware/task conditions → `src/mstr_qualify/reporting.py`, `tests/unit/test_reporting.py`, `tests/fixtures/reporting/`. Evidence: `evidence/T009-comparability.md`.
- [x] T010 Implement dependency-light offline CLI commands `validate`, `rights`, `candidate static`, `manifest validate` → `src/mstr_qualify/cli.py`, `tests/integration/test_cli_offline.py`.
- [x] T011 Freeze harness quality gates and baseline test evidence → `evidence/T011-harness-foundation-qualification.md`, `configs/quality.toml`, plus passing `tests/`; add CI workflow only if explicitly chosen and document absence otherwise.

**Checkpoint:** foundational harness ready — REACHED (T003–T011 canonical). User-story work can begin according to dependencies below.

---

## Phase 3 — User Story 2: Reproducible Static Candidate Admission (P1) — COMPLETE

**Goal:** identify compact candidate foundations that are legally/distributably/technically eligible for later local qualification without downloading weights.  
**Prerequisite:** T003–T011 canonical.  
**Independent test:** every candidate produces a schema-valid record pinned to an immutable upstream revision; ambiguous/incompatible rights fail closed; no weight files are accessed.

- [x] T012 [P] [US2] Qualify Qwen3.5-2B → `artifacts/candidates/qwen3.5-2b.json`, `evidence/candidates/T012-qwen3.5-2b.md`.
- [x] T013 [P] [US2] Qualify Qwen3.5-4B → `artifacts/candidates/qwen3.5-4b.json`, `evidence/candidates/T013-qwen3.5-4b.md`.
- [x] T014 [P] [US2] Qualify Ministral-3-3B → `artifacts/candidates/ministral-3-3b.json`, `evidence/candidates/T014-ministral-3-3b.md`.
- [x] T015 [P] [US2] Qualify Qwen3-4B control → `artifacts/candidates/qwen3-4b.json`, `evidence/candidates/T015-qwen3-4b.md`.
- [x] T016 [P] [US2] Qualify Granite-4.1-3B including FIM/component rights → `artifacts/candidates/granite-4.1-3b.json`, `evidence/candidates/T016-granite-4.1-3b.md`.
- [x] T017 [P] [US2] Qualify SmolLM3-3B → `artifacts/candidates/smollm3-3b.json`, `evidence/candidates/T017-smollm3-3b.md`.
- [x] T018 [P] [US2] Qualify Qwen2.5-Coder-1.5B lower-bound control → `artifacts/candidates/qwen2.5-coder-1.5b.json`, `evidence/candidates/T018-qwen2.5-coder-1.5b.md`.
- [x] T019 [P] [US2] Record Qwen2.5-Coder-3B as reference-only/ineligible unless exact current terms changed → `artifacts/candidates/qwen2.5-coder-3b-reference.json`, `evidence/candidates/T019-qwen2.5-coder-3b.md`.
- [x] T020 [P] [US2] Record useful compact post-trained comparison points without treating them as foundation winners → `artifacts/candidates/comparisons/*.json`, `evidence/candidates/T020-posttrained-comparisons.md`.
- [x] T021 [US2] Re-scan current approximately 1B–5B open foundation landscape immediately before first weight-access planning → `evidence/T021-landscape-rescan.md`; any new candidate gets `artifacts/candidates/<id>.json` under the same schema.
- [x] T022 [US2] Select bounded weight-eligible candidate set without final backbone admission → `artifacts/decisions/T022-static-candidate-admission.json`, `evidence/T022-static-candidate-admission.md`.

**Checkpoint:** US2 independently demonstrable; weight-eligible set exists without any model acquisition — **REACHED (T012–T022 canonical)**.

---

## Phase 4 — User Story 1: Universal-Laptop Local Artifact Qualification (P1)

**Goal:** prove which admitted candidates actually fit and function under the universal-laptop product envelope.  
**Prerequisite:** T022 canonical.  
**Authority:** no candidate weight access before T028.  
**Independent test:** every admitted candidate has pinned artifact/runtime identity and U1 8GB/CPU/8K evidence or an explicit rejection reason.

- [x] T023 [P] [US1] Define runtime/platform adapter protocols with dummy implementations → `src/mstr_qualify/runtimes/base.py`, `src/mstr_qualify/measurement/platform.py`, `tests/unit/test_runtime_protocol.py`, `tests/unit/test_platform_sampler.py`.
- [x] T024 [P] [US1] Implement artifact manifest/hash verification → `src/mstr_qualify/artifacts.py`, `tests/unit/test_artifacts.py`, `tests/fixtures/artifacts/`.
- [x] T025 [P] [US1] Implement Windows/Linux/macOS memory/paging samplers and unavailable-metric semantics → `src/mstr_qualify/measurement/{windows,linux,macos}.py`, `tests/unit/measurement/`.
- [x] T026 [P] [US1] Implement `MSTR-MEASURE-v0` monotonic event/TTFI/TTFA/TTFCE/TTVC logic → `src/mstr_qualify/measurement/protocol.py`, `tests/unit/measurement/test_protocol.py`.
- [x] T027 [US1] Freeze exact weight-access/acquisition manifest including candidates/revisions, source URLs, expected integrity checks, storage ceiling, runtime/quantizer, network behavior, cost ceiling, retention/cleanup → `artifacts/manifests/T027-weight-access.json`, `specs/000-universal-laptop-interaction-contract/evidence/T027-weight-access-preflight.md`.
- [x] T028 [US1] **EXPLICIT WEIGHT ACCESS GATE:** only after separate exact authorization, acquire T027-listed candidate artifacts, verify source/integrity, keep binaries outside Git → `artifacts/manifests/T028-acquired-artifacts.json`, `evidence/T028-weight-acquisition.md`; downloaded files remain ignored/external.
- [x] T029 [US1] Build/obtain quality-oriented and compatibility-oriented Q4 profiles where practical, with exact quantizer/recipe/hash → `artifacts/manifests/quantization/*.json`, `evidence/T029-q4-profiles.md`.
- [ ] T030 [US1] Implement/qualify portable CPU runtime adapters; acceleration is separate bonus data → `src/mstr_qualify/runtimes/<runtime>.py`, `configs/runtimes/*.json`, `tests/integration/test_runtime_adapters.py`, `evidence/T030-runtime-adapters.md`.
- [ ] T031 [US1] Measure 4K/8K/16K artifact/load/memory/paging/prefill/decode behavior → `artifacts/results/local/T031/*.jsonl`, `evidence/T031-local-memory-throughput.md`.
- [ ] T032 [US1] Measure 10-minute sustained CPU behavior and reference-editor responsiveness on required lanes → `artifacts/results/local/T032/*.jsonl`, `evidence/T032-sustained-responsiveness.md`.
- [ ] T033 [US1] Measure Q4 regressions in raw coding/FIM/multilingual/schema/tool/edit primitives → `artifacts/results/local/T033/*.jsonl`, `evidence/T033-q4-regressions.md`.
- [ ] T034 [US1] Reject rights/U1/offline/size/runtime failures and freeze local-qualified set → `artifacts/decisions/T034-local-artifact-admission.json`, `evidence/T034-local-artifact-admission.md`.

**Checkpoint:** US1 qualification outcome independently demonstrable for every locally admitted candidate.

---

## Mandatory Interposition Gate — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Entry prerequisite:** T034 `COMPLETE_CANONICAL`.  
**Package:** `specs/001-agent-harness-verified-loop-foundation/`.  
**Authority:** this gate does not authorize weight-changing training.

After T034, **every legacy MSTR-000 task T035–T090 is blocked until MSTR-000A is `COMPLETE_CANONICAL` and its A021/A022 reconciliation has produced the exact ownership/supersession map for the legacy interaction, tournament, environment, verifier, and training-preflight tasks below.**

```text
T034_COMPLETE_CANONICAL
-> MSTR_000A_A001..A024
-> MSTR_000A_COMPLETE_CANONICAL
-> LEGACY_TASK_RECONCILIATION_MAP_CANONICAL
-> resume only the legacy tasks explicitly retained by that map
```

No lower phase prerequisite in this file may be interpreted as bypassing this gate. In particular, T035–T052 may not execute under their historical ordering before MSTR-000A closeout, and T053 remains separately founder-authorized even after MSTR-000A closes.

This interposition also prevents duplicate execution of T065–T072: MSTR-000A A022 must classify those tasks as consumed, superseded, or expansion/hardening work before any of them resumes.

---

## Phase 5 — User Story 3: Stable Interaction + Deterministic Edit Contract (P1)

**Goal:** freeze a trainable/servable prompt-tool-edit contract before material post-training.  
**Prerequisite:** T034 + MSTR-000A `COMPLETE_CANONICAL` + canonical A021/A022 reconciliation map retaining the task.  
**Independent test:** canonical fixtures are deterministic; malformed calls fail explicitly; stale hashes cannot overwrite; Interaction v0 validates against schema.

- [ ] T035 [P] [US3] Implement prompt/stable-prefix representation and canonical hashing → `src/mstr_qualify/interaction/prompt.py`, `configs/interaction/prompt-arms/*.json`, `tests/contract/test_prompt_prefix.py`.
- [ ] T036 [P] [US3] Implement candidate tool grammars/parsers with malformed/schema failure semantics → `src/mstr_qualify/interaction/tools.py`, `configs/interaction/tool-arms/*.json`, `tests/unit/interaction/test_tools.py`.
- [ ] T037 [P] [US3] Implement deterministic tool-result serialization → `src/mstr_qualify/interaction/serialization.py`, `tests/contract/test_tool_serialization.py`, `tests/fixtures/interaction/tool-results/`.
- [ ] T038 [P] [US3] Implement edit-format tournament adapters for whole-file/unified-diff/search-replace/anchored patch → `src/mstr_qualify/interaction/edits.py`, `configs/interaction/edit-arms/*.json`, `tests/unit/interaction/test_edits.py`.
- [ ] T039 [US3] Implement deterministic file-hash/version stale-write transactions and conflict rejection → `src/mstr_qualify/interaction/apply.py`, `tests/security/test_stale_write.py`, `tests/integration/test_apply_transactions.py`.
- [ ] T040 [P] [US3] Define model-visible network/privacy/sandbox/task-state/context-order semantics → `configs/interaction/runtime-semantics.json`, `tests/contract/test_runtime_semantics.py`.
- [ ] T041 [US3] Run prompt/cache/tool/result/edit bake-off on local-qualified candidates → `artifacts/results/interaction/T041/*.jsonl`, `evidence/T041-interaction-bakeoff.md`.
- [ ] T042 [US3] Freeze Interaction Contract v0 candidate and fixtures → `configs/interaction/mstr-interaction-v0.json`, `artifacts/decisions/T042-interaction-v0.json`, `evidence/T042-interaction-v0.md`.

**Checkpoint:** US3 independently passes contract/serialization/stale-write tests.

---

## Phase 6 — User Story 4: Verified Candidate Selection + Equivalent Bounded Adaptation (P1)

**Goal:** select the strongest local foundation using comparable verified evidence rather than one leaderboard.  
**Prerequisite:** MSTR-000A `COMPLETE_CANONICAL`, retained task ownership from A021/A022, and T042 where retained.  
**Independent test:** regenerate raw/neutral/full-system scorecards from exact evidence; failed seeds remain visible; finalists receive equivalent bounded adaptation.

- [ ] T043 [US4] Freeze tournament task/seed/sampling/verifier/timeout/cache manifest before scoring → `benchmarks/manifests/T043-candidate-tournament.json`, `evidence/T043-tournament-freeze.md`.
- [ ] T044 [P] [US4] Run raw coding/FIM/multilingual surface → `artifacts/results/tournament/T044-raw/*.jsonl`, `evidence/T044-raw-results.md`.
- [ ] T045 [P] [US4] Run tool/edit reliability under Interaction v0 → `artifacts/results/tournament/T045-tool-edit/*.jsonl`, `evidence/T045-tool-edit-results.md`.
- [ ] T046 [US4] Implement/use neutral minimal repository harness and run localization/repair tasks → `src/mstr_qualify/harness/neutral.py`, `tests/integration/test_neutral_harness.py`, `artifacts/results/tournament/T046-repo/*.jsonl`, `evidence/T046-neutral-repo-results.md`.
- [ ] T047 [US4] Compute U1 solve rate, TTVC, completions/hour, utility-per-GB with failure-inclusive reporting → `artifacts/results/tournament/T047-utility.json`, `evidence/T047-laptop-utility.md`.
- [ ] T048 [US4] Define optional external competitive TTVC protocol without executing paid systems → `benchmarks/manifests/T048-competitive-ttvc.json`, `evidence/T048-competitive-protocol.md`.
- [ ] T049 [US4] Generate pre-adaptation raw/neutral/full scorecard → `artifacts/decisions/T049-pre-adaptation-scorecard.json`, `evidence/T049-pre-adaptation-scorecard.md`.
- [ ] T050 [US4] Select finalists for equivalent bounded adaptation → `artifacts/decisions/T050-finalists.json`, `evidence/T050-finalist-selection.md`.
- [ ] T051 [US4] Freeze small decontaminated execution-grounded adaptation set manifest with FIM/failure/recovery/general-reasoning replay → `artifacts/manifests/T051-micro-adaptation-data.json`, `evidence/T051-micro-adaptation-data.md`; training data binaries remain external/ignored.
- [ ] T052 [US4] Freeze identical adaptation recipe: token/update budget, seeds, hardware, optimizer/config, cost ceiling, stopping/regression rules → `artifacts/manifests/T052-micro-adaptation-recipe.json`, `evidence/T052-micro-adaptation-preflight.md`.
- [ ] T053 [US4] **EXPLICIT BOUNDED TRAINING GATE:** only after separate exact authorization, run T052 for finalists; no long training → `artifacts/results/adaptation/T053/*.json`, `evidence/T053-micro-adaptation-execution.md`; resulting model binaries stay outside Git.
- [ ] T054 [US4] Re-run local/quality tournament on adapted finalists and compare regressions/gains → `artifacts/results/adaptation/T054/*.jsonl`, `evidence/T054-post-adaptation-results.md`.
- [ ] T055 [US4] Freeze top-one backbone or top-two controlled MSTR-001 mid-training pilot set → `artifacts/decisions/T055-backbone-decision.json`, `evidence/T055-backbone-decision.md`; this is not long-training authority.

**Checkpoint:** US4 independently produces the evidence-backed top-one/top-two decision.

---

## Phase 7 — User Story 5: Smallest Useful Context Engine (P2)

**Goal:** select the smallest repository-context system that earns its resource cost.  
**Prerequisite:** MSTR-000A `COMPLETE_CANONICAL` and its reconciliation map; final quality-facing comparison uses the retained frozen interaction/task surface.  
**Independent test:** each arm reports localization/solve-rate/tokens/TTVC/RAM/disk/build/update under a common manifest; default is the smallest Pareto-efficient arm.

- [ ] T056 [US5] Implement `ContextProvider` and exact/ripgrep baseline → `src/mstr_qualify/context/base.py`, `src/mstr_qualify/context/exact.py`, `tests/unit/context/test_exact.py`, `configs/context/exact.json`.
- [ ] T057 [US5] Implement Tree-sitter/RepoMap-style symbols and resource metrics → `src/mstr_qualify/context/symbols.py`, `tests/unit/context/test_symbols.py`, `configs/context/symbols.json`.
- [ ] T058 [US5] Implement incremental sparse index with startup/update/RAM/disk metrics → `src/mstr_qualify/context/sparse.py`, `tests/unit/context/test_sparse.py`, `configs/context/sparse.json`.
- [ ] T059 [P] [US5] Evaluate embeddings/reranker experimental arm without making it mandatory → `src/mstr_qualify/context/embeddings.py` or isolated adapter config, `configs/context/embeddings.json`, `artifacts/results/context/T059/*.jsonl`.
- [ ] T060 [P] [US5] Evaluate SCIP experimental arm → `src/mstr_qualify/context/scip.py` or isolated adapter config, `configs/context/scip.json`, `artifacts/results/context/T060/*.jsonl`.
- [ ] T061 [P] [US5] Evaluate Graphify experimental arm in isolated optional integration → `configs/context/graphify.json`, `artifacts/results/context/T061/*.jsonl`, `evidence/context/T061-graphify.md`.
- [ ] T062 [P] [US5] Evaluate Code-Graph-RAG experimental arm in isolated optional integration → `configs/context/code-graph-rag.json`, `artifacts/results/context/T062/*.jsonl`, `evidence/context/T062-code-graph-rag.md`.
- [ ] T063 [US5] Generate common Context Pareto report → `artifacts/results/context/T063-pareto.json`, `evidence/T063-context-pareto.md`.
- [ ] T064 [US5] Freeze default minimal Context Engine plus RAM/disk budget → `artifacts/decisions/T064-context-engine.json`, `evidence/T064-context-engine-decision.md`.

**Checkpoint:** US5 independently yields one default context decision or an explicit no-extra-context decision.

---

## Phase 8 — User Story 6: Verifiable Environment / Verifier Factory MVP (P2)

**Goal:** preserve the legacy environment/verifier expansion tasks without duplicating the MSTR-000A pre-training MVP.  
**Prerequisite:** MSTR-000A `COMPLETE_CANONICAL` + canonical A022 mapping that explicitly retains each task below as expansion/hardening work.  
**Independent test:** a retained fixture task passes its known-good solution, fails no-op/unsolved, rejects canonical reward shortcuts, resets reproducibly, and exposes reset/storage/CPU cost.

- [ ] T065 [P] [US6] Implement `EnvironmentTask`/`VerifierDefinition` records and validation → `src/mstr_qualify/environment/models.py`, `src/mstr_qualify/verifier/models.py`, `schemas/environment-task.schema.json`, `schemas/verifier.schema.json`, `tests/contract/test_environment_schemas.py`.
- [ ] T066 [P] [US6] Implement deterministic workspace reset/snapshot abstraction with clean-hash verification → `src/mstr_qualify/environment/workspace.py`, `tests/integration/test_workspace_reset.py`.
- [ ] T067 [US6] Implement verifier runner with protected evaluator paths/structured results → `src/mstr_qualify/verifier/runner.py`, `tests/integration/test_verifier_runner.py`.
- [ ] T068 [US6] Implement environment admission checks: oracle/reference pass, no-op fail, unsolved/broken fail → `src/mstr_qualify/environment/admission.py`, `tests/integration/test_environment_admission.py`, `benchmarks/fixtures/environment/`.
- [ ] T069 [US6] Implement reward-shortcut battery: test deletion, assertion weakening, hardcoding, evaluator tamper, spoofing, cache/deleted-solution recovery → `src/mstr_qualify/verifier/shortcuts.py`, `tests/security/test_reward_shortcuts.py`.
- [ ] T070 [US6] Implement future-history/public-solution/network leakage controls → `src/mstr_qualify/environment/leakage.py`, `tests/security/test_environment_leakage.py`.
- [ ] T071 [US6] Measure task yield/reset/startup/CPU/storage/failure/reproducibility on MVP fixtures → `artifacts/results/environment/T071.json`, `evidence/T071-environment-throughput.md`.
- [ ] T072 [US6] Freeze downstream MSTR-003 environment/verifier contract requirements; do not imply MSTR-003 execution authority → `artifacts/decisions/T072-environment-requirements.json`, `evidence/T072-environment-requirements.md`.

**Checkpoint:** US6 independently proves environment/verifier expansion/hardening requirements for the later RL workstream without duplicating MSTR-000A.

---

## Phase 9 — User Story 7: Security, Privacy, Provenance, and Evaluation Integrity (P2)

**Goal:** make the entire qualification chain auditable and fail closed against malicious repository input, leakage, and incompatible provenance.  
**Prerequisite:** MSTR-000A `COMPLETE_CANONICAL` + canonical reconciliation map retaining the task.  
**Independent test:** malicious repository fixtures cannot elevate instructions, escape workspace scope, exfiltrate secrets/network by default, or bypass benchmark leakage/provenance audit rules.

- [ ] T073 [P] [US7] Define repository-content authority/trust model and prompt-injection fixtures → `docs/security/REPOSITORY_TRUST_MODEL.md`, `tests/security/fixtures/prompt_injection/`, `tests/security/test_prompt_injection.py`.
- [ ] T074 [P] [US7] Implement workspace traversal, secret handling, network/telemetry default-off tests → `tests/security/test_workspace_scope.py`, `tests/security/test_secrets.py`, `tests/security/test_network_policy.py`.
- [ ] T075 [P] [US7] Implement provenance record schema/model and lineage validation → `schemas/provenance-record.schema.json`, `src/mstr_qualify/provenance.py`, `tests/contract/test_provenance.py`.
- [ ] T076 [US7] Define exact/fuzzy/AST/identity benchmark-exclusion fingerprinting and owner opt-out design → `docs/data/DECONTAMINATION_AND_OPTOUT.md`, `src/mstr_qualify/decontamination.py`, `tests/unit/test_decontamination.py`.
- [ ] T077 [P] [US7] Implement teacher/API-output provenance and terms gate → `src/mstr_qualify/teacher_rights.py`, `tests/unit/test_teacher_rights.py`, `docs/data/TEACHER_OUTPUT_POLICY.md`.
- [ ] T078 [US7] Implement runtime evaluation leakage fixtures for network/future-history/cache/public-solution paths → `tests/security/fixtures/leakage/`, `tests/security/test_runtime_leakage.py`.
- [ ] T079 [US7] Freeze private/fresh MSTR Gauntlet construction/access contract without publishing hidden tasks → `benchmarks/private/README.md`, `benchmarks/private/manifest-template.json`, `docs/evaluation/GAUNTLET_POLICY.md`.
- [ ] T080 [US7] Implement evidence-audit command traversing report → run → task → artifact/runtime/hardware/contracts/provenance → `src/mstr_qualify/audit.py`, CLI wiring in `src/mstr_qualify/cli.py`, `tests/integration/test_evidence_audit.py`.
- [ ] T081 [US7] Produce security/provenance readiness evidence → `evidence/T081-security-provenance-readiness.md`.

**Checkpoint:** US7 independently yields an auditable, privacy-preserving, leakage-aware qualification chain.

---

## Phase 10 — User Story 8: MSTR-000 Closeout and Buildable Next-Stage Decision (P1, Dependency-Final)

**Goal:** close MSTR-000 only when a new agent can execute the next workstream without reopening settled architecture questions.  
**Prerequisite:** MSTR-000A `COMPLETE_CANONICAL`, canonical task reconciliation, mandatory retained evidence from T034/T055/T064/T072/T081, and every blocking implementation-readiness item.  
**Independent test:** a new agent can reconstruct selected hardware/distribution/runtime/interaction/context/backbone decisions and exact MSTR-001 authority from repository files only.

- [ ] T082 [US8] Freeze measured universal-laptop hardware/OS floor and default context → `artifacts/decisions/T082-hardware-floor.json`, `evidence/T082-hardware-floor.md`.
- [ ] T083 [US8] Freeze closeout distribution/install/privacy contract revision → `artifacts/decisions/T083-distribution-contract.json`, `evidence/T083-distribution-contract.md`.
- [ ] T084 [US8] Freeze Interaction Contract v1 plus fixtures/migration policy → `configs/interaction/mstr-interaction-v1.json`, `artifacts/decisions/T084-interaction-v1.json`, `evidence/T084-interaction-v1.md`.
- [ ] T085 [US8] Freeze portable runtime/Q4 baseline, provenance contract, and acceptance thresholds → `artifacts/decisions/T085-runtime-q4.json`, `evidence/T085-runtime-q4.md`.
- [ ] T086 [US8] Freeze minimal Context Engine/resource budget → `artifacts/decisions/T086-context-engine.json`, `evidence/T086-context-engine.md`.
- [ ] T087 [US8] Freeze top backbone/top-two set with final raw/neutral/full scorecard → `artifacts/decisions/T087-backbone.json`, `evidence/T087-final-scorecard.md`.
- [ ] T088 [US8] Produce **bounded MSTR-001 Data Engine + Code/FIM Mid-Training** Spec Kit input package with data/compute/cost/rights/regression gates and explicit non-authorities → `artifacts/decisions/T088-mstr-001-proposal.json`, `docs/handoffs/MSTR-001-PREPLAN.md`.
- [ ] T089 [US8] Perform independent Spec Kit/evidence consistency review; resolve all CRITICAL/HIGH findings → `evidence/T089-independent-closeout-review.md`.
- [ ] T090 [US8] Record explicit founder acceptance, mark MSTR-000 CLOSED_CANONICAL, update exact next authority → `artifacts/decisions/T090-founder-closeout.json`, `docs/canonical/CURRENT_STATE.md`, `checklists/implementation-readiness.md`.

**Checkpoint:** US8 complete; MSTR-000 may become CLOSED_CANONICAL. No long training is implied unless a later exact MSTR-001 task authorizes it.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 0 canonical history
    -> Phase 1 Setup (T003)
    -> Phase 2 Foundational (T004-T011)
    -> US2 static admission (T012-T022)
    -> US1 local artifact qualification (T023-T034)
    -> MSTR-000A A001-A024 COMPLETE_CANONICAL
    -> canonical legacy-task reconciliation map
    -> retained US3 interaction work
    -> retained US4 quality/adaptation preflight
    -> separate founder gate before any T053/equivalent weight change

Legacy P2 phases US5/US6/US7 are also blocked after T034 until MSTR-000A closeout classifies their overlap/ownership. They may resume only where the A021/A022 mapping explicitly retains them.

US8 closeout waits for MSTR-000A plus every retained blocking decision.
```

### User Story Dependencies

- **US2 (P1):** first current user-story phase because US1 local qualification needs an admitted candidate set.
- **US1 (P1):** depends on US2 static admission.
- **MSTR-000A:** depends on US1/T034 and is the mandatory interposition before all legacy T035+ work.
- **US3 (P1):** depends on MSTR-000A closeout and explicit retention/reconciliation of the historical interaction tasks.
- **US4 (P1):** depends on MSTR-000A closeout plus the retained/frozen interaction contract.
- **US5 (P2):** resumes only after MSTR-000A reconciliation; final quality decision uses the frozen interaction/task surface.
- **US6 (P2):** MSTR-000A owns the pre-training MVP; legacy US6 tasks resume only as explicitly retained expansion/hardening work.
- **US7 (P2):** resumes only after MSTR-000A reconciliation so security/evaluation contracts do not diverge from the new loop/event/verifier authority.
- **US8 (P1 dependency-final):** closes only after MSTR-000A and all required retained outputs are canonical.

### Parallel Opportunities

- Setup is intentionally serial: T003.
- Foundational: T004 and T005 can run in parallel; subsequent foundation tasks use their contracts/helpers.
- US2: T012–T020 can be assigned to separate reviewers/agents after the common rights/schema gate is ready.
- US1: T023–T026 can run in parallel before the T027 acquisition preflight.
- MSTR-000A parallelism is defined only by `specs/001-agent-harness-verified-loop-foundation/tasks.md`.
- After MSTR-000A closeout, only legacy tasks explicitly retained by the reconciliation map may use their historical `[P]` opportunities.
- US8 is mostly sequential convergence and should not be parallelized in ways that race canonical decisions.
