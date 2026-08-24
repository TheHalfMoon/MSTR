# MSTR Training Execution Strategy

**Status:** Canonical program-level planning input; no execution authority.  
**Checkpoint:** 2026-08-24.  
**Applies primarily to:** MSTR-001, MSTR-002, and bounded experiments feeding MSTR-003.  
**Product dependency:** NONE. The end-user MSTR product must not require Colab or Unsloth.

## 1. Purpose

Define an accessible, reproducible training path that can be executed by a small team without compromising MSTR's universal-laptop product goal.

The default accessible stack is:

```text
Google Colab
    = hosted GPU execution environment

Unsloth
    = preferred efficient fine-tuning / post-training framework

MSTR qualification harness
    = canonical evidence, manifests, regression gates, and decisions

llama.cpp / GGUF-class local runtime
    = primary local deployment qualification path
```

Colab and Unsloth are implementation candidates, not architectural authorities. A later Spec Kit may replace either if exact evidence shows a better path.

## 2. Why Colab + Unsloth

As of 2026-08-24, Unsloth documents fine-tuning support for compact Qwen3.5 models including 0.8B, 2B, and 4B and provides Google Colab notebooks. It supports LoRA/SFT, RL-oriented workflows, and GGUF export.

Primary sources to revalidate before execution:

- https://unsloth.ai/docs/models/qwen3.5/fine-tune
- https://unsloth.ai/docs/get-started/fine-tuning-llms-guide
- https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf
- https://research.google.com/colaboratory/faq.html
- https://research.google.com/colaboratory/runtime-version-faq.html

Google Colab explicitly treats resource availability, GPU type, usage limits, and runtime duration as dynamic. Therefore MSTR must be designed for interruption and resume rather than assuming an uninterrupted training machine.

## 3. Training lanes

### C0 — Smoke / notebook qualification

Purpose: prove environment, model load, tokenizer/chat/FIM assumptions, one training step, one eval step, checkpoint save, reload, and export path.

Rules:
- smallest admitted model/artifact sufficient to test the path;
- no long run;
- fail before spending meaningful compute if package/model compatibility is broken;
- record exact Colab runtime version, GPU, CUDA, PyTorch, Transformers, Unsloth, TRL, tokenizer, and repository commit.

### C1 — Micro adaptation

Purpose: compare methods cheaply before choosing a pilot recipe.

Candidate arms:
- bf16/fp16 LoRA where supported;
- QLoRA only where the selected model family and evidence justify it;
- limited full fine-tuning only if a later Spec Kit explicitly justifies the compute and expected value.

For Qwen3.5 specifically, current Unsloth guidance says 4-bit QLoRA is not recommended because quantization differences are higher than normal. Therefore, if a Qwen3.5 compact model wins MSTR qualification, **bf16 LoRA is the default first pilot** and QLoRA is an explicit experimental arm, not the default.

### C2 — MSTR-001 bounded code/FIM pilot

Purpose: determine whether continued code/repository/FIM training improves the selected foundation without unacceptable forgetting or deployment regression.

Must include:
- immutable data/provenance manifest;
- exact token/update budget;
- ordinary + structured/function/dependency-aware FIM as specified by MSTR-001;
- general-reasoning replay;
- fixed eval checkpoints;
- bounded stopping criteria;
- quantized regression after the pilot.

### C3 — MSTR-002 SFT

Purpose: teach coding, repository, tool, edit, planning, recovery, and security behavior under the frozen Interaction Contract.

Unsloth is the preferred first implementation for compact-model SFT/LoRA if still supported and reproducible. The Spec Kit must retain a fallback path using standard Transformers/TRL-compatible training rather than binding MSTR data/contracts to Unsloth internals.

### C4 — MSTR-003 RL experiments

Unsloth may be used for cheap GRPO/RL notebook experiments when appropriate, but it is **not preselected as the scaled agentic RL framework**. `slime`, `verl`, and alternatives remain tournament candidates for long-horizon executable-environment RL.

## 4. Backbone-specific method rule

Training method follows the selected backbone; the framework never selects the backbone.

```text
backbone qualification
-> runtime/Q4 qualification
-> Interaction Contract freeze
-> micro method tournament
-> training method decision
```

No candidate receives an advantage simply because it is easier to train in one framework.

## 5. Colab reproducibility contract

Every Colab run must start from a machine-readable run manifest containing at least:

```text
run_id
git_commit
spec/workstream/task_id
base_model_id
base_model_revision
base_artifact_hash
tokenizer_id + revision
interaction_contract_version
dataset_manifest_id + hashes
training_method
precision
LoRA/adapter configuration
sequence/context settings
optimizer + scheduler
batch/accumulation settings
seed
max steps/tokens/epochs
eval cadence
checkpoint cadence
stopping rules
expected cost ceiling
allowed network sources
```

At runtime also capture:

```text
Colab runtime version
OS/Python
GPU model + VRAM
CUDA/driver where exposed
PyTorch
Transformers
Unsloth
Unsloth Zoo
TRL
bitsandbytes/PEFT when used
pip/uv lock snapshot
actual wall time
actual checkpoints
actual cost/compute units if applicable
```

A notebook screenshot is not canonical evidence.

## 6. Runtime-version and dependency policy

Colab runtime images change. MSTR must:
- record the selected Colab runtime version;
- pin training-critical package versions;
- save a lock/snapshot beside each run manifest;
- prefer an explicit compatible Transformers version required by the selected model;
- treat dependency-resolution drift as a new run environment, not as the same experiment;
- rerun C0 after a material runtime/framework update.

For current Qwen3.5 + Unsloth planning, Transformers v5 compatibility must be revalidated immediately before use.

## 7. Interruption-safe checkpointing

Colab must be assumed interruptible.

Training work happens on fast ephemeral runtime storage. Durable storage receives bounded artifacts only.

Recommended lifecycle:

```text
prepare manifest
-> resolve/pin environment
-> stage verified data locally
-> train on ephemeral local disk
-> evaluate
-> write atomic checkpoint
-> hash checkpoint
-> sync selected checkpoint + manifest + metrics to durable storage
-> continue
```

Rules:
- never rely on `/content` surviving a disconnect;
- avoid syncing thousands of tiny training files to Drive;
- checkpoint at the same logical eval/save boundaries used by the training recipe;
- a resumed run verifies base revision, tokenizer, dataset manifest, config, previous checkpoint hash, and code commit before continuing;
- a mismatch starts a new run lineage instead of silently resuming.

## 8. Proposed future repository structure

Created only by the later workstream that authorizes training:

```text
training/
  README.md
  configs/
    midtrain/
    sft/
    preference/
    rl/
  unsloth/
    common.py
    train.py
    resume.py
    export.py
  colab/
    mstr-smoke.ipynb
    mstr-midtrain.ipynb
    mstr-sft.ipynb
    mstr-eval-export.ipynb
  manifests/
  scripts/
    verify_run.py
    sync_checkpoint.py
    export_gguf.py
```

Notebook cells should call repository code/configs; training logic must not exist only inside notebooks.

## 9. Data movement

Canonical metadata lives in Git. Large datasets/checkpoints remain outside Git.

```text
Git:
  schemas
  configs
  manifests
  provenance
  hashes
  reports

External durable storage:
  admitted datasets
  checkpoints
  merged weights
  GGUFs
  large logs
```

Before a Colab run, data is copied/staged to local ephemeral disk and verified against the canonical manifest. No private repository data, secrets, or credentials become training data by default.

## 10. Checkpoint and artifact classes

Every material training run should distinguish:

```text
ADAPTER_CHECKPOINT
MERGED_MASTER_CHECKPOINT
OPTIMIZER_RESUME_STATE
TOKENIZER/PROCESSOR_ARTIFACTS
QUANTIZED_DEPLOYMENT_ARTIFACTS
```

The master post-training artifact is not automatically the release artifact.

Expected export qualification:

```text
adapter
-> merged bf16/fp16 master
-> GGUF/reference quantization
-> Q8
-> Q6
-> Q5
-> Q4 candidate(s)
-> MSTR laptop regression suite
```

For the universal-laptop product, the Q4-class artifact is release-critical even if the master checkpoint is stronger.

## 11. Export and chat-template integrity

When exporting with Unsloth or another framework:
- preserve tokenizer/processor files required by the selected backbone;
- preserve the exact trained chat/FIM/tool template;
- hash every exported artifact;
- test merged-master behavior before quantization;
- test each quantized artifact independently;
- do not attribute a broken template/EOS/export pipeline to model intelligence.

GGUF export is a planned path because Unsloth supports direct GGUF export and MSTR targets local llama.cpp-class deployment.

## 12. Regression gates after every training stage

No stage advances from a single improvement number.

At minimum recheck:
- raw coding;
- FIM;
- multilingual coding;
- repository localization/repair;
- tool/schema reliability;
- Interaction Contract compliance;
- security behavior;
- quantized behavior;
- 8GB/CPU deployment feasibility;
- TTVC where the stage makes agent-level claims.

Agent training that improves SWE tasks while materially damaging FIM or Q4 reliability is not automatically accepted.

## 13. Compute escalation policy

```text
free/available Colab
-> paid Colab only under exact authority
-> dedicated/rented GPU only under exact authority
-> multi-GPU/cluster only after a bounded pilot proves value
```

The project must not design a recipe that requires frontier-scale compute merely because a framework can support it.

No paid Colab, rented GPU, or other compute is authorized by this document.

## 14. Training decision records

Every method change requires a decision record backed by equivalent evidence, including:
- LoRA vs QLoRA;
- adapter rank/targets;
- precision;
- sequence length;
- code/FIM mix;
- reasoning replay;
- SFT mix;
- checkpoint selected for continuation;
- export/quantization recipe.

Failed and interrupted runs remain evidence.

## 15. Relationship to MSTR workstreams

### MSTR-000
Qualifies hardware, backbone, interaction/runtime constraints. Only T053 can authorize bounded equivalent micro-adaptation.

### MSTR-001
Owns Data Engine + bounded code/FIM mid-training. It must turn this strategy into a dedicated Spec Kit with exact data, compute, cost, checkpoint, and regression contracts.

### MSTR-002
Owns coding/repository/tool/planning SFT and persistent FIM replay.

### MSTR-003
Owns executable-environment RL and framework selection. Colab/Unsloth may support pilots but do not preempt the RL framework tournament.

### MSTR-004+
Own local inference, packaging, release qualification, and product delivery; they consume exported artifacts but do not inherit the training stack as a user dependency.

## 16. Current pause

This strategy is finalized as planning only.

```text
EXECUTION_STATE = PAUSED
NEXT_MSTR_TASK_ON_RESUME = T010
MODEL_ACCESS = NONE
TRAINING = NONE
COLAB_RUN = NONE
UNSLOTH_INSTALL = NONE
```

Resume only after explicit founder direction following completion of WePLD and live GitHub reconciliation.
