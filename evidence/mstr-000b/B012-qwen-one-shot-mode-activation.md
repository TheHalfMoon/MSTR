# B012 Qwen One-Shot Raw-Code Recovery Activation

Status: repository-only activation candidate

Canonical activation base: `04096a180e47ed8f81ee81c1bf3d9e471be607fc`
Repair package merge commit: `04096a180e47ed8f81ee81c1bf3d9e471be607fc`
Repair package postmerge run: `34282489164`
Repair package postmerge evidence head: `3618b69ab145f5ed4d18502ca5064812aa6081cd`

## Activated surface

The separately reviewed workflow specification `configs/workflows/b012-qwen-raw-code-one-shot-recovery.yml` is materialized byte-for-byte at `.github/workflows/b012-qwen-raw-code-recovery.yml`. The exact owner-scoped issue command is:

```text
B012_RECOVER_RAW_CODE_ONE_SHOT qwen3.5-0.8b-control 34155931982
```

No command is issued by this activation change. Activation is distinct from dispatch.

## Execution-mode boundary

The activated variant preserves the canonical per-case durability topology and the frozen raw-code proxy inputs while invoking the isolated raw-completion helper with explicit `--no-conversation`. This is execution-mode ambiguity hardening only; it does not claim that conversation mode caused either hosted-runner shutdown.

## Authority boundary

Existing authority remains `B012_FOUNDER_AUTHORITY_FOR_EQUIVALENT_QUALIFICATION`. This activation creates no retry, redispatch, cross-run-resume, or external-dispatch authority, performs no model access or model execution, changes no candidate/revision/file identity, performs no training or weight-changing training, spends USD 0.00, retains no model binaries in Git or on the Founder machine, and makes no model-quality or candidate-admission decision.

## Dispatch boundary

The executor binding is restored to `SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL` only for a later fresh exact-main eligibility and authority gate after guarded merge and exact-main postmerge verification. This repository change does not issue the owner command.
