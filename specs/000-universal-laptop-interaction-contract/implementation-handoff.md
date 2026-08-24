# MSTR-000 Implementation Handoff

## Mission

Continue MSTR exactly from canonical repository truth. Do not redesign the project, reopen settled planning without evidence, select a backbone early, or start training outside an explicit task gate.

## Start Here

Read in this order:

1. `AGENTS.md`
2. `.specify/memory/constitution.md`
3. `docs/canonical/CURRENT_STATE.md`
4. `docs/canonical/PROGRAM_ROADMAP.md`
5. `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`
6. `specs/000-universal-laptop-interaction-contract/spec.md`
7. `clarification-closeout.md`
8. `research.md`
9. `plan.md`
10. `data-model.md`
11. `contracts/`
12. `quickstart.md`
13. `checklists/implementation-readiness.md`
14. `tasks.md`
15. `docs/handoffs/MSTR-RESUME-AFTER-WEPLD.md`

## Current canonical point

```text
MSTR-000 = CANONICAL_ACTIVE_BUT_PAUSED
T000-T009 = COMPLETE_CANONICAL
NEXT_TASK_ON_RESUME = T010
FINAL_BACKBONE = UNSELECTED
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
TRAINING = NONE
LONG_TRAINING = PROHIBITED_IN_MSTR-000
LARGE_SCALE_RL = PROHIBITED_IN_MSTR-000
```

## Founder pause

MSTR is intentionally paused after plan finalization so the founder can finish WePLD.

Do not start T010 or any later task until the founder explicitly resumes MSTR. On resume, verify live GitHub truth before any mutation.

## Strategy per task

```text
verify live base
-> focused branch
-> confirm task prerequisites/authority
-> smallest implementation
-> focused/full tests where available
-> exact evidence
-> update task/state traceability
-> exact-head review
-> canonical merge
```

## Training direction — future only

Google Colab + Unsloth is the preferred accessible future training path, subject to the selected backbone and later Spec Kit gates. For a Qwen3.5 compact winner, current planning uses bf16 LoRA as the first pilot and treats QLoRA as experimental.

This is not current execution authority. See `docs/canonical/TRAINING_EXECUTION_STRATEGY.md`.

## Do Not

No force push or destructive history rewriting. No model weights unless the exact task authorizes them. No gated-term acceptance, paid API, paid Colab, rented compute, or training without explicit authority. No large corpus/long SFT/RL. No one-benchmark selection. No silent hardware-floor change. No binaries/caches/credentials/private data in Git. No mandatory graph/vector/subagent complexity without tournament evidence.

## Product invariant

`download -> install/launch -> open repo -> local coding assistance`

No discrete GPU, provider login, API key, subscription, activation, mandatory cloud, or Docker/Python/Node requirement for basic end-user launch.

## Done means for MSTR-000

Freeze measured support floor, distribution contract, local runtime/Q4, Interaction Contract v1, deterministic apply, minimal context, top backbone/top-two, environment MVP requirements, bounded MSTR-001 proposal, independent review, and founder acceptance.
