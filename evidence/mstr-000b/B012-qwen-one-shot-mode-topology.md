# B012 Qwen One-Shot Raw-Code Mode Repair

## Scope

This package is an inert B012 repair for `qwen3.5-0.8b-control`. It does not activate a workflow, access model weights, execute a model, create retry or dispatch authority, make a candidate-admission decision, or change B012 benchmark inputs.

Exact repair base:

```text
CANONICAL_MAIN = 9ff1680c21be366f11133a4ba2e68ebe0fc1e53b
PRIOR_QUALIFICATION_RUN_ID = 34155931982
TRIGGERING_INCIDENT_RUN_ID = 34265475666
INCIDENT_POSTMERGE_RUN_ID = 34274596048
CANDIDATE_ID = qwen3.5-0.8b-control
```

The triggering incident remains classified as `B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN`. Its durable evidence proves `init`, `source`, and `quantize`, including the exact Q4_K_M identity, but proves no completed raw-code case. The incident therefore remains non-adjudicative: raw-code result `NONE_DURABLY_PROVEN`, model-quality verdict `NONE`, and candidate-admission decision `NONE`.

## Execution-mode ambiguity

The pinned B012 llama.cpp runtime revision is:

```text
3173a56471c1753650cd806694145ffd6dcace67
```

At that exact runtime revision, `llama-cli` exposes `--conversation` and `--no-conversation`, and its documented default permits conversation mode to be auto-enabled when a chat template is available. Conversation mode also enables interactive behavior.

The frozen B012 raw-code proxy is not a chat benchmark. Its semantics are direct raw completion: each frozen Python prompt is passed to the runtime, the returned completion is concatenated directly with that prompt, and `ast.parse(prompt + completion)` provides the observational syntax check.

The Qwen source is conversational-capable, so leaving the runtime mode implicit creates an avoidable execution-mode ambiguity. This repair makes the intended one-shot raw-completion mode explicit by adding exactly `--no-conversation` in an isolated helper.

This is semantic hardening, not a root-cause claim. The repository does **not** claim that auto-conversation caused hosted-runner termination in run `34265475666`.

## Semantic preservation

The repair preserves all frozen benchmark and artifact identities:

- raw-code manifest unchanged;
- case set and order unchanged: `python-clamp`, `python-dedupe`, `python-safe-divide`;
- prompts and required substrings unchanged;
- context tokens `2048`;
- generated tokens `96`;
- threads `2`;
- GPU layers `0`;
- temperature `0.0`;
- seed `42`;
- pinned llama.cpp runtime revision unchanged;
- Q4_K_M SHA-256 `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`;
- Q4_K_M size `541903296` bytes;
- per-case JSON checkpoint topology unchanged;
- score remains observational and is not an admission gate.

The canonical shared helper `colab/mstr_b012_raw_code.py` remains byte-for-byte unchanged. The one-shot behavior exists only in `colab/mstr_b012_raw_code_one_shot.py`, and `colab/mstr_b012_qwen_raw_code_one_shot.py` binds that helper to the already-reviewed case-checkpoint executor only after a later canonical activation record exists.

## Authority and storage boundary

The only relevant execution authority remains `B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION`. This repair does not modify or transfer it.

```text
CANDIDATE_EXPANSION = false
REVISION_OR_FILE_EXPANSION = false
RETRY_AUTHORITY_CREATED = false
EXTERNAL_DISPATCH_AUTHORITY_CREATED = false
CROSS_RUN_RESUME_AUTHORITY_CREATED = false
TRAINING = false
WEIGHT_CHANGING_TRAINING = false
PAID_COMPUTE = false
PAID_MODEL_API = false
PAID_COST_USD = 0.0
GIT_MODEL_BINARIES = 0
FOUNDER_MACHINE_MODEL_BINARIES = 0
PRODUCTION_RELEASE = false
```

No model or generated binary is introduced by this package. Durable repository evidence remains text/JSON only.

## Activation boundary

Repair review is not activation, and activation is not dispatch.

This package intentionally does not modify `.github/workflows/b012-qwen-raw-code-recovery.yml` or `artifacts/manifests/B012-executor-toolchain-binding.json`. A later, separate canonical activation change must bind the exact repair hashes and may materialize the owner-scoped command:

```text
B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982
```

That activation must independently pass exact-head qualification, substantive semantic/security review, mandatory premerge verification, guarded merge, exact-main postmerge verification, live B012 eligibility, and re-verification of the existing Founder authority before any external dispatch is considered.
