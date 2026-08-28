# B016 — Software Evolution Record v0

**Task:** `B016`
**State:** IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT
**Canonical main at execution:** `2cd82ba78bcb886962a163013fa2861d5dd2b013`
**Exact entry evidence:** run `33171129526` / job `98848292231`

## Decision

B016 freezes `mstr.software-evolution-record.v0` as the structural contract for repository-evolution lineage used by later fixture extraction and data-engine work.

The record binds:

- repository and base revision identity;
- issue/feature/direction identity;
- an explicit visible-context manifest for one target step;
- ordered change, test/CI, review, and recovery event records;
- final revision and final verifier identity;
- provenance, rights, and contamination evidence states;
- an explicit future-history boundary for every model-facing projection.

The design schema and runtime schema are byte-identical. Dedicated valid and invalid fixtures are registered in the offline schema validator.

## Future-history boundary

The contract supports exactly two projection modes:

```text
FORWARD_STEP
RETROSPECTIVE_REVIEW
```

`FORWARD_STEP` is fail closed. The following channels are structurally forced to `HIDDEN`:

```text
final_revision_visibility
future_patch_visibility
future_test_result_visibility
future_review_visibility
```

A forward projection also rejects a retrospective-context reason. This prevents a record from silently labeling future information as intentionally retrospective while still claiming to be a forward training step.

`RETROSPECTIVE_REVIEW` requires an explicit `retrospective_context_reason`. Future information may be visible only through the explicit `VISIBLE_AS_RETROSPECTIVE_CONTEXT` state; it is never the default.

Every change/test/CI/review/recovery event independently declares `model_visibility` as one of:

```text
MODEL_VISIBLE
VERIFIER_ONLY
FUTURE_HIDDEN
```

The visible-context manifest binds the target event, cutoff sequence, visible artifacts/events, and the explicit set of excluded future event identities.

## B016 / B017 boundary

B016 freezes representation and fail-closed visibility semantics. JSON Schema intentionally does not pretend to evaluate cross-event arithmetic or graph consistency such as proving that every `excluded_future_event_id` has a sequence greater than the cutoff or that every referenced event ID exists exactly once.

B017 owns the tiny fixture-only extractor/projection proof that will enforce deterministic ordering, referential integrity, cutoff application, and projection behavior over synthetic or repository-owned fixtures. B017 must reject any projection that would expose an event after the declared cutoff in `FORWARD_STEP` mode.

This separation keeps B016 a stable data contract and B017 the executable semantic proof.

## Rights, provenance, and contamination

The record requires provenance, rights, and contamination fields even when their state is unresolved or incompatible. The schema preserves negative/failure evidence rather than making invalid source material unrepresentable.

```text
provenance.lineage_status = COMPLETE | INCOMPLETE | UNRESOLVED
rights.decision = COMPATIBLE | INCOMPATIBLE | UNRESOLVED
contamination_status = CLEAR | DETECTED | UNRESOLVED
```

Training admission is not created by this record. `MSTR-DATA-CONSTITUTION-v0` remains the authority for stage admission and fails closed on unresolved/incompatible rights, contamination, provenance, benchmark, verifier-health, and related policy requirements.

## Canonical entry provenance

```text
ENTRY_GATE_TASK = B016
ENTRY_GATE_CANONICAL_MAIN = 2cd82ba78bcb886962a163013fa2861d5dd2b013
ENTRY_GATE_RUN = 33171129526
ENTRY_GATE_JOB = 98848292231
ENTRY_GATE_ELIGIBLE = true
ENTRY_GATE_DRIFT = clean
```

## Scope and non-authorities

This task is contract/fixture work only. It performs no corpus extraction beyond repository-owned test fixtures and grants no external-effect authority.

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B011 remains separately blocked on its exact founder weight-access authority envelope.
