# MSTR Q4 Promotion Contract v0

## Scope

This contract freezes the release-relevant Q4 checkpoint-promotion rule and the training-method tournament preflight required by MSTR-000B B028. It is a contract/preflight artifact only. It does not execute a model, acquire model weights, quantize a model, train a model, spend paid compute, or authorize any later external effect.

## Product Rule

Q4 behavior is product behavior. After every material weight-changing stage, the checkpoint MUST be exported and evaluated through the canonical release-relevant Q4 path before it may become the parent of another material weight-changing stage.

```text
SOURCE CHECKPOINT
-> VERIFY SOURCE CHECKPOINT SHA-256
-> MERGE / EXPORT MASTER
-> VERIFY MERGED-MASTER SHA-256
-> PIN EXPORT TOOL + REVISION + RECIPE HASH
-> BUILD CANONICAL Q4
-> VERIFY CANONICAL-Q4 SHA-256
-> PIN QUANTIZER + REVISION + RECIPE HASH
-> RUN REQUIRED Q4 REGRESSION
-> RUN APPLICABLE UNIVERSAL-LAPTOP HARD GATE
-> Q4PromotionRecord = PROMOTED | REJECTED
```

A BF16/FP16/master-only improvement is never sufficient promotion evidence.

## Fail-Closed Promotion

`mstr.q4-promotion.v0` is `PROMOTED` only when all required identity and integrity fields are present, artifact integrity is `PASS`, Q4 regression is `PASS`, and the universal-laptop gate is either `PASS` or explicitly `NOT_REQUIRED` with an auditable reason and evidence identity. A promoted record has no rejection reasons.

Any failed or ambiguous mandatory gate produces `REJECTED` with at least one exact rejection reason. Missing hashes, missing tool revisions, missing recipe hashes, failed integrity, failed Q4 regression, or an applicable failed laptop gate cannot be overridden by a master-checkpoint score.

Consumers MUST determine parent eligibility by requiring `promotion_status == PROMOTED`. This contract does not create training authority; it only constrains a later separately authorized training sequence.

## Equivalent Method Tournament Preflight

Every concrete finalist tournament MUST include every technically supported arm from this exact set:

1. `LORA_16BIT`
2. `LORA_16BIT_RSLORA`
3. `QLORA_4BIT`
4. `QLORA_4BIT_RSLORA`

Equivalent cells bind the same immutable base revision, admitted dataset manifest, token/update budget, seed policy, context/environment identity, evaluation identity/checkpoints, export recipe, and canonical-Q4 regression path.

A method is not selected by framework convenience. Method selection later consumes DVCR, TTVC, direct coding/FIM, Q4 regression, stability, cost, and reproducibility evidence.

## Candidate-Specific Support Is Not Inferred

Generic framework documentation is not sufficient proof that a concrete MSTR finalist supports one arm. Before execution, every finalist/arm cell MUST be revalidated against the exact backbone revision and exact framework/tool revisions. A supported cell records exact support evidence. An unsupported cell records an exact incompatibility reason and evidence identity. If support is unresolved, the cell remains `REVALIDATION_REQUIRED` and cannot execute.

B009 remains source-level compatibility evidence only; it explicitly does not convert generic trainer/converter presence into an executed candidate-specific pass.

## Guidance Snapshot — 2026-08-29

The B028 preflight revalidated current public guidance immediately before implementation:

- PEFT `main` revision `9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe`; current LoRA documentation exposes `use_rslora` and documents QLoRA-style `target_modules=all-linear`.
- Transformers `main` revision `42ca97014c85d71a88ad60d55f08cb9fb4d26e2c`; current bitsandbytes documentation describes QLoRA as 4-bit quantization with trainable LoRA weights.
- Unsloth `main` revision `e1653bcd1da874466da48ee5360ff60fc10d7973`; current public guidance advertises 4-bit and 16-bit LoRA support.

These observations justify preserving all four tournament arms in the preflight. They do not prove any specific MSTR candidate supports a given arm.

## Authority Boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
QUANTIZATION_EXECUTION = NONE
TRAINING_EXECUTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
PAID_COMPUTE = NONE
PAID_MODEL_API = NONE
LARGE_DATASET_INGESTION = NONE
PRODUCTION_RELEASE = NONE
B028_AUTHORITY = CONTRACT_AND_PREFLIGHT_ONLY
```
