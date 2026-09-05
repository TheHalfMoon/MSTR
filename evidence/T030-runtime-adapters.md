# T030 Portable CPU Runtime Adapter Evidence

**Task:** `T030`

**Canonical reconciliation base:** `226609e3a29a5e5d038bbd0e9c744f3ff2877112`

**Historical source PR:** `#96`

**Historical source head:** `b4adce223a9a5c833f2c2392d742cb93bdad0ba3`

**State:** `CURRENT_MAIN_RECONCILIATION / IMPLEMENTATION_CANDIDATE / QUALIFICATION_PENDING / NOT_COMPLETE_CANONICAL`

## Entry Gate

Canonical `docs/canonical/PROGRAM_ROADMAP.md` treats MSTR-000 T030-T034 as a parallel candidate/runtime qualification branch. T029 is now `COMPLETE_CANONICAL`. T030 is model-independent adapter infrastructure only: this reconciliation consumes the canonical T023 runtime protocol but performs no T031 measurement, model inference, artifact acquisition, conversion, quantization, or other model execution.

```text
T029 = COMPLETE_CANONICAL
T023_RUNTIME_PROTOCOL = CANONICAL
MODEL_WEIGHT_ACCESS_BY_T030 = NONE
MODEL_EXECUTION_BY_T030 = NONE
PAID_COMPUTE = NONE
PRODUCTION_RELEASE = NONE
```

PR #96 is retained as historical evidence only. Its branch diverged from current main and is not merge-authorized. This candidate reconstructs the still-valid nine-file T030 implementation directly on exact current main rather than rebasing or merging the stale branch.

## Reconciled Surface

```text
src/mstr_qualify/runtimes/benchmark_cli.py
src/mstr_qualify/runtimes/__init__.py
configs/runtimes/llama-cpp-cpu.json
artifacts/decisions/T030-runtime-interface-scan.json
tests/unit/test_runtime_benchmark_cli.py
tests/security/test_runtime_benchmark_boundary.py
tests/security/test_runtime_profile_alias_boundary.py
tests/integration/test_runtime_adapters.py
evidence/T030-runtime-adapters.md
```

The implementation is intentionally model-independent and preserves the historical security hardening that remained compatible with current T023 and identifier interfaces.

The adapter:

- keeps `LoadRequest` identity-only; artifact location remains an environment/caller input;
- verifies local artifact SHA-256 against the exact load identity before entering `READY`;
- performs no artifact acquisition;
- rejects Hugging Face provider-acquisition flags and llama.cpp RPC flags, including `--flag=value` forms;
- requires exactly one runtime device selector across the complete generated CLI token set and requires it to be `none`;
- forces `n_gpu_layers=0` and `--device none` for the portable CPU path;
- binds prompt/generation token counts, thread count, GPU-layer count, device selection, model filename, and runtime build commit to returned JSON before accepting a result;
- rejects non-finite or non-positive timing evidence;
- exposes stable fail-closed errors for artifact, process, profile, and output failures;
- represents isolated benchmark processes as `supports_prefix_cache=false` with `PrefixCacheState.EMPTY` rather than inventing reusable cache state;
- retains a verified benchmark observation structure for later T031 plumbing without authorizing or performing T031 execution.

## Security Boundary

The historical review discovered a cross-field CLI alias path where device-selector validation could have covered only `output_args`. The retained hardened implementation validates the complete generated `command_tokens` tuple. Dedicated regression coverage injects both `-dev` and `--device` through all non-output CLI argument fields and requires rejection.

```text
model_arg
prompt_arg
generation_arg
threads_arg
gpu_layers_arg
repetitions_arg
```

Provider acquisition and RPC paths are also prohibited by profile validation. This candidate contains no network operation and no runtime acquisition operation.

## llama.cpp Interface Reverification

Official upstream evidence was reverified on 2026-09-05 at the exact historical pin:

```text
repository = https://github.com/ggml-org/llama.cpp
revision   = 3173a56471c1753650cd806694145ffd6dcace67
interfaces = tools/llama-bench/README.md
             tools/llama-bench/llama-bench.cpp
```

The pinned interface documents or implements:

```text
-m / --model
-p / --n-prompt
-n / --n-gen
-t / --threads
-ngl / --n-gpu-layers
-dev / --device
-r / --repetitions
-rpc / --rpc
-o / --output json
```

Pinned source still proves `device=none` is accepted and serialized as `devices=none`, and exposes the identity/measurement fields consumed by the adapter, including `build_commit`, `model_filename`, `n_prompt`, `n_gen`, `n_threads`, `n_gpu_layers`, `devices`, `avg_ns`, and `avg_ts`.

The repository profile supplies:

```text
-ngl 0
--device none
-r 1
-o json
```

A returned result that does not prove requested token/thread/GPU/device/model/build identities fails closed.

## llamafile Disposition Reverification

The latest published `mozilla-ai/llamafile` release remains `0.10.5` as reverified on 2026-09-05. Current repository code search for `llamafile-bench` returned zero matches. The prior disposition therefore remains:

```text
DEFERRED_INTERFACE_NOT_PROVEN
```

No guessed adapter or compatibility result is created.

## Test Boundary

The T030 tests use temporary synthetic bytes and injected deterministic command runners only. They do not download or execute model weights, require a real runtime binary, or access the network.

Focused assertions include:

```text
LOCAL_ARTIFACT_SHA_MISMATCH -> REJECT
FORMAT_OR_CONTEXT_UNSUPPORTED -> REJECT
CPU_ONLY_COMMAND -> -ngl 0 + --device none
RPC_OR_PROVIDER_NETWORK_FLAGS -> REJECT
DUPLICATE_OR_NON_NONE_DEVICE_SELECTOR -> REJECT
CROSS_FIELD_DEVICE_SELECTOR_ALIAS -> REJECT
PREFIX_CACHE_REUSE -> FALSE / EMPTY
NONZERO_PROCESS -> STABLE_FAILURE
MALFORMED_JSON -> STABLE_FAILURE
NONFINITE_OR_ZERO_MEASUREMENT -> REJECT
RESULT_TOKEN_THREAD_GPU_DEVICE_IDENTITY_MISMATCH -> REJECT
MODEL_OR_RUNTIME_BUILD_IDENTITY_MISMATCH -> REJECT
VALID_PINNED_RESULT -> ACCEPT
```

## Qualification Boundary

Historical PR #96 qualification attempts remain immutable infrastructure evidence only because its hosted jobs failed before executing repository gates. They do not transfer to this candidate.

The first current-main qualification attempt was also not a PASS:

```text
RUN = 33969313680
TARGET_HEAD = 67a0842c24fe1e7d0732626d5decce13badf5223
IDENTITY_SCOPE = FAILURE
CAUSE = git diff --check rejected four Markdown trailing-whitespace hard breaks in this evidence file
QUALITY = SUCCESS
FINAL_QUALIFICATION = SKIPPED
DISPOSITION = NEGATIVE CANDIDATE EVIDENCE / SUPERSEDED BY FORMATTING REPAIR
```

That run did execute and pass focused T030 tests, offline validation, full pytest, Ruff, and mypy, but its results do not transfer to the repaired head. Fresh qualification must bind the exact repaired head and execute all gates again.

```text
T030_FOCUSED_TESTS = REQUIRED_ON_REPAIRED_HEAD
MSTR_QUALIFY_VALIDATE = REQUIRED_ON_REPAIRED_HEAD
FULL_PYTEST = REQUIRED_ON_REPAIRED_HEAD
RUFF = REQUIRED_ON_REPAIRED_HEAD
MYPY = REQUIRED_ON_REPAIRED_HEAD
EXACT_HEAD_SCOPE_AND_IDENTITY = REQUIRED_ON_REPAIRED_HEAD
INDEPENDENT_SUBSTANTIVE_REVIEW = REQUIRED
MANDATORY_PREMERGE = REQUIRED
POSTMERGE_VERIFICATION = REQUIRED
T030_COMPLETE_CANONICAL = NO_UNTIL_GOVERNED_CLOSEOUT
```

No PASS is claimed in this file for the repaired head before those gates complete.

## Authority Boundary

```text
NEW_MODEL_WEIGHT_ACCESS = NONE
MODEL_INFERENCE = NONE
RUNTIME_MODEL_EXECUTION = NONE
CONVERSION_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PRODUCTION_RELEASE = NONE
B012_AUTHORITY = NONE
T031_EXECUTION_AUTHORITY = NONE_INFERRED_BY_T030
```

T030 implementation and qualification do not authorize T031 model/runtime measurements. Any later external execution remains separately governed by exact current authority and artifact/runtime/hardware identity.
