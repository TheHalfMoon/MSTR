# MSTR-000 Implementation Readiness Checklist

MSTR-000 is a qualification program. This checklist governs whether the project is ready to move from preconstruction into serious model training.

## Universal-laptop product gate

- [ ] Exact supported OS/CPU matrix is measured and documented rather than summarized as generic x86_64/ARM64 support.
- [ ] Reference 8 GB system runs MSTR alongside the reference OS/editor workload without OOM or sustained swap thrashing.
- [ ] 8K default context is proven; 4K/8K/16K memory and latency behavior are separately characterized.
- [ ] No discrete GPU is required.
- [ ] Primary Q4 model artifact meets the <=3 GB target or an explicit founder-approved revision exists.
- [ ] MSTR process RSS is measured against the <=4 GB soft target at the reference 8K context, and whole-system responsiveness is acceptable.
- [ ] Windows, Linux, and macOS runtime paths are proven or precisely scoped with no misleading compatibility claim.
- [ ] CPU-only TTFA, TTFCE, and TTVC are measured on real repositories.
- [ ] Sustained CPU inference is tested for throttling and interactive usability; energy/task is recorded where reliable counters exist.
- [ ] 4 GB and older-hardware behavior is characterized even if it is not the mandatory primary floor.

## Universal distribution/install/privacy gate

- [ ] Local use requires no provider account, API key, or subscription.
- [ ] Offline operation after installation is proven.
- [ ] Telemetry and network egress are off by default.
- [ ] Basic local coding assistance launches without requiring Docker, Python, Node.js, or building MSTR from source.
- [ ] A portable CPU runtime path is proven for the primary artifact.
- [ ] TTFI/install friction is measured on each required OS path.
- [ ] Artifact checksums, quantization provenance, runtime version/build flags, and installation provenance are recorded.

## Model rights and candidate gate

- [ ] Every primary candidate has an exact upstream revision and license/terms record.
- [ ] Primary candidate rights permit intended personal and commercial use.
- [ ] Primary candidate rights permit modification/fine-tuning and quantization/conversion.
- [ ] Primary candidate rights permit redistribution of intended derivative MSTR weights/artifacts.
- [ ] Primary release does not require every end user to obtain a separate provider account or commercial model license.
- [ ] Runtime/tool dependency licenses are compatible with the intended release.
- [ ] Teacher/API-output and dataset rights are tracked separately from the base-model license.
- [ ] `Qwen/Qwen2.5-Coder-3B` remains excluded from primary-backbone eligibility while its upstream research/non-commercial license remains incompatible.

## Model quality gate

- [ ] At least three materially different eligible compact candidates were qualified.
- [ ] Candidate comparison used the same interaction contract and evaluation manifest.
- [ ] Q4 quality and tool-call reliability were measured, not inferred from BF16/reference precision.
- [ ] Top candidates received equivalent bounded adaptation before final ranking where required.
- [ ] No vendor-reported leaderboard result is used as the sole selection reason.
- [ ] A lower-bound very-small coder control is included so MSTR does not assume more parameters automatically improve laptop utility.

## Interaction-contract gate

- [ ] Prompt prefix is versioned and cache-stable.
- [ ] Tool grammar is versioned.
- [ ] Tool-result serialization is deterministic.
- [ ] FIM control semantics are frozen.
- [ ] Edit grammar is frozen.
- [ ] Stale-write/file-version behavior is deterministic.
- [ ] Local inference baseline and cache behavior are recorded.
- [ ] Network/privacy/sandbox semantics visible to the model are frozen.
- [ ] Task-state/compaction schema is frozen if used.

## Runtime gate

- [ ] Exact-search baseline exists.
- [ ] Tree-sitter/symbol context marginal value is measured.
- [ ] Any additional index/retriever proves value per RAM, disk, token, and millisecond.
- [ ] Context-engine memory is included in the 8 GB whole-laptop budget.
- [ ] Graphify and Code-Graph-RAG are not mandatory unless tournament evidence justifies them.
- [ ] Deterministic apply engine passes stale/conflict tests.
- [ ] Verification path can run locally without a cloud service.

## Evaluation-integrity gate

- [ ] Raw model, neutral harness, and full MSTR system are scored separately.
- [ ] Private MSTR Gauntlet design exists before major training.
- [ ] Training contamination controls are defined.
- [ ] Runtime answer-leakage controls are defined separately.
- [ ] Public benchmark limitations are documented.
- [ ] Material results bind exact model/artifact/runtime/hardware/config/task identities.

## Environment/RL readiness gate

- [ ] Executable-task factory MVP exists.
- [ ] Oracle/reference patch passes.
- [ ] No-op state fails.
- [ ] Unsolved-state/difficulty check exists.
- [ ] Reward-shortcut battery exists.
- [ ] Future-history/public-solution leakage is blocked in solver environments.
- [ ] Environment reset/startup/storage throughput is measured.
- [ ] CPU/sandbox capacity estimate accompanies any future GPU-RL budget.

## Governance gate

- [ ] MSTR-000 planning itself contains no unauthorized model-weight downloads, paid model calls, or rented training execution.
- [ ] All MSTR-000 tasks relevant to closeout are complete.
- [ ] Evidence is bound to exact model/runtime/config identities.
- [ ] Material findings are reconciled.
- [ ] Independent review is complete.
- [ ] Founder explicitly accepts the MSTR-000 closeout.

If any mandatory item remains unresolved, MSTR-001 may perform only bounded follow-up experiments; long training is not ready.
