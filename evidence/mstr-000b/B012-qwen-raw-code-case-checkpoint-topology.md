# B012 Qwen raw-code per-case durability topology repair

Status: `READY_FOR_SEPARATE_CANONICAL_ACTIVATION`

## Canonical incident prerequisite

This repair is based on canonical `main` `2d35efe6d7350f6aa0241ee9de128134cd321f90`, which merged PR #196 and recorded run `34231845282` as:

`B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN`

Post-merge verification run `34250328560` completed successfully before this repair package was created.

The incident proves durable Stage 01, Stage 02, and Stage 03 evidence, including the exact Q4 identity:

- SHA-256: `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`
- size: `541903296`

It does not prove any raw-code result, model-quality verdict, candidate admission decision, finalization, or cleanup completion.

## Repair objective

The prior staged topology made all three frozen raw-code cases one execution step and uploaded durable JSON only after the complete case set returned. A hosted-runner shutdown during that step therefore left no durable raw-code case result.

This package changes only the recovery evidence topology. It does not change the frozen benchmark.

The proposed non-active topology is:

```text
init
-> source
-> quantize
-> raw-code-python-clamp
-> upload JSON
-> raw-code-python-dedupe
-> upload JSON
-> raw-code-python-safe-divide
-> upload JSON
-> finalize
-> upload JSON
-> always cleanup
```

Every completed raw-code case becomes durable before the next case begins. The maximum raw-code work that can remain uncheckpointed is one frozen case.

## Frozen semantics

The exact raw-code case order remains:

1. `python-clamp`
2. `python-dedupe`
3. `python-safe-divide`

The canonical manifest `benchmarks/manifests/B012-raw-code-proxy.json` is unchanged.

The repair preserves:

- exact candidate `qwen3.5-0.8b-control`;
- exact B010 revision and file set;
- exact source verification;
- exact Q4_K_M identity;
- exact pinned llama.cpp runtime/tool revisions and build flags;
- exact prompts;
- exact sampling and seed;
- exact three-case task set and order;
- the existing `run_raw_code_proxy()` helper;
- no prefill/decode rerun;
- observational raw-code semantics only;
- no admission-by-proxy.

Each raw-code case independently re-verifies canonical-main continuity and exact Q4 identity before model execution.

## Durability and cleanup

Durable workflow artifacts remain JSON-only. No GGUF, safetensors, model source file, executable, or other model binary is uploaded.

The cleanup step remains under an `always()` boundary. If infrastructure termination prevents cleanup from executing, cleanup completion remains unproven and must be recorded fail-closed.

This repair does not claim cross-run resume authority. A future infrastructure interruption must be canonicalized before any later execution lifecycle is authorized. The durable per-case checkpoints make any completed case evidence available to that later governed lifecycle.

## Authority boundary

```text
SOURCE_CODE_PERMISSION != DATA_ADMISSION != MODEL_WEIGHT_AUTHORITY != TRAINING_AUTHORITY != EXTERNAL_EFFECT_AUTHORITY
```

This repair package creates none of the following:

- retry authority;
- external dispatch authority;
- training authority;
- weight-changing authority;
- paid-compute authority;
- paid-model-API authority;
- candidate expansion;
- revision/file expansion;
- production-release authority.

Recorded paid cost remains `0.0`.

## Activation boundary

This package does not modify `.github/workflows/b012-qwen-raw-code-recovery.yml` and therefore does not activate the new topology.

A separate canonical activation lifecycle is required. Only that later activation may bind the exact reviewed manifest/script/workflow hashes into `B012-executor-toolchain-binding.json` and materialize the new active workflow after independently re-proving current-main B012 eligibility and the existing Founder authority.

The later exact owner command is proposed as:

`B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982`

Repair review is not activation. Activation is not dispatch.


## Canonical checkpoint evidence lifecycle

GitHub Actions checkpoint artifacts are transient transport, not the canonical long-term evidence store. The seven-day artifact retention window is intentionally bounded and does not authorize a new persistent cloud store or paid storage. Canonical storage policy remains `docs/canonical/STORAGE_ARCHITECTURE.md`: JSON reports, manifests, hashes, evidence, and reports return to Git; model and derived binaries remain ephemeral.

Every required checkpoint artifact from an authorized case-checkpoint dispatch MUST be captured, hash-verified, and canonicalized into Git evidence before B012 dispatch closeout or any candidate-admission decision. If any required checkpoint artifact is missing, expired, inconsistent, or cannot be canonicalized, the run remains fail-closed and B012 completion/admission is not proven. Runner cleanup may occur after artifact upload because uploaded JSON survives the ephemeral VM; cleanup does not substitute for canonical evidence capture.

The stage writer also commits a stage checkpoint before persisting the completed-stage state. A checkpoint-write failure therefore cannot leave the durable state claiming that a stage completed when its required checkpoint was never written.
