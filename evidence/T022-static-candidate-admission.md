# T022 — Bounded Weight-Eligible Candidate Set Selection

**Task:** MSTR-000 / T022
**Branch:** task/000-t022-static-admission
**Decision record:** `artifacts/decisions/T022-static-candidate-admission.json` — canonical T007 immutable envelope (`mstr.evidence-envelope.v1`, record_type `T022-static-candidate-admission`), envelope SHA-256 `8d6cdc6c0e233354bdea0bfb45dc246712969b1a05b1c8706527dd3ff03bec34`, loadable via `load_finalized_evidence`.
**Scope:** select the bounded set of candidates that may proceed to weight-access planning (T027/T028) — WITHOUT final backbone admission, WITHOUT downloading weights, WITHOUT execution. Metadata only; all facts already canonical from T012–T021.

## Decision

All **eight** static_qualified records enter the bounded weight-eligible set:

| # | candidate | role | family | params | FIM | caveat |
|---|---|---|---|---|---|---|
| 1 | qwen3.5-2b | foundation | qwen3_5 (multimodal) | 2.27B | yes | — |
| 2 | qwen3.5-4b | foundation | qwen3_5 (multimodal) | 4.66B | yes | — |
| 3 | ministral-3-3b | foundation | mistral3 (multimodal) | ~4.25B | no | license re-verification required |
| 4 | qwen3-4b | control | qwen3 (text-only) | 4.02B | yes | — |
| 5 | granite-4.1-3b | foundation | granite (text-only) | 3.40B | yes | license re-verification required |
| 6 | smollm3-3b | foundation | smollm3 (text-only) | 3.08B | no | license re-verification required |
| 7 | qwen2.5-coder-1.5b | control | qwen2 coder | 1.54B | yes | — |
| 8 | yi-coder-1.5b | control | llama coder | 1.48B | no | — |

## Rationale

1. **Rights:** every selected record recomputes `pass_permissive` through the T006 fail-closed gate at its pinned revision (FR-015). The three caveated records carry explicit missing-LICENSE-text flags: they stay in the set CONDITIONALLY and drop automatically if T027 preflight re-verification fails.
2. **Envelope plausibility:** each candidate plausibly satisfies the Q4 ≤3GB artifact target after quantization (FR-003); final confirmation is measured, not assumed (T031+).
3. **Diversity (FR-019):** the set spans six architecture families (qwen3_5, mistral3, qwen3, granite, smollm3, qwen2/llama-coder), three text-only vs two multimodal bases, native-FIM vs non-FIM tokenizers — a materially different comparison per the spec.
4. **Controls:** two deliberately lightweight code-oriented controls satisfy and exceed FR-019's minimum.

## Exclusions (explicit)

- `afm-4.5b-base`: reference_only — post-trained artifact (SFT+RL documented in model card).
- `qwen2.5-coder-3b-reference`: reference_only — research license fails closed rights gates.
- All `comparison-*` records: post-trained comparison points never enter foundation admission by role.

## What this decision does NOT grant

```text
BACKBONE_ADMISSION = NOT_GRANTED
WEIGHT_ACCESS = NOT_GRANTED (requires T027 preflight + separate exact T028 authorization)
LOCAL_QUALIFIED = NOT_GRANTED (T034 decides after measured local evidence)
FINALIST_STATUS = NOT_GRANTED (T050 decides)
```

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = NONE (decision uses already-canonical records only)
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```

## Result candidate

```text
T022_RESULT = PASS_CANDIDATE
NEXT_TASKS_AFTER_CANONICAL_MERGE = T023-T026 [P] (Phase-4 harness infrastructure), then T027 preflight
```
