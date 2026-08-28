# B006 Candidate Reconciliation Evidence

**Workstream:** MSTR-000B
**Task:** B006
**State:** COMPLETE_CANONICAL
**Implementation PR:** `#57`
**Final implementation head:** `98b549e9d8b2550725861e133ee8f909690dc9c8`
**Canonical implementation merge:** `c96e2fb228a7f3fb0399484a9e6bb1e1d1eb086c`
**Canonical main at entry:** `ebd31e7657cb42479b28a4cb1cc8a5ce2ae56b6a`
**Branch:** `research/000b-b006-candidate-reconciliation`

## Entry gate

B006 material work began only after exact-main production eligibility and canonical drift were re-proved on canonical main.

```text
ENTRY_GATE_TASK = B006
ENTRY_GATE_CANONICAL_MAIN = ebd31e7657cb42479b28a4cb1cc8a5ce2ae56b6a
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_REASONS = []
ENTRY_GATE_RUN = 33145225542
ENTRY_GATE_JOB = 98764633198
ENTRY_GATE_DRIFT = clean
```

## Scope

This implementation reconciles the nine `newly_relevant_for_b006` rows from the canonical B005 discovery manifest and the four existing candidate records explicitly flagged for material revalidation. It does not select a final backbone and creates no model-access, inference, training, compute, or production authority.

Public metadata snapshots were executed separately from the implementation branch and asserted exact pinned upstream revisions. They fetched metadata JSON only and performed no model-file resolve/download.

```text
NEW_CANDIDATE_METADATA_RUN = 33145341065
NEW_CANDIDATE_METADATA_RESULT = SUCCESS
REVALIDATION_METADATA_RUN = 33145441559
REVALIDATION_METADATA_JOB = 98765300807
REVALIDATION_METADATA_RESULT = SUCCESS
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
GATED_TERMS_ACCEPTANCE = NONE
MODEL_EXECUTION = NONE
```

## Classification semantics

`candidate_role` describes the technical comparison role. `status` and the fail-closed rights record determine whether a candidate is admitted to the primary path. A technically useful control may therefore remain `reference_only` when required component rights are unresolved. `pass_conditional`, unknown substantive rights, account/clickthrough gates, downstream-license obligations, or field/scale restrictions do not satisfy the repository primary-rights gate.

## Newly relevant B005 rows

| Upstream | B006 classification | Rights result | Rationale |
| --- | --- | --- | --- |
| `JetBrains/Mellum-4b-base` | primary-eligible foundation candidate / `static_qualified` | `pass_permissive` | Apache-2.0, no public access gate observed, code-specialized base checkpoint. Runtime and artifact fit remain later tasks. |
| `bigcode/starcoder2-3b` | `reference_only` | fail closed | BigCode OpenRAIL-M carries use restrictions and downstream enforceable-provision obligations incompatible with the unrestricted primary gate. |
| `stabilityai/stable-code-3b` | `reference_only` | fail closed | Stability AI Community License has scale/revenue and model-improvement restrictions plus downstream obligations. |
| `google/codegemma-2b` | `reference_only` | fail closed | Public model page requires account/login and clickthrough acceptance of Gemma terms before weight access. No terms were accepted. |
| `tiiuae/Falcon-H1-3B-Base` | needs founder/legal clarification / `discovered` | fail closed | The currently linked license terms identify a different Falcon work; exact license applicability to Falcon-H1-3B-Base is not established, so substantive rights are recorded unknown. |
| `microsoft/bitnet-b1.58-2B-4T-bf16` | technical `control`, primary-ineligible / `reference_only` | fail closed | Microsoft declares MIT for model/code, but the model card identifies a LLaMA 3 tokenizer. Independent tokenizer redistribution provenance was not established, so FR-016 fails closed. |
| `LiquidAI/LFM2.5-2.6B-Base` | `reference_only` | fail closed | LFM Open License v1.0 includes revenue/scale-based commercial restrictions and downstream licensing obligations. |
| `LiquidAI/LFM2.5-1.2B-Base` | `reference_only` | fail closed | Same LFM Open License restrictions; useful low-parameter/on-device reference, but not primary-rights eligible. |
| `Qwen/Qwen3.5-0.8B-Base` | lower-bound `control` / `static_qualified` | `pass_permissive` | Apache-2.0 and public ungated metadata. Multimodal component cost and clean-foundation provenance caveats remain explicit; no runtime admission is implied. |

## Required revalidations from B005

### Qwen3.5 2B and 4B

The exact pinned revisions remain Apache-2.0 and public/ungated. B006 preserves both records as `foundation` / `static_qualified`. The current model-card wording that includes both pre-training and post-training is recorded as a provenance caveat; B006 does not silently reinterpret repository naming as proof of a pristine pretraining-only checkpoint.

Pinned metadata counts:

```text
Qwen/Qwen3.5-2B-Base = 2,274,069,824 safetensors parameters
Qwen/Qwen3.5-4B-Base = 4,659,865,088 safetensors parameters
```

### Yi-Coder 1.5B

The exact pinned public metadata reports `1,476,495,360` safetensors parameters. The existing approximate `1,480,000,000` value is corrected to the exact metadata count. Yi-Coder remains a code-specialized `control` / `static_qualified` under Apache-2.0. Its base/post-training lineage caveat remains explicit rather than being inferred away.

### Ministral 3 3B Base

The exact pinned metadata reports `4,251,743,232` serialized parameters. The current model-card family description separately reports approximately 3.4B language-model parameters plus 0.4B vision-encoder parameters. B006 reconciles these as distinct accounting surfaces instead of treating them as revision drift. The candidate remains Apache-2.0 `foundation` / `static_qualified`; multimodal runtime and artifact economics remain later measured tasks.

## Rights-gate outcome

Primary-rights eligible after B006 reconciliation:

- `JetBrains/Mellum-4b-base`
- `Qwen/Qwen3.5-0.8B-Base`
- existing `Qwen/Qwen3.5-2B-Base`
- existing `Qwen/Qwen3.5-4B-Base`
- existing `01-ai/Yi-Coder-1.5B` as a control
- existing `mistralai/Ministral-3-3B-Base-2512`

Not primary-rights eligible from the newly reviewed set:

- `bigcode/starcoder2-3b`
- `stabilityai/stable-code-3b`
- `google/codegemma-2b`
- `LiquidAI/LFM2.5-2.6B-Base`
- `LiquidAI/LFM2.5-1.2B-Base`
- `microsoft/bitnet-b1.58-2B-4T-bf16` until tokenizer-component rights are established
- `tiiuae/Falcon-H1-3B-Base` until exact license applicability is clarified

These classifications are static metadata/rights results only. They do not prove runtime support, quantized artifact fit, tokenizer economics, benchmark quality, or final backbone selection.

## Authority boundary

```text
PUBLIC_METADATA_ONLY = YES
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
NEW_AUTHORITY_CREATED = NO
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

## Closeout rule

This evidence is implementation evidence only. B006 remains not `COMPLETE_CANONICAL` until the exact implementation head is schema/rights/test qualified, independently reviewed with no unresolved material finding, merged to `main` with expected-head protection, and post-merge verification succeeds. A separate canonical closeout must then align the task catalog/checkbox/evidence identity before any successor task materially mutates the repository.
## Canonical closeout evidence

B006 is canonicalized only after the implementation was independently qualified, reviewed, merged with exact-head protection, and re-verified on the resulting canonical main.

```text
ENTRY_RUN = 33145225542
ENTRY_JOB = 98764633198
IMPLEMENTATION_PR = #57
FINAL_IMPLEMENTATION_HEAD = 98b549e9d8b2550725861e133ee8f909690dc9c8
CANONICAL_IMPLEMENTATION_MERGE = c96e2fb228a7f3fb0399484a9e6bb1e1d1eb086c
EXACT_HEAD_QUALIFICATION_RUN = 33146528197
EXACT_HEAD_QUALIFICATION_JOB = 98768693522
INDEPENDENT_REVIEW_RUN = 33146704635
INDEPENDENT_REVIEW_JOB = 98769231950
POST_IMPLEMENTATION_VERIFY_RUN = 33146803658
POST_IMPLEMENTATION_VERIFY_JOB = 98769528432
POST_IMPLEMENTATION_MAIN = c96e2fb228a7f3fb0399484a9e6bb1e1d1eb086c
POST_IMPLEMENTATION_B006_ELIGIBLE = true
POST_IMPLEMENTATION_B007_ELIGIBLE = false
POST_IMPLEMENTATION_B007_REASON = prerequisite.unsatisfied:B006
POST_IMPLEMENTATION_DRIFT = clean
TARGETED_GOVERNANCE_TESTS = 59 passed
FULL_PYTEST = 502 passed
RUFF = PASS
MYPY = PASS / 26 source files
VALIDATE = PASS / 10 valid / 10 invalid rejected
```

The B007 block observed after the implementation merge is the expected pre-closeout state: B006 remained `PENDING` until this separate canonical state transition. This closeout changes no candidate classification, rights fact, model artifact, runtime behavior, or external authority.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
NEW_AUTHORITY_CREATED = NO
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
B007_MATERIAL_EXECUTION = NOT_STARTED
```
