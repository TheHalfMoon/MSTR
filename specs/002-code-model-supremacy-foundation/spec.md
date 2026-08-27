# Specification — MSTR-000B Code Model Supremacy Foundation

**Workstream:** MSTR-000B  
**Status:** PLANNING  
**Primary objective:** maximize verified software-building capability per parameter/GB while preserving the MSTR universal-laptop contract.

## 1. Problem

MSTR's mission is now explicitly code-specialized: software direction -> verified working code. The pre-existing compact-backbone scan and training plan were created before this mission was sharpened and therefore contain structural gaps:

1. the backbone scan excluded many specialized variants, creating risk that code-specialized foundations are omitted;
2. the repository has prose dependency rules but no machine-enforced task gate, and live execution has already demonstrated sequence drift;
3. code-focused continued pretraining is underspecified relative to agent post-training;
4. data is not yet organized around software evolution, feature construction, student-specific self-alignment, or dynamic difficulty;
5. verifier correctness/health is not yet a training-data admission primitive;
6. test generation is not yet a first-class learned skill;
7. expensive Direction-to-Done evaluation lacks a multi-fidelity promotion ladder;
8. Q4 regression is not yet explicitly in every material training iteration;
9. training-method choice is not yet an equivalent measured tournament;
10. long-run repository health is not yet a product metric.

## 2. User Outcome

A future MSTR release should be small enough for ordinary low-resource laptops yet unusually strong at:

- understanding terse software direction;
- navigating real repositories;
- implementing new features and bounded greenfield software;
- editing existing code precisely;
- writing/reusing tests and verifiers;
- using developer tools correctly;
- diagnosing failures and recovering;
- maintaining repository quality over repeated tasks;
- completing work under an 8K context and Q4 local runtime.

## 3. Required Product Metrics

The workstream MUST preserve existing metrics and add capability-efficiency metrics:

```text
DVCR = Direction-to-Verified-Completion Rate
TTVC = Time to Verified Completion
FPAR = First-Pass Accept Rate
ESR = Edit-Survival Rate
RSR = Repair Success Rate
TER = Tool Error Rate
RHD = Repository Health Delta
VC_PER_GB = Verified Completion utility per artifact GB
```

Tokenizer/context efficiency MUST be measured separately rather than hidden inside DVCR.

## 4. Functional Requirements

### FR-001 — Machine task/dependency gate

The repository MUST gain a machine-readable/task-validator mechanism that can determine whether a requested task is dependency-satisfied from canonical state and task metadata.

The gate MUST fail closed when:
- predecessor completion is missing;
- required explicit authority is missing;
- canonical state and checkbox/evidence state conflict materially;
- a stale/superseded task attempts execution;
- a candidate-dependent task runs before the stable candidate pool exists.

The validator MUST NOT silently mutate project state.

### FR-002 — Correct MSTR-000A early/convergence split

Model-independent MSTR-000A foundation work MAY proceed before T034 only when exact task dependencies allow it and no candidate result is consumed.

Candidate-dependent convergence such as cross-harness tournament/headline candidate comparison MUST wait for equivalent candidate qualification and MSTR-000B candidate-pool convergence.

### FR-003 — Mission-aligned backbone rescan

The project MUST rescan compact foundations without excluding code-specialized base/foundation models by category.

`JetBrains/Mellum-4b-base` MUST receive explicit review because it is a concrete previously omitted code-specialized base candidate. Other compact code-specialized families MUST be considered under the same rights/evidence rules.

No candidate is admitted solely because of benchmark reputation.

### FR-004 — Backbone scoring dimensions

Every serious backbone candidate MUST be scored on:
- rights/distribution fit;
- provenance/base status;
- parameter/artifact size;
- Q4 compatibility and size;
- CPU runtime compatibility;
- 8K context behavior;
- code/FIM prior;
- tokenizer code density;
- trainability/framework support;
- raw direct coding;
- repository/task relevance;
- quantization regression.

### FR-005 — New candidate external-effect gate

If MSTR-000B proposes weight access outside the existing frozen T027/T028 envelope, the exact candidate/revision/files/network/cost/retention envelope MUST receive separate founder authorization before access.

### FR-006 — Data Constitution

MSTR-001 entry MUST consume a versioned Data Constitution covering source classes, target distribution, provenance, licenses, benchmark exclusion, contamination, dedup, language mix, difficulty, synthetic data, teacher data, and training/eval boundaries.

### FR-007 — Software evolution records

The data model MUST support repository-evolution units tying together base revision, direction/issue, changes, tests/CI, review feedback, repairs, and final verified state without exposing future-history information to the model at the wrong step.

### FR-008 — Student self-alignment

The system MUST define an execution-filtered student self-alignment factory in which the student may generate tasks/solutions/tests but positive admission requires independent execution/verifier proof, provenance checks, and contamination checks.

### FR-009 — Teacher rescue

A stronger teacher MAY be used only as a bounded rescue/reference source when exact output/data rights permit it. Teacher outputs MUST pass the same verifier/provenance/admission rules as student outputs.

Teacher output MUST NOT become truth by model identity.

### FR-010 — Difficulty/frontier curriculum

Training tasks MUST support dynamic difficulty labels relative to an exact student checkpoint and evaluation protocol.

At minimum:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

Difficulty estimates MUST be refreshable as model capability changes.

### FR-011 — Test-generation curriculum

MSTR-002 entry MUST include training/evaluation for reproduction tests, regression tests, boundary/error tests, and failure-before/pass-after behavior where applicable.

The same model may operate in builder/tester/reviewer modes; separate runtime models are not required.

### FR-012 — Verifier Health Contract

Training/evaluation examples MUST carry verifier-health status.

The contract MUST distinguish at least:

```text
HEALTHY
PARTIAL
DISAGREEMENT
BROKEN
LEAKED
TAMPERED
```

Only examples meeting the training stage's verifier-health threshold may become clean positive examples.

### FR-013 — Greenfield/feature curriculum

Direction-to-Done and training data MUST materially cover new feature implementation, bounded greenfield programs, API/CLI construction, integrations, migrations, refactoring with behavioral preservation, build/CI repair, test authoring, and bug repair.

Bug-patch tasks MUST NOT dominate the product evaluation by default.

### FR-014 — Feature-tree/semantic synthesis

Feature-tree or equivalent semantic-complexity synthesis MUST be evaluated as an experimental generator for progressively harder function/module/file/multi-file/program tasks. It is not automatically admitted into production training data.

### FR-015 — Multi-fidelity research ladder

MSTR Research Loop MUST implement promotion tiers:

```text
L0 contract/smoke
L1 code/FIM/edit/tool
L2 executable small-repo
L3 Direction-to-Done/feature/program
L4 Q4 universal-laptop
```

Promotion criteria MUST be predeclared. Expensive levels MUST not be run for every weak experiment.

### FR-016 — Adaptive Build Loop

MSTR-BUILD-LOOP MUST be implemented as a bounded state graph with a trivial-task fast path rather than forcing every task through every conceptual state.

### FR-017 — Adaptive test-time compute

The runtime/harness MAY spend additional bounded attempts only when verifier evidence/uncertainty and expected benefit justify the cost. Best-of-K/multi-branch execution is optional and must be measured against DVCR/TTVC/resource cost.

### FR-018 — Selective context intents

Context policy MUST support explicit intent classes including `NO_RETRIEVAL`, `NEED_FILE`, `NEED_SYMBOL`, `NEED_HISTORY`, `NEED_TEST`, `NEED_CONFIG`, and `NO_MORE_CONTEXT` where the active interaction contract supports them.

### FR-019 — Q4-in-the-loop

Every material weight-changing stage MUST re-export/qualify the release-relevant Q4 artifact before the stage may become the parent of a more expensive training stage.

### FR-020 — Training method tournament

Before selecting the default compact-model method, the project MUST preflight equivalent candidate arms where supported:
- 16-bit LoRA;
- 16-bit LoRA + rsLoRA;
- 4-bit QLoRA;
- 4-bit QLoRA + rsLoRA.

Full fine-tuning remains separately justified and is not the default.

### FR-021 — Repository Health Delta

The evaluation system MUST support multi-round repository sequences and report whether codebase health improves, holds, or degrades. The exact metric set may vary by language but should include structural/test/dependency quality where measurable.

### FR-022 — Cross-harness robustness

MSTR MUST preserve separate RAW_MODEL, H0 neutral, H1 MSTR-native, and H2 WePLD score surfaces. Training/evaluation MUST detect severe scaffold overfitting.

### FR-023 — Programming-language target mix

MSTR-001 MUST freeze a target language/tooling mixture derived from intended software-building usage and evidence. Long-tail breadth MUST NOT consume capacity merely for marketing coverage.

### FR-024 — Training readiness

No weight-changing training gate may open until the MSTR-000B closeout explicitly verifies all required contracts and identifies unresolved risks.

## 5. Non-Functional Requirements

### NFR-001 — Reproducibility

Every material candidate/data/training/evaluation result must bind to exact model, tokenizer, runtime, task, verifier, data, hardware, context, quantization, sampling, and code identities as applicable.

### NFR-002 — Rights/provenance

All primary-product model/data/teacher/tool inputs fail closed on ambiguous or incompatible rights.

### NFR-003 — Privacy

Private user repositories and production traces default to not-ingested. No hidden telemetry.

### NFR-004 — Cost discipline

Planning and metadata work MUST not imply paid compute. Free/authorized compute remains preferred until evidence justifies escalation and separate authority is granted.

### NFR-005 — Universal-laptop preservation

No training success may silently raise the 8GB/CPU/8K/Q4<=3GB product floor.

## 6. Acceptance Criteria

MSTR-000B can close only when:

1. task/dependency enforcement is implemented and tested;
2. mission-aligned backbone rescan is canonical;
3. code-specialized candidates are admitted/rejected with explicit reasons;
4. tokenizer and Q4/runtime economics are measured for the stable candidate pool;
5. Data Constitution is frozen;
6. software-evolution schema is frozen;
7. self-alignment/teacher/difficulty contracts are frozen;
8. test-generation and verifier-health contracts are frozen;
9. greenfield/feature curriculum is specified;
10. multi-fidelity research ladder is qualified on at least one non-weight experiment;
11. Q4-in-the-loop regression contract is frozen;
12. training-method tournament preflight is frozen;
13. repository-health metric contract is frozen;
14. A019/A020 and downstream MSTR-001/002/003 dependencies are reconciled;
15. weight-changing training remains behind an explicit founder gate.

## 7. Explicit Non-Authorities

This specification does not authorize:

```text
NEW MODEL WEIGHT ACCESS OUTSIDE EXISTING AUTHORITY
LARGE DATASET INGESTION
PAID COLAB
RENTED GPU
WEIGHT-CHANGING TRAINING
LARGE-SCALE RL
PRODUCTION RELEASE
PRIVATE USER TRACE INGESTION
```
