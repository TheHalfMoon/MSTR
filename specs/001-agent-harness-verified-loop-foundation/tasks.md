# Tasks — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

```text
WORKSTREAM = MSTR-000A
EARLY_SAFE_ENTRY = AFTER_FOUNDATIONAL_T011_WHEN_EXACT_TASK_DEPENDENCIES_ARE_SATISFIED
CONVERGENCE_ENTRY = STABLE_EQUIVALENT_CANDIDATE_QUALIFICATION + MSTR-000B_REQUIRED_OUTPUTS
WEIGHT_CHANGING_TRAINING = PROHIBITED
PAID_COMPUTE = PROHIBITED
LARGE_DATASET_INGESTION = PROHIBITED
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

## Sequence Amendment

The original blanket `ENTRY_GATE = T034_COMPLETE_CANONICAL` is superseded because model-independent MSTR-000A infrastructure can safely advance before candidate convergence and live history already contains canonical A001/A002 work.

```text
EARLY_SAFE = A001-A018 when each exact prerequisite is satisfied and no unqualified candidate result is consumed
CONVERGENCE = A019-A024 only after stable/equivalent candidate qualification and the MSTR-000B prerequisites named below
```

T029–T034 in MSTR-000 remain active according to their own canonical state and are not reopened by this package. No A-task may bypass an explicit external-effect gate. The machine task validator introduced by MSTR-000B becomes authoritative for eligibility once canonical.

## Phase A — Contract and Replay Spine

- [x] **A001 [P] Freeze canonical `mstr.loop-contract.v0` implementation contract** from the planning schema, including success/verifier, recovery, budgets, and effect envelope semantics.  
  Outputs: `schemas/mstr-loop-contract-v0.schema.json`, contract fixtures, `evidence/mstr-000a/A001-loop-contract.md`.  
  Canonical implementation: PR #37 / merge `5693749dd560979496efad488789ec35b2c2a84d`.

- [x] **A002 [P] Freeze typed append-oriented run-event vocabulary and canonical serialization/hash rules.**  
  Outputs: `schemas/mstr-run-event-v0.schema.json`, event fixtures, serialization tests, `evidence/mstr-000a/A002-event-contract.md`.  
  Canonical implementation: PR #37 / merge `5693749dd560979496efad488789ec35b2c2a84d`.

- [ ] **A003 Implement append-oriented event log + monotonic sequence validation + deterministic replay.**  
  Must prove model-visible history reconstruction from events.  
  Outputs: implementation under `src/mstr_qualify/`, unit/contract tests, `evidence/mstr-000a/A003-event-log-replay.md`.

- [ ] **A004 Implement `AgentState` projection and bounded compaction.**  
  Must preserve uncertainty, verifier failures, changed files, known failures, and remaining work.  
  Outputs: projection/compaction module, adversarial compaction fixtures, `evidence/mstr-000a/A004-agent-state.md`.

**Checkpoint A:** event log is authoritative; model history and AgentState are reproducible projections.

## Phase B — Build Loop + Harness Arms

- [ ] **A005 Implement `MSTR-BUILD-LOOP-v0` bounded state graph.**  
  Conceptual states: ORIENT, GOAL, LOCALIZE, PLAN, ACT, OBSERVE, VERIFY, RECOVER, STOP. The graph MUST support a trivial-task fast path and MUST NOT force every task through every conceptual state. Builder cannot directly emit canonical success.  
  Outputs: loop implementation, state-machine tests, `evidence/mstr-000a/A005-build-loop.md`.

- [ ] **A006 Implement protected finalizer / verifier boundary.**  
  Success must be mechanically derived from required verifier results; fake model completion must fail.  
  Outputs: finalizer/verifier interface, contract/security tests, `evidence/mstr-000a/A006-finalizer.md`.

- [ ] **A007 Implement H0 neutral-minimal harness.**  
  Minimum repository read/search, shell, one deterministic edit/apply path, verifier invocation, bounded state.  
  Outputs: neutral harness profile/config + tests + `evidence/mstr-000a/A007-neutral-harness.md`.

- [ ] **A008 Implement H1 MSTR-native typed harness.**  
  Adds typed tools/results, stale-safe edits, selective context, recovery cadence, compact state, and measured cache/prefix semantics where applicable.  
  Outputs: native harness profile/config + tests + `evidence/mstr-000a/A008-mstr-harness.md`.

- [ ] **A009 Implement H2 WePLD-native adapter.**  
  Map WePLD goal/spec/task/effect/verifier state into MSTR loop contracts without making WePLD mandatory for standalone MSTR.  
  Outputs: adapter contract/config, integration fixtures, `evidence/mstr-000a/A009-wepld-adapter.md`.

- [ ] **A010 Freeze evidence-derived `CapabilityProfile` contract for WePLD routing.**  
  Include reliable context budget, edit preference, tool reliability, localization, planning depth, verifier cadence, repair depth, FIM/shell/compaction strength.  
  Outputs: schema + fixtures + `evidence/mstr-000a/A010-capability-profile.md`.

**Checkpoint B:** same model can run under neutral/MSTR/WePLD harness surfaces with exact score separation.

## Phase C — Environment + Verifier Factory MVP

- [ ] **A011 Freeze environment/setup/verifier manifest schemas and effect boundaries.**  
  Outputs: schemas, known-good/known-bad fixture contracts, `evidence/mstr-000a/A011-env-verifier-contracts.md`.

- [ ] **A012 Implement clean-checkout environment reset/setup abstraction.**  
  Must record repo revision, setup recipe, health targets, reset, network/effects, resource limits.  
  Outputs: environment module + integration tests + `evidence/mstr-000a/A012-environment-reset.md`.

- [ ] **A013 Implement bounded environment bootstrap/admission loop.**  
  Stage A defines health targets; Stage B attempts setup from clean state; independent checker verifies targets; repeated failure rejects the environment.  
  Outputs: admission module, fixtures, `evidence/mstr-000a/A013-autoinstall-admission.md`.

- [ ] **A014 Implement verifier runner + reward-shortcut battery.**  
  Cover test/evaluator deletion, assertion weakening, hardcoding, spoofing, cached/future solution leakage, prohibited network, and protected-path tamper.  
  Outputs: verifier modules, security tests, `evidence/mstr-000a/A014-verifier-shortcuts.md`.

**Checkpoint C:** at least one controlled environment proves known-good pass, no-op/broken fail, reset reproducibility, and shortcut resistance.

## Phase D — Direction-to-Done + Trajectory Factory

- [ ] **A015 Freeze `DirectionTaskManifest` and MSTR Direction-to-Done v0 task taxonomy.**  
  Include terse feature direction, multi-file construction, repair, build/tooling, bounded greenfield, WePLD-spec-driven, failure/recovery, and security-sensitive tasks. MSTR-000B B025 extends the greenfield/feature curriculum before headline convergence.  
  Outputs: schema/manifests + `evidence/mstr-000a/A015-direction-to-done.md`.

- [ ] **A016 Implement DVCR/TTVC + diagnostic metric computation.**  
  Mandatory: DVCR, TTVC, first-pass accept, edit-survival, repair success, tool-error, tool/tokens/context per verified completion, harness overhead. Repository Health Delta is added by MSTR-000B B030.  
  Outputs: metric module/tests + `evidence/mstr-000a/A016-metrics.md`.

- [ ] **A017 Freeze failure taxonomy and training trajectory contract.**  
  Preserve verified success, recovered success, valid failure, timeout, invalid environment/verifier, contamination/leakage/authority failure. MSTR-000B verifier-health records become a required admission input before training.  
  Outputs: `mstr.trajectory-manifest.v0`, failure taxonomy, fixtures, `evidence/mstr-000a/A017-trajectory-contract.md`.

- [ ] **A018 Implement trajectory recorder/replay/admission.**  
  Successful training examples require verifier proof; failures remain evidence; private user traces default to rejected/not-ingested.  
  Outputs: recorder/replay/admission modules + tests + `evidence/mstr-000a/A018-trajectory-factory.md`.

**Checkpoint D:** one successful and one failed/recovered trajectory replay from exact events and identities.

## Phase E — Harness Tournament + Research Loop — CONVERGENCE GATED

A019/A020 MUST NOT run as headline/final candidate evidence until MSTR-000B has produced the required stable pool and verifier/research contracts.

Prerequisites include at minimum:

```text
A001-A018 required outputs
+ existing-candidate T034/equivalent qualification
+ MSTR-000B B013 stable product-aligned candidate pool
+ MSTR-000B B023 verifier-health implementation
+ MSTR-000B B026 research ladder
```

- [ ] **A019 Run cross-harness baseline/tournament on the same qualified candidate/task cells.**  
  Compare H0 neutral, H1 MSTR, H2 WePLD where available. Pin model, artifact, runtime, interaction/loop, verifier health, task, sampling, timeout, cache, hardware. Candidate pool MUST equal the canonical B013 pool or carry a governed supersession.  
  Outputs: `artifacts/results/harness/A019/*.jsonl`, `artifacts/decisions/A019-harness-scorecard.json`, `evidence/mstr-000a/A019-harness-tournament.md`.

- [ ] **A020 Implement and qualify `MSTR-RESEARCH-LOOP-v0` with one non-weight-changing campaign using the MSTR-000B multi-fidelity ladder.**  
  Baseline -> hypothesis -> bounded mutation -> run -> evaluate -> keep/discard/crash; frozen evaluator/verifier/hidden tasks/budget/product constraints.  
  Outputs: research-loop contract/ledger/tests + `artifacts/results/research/A020/` + `evidence/mstr-000a/A020-autoresearch.md`.

**Checkpoint E:** autonomous bounded research decisions are reproducible and cannot mutate their evaluation authority.

## Phase F — Training-Readiness Reconciliation and Closeout

- [ ] **A021 Reconcile current MSTR-000 T035–T052 with MSTR-000A + MSTR-000B outputs.**  
  Ensure final Interaction Contract consumes Build Loop/event/state/verifier semantics and training-preflight uses trajectory/environment/data/verifier-health/curriculum contracts. No duplicate incompatible contract may remain.

- [ ] **A022 Reconcile current T065–T071 environment/verifier tasks.**  
  Mark each as consumed, superseded, or expansion/hardening beyond the MSTR-000A MVP. Duplicate implementation is prohibited. MSTR-000B B022/B023 verifier-health work is additive and must not be dropped.

- [ ] **A023 Amend downstream MSTR-001/MSTR-002/MSTR-003 entry contracts/roadmap requirements together with MSTR-000B B032.**  
  MSTR-001: Data Constitution + software evolution + code/FIM + difficulty/frontier + Q4 promotion.  
  MSTR-002: execution-grounded SFT + self-alignment + test generation + verifier health + failure/recovery + simplicity/surgical preference under same loop.  
  MSTR-003: bounded executable agent RL in admitted environments with frontier curriculum, verifier/reward-hacking controls, and multi-fidelity promotion.

- [ ] **A024 Final Constitution Check + MSTR-000A closeout.**  
  Freeze exact versions, unresolved risks, task supersession map, harness winner/default (if evidence supports one), Direction-to-Done v0 identity, environment/verifier MVP identity, and training-readiness statement.  
  Must include a pinned RAW_MODEL scorecard for every eligible B013 cell (or a recorded `N/A` reason per cell explaining why raw measurement is not meaningful), distinguishing model improvement from harness-only gains per constitution III.  
  Must consume or explicitly defer all MSTR-000B hard training-readiness prerequisites and leave weight-changing training under its separate founder gate.

## Hard Gates

MSTR-000A cannot close with any of these unresolved:

```text
MODEL_CAN_SELF_DECLARE_SUCCESS = YES
EVENT_REPLAY_INCOMPLETE = YES
HARNESS_GAIN_MISATTRIBUTION = YES
ENVIRONMENT_GOOD/BAD_CHECK_MISSING = YES
REWARD_SHORTCUT_BATTERY_MISSING = YES
DIRECTION_TO_DONE_IDENTITY_UNFROZEN = YES
FAILED_TRAJECTORIES_SILENTLY_DROPPED = YES
PRIVATE_USER_TRACE_DEFAULT_INGEST = YES
RESEARCH_LOOP_CAN_MUTATE_EVAL = YES
MSTR_000B_REQUIRED_CONVERGENCE_BYPASSED = YES
T053_OR_SUCCESSOR_TRAINING_GATE_BYPASSED = YES
```

## Quality Gates

Every material implementation head must run the repository's current frozen gates plus task-specific tests. Historical gate results are not reusable as PASS for a new head.

No CI run -> do not claim CI PASS.
