# Contracts — MSTR-000A

This directory freezes framework-neutral contract intent for the verified agent-loop foundation.

## Contract Families

- `loop-contract.schema.json` — bounded agent-loop authority and stop/recovery policy.
- `run-event.schema.json` — append-oriented typed event envelope.
- `trajectory-manifest.schema.json` — training/evaluation trajectory identity and admission.

Future implementation may add separate schemas for environment, verifier, harness profile, capability profile, research campaign, and direction task records. It must not weaken the invariants frozen here.

## Core Invariants

1. A model cannot self-author successful terminal verification.
2. Every model-visible fact is reconstructable from ordered events.
3. Event order is monotonic and decision records are deterministically serializable.
4. Harness/model comparisons require exact identity binding.
5. Failed/recovered runs remain representable.
6. Private user traces are not training-admitted by default.
7. Research campaigns freeze evaluation/verifier authority before experimental mutation.

## Versioning

Schema versions are explicit strings. A material change to model-visible semantics or terminal success rules requires a new schema/contract version and migration/regression evidence.
