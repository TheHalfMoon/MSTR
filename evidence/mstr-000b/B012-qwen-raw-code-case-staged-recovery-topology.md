# B012 Qwen Raw-Code Case-Staged Durability Repair

## Status

This file records a **non-active repository repair package** for B012. It does not activate a workflow, perform model access, execute a model, create retry authority, create external-dispatch authority, make a candidate-admission decision, or make a model-quality decision.

The repair package is based on canonical main:

```text
2d35efe6d7350f6aa0241ee9de128134cd321f90
```

The triggering canonical incident is Qwen staged recovery run `34231845282`, canonicalized by PR #196 and post-merge verification run `34250328560`.

## Proven Incident Boundary

Canonical incident evidence proves:

```text
CANDIDATE = qwen3.5-0.8b-control
DURABLE_STAGES = init, source, quantize
RAW_CODE_STAGE = cancelled
RAW_CODE_RESULT = NONE_DURABLY_PROVEN
CANDIDATE_ADMISSION_DECISION = NONE
MODEL_QUALITY_VERDICT = NONE
SAME_STAGED_TOPOLOGY_REDISPATCH_AUTHORIZED = false
SEPARATE_TOPOLOGY_REPAIR_REQUIRED = true
```

The incident does not prove which raw-code case, if any, completed before runner shutdown because the consumed topology executed all three frozen raw-code cases inside one workflow step and uploaded JSON only after the whole stage returned.

## Repair Goal

Reduce the maximum uncheckpointed raw-code work from the complete three-case proxy to exactly one frozen case while preserving the original candidate, source files, Q4 identity, raw-code benchmark manifest, prompts, sampling parameters, runtime/tool revisions, helper implementation, and observational interpretation.

The proposed non-active topology is:

```text
init
-> source
-> quantize
-> raw-code-python-clamp
-> upload JSON checkpoint
-> raw-code-python-dedupe
-> upload JSON checkpoint
-> raw-code-python-safe-divide
-> upload JSON checkpoint
-> finalize
```

The frozen raw-code case order remains:

```text
python-clamp
python-dedupe
python-safe-divide
```

Each case is executed by the existing `run_raw_code_proxy()` helper using a one-task projection of the unchanged canonical raw-code manifest. The finalizer re-aggregates the three one-case observations in the original order and retains:

```text
interpretation = OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION
```

## Exact Preserved Identities

```text
PRIOR_QUALIFICATION_RUN = 34155931982
TRIGGERING_INCIDENT_RUN = 34231845282
Q4_K_M_SHA256 = 177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa
Q4_K_M_SIZE_BYTES = 541903296
RAW_CODE_MANIFEST_SHA256 = 038586bb8156add6bb2de8573a9d15d0f1201909c36820a6cc608a2b5d393349
RAW_CODE_HELPER_SHA256 = bd6d34afd8af60497a4971bb7245fc359c4132bad3772be212b6848aa73060d8
CASE_STAGED_SCRIPT_SHA256 = e6264c2930d61e54f190a07ddc645162b658b04f694bc33a94b7c70df4a127d7
CASE_STAGED_WORKFLOW_SHA256 = dc1aad036035a721473a727be28ffe051cb546e86c899a1efcd3c09f624c4565
REPAIR_MANIFEST_SHA256 = 95fed054b7e4d6718d0ae283158cc2732843f62a27c5bb78662342bf48aad0b9
```

## Authority Boundary

This repair package creates or performs none of:

```text
AUTHORITY_SCOPE_MODIFICATION
AUTHORITY_TRANSFER
RETRY_AUTHORITY
EXTERNAL_DISPATCH_AUTHORITY
NEW_CANDIDATE_ACCESS
CANDIDATE_REVISION_OR_FILE_EXPANSION
PREFILL_RERUN
DECODE_RERUN
TRAINING
WEIGHT_CHANGING_TRAINING
PAID_COMPUTE
PAID_MODEL_API
PRODUCTION_RELEASE
MODEL_ACCESS
MODEL_EXECUTION
GIT_MODEL_BINARIES
FOUNDER_MACHINE_MODEL_BINARIES
```

Existing authority remains:

```text
B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION
```

This package does not consume that authority because it does not dispatch or execute model work.

## Activation Boundary

The package is intentionally not active. It does not modify:

```text
.github/workflows/b012-qwen-raw-code-recovery.yml
artifacts/manifests/B012-executor-toolchain-binding.json
benchmarks/manifests/B012-raw-code-proxy.json
colab/mstr_b012_raw_code.py
```

A separate activation PR is required after this exact repair head completes fresh qualification, independent semantic review, mandatory premerge verification, guarded merge, and post-merge verification.

A later activation must re-prove exact-main B012 eligibility and the existing Founder authority, bind the exact repair manifest/script/workflow hashes into the executor binding, and materialize the reviewed workflow as the active recovery workflow.

The future exact owner command proposed by this repair is:

```text
B012_RECOVER_RAW_CODE_CASE_STAGED qwen3.5-0.8b-control 34155931982 34231845282
```

This repair package does **not** issue that command. Repair review is not activation, activation is not dispatch, and dispatch success is not canonical B012 closeout.

## Completion Boundary

This repair package is not canonical merely because these files exist on a branch. Canonicalization requires:

1. exact-head qualification;
2. independent substantive semantic review;
3. review-state reconciliation;
4. mandatory premerge verification;
5. guarded merge with the expected head SHA;
6. exact-main post-merge verification.

Only then may a separate activation lifecycle begin.
