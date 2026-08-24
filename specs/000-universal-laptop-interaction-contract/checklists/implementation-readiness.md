# MSTR-000 Implementation Readiness Checklist

MSTR-000 is a qualification program. This checklist governs whether the project is ready to move from preconstruction into serious model training.

## Universal-laptop product gate

- [ ] Exact supported CPU architectures are measured and documented.
- [ ] 8 GB RAM reference system can load and use the primary Q4 candidate without swap-thrashing under the bounded reference context.
- [ ] No discrete GPU is required.
- [ ] Primary artifact meets the download-size target or an explicit founder-approved revision exists.
- [ ] Windows, Linux, and macOS runtime paths are proven or explicitly scoped with no misleading compatibility claim.
- [ ] CPU-only TTFA and TTVC are measured on real repositories.

## Model gate

- [ ] At least three materially different eligible 2B–4B candidates were qualified.
- [ ] Candidate comparison used the same interaction contract and evaluation manifest.
- [ ] Q4 quality and tool-call reliability were measured, not inferred from BF16.
- [ ] Top candidates received equivalent bounded adaptation before final ranking where required.
- [ ] No vendor-reported leaderboard result is used as the sole selection reason.

## Interaction-contract gate

- [ ] Prompt prefix is versioned and cache-stable.
- [ ] Tool grammar is versioned.
- [ ] Tool-result serialization is deterministic.
- [ ] FIM control semantics are frozen.
- [ ] Edit grammar is frozen.
- [ ] Stale-write/file-version behavior is deterministic.
- [ ] Local inference baseline and cache behavior are recorded.

## Runtime gate

- [ ] Exact-search baseline exists.
- [ ] Tree-sitter/symbol context marginal value is measured.
- [ ] Any additional index/retriever proves value per RAM, token, and millisecond.
- [ ] Graphify and Code-Graph-RAG are not mandatory unless tournament evidence justifies them.
- [ ] Deterministic apply engine passes stale/conflict tests.
- [ ] Verification path can run locally without a cloud service.

## Evaluation-integrity gate

- [ ] Raw model, neutral harness, and full MSTR system are scored separately.
- [ ] Private MSTR Gauntlet design exists before major training.
- [ ] Training contamination controls are defined.
- [ ] Runtime answer-leakage controls are defined separately.
- [ ] Public benchmark limitations are documented.

## Environment/RL readiness gate

- [ ] Executable-task factory MVP exists.
- [ ] Oracle/reference patch passes.
- [ ] No-op state fails.
- [ ] Reward-shortcut battery exists.
- [ ] Environment reset/startup/storage throughput is measured.
- [ ] CPU/sandbox capacity estimate accompanies any future GPU-RL budget.

## Governance gate

- [ ] All MSTR-000 tasks relevant to closeout are complete.
- [ ] Evidence is bound to exact model/runtime/config identities.
- [ ] Material findings are reconciled.
- [ ] Independent review is complete.
- [ ] Founder explicitly accepts the MSTR-000 closeout.

If any mandatory item remains unresolved, MSTR-001 may perform only bounded follow-up experiments; long training is not ready.
