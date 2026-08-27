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

Then B013 may include the candidate in the stable pool.

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

## Training Hard Stop

Even after B034:

```text
TRAINING = NOT_AUTHORIZED
```

The next training gate must be explicit and must name exact model(s), data manifest, recipe/method cells, compute, cost, network, checkpoints and stopping/regression rules.
