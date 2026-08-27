# MSTR Agent Instructions

## Read Order

Before changing the repository, read in this exact order:

1. `README.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. `docs/canonical/AGENT_HARNESS_AND_RESEARCH_LOOP_STRATEGY.md`
6. `docs/canonical/CODE_MODEL_SUPREMACY_STRATEGY.md`
7. the active `specs/<id>-*/spec.md`
8. that spec's `clarification-closeout.md`
9. `research.md`
10. `plan.md`
11. `data-model.md`
12. `contracts/README.md` and relevant schemas
13. `quickstart.md`
14. `checklists/implementation-readiness.md`
15. `tasks.md`
16. `implementation-handoff.md`

Do not reconstruct requirements from chat history when the canonical package answers the question.

## Mandatory Pre-Training Convergence

MSTR now has two interposed pre-training foundations:

```text
MSTR-000A = verified agent harness + Direction-to-Done foundation
MSTR-000B = code-model supremacy / backbone + data + curriculum + verifier-health foundation
```

The old blanket rule that all MSTR-000A implementation waits for T034 is superseded by exact task dependencies:

```text
EARLY_SAFE MSTR-000A A001-A018
  = may proceed when exact prerequisites are satisfied and no unqualified candidate result or external-effect authority is consumed

MSTR-000 T030-T034
  = continue under their own canonical task graph

MSTR-000B early-safe governance/backbone-metadata/data-contract work
  = may proceed when exact prerequisites are satisfied

CONVERGENCE
  = candidate-dependent A019-A024 / final tournament / training preflight require the stable product-aligned candidate pool and MSTR-000B prerequisites
```

No stale MSTR-000 or MSTR-000A task numbering may bypass MSTR-000B and jump to weight-changing training.

Canonical packages:
- `specs/001-agent-harness-verified-loop-foundation/`
- `specs/002-code-model-supremacy-foundation/`

## Machine Task Eligibility

MSTR-000B introduces a machine-readable task/dependency gate.

Once B002 is canonical, autonomous implementation agents MUST run the task eligibility validator before beginning a material task and MUST fail closed when it reports an unresolved prerequisite, supersession, missing authority, candidate-pool requirement, or material canonical-state drift.

The validator verifies existing authority; it never creates authority.

Until B002 is canonical, agents must manually apply the exact task prerequisites and may not use the absence of the validator as permission to bypass them.

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
TEACHER_OUTPUT != VERIFIED_TRUTH
TESTS_PASS != VERIFIER_HEALTH_BY_ITSELF
```

Live canonical GitHub truth overrides stale handoffs.

## Product Invariant

The primary MSTR release must remain usable on ordinary laptops without a discrete GPU or cloud account. Optional larger editions may exist, but they must never redefine the primary product into a workstation/cloud model.

```text
UNIVERSAL_LAPTOP_PRIMARY = REQUIRED
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CONTEXT = 8K
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
DISCRETE_GPU_REQUIREMENT = PROHIBITED
CLOUD_REQUIREMENT = PROHIBITED
ACCOUNT_REQUIREMENT = PROHIBITED
API_KEY_REQUIREMENT = PROHIBITED
OFFLINE_AFTER_INSTALL = REQUIRED
TELEMETRY_DEFAULT = OFF
```

Basic local coding assistance must not require Docker, Python, Node.js, or a developer toolchain merely to launch MSTR. Repository-specific build/test verification may require the toolchain that the repository itself requires.

## Primary Software-Building Objective

MSTR's primary optimization target is software engineering, not general assistant breadth.

```text
PRIMARY_PURPOSE = SOFTWARE_DIRECTION_TO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC
PRIMARY_EFFICIENCY_TARGET = VERIFIED_SOFTWARE_CAPABILITY_PER_GB
```

General reasoning remains a guardrail/capability only where it supports software planning, implementation, debugging, verification, and safe execution.

## Backbone Search Rule

Because MSTR is explicitly code-specialized, code-specialized base/foundation models MUST NOT be excluded merely for specialization. They compete under the same exact rights, provenance, Q4/runtime, tokenizer, trainability, raw-code, and universal-laptop gates as general foundations.

No named model is preselected. `JetBrains/Mellum-4b-base` is a mandatory rescan candidate because its omission demonstrates the old scan gap, not because it is assumed to win.

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

MSTR-000, MSTR-000A, and MSTR-000B are pre-training qualification/foundation workstreams. They may build the qualification harness, manifests, tests, fixtures, evidence, context experiments, loop/harness/environment/verifier infrastructure, task-gate infrastructure, metadata rescans, and training-signal contracts defined by their task graphs.

No task may infer authority for:

```text
NEW MODEL_WEIGHT_ACCESS OUTSIDE EXACT CANONICAL ENVELOPE
GATED_TERMS_ACCEPTANCE
PAID_MODEL_API_EXECUTION
RENTED_COMPUTE
LARGE_DATASET_INGESTION
WEIGHT_CHANGING_TRAINING
LONG_TRAINING
LARGE_SCALE_RL
PRODUCTION_RELEASE
```

unless the exact canonical task explicitly grants that authority and states scope/cost/resource ceilings where relevant.

MSTR-000A and MSTR-000B grant no weight-changing training authority.

## Training-Signal Integrity

Clean positive training data must satisfy stage-specific provenance, contamination, rights, and verifier-health gates.

MSTR-000B establishes:
- Data Constitution;
- software-evolution records;
- execution-filtered student self-alignment;
- bounded teacher rescue;
- checkpoint-relative difficulty/frontier curriculum;
- verifier-health records;
- test-generation and greenfield/feature curricula;
- multi-fidelity research promotion;
- Q4-in-the-loop regression.

Failed trajectories remain evidence. Contaminated/leaked/authority-violating examples fail closed. Teacher outputs do not bypass independent verification.

## Evidence Identity

Every material model/runtime result must bind evidence to exact identities where applicable:

- upstream model repository + immutable revision;
- weight/artifact checksum;
- tokenizer revision;
- quantization method and tool revision;
- runtime commit/version and build flags;
- OS, CPU, RAM, thread count and acceleration backend;
- context length and cache settings;
- prompt/tool/edit/loop contract version;
- task/benchmark manifest;
- verifier policy + verifier-health identity;
- seed/sampling config;
- data/difficulty identity for training evidence;
- result/failure classification;
- paid/resource cost if any.

A missing mandatory identity field invalidates the result for material direct comparison.

## Evaluation Discipline

Always report separately:

1. raw MSTR model quality;
2. MSTR with a neutral minimal harness;
3. MSTR with the MSTR-native harness where applicable;
4. MSTR + WePLD full-system results where applicable.

Do not claim model improvement from a harness-only gain.

The primary quality metric for direction-driven software work is verified completion rate. The primary speed metric is verified task completion latency, not tokens per second alone.

```text
PRIMARY_QUALITY = DVCR
DVCR = DIRECTION_TO_VERIFIED_COMPLETION_RATE
NORTH_STAR_SPEED = TTVC
TTVC = TIME_TO_VERIFIED_COMPLETION
```

DVCR and TTVC must be reported together. A fast failed run is not a successful TTVC result.

For long-horizon/multi-round claims also report repository-health effects where measurable. A model that repeatedly solves tasks by accumulating severe technical debt is not the best software builder.

For the universal-laptop release, whole-system usability matters: model RSS alone is insufficient. Measure MSTR alongside the reference OS/editor workload and reject sustained swap thrashing, OOM behavior, or severe interactive degradation.

## Implementation Discipline

For each task:

1. verify exact canonical base;
2. read task prerequisites and output paths;
3. run task eligibility validation once B002 is available;
4. create a focused branch;
5. implement the smallest compliant change;
6. add contract/unit/integration/security tests required by the task;
7. run focused and full applicable test gates;
8. record evidence;
9. update the task checkbox only when evidence exists and canonical closeout requirements are satisfied;
10. update canonical state only when the state actually changes;
11. open/review/merge without destructive history rewriting.

No force-push is required.

If no GitHub Actions run exists, do not claim CI PASS.
