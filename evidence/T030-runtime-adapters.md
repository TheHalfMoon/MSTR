# T030 Portable CPU Runtime Adapter Evidence

**Task:** `T030`

**Canonical reconciliation base:** `226609e3a29a5e5d038bbd0e9c744f3ff2877112`

**Historical source PR:** `#96`

**Historical source head:** `b4adce223a9a5c833f2c2392d742cb93bdad0ba3`

**State:** `IMPLEMENTATION_MERGED / POSTMERGE_VERIFIED / CLOSEOUT_CANDIDATE / COMPLETE_CANONICAL_ON_CLOSEOUT_MERGE`

## Entry Gate

Canonical `docs/canonical/PROGRAM_ROADMAP.md` treats MSTR-000 T030-T034 as a parallel candidate/runtime qualification branch. T029 is `COMPLETE_CANONICAL`. T030 is model-independent adapter infrastructure only: this reconciliation consumes the canonical T023 runtime protocol but performs no T031 measurement, model inference, artifact acquisition, conversion, quantization, or other model execution.

```text
T029 = COMPLETE_CANONICAL
T023_RUNTIME_PROTOCOL = CANONICAL
MODEL_WEIGHT_ACCESS_BY_T030 = NONE
MODEL_EXECUTION_BY_T030 = NONE
PAID_COMPUTE = NONE
PRODUCTION_RELEASE = NONE
```

PR #96 is retained as historical evidence only. Its branch diverged from current main and is not merge-authorized. This candidate reconstructs and hardens the still-valid T030 implementation directly on exact current main rather than rebasing or merging the stale branch.

## Reconciled Surface

```text
src/mstr_qualify/runtimes/benchmark_cli.py
src/mstr_qualify/runtimes/__init__.py
configs/runtimes/llama-cpp-cpu.json
artifacts/decisions/T030-runtime-interface-scan.json
tests/unit/test_runtime_benchmark_cli.py
tests/security/test_runtime_benchmark_boundary.py
tests/security/test_runtime_profile_alias_boundary.py
tests/security/test_runtime_environment_boundary.py
tests/integration/test_runtime_adapters.py
evidence/T030-runtime-adapters.md
```

The implementation is intentionally model-independent and preserves the historical hardening that remained compatible with current T023 and identifier interfaces while adding current-main security repairs discovered during substantive inspection.

The adapter:

- keeps `LoadRequest` identity-only; artifact location remains a caller input;
- verifies local artifact SHA-256 against the exact load identity before entering `READY`;
- revalidates the loaded artifact SHA-256 immediately before every benchmark process and rejects observed post-load mutation or disappearance before launch;
- performs no artifact acquisition;
- rejects direct model-URL, Docker repository, Hugging Face provider-acquisition, and llama.cpp RPC CLI flags, including equals forms;
- strips inherited `LLAMA_ARG_*` and `HF_*` environment option surfaces before the real runtime subprocess executes;
- requires exactly one runtime device selector across the complete generated CLI token set and requires it to be `none`;
- forces `n_gpu_layers=0` and `--device none` for the portable CPU path;
- binds prompt/generation token counts, thread count, GPU-layer count, device selection, model filename, and runtime build commit to returned JSON before accepting a result;
- rejects non-finite or non-positive timing evidence;
- exposes stable fail-closed errors for artifact, process, profile, and output failures;
- represents isolated benchmark processes as `supports_prefix_cache=false` with `PrefixCacheState.EMPTY` rather than inventing reusable cache state;
- retains a verified benchmark observation structure for later T031 plumbing without authorizing or performing T031 execution.

The pre-process SHA-256 revalidation is a fail-closed check against observed post-load mutation. It does not claim filesystem-level atomicity between the final hash read and a separate external executable opening the path.

## Security Boundary

### Cross-field device selector alias

Historical review discovered a cross-field CLI alias path where device-selector validation could have covered only `output_args`. The retained hardened implementation validates the complete generated `command_tokens` tuple. Dedicated regression coverage injects both `-dev` and `--device` through all non-output CLI argument fields and requires rejection.

### Inherited upstream option environment

Current-main substantive inspection found that the pinned upstream parser accepts runtime options from environment variables, while the historical adapter only rejected unsafe argv tokens. At the pinned revision, `common/arg.cpp` exposes environment-backed surfaces including:

```text
LLAMA_ARG_MODEL_URL
LLAMA_ARG_DOCKER_REPO
LLAMA_ARG_HF_REPO
LLAMA_ARG_HF_FILE
HF_TOKEN
LLAMA_ARG_RPC
LLAMA_ARG_DEVICE
LLAMA_ARG_N_GPU_LAYERS
```

Because `subprocess.run` inherits environment by default, a hostile or accidental inherited variable could have re-enabled network acquisition, RPC, or non-CPU behavior despite a safe argv profile. That finding invalidated the pre-finding candidate for merge qualification.

The repair makes the default real subprocess runner pass an explicit sanitized environment that removes every `LLAMA_ARG_*` and `HF_*` variable while preserving unrelated process environment. `tests/security/test_runtime_environment_boundary.py` proves removal of current/future upstream option variables and preservation of an unrelated sentinel variable. Injected deterministic test runners remain unaffected because they receive only command tokens and timeout.

### Post-load artifact identity drift

A later substantive inspection found that artifact SHA-256 was originally checked only during `load()`, while each `prefill()` or `decode()` launches a new process that opens the artifact path later. A file changed after `READY` could therefore have caused execution against bytes different from the `LoadRequest.artifact_sha256` identity.

The repair revalidates file existence and SHA-256 immediately before each benchmark process. A dedicated regression mutates the local artifact after `load()` and proves that `runtime.artifact_hash_changed_after_load` is raised before the injected runner is called.

### Direct acquisition aliases in argv

A further pinned-upstream review found direct acquisition surfaces not covered by the historical HF/RPC denylist:

```text
-mu / --model-url
-dr / --docker-repo
```

These are now prohibited alongside Hugging Face and RPC flags. Regression cases cover both long and short equals forms.

The consolidated boundary is:

```text
INHERITED_LLAMA_ARG_* -> REMOVED_BEFORE_REAL_SUBPROCESS
INHERITED_HF_* -> REMOVED_BEFORE_REAL_SUBPROCESS
SAFE_UNRELATED_ENV -> PRESERVED
ARGV_MODEL_URL_OR_DOCKER_ACQUISITION -> REJECT
ARGV_HF_PROVIDER_ACQUISITION -> REJECT
ARGV_RPC -> REJECT
POST_LOAD_ARTIFACT_MUTATION_OBSERVED_BEFORE_LAUNCH -> REJECT
DUPLICATE_OR_NON_NONE_DEVICE_SELECTOR -> REJECT
CROSS_FIELD_DEVICE_SELECTOR_ALIAS -> REJECT
```

## llama.cpp Interface Reverification

Official upstream evidence was reverified on 2026-09-05 at the exact historical pin:

```text
repository = https://github.com/ggml-org/llama.cpp
revision   = 3173a56471c1753650cd806694145ffd6dcace67
interfaces = tools/llama-bench/README.md
             tools/llama-bench/llama-bench.cpp
             common/arg.cpp
```

The pinned interface documents or implements:

```text
-m / --model
-mu / --model-url
-dr / --docker-repo
-p / --n-prompt
-n / --n-gen
-t / --threads
-ngl / --n-gpu-layers
-dev / --device
-r / --repetitions
-hf / -hfr / --hf-repo
-hff / --hf-file
-hft / --hf-token
-rpc / --rpc
-o / --output json
```

Pinned source proves `device=none` is accepted and serialized as `devices=none`, exposes the identity/measurement fields consumed by the adapter, and proves that runtime option environment variables are first-class parser inputs. These interfaces define the current denylist and environment-sanitization boundary.

The repository profile supplies:

```text
-m <already-present-local-artifact>
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

The T030 tests use temporary synthetic bytes and injected deterministic command runners, plus a monkeypatched subprocess regression that inspects the sanitized environment without executing a real runtime. They do not download or execute model weights, require a real runtime binary, or access the network.

Focused assertions include:

```text
LOCAL_ARTIFACT_SHA_MISMATCH -> REJECT
POST_LOAD_ARTIFACT_SHA_MUTATION -> REJECT_BEFORE_PROCESS
FORMAT_OR_CONTEXT_UNSUPPORTED -> REJECT
CPU_ONLY_COMMAND -> -ngl 0 + --device none
MODEL_URL_OR_DOCKER_ACQUISITION_FLAGS -> REJECT
RPC_OR_HF_PROVIDER_NETWORK_FLAGS -> REJECT
INHERITED_RUNTIME_NETWORK_OR_DEVICE_ENV -> REMOVED
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

## Qualification History

Historical PR #96 qualification attempts remain immutable infrastructure evidence only. They do not transfer to this candidate.

Current-main attempt 1:

```text
RUN = 33969313680
TARGET_HEAD = 67a0842c24fe1e7d0732626d5decce13badf5223
IDENTITY_SCOPE = FAILURE
CAUSE = git diff --check rejected Markdown trailing whitespace
QUALITY = SUCCESS
FINAL_QUALIFICATION = SKIPPED
DISPOSITION = NEGATIVE CANDIDATE EVIDENCE / SUPERSEDED
```

Current-main attempt 2:

```text
RUN = 33969546445
TARGET_HEAD = 776b5d4c1d8ba07f23ab7f78b27c067a1d132e07
IDENTITY_SCOPE = SUCCESS
QUALITY = SUCCESS
FINAL_QUALIFICATION = FAILURE
CAUSE = live PR head advanced during the run
DISPOSITION = NON_TRANSFERABLE EXACT-HEAD EVIDENCE
```

Current-main attempt 3:

```text
RUN = 33969770038
TARGET_HEAD = 829e9e400849a7cd2670dfc300d4ed78ead0989c
IDENTITY_SCOPE = SUCCESS
QUALITY = SUCCESS
FINAL_QUALIFICATION = FAILURE
CAUSE = live PR head advanced before final guard
DISPOSITION = NON_TRANSFERABLE EXACT-HEAD EVIDENCE
```

Current-main attempt 4:

```text
RUN = 33969835802
TARGET_HEAD = 5f51b19e929062623a4c9adfe0ae847307e6a421
IDENTITY_SCOPE = SUCCESS
QUALITY = SUCCESS
FINAL_QUALIFICATION = SUCCESS
LATER_DISPOSITION = SUPERSEDED_BY_MATERIAL_ENVIRONMENT_SECURITY_FINDING
```

Attempt 4 genuinely qualified its exact target at the time it completed. A later substantive inspection found the inherited runtime environment bypass, so the successful run became historical evidence only.

Current-main attempt 5:

```text
RUN = 33970180495
TARGET_HEAD = e14409f7b0d3d672bba1faf69c84e46eb20da369
IDENTITY_SCOPE = SUCCESS
FOCUSED_TESTS = 40 PASSED
MSTR_QUALIFY_VALIDATE = PASS
FULL_PYTEST = 1349 PASSED
RUFF = FAILURE_I001_IMPORT_FORMATTING
MYPY = NOT_REACHED
FINAL_QUALIFICATION = SKIPPED
DISPOSITION = NEGATIVE QUALIFICATION EVIDENCE / FORMATTING_REPAIRED
```

The Ruff finding required only removal of one blank line in `tests/security/test_runtime_environment_boundary.py`; no runtime logic changed in that repair.

Current-main attempt 6:

```text
RUN = 33971084397
TARGET_HEAD = db6677d4ec1ae2d06b27344a80e95257097070a3
IDENTITY_SCOPE = SUCCESS
QUALITY = SUCCESS
FINAL_QUALIFICATION = SUCCESS
LATER_DISPOSITION = SUPERSEDED_BY_MATERIAL_SUBSTANTIVE_REVIEW_FINDINGS
```

Attempt 6 genuinely qualified its exact target. Subsequent independent substantive inspection found both the post-load artifact identity drift and the missing `--model-url` / `--docker-repo` acquisition aliases. The candidate changed to repair those findings, so attempt 6 does not transfer to the final hardened head.

Two focused hardening diagnostics were then executed on repaired intermediate heads:

```text
RUN = 33971363161
TARGET_HEAD = 4ac2bdd527dad23ec931c9eaecc8e2c41d97eff8
FUNCTIONAL_TESTS = 29 PASSED
RUFF = PASS
MYPY = PASS
WORKFLOW_RESULT = FAILURE
CAUSE = diagnostic checkout was shallow, so final git diff --check could not resolve canonical base object
DISPOSITION = HARNESS_ONLY_NEGATIVE_EVIDENCE / NOT_QUALIFICATION
```

```text
RUN = 33971535582
TARGET_HEAD = 4dc1220bd6f3b8e14ffa978b363e443c15f1232b
FUNCTIONAL_TESTS = 45 PASSED
RUFF = PASS
MYPY = PASS
WORKFLOW_RESULT = FAILURE
CAUSE = diagnostic checkout was shallow, so final git diff --check could not resolve canonical base object
DISPOSITION = HARNESS_ONLY_NEGATIVE_EVIDENCE / NOT_QUALIFICATION
```

Those diagnostics prove the focused code/static gates reached PASS before the harness-only failure, but neither is a qualification result and neither may be promoted to merge authority.

Fresh qualification must execute every frozen gate again on one final immutable head with full Git history available for exact base/head topology checks:

```text
T030_FOCUSED_TESTS = REQUIRED_ON_FINAL_HARDENED_HEAD
MSTR_QUALIFY_VALIDATE = REQUIRED_ON_FINAL_HARDENED_HEAD
FULL_PYTEST = REQUIRED_ON_FINAL_HARDENED_HEAD
RUFF = REQUIRED_ON_FINAL_HARDENED_HEAD
MYPY = REQUIRED_ON_FINAL_HARDENED_HEAD
EXACT_HEAD_SCOPE_AND_IDENTITY = REQUIRED_ON_FINAL_HARDENED_HEAD
INDEPENDENT_SUBSTANTIVE_REVIEW = REQUIRED_AFTER_QUALIFICATION
MANDATORY_PREMERGE = REQUIRED
POSTMERGE_VERIFICATION = REQUIRED
T030_COMPLETE_CANONICAL = NO_UNTIL_GOVERNED_CLOSEOUT
```

No qualification PASS is claimed for the final hardened head before a fresh exact-head run reaches a successful terminal final guard.

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


## Canonical Closeout Lifecycle

The current-main T030 reconciliation completed the governed implementation lifecycle on one exact final hardened head. Historical PR #96 remains provenance only and was never merged into current main.

```text
IMPLEMENTATION_PR = #165
IMPLEMENTATION_HEAD = 0462786550d24096272b7541ab286e838b4a1c2e
IMPLEMENTATION_TREE = b016ab6a3899accc352d8f177a2ba76451259f66
EXACT_HEAD_QUALIFICATION = 33971815139 / SUCCESS / evidence f48819767b1d571819736562aba22e84a84b3a85
SECOND_EXACT_HEAD_QUALIFICATION = 33971878391 / SUCCESS / evidence b23bc1c7401262bfd41af33bfc1562295e7acc54
INDEPENDENT_SEMANTIC_SECURITY_REVIEW = 33972061731 / SUCCESS / evidence 540d3346863f8be053e8ac199703a884a33998da
REVIEW_SUBMISSION = 5121599106 / COMMENTED / FINDINGS_NONE
MANDATORY_PREMERGE = 33972305104 / SUCCESS / evidence 62e7684531a788c22888eadcfc6e8d09b0c54e96
MERGE = 8916fa7138ad56d18452b7a20db9c8cb982648ba
MERGE_TREE = b016ab6a3899accc352d8f177a2ba76451259f66
POSTMERGE = 33972551215 / SUCCESS / evidence c6ae1aeb25bed755e86515d6914fb871e1f5a164
```

The successful postmerge replay on exact canonical main recorded:

```text
T030_FOCUSED_TESTS = 45 PASSED
MSTR_QUALIFY_VALIDATE = PASS / 30 VALID FIXTURES / 30 INVALID FIXTURES REJECTED
FULL_PYTEST = 1354 PASSED
RUFF = PASS
MYPY = PASS / 45 SOURCE FILES
FINAL_POSTMERGE_GUARD = PASS
```

This closeout is governance-only. It does not reacquire deleted model binaries, execute a model/runtime pair, regenerate Q4 artifacts, widen the T027/T028 candidate envelope, create B012 authority, authorize paid compute, or create T031 material execution authority.

## Completion Boundary

```text
T030_IMPLEMENTATION_LIFECYCLE = COMPLETE
T030_CLOSEOUT_STATE = COMPLETE_CANONICAL_ON_MERGE
T030_COMPLETE_CANONICAL = YES_ON_CLOSEOUT_MERGE
T031_EXECUTION_AUTHORITY = NOT_CREATED_BY_T030
B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION = ABSENT
```

Upon merge of this bounded closeout, T030 is `COMPLETE_CANONICAL`. T031 remains a separate material measurement task and must bind exact current authority plus artifact/runtime/hardware identity before external execution.
