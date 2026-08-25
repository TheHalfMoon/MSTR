# T019 — Reference-Only Record: Qwen2.5-Coder-3B

**Task:** MSTR-000 / T019
**Scope:** record exact current terms; no weight access, no execution, no paid API.

## Live verification (pinned revision 09d9bc5d376b0cfa0100a0694ea7de7232525803, fetched 2026-08-25)

The pinned `LICENSE` file is verbatim the **Qwen RESEARCH LICENSE AGREEMENT** (Release Date: September 19, 2024). HF model tags carry `license:other`.

## Fail-closed determination

```text
commercial_use = NO (research/non-commercial only)
derivative_redistribution = NO (not freely granted)
end_user_separate_license_required = TRUE (commercial use needs separate Qwen commercial license)
field_or_scale_restrictions = research-only restriction recorded
```

Current exact terms have NOT changed since the plan was finalized: the license remains research-restricted. Per FR-015/FR-017 this candidate is ineligible for primary-backbone admission regardless of capability.

## Record

`artifacts/candidates/qwen2.5-coder-3b-reference.json`: schema-valid (CLI validate exit 0), status `reference_only`, rights decision `fail`. The T006 recomputed gate rejects it as expected (`python -m mstr_qualify rights` exit 1 with reason codes: declared_fail, commercial_use_denied, derivative_redistribution_denied, end_user_separate_license_required, field_or_scale_restriction_present) — this rejection is itself a live demonstration that the fail-closed gate works on real upstream terms.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = metadata-only HTTPS GETs to huggingface.co at pinned revision
TRAINING = NONE
```
