# MSTR-000 Tasks

All tasks are preconstruction qualification tasks. A checked task means evidence was produced and reviewed; it does not itself select the final backbone or authorize long training.

No model-weight download, paid model API execution, or rented training compute is authorized by this planning PR. After the plan becomes canonical, only the explicit task that names such access may authorize it.

## Governance, hardware, and measurement

- [x] T000 Define the universal-laptop reference hardware/OS matrix, concurrent editor workload, exact support floor, and 4K/8K/16K context ladder. Evidence: `evidence/T000-universal-laptop-hardware-matrix.md`. The task defines a qualification floor; final measured support remains T060.
- [x] T001 Define canonical TTFI, TTFA, TTFCE, TTVC, artifact-size, process-RSS, total-system-memory, swap/page-fault, throughput, sustained-thermal, and optional energy measurement procedures. Evidence: `evidence/T001-measurement-procedures.md` (`MSTR-MEASURE-v0`).
- [x] T002 Freeze the universal distribution/install/privacy contract: no account/API key, offline after install, telemetry/network off by default, portable CPU runtime, and no Docker/dev-toolchain requirement merely to launch basic assistance. Evidence: `evidence/T002-distribution-install-privacy-contract.md` (`MSTR-DIST-v0`).
- [ ] T003 Define the primary-backbone rights gate covering use, commercial use, modification/fine-tuning, quantization/conversion, derivative redistribution, and end-user obligations.
- [ ] T004 Define evidence identity requirements for model revision, checksums, tokenizer, quantizer, runtime/build flags, hardware, context/cache, interaction contract, task manifest, and seeds.
- [ ] T005 Freeze the MSTR-000 benchmark/task manifest and seed policy before candidate scoring.
- [ ] T006 Define raw-model, neutral-harness, and full-system reporting surfaces plus the competitive TTVC protocol.

## Base-model static qualification — no weight download required

- [ ] T007 Qualify `Qwen/Qwen3.5-2B-Base`: license/terms, architecture, tokenizer, vision footprint, local-runtime support, quantization maturity, and exact upstream revision.
- [ ] T008 Qualify `Qwen/Qwen3.5-4B-Base` under the same static gate.
- [ ] T009 Qualify `mistralai/Ministral-3-3B-Base-2512` under the same static gate.
- [ ] T010 Qualify `Qwen/Qwen3-4B-Base` as the mature dense control.
- [ ] T011 Qualify `ibm-granite/granite-4.1-3b-base`, including FIM suitability and distribution rights.
- [ ] T012 Qualify `HuggingFaceTB/SmolLM3-3B-Base` as an open text-only control.
- [ ] T013 Qualify `Qwen/Qwen2.5-Coder-1.5B` as the code-specialized lower-bound control.
- [ ] T014 Record `Qwen/Qwen2.5-Coder-3B` as ineligible for the primary backbone while its upstream research/non-commercial license remains incompatible.
- [ ] T015 Review useful post-trained comparison points such as Phi-4-mini-instruct without treating them as foundation candidates.
- [ ] T016 Re-scan the current compact open-base landscape immediately before the first weight-access task; statically qualify any materially stronger eligible candidate.
- [ ] T017 Select the bounded set of candidates eligible to proceed to task-scoped local artifact qualification. This is not final backbone admission.

## Task-scoped local Q4 qualification

- [ ] T018 Define the exact candidate weight-access manifest, upstream revisions, expected hashes, storage ceiling, quantization recipes, runtime versions, and cost ceiling if any.
- [ ] T019 After explicit task authorization, obtain/build pinned Q4-class test artifacts for the admitted candidates only.
- [ ] T020 Compare at least one quality-oriented and one compatibility-oriented Q4 profile where practical; record exact quantizer/tool revision.
- [ ] T021 Prove portable CPU runtime paths and record optional Metal/Vulkan/CUDA/etc. acceleration only as bonuses.
- [ ] T022 Measure artifact size, process RSS, total-system memory pressure, swap/page faults, cold load, warm TTFA, and throughput at 4K/8K/16K on the reference matrix.
- [ ] T023 Run sustained CPU inference to measure throttling/responsiveness; measure energy per task where reliable counters exist.
- [ ] T024 Measure Q4 degradation in coding, FIM, multilingual instruction following, JSON/tool calls, and edit grammar.
- [ ] T025 Reject candidates that violate rights, artifact-size, CPU-runtime, whole-laptop memory, responsiveness, or offline-use gates.

## Interaction contract

- [ ] T026 Run prompt-prefix/cache-layout bake-off on surviving candidates.
- [ ] T027 Run tool-call grammar and deterministic result-serialization bake-off.
- [ ] T028 Run edit-format tournament: whole-file vs unified-diff vs search/replace vs anchored patch.
- [ ] T029 Define deterministic stale-safe apply semantics and file-version/hash contract.
- [ ] T030 Define network/privacy/sandbox semantics visible to the model and task-state/compaction schema if used.
- [ ] T031 Produce Interaction Contract v0 candidate from T026–T030.

## Quality tournament

- [ ] T032 Run fresh raw coding/FIM/multilingual control suite on surviving candidates.
- [ ] T033 Run tool/edit reliability suite under Interaction Contract v0.
- [ ] T034 Run bounded repository-localization and repair suite with a neutral minimal harness.
- [ ] T035 Measure whole-laptop verified completion rate, TTVC, verified completions/hour, and verified utility per GB.
- [ ] T036 If separately authorized and access is available, run the fixed competitive TTVC protocol against selected cloud coding systems; keep cloud/harness effects separate from model comparisons.
- [ ] T037 Select top candidates for bounded micro-adaptation; do not select the final backbone yet.

## Bounded micro-adaptation

- [ ] T038 Define a small, decontaminated, execution-grounded adaptation set shared across candidates, including FIM replay and failure/recovery examples.
- [ ] T039 Define the identical bounded adaptation recipe, exact token/update budget, hardware, seeds, and cost ceiling.
- [ ] T040 Run the identical bounded adaptation protocol for the top candidates only after task authorization.
- [ ] T041 Re-run T022–T035 after adaptation.
- [ ] T042 Decide whether a top-two MSTR-001 pilot remains necessary or whether one candidate is decisively dominated.

## Context tournament

- [ ] T043 Establish exact-search/ripgrep baseline.
- [ ] T044 Add Tree-sitter RepoMap-style symbols and measure marginal value.
- [ ] T045 Add incremental sparse index and measure marginal value, memory, disk, startup, and incremental-update cost.
- [ ] T046 Evaluate optional embeddings/reranker arm.
- [ ] T047 Evaluate optional SCIP arm on supported languages.
- [ ] T048 Evaluate Graphify as an experimental arm.
- [ ] T049 Evaluate Code-Graph-RAG as an experimental arm.
- [ ] T050 Select the smallest context stack on the solve-rate/token/latency/RAM/disk Pareto frontier. Context-engine memory counts against the 8 GB whole-laptop budget.

## Environment factory

- [ ] T051 Build a small deterministic executable-task factory prototype.
- [ ] T052 Add oracle/reference-pass, no-op-fail, and unsolved-state checks.
- [ ] T053 Add reward-shortcut attacks: test deletion, assertion weakening, hardcoding, verifier tampering, future-history lookup, public-solution/network lookup, cache/deleted-solution recovery, and output spoofing.
- [ ] T054 Measure task yield, reset latency, CPU utilization, storage footprint, environment failure rate, and reproducibility.

## Security, privacy, and provenance

- [ ] T055 Define repository-content trust boundaries and prompt-injection test cases.
- [ ] T056 Define local network/telemetry defaults, secret-handling boundaries, and offline privacy tests.
- [ ] T057 Define training-data provenance schema, benchmark exclusion, owner opt-out, and license checks.
- [ ] T058 Define teacher/API-output provenance and terms checks before any synthetic/distilled data can enter MSTR training.
- [ ] T059 Define runtime answer-leakage controls for future benchmark runs.

## MSTR-000 closeout

- [ ] T060 Freeze the measured universal-laptop hardware/OS floor and default context.
- [ ] T061 Freeze the distribution/install/privacy contract and basic local runtime requirements.
- [ ] T062 Freeze Interaction Contract v1.
- [ ] T063 Record selected portable local inference baseline, Q4 profile, artifact provenance contract, and acceptance thresholds.
- [ ] T064 Record selected minimal Context Engine and its RAM/disk budget.
- [ ] T065 Record top backbone choice or top-two MSTR-001 pilot set.
- [ ] T066 Produce MSTR-001 bounded training proposal and compute/environment budget, including dataset/teacher rights constraints.
- [ ] T067 Independent review and reconciliation of all MSTR-000 evidence.
- [ ] T068 Founder acceptance of MSTR-000 closeout before serious training begins.
