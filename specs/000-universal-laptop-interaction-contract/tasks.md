# Tasks: MSTR-000 Universal Laptop Qualification + Interaction Contract

**Format:** `- [ ] T### [P?] [US#] Description with concrete output paths`. `[P]` means safe parallel work after prerequisites. T000–T002 are canonical complete. Earlier incomplete noncanonical T003+ draft IDs are superseded by this graph.

## Phase 1: Canonical Product Foundation — COMPLETE
- [x] T000 [US1] Universal-laptop matrix in `evidence/T000-universal-laptop-hardware-matrix.md`.
- [x] T001 [US1] `MSTR-MEASURE-v0` in `evidence/T001-measurement-procedures.md`.
- [x] T002 [US1] `MSTR-DIST-v0` in `evidence/T002-distribution-install-privacy-contract.md`.

## Phase 2: Qualification Harness Foundation
**Independent test:** offline `python -m mstr_qualify validate` validates schemas/fixtures; full tests pass without model weights.
- [ ] T003 [P] [US2] Bootstrap `pyproject.toml`, `src/mstr_qualify/`, `tests/`, `configs/`, `schemas/`, `artifacts/`, `.gitignore`.
- [ ] T004 [P] [US7] Implement design schemas in `schemas/` and strict loader `src/mstr_qualify/schemas.py`; valid/invalid fixtures `tests/contract/`.
- [ ] T005 [P] [US7] Typed errors + ID/SHA helpers in `errors.py`/`ids.py`; unit tests.
- [ ] T006 [US2] Rights gate `rights.py`, tests, `evidence/T006-primary-backbone-rights-gate.md`.
- [ ] T007 [US7] Immutable evidence serialization `evidence.py`; golden/round-trip tests.
- [ ] T008 [US2] Task/benchmark manifests `manifests.py`; baseline `benchmarks/manifests/`.
- [ ] T009 [US4] Reporting/comparability `reporting.py`; reject mismatched cache/hardware/manifest.
- [ ] T010 [US2] CLI `validate`, `rights`, `candidate static`, `manifest validate`; offline integration test.
- [ ] T011 [US7] Quality config/full baseline gates; `evidence/T011-harness-foundation-qualification.md`.

## Phase 3: US2 Static Candidate Admission
**Prereq:** T003–T011. **Test:** schema-valid candidate record per exact revision, no weights.
- [ ] T012 [P] [US2] Qwen3.5-2B candidate JSON + evidence.
- [ ] T013 [P] [US2] Qwen3.5-4B candidate JSON + evidence.
- [ ] T014 [P] [US2] Ministral-3-3B candidate JSON + evidence.
- [ ] T015 [P] [US2] Qwen3-4B control JSON + evidence.
- [ ] T016 [P] [US2] Granite-4.1-3B JSON + evidence including FIM/components.
- [ ] T017 [P] [US2] SmolLM3-3B JSON + evidence.
- [ ] T018 [P] [US2] Qwen2.5-Coder-1.5B control JSON + evidence.
- [ ] T019 [P] [US2] Qwen2.5-Coder-3B reference-only/ineligible record with exact terms.
- [ ] T020 [P] [US2] Compact post-trained comparison records under `artifacts/candidates/comparisons/`.
- [ ] T021 [US2] Current 1B–5B foundation rescan; `evidence/T021-landscape-rescan.md`.
- [ ] T022 [US2] Static admission decision `artifacts/decisions/T022-static-candidate-admission.json`.

## Phase 4: US1 Task-Scoped Local Artifact Qualification
**Prereq:** T022. **No weight access before T028.**
- [ ] T023 [P] [US1] `RuntimeAdapter` + `PlatformSampler` protocols and dummy tests.
- [ ] T024 [P] [US1] Artifact manifest/hash verification `artifacts.py` + mismatch tests.
- [ ] T025 [P] [US1] Windows/Linux/macOS memory/paging samplers + fixture tests.
- [ ] T026 [P] [US1] `MSTR-MEASURE-v0` clocks/TTFI/TTFA/TTFCE/TTVC implementation + edge tests.
- [ ] T027 [US1] Weight-access manifest with exact candidates/revisions/hash/storage/runtime/quantizer/network/cost/retention.
- [ ] T028 [US1] **EXPLICIT WEIGHT ACCESS:** acquire only T027 artifacts after exact authorization; verify provenance; no binaries in Git.
- [ ] T029 [US1] Compatibility + quality Q4 profiles where practical; exact quantizer/recipe/hash.
- [ ] T030 [US1] Portable CPU runtime adapters; acceleration only bonus surfaces.
- [ ] T031 [US1] 4K/8K/16K size/load/memory/paging/prefill/decode results under `artifacts/results/local/`.
- [ ] T032 [US1] 10-minute sustained CPU/editor responsiveness characterization.
- [ ] T033 [US1] Q4 raw coding/FIM/multilingual/schema/edit primitive regressions.
- [ ] T034 [US1] Local artifact admission decision rejecting rights/U1/offline/size failures.

## Phase 5: US3 Interaction + Deterministic Edit Contract
**Prereq:** T034.
- [ ] T035 [P] [US3] Prompt/stable-prefix representation + hash golden fixtures.
- [ ] T036 [P] [US3] Tool grammar/parsers + malformed/schema tests.
- [ ] T037 [P] [US3] Deterministic tool-result serializers + byte-stability tests.
- [ ] T038 [P] [US3] Whole-file/unified-diff/search-replace/anchored edit adapters.
- [ ] T039 [US3] File hash/version stale-write transactions + conflict tests.
- [ ] T040 [P] [US3] Network/privacy/sandbox/task-state semantics configs.
- [ ] T041 [US3] Prompt/cache/tool/result/edit bake-off results.
- [ ] T042 [US3] Freeze `configs/interaction/mstr-interaction-v0.json` + decision.

## Phase 6: US4 Candidate Quality + Bounded Adaptation
**Prereq:** T042.
- [ ] T043 [US4] Freeze tournament task/seed/verifier/timeout manifest.
- [ ] T044 [P] [US4] Raw coding/FIM/multilingual results.
- [ ] T045 [P] [US4] Tool/edit reliability under Interaction v0.
- [ ] T046 [US4] Neutral minimal repository harness + localization/repair results.
- [ ] T047 [US4] Whole-laptop solve rate/TTVC/completions-hour/utility-per-GB.
- [ ] T048 [US4] Define optional external competitive TTVC protocol; no paid execution implied.
- [ ] T049 [US4] Pre-adaptation scorecard raw/neutral/full.
- [ ] T050 [US4] Select finalists.
- [ ] T051 [US4] Decontaminated execution-grounded micro-adaptation dataset manifest with FIM/recovery/reasoning replay.
- [ ] T052 [US4] Identical adaptation recipe/token/update/seeds/hardware/cost ceiling.
- [ ] T053 [US4] **EXPLICIT BOUNDED TRAINING:** run only after exact authorization.
- [ ] T054 [US4] Re-run local/quality suite on adapted finalists.
- [ ] T055 [US4] Top-one/top-two MSTR-001 pilot decision; not long-training authority.

## Phase 7: US5 Context Engine Tournament
- [ ] T056 [US5] `ContextProvider` + exact/ripgrep baseline.
- [ ] T057 [US5] Tree-sitter/RepoMap-style symbols + resource metrics.
- [ ] T058 [US5] Incremental sparse index + startup/update/RAM/disk.
- [ ] T059 [P] [US5] Embeddings/reranker experimental arm.
- [ ] T060 [P] [US5] SCIP experimental arm.
- [ ] T061 [P] [US5] Graphify experimental arm.
- [ ] T062 [P] [US5] Code-Graph-RAG experimental arm.
- [ ] T063 [US5] Context Pareto report.
- [ ] T064 [US5] Default minimal Context Engine decision + RAM/disk budget.

## Phase 8: US6 Environment / Verifier Factory MVP
- [ ] T065 [P] [US6] EnvironmentTask/Verifier records and validation.
- [ ] T066 [P] [US6] Deterministic workspace reset/snapshot + clean-hash tests.
- [ ] T067 [US6] Verifier runner with protected evaluator paths.
- [ ] T068 [US6] Oracle/reference pass, no-op fail, unsolved/broken fail admission.
- [ ] T069 [US6] Reward-shortcut battery: test deletion, assertion weakening, hardcoding, evaluator tamper, spoofing, cache/deleted solution.
- [ ] T070 [US6] Future-history/public-solution/network leakage controls.
- [ ] T071 [US6] Task yield/reset/startup/CPU/storage/failure/repro metrics.
- [ ] T072 [US6] Freeze MSTR-001 environment-factory MVP requirements.

## Phase 9: US7 Security, Privacy, Provenance, Benchmark Integrity
- [ ] T073 [P] [US7] Repository authority/trust model + prompt-injection fixtures.
- [ ] T074 [P] [US7] Workspace traversal, secrets, network/telemetry tests.
- [ ] T075 [P] [US7] Provenance record schema/model.
- [ ] T076 [US7] Benchmark exclusion/decontamination fingerprint + opt-out design.
- [ ] T077 [P] [US7] Teacher/API-output provenance/terms gate.
- [ ] T078 [US7] Runtime evaluation leakage fixtures.
- [ ] T079 [US7] Private/fresh MSTR Gauntlet contract in `benchmarks/private/README.md`.
- [ ] T080 [US7] Evidence audit command report->run->task->artifact/runtime/hardware/contracts/provenance.
- [ ] T081 [US7] Security/provenance readiness evidence.

## Phase 10: US8 MSTR-000 Closeout
- [ ] T082 [US8] Freeze measured hardware/OS floor + default context.
- [ ] T083 [US8] Freeze closeout distribution/install/privacy contract.
- [ ] T084 [US8] Freeze Interaction Contract v1 + fixtures/migration.
- [ ] T085 [US8] Freeze portable runtime/Q4 baseline + provenance/thresholds.
- [ ] T086 [US8] Freeze minimal Context Engine + resource budget.
- [ ] T087 [US8] Freeze top backbone/top-two with final scorecard.
- [ ] T088 [US8] Bounded MSTR-001 proposal with data/compute/environment/cost/rights/regression gates/non-authorities.
- [ ] T089 [US8] Independent Spec Kit consistency/evidence review; resolve CRITICAL/HIGH.
- [ ] T090 [US8] Founder acceptance; set MSTR-000 CLOSED_CANONICAL; update current state and exact next MSTR-001 authority.

## Dependencies
Critical path: `T003-T011 -> T012-T022 -> T023-T034 -> T035-T042 -> T043-T055 -> T064+T072+T081 -> T082-T090`.

US6 environment work can begin after harness foundation. T012–T020 can parallelize. T059–T062 can parallelize after context interface/baselines. T073/T074/T075/T077 can parallelize after harness foundation.

External-effect gates: **T028 first possible weight acquisition; T053 bounded micro-adaptation only. No MSTR-000 task authorizes long training or large-scale RL.**

## Completion Rule
A checkbox becomes `[x]` only when output paths exist, independent test/gate passes, identities are complete, external effects stayed in scope, and the result is canonical through repository governance.
