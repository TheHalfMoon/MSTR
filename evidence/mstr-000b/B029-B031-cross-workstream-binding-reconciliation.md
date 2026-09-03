# B029–B031 Cross-Workstream Binding Reconciliation

**Workstream:** MSTR-000B
**State:** RECONCILED_PENDING_CANONICAL_MERGE
**Canonical base:** `b20349c23ada1130f98e28c0e1e3db56ed692d13`

## Purpose

Replace three prose-only fail-closed bindings with exact repository-owned MSTR-000A prerequisite identities. This is task-gate governance repair only. It does not execute B029, B030, A019, A020, B031, or any external effect.

## B029 binding

B029 requires the already-canonical MSTR-000A loop/context contract surfaces that are both semantically sufficient and directly machine-bindable:

- `A005` — `MSTR-BUILD-LOOP-v0`, repair/timeout/tool budgets, recovery semantics, and the canonical AgentState dependency;
- `A006` — protected verifier/finalizer authority used to justify bounded repair decisions;
- `A008` — explicit selective context and bounded recovery cadence for the MSTR-native harness;
- `A010` — evidence-derived reliable context budget, verifier cadence, and repair-depth capability profile.

B020 remains the MSTR-000B checkpoint-relative difficulty prerequisite. No synthetic binding is added for A001-A004: their required semantics are already consumed by these canonical downstream surfaces, and A001-A003 do not expose repository-owned state-evidence files in the MSTR-000A evidence namespace.

## B030 binding

The canonical dependency text requires `A019-ready harness surfaces`. Those are the three already-canonical harness variants that A019 later compares:

- `A007` — H0 neutral-minimal harness;
- `A008` — H1 MSTR-native harness;
- `A009` — H2 WePLD-native adapter.

B024/B025 remain the MSTR-000B test-generation and feature/greenfield curriculum prerequisites. B030 itself freezes Repository Health Delta and raw/H0/H1/H2 attribution; this reconciliation does not pre-author or pre-implement those metrics.

## B031 binding

B031 already names A019 and A020 as prerequisites. This reconciliation binds them to the MSTR-000A checklist and their exact required evidence paths:

- `A019` -> `evidence/mstr-000a/A019-harness-tournament.md`;
- `A020` -> `evidence/mstr-000a/A020-autoresearch.md`.

Both tasks remain incomplete and their evidence files do not yet exist. Therefore B031 remains ineligible after this repair, but for real unsatisfied prerequisites rather than `prerequisite.missing_task_binding`. No A019/A020 completion is inferred.

## Preserved hard stops

```text
B011_AUTHORITY_CHANGE = NONE
B013_CANDIDATE_POOL_BINDING_CHANGE = NONE
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
```

B011 remains separately blocked on the exact founder authority required by canonical B010. B013 remains separately blocked on candidate qualification/convergence. This repair creates no authority and cannot satisfy either gate.
