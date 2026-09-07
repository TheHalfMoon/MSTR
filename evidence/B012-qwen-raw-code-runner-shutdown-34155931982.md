# B012 Qwen Raw-Code Runner Shutdown — Run 34155931982

**Task:** `MSTR-000B / B012`  
**Candidate:** `qwen3.5-0.8b-control`  
**Canonical main at dispatch:** `7ebb02c3c46c64d226d412def8bc88fd5f2c1594`  
**Workflow run:** `34155931982`  
**Workflow job:** `101847640786`  
**Classification:** `B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_AFTER_STAGE05_NO_RAW_CODE_RESULT`

## Durable evidence before shutdown

The staged topology preserved valid JSON checkpoints through Stage 05:

- Stage 01 `init`: artifact `10031093785`
- Stage 02 `source`: artifact `10031125136`
- Stage 03 `quantize`: artifact `10031142398`
- Stage 04 `prefill`: artifact `10031325318`
- Stage 05 `decode`: artifact `10031329744`

The Stage 05 artifact digest is
`sha256:726e154a9e94c67eea4b0bdec5440912af6055e46cac9f95861872a044616fee`,
and the Stage 05 checkpoint JSON SHA-256 is
`2141781456f54623e6b87c9e7528ea767f49062670fbb62b77d639b3ec3d1f88`.

The durable Stage 03 evidence records Q4_K_M SHA-256
`177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`
at `541903296` bytes. Stage 04 and Stage 05 completed under the canonical
B012 benchmark contract.

## Shutdown

Stage 06 `raw-code` started, but the GitHub-hosted runner emitted
`The runner has received a shutdown signal.` at
`2026-09-07T19:54:56.1281340Z`. The Stage 06 step concluded `cancelled`.
No Stage 06 checkpoint or final Stage 07 evidence was uploaded.

## Evidence limits

- raw-code result: `NONE`
- candidate admission decision: `NONE`
- model-quality verdict from this shutdown: `NONE`
- training: `false`
- paid cost: `USD 0.00`
- retry authority created by this evidence: `false`
- external-dispatch authority created by this evidence: `false`

This incident does not invalidate the already durable Stage 01–05
observations and does not convert infrastructure cancellation into a
candidate-quality verdict.

## Recovery boundary

The separately reviewable recovery package is intentionally inert. It is
limited to exact Qwen source reacquisition, exact Q4 regeneration with
identity matching to the durable Stage 03 Q4_K_M observation, and the
missing raw-code proxy. It does not rerun prefill or decode and does not
perform candidate admission.

A separate activation change, exact-main verification, and an explicit
canonical issue dispatch remain required before any recovery model access.

## Provenance correction — 2026-09-07

A later raw-code recovery attempt exposed an inconsistency in the repository copy of this incident record. The immutable Stage 03 artifact `10031142398` (artifact digest `sha256:925f5447fb6f93bbfedcdad1eab3b2cc9e95b3748f041e313b5fb96052a4aeb1`) and the Stage 05 artifact `10031329744` both record the Q4_K_M SHA-256 actually used by prefill/decode as `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa` at `541903296` bytes. The prior repository value `47f87d507130b70d7b54a159e7bf982e4fbe7dc75eae74e3cd9c9c9284805626` was therefore a provenance transcription error and is superseded by the durable workflow artifacts.

This correction changes no candidate verdict, authority, runtime metric, source revision, or model binary.
