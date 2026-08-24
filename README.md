# MSTR

MSTR is an independent research and engineering project for building an **extremely capable software-engineering model that ordinary people can run locally on an ordinary laptop**.

## Primary product constraint

MSTR is not allowed to become a cloud-only or workstation-only model. The primary release must target broad laptop availability:

```text
PRIMARY_MODE = LOCAL / OFFLINE-CAPABLE
DISCRETE_GPU_REQUIRED = NO
REFERENCE_RAM = 8_GB
REFERENCE_CPU = MODERN_X86_64_OR_ARM64
PRIMARY_QUANT = Q4_CLASS
PRIMARY_DOWNLOAD_TARGET = <= 3_GB
PRIMARY_RUNTIME_WORKING_SET_TARGET = <= 6_GB_AT_BOUNDED_CONTEXT
WINDOWS = REQUIRED
LINUX = REQUIRED
MACOS = REQUIRED
```

These are product qualification targets, not claims already proven.

MSTR may later publish stronger optional editions, but the universal-laptop release remains the primary product and may not be treated as a degraded afterthought.

## Current phase

MSTR begins in **preconstruction**. No backbone is selected, no model weights are admitted, and no long training run is authorized.

The first governed workstream is **MSTR-000 — Universal Laptop Interaction Contract + Base/Local/Speed Qualification**. Its purpose is to empirically freeze the coupled model/runtime/tool/edit contract before serious training compute is spent.

```text
PROJECT_PHASE = PRECONSTRUCTION
PRIMARY_PARAMETER_CLASS = 2B_TO_4B_DENSE_CANDIDATES
BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
LONG_TRAINING = NOT_STARTED
MODEL_WEIGHT_ADMISSION = NONE
MSTR_000 = ACTIVE_PLANNING_CANDIDATE
```
