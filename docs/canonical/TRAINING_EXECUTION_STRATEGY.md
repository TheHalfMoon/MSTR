# MSTR Training Execution Strategy

**Status:** Canonical program-level planning input; no execution authority.  
**Checkpoint:** 2026-08-27.  
**Applies primarily to:** MSTR-001, MSTR-002, bounded experiments feeding MSTR-003, and MSTR-000B method/data preflight.  
**Product dependency:** NONE. The end-user MSTR product must not require Colab or Unsloth.

## 1. Purpose

Define an accessible, reproducible training path that maximizes code-specialized software-building capability without compromising MSTR's universal-laptop product goal.

The accessible stack remains:

```text
Google Colab
    = hosted GPU execution environment

Unsloth
    = preferred efficient compact-model training framework candidate

MSTR qualification/harness system
    = canonical evidence, manifests, trajectories, verifier health, research promotion and decisions

llama.cpp / GGUF-class runtime
    = primary local deployment qualification path
```

Colab and Unsloth are implementation candidates, not architectural authorities. A later Spec Kit may replace either if exact evidence shows a better path.

## 2. Training Philosophy

MSTR does not assume that post-training alone can turn an ordinary small foundation into the best possible code model.

The intended sequence is:

```text
PRODUCT-ALIGNED FOUNDATION
-> CODE-FOCUSED CONTINUED/MID-TRAINING
-> FIM / REPOSITORY CAPABILITY
-> EXECUTION-FILTERED SELF-ALIGNMENT
-> SOFTWARE-EVOLUTION / DIRECTION-TO-DONE SFT
-> FAILURE/RECOVERY/PREFERENCE TRAINING
-> BOUNDED EXECUTABLE AGENT RL
-> EXPORT + INTEGRITY + Q4 PRODUCT REGRESSION AFTER EACH MATERIAL STAGE
```

A strong code prior is a prerequisite to efficient agent optimization. Training data is chosen for alignment with real software-building work, not token volume alone.

## 3. Mandatory Pre-Training Inputs

Before any weight-changing task opens, exact canonical work must provide:

```text
stable product-aligned candidate/finalist identity
frozen model/tokenizer/artifact identity
MSTR loop/event/state/verifier semantics
Data Constitution
software-evolution contract
self-alignment + teacher-rescue policy
difficulty/frontier curriculum
verifier-health contract
test-generation curriculum
feature/greenfield curriculum
multi-fidelity research ladder
Q4 promotion contract
training-method tournament preflight
explicit founder authority
```

Missing required input blocks training.

## 4. Training Lanes

### C0 — Environment / export smoke

Purpose: prove environment, exact model/tokenizer load, one training step, eval, checkpoint, resume, merge/export and canonical Q4 path.

Rules:
- smallest relevant admitted cell sufficient to prove the path;
- no material run;
- record exact Colab runtime, GPU, CUDA, PyTorch, Transformers, Unsloth, TRL/PEFT/bitsandbytes where used, repository commit, model/tokenizer revision and manifest;
- run Q4 export smoke before trusting the recipe.

### C1 — Method tournament

Purpose: choose the most efficient stable adaptation mechanism before investing in model-specific pilots.

Equivalent candidate arms **MUST include every technically supported arm** from:

```text
16BIT_LORA
16BIT_LORA_RSLORA
4BIT_QLORA
4BIT_QLORA_RSLORA
```

For every arm not executed, the decision record MUST state the exact backbone/framework compatibility reason, authoritative evidence identity, and whether the omission is `UNSUPPORTED`, `INCOMPATIBLE`, or `SEPARATELY_GATED`. Convenience or notebook availability is not a valid omission reason.

No arm wins because it is easier in Unsloth. Revalidate current model-specific documentation immediately before execution; do not preserve stale blanket claims about a family indefinitely.

Full fine-tuning is non-default and requires separate evidence/authority because of cost and catastrophic-forgetting risk.

Selection consumes:
- DVCR/proxy gains appropriate to the stage;
- raw coding/FIM;
- Q4 regression;
- stability;
- memory/runtime requirements;
- wall time/cost;
- reproducibility/resume behavior.

### C2 — MSTR-001 bounded continued code/FIM pilot

Purpose: determine whether a code/software data mixture deepens the foundation enough to improve later agent behavior.

Required data families are governed by `MSTR-DATA-CONSTITUTION-v0` and may include:
- code;
- tests;
- diffs;
- build/CI/tooling;
- repository windows;
- software-evolution projections;
- ordinary FIM;
- instruction-aware FIM;
- function/dependency-aware FIM;
- cross-file/repository FIM;
- test-aware/diff-aware experimental FIM;
- bounded general/software-reasoning replay.

Use a checkpoint-relative difficulty/frontier sampler. The pilot must not simply maximize training tokens.

After each material checkpoint:

```text
source checkpoint
-> merged master
-> verify merged-master SHA-256
-> canonical Q4 export
-> verify canonical-Q4 SHA-256
-> direct code/FIM tests
-> selected executable repo tests
-> required Q4/universal-laptop regression
-> Q4PromotionRecord
-> PROMOTE | REJECT
```

Only `PROMOTED` checkpoints may become parents of a later material weight-changing stage.

### C3 — MSTR-002 execution-grounded SFT / preference

Purpose: teach the same software-building loop MSTR serves with.

Data includes:
- verified direction-to-done trajectories;
- software-evolution trajectories;
- student self-alignment positives;
- permitted independently verified teacher-rescue examples;
- repository inspection/localization;
- tool use/edit/apply;
- tester/reviewer mode examples;
- build/test/verifier use;
- failure/recovery;
- minimal/surgical-change preference pairs;
- invalid tool/edit/fake-completion negatives;
- feature/greenfield tasks;
- persistent FIM/direct-code replay.

Clean positive SFT admission requires the stage's provenance/rights/contamination/verifier-health threshold.

### C4 — MSTR-003 executable agent RL

Purpose: improve long-horizon verified completion only after environment/verifier/data foundations prove reliable.

Requirements:
- admitted runnable environments;
- verifier-health proof;
- reward-shortcut battery;
- checkpoint-relative difficulty/frontier curriculum;
- failure-inclusive trajectories;
- same or migration-proven model-visible loop semantics;
- multi-fidelity promotion before expensive campaigns;
- a successful identity-bound Q4 promotion record before a checkpoint is reused as a later material-stage parent.

Unsloth may be used for cheap GRPO/RL pilots where appropriate. `slime`, `verl`, and alternatives remain candidates for scaled long-horizon RL. No scaled framework is preselected.

## 5. Student Self-Alignment

MSTR treats execution-filtered self-alignment as a first-class data source.

```text
student proposes task/solution/tests
-> bind seed + generated-artifact provenance/rights
-> admitted sandbox executes
-> independent verifier + verifier-health
-> contamination checks
-> difficulty calibration
-> stage admission
```

The purpose is not self-confirmation. A student-generated example cannot validate itself. Missing or unresolved provenance/rights/contamination evidence fails closed.

## 6. Teacher Rescue

Teacher use is bounded and secondary.

A teacher may address useful hard-frontier cells only when:
- teacher/API terms are recorded;
- concrete teacher-output rights are compatible;
- exact output provenance is recorded;
- contamination/leakage status is clear;
- exact cost/network authority exists;
- outputs are independently executed/verified.

Teacher output is evidence candidate, not truth. Unresolved output rights or contamination fails closed.

Large code/agent models, including future/current Qwen3.8-class models, may be reference/teacher candidates while remaining unsuitable as the universal-laptop release backbone.

## 7. Difficulty / Frontier Policy

Every training task family is calibrated against an exact student checkpoint and harness/sampling identity.

Classes:

```text
TOO_EASY
LEARNABLE_FRONTIER
HARD_FRONTIER
CURRENTLY_UNPRODUCTIVE
INVALID
```

Prefer the learnable frontier while maintaining easy/core replay and hard expansion cells. Recalibrate after material checkpoints; difficulty labels are not permanent task metadata.

## 8. Multi-Fidelity Experiment Promotion

Training research uses the MSTR-000B ladder:

```text
L0 CONTRACT/SMOKE
-> L1 CODE/FIM/EDIT/TOOL
-> L2 EXECUTABLE SMALL-REPO
-> L3 DIRECTION-TO-DONE / FEATURE / PROGRAM
-> L4 Q4 UNIVERSAL-LAPTOP
```

Weak experiments are discarded before expensive evaluation. Promotion criteria are frozen before each campaign. Every material result uses the exact `MaterialResultIdentity` contract; missing required identity invalidates comparison/promotion.

## 9. Colab Reproducibility Contract

Every Colab run starts from a machine-readable run manifest containing at least:

```text
run_id
git_commit
spec/workstream/task_id
base_model_id + immutable revision
base_artifact_hash
tokenizer_id + revision
interaction + loop contract versions
dataset/Data-Constitution manifest ids + hashes
software-evolution/self-alignment/curriculum identities where used
verifier + verifier-health policy
training_method
precision
adapter configuration
sequence/context settings
optimizer + scheduler
batch/accumulation settings
seed
max steps/tokens/epochs
eval cadence
checkpoint cadence
stopping/promotion rules
expected cost ceiling
allowed network sources
```

Runtime capture:

```text
Colab runtime version
OS/Python
GPU + VRAM
CUDA/driver where exposed
PyTorch
Transformers
Unsloth + Unsloth Zoo where relevant
TRL
PEFT/bitsandbytes where relevant
lock snapshot
wall time
checkpoint identities
actual cost/compute if applicable
```

A notebook screenshot is not canonical evidence.

## 10. Dependency / Runtime Drift

Colab/runtime packages change. MSTR must:
- pin training-critical package versions;
- capture lock/environment snapshots;
- rerun C0 after material framework/runtime changes;
- treat dependency-resolution drift as a new environment identity;
- revalidate exact current backbone support immediately before a training gate.

No model-specific recommendation copied from old documentation remains permanently authoritative.

## 11. Interruption-Safe Checkpointing

Assume Colab interruption.

```text
manifest
-> verify/stage data
-> train on ephemeral disk
-> evaluate
-> atomic checkpoint
-> hash
-> sync selected durable checkpoint + manifest/metrics
-> verify resume identity before continuation
```

A resume mismatch starts a new lineage.

## 12. Data Movement

Git contains only metadata/code/config/manifests/hashes/reports.

Large datasets/checkpoints/model artifacts stay outside Git and never on the founder Mac under current policy.

Any new persistent large-artifact store requires explicit project authority.

## 13. Proposed Training Repository Structure

Created only by the later authorized workstream:

```text
training/
  README.md
  configs/
    continued_pretraining/
    fim/
    sft/
    preference/
    rl/
    methods/
  data/
    manifests/
    curriculum/
  unsloth/
    common.py
    train.py
    resume.py
    export.py
  colab/
    mstr-smoke.ipynb
    mstr-code-pilot.ipynb
    mstr-sft.ipynb
    mstr-rl-pilot.ipynb
    mstr-eval-export.ipynb
  manifests/
  scripts/
    verify_run.py
    sync_checkpoint.py
    export_gguf.py
    calibrate_difficulty.py
```

Notebooks call repository code/configs. Unique notebook-only training logic is prohibited.

## 14. Export / Q4 Promotion

Artifact classes:

```text
ADAPTER_CHECKPOINT
MERGED_MASTER_CHECKPOINT
OPTIMIZER_RESUME_STATE
TOKENIZER/PROCESSOR_ARTIFACTS
QUANTIZED_DEPLOYMENT_ARTIFACTS
```

Every material weight-changing stage must emit a `Q4PromotionRecord` containing at minimum:

```text
source_training_run_id
source_checkpoint_sha256
merged_master_sha256
export_tool_id + exact revision
export_recipe_hash
quantizer_tool_id + exact revision
quantization_recipe_hash
canonical_q4_artifact_sha256
artifact_integrity_status
q4_regression_manifest_id + result
universal_laptop_gate_result
promotion_status
```

Release-relevant promotion is fail closed:

```text
checkpoint
-> merged master
-> verify master hash
-> GGUF/reference conversion with pinned tool revision + recipe
-> canonical Q4
-> verify Q4 hash
-> direct-code/FIM regression
-> tool/edit/recovery regression
-> Direction-to-Done subset
-> universal-laptop gate when required
-> PROMOTE only if every required gate passes
```

`REJECTED`, missing, incomplete, or identity-ambiguous promotion records cannot be used as parent checkpoints for later material weight-changing stages. A BF16/FP16/master-only gain does not qualify for continuation.

Q8/Q6/Q5 may be diagnostic arms, not mandatory persistent artifacts.

## 15. Regression Gates

After every material stage recheck applicable:
- raw coding;
- FIM;
- multilingual/core-language mix;
- tokenizer/template integrity;
- repository localization/feature building;
- tester/reviewer behavior;
- tool/schema/edit reliability;
- failure/recovery;
- security;
- verifier health;
- Q4 behavior;
- DVCR/TTVC where agent-level claims are made;
- repository health over repeated tasks;
- 8GB/CPU deployment feasibility at release-relevant promotions.

An agent metric gain does not justify destroying direct coding/FIM or Q4 quality.

## 16. Compute Escalation

```text
free/available Colab
-> paid Colab only under exact authority
-> dedicated/rented GPU only under exact authority
-> multi-GPU/cluster only after bounded evidence proves value
```

No paid compute is authorized by this document.

## 17. Research Method Decisions

Every method/data change is an evidence-backed decision cell, including:
- backbone;
- tokenizer implications;
- LoRA/QLoRA/rsLoRA;
- precision;
- adapter rank/targets;
- context length;
- code/FIM mix;
- software-evolution mix;
- student/teacher mix;
- frontier thresholds;
- SFT/recovery/preference mix;
- RL algorithm/framework;
- checkpoint selected for continuation;
- export/quantization recipe.

Failed/interrupted/invalid experiments remain evidence.

## 18. Workstream Ownership

### MSTR-000A
Owns model-visible loop/harness/event/state/environment/verifier/trajectory foundation.

### MSTR-000B
Owns product-aligned rescan, task-gate enforcement, Data Constitution, software-evolution/self-alignment/difficulty/verifier-health/test-generation/feature curricula, multi-fidelity research policy, Q4 promotion and method preflight.

### MSTR-001
Owns actual Data Engine + bounded continued code/FIM training when authorized.

### MSTR-002
Owns actual execution-grounded SFT/preference/recovery training when authorized.

### MSTR-003
Owns actual executable-environment RL and scaled framework selection when authorized.

### MSTR-004+
Own inference/package/release; training infrastructure never becomes an end-user dependency.

## 19. Current Authority

```text
TRAINING_STRATEGY = PLANNING_ONLY
WEIGHT_CHANGING_TRAINING = NOT_AUTHORIZED
PAID_COLAB = NOT_AUTHORIZED
RENTED_GPU = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

Live `CURRENT_STATE.md` and exact task gates control execution.
