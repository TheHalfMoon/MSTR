# B012 Qwen Case-Checkpoint Recovery Activation

Status: repository-only activation candidate

Canonical activation base: `4deca995306c197e5cefaf8202e64fe5469f873c`
Repair package merge commit: `4deca995306c197e5cefaf8202e64fe5469f873c`
Repair package postmerge run: `34261221062`
Repair package postmerge evidence head: `f5dac568a809fe9fed707c3c2d8a298c859d16bb`

## Activated surface

The separately reviewed workflow specification `configs/workflows/b012-qwen-raw-code-case-checkpoint-recovery.yml` is materialized byte-for-byte at `.github/workflows/b012-qwen-raw-code-recovery.yml`. The exact owner-scoped issue command is:

```text
B012_RECOVER_RAW_CODE_CASE_CHECKPOINT qwen3.5-0.8b-control 34155931982
```

No command is issued by this activation change. Activation is distinct from dispatch.

## Authority boundary

Existing authority remains `B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION`. This activation creates no retry authority and no external-dispatch authority, performs no model access or model execution, changes no candidate/revision/file identity, performs no training or weight-changing training, spends USD 0.00, and makes no model-quality or candidate-admission decision.

## Durability boundary

The active topology preserves a maximum of one uncheckpointed raw-code case, writes each stage checkpoint before persisting completed-stage state, treats Actions artifacts as transient transport, and requires required checkpoint evidence to be hash-verified and canonicalized to Git before dispatch closeout or candidate admission. Missing, expired, inconsistent, or non-canonicalizable required evidence fails closed.
