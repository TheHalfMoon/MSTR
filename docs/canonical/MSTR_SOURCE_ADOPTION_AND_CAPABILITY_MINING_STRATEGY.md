# MSTR Source Adoption and Capability Mining Strategy

Status: CANONICAL_PLANNING_AMENDMENT_ON_MERGE  
Date: 2026-09-08  
Scope: MSTR-000A / MSTR-000B downstream planning  
External effects created by this document: NONE

## 1. Purpose

MSTR may study, copy, adapt, or reimplement useful implementation primitives from authorized source repositories, but source availability must never become an excuse for dependency sprawl, hidden authority expansion, provenance loss, evaluator leakage, or hardware assumptions that violate the local-first product contract.

This strategy turns source use into an auditable engineering process. The objective is not to vendor entire repositories. The objective is to mine the smallest useful capability, prove that it improves MSTR under its own metrics and constraints, preserve provenance, and keep a tested rollback path.

## 2. Non-negotiable authority boundary

The following identities are distinct and MUST NOT be collapsed:

```text
SOURCE_CODE_PERMISSION
  != DATA_ADMISSION
  != MODEL_WEIGHT_AUTHORITY
  != TRAINING_AUTHORITY
  != EXTERNAL_EFFECT_AUTHORITY
```

Founder-stated permission to use source code authorizes source-code study/copy/adaptation within repository governance. It does not authorize:

- ingestion of third-party datasets or repository contents as training/evaluation data;
- downloading or executing model weights outside existing model authority;
- training, fine-tuning, distillation, RL, speculative-draft training, or paid compute;
- network or cloud execution that is otherwise gated;
- weakening license, NOTICE, attribution, export, privacy, or security obligations;
- treating an upstream benchmark result or vendor claim as MSTR evidence.

Every later external effect still requires its own canonical authority.

## 3. Source adoption modes

Each source receives exactly one current disposition for each proposed capability:

- `ADOPT_PRIMITIVE`: copy or adapt a bounded implementation primitive after review and qualification.
- `REFERENCE_BASELINE`: implement or exercise an equivalent baseline to measure whether added complexity earns its cost.
- `STUDY_METHOD`: use the method or architecture as research input only; no code enters the core from this disposition.
- `REJECT_FOR_CORE`: useful upstream work that would violate MSTR footprint, determinism, offline, dependency, security, or authority constraints if imported into the product core.

A source may have different dispositions for different primitives. No repository receives blanket admission.

## 4. SourceAdoptionRecord

Any copied, adapted, vendored, or behaviorally reimplemented primitive MUST have a `SourceAdoptionRecord` before merge. The record MUST contain:

- `source_id`
- upstream repository and canonical URL
- observed and adopted immutable revision
- source-use permission provenance
- upstream license identifier/file and retained attribution/NOTICE obligations
- exact copied/adapted source paths or method references
- `adoption_mode`
- MSTR capability and task consuming the primitive
- reason for adoption and rejected simpler alternatives
- direct and transitive dependencies introduced
- network, filesystem, subprocess, container, GPU, and secret-access surfaces
- offline and privacy behavior
- product footprint impact: installed bytes, startup latency, steady RSS, dependency count
- integration patch/tree hash
- behavior/equivalence tests
- security/threat review
- evaluator-isolation review when relevant
- update policy and upstream churn policy
- rollback/fallback path
- explicit authority fields for data, model access, training, paid compute, and external effects

A missing record is a merge blocker for source-derived core code.

## 5. Minimal primitive rule

MSTR MUST prefer, in order:

1. a small MSTR-native implementation that captures the needed invariant;
2. a copied/adapted bounded upstream primitive with provenance;
3. a pinned optional dependency with a narrow adapter;
4. whole-repository vendoring only when no smaller form preserves correctness and the footprint is independently justified.

`git submodule`, mutable branch dependencies, install-time code fetches, and runtime auto-updaters are forbidden in the baseline product path unless a later explicit plan changes this rule.

## 6. Anti-complexity gate

Every proposed harness/runtime capability MUST be compared against `MINIMAL_BASH_LINEAR_BASELINE` before promotion.

The comparison records at least:

- verifier-correct task rate / DVCR impact;
- TTVC impact;
- harness LOC;
- direct/transitive dependency count;
- prompt/tool-schema token overhead;
- cold-start latency;
- steady-state RSS;
- filesystem/process/network attack surface;
- failure modes and recovery burden;
- platform portability;
- deterministic replay quality.

Complexity without measured user-visible or verifier-visible benefit is rejected.

## 7. ExecutionBackendProfile

MSTR-000A successor harness work SHOULD introduce an `ExecutionBackendProfile` abstraction with a local subprocess baseline and optional adapters. The profile records:

- backend identity and immutable implementation revision;
- local/remote/sandbox class;
- process and session lifecycle;
- timeout, cancellation, and cleanup semantics;
- streaming/stdout/stderr behavior;
- interactive command support;
- workspace reset/snapshot semantics;
- filesystem/network isolation;
- credential/secret boundary;
- supported operating systems;
- startup latency and RSS;
- fallback backend.

Docker or remote sandboxing may be an optional profile, not a universal baseline requirement.

## 8. ResumableTaskCheckpoint

Long-running MSTR work SHOULD persist a small, secret-free `ResumableTaskCheckpoint` inspired by durable workflow systems rather than relying on process memory. It records:

- task/goal identity;
- requirements and accepted decisions;
- repository/base/head/tree identity;
- completed phases and durable evidence references;
- pending verifier/reviewer actions;
- tool/environment identity;
- resumable reason and next legal transition;
- redaction status and prohibited secret classes.

A checkpoint is state, not authority. Resuming from it MUST revalidate live repository state and authority.

## 9. ImprovementDecisionRecord

Automated prompt/tool/skill/harness improvement MUST create an immutable `ImprovementDecisionRecord` containing:

- diagnosis and hypothesis;
- candidate revision;
- allowed evidence exposed to the optimizer;
- protected evaluation evidence withheld from the optimizer;
- evaluator identity;
- regression set identity;
- outcome: `KEEP`, `DISCARD`, `CRASH`, or `INCONCLUSIVE`;
- metric deltas and uncertainty;
- failure evidence;
- rollback target.

The optimizer MUST NOT read protected evaluation outputs before proposing the candidate. The evaluator MUST NOT mutate the candidate being evaluated. Discarded and crashed attempts remain durable negative evidence.

Whole-skill changes may update prompts, scripts, references, and bounded configuration atomically, but they still require the same frozen evaluator and regression gate.

## 10. RepositoryContextIndexProfile

Repository-context retrieval MUST use an explicit ladder:

1. `grep/find` baseline;
2. deterministic syntax/symbol index where justified;
3. token-budgeted ranked repository map;
4. learned retrieval only after an evidence-backed need.

A `RepositoryContextIndexProfile` records parser versions, included file classes, ignore rules, graph/ranking method, token budget, invalidation rules, stale-index detection, offline behavior, privacy boundary, and fallback.

The index is disposable derived state. Repository truth always remains the checked-out tree.

## 11. TrainingBackendParityRecord

A faster training backend MUST NOT become canonical only because it completes faster. Before promotion, a `TrainingBackendParityRecord` compares the reference implementation and the accelerated backend under an authorized, bounded experiment with identical data, seed, update budget, model revision, and objective.

The record compares at least:

- trainable parameter set and count;
- optimizer/scheduler semantics;
- loss trajectory within declared tolerance;
- checkpoint serialization and resume behavior;
- merged-weight identity or declared numerical tolerance;
- post-merge inference behavior;
- Q4 conversion outcome where applicable;
- peak memory and wall-clock improvement;
- unexplained divergences.

Unexplained semantic or artifact divergence fails closed. This record does not itself authorize training.

## 12. Runtime acceleration ladder

Runtime acceleration follows baseline-first promotion:

1. ordinary autoregressive reference path;
2. native runtime acceleration already supported by the pinned runtime, including speculative/draft paths where compatible;
3. custom or source-derived acceleration only when step 2 cannot meet the measured goal.

Each rung measures verifier correctness, TTVC, steady RSS, startup latency, artifact footprint, determinism, and fallback behavior. Vendor speed claims are research signals, not MSTR evidence.

## 13. Behavioral reconstruction evaluation

MSTR SHOULD add a bounded behavioral-reconstruction evaluation lane inspired by whole-program reconstruction research. A task may expose specification/documentation and a permitted executable behavioral oracle while withholding source implementation. Evaluation MUST use hidden behavioral tests and must keep evaluator-owned cases unavailable to the candidate/optimizer.

This lane complements repository evolution and greenfield tasks; it does not replace them.

## 14. Donor capability matrix

The research snapshot dated 2026-09-08 is the exact revision source of truth for this planning amendment. Current planned dispositions are:

| Source | Planned disposition | MSTR capability mined |
|---|---|---|
| Tencent/LoopForge | ADOPT_PRIMITIVE | resumable workflow/checkpoint semantics |
| Tencent/SkillHone | ADOPT_PRIMITIVE | persistent improvement decisions and optimizer/evaluator separation |
| deepseek-ai/deepseek-harness | STUDY_METHOD | compatibility/churn and harness primitive mining |
| SWE-agent/mini-swe-agent | REFERENCE_BASELINE | minimal bash-only agent/harness complexity baseline |
| SWE-agent/SWE-ReX | ADOPT_PRIMITIVE | execution backend/session abstraction |
| Aider-AI/aider | ADOPT_PRIMITIVE | deterministic repository map/context ranking ideas |
| ifm-ai/xllm | STUDY_METHOD | local model lifecycle/runtime method mining |
| ifm-ai/horizon-post-train | STUDY_METHOD | post-training architecture/method mining |
| ifm-ai/uno | STUDY_METHOD | parallel/lossless-generation acceleration research |
| Tencent/AngelSlim | STUDY_METHOD | compression/speculative-decoding acceleration research |
| ggml-org/llama.cpp | REFERENCE_BASELINE | native local inference and acceleration baseline |
| unslothai/unsloth | REFERENCE_BASELINE | accelerated-training parity candidate |
| bigcode-project/selfcodealign | STUDY_METHOD | synthetic task/response/test generation and execution filtering |
| facebookresearch/swe-rl | STUDY_METHOD | software-evolution task/reward methodology |
| facebookresearch/ProgramBench | REFERENCE_BASELINE | behavioral reconstruction evaluation |
| microsoft/FEA-Bench | STUDY_METHOD | repository feature-implementation benchmark design; no dataset scraping admission |
| CodeClash-ai/CodeClash | STUDY_METHOD | long-horizon goal-oriented software-engineering evaluation |
| karpathy/autoresearch | REFERENCE_BASELINE | bounded propose-run-keep/discard/crash research controller |

The matrix is a plan, not evidence that any primitive has already been copied or adopted.

## 15. Upstream refresh and rollback

Source refreshes MUST be explicit repository changes. Every refresh MUST:

1. pin the newly observed revision;
2. diff the adopted upstream paths against the prior revision;
3. re-run license/NOTICE and transitive-dependency review;
4. re-run security and behavior/equivalence tests;
5. re-run local footprint/latency/RSS gates when the runtime path changes;
6. preserve the previous adopted revision as a rollback target;
7. update the SourceAdoptionRecord.

No source is auto-updated in production or during installation.

## 16. Dependency-ordered integration

This strategy does not reopen completed MSTR-000B work. It binds into remaining work as follows:

- `B031`: remains the existing three-seed ladder prerequisite; no source adoption changes its authority.
- `B032`: freezes the source-adoption/capability-mining design, SourceAdoptionRecord contract, anti-complexity baseline, execution-backend/checkpoint/improvement/context/parity records, and downstream MSTR-000A obligations.
- `B033`: red-teams hidden authority expansion, evaluator leakage, mutable-upstream dependencies, transitive assets, license/NOTICE loss, data/model permission conflation, dependency bloat, stale context indexes, checkpoint secret leakage, and rollback failure.
- `B034`: closes MSTR-000B only after these additions and all earlier gates are canonical.
- MSTR-000A successor tasks consume the frozen interfaces for harness runtime, resumability, self-improvement, and context management.

## 17. Definition of adoption done

A source-derived capability is not `ADOPTED_CANONICAL` until all of the following are true:

- immutable upstream revision recorded;
- SourceAdoptionRecord complete;
- exact source paths/method scope bounded;
- license/NOTICE/provenance retained;
- direct/transitive dependency surface reviewed;
- deterministic/offline/privacy behavior proven where required;
- equivalence/behavior tests pass;
- anti-complexity gate passes against the minimal baseline;
- independent review finds no unresolved blocker;
- mandatory premerge qualification succeeds on the exact head;
- canonical merge and postmerge verification succeed;
- any separate runtime/model/training/external-effect authority is independently satisfied.

Until then the capability remains research or a non-canonical candidate.

## 18. Canonical planning-base reconstruction

This amendment was reconstructed from exact canonical `main` `5e74e77c1fc86d4ebc7e64654f45bd18f565edd6` rather than rebasing or merging the stale planning branch. The prior research artifacts were treated as source material, all 18 upstream refs were reverified, and the five moved heads were repinned in the companion snapshot.

Completed B014-B030 history remains closed and unchanged. B031 retains its existing exact prerequisites and authority semantics. B032 is the first remaining task that may freeze these interfaces into downstream entry contracts; B033 independently red-teams them; B034 may close only after these obligations and all earlier canonical requirements are satisfied.

This planning amendment creates no model access, model execution, dataset admission, training, paid compute, external dispatch, or production-release authority.
