# B012 Qwen Q4 provenance repair after recovery run 34163308005

## Observed failure

Recovery workflow run `34163308005` on canonical main `f78359f87ab5f5259e5569bea178261dbd9cc8e7` failed closed before raw-code execution with `B012 Qwen recovery regenerated Q4 SHA-256 mismatch`. The failure JSON was durably uploaded as artifact `10033484666` with artifact digest `sha256:ab8ad711b7c4794247f892bdf36d74fbc4213f130db298f2c504abbace6f6bae`. Cleanup succeeded.

## Root cause

The recovery package had been bound to Q4_K_M SHA-256 `47f87d507130b70d7b54a159e7bf982e4fbe7dc75eae74e3cd9c9c9284805626`. Reinspection of the immutable original run artifacts showed that both Stage 03 artifact `10031142398` (`sha256:925f5447fb6f93bbfedcdad1eab3b2cc9e95b3748f041e313b5fb96052a4aeb1`) and Stage 05 artifact `10031329744` record the Q4_K_M artifact actually used by prefill/decode as `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa` at `541903296` bytes. The repository incident record had transcribed the wrong hash.

Therefore run `34163308005` is a provenance-binding failure, not a model-quality failure and not a raw-code result. The observed regenerated Q4 hash was not included in the v1 failure schema and cannot be reconstructed after cleanup; the repaired runner records it on any future mismatch.

## Boundary

This repair performs no model access, does not authorize a retry, does not create external-dispatch authority, does not expand candidate/revision/file scope, and does not change prior prefill/decode observations. Any future recovery execution remains separately gated by canonical repository governance.

```text
MODEL_ACCESS_DURING_REPAIR = NONE
MODEL_EXECUTION_DURING_REPAIR = NONE
TRAINING = false
PAID_COST_USD = 0.0
```
