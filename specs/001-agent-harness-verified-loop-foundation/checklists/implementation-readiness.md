# Implementation Readiness Checklist — MSTR-000A

## Planning Package

- [x] Founder objective is explicit: smallest exceptional coding/building model, not general-purpose chat.
- [x] Product envelope remains 8 GB / CPU / 8K / Q4 <= 3 GB.
- [x] T029–T034 continuation is preserved.
- [x] Weight-changing training remains separately gated.
- [x] Build Loop, Environment Loop, and Research Loop are separately defined.
- [x] Neutral/MSTR/WePLD harness score surfaces are separated.
- [x] Environment/verifier MVP is moved before weight-changing agent training.
- [x] Private/fresh Direction-to-Done evaluation is required.
- [x] Failure/recovery trajectories remain first-class evidence.
- [x] Autoresearch may not mutate frozen evaluation authority.
- [x] Private user repository traces are excluded from training by default.
- [x] External donor projects are research references only until separately admitted.

## Required Before Implementation Starts

- [ ] This Spec Kit package is merged to canonical `main` on exact reviewed head.
- [ ] T034 is `COMPLETE_CANONICAL`.
- [ ] `CURRENT_STATE.md` points to MSTR-000A as the next mandatory workstream.
- [ ] No unresolved constitutional conflict exists.
- [ ] No active conflicting implementation PR changes the same authority surface.

## Required Before Event/Loop Code

- [ ] Canonical serialization rule is selected/reused.
- [ ] Loop/event/trajectory schemas pass validation fixtures.
- [ ] Event ordering/hash identity policy is frozen.
- [ ] Terminal success finalizer authority is explicit.

## Required Before Environment Execution

- [ ] Exact isolation/reset mechanism is admitted.
- [ ] Network/effect envelope is explicit.
- [ ] Known-good and known-bad verifier fixtures exist.
- [ ] Reward-shortcut test battery exists.
- [ ] Secrets/private-data handling is explicit.

## Required Before Harness Tournament

- [ ] Neutral harness qualified.
- [ ] MSTR native harness qualified.
- [ ] WePLD adapter qualified or explicitly deferred with a blocking reason.
- [ ] Comparable identity fields are complete.
- [ ] DVCR/TTVC and diagnostic metrics are mechanically reproducible.

## Required Before MSTR-000A Closeout

- [ ] Direction-to-Done v0 frozen.
- [ ] Successful and failed trajectories replay deterministically.
- [ ] Event integrity: every event carries a non-null SHA-256; replay rejects missing hashes, duplicate/gap/reordered/substituted events, and broken predecessor chains.
- [ ] Training trajectory admission contract frozen.
- [ ] Research Loop v0 baseline/keep/discard/crash behavior proven.
- [ ] Existing T035–T052 sequencing reconciled.
- [ ] Existing T065–T071 environment/verifier tasks reconciled against this MVP.
- [ ] MSTR-001/002/003 entry contracts updated or explicitly queued for update.
- [ ] T053 or successor remains a separate explicit founder weight-changing gate.
- [ ] Final Constitution Check rerun.

- RAW_MODEL scorecard required for every eligible tournament cell (or recorded N/A reason) before MSTR-000A closeout.
