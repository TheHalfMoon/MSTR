# Implementation Handoff — MSTR-000B

## Objective

Implement the strongest evidence-driven pre-training foundation for MSTR's code-specialized mission without starting training or weakening the universal-laptop contract.

## Canonical Entry

Read:
1. `AGENTS.md`;
2. constitution;
3. `CURRENT_STATE.md`;
4. `PROGRAM_ROADMAP.md`;
5. `CODE_MODEL_SUPREMACY_STRATEGY.md`;
6. MSTR-000A package;
7. this full MSTR-000B package.

## First Implementation Unit

Start with B001/B002 unless live repository truth shows a canonical successor already implemented.

Do not modify or close active PR #38 work unless its exact task and branch ownership require it. MSTR-000B planning was authored while PR #38 (`A003 event log + deterministic replay`) was open.

## Key Design Decisions

- `MSTR-000B` does not select a final model.
- `Mellum-4b-base` is mandatory to review but receives no admission privilege.
- new candidate weight access is separately gated;
- student self-alignment is first-class;
- teacher output is untrusted until independently verified;
- difficulty is student/checkpoint-relative;
- verifier health is part of training admission;
- test generation is a core learned skill;
- feature/greenfield tasks are first-class;
- Q4 regression is part of every material training promotion;
- default runtime remains one builder + independent deterministic verifier;
- WePLD is the primary Half Moon full-system partner, not a raw-model score multiplier.

## Execution Discipline

For every B-task:

```text
verify live main
-> task eligibility
-> focused branch
-> smallest compliant implementation
-> tests/fixtures/evidence
-> frozen quality gates
-> PR
-> exact-head review
-> resolve material findings
-> merge expected head
-> canonical reconciliation
-> next eligible task
```

No force-push/rebase/destructive history rewrite.

## Hard Stop

If a task requires:
- new model weight access outside current authority;
- paid compute/API;
- large corpus ingestion;
- weight-changing training;
- private user trace ingestion;

stop at the exact gate with a complete authorization envelope. Do not infer permission from generic continuation.
