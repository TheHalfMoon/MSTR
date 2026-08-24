# MSTR Agent Instructions

## Read order

Before changing the repository, read in this order:

1. `README.md`
2. `docs/canonical/CURRENT_STATE.md`
3. the active `specs/<id>-*/spec.md`
4. that spec's `research.md`
5. `plan.md`
6. `tasks.md`
7. `checklists/implementation-readiness.md`

## Canonical authority

GitHub `main` is the canonical repository state. A branch, pull request, model output, benchmark score, external consultation, or local experiment is evidence only until its result is explicitly recorded and merged through the governed workflow.

```text
MODEL_OUTPUT != PROJECT_AUTHORITY
BENCHMARK_SCORE != BACKBONE_SELECTION
PUBLIC_LEADERBOARD != MSTR_TRUTH
HARNESS_GAIN != MODEL_GAIN
```

## Product invariant

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

## License and distribution invariant

A primary backbone must permit the intended worldwide use and redistribution of MSTR. Before any candidate is admitted for weight-access qualification, record the exact upstream revision and verify rights for at least:

- personal and commercial use;
- modification and fine-tuning;
- quantization/conversion;
- redistribution of derivative weights/artifacts;
- publication of the intended MSTR release without requiring every user to obtain a separate provider account or commercial license.

Research-only, non-commercial-only, or otherwise incompatible weights may be used only as explicitly labeled research references when separately authorized. They cannot become the primary MSTR backbone.

Teacher/API output terms, datasets, runtime dependencies, and quantization tooling must be checked separately; a permissive base-model license does not make the whole training/distribution chain permissive.

## Current phase and weight authority

MSTR is in preconstruction. MSTR-000 exists to qualify the interaction contract and leading base/runtime choices before expensive training.

Before the MSTR-000 planning package is canonical:

```text
MODEL_WEIGHT_DOWNLOAD = PROHIBITED
PAID_MODEL_API_EXECUTION = PROHIBITED
RENTED_TRAINING_COMPUTE = PROHIBITED
```

After MSTR-000 becomes canonical, only an explicit MSTR-000 task may authorize bounded candidate-weight access. Such access must be pinned, checksummed, reversible, and limited to qualification. It does **not** constitute final backbone/product admission.

Until MSTR-000 closes:

```text
FINAL_BACKBONE_ADMISSION = PROHIBITED
LONG_TRAINING = PROHIBITED
LARGE_DATASET_INGESTION = PROHIBITED
LARGE_SCALE_RL = PROHIBITED
PRODUCTION_RELEASE_CLAIMS = PROHIBITED
```

Any task requiring paid API usage or rented compute must state its cost ceiling before execution.

## Evidence identity

Every material model/runtime result must bind evidence to exact identities where applicable:

- upstream model repository + revision/commit;
- weight/artifact checksum;
- tokenizer revision;
- quantization method and tool revision;
- runtime commit/version and build flags;
- OS, CPU, RAM, thread count and acceleration backend;
- context length and cache settings;
- prompt/tool/edit contract version;
- task manifest and seed.

## Evaluation discipline

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

For the universal-laptop release, whole-system usability matters: model RSS alone is insufficient. Measure the model alongside the reference OS/editor workload and reject sustained swap thrashing, OOM behavior, or severe interactive degradation.
