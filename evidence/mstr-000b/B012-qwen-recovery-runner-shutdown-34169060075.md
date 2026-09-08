# B012 Qwen Raw-Code Recovery Infrastructure Cancellation — Run 34169060075

## Classification

Run `34169060075` did not produce a durable Qwen raw-code recovery result. The GitHub-hosted runner received a shutdown signal while `colab/mstr_b012_qwen_raw_code_recovery.py` was still running. GitHub cancelled the recovery step and skipped both the later JSON upload step and the explicit cleanup step. The workflow artifact API is empty.

The canonical classification for this attempt is:

`B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RECOVERY_RESULT`

This is not a model-quality verdict and is not equivalent to `B012_RAW_CODE_RECOVERY_FAILED_CLOSED`, because the recovery executor did not complete its own success or fail-closed JSON path.

## Exact live evidence

- workflow: `B012 Qwen raw-code recovery`
- run: `34169060075`
- job: `101885732522`
- candidate: `qwen3.5-0.8b-control`
- canonical main at dispatch: `5e74e77c1fc86d4ebc7e64654f45bd18f565edd6`
- run created: `2026-09-07T23:09:11Z`
- recovery step began: `2026-09-07T23:09:17Z`
- runner shutdown signal: `2026-09-07T23:30:01.6143454Z`
- run final update: `2026-09-07T23:30:06Z`
- workflow conclusion: `failure`
- recovery-step conclusion: `cancelled`
- recovery-JSON upload conclusion: `skipped`
- explicit ephemeral cleanup conclusion: `skipped`
- workflow artifacts: none

The job log reports `The runner has received a shutdown signal.` followed by `The operation was canceled.` There is no executor-authored recovery success/failure JSON for this attempt.

## Preserved prior qualification evidence

This incident does not modify the durable Qwen Stage 01–05 evidence from qualification run `34155931982`.

The preserved Stage 05 checkpoint remains:

- artifact: `10031329744`
- checkpoint SHA-256: `2141781456f54623e6b87c9e7528ea767f49062670fbb62b77d639b3ec3d1f88`
- Q4_K_M SHA-256 expected from the durable Stage 03/05 evidence: `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`
- Q4_K_M size: `541903296` bytes

The interrupted recovery did not durably prove whether exact Q4 regeneration completed, which raw-code case (if any) began or completed, or whether ephemeral cleanup completed. Those facts remain `UNKNOWN_UNRECORDED` / `NOT_PROVEN`; they must not be inferred from elapsed wall time.

## Recurrence finding

The recovery topology had already produced failed recovery run `34163308005` before the Q4 provenance correction. Run `34169060075` used the same activated single-job recovery topology after that correction. It again ended without durable recovery JSON, this time because the hosted runner shut down after approximately twenty-one minutes.

The activated recovery performs pinned Python-toolchain installation, two pinned llama.cpp builds, exact Qwen source reacquisition, exact Q4 regeneration, and all three frozen raw-code cases before the only durable JSON upload. A hosted-runner shutdown at any point before that upload can therefore lose the entire recovery result.

The recurrence establishes that repeating the same recovery topology is not an acceptable evidence-preserving next action. It does not establish a Qwen quality defect and does not create retry or dispatch authority.

## Evidence limits

This evidence does **not** establish:

- any Qwen raw-code score or completion;
- any candidate admission decision;
- any model-quality verdict;
- whether source reacquisition completed before shutdown;
- whether exact Q4 regeneration completed before shutdown;
- whether any raw-code case completed before shutdown;
- whether ephemeral cleanup completed after the shutdown.

No durable model/GGUF artifact was produced by the workflow artifact API. The canonical authority boundaries remain unchanged: no training, no candidate/revision/file expansion, no paid compute/API authority, no Git model binaries, and no founder-machine model binaries.

## Recovery boundary

The active Qwen recovery path must now be treated as blocked pending a separately reviewed topology repair. This incident does not authorize repeating `B012_RECOVER_RAW_CODE qwen3.5-0.8b-control 34155931982` using the unchanged recovery topology.

A repair must preserve the exact Qwen candidate/revision/files, the frozen raw-code manifest and sampling parameters, the exact pinned tool/runtime identities or an explicitly reviewed equivalent binding, Q4 identity verification, zero-USD ceiling, ephemeral model-binary lifecycle, and no-training boundary. It must make partial progress durable enough that another hosted-runner shutdown cannot erase all recovery evidence.

Machine-readable evidence: `artifacts/results/equivalent/B012/failures/B012-qwen3.5-0.8b-control-raw-code-recovery-run-34169060075.json`.
