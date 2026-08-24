# MSTR

MSTR is an independent research and engineering project for building an **extremely capable software-engineering model that ordinary people can install and run locally on an ordinary laptop**.

## Primary product invariant

MSTR is not allowed to become a cloud-only or workstation-only model. The universal-laptop release is the primary product, not a degraded afterthought.

```text
PRIMARY_MODE = LOCAL / OFFLINE-CAPABLE
DISCRETE_GPU_REQUIRED = NO
ACCOUNT_REQUIRED = NO
API_KEY_REQUIRED = NO
REFERENCE_TOTAL_RAM = 8_GB
REFERENCE_CPU = MODERN_X86_64_OR_ARM64
PRIMARY_QUANT = Q4_CLASS
PRIMARY_DOWNLOAD_TARGET = <= 3_GB
REFERENCE_CONTEXT = 8192_TOKENS
CONTEXT_LADDER = 4096 / 8192 / 16384
MSTR_PROCESS_RSS_SOFT_TARGET = <= 4_GB_AT_REFERENCE_CONTEXT
WHOLE_LAPTOP_USABILITY = REQUIRED
BASIC_MODE_DOCKER_REQUIRED = NO
WINDOWS = REQUIRED
LINUX = REQUIRED
MACOS = REQUIRED
OFFLINE_AFTER_INSTALL = REQUIRED
TELEMETRY_DEFAULT = OFF
```

These are qualification targets, not performance claims already proven. MSTR-000 must replace provisional values with measured limits and an explicit OS/CPU support matrix.

The 8 GB gate is a **whole-laptop** gate: MSTR must remain usable while a reference editor and operating system are running. Model-only RAM measurements are insufficient, and sustained swap thrashing is a failure.

MSTR may later publish stronger optional editions, but the universal-laptop release remains the primary product and its hardware floor may not be silently raised.

## Distribution principle

The primary MSTR release must be usable without a provider login, API key, subscription, or network connection after installation. Its backbone and distribution chain must permit the intended use, modification, quantization, and redistribution of derivative artifacts.

## Current phase

MSTR begins in **preconstruction**. No final backbone is selected, no model weights are currently authorized for download by the planning candidate, and no long training run is authorized.

The first governed workstream is **MSTR-000 — Universal Laptop Interaction Contract + Base/Local/Speed Qualification**. Its purpose is to empirically freeze the coupled model/runtime/tool/edit/distribution contract before serious training compute is spent.

```text
PROJECT_PHASE = PRECONSTRUCTION
PRIMARY_PARAMETER_CLASS = APPROX_2B_TO_4B_DENSE_CANDIDATES
LOWER_BOUND_CONTROL = APPROX_1_5B
BACKBONE = UNSELECTED
INTERACTION_CONTRACT = UNFROZEN
DISTRIBUTION_CONTRACT = UNFROZEN
LONG_TRAINING = NOT_STARTED
FINAL_MODEL_WEIGHT_ADMISSION = NONE
MSTR_000 = ACTIVE_PLANNING_CANDIDATE
```
