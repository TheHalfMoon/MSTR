# B012 Qwen Raw-Code Completion Runtime Contract Repair

## Scope

This package records a non-executing runtime-contract repair for the Qwen raw-code recovery path after GitHub Actions run `34288154926` failed before any durable raw-code case result.

The package does not activate a workflow, execute a model, re-acquire model weights, authorize a retry, authorize external dispatch, create cross-run resume authority, expand candidate/revision/file scope, perform training, spend paid compute, or authorize B013.

## Canonical incident

The triggering incident is run `34288154926`, attempt `1`, on canonical main `66cd090fc75286bfc24db4bdf8fe58b64394e228`.

The exact terminating parser error was:

```text
error: invalid argument: --no-conversation
```

The canonical incident classification is:

`B012_EXECUTOR_RUNTIME_CLI_INCOMPATIBILITY_RAW_CODE_UNEXECUTED`

Durable execution reached `init`, `source`, and `quantize`. No raw-code case completed durably. The durable raw-code result remains `NONE_DURABLY_PROVEN`, model-quality verdict remains `NONE`, candidate-admission decision remains `NONE`, and candidate execution completion remains `NOT_PROVEN`.

The incident aggregate SHA-256 is `20e30ef5382189dc22407df0caaab171668c91863cdf972a66bfd90e4615f03d`.

## Exact repair entry

The incident package was merged by PR #202 at canonical merge `e87328872232471fa0e1eb05d74223bc0aeaafd3` and post-merge verification run `34296926324` succeeded.

A separate repair-entry gate was then created on that unchanged canonical main.

- Entry v1 run `34297897331` failed on attempt `1` because the evidence workflow had not installed the repository package, producing `No module named mstr_qualify`. It did not produce `eligible=false` and performed no model access or execution. The failed run is preserved and was not rerun.
- Entry v2 run `34297979527`, attempt `1`, evidence head `ad87bba0447143837d26af6cf6b53911b8a708e3`, succeeded after installing the repository package. It proved B012 `eligible=true`, reasons `[]`, observed state `PENDING`, exact Founder authority satisfied, all prerequisites satisfied, and semantic checks true on canonical main `e87328872232471fa0e1eb05d74223bc0aeaafd3`.

Entry verification performed no model access, model execution, paid compute, or training.

## Pinned runtime source finding

The B012 toolchain lock pins llama.cpp runtime commit `3173a56471c1753650cd806694145ffd6dcace67`.

At that exact immutable upstream commit:

- `tools/cli/cli.cpp` parses with `LLAMA_EXAMPLE_CLI`.
- `common/arg.cpp` scopes `--conversation` / `--no-conversation` to `LLAMA_EXAMPLE_COMPLETION`.
- `tools/completion/completion.cpp` parses with `LLAMA_EXAMPLE_COMPLETION`.
- `tools/completion/CMakeLists.txt` defines the official `llama-completion` executable.
- The completion parser supports `--no-conversation`, `--no-display-prompt`, and `--simple-io`.

The immutable upstream Git blob identities bound by this repair are:

- `common/arg.cpp`: `4469612cd5b26611ee08a1937cb721576e24d095`
- `tools/cli/cli.cpp`: `dcdb6aeac21dcada049f9cd7cc37d352b41f1f35`
- `tools/completion/CMakeLists.txt`: `a310251eff6e18c5ab09787066d7c76afa673e8f`
- `tools/completion/completion.cpp`: `941b7399b2e3fb9a069619c17d1f64b67320ef72`
- `tools/completion/main.cpp`: `bea9a0ec9aa75e9eb4f7962d85ed136e9e0dcb7b`

## Why deleting `--no-conversation` is not equivalent

The frozen B012 raw-code proxy is a raw prompt-to-completion measurement. Silently deleting the rejected flag from `llama-cli` would remove the parser error but would not prove that the resulting execution preserves raw completion semantics. It could instead enter chat-oriented behavior and change the benchmark contract without a recorded migration.

The compatible repair is to keep the exact pinned runtime commit and move only the executable/parser surface from `llama-cli` / `LLAMA_EXAMPLE_CLI` to the official `llama-completion` / `LLAMA_EXAMPLE_COMPLETION` path. Conversation remains explicitly disabled, prompt display remains disabled, and simple I/O remains enabled.

## Equivalence boundary

The repair keeps all material benchmark inputs unchanged:

- same B010 Qwen candidate identity and exact source file scope;
- same conversion and quantization contract;
- same Q4 target contract;
- same three raw-code prompts;
- same `2048` context-token limit;
- same `96` generated-token limit;
- same `2` CPU threads and `0` GPU layers;
- same temperature `0.0` and seed `42`;
- same `ast.parse(prompt + completion)` verifier;
- same observational-only interpretation, not a final admission gate.

The only intended semantic migration is the runtime executable/parser surface required to express the already-frozen raw completion request on the pinned llama.cpp commit.

## Repair package

The inactive repair package consists of:

- `colab/mstr_b012_raw_code_completion.py`
- `colab/mstr_b012_qwen_raw_code_completion.py`
- `benchmarks/manifests/B012-raw-code-proxy-completion-runtime.json`
- `artifacts/manifests/B012-qwen-raw-code-completion-runtime-repair.json`
- `configs/workflows/b012-qwen-raw-code-completion-recovery.yml`
- `tests/contract/test_b012_qwen_raw_code_completion_runtime_contract.py`

The active workflow `.github/workflows/b012-qwen-raw-code-recovery.yml`, current executor binding `artifacts/manifests/B012-executor-toolchain-binding.json`, and active one-shot raw-code helper `colab/mstr_b012_raw_code_one_shot.py` are intentionally not changed by this repair package.

The inactive workflow template contains a proposed new command only for a future separately governed activation change. This repair package itself has no executable GitHub Actions trigger.

## Activation boundary

This repair is ready only for separate canonical activation after qualification, independent semantic/security review, mandatory premerge proof, guarded merge, and post-merge verification.

A future activation change must bind exact SHA-256 identities for the canonical repair package and active workflow, preserve exact-main B012 eligibility and Founder authority, and continue to create no authority beyond the already canonical B012 scope.

No model execution may occur merely because this repair becomes canonical. A fresh exact-main eligibility and authority proof is required before any newly activated dispatch, and the failed run `34288154926` must never be rerun.
