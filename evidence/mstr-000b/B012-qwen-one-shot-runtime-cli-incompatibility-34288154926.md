# B012 Qwen One-Shot Raw-Code Runtime CLI Incompatibility — Run 34288154926

## Scope

This document canonicalizes the first execution attempt of the separately activated Qwen one-shot raw-code recovery topology. It records only evidence that survived GitHub Actions run `34288154926`, attempt `1`, on canonical main `66cd090fc75286bfc24db4bdf8fe58b64394e228`.

This incident package does not execute a model, authorize a retry, expand candidate/revision/file scope, perform training, spend paid compute, or authorize B013.

## Dispatch identity

- Issue: `#162`
- Owner comment ID: `5592988994`
- Exact command: `B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982`
- Workflow: `B012 Qwen raw-code one-shot recovery`
- Workflow path: `.github/workflows/b012-qwen-raw-code-recovery.yml`
- Run: `34288154926`
- Job: `102268410928`
- Attempt: `1`
- Event: `issue_comment`
- Head: `66cd090fc75286bfc24db4bdf8fe58b64394e228`
- Conclusion: `failure`

No rerun was performed.

## Durable execution evidence

The run completed and durably uploaded the following stages before the raw-code failure:

1. `init` — exact recovery toolchains initialized.
2. `source` — all nine exact B010 Qwen source files reacquired and verified, totaling `1769897109` bytes.
3. `quantize` — the exact Q4 artifacts were regenerated and verified.

The regenerated identities were:

- F16: `198297c5988d7420ef3939911c5a8e1a018a7404e7bf6fb5e6965c3cc9a04045`, `1557662144` bytes.
- Q4_K_M: `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`, `541903296` bytes.
- Q4_K_S: `a412656365e22625d722ede780dd745c2491aa74372ee4b20f2891947ba07c9e`, `516778432` bytes.

Stage `raw-code-python-clamp` failed. Its upload step still succeeded and preserved the failure/state JSON plus all preceding checkpoints. `python-dedupe`, `python-safe-divide`, and finalization were skipped. The explicit workflow cleanup step succeeded.

No completed raw-code case checkpoint exists for this run. The durable raw-code result therefore remains `NONE_DURABLY_PROVEN`.

## Exact failure

The executor-authored failure record contains:

```text
llama-cli raw-code execution failed for python-clamp: warning: no usable GPU found, --gpu-layers option will be ignored
warning: one possible reason is that llama.cpp was compiled without GPU support
warning: consult docs/build.md for compilation instructions
error: invalid argument: --no-conversation
```

The CPU-only GPU warnings are not treated as the failure cause. The terminating parser error is the rejected `--no-conversation` argument.

The correct incident classification is:

`B012_EXECUTOR_RUNTIME_CLI_INCOMPATIBILITY_RAW_CODE_UNEXECUTED`

This is not a model-quality verdict and is not a runner-shutdown incident.

## Pinned runtime compatibility finding

The B012 toolchain lock pins `llama.cpp` runtime commit `3173a56471c1753650cd806694145ffd6dcace67` and the frozen raw-code manifest names runtime `llama.cpp-llama-cli-cpu`.

At that exact upstream commit:

- `common/arg.cpp` defines `--conversation` / `--no-conversation` only for `LLAMA_EXAMPLE_COMPLETION`.
- `tools/cli/cli.cpp` parses arguments using `LLAMA_EXAMPLE_CLI`.
- `tools/cli/cli-context.cpp` submits message-based requests to `/v1/chat/completions`.

Therefore the one-shot repair introduced a completion-only argument into a CLI parser that does not expose it. The observed failure is consistent with the exact pinned source and with the executor-authored failure JSON.

This evidence does not claim that a usable model inference completed. The model-inference completion state remains `NOT_PROVEN` because the CLI failed before any durable raw-code result was produced.

## Why silently deleting the flag is not an acceptable repair

Deleting `--no-conversation` would make the command different, but it would not establish the intended raw one-shot completion semantics. At the pinned commit, `llama-cli` is chat-completions oriented. Treating an unreviewed chat path as equivalent to the frozen raw-code proxy would change benchmark semantics without recording the migration.

Canonical B012 governance explicitly requires equivalent qualification for every B010 qualification candidate and allows T029–T034 protocol reuse only where compatible; when superseded, the migration must be recorded. Any runtime-contract repair must therefore be separately reviewed for equivalence impact across both `mellum-4b` and `qwen3.5-0.8b-control`.

## Durable artifacts

- Stage 01 artifact `10080491362`, archive SHA-256 `f9901fa1f59e8a9d1913c2ca794d95735a0ff85753eaaa0e148a592c9c782495`.
- Stage 02 artifact `10080513976`, archive SHA-256 `ccceafbce9e4414a4d64648d08268cf8fca78d40f097e03c9828a82de8cc53e4`.
- Stage 03 artifact `10080541374`, archive SHA-256 `bff7116601dee3124be48361cc144798944de6fdef74b8a6e25a14e281b1ea8f`.
- Stage 04a failure artifact `10080542101`, archive SHA-256 `14d67ce0a098d9e59f2b1067ceaa079b0dc082f1f321263f272ba81138ce4168`.

Canonicalized source JSON SHA-256 values:

- Failure: `b0aff98dabafd1335b27a771cd74e4cffa9364da3a7d22154db618a7173743ef`.
- State: `4c5c6521180b17949d77bdedf2d18c04dfb7f3345dde40db14527ff3b407e3b8`.
- Init checkpoint: `fb6b5165037691699a36ed53a5d239d500a2818ed230f06932743bfc6072f14f`.
- Source checkpoint: `d95e154bb519cd89359483f49566ad7bcda05127991bd8b1116d8a250e7e5b58`.
- Quantize checkpoint: `0f09abec985a3bb26987f529d86a9d9b1ed6dd2859250700520a81be733322e7`.

Aggregate incident SHA-256: `20e30ef5382189dc22407df0caaab171668c91863cdf972a66bfd90e4615f03d`.

## Authority and entry proof

Incident canonicalization entry was reverified against the unchanged canonical main.

- Entry gate v1 run `34290792864` failed before an eligibility verdict because its detached checkout lacked local `refs/heads/main`. That run is retained as negative harness evidence and was not rerun.
- Entry gate v2 run `34290864636` repaired only the harness by materializing local `refs/heads/main` at the exact canonical SHA. It succeeded on attempt `1` and proved `B012` eligible with no reasons, observed state `PENDING`, exact Founder authority satisfied, all prerequisites satisfied, and all semantic checks true.

The authority remains bounded to the existing two B010 candidates. Training, weight-changing training, paid compute, paid model API, production release, candidate expansion, revision/file expansion, and durable model binaries remain prohibited by this incident package.

## Fail-closed consequence

The executor binding must be reblocked as:

`BLOCKED_PENDING_QWEN_RAW_CODE_RUNTIME_CONTRACT_REPAIR`

This incident creates no retry authority, no external dispatch authority, and no cross-run resume authority. The same one-shot topology must not be redispatched.

B012 remains `PENDING`. B013 remains unauthorized to open. A separately qualified runtime-contract repair and any required equivalence migration must become canonical before another model execution can be considered.
