# MSTR Agent Instructions

## Read Order

Before changing the repository, read in this exact order:

1. `README.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. the active `specs/<id>-*/spec.md`
6. that spec's `clarification-closeout.md`
7. `research.md`
8. `plan.md`
9. `data-model.md`
10. `contracts/README.md` and relevant schemas
11. `quickstart.md`
12. `checklists/implementation-readiness.md`
13. `tasks.md`
14. `implementation-handoff.md`

Do not reconstruct requirements from chat history when the canonical package answers the question.

## Spec Kit Workflow

MSTR uses Spec-Driven Development.

For every buildable workstream:

```text
constitution
-> spec
-> clarification closeout
-> research
-> plan
-> data model/contracts/quickstart
-> tasks
-> consistency review
-> implementation
-> convergence/closeout
```

`spec.md` owns what must be true.  
`plan.md` owns how the active workstream is technically executed.  
`tasks.md` is the executable work queue.  
The constitution is a blocking governance layer over all three.

Do not skip from a broad idea directly to implementation when a Spec Kit gate is unresolved.

## Canonical Authority

GitHub `main` is the canonical repository state. A branch, pull request, model output, benchmark score, external consultation, or local experiment is evidence only until its result is explicitly recorded and merged through the governed workflow.

```text
MODEL_OUTPUT != PROJECT_AUTHORITY
BENCHMARK_SCORE != BACKBONE_SELECTION
PUBLIC_LEADERBOARD != MSTR_TRUTH
HARNESS_GAIN != MODEL_GAIN
```

Live canonical GitHub truth overrides stale handoffs.

## Product Invariant

The primary MSTR release must remain usable on ordinary laptops without a discrete GPU or cloud account. Optional larger editions may exist, but they must never redefine the primary product into a workstation/cloud model.

```text
UNIVERSAL_LAPTOP_PRIMARY = REQUIRED
DISCRETE_GPU_REQUIREMENT = PROHIBITED
CLOUD_REQUIREMENT = PROHIBITED
ACCOUNT_REQUIREMENT = PROHIBITED
API_KEY_REQUIREMENT = PROHIBITED
OFFLINE_AFTER_INSTALL = REQUIRED
TELEMETRY_DEFAULT = OFF
```

Basic local coding assistance must not require Docker, Python, Node.js, or a developer toolchain merely to launch MSTR. Repository-specific build/test verification may require the toolchain that the repository itself requires.

## License and Distribution Invariant

A primary backbone must permit the intended worldwide use and redistribution of MSTR. Before candidate weight access, record the exact upstream revision and fail closed on rights for:

- personal and commercial use;
- modification and fine-tuning;
- quantization/conversion;
- redistribution of derivative weights/artifacts;
- publication of the intended MSTR release without forcing every end user to obtain a separate provider account or commercial license.

Research-only, non-commercial-only, or otherwise incompatible weights may be used only as explicitly labeled research references when separately authorized. They cannot become the primary MSTR backbone.

Teacher/API output terms, datasets, runtime dependencies, tokenizer/vision components, and quantization tooling must be checked separately; a permissive base-model license does not make the whole training/distribution chain permissive.

## Current Phase and External-Effect Authority

MSTR-000 is preconstruction/qualification. It may build the qualification harness, manifests, tests, fixtures, evidence, context experiments, and verifier/environment MVP defined by its task graph.

No task may infer authority for:

```text
MODEL_WEIGHT_ACCESS
GATED_TERMS_ACCEPTANCE
PAID_MODEL_API_EXECUTION
RENTED_COMPUTE
LARGE_DATASET_INGESTION
LONG_TRAINING
LARGE_SCALE_RL
PRODUCTION_RELEASE
```

unless the exact canonical task explicitly grants that authority and states scope/cost/resource ceilings where relevant.

Until MSTR-000 closes:

```text
FINAL_BACKBONE_ADMISSION = PROHIBITED_BEFORE_EVIDENCE
LONG_TRAINING = PROHIBITED
LARGE_DATASET_INGESTION = PROHIBITED
LARGE_SCALE_RL = PROHIBITED
PRODUCTION_RELEASE_CLAIMS = PROHIBITED
```

## Evidence Identity

Every material model/runtime result must bind evidence to exact identities where applicable:

- upstream model repository + immutable revision;
- weight/artifact checksum;
- tokenizer revision;
- quantization method and tool revision;
- runtime commit/version and build flags;
- OS, CPU, RAM, thread count and acceleration backend;
- context length and cache settings;
- prompt/tool/edit contract version;
- task/benchmark manifest;
- verifier policy;
- seed/sampling config;
- result/failure classification;
- paid/resource cost if any.

A missing mandatory identity field invalidates the result for material direct comparison.

## Evaluation Discipline

Always report separately:

1. raw MSTR model quality;
2. MSTR with a neutral minimal harness;
3. the full optimized MSTR system.

Do not claim model improvement from a harness-only gain.

The primary speed metric is verified task completion latency, not tokens per second alone.

```text
NORTH_STAR_SPEED = TTVC
TTVC = TIME_TO_VERIFIED_COMPLETION
```

For the universal-laptop release, whole-system usability matters: model RSS alone is insufficient. Measure MSTR alongside the reference OS/editor workload and reject sustained swap thrashing, OOM behavior, or severe interactive degradation.

## Implementation Discipline

For each task:

1. verify exact canonical base;
2. read task prerequisites and output paths;
3. create a focused branch;
4. implement the smallest compliant change;
5. add contract/unit/integration/security tests required by the task;
6. run focused and full applicable test gates;
7. record evidence;
8. update the task checkbox only when evidence exists;
9. update canonical state only when the state actually changes;
10. open/review/merge without destructive history rewriting.

No force-push is required.

If no GitHub Actions run exists, do not claim CI PASS.
