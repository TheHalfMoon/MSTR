# B012 Mellum Repeated Infrastructure Cancellation — Run 34068813113

## Classification

Run `34068813113` did not produce a B012 qualification result. The GitHub-hosted runner received a shutdown signal while `colab/mstr_b012_execute.py` was still running. GitHub cancelled the execution step and skipped the later durable-evidence upload step. The workflow artifact API is empty.

The canonical classification for this attempt is:

`B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_NO_DURABLE_RESULT`

This is not a model-quality verdict and is not equivalent to `B012_EXECUTION_FAILED_CLOSED`, because the executor did not complete its own result or failure-record path.

## Exact live evidence

- workflow: `B012 equivalent candidate qualification`
- run: `34068813113`
- job: `101582272038`
- candidate: `mellum-4b`
- canonical main at dispatch: `61bacde1ee21831080accc8a226433562a6aeaf9`
- run created: `2026-09-07T00:07:53Z`
- execution step began: `2026-09-07T00:07:58Z`
- runner shutdown signal: `2026-09-07T01:16:53.057Z`
- run final update: `2026-09-07T01:16:57Z`
- workflow conclusion: `failure`
- execution-step conclusion: `cancelled`
- durable-evidence upload conclusion: `skipped`
- workflow artifacts: none

The job log reports `The runner has received a shutdown signal` followed by `The operation was canceled.` There is no executor-authored B012 failure JSON for this attempt.

## Recurrence finding

This is the second governed `mellum-4b` B012 execution to end with the same infrastructure classification and no durable executor result. The prior incident is run `34064172421`, job `101569918156`.

Both executions used the same canonical single-job topology: one long `Execute governed B012 qualification` step followed by one `if: always()` JSON upload step. A runner shutdown during the executor prevents the later upload step from running, so all runner-local diagnostic/result JSON can be lost together with the ephemeral VM.

The recurrence therefore establishes a workflow-level evidence durability defect for this topology. It does not establish a Mellum quality defect and does not prove which internal executor phase was active at either shutdown.

## Evidence limits

Because the executor was terminated externally and produced no durable result, this evidence does **not** establish:

- any model-quality verdict;
- candidate execution completion;
- whether model access had already occurred before shutdown;
- any benchmark result;
- any raw-code result;
- any B012 qualification decision.

The authorized executor contains no training path. The attempt did not expand candidate authority, use a paid model API, authorize paid compute, or authorize persistent model binaries.

## Recovery boundary

This evidence does not create retry authority. It specifically does not authorize another execution using the same unmodified single-job evidence-loss topology.

The canonical storage policy continues to prohibit Git persistence, founder-machine persistence, or default cloud persistence of model/GGUF binaries. A recovery must preserve the ephemeral-binary lifecycle and may durably emit only reports, manifests, evidence, and other authorized small outputs unless a separate founder storage decision is canonicalized.

A separately reviewed topology repair must be canonical before another B012 external execution is considered. That repair must preserve the exact B012 authority, candidate set, source revisions/files, benchmark semantics, USD `0.00` cost ceiling, and no-training boundary.

Machine-readable evidence: `artifacts/results/equivalent/B012/failures/B012-mellum-4b-run-34068813113.json`.
