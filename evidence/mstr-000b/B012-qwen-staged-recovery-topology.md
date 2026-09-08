# B012 Qwen Raw-Code Recovery Staged Durability Repair

## Classification

This package is a repository-only topology repair for the exact authorized B012 Qwen raw-code recovery path. It performs no model access or model execution and creates no retry, dispatch, training, paid-compute, candidate-expansion, revision-expansion, or file-expansion authority.

The package remains `READY_FOR_SEPARATE_CANONICAL_ACTIVATION` until a separate activation change materializes the reviewed workflow on canonical `main` and binds it into the B012 executor manifest.

## Triggering evidence

The repair responds to two failed recovery attempts without converting either failure into a model-quality verdict:

- run `34163308005`: recovery failed before raw-code execution and produced no usable raw-code verdict;
- run `34169060075`: the GitHub-hosted runner received a shutdown signal while the monolithic recovery step was still running; upload and cleanup steps were skipped and the artifact API contained no durable recovery result.

PR #193 canonicalized the latter incident and changed the B012 executor binding to `BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR`.

## Root cause

The activated recovery topology placed pinned toolchain preparation, exact source reacquisition, exact Q4 regeneration, and the frozen raw-code proxy inside one long workflow step. The only durable JSON upload occurred after that step returned. A hosted-runner shutdown could therefore erase all in-step evidence, including any locally written fail-closed JSON.

Increasing the timeout does not repair this durability boundary.

## Repair

The staged recovery preserves one ephemeral job and the same model/runtime semantics while introducing five explicit stages:

```text
init
-> source
-> quantize
-> raw-code
-> finalize
```

Every completed stage writes a JSON checkpoint and is followed by a pinned `actions/upload-artifact` JSON-only upload before the next stage begins.

The boundaries are deliberate:

1. `init` prepares the exact pinned replay/runtime toolchains before model access.
2. `source` reacquires and verifies only the exact B010 Qwen files and durably records the verification identities.
3. `quantize` regenerates the exact Q4 artifact and requires the canonical Stage 03 SHA-256 and size before durably recording that identity.
4. `raw-code` executes only the frozen raw-code proxy and durably records its result.
5. `finalize` emits the bounded recovery result without making a candidate-admission decision.

If a hosted runner shuts down during a later stage, already-uploaded earlier-stage JSON remains durable. The interrupted stage remains unproven until a later governed dispatch; elapsed wall time is never used to infer completion.

## Preserved exact scope

The repair preserves:

- candidate: `qwen3.5-0.8b-control`;
- prior qualification run: `34155931982`;
- prior durable Stage 05 checkpoint SHA-256: `2141781456f54623e6b87c9e7528ea767f49062670fbb62b77d639b3ec3d1f88`;
- expected Q4_K_M SHA-256: `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`;
- expected Q4_K_M size: `541903296` bytes;
- exact B010 source identities/files;
- pinned T031 replay dependency identity;
- pinned llama.cpp conversion/runtime commits and build flags;
- frozen raw-code manifest and sampling semantics;
- no prefill rerun;
- no decode rerun;
- JSON-only durable outputs;
- no model binaries in Git or on the founder machine;
- zero-USD ceiling and no paid model API;
- no training or weight-changing operation.

## Activation boundary

This package does not change the active workflow. A separate activation PR is required to:

1. re-prove exact-main B012 eligibility and the existing canonical B012 Founder authority;
2. bind this exact repair-manifest/script/workflow identity into `B012-executor-toolchain-binding.json`;
3. materialize the staged workflow as `.github/workflows/b012-qwen-raw-code-recovery.yml`;
4. keep the binding fail closed until that activation passes exact-head qualification, independent substantive semantic review, mandatory premerge verification, guarded merge, and exact-main postmerge verification.

Only after that lifecycle may a new exact owner issue-comment dispatch use:

`B012_RECOVER_RAW_CODE_STAGED qwen3.5-0.8b-control 34155931982`

The command is a dispatch surface under the already-canonical B012 authority. This package itself grants no new authority.
