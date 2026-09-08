# B012 Qwen Staged Recovery Infrastructure Cancellation — Run 34231845282

## Classification

Run `34231845282` preserved durable checkpoints through `init`, `source`, and `quantize`, then the GitHub-hosted runner received a shutdown signal while the frozen raw-code proxy was executing. The raw-code stage was cancelled; Stage 04 upload, Stage 05 finalization, final JSON upload, and the explicit cleanup step did not run to completion.

The canonical classification for this attempt is:

`B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN`

This is not a model-quality verdict. It is also not the earlier `NO_DURABLE_RECOVERY_RESULT` class because this staged topology successfully preserved three JSON checkpoint artifacts before the interruption.

## Exact live evidence

- workflow: `B012 Qwen raw-code staged recovery`
- run: `34231845282`
- job: `102079676195`
- candidate: `qwen3.5-0.8b-control`
- canonical main at dispatch: `98feee7765cbf64428f149f885519cef76800caf`
- run created: `2026-09-08T13:25:14Z`
- raw-code stage began: `2026-09-08T13:35:05Z`
- runner shutdown signal: `2026-09-08T13:44:52.5488705Z`
- run final update: `2026-09-08T13:44:57Z`
- workflow conclusion: `failure`
- raw-code-stage conclusion: `cancelled`
- finalize-stage conclusion: `skipped`
- explicit cleanup conclusion: `skipped`
- workflow timeout budget: `45` minutes

The shutdown occurred before the configured workflow timeout budget. The available log proves a runner shutdown signal and cancellation, but it does not prove a more specific platform root cause. The incident therefore remains infrastructure-classified without attributing an unproven cancellation source.

## Durable progress preserved

Exactly three JSON checkpoint artifacts are durable:

1. Stage 01 `init`: artifact `10058420119`, digest `sha256:fe42fd594f5a5501f25ce2fe2f9449031e1760eec90d71bf2983f6965aa297fc`.
2. Stage 02 `source`: artifact `10058479985`, digest `sha256:1884986d415cacfc7d51b072dd87124cd6c0577e33585a3ec199019883f4e71b`.
3. Stage 03 `quantize`: artifact `10058522893`, digest `sha256:ff094686270f646371a9b218ce0fbc8378d5b2b0cbc4d9f8794b5bfcb6c86f68`.

Stage 02 durably proves all nine exact B010 Qwen files were reacquired and hash/size verified, totaling `1769897109` bytes. The canonical weight body remained SHA-256 `c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c` at `1746942600` bytes.

Stage 03 durably proves exact Q4 regeneration matched the previously qualified identity: Q4_K_M SHA-256 `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`, size `541903296` bytes, with `matches_prior_stage03=true`.

These checkpoints prove source and Q4 equivalence only. They do not prove a raw-code result or candidate admission.

## Unproven surfaces

No Stage 04 or Stage 05 artifact exists. Therefore the repository must not infer:

- any completed raw-code case or score;
- any raw-code success/failure verdict;
- any candidate admission decision;
- any model-quality verdict;
- completion of final recovery evidence;
- completion of the explicit ephemeral cleanup step.

The hosted runner terminated the orphan `llama-cli` process after the shutdown. No durable model/GGUF artifact was uploaded. Explicit cleanup completion remains `NOT_PROVEN` because the workflow cleanup step itself was skipped.

## Governance consequence

B012 remains `PENDING`; B013 remains blocked by B012. The executor binding must fail closed as `BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR` until a genuinely different recovery topology is separately reviewed and activated.

This evidence creates no retry authority, external dispatch authority, candidate expansion, revision/file expansion, training authority, paid-compute authority, paid-model-API authority, production-release authority, Git model binaries, or founder-machine model binaries.

The unchanged staged command must not be reissued from this incident. A later dispatch is only eligible after a new topology repair and separate canonical activation lifecycle re-prove the existing B012 authority and exact-main eligibility.

## Required next action

Design a new repository-only durability repair that preserves the frozen candidate, Q4 identity, raw-code prompts, sampling parameters, runtime identities, and zero-cost boundary while materially reducing the amount of uncheckpointed work before and within raw-code execution. The repair itself must perform no model access and must pass exact-head qualification, independent semantic review, mandatory premerge verification, guarded merge, and exact-main postmerge verification before any later dispatch.
