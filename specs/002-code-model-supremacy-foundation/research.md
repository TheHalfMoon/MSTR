# Research — MSTR-000B Code Model Supremacy Foundation

**Research date:** 2026-08-27  
**Question:** What gives a <=3 GB Q4, 8 GB RAM, CPU-usable code model the highest probability of becoming exceptionally strong at taking software direction and finishing verified software work?

## Executive Findings

1. **Backbone search must match the current mission.** The original T021 scan excluded specialized variants, but MSTR is now explicitly code-specialized. Code-specialized bases must be first-class candidates when rights and deployment fit.
2. **Code prior matters before agent RL.** Cursor Composer 2 reports that continued code-focused pretraining improved downstream RL; agent training does not erase the need for strong coding knowledge.
3. **Data distribution matters more than raw token count for a small model.** Student-aligned, software-distribution-matched data is unusually high leverage.
4. **Software evolution is richer than static code.** Issues, commits, tests, CI, reviews, and repairs expose the actual engineering process.
5. **Self-alignment can outperform blanket teacher distillation.** Execution-filtered student-generated examples preserve the student's own distribution while retaining correctness gates.
6. **Difficulty should track the student's frontier.** Easy datasets waste compute; impossible tasks provide little useful signal. Dynamic difficulty is a training primitive.
7. **Test generation and verifier health must be learned/validated explicitly.** Passing a weak test suite is not enough.
8. **Feature/greenfield work must be prominent.** Bug repair alone is too narrow for the founder goal of direction -> build.
9. **Research needs multi-fidelity promotion.** Full Direction-to-Done and laptop tests are too expensive for every experiment.
10. **Q4 behavior is the product behavior.** Every material stage must recheck the actual deployment quantization.
11. **Repository health across repeated tasks matters.** Single-ticket solve rate can hide compounding technical debt.
12. **Machine-enforced task gates are required.** Live repository history already demonstrated that prose ordering can drift from execution.

---

## 1. Product-Aligned Backbone Search

### JetBrains Mellum-4B

Source:
- https://huggingface.co/JetBrains/Mellum-4b-base

Relevant facts from the model card:
- 4B LLaMA-style base model;
- Apache-2.0;
- optimized specifically for code-related tasks;
- 8,192-token context;
- trained on approximately 4.2T tokens;
- training corpus includes The Stack, StarCoder data, The Stack v2, CommitPack, and English Wikipedia;
- intended for developer tooling/local use and supports later SFT/RL adaptation.

MSTR conclusion:
- Mellum is not preselected as winner;
- its omission from the existing candidate set proves the old scan heuristic is no longer sufficient after MSTR became explicitly code-specialized;
- it must be reviewed under the same exact rights, Q4, runtime, tokenizer, and raw-quality gates as all other foundations.

Other code-specialized compact families should be reviewed similarly. License incompatibility may place some models in control/reference-only lanes rather than primary admission.

---

## 2. Continued Code Pretraining Before Agent RL

Sources:
- https://prod.cursor.com/blog/composer-2-technical-report
- https://cursor.com/blog/composer-2

Cursor reports a two-stage training strategy for Composer 2:

```text
continued pretraining on a code-emphasized data mix
-> large-scale RL in realistic Cursor sessions
```

The technical report states that lower continued-pretraining loss / stronger code knowledge reliably translated into stronger downstream agent RL performance.

MSTR conclusion:
- MSTR-001 code/FIM mid-training is a central capability stage, not merely optional polishing;
- a sophisticated harness cannot be expected to compensate for an under-specialized code prior;
- MSTR should spend scarce training budget only after measuring whether continued pretraining improves direct coding/FIM and agent-relevant proxies.

Do not copy:
- frontier-scale compute assumptions;
- 32K/256K context as a product target;
- Cursor proprietary training data.

---

## 3. Execution-Filtered Student Self-Alignment

Source:
- https://arxiv.org/abs/2410.24198

SelfCodeAlign uses the same base model to generate coding concepts/tasks, multiple responses and tests, then sandbox-executes and selects passing examples for instruction tuning. The paper reports strong gains across 3B–33B models and shows that self-aligned data can outperform direct distillation approaches in its evaluated settings.

MSTR conclusion:

```text
STUDENT GENERATION
-> MULTIPLE SOLUTIONS / TESTS
-> SANDBOX EXECUTION
-> INDEPENDENT VERIFIER
-> PROVENANCE/CONTAMINATION CHECK
-> TRAINING ADMISSION
```

This should become a first-class MSTR data-factory path.

Teacher models remain useful for frontier rescue, but teacher output must pass the same verification and rights gates.

---

## 4. Difficulty-Aware Curriculum / MicroCoder

Sources:
- https://www.microsoft.com/en-us/research/publication/scaling-data-difficulty-improving-coding-models-via-reinforcement-learning-on-fresh-and-challenging-problems/
- https://www.microsoft.com/en-us/research/publication/breaking-training-bottlenecks-effective-and-stable-reinforcement-learning-for-coding-models/

Microsoft's 2026 MicroCoder work reports that a more challenging curated dataset produced roughly 3x larger gains than mainstream datasets of similar size within 300 training steps in their evaluated setup, and that difficulty, diversity, truncation behavior, and evaluator quality materially affect coding RL.

MSTR conclusion:
- difficulty must be measured relative to the current student checkpoint;
- curriculum selection is dynamic rather than a frozen easy/hard label;
- training should focus on the learnable frontier and gradually promote harder tasks;
- evaluation quality/speed is itself part of training efficiency.

---

## 5. Software Evolution as Training Signal

Source:
- https://arxiv.org/abs/2502.18449

SWE-RL trains on open-source software evolution records: code snapshots, code changes, issues and pull requests. The work demonstrates that software lifecycle data can teach repository reasoning rather than only static completion.

MSTR conclusion:
- create a SoftwareEvolutionRecord binding base revision, direction/issue, relevant context, change sequence, tests/CI, review feedback, repair events and final verified revision;
- derive localization, edit, review-repair and failure-recovery examples while preserving future-history isolation;
- do not leak the final patch or future commit into model-visible context for earlier steps.

---

## 6. Feature Implementation / FEA-Bench

Sources:
- https://www.microsoft.com/en-us/research/publication/fea-bench-a-benchmark-for-evaluating-repository-level-code-generation-for-feature-implementation/
- https://github.com/microsoft/FEA-Bench

FEA-Bench contains 1,401 feature-implementation tasks from 83 GitHub repositories and evaluates both generation of new components and edits to existing code.

MSTR conclusion:
- Direction-to-Done must include feature addition, not just bug repair;
- public FEA-Bench can be continuity evidence where rights/environment allow;
- private MSTR tasks should include similar feature-increment behavior with fresh hidden acceptance criteria.

---

## 7. Whole-Program Construction / ProgramBench

Source:
- https://programbench.com/

As of 2026-08-16, ProgramBench exposes 200 program reconstruction tasks and more than 248,000 hidden behavioral tests. Even frontier agents fully solve only a small fraction of tasks on the current leaderboard.

MSTR conclusion:
- bounded greenfield/whole-program construction is a separate skill from patching;
- the private Gauntlet should contain small/medium program-building tasks that fit the universal-laptop research budget;
- ProgramBench itself is supporting/reference evaluation, not necessarily a training dataset.

---

## 8. Feature-Tree-Driven Synthetic Data

Source:
- https://www.microsoft.com/en-us/research/articles/feature-tree-driven-synthesis-improves-training-data-for-code-llms/

Microsoft Research describes a semantic feature-tree synthesis method that scales examples from simple functions toward more complex files and cross-component structures. Their EpiCoder training used more than 430k synthesized instruction samples.

MSTR conclusion:
- evaluate semantic/feature-tree synthesis as a controllable curriculum generator;
- use it to produce difficulty tiers from function -> module -> file -> multi-file feature -> small program;
- synthetic output is admitted only after rights/provenance and verifier checks.

---

## 9. Selective Retrieval / Repoformer

Sources:
- https://repoformer.github.io/
- https://arxiv.org/abs/2403.10059

Repoformer finds that repository retrieval can be unnecessary or harmful and reports large serving-latency savings from selective retrieval in its evaluated code-completion setting.

MSTR conclusion:
- `NO_RETRIEVAL` must be a learned/valid outcome;
- context acquisition should be intent-aware rather than blindly retrieving files;
- at 8K, tokenizer efficiency and retrieval selectivity are model capability.

---

## 10. Long-Term Repository Health / CodeClash

Source:
- https://codeclash.ai/

CodeClash evaluates repeated goal-oriented software development rounds and reports that model-maintained codebases can accumulate technical debt and become messy over time.

MSTR conclusion:
- add Repository Health Delta over multi-round task sequences;
- successful task completion is insufficient if the model systematically adds duplication, dead code, architecture violations, or test debt;
- minimal/surgical behavior is a training preference target, not only a prompt instruction.

---

## 11. Harness / Agent Loop Evidence

Existing MSTR-000A research already covers:
- Karpathy autoresearch;
- DeepSeek Harness;
- Cursor production-like train/serve harness consistency;
- Cursor autoinstall;
- Claude goal loops;
- SWE-agent / mini-SWE-agent;
- executable-environment training;
- function-/instruction-aware FIM.

MSTR-000B extends those conclusions rather than replacing them.

Primary new implication:
- the harness is necessary but not sufficient;
- the model foundation, data distribution, verifier health, and curriculum must be optimized with equal rigor.

---

## 12. Unsloth / Training-Method Implications

Current planning source supplied by founder:
- https://unsloth.ai/docs/models/qwen3.8/train

Related current Unsloth documentation should be revalidated before execution.

MSTR conclusion:
- Unsloth remains a preferred accessible implementation path on Colab;
- training method must be evidence-selected, not framework-selected;
- equivalent compact-model arms should include LoRA/rsLoRA and QLoRA/rsLoRA where architecture support is current and stable;
- full fine-tuning remains non-default;
- Qwen3.8-class larger models may be useful teacher/reference candidates but do not satisfy the primary 8GB/Q4 product envelope.

---

## 13. Gaps in Current MSTR Plan

### P0

1. mission-aligned backbone rescan;
2. machine task/dependency enforcement;
3. code-focused continued-pretraining/data-mixture program;
4. student-frontier curriculum;
5. execution-filtered self-alignment factory;
6. software-evolution corpus;
7. test-generation curriculum;
8. verifier-health contract.

### P1

9. greenfield/feature curriculum;
10. feature-tree synthesis arm;
11. multi-fidelity autoresearch ladder;
12. adaptive loop/test-time compute;
13. tokenizer economics;
14. Q4-in-the-loop regression;
15. repository-health-over-time metric;
16. cross-harness robustness.

### P2

17. learned verifier/reranker only if deterministic verification leaves a measured gap;
18. multi-agent topologies only if they justify cost;
19. sub-Q4 release quantization only if evidence shows an exceptional quality/size frontier.

---

## 14. Research Decision

MSTR should not begin weight-changing training until MSTR-000B converts these gaps into executable contracts and reconciles them with MSTR-000A and downstream workstreams.

The intended flywheel is:

```text
product-aligned foundation
-> high-signal software data
-> student self-alignment
-> difficulty/frontier curriculum
-> executable verification
-> SFT/RL under production-compatible harness
-> Q4 regression
-> Direction-to-Done / WePLD evidence
-> autoresearch learns what to improve next
```

This is the highest-confidence route identified for maximizing tiny-model software-building capability without abandoning the universal-laptop constraint.
