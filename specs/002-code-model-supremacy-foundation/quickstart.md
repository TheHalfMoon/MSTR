# Quickstart — MSTR-000B

## Preconditions

```text
MSTR-000B_SPEC_KIT = CANONICAL
WEIGHT_CHANGING_TRAINING = NO
PAID_COMPUTE = NO
LARGE_DATASET_INGESTION = NO
FOUNDER_MAC_LARGE_ARTIFACTS = ZERO
```

Before each task:
1. fetch exact live `main` and inspect open PRs/reviews/checks;
2. read the exact task prerequisites/external-effect class;
3. for B001/B002 only, manually verify exact prerequisites because the validator is not yet canonical;
4. once B002 is `COMPLETE_CANONICAL`, require exact-main `eligible=true` before every material B003+ task execution and again before merge;
5. fail closed on validator error/ineligible result, supersession, missing authority, candidate-pool mismatch, or canonical drift;
6. do not infer external-effect or training authority from this workstream.

## Immediate Implementation Order

The bootstrap governance chain is:

```text
B001 task contracts
-> B002 task eligibility validator
-> B003 drift detector
-> B004 sequence reconciliation
```

Only B001/B002 use manual gate verification. B003+ uses the canonical machine gate.

In parallel, metadata-only backbone work may proceed under exact prerequisites:

```text
B005 rescan
-> B006 candidate records
-> B007 tokenizer protocol
-> B008 tokenizer economics
-> B009 compatibility matrix
```

B010 separates `qualification_candidates[]` from `new_weight_access_required_candidates[]`. No new model artifact may be acquired until B011 has exact founder authorization for a non-empty access-required list. A candidate that needs no new acquisition may still require B012 equivalent qualification.

## Data / Training-Signal Contract Order

B014 is the root of several parallel contract branches; they are not one serial chain:

```text
B014 Data Constitution
  |
  +-> B015 language/tooling policy
  |
  +-> B016 software evolution -> B017 fixture extractor
  |
  +-> B018 self-alignment -> B019 teacher-rescue policy
  |
  +-> B020 difficulty -> B021 frontier calibrator
  |
  +-> B022 verifier-health contract
  |      + A006 finalizer + A014 shortcut battery + B002
  |      -> B023 verifier-health evaluator
  |      -> B024 test-generation curriculum
  |
  +-> B025 feature/greenfield curriculum

B022 + B024 + B025 -> B026 research ladder
```

Fixture-only validation is preferred before any large corpus or training proposal. Self-alignment, teacher, and generated-test admission must bind exact provenance, rights, contamination, and verifier-health evidence.

## Candidate Convergence

A new candidate joins headline comparison only after:

```text
static rights/provenance PASS
+ B010 qualification classification
+ exact acquisition authority if new access is needed
+ verified artifact identity where applicable
+ B012 equivalent Q4/runtime/resource/raw qualification
+ tokenizer economics
+ comparable evidence
```

`B011 = NOT_REQUIRED_NO_NEW_ACCESS` does not skip B012 when a qualification candidate exists.

Before B013 may freeze `stable_pool=true`, create a frontier-freshness snapshot at exact B013 entry. Compare the snapshot cutoff against the last canonical backbone/access scan and explicitly disposition every material compact code/model release that could plausibly change the universal-laptop candidate decision.

```text
B012 complete
-> exact B013 entry gate
-> frontier snapshot
-> material post-scan releases?
   |
   +-> NO / all evidence-backed terminal dispositions
   |      -> comparable stable pool may be frozen
   |
   +-> YES / plausible challenger lacks equivalent qualification
          -> B013 remains PENDING
          -> STOP
          -> create separately governed refresh/task-graph amendment
          -> metadata/rights/tokenizer/compatibility
          -> exact access envelope + Founder authority if new weight access is required
          -> equivalent qualification
          -> resume B013 only after canonical refresh or evidence-backed rejection
```

Do not rewrite completed historical B005-B012 work to simulate a new scan. Preserve historical truth and use a canonical successor/addendum path.

For the 2026-09-04 frontier snapshot, `K2 Horizon 3.7B` is a mandatory review input only. It is not admitted or authorized by naming it.

The detailed planning amendment is `docs/canonical/MSTR_FRONTIER_ACCELERATION_STRATEGY.md`; external research detail is in `research-frontier-2026-09-04.md`.

## Q4 Promotion

Every material weight-changing checkpoint later in the program must pass:

```text
source checkpoint hash
-> merged-master hash
-> pinned export tool/revision + recipe hash
-> canonical Q4 hash
-> pinned quantizer/revision + recipe hash
-> required Q4 regressions
-> applicable universal-laptop gate
-> Q4PromotionRecord = PROMOTED
```

Only a promoted checkpoint may parent the next material stage.

Q4 remains the mandatory promotion/product anchor. Future Q3/Q2/structured-ternary or Sherry-class experiments are additive challenger arms only; they cannot replace the required Q4 record. Any low-bit method that changes weights remains behind exact training authority.

## Downstream Acceleration Handoff

When B032 becomes eligible, it must carry the canonical frontier-acceleration strategy into downstream work without executing it prematurely:

```text
MSTR-001
  checkpoint-lineage substrate comparison where applicable
  + code/FIM/repository prior
  + low-bit compatibility awareness
  + mandatory Q4 promotion

MSTR-002
  production-compatible software-engineering trajectories
  + failure/recovery/negative examples

MSTR-003
  executable RL
  + dynamic synthetic environments
  + previous-MSTR bootstrap with independent admission
  + targeted trajectory-feedback research
  + reward-shortcut resistance

MSTR-004
  Q4 anchor
  + Q3/Q2/structured-ternary challengers
  + runtime/kernel/speculation/parallel-generation research
  + FAST/NORMAL/DEEP effort control
  + TTVC as the speed north star

MSTR-006
  sealed public-derived evaluation
  + fresh/private Gauntlet
  + future-Git-history/network/public-solution leakage controls
```

## Training Hard Stop

Even after B034:

```text
TRAINING = NOT_AUTHORIZED
```

The next training gate must be explicit and must name exact model(s), data manifest, recipe/method cells, compute, cost, network, checkpoints and stopping/regression rules.