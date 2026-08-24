# T006 — Primary Backbone / Component Rights Gate Evidence

**Task:** MSTR-000 / T006  
**Canonical base:** `47b6f07449f92136336044b29f73c0a4e8a8a218`  
**Branch:** `task/000-t006-rights-gate`  
**Scope:** generic fail-closed rights evaluation only. No candidate is qualified by this task, no model weights are accessed, and no legal conclusion is inferred without later source-specific evidence.

## Gate semantics

Primary MSTR admission is recomputed from rights facts rather than trusting a declared `decision` field.

A required backbone/tokenizer/vision component can pass only when:

- personal use = yes;
- commercial use = yes;
- modification = yes;
- fine-tuning = yes;
- quantization = yes;
- derivative redistribution = yes;
- intended primary distribution does not require a provider account, gated click-through, or separate end-user license;
- no field/scale restriction is recorded;
- license name, terms-source evidence, and rationale are present;
- declared decision is `pass_permissive`.

`unknown`, missing, invalid, explicit denial, `pass_conditional`, `reference_only`, or any required component failure makes the computed primary result fail. Later candidate tasks must provide exact source evidence; this evaluator does not fetch or interpret external legal text by itself.

## Local validation

```text
Python = 3.13.5
T006 focused tests = 17 passed
full prepared harness suite = 58 passed
python -m compileall src = PASS
```

Tests cover all six required-right unknown states, explicit denial, all three user-facing gates, field/scale restrictions, conditional declared decisions, missing terms evidence, multi-component aggregation, deterministic component ordering, and empty component rejection.

Ruff/mypy remain unavailable locally and are not claimed PASS; T011 remains the foundational quality closeout.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
CANDIDATE_ADMISSION = NONE_BY_T006_ALONE
```

## Result candidate

```text
T006_RESULT = PASS_CANDIDATE
NEXT_TASK_AFTER_CANONICAL_MERGE = T007
```
