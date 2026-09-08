# B012 Qwen Case-Checkpoint Recovery Infrastructure Cancellation — Run 34265475666

## Classification

Run `34265475666` preserved durable JSON checkpoints through `init`, `source`, and `quantize`, then the GitHub-hosted runner received a shutdown signal while the first frozen raw-code case, `python-clamp`, was executing. The `python-clamp` checkpoint upload, all later raw-code cases, finalization, and explicit cleanup did not run to completion.

The canonical classification for this attempt is:

`B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN`

This is an infrastructure cancellation classification, not a model-quality verdict and not a candidate-admission decision.

## Exact live evidence

- workflow: `B012 Qwen raw-code case-checkpoint recovery`
- run: `34265475666`
- attempt: `1`
- job: `102193622602` (`recover`)
- candidate: `qwen3.5-0.8b-control`
- canonical main at dispatch: `145be15a32448d00fada0e2d9bf736f265c942a1`
- run created: `2026-09-08T18:50:57Z`
- runner shutdown signal: `2026-09-08T19:07:25.8017163Z`
- run final update: `2026-09-08T19:07:31Z`
- workflow conclusion: `failure`
- interrupted stage: `raw-code-python-clamp`
- interrupted stage conclusion: `cancelled`
- interrupted checkpoint upload: `skipped`
- later raw-code stages: `skipped`
- finalize: `skipped`
- explicit cleanup: `skipped`
- workflow timeout budget: `45` minutes

The available log proves a runner shutdown signal and cancellation. It does not prove a more specific platform root cause.

## Durable checkpoint transport captured

Exactly three required stage checkpoint artifacts were uploaded before the interruption and were captured before expiry:

1. Stage 01 `init`
   - artifact id: `10071904755`
   - artifact digest: `sha256:f71e76471078a7d457e85cb2b5655f11a63e9f88e1ade11e645b8503e66af576`
   - canonical checkpoint SHA-256: `fabc44925fdb8243d5eeca856b6e9b5fd83db54c4dc9cca27967409382721fb4`
2. Stage 02 `source`
   - artifact id: `10071960486`
   - artifact digest: `sha256:e419d6a79478b9b3626cf2dd1bc702df8dfb4f9c966cae3c182035d17581dcd3`
   - canonical checkpoint SHA-256: `38f9693bd55f77f8634ce01dec0e932e990790735399ade55f0a4230bdbf585e`
3. Stage 03 `quantize`
   - artifact id: `10071997161`
   - artifact digest: `sha256:422d386a40b82855025092186502312a402e9a3953af45a2e70e199e4c846520`
   - canonical checkpoint SHA-256: `ed15864153a8e4b26fffca5298dcbd80763e9c7edd0106845555b8325b079205`

The terminal case-state JSON captured from the Stage 03 cumulative transport has SHA-256 `e5accce8487556a649db0c147a3c5876c0b31f8c1c0b334e48510f3680f58733`.

Only JSON reports/state are canonicalized. No GGUF, safetensors, model source body, executable, or other model binary is committed to Git.

## Durable progress proven

The captured source checkpoint proves all nine exact B010 Qwen files were reacquired and verified, totaling `1769897109` bytes. The frozen weight body remains:

- SHA-256: `c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c`
- size: `1746942600` bytes

The quantize checkpoint proves exact Q4 regeneration matched the previously qualified identity:

- F16 SHA-256: `198297c5988d7420ef3939911c5a8e1a018a7404e7bf6fb5e6965c3cc9a04045`
- F16 size: `1557662144` bytes
- Q4_K_M SHA-256: `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`
- Q4_K_M size: `541903296` bytes
- prior Stage 03 identity match: `true`

These checkpoints prove source and Q4 equivalence only.

## Raw-code result remains unproven

No raw-code case checkpoint artifact exists. The first case did not reach its durable checkpoint boundary. Therefore this incident records:

- durably completed raw-code cases: `0`
- raw-code result: `NONE_DURABLY_PROVEN`
- candidate admission decision: `NONE`
- model-quality verdict: `NONE`
- candidate execution completion: `NOT_PROVEN`
- explicit cleanup completion: `NOT_PROVEN`

The repository must not infer a raw-code score, pass/fail verdict, candidate admission, or model-quality conclusion from this attempt.

## Governance consequence

B012 remains `PENDING`; B013 remains blocked by B012.

The active case-checkpoint topology explicitly creates neither same-topology redispatch authority nor cross-run resume authority. This incident therefore does not authorize repeating `B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982`.

The executor binding must fail closed as:

`BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR`

until a genuinely different recovery topology is separately reviewed and activated under canonical governance.

This evidence creates no retry authority, external-dispatch authority, candidate expansion, revision/file expansion, training authority, weight-changing authority, paid-compute authority, paid-model-API authority, production-release authority, Git model binaries, or founder-machine model binaries.

## Required next action

Canonicalize this incident and all captured required checkpoint JSON through the normal branch, exact-head qualification, independent semantic/security review, mandatory premerge verification, guarded merge, and exact-main postmerge verification lifecycle.

After this incident is canonical, design a new repository-only durability repair that preserves the exact candidate, revision/files, source verification, Q4 identity, frozen raw-code manifest, prompts, sampling, runtime/tool identities, zero-cost boundary, and no-admission-by-proxy semantics while materially reducing the uncheckpointed execution boundary inside a raw-code case.

Repair review is not activation. Activation is not dispatch. Any later external dispatch must independently prove exact-main B012 eligibility and whatever explicit authority canonical governance requires at that later frontier.

Machine-readable incident evidence:

`artifacts/results/equivalent/B012/failures/B012-qwen3.5-0.8b-control-raw-code-case-checkpoint-recovery-run-34265475666.json`

Machine-readable incident SHA-256:

`e03d0030cb500a2fc97ec3a2f66c17b463028582643d9169c7be6994bc955152`
