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
```

The adapter:

- keeps `LoadRequest` identity-only; artifact location remains an environment/caller input;
- verifies the local artifact SHA-256 against the exact load identity before entering `READY`;
- performs no artifact acquisition and rejects provider repository/token flags in profiles;
- forces the configured benchmark CLI to `n_gpu_layers=0` for the portable CPU path;
- binds prompt/generation token counts, thread count, GPU-layer count, model filename and runtime build commit to the returned JSON before accepting a result;
- exposes stable fail-closed error codes for missing artifacts, hash mismatch, unsupported format/context, missing executable, timeout, non-zero process exit, malformed JSON, output shape/type mismatch and result identity mismatch;
- models benchmark calls as isolated processes with `supports_prefix_cache=false` and `PrefixCacheState.EMPTY` rather than pretending that reusable cache state exists;
- preserves the verified benchmark observation for later T031 measurement plumbing without mutating the T023 protocol.

## llama.cpp Interface Pin

Live official upstream verification on 2026-08-29 pinned:

```text
repository = https://github.com/ggml-org/llama.cpp
revision   = 3173a56471c1753650cd806694145ffd6dcace67
interface  = tools/llama-bench/README.md
```

The pinned interface documents:

```text
-m / --model
-p / --n-prompt
-n / --n-gen
-t / --threads
-ngl / --n-gpu-layers
-r / --repetitions
-o / --output json
```

Its JSON format exposes the identity/measurement fields consumed by the adapter, including `build_commit`, `model_filename`, `n_prompt`, `n_gen`, `n_threads`, `n_gpu_layers`, `avg_ns`, and `avg_ts`.

The repository profile always supplies `-ngl 0`, one repetition, and JSON output. A returned result that does not prove those requested identities fails closed.

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

The T030 tests use a temporary fixture artifact and injected deterministic command runner. They exercise adapter semantics without downloading or executing model weights or requiring a real runtime binary.

Required focused assertions include:

```text
LOCAL_ARTIFACT_SHA_MISMATCH -> REJECT
FORMAT_OR_CONTEXT_UNSUPPORTED -> REJECT
CPU_ONLY_COMMAND -> -ngl 0
PROVIDER_ACQUISITION_FLAGS -> ABSENT
PREFIX_CACHE_REUSE -> FALSE / EMPTY
NONZERO_PROCESS -> STABLE_FAILURE
MALFORMED_JSON -> STABLE_FAILURE
RESULT_TOKEN_THREAD_GPU_IDENTITY_MISMATCH -> REJECT
RUNTIME_BUILD_IDENTITY_MISMATCH -> REJECT
VALID_PINNED_RESULT -> ACCEPT
```

## Qualification Boundary

No repository quality gate has yet been claimed on the final T030 implementation head. Historical CI results from other tasks are not reusable.

```text
T030_FOCUSED_TESTS = PENDING_FINAL_HEAD_EXECUTION
MSTR_QUALIFY_VALIDATE = PENDING_FINAL_HEAD_EXECUTION
FULL_PYTEST = PENDING_FINAL_HEAD_EXECUTION
RUFF = PENDING_FINAL_HEAD_EXECUTION
MYPY = PENDING_FINAL_HEAD_EXECUTION
CI_PASS = NOT_CLAIMED
T030_COMPLETE_CANONICAL = NO
```

The repository currently has a separately proven hosted-runner failure in which Ubuntu, Windows and macOS jobs all fail before exposing any step. If T030 hosted qualification exhibits the same condition, that is infrastructure evidence only; it is neither implementation failure nor PASS.

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
