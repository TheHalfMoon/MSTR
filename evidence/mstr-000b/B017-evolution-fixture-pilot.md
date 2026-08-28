# B017 — Fixture-Only Software-Evolution Projection Pilot

**Task:** `B017`
**State:** IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT
**Canonical main at execution:** `f7a386214a1346b75dd3311390aa1e19bf354bb1`
**Exact entry evidence:** run `33174634290` / job `98859944051` — SUCCESS

## Scope

B017 implements the smallest fixture-only proof required by the canonical MSTR-000B plan. It does not ingest a corpus and does not access or execute model weights.

Implementation:

- `src/mstr_qualify/software_evolution.py`
- `tests/fixtures/software_evolution/b017-localization.json`
- `tests/fixtures/software_evolution/b017-edit.json`
- `tests/fixtures/software_evolution/b017-review-repair.json`
- `tests/unit/test_software_evolution_projection.py`

The pilot accepts only `REPOSITORY_OWNED_FIXTURE` or `SYNTHETIC_VERIFIED` B016 records with compatible rights, complete provenance lineage, and `CLEAR` contamination status.

## Frozen B016 Contract Consumption

B017 consumes `mstr.software-evolution-record.v0` without changing its schema or runtime registration.

The projector validates the frozen B016 schema first, then applies stricter fixture-pilot invariants required to make deterministic forward-step projections safe:

1. event IDs are unique across all event collections;
2. event sequence values are globally unique;
3. events are projected in deterministic global sequence order independent of source-array ordering;
4. every change extends the current revision linearly;
5. test/CI and review events bind to the current revision at their sequence point;
6. recovery events reference a prior trigger event and advance the current revision to their declared resulting revision;
7. `final_revision` equals the terminal fixture revision;
8. visible-context and future-history target/cutoff identities agree exactly;
9. the target is the first chronological event after the cutoff;
10. every post-cutoff event is `FUTURE_HIDDEN`;
11. every pre-cutoff revision-changing event is model-visible;
12. declared visible-event IDs equal the complete model-visible pre-cutoff set;
13. declared excluded-future-event IDs equal the complete post-cutoff set;
14. visible artifact IDs may not contain future change, test/CI, or review artifact identities;
15. review-repair projections require their trigger event to be model-visible.

The model-visible projection and supervision target are serialized separately. Future targets, final revision evidence, later tests, later reviews, and later change artifacts are not copied into `model_input` for forward-step examples.

Visible events retain the B016 event-specific fields and also expose `evolution_event_type` so a `TEST_CI` collection event remains distinguishable from its inner `event_kind` value such as `TEST` or `CI`.

## Demonstrated Projections

### Localization

`b017-localization.json` projects a first-change localization target from direction/base context only. The target change and every later event remain future-hidden.

### Edit

`b017-edit.json` projects a second edit after a visible first change, failed test, review, and replan. The target patch identity, target revision transition, and later passing test remain outside model-visible input.

### Review Repair

`b017-review-repair.json` projects a repair action after a visible failing test and review. The repair itself and the later passing test remain future-hidden.

## Adversarial Coverage

The focused tests reject:

- duplicate cross-collection event IDs or sequences;
- non-linear revision ancestry;
- stale test/review revision references;
- incorrect terminal revision;
- target/cutoff inconsistencies;
- non-first target events;
- visible/excluded event-set inconsistencies;
- model-visible future events;
- future patch or future test evidence in visible artifacts;
- non-fixture public repository inputs;
- unresolved rights, provenance, or contamination;
- retrospective-review mode in this forward-step pilot;
- projection-kind/target-kind mismatch;
- review-repair with a hidden trigger.

## Execution Evidence

Entry gate:

- run `33174634290`, job `98859944051` — SUCCESS
- B017 `eligible=true`
- B017 `canonical_state=PENDING`
- B017 external authority required: `false`
- task drift: clean
- B011: blocked

Intermediate build evidence retained transparently:

- run `33176620366`, job `98866797026` — FAILED during the aggregated frozen-gates step; identity, entry, exact scope, and focused tests had passed. This run is not treated as PASS.
- diagnostic run `33176730639`, job `98867173563` — the same pre-fix candidate independently passed offline validation, full pytest, Ruff, and mypy as separate steps. This diagnostic does not replace exact-head qualification.
- run `33177063565`, job `98868325024` — FAILED at the standalone full Ruff step after entry, scope, focused tests, offline validation, and full pytest passed. This run is not treated as PASS.
- Ruff-family diagnostic run `33177289096`, job `98869095454` — configured `E`, `F`, `I`, `UP`, and `B` rule families each passed independently on the same candidate. This diagnostic does not replace exact-head qualification.
- exact-head qualification attempt run `33177408512`, job `98869505359` — FAILED at `git diff --check` because this evidence file contained Markdown trailing whitespace. No later gate in that run executed, and the run is not treated as PASS.

A later exact-final-head qualification is required before merge and is the only evidence that may qualify the final implementation candidate.

## Authority Boundary

B017 creates no external-effect authority.

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
```

B011 remains blocked by its exact repository-required founder authority envelope.
