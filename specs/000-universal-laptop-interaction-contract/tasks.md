# MSTR-000 Tasks

All tasks are preconstruction qualification tasks. A checked task means evidence was produced and reviewed; it does not itself select the final backbone or authorize long training.

## Governance and measurement

- [ ] T000 Define the universal-laptop reference hardware matrix and exact support floor.
- [ ] T001 Define canonical TTFA, TTFCE, TTVC, peak-memory, artifact-size, and throughput measurement procedures.
- [ ] T002 Freeze the MSTR-000 benchmark/task manifest and seed policy before candidate scoring.
- [ ] T003 Define raw-model, neutral-harness, and full-system reporting surfaces.

## Interaction contract

- [ ] T004 Run prompt-prefix/cache-layout bake-off.
- [ ] T005 Run tool-call grammar and serialization bake-off.
- [ ] T006 Run edit-format tournament: whole-file vs unified-diff vs search/replace vs anchored patch.
- [ ] T007 Define deterministic stale-safe apply semantics and file-version contract.
- [ ] T008 Produce Interaction Contract v0 candidate from T004–T007.

## Base-model static qualification

- [ ] T009 Qualify Qwen3.5-2B-Base license, architecture, tokenizer, local-runtime support, and total footprint.
- [ ] T010 Qualify Qwen3.5-4B-Base license, architecture, tokenizer, local-runtime support, and total footprint.
- [ ] T011 Qualify Ministral-3-3B-Base-2512 license, architecture, tokenizer, local-runtime support, and total footprint.
- [ ] T012 Qualify Qwen3-4B-Base as mature dense control.
- [ ] T013 Qualify Qwen2.5-Coder-3B as code-specialized control.
- [ ] T014 Re-scan current 2B–4B open base landscape immediately before downloads; admit any materially stronger eligible candidate.

## Local Q4 qualification

- [ ] T015 Build or obtain reproducibly pinned Q4 test artifacts for admitted candidates.
- [ ] T016 Measure artifact size, peak memory, cold load, warm TTFA, and CPU throughput on the reference matrix.
- [ ] T017 Measure Q4 degradation in coding, FIM, JSON/tool calls, and edit grammar.
- [ ] T018 Reject candidates that violate the universal-laptop primary gate.

## Quality tournament

- [ ] T019 Run fresh raw coding/FIM/multilingual control suite on surviving candidates.
- [ ] T020 Run tool/edit reliability suite under Interaction Contract v0.
- [ ] T021 Run bounded repository-localization and repair suite with neutral harness.
- [ ] T022 Compute TTVC and verified-completion-per-GB metrics.
- [ ] T023 Select top candidates for bounded micro-adaptation; do not select final backbone yet.

## Bounded micro-adaptation

- [ ] T024 Define a small, decontaminated, execution-grounded adaptation set shared across candidates.
- [ ] T025 Run identical bounded adaptation protocol for the top candidates.
- [ ] T026 Re-run T016–T022 after adaptation.
- [ ] T027 Decide whether a top-two pilot remains necessary or whether one candidate is decisively dominated.

## Context tournament

- [ ] T028 Establish exact-search/ripgrep baseline.
- [ ] T029 Add Tree-sitter RepoMap-style symbols and measure marginal value.
- [ ] T030 Add incremental sparse index and measure marginal value/memory.
- [ ] T031 Evaluate optional embeddings/reranker arm.
- [ ] T032 Evaluate optional SCIP arm on supported languages.
- [ ] T033 Evaluate Graphify as an experimental arm.
- [ ] T034 Evaluate Code-Graph-RAG as an experimental arm.
- [ ] T035 Select the smallest context stack on the solve-rate/token/latency/RAM Pareto frontier.

## Environment factory

- [ ] T036 Build a small deterministic executable-task factory prototype.
- [ ] T037 Add oracle/reference-pass, no-op-fail, and unsolved-state checks.
- [ ] T038 Add reward-shortcut attacks: test deletion, assertion weakening, hardcoding, verifier tampering, future-history lookup, output spoofing.
- [ ] T039 Measure task yield, reset latency, CPU utilization, storage footprint, and failure rate.

## Security and integrity

- [ ] T040 Define repository-content trust boundaries and prompt-injection test cases.
- [ ] T041 Define training-data provenance schema, benchmark exclusion, and opt-out requirements.
- [ ] T042 Define runtime leakage controls for future benchmark runs.

## MSTR-000 closeout

- [ ] T043 Freeze measured universal-laptop hardware floor.
- [ ] T044 Freeze Interaction Contract v1.
- [ ] T045 Record selected local inference baseline and Q4 acceptance thresholds.
- [ ] T046 Record selected minimal Context Engine.
- [ ] T047 Record top backbone choice or top-two MSTR-001 pilot set.
- [ ] T048 Produce MSTR-001 bounded training proposal and compute/environment budget.
- [ ] T049 Independent review and reconciliation of all MSTR-000 evidence.
- [ ] T050 Founder acceptance of MSTR-000 closeout before serious training begins.
