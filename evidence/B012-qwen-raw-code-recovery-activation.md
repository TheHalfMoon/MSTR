# B012 Qwen raw-code recovery activation

## Scope

This repository change activates only the already-reviewed Qwen raw-code recovery package for the missing Stage 06 evidence from workflow run `34155931982`.

## Canonical provenance

- activation base main: `31549eeb78f2b3346c0915519cf5f4899ab47773`
- inert recovery package merge: PR #184 / `31549eeb78f2b3346c0915519cf5f4899ab47773`
- inert recovery package postmerge verification: run `34161170022` / SUCCESS
- postmerge evidence head: `3bdab353ee6aa7dd60510208b1e0f02545d3ebea`
- candidate: `qwen3.5-0.8b-control`
- exact recovery dispatch: `B012_RECOVER_RAW_CODE qwen3.5-0.8b-control 34155931982`

## Activation effect

The reviewed workflow spec is materialized byte-for-byte at `.github/workflows/b012-qwen-raw-code-recovery.yml`. The activated recovery manifest is SHA-256-bound into the existing B012 executor binding.

This activation performs no model access or execution. It creates no retry authority and no external-dispatch authority. It does not expand candidate, revision, file, network, quantization, runtime, cost, training, or durable-artifact scope.

External recovery execution remains separately gated by canonical postmerge verification of this activation and the exact owner-authored Issue #162 dispatch command.

```text
MODEL_ACCESS_DURING_ACTIVATION = NONE
MODEL_EXECUTION_DURING_ACTIVATION = NONE
TRAINING = false
PAID_COST_USD = 0.0
GIT_MODEL_BINARIES = 0
FOUNDER_MACHINE_MODEL_BINARIES = 0
```
