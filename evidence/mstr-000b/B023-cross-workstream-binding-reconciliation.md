# B023 Cross-Workstream Prerequisite Binding Reconciliation

**State:** `IMPLEMENTATION_ACTIVE`

## Purpose

Reconcile the machine task gate with already-canonical MSTR-000A prerequisites A006 and A014 without granting B023 implementation authority by assertion. The repair remains repository-local, read-only, and fail-closed.

## Canonical diagnostic

On exact canonical `main=db12d1467bb81185a9affffb4d470626ceceddfa`, diagnostic run `33499263750` observed `task drift = clean` and `B023 eligible=false` because A006 and A014 returned `prerequisite.missing_task_binding`. B002 and B022 were independently recognized as `COMPLETE_CANONICAL`.

## Binding rule

An external prerequisite is satisfied only when the catalog contains an explicit repository-local cross-workstream binding, the exact bound canonical task checklist contains one checked task entry, the exact bound evidence declares both the expected task identity and `COMPLETE_CANONICAL`, and every required evidence path exists inside the repository. Unknown external prerequisite ids remain fail-closed.

## Authority boundary

This maintenance repair creates no external authority, candidate-pool decision, task completion state, model access, model execution, paid compute, training, large dataset ingestion, or production release. It only permits the existing B002 machine gate to verify already-canonical cross-workstream prerequisites.

## Independent-review hardening

The review repair binds each external prerequisite to an explicit fully qualified `task_identity`, permits only the repository-owned MSTR-000A checklist/evidence namespace for these v0 external bindings, and requires exactly one structured `Task` declaration plus exactly one structured `State` declaration in the bound canonical evidence. Duplicate or split identity/state records fail closed.

A006's older canonical evidence uses the legacy bare `A006` task token. The gate qualifies that token only through the explicit `MSTR-000A / A006` binding plus the enforced MSTR-000A checklist and evidence namespace; a bare token cannot select another workstream or evidence namespace. A014 already declares the fully qualified identity directly.

## Review diagnostic hardening

Independent review also identified that an absent, unreadable, or non-unique external checklist entry was reported as `prerequisite.state_checkbox_conflict`. The repair now distinguishes an unverifiable checklist as `prerequisite.external_checkbox_unverifiable` while preserving `prerequisite.state_checkbox_conflict` for a uniquely located but unchecked checklist entry. Both cases remain fail-closed.
