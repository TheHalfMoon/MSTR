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

The primary MSTR release must remain usable on ordinary laptops without a discrete GPU. Optional larger editions may exist, but they must never redefine the primary product into a workstation/cloud model.

```text
UNIVERSAL_LAPTOP_PRIMARY = REQUIRED
DISCRETE_GPU_REQUIREMENT = PROHIBITED
CLOUD_REQUIREMENT = PROHIBITED
```

## Current phase

MSTR is in preconstruction. MSTR-000 exists to qualify the interaction contract and leading base/runtime choices before expensive training.

Until MSTR-000 closes:

```text
BACKBONE_SELECTION = PROHIBITED
LONG_TRAINING = PROHIBITED
LARGE_DATASET_INGESTION = PROHIBITED
MODEL_WEIGHT_ADMISSION = NONE
PRODUCTION_RELEASE_CLAIMS = PROHIBITED
```

Small, bounded, reversible experiments may be planned only when they are explicitly listed in MSTR-000 and do not imply final backbone selection.

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
