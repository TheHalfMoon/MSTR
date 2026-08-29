# T030 Portable CPU Runtime Adapter Evidence

**Task:** `T030`  
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`  
**State:** `IMPLEMENTATION_ACTIVE / QUALIFICATION_PENDING`

## Entry Gate

Canonical `docs/canonical/PROGRAM_ROADMAP.md` treats MSTR-000 T030-T034 as a parallel candidate/runtime qualification branch. This implementation is model-independent adapter infrastructure only. It consumes the canonical T023 runtime protocol and does not consume a T029 model result, perform T031 measurement, or infer T029 completion.

```text
T022 = COMPLETE_CANONICAL
T023_RUNTIME_PROTOCOL = CANONICAL
MODEL_WEIGHT_ACCESS_BY_T030_IMPLEMENTATION = NONE
MODEL_EXECUTION_BY_T030_IMPLEMENTATION = NONE
PAID_COMPUTE = NONE
PRODUCTION_RELEASE = NONE
```

## Implemented Surface

T030 adds a profile-driven `BenchmarkCliRuntimeAdapter` that implements the T023 lifecycle against an already-installed local benchmark CLI and an already-present local model artifact.

Files:

```text
src/mstr_qualify/runtimes/benchmark_cli.py
src/mstr_qualify/runtimes/__init__.py
configs/runtimes/llama-cpp-cpu.json
artifacts/decisions/T030-runtime-interface-scan.json
tests/unit/test_runtime_benchmark_cli.py
tests/security/test_runtime_benchmark_boundary.py
tests/integration/test_runtime_adapters.py
```

The adapter:

- keeps `LoadRequest` identity-only; artifact location remains an environment/caller input;
- verifies the local artifact SHA-256 against the exact load identity before entering `READY`;
- performs no artifact acquisition;
- rejects Hugging Face provider-acquisition flags and llama.cpp RPC flags in runtime profiles, including `--flag=value` forms;
- requires exactly one runtime device selector and requires it to be `none`;
- forces `n_gpu_layers=0` and `--device none` for the portable CPU path;
- binds prompt/generation token counts, thread count, GPU-layer count, device selection, model filename and runtime build commit to returned JSON before accepting a result;
- rejects non-finite/zero timing data rather than admitting malformed measurement evidence;
- exposes stable fail-closed errors for missing artifacts, hash mismatch, unsupported format/context, missing executable, timeout, non-zero process exit, malformed JSON, output shape/type mismatch and result identity mismatch;
- models benchmark calls as isolated processes with `supports_prefix_cache=false` and `PrefixCacheState.EMPTY` rather than pretending that reusable cache state exists;
- preserves the verified benchmark observation for later T031 measurement plumbing without mutating the T023 protocol.

## llama.cpp Interface Pin

Live official upstream verification on 2026-08-29 pinned:

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

Pinned source proves that device value `none` is accepted and represented as `devices=none`. The JSON format exposes the identity/measurement fields consumed by the adapter, including `build_commit`, `model_filename`, `n_prompt`, `n_gen`, `n_threads`, `n_gpu_layers`, `devices`, `avg_ns`, and `avg_ts`.

The repository profile always supplies:

```text
-ngl 0
--device none
-r 1
-o json
```

A returned result that does not prove the requested token/thread/GPU/device/model/build identities fails closed.

## llamafile Disposition

Current release verification pinned:

```text
release = 0.10.5
commit  = 486e6c5f9356eae50b851b07517bfae1f2420193
tree    = 088f5d67a6459c47d58f098f33dc0906f8b3f0d4
```

The pinned release tree and current code search did not expose a current `llamafile-bench` entry point. Historical benchmark-interface behavior is not treated as current authority. T030 therefore records llamafile as:

```text
DEFERRED_INTERFACE_NOT_PROVEN
```

No fake adapter, guessed CLI, or compatibility result is created.

## Test Intent

The T030 tests use temporary synthetic fixture bytes and injected deterministic command runners. They exercise adapter semantics without downloading or executing model weights or requiring a real runtime binary.

The exact task-required integration path now exists:

```text
tests/integration/test_runtime_adapters.py
```

Focused assertions include:

```text
LOCAL_ARTIFACT_SHA_MISMATCH -> REJECT
FORMAT_OR_CONTEXT_UNSUPPORTED -> REJECT
CPU_ONLY_COMMAND -> -ngl 0 + --device none
RPC_OR_PROVIDER_NETWORK_FLAGS -> REJECT
DUPLICATE_OR_NON_NONE_DEVICE_SELECTOR -> REJECT
PREFIX_CACHE_REUSE -> FALSE / EMPTY
NONZERO_PROCESS -> STABLE_FAILURE
MALFORMED_JSON -> STABLE_FAILURE
NONFINITE_OR_ZERO_MEASUREMENT -> REJECT
RESULT_TOKEN_THREAD_GPU_DEVICE_IDENTITY_MISMATCH -> REJECT
MODEL_OR_RUNTIME_BUILD_IDENTITY_MISMATCH -> REJECT
VALID_PINNED_RESULT -> ACCEPT
```

## Qualification Boundary

The earlier hosted qualification run `33264129717` targeted stale head `f87f421745c1aafd9cfff1615fc843114b4135c8` and failed before exposing any steps. It is infrastructure evidence only and cannot qualify the current implementation.

No repository quality gate is claimed on the current final candidate head until exact-head qualification executes.

```text
T030_FOCUSED_TESTS = PENDING_FINAL_HEAD_EXECUTION
MSTR_QUALIFY_VALIDATE = PENDING_FINAL_HEAD_EXECUTION
FULL_PYTEST = PENDING_FINAL_HEAD_EXECUTION
RUFF = PENDING_FINAL_HEAD_EXECUTION
MYPY = PENDING_FINAL_HEAD_EXECUTION
CI_PASS = NOT_CLAIMED
T030_COMPLETE_CANONICAL = NO
```

The repository has separately proven hosted-runner failures where Ubuntu, Windows and macOS jobs all failed before exposing a step. A fresh exact-head T030 run is still required; if it exhibits the same condition, that remains infrastructure evidence only.

## Authority Boundary

```text
NEW_MODEL_WEIGHT_ACCESS = NONE
MODEL_INFERENCE = NONE
QUANTIZATION_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PRODUCTION_RELEASE = NONE
```

T030 implementation does not authorize T031 measurements. Actual runtime/model execution remains a later governed action with exact artifact/runtime/hardware identity and applicable external-effect authority.
