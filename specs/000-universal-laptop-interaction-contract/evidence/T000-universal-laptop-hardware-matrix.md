# T000 — Universal Laptop Reference Hardware / OS Matrix

**Task:** MSTR-000 / T000  
**Status:** COMPLETE_CANDIDATE  
**Authority:** Qualification definition only; this document does not claim measured performance or final platform support.  
**Canonical base:** `5a898420286f833caff4edd54d902cfaf10ccb13`

## 1. Decision

MSTR will qualify the primary release against a **whole-laptop** envelope rather than a model-only memory envelope.

The first mandatory qualification tier is an 8 GB laptop with no discrete GPU, an ordinary editor open on a medium repository, and an 8K model context. A model that merely loads while exhausting the machine is not considered usable.

```text
UNIVERSAL_PRIMARY_TIER = U1
TOTAL_RAM = 8_GB
DISCRETE_GPU = ABSENT
CPU_ONLY = REQUIRED
REFERENCE_CONTEXT = 8192_TOKENS
CONTEXT_LADDER = 4096 / 8192 / 16384
PRIMARY_Q4_ARTIFACT_TARGET = <= 3_GB
MSTR_PROCESS_RSS_SOFT_TARGET = <= 4_GB_AT_8K
WHOLE_LAPTOP_RESPONSIVENESS = REQUIRED
SUSTAINED_SWAP_THRASHING = FAIL
```

These are **qualification targets**. T060 will freeze the final measured support floor after real candidate/runtime evidence exists.

## 2. Terms

### Qualification floor

The machine classes MSTR must test before the primary release can claim broad laptop availability.

### Final support floor

The lowest hardware/OS configuration actually proven by measurements. It is not established by T000; it is frozen at MSTR-000 closeout (T060).

### Required lane

A platform family that must be proven for the primary release or explicitly blocked from release with no misleading compatibility claim.

### Characterization lane

A useful lower-priority/legacy platform that MSTR will measure where practical, but whose failure does not automatically block the primary release.

## 3. Memory / context tiers

| Tier | Role | Total RAM | Default test context | GPU requirement | Status |
|---|---|---:|---:|---|---|
| U0 | stretch / low-memory characterization | 4 GB | 4K | none | non-blocking characterization |
| U1 | **universal primary qualification** | **8 GB** | **8K** | **none** | mandatory gate |
| U2 | recommended headroom | 16 GB | 16K | none | mandatory secondary characterization |
| U3 | optional accelerated | >=16 GB | 16K+ as measured | optional GPU/NPU | bonus only; may not redefine primary |

Rules:

1. U1 is the release-defining tier.
2. U0 exists because a genuinely useful 4 GB path would materially broaden access; failure at U0 does not invalidate U1.
3. U2 must use the same primary model family/artifact class; it is not permission to replace the universal model with a larger workstation model.
4. U3 acceleration is optional. Any CUDA/Metal/Vulkan/NPU benefit is reported separately from the CPU-only gate.
5. Vendor maximum-context claims do not define MSTR usability. 4K/8K/16K are the first reproducible ladder; larger contexts may be characterized later.

## 4. Required platform qualification lanes

### P1 — Windows x86_64 — REQUIRED

```text
OS_FAMILY = CURRENT_VENDOR_SUPPORTED_WINDOWS_64_BIT_AT_TEST_TIME
CPU = X86_64
RAM = 8_GB_U1
DISCRETE_GPU = NONE_REQUIRED
RUNTIME = NATIVE_PORTABLE_CPU_PATH_REQUIRED
```

The exact Windows release/build, CPU model, ISA features, power mode, and runtime binary must be pinned in measurement evidence.

An AVX2-capable machine is the **primary x86_64 performance reference** because it represents a broad modern laptop class. If the selected runtime offers a non-AVX2 compatibility path, T001/T022 must characterize it separately rather than silently treating AVX2 as the final support floor.

### P2 — Linux x86_64 — REQUIRED

```text
OS_FAMILY = CURRENT_SUPPORTED_LTS_REFERENCE_AT_TEST_TIME
CPU = X86_64
RAM = 8_GB_U1
DISCRETE_GPU = NONE_REQUIRED
RUNTIME = PORTABLE_CPU_PATH_REQUIRED
```

Use one pinned mainstream LTS distribution as the reproducible reference lane. Additional distributions may be smoke-tested, but the primary release should avoid unnecessary distro-specific dependencies.

### P3 — macOS arm64 — REQUIRED

```text
OS_FAMILY = CURRENT_VENDOR_SUPPORTED_MACOS_AT_TEST_TIME
CPU = APPLE_SILICON_ARM64
MINIMUM_REFERENCE_CLASS = M1_CLASS
RAM = 8_GB_UNIFIED_MEMORY_U1
DISCRETE_GPU = NONE_REQUIRED
RUNTIME = CPU_PATH_REQUIRED
METAL = OPTIONAL_ACCELERATION
```

Metal results are reported separately; CPU-only/basic operation must remain identifiable so acceleration is not mistaken for the universal requirement.

## 5. Secondary / characterization platform lanes

| Lane | Platform | Priority | Rule |
|---|---|---|---|
| P4 | Windows arm64 | secondary | characterize if portable runtime is mature; no primary launch claim without evidence |
| P5 | Linux arm64 | secondary | characterize on a real laptop-class ARM64 device where available |
| P6 | macOS x86_64 / Intel | legacy characterization | test only if supported by chosen runtime/toolchain; do not promise before evidence |
| P7 | x86_64 without AVX2 | compatibility characterization | test if runtime provides a viable path; publish severe performance limits plainly |

No unsupported lane may be generalized into "all laptops" marketing.

## 6. CPU reference classes

MSTR will record exact CPU models in every performance result. T000 does not declare a final CPU-generation cutoff.

### C1 — Primary x86_64 performance class

- laptop-class x86_64 CPU;
- at least 4 physical cores or equivalent modern mobile configuration;
- AVX2 available for the primary performance lane;
- no discrete GPU required;
- balanced/normal power mode for interactive measurements;
- exact thread count and runtime thread configuration recorded.

### C2 — Apple Silicon baseline

- M1-class 8 GB Apple Silicon as the earliest mandatory macOS arm64 reference class;
- exact SoC and core configuration recorded;
- CPU and optional Metal results separated.

### C3 — Reduced-ISA / older CPU characterization

Where the runtime permits it, test lower-ISA x86_64 separately. This lane is intended to discover whether MSTR can broaden compatibility; it must not be used to depress the main quality/latency standard for U1.

## 7. Reference concurrent editor workload

The universal-laptop test must not run MSTR on an otherwise empty machine.

### E1 — Required baseline editor workload

Use a pinned **VS Code Stable** build (or the same pinned compatible build across required OS lanes where necessary) with:

- third-party extensions disabled;
- built-in Git/file services allowed;
- one medium reference repository open;
- initial indexing/file discovery allowed to settle before warm measurements;
- no cloud AI extension running;
- editor process kept open throughout MSTR memory/latency measurements.

The exact editor version and baseline memory footprint must be recorded by T001/T022.

### E2 — Heavy-editor characterization

A JetBrains-class IDE workload should be characterized later as a secondary, non-blocking lane because many real developers use heavier IDEs. It is not the U1 reproducibility baseline.

MSTR itself must remain editor-agnostic; these workloads exist only to model real concurrent laptop pressure.

## 8. Reference repository workload classes

T000 defines repository *classes*; T005 later freezes exact benchmark repositories/tasks.

### R0 — small

- approximately 10K–50K source LOC;
- approximately 100–500 tracked source/config/test files.

### R1 — medium — U1 reference class

- approximately 100K–500K source LOC;
- approximately 1,000–5,000 tracked source/config/test files;
- multiple directories/modules;
- Git repository;
- realistic tests/build metadata, but no build/test process running during idle memory baseline.

### R2 — large characterization

- >500K source LOC or >5,000 tracked source/config/test files;
- used to measure index growth and retrieval degradation, not to redefine the 8 GB minimum.

T005 must choose exact clean repositories and commit SHAs satisfying these classes.

## 9. Storage / installation qualification

Provisional U1 storage envelope:

```text
PRIMARY_MODEL_ARTIFACT <= 3_GB
FREE_DISK_BEFORE_INSTALL >= 6_GB_PROVISIONAL
USER_SIDE_MODEL_CONVERSION = NOT_REQUIRED
BUILD_FROM_SOURCE = NOT_REQUIRED_FOR_BASIC_USE
```

The 6 GB free-disk value is a qualification allowance, not the final packaged size. T002/T061 will freeze the actual installer/runtime/cache budget. Repository contents and repository-specific build dependencies are outside the MSTR installer size, but MSTR-created indexes/caches must be measured separately and bounded.

## 10. Power / thermal conditions

For repeatability:

- primary performance runs use normal/balanced power mode with the laptop connected to AC power;
- a sustained CPU run must be included to reveal throttling rather than reporting only burst speed;
- battery-mode and energy-per-task measurements are characterization metrics where reliable counters are available;
- no overclocked/high-performance-only configuration may be the sole evidence for U1.

T001 defines exact durations and metrics.

## 11. U1 pass/fail semantics

A candidate/runtime can pass the U1 hardware gate only if later measurement proves all of the following on every required P1/P2/P3 lane or an explicitly approved scoped exception exists:

1. primary Q4-class model artifact meets the size gate or a founder-approved revision is recorded;
2. model/runtime can launch without a discrete GPU;
3. 8K reference context can be used without OOM;
4. process RSS is measured against the <=4 GB soft target;
5. OS + E1 editor + MSTR remain usable together;
6. no sustained swap thrashing occurs under the T001 definition;
7. editor interaction does not become severely degraded under the T001 responsiveness definition;
8. CPU inference completes the required smoke/task workload rather than merely loading;
9. offline local use does not require a provider account/API key;
10. any optional acceleration is reported separately from the CPU-only result.

The `<=4 GB` process RSS value is a **soft design target**, not a loophole: exceeding it requires whole-system evidence and explicit review. The final hard memory threshold is T060's responsibility.

## 12. Evidence schema required for later measurements

Every hardware result must include at least:

```text
OS_NAME
OS_VERSION_BUILD
CPU_MODEL
CPU_ARCH
CPU_ISA_FEATURES_RELEVANT_TO_RUNTIME
PHYSICAL_CORES
LOGICAL_THREADS
TOTAL_RAM
POWER_MODE
GPU_NPU_PRESENT_AND_USED
EDITOR_NAME_VERSION
EDITOR_BASELINE_RSS
REFERENCE_REPO_ID_AND_COMMIT
MODEL_ID_AND_REVISION
MODEL_ARTIFACT_SHA256
QUANTIZATION_RECIPE_TOOL_VERSION
RUNTIME_VERSION_COMMIT_BUILD_FLAGS
RUNTIME_THREADS
CONTEXT_LENGTH
KV_CACHE_FORMAT_IF_CONFIGURABLE
PROMPT_CONTRACT_VERSION
PROCESS_PEAK_RSS
SYSTEM_AVAILABLE_MEMORY_MINIMUM
SWAP_PAGEFAULT_METRICS
COLD_LOAD_TIME
TTFA
TOKENS_PER_SECOND
SOURCE_CODE_CHARACTERS_PER_SECOND
SUSTAINED_RUN_DURATION
THERMAL_OR_THROTTLING_OBSERVATION
```

T001 will define the exact collection procedure and pass/fail thresholds for dynamic measurements.

## 13. What T000 does not prove

T000 does **not** prove:

- that any current candidate fits U1;
- that MSTR works on every Windows/Linux/macOS machine;
- a final CPU generation/ISA minimum;
- a final installer size;
- performance, TTFA, TTVC, or energy claims;
- that 8K is the final optimal context;
- that 4 GB laptops are supported.

Those require later MSTR-000 evidence.

## 14. T000 result

```text
T000_RESULT = PASS
REFERENCE_MATRIX = DEFINED
PRIMARY_TIER = U1_8GB_CPU_ONLY_8K
REQUIRED_PLATFORM_LANES = WINDOWS_X86_64 + LINUX_X86_64 + MACOS_ARM64
STRETCH_TIER = U0_4GB_4K_CHARACTERIZATION
RECOMMENDED_TIER = U2_16GB_16K
OPTIONAL_ACCELERATION = NON_BLOCKING
FINAL_SUPPORT_FLOOR = UNFROZEN_UNTIL_T060
MODEL_WEIGHT_ACCESS = NONE
NEXT_TASK = T001_MEASUREMENT_PROCEDURES
```
