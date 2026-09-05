# T031 Canonical Executor / Toolchain Binding

**Task:** MSTR-000 / T031 pre-dispatch execution binding
**Source main:** `891af2215a2244a6a0912d49d782f42bcc38b6ef`
**Scope:** exact Founder-authorized T029 candidate set only
**External model execution in this change:** NONE
**Paid cost:** USD 0.00

## Purpose

This change supplies the separately reviewed executor/toolchain binding required by the canonical
T031 Founder authority before any T031 model access may be dispatched. It does not mutate the
canonical authority or execution envelope and does not expand their scope.

The authority intentionally remains recorded as
`BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING`. This proposal satisfies that condition only
when this exact file set is canonical on `main`; an unmerged branch or PR does not permit model
access.

## Authority boundary

Founder decision:

`FOUNDER_T031_LOCAL_MEASUREMENT_DECISION=AUTHORIZE_EXACT_T029_CANDIDATES`

Canonical decision surface:

- Issue #167
- Founder decision comment `5553875809`

Exact candidates:

- `granite-4.1-3b`
- `ministral-3-3b`
- `qwen2.5-coder-1.5b`
- `qwen3-4b`
- `qwen3.5-2b`
- `qwen3.5-4b`
- `smollm3-3b`
- `yi-coder-1.5b`

No B012 candidate, new candidate, revision/file expansion, T032, T033, T034 admission decision,
training, weight-changing operation, paid compute, paid model API, gated-terms acceptance,
production release, Git model binary, or founder-machine model binary is authorized here.

## Toolchain resolution evidence

Toolchain discovery performed no model access, inference, quantization, or training.

Dependency-resolution evidence:

- run `33987218696`
- artifact `9975528248`
- artifact ZIP SHA-256
  `e08ccaf2a601193c060e9e378d356e80ed1ad6c701817d61c80965dd03abe99f`
- report SHA-256
  `6c90af7fa0d148ad9f3740d327a6e1ffdfd1b58b5009f2213a975bb1fad43f84`

Exact pip-wheel evidence:

- run `33987490628`
- artifact `9975602854`
- artifact ZIP SHA-256
  `0c77b7c1fcd7fc6ef659293bb4d26fea568ec083e5978c3aac06a1e3c6942e9d`
- report SHA-256
  `0cfbf0151ad03a7e1a0d902b1b1351310cd7ef18d8185ba2de990d212f7498ef`

The lock converts the resolved graph into direct HTTPS wheel URLs plus exact SHA-256 values.
Execution downloads those objects from only `files.pythonhosted.org`, `download.pytorch.org`, or
`download-r2.pytorch.org`, verifies every object, then installs with `--no-index --no-deps`.
Package-index resolution is absent from the model-execution phase.

The GitHub-hosted image identity is also fail-closed on Python 3.11.9 and the exact observed CMake,
GCC, and G++ first-line versions. A future hosted-image drift invalidates the run rather than
silently changing the execution toolchain.

## Pinned conversion and runtime identity

Conversion / quantization:

- repository: `https://github.com/ggml-org/llama.cpp.git`
- commit: `fc35562ba46fbbf8e30cac85edbb39642c37d248`
- conversion command follows canonical T029:
  `convert_hf_to_gguf.py <source> --outfile <f16.gguf> --outtype f16`
- exact regenerated identities: F16, `Q4_K_M`, and `Q4_K_S`

Runtime:

- repository: `https://github.com/ggml-org/llama.cpp.git`
- commit: `3173a56471c1753650cd806694145ffd6dcace67`
- CPU-only: `-ngl 0`, `--device none`
- inherited `LLAMA_ARG_*`, Hugging Face, CUDA/NVIDIA, and common provider credential variables are
  removed before llama.cpp execution
- runtime output must report the requested model, token counts, threads, zero GPU layers,
  `devices=none`, and a build commit matching the pinned runtime identity
- every local toolchain subprocess is bounded by an explicit timeout; timeout is a fail-closed
  `ToolchainError`, never an implicit hang or success

## Source acquisition and artifact regeneration

Immediately before the first model byte is requested, the executor requires checked-out `HEAD` to
equal live remote `main`.

For the selected candidate, acquisition is restricted to the exact pinned model revision and the
exact required file set. Every file is verified against its canonical T028 per-file SHA-256 and
size. Absolute paths, `..`, dot components, empty components, and backslash paths are rejected.
Model HTTP redirects must remain within only `huggingface.co` and `us.aws.cdn.hf.co`.

The regenerated F16, `Q4_K_M`, and `Q4_K_S` hashes and byte sizes must match canonical T029 evidence
exactly. `Q4_K_S` is identity-regeneration evidence only; T031 measures `Q4_K_M`. Source, F16,
`Q4_K_S`, tool builds, and model binaries are deleted from the ephemeral runner as soon as their
bounded purpose is complete.

Workdir cleanup and creation are inside the fail-closed execution envelope. A filesystem error
before acquisition therefore produces failure evidence and the final cleanup path still runs.

## Measurement semantics

T031 measures contexts 4096, 8192, and 16384 using `MSTR-MEASURE-v0` deterministic microbenchmark
statistics:

- 2 warmups excluded;
- 10 measured independent process launches;
- median, p90, minimum, maximum, and sample count;
- process-cold natural-OS-cache state;
- 2 CPU threads;
- process RSS/HWM/swap/major-fault observations;
- whole-system total/available memory, swap state, page-major-fault, swap-in, and swap-out deltas;
- prefill tokens/second from isolated prefill runs.

Decode follows the already canonical T030 adapter surface: an isolated `prompt=0`, `generation=128`
companion benchmark. It is explicitly labeled
`T030_ISOLATED_DECODE_COMPANION_NOT_POST_PREFILL_KV_CACHE`; it is not represented as decode after a
filled 4K/8K/16K KV cache.

Load behavior is retained as the explicitly named estimate
`estimated_load_and_process_startup_seconds`, computed as process wall time minus llama-bench's
reported average benchmark operation time. It is not presented as a directly instrumented
model-load event.

Tokenizer-normalized UTF-8/character output rates are recorded as not measured by this T031 runtime
microbenchmark, rather than inferred from token throughput.

The GitHub-hosted lane is labeled
`AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM`. It cannot satisfy the U1 8 GB hardware
claim, sustained T032 requirement, T033 quality-regression requirement, or T034 admission gate.

## Dispatch lifecycle

This binding PR itself performs no model access.

After this exact binding becomes canonical, dispatch is permitted only through `workflow_dispatch`
from canonical `main`, selecting one of the eight exact Founder-authorized candidates. The governed
workflow has no push, branch-creation, wildcard-branch, or arbitrary-ref execution trigger.

The workflow verifies `refs/heads/main` before selecting the candidate, explicitly checks out live
canonical `main` with persisted Git credentials disabled, and then invokes the exact bound executor.
Global workflow concurrency is one candidate and `cancel-in-progress` is false. The executor
rechecks live `main` again immediately before model access and again before reporting success. A
main movement invalidates the run.

Only JSON/JSONL measurement evidence is uploaded. Any identity, authority, toolchain, network,
artifact, runtime, or live-main mismatch fails closed; failed runs remain failure evidence and are
never rewritten as success.
