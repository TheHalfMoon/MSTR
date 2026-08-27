# Research — MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Research date:** 2026-08-26; sequencing reconciliation 2026-08-27  
**Purpose:** Identify the highest-leverage harness, loop, environment, verifier, training-signal, and self-improvement patterns for a very small code-specialized model whose primary job is to turn terse software direction into verified working software.

## Research Question

What changes to the current MSTR plan most increase the probability that a <=3 GB Q4, 8 GB RAM, CPU-usable model becomes exceptionally strong at real coding/building rather than merely scoring well on isolated code benchmarks?

## Sequence Reconciliation

The source findings below remain valid. The original conclusion that all MSTR-000A implementation followed T034 was a planning simplification and is superseded by the canonical early-safe/convergence split when the MSTR-000B amendment merges:

```text
A001-A018 = may proceed early when exact dependencies hold and no unqualified candidate/external authority is consumed
A019-A024 = convergence-gated on equivalent candidate qualification + MSTR-000B candidate/verifier/research prerequisites
```

This is a sequencing correction, not a change to the research conclusion that environment/verifier/harness foundations must exist before weight-changing agent training.

## Decision Summary

1. **Train and serve inside compatible loop semantics.** Agent behavior must not be taught under a materially different tool/edit/state protocol from production.
2. **Build executable environment + verifier foundations before weight-changing agent training.** Training signal quality depends on runnable tasks and trustworthy rewards.
3. **Make the agent loop a first-class contract.** Prompt/tool schemas alone are insufficient for long-horizon software completion.
4. **Use a minimal default harness, not a permanent multi-agent scaffold.** A small model must learn software engineering rather than overfit one elaborate scaffold.
5. **Keep raw / neutral harness / optimized MSTR / WePLD system surfaces separate.** Harness improvements are valuable but are not raw model gains.
6. **Create a private/fresh Direction-to-Done surface.** Bug-patch benchmarks alone do not capture the founder goal of receiving a direction and building the requested software.
7. **Preserve failures and recovery.** Invalid tools, bad edits, build/test failures, timeouts, and repairs are useful training/evaluation signal.
8. **Build an autoresearch loop around frozen evaluation.** The agent may mutate bounded experimental surfaces, never the metric/verifier/hidden answer.
9. **Use selective context.** `NO_RETRIEVAL` must be a valid outcome; more context is not always better.
10. **Treat WePLD as the strongest Half Moon system integration, not as a mandatory standalone dependency.**
11. **Treat Q4 promotion as a checkpoint-parent gate.** A master-checkpoint gain is not allowed to seed the next material stage until export identity, artifact integrity, required Q4 regression, and applicable universal-laptop gates pass.

---

## Source Review

### 1. Karpathy — autoresearch

Sources:
- https://github.com/karpathy/autoresearch
- https://github.com/karpathy/autoresearch/blob/master/program.md

Relevant observations:
- The research loop deliberately freezes data prep/evaluation while the agent mutates a bounded training surface.
- Experiments use a fixed wall-clock budget and a single ledger with keep/discard/crash outcomes.
- Baseline is established before experimentation.
- Failed/crashed experiments remain recorded.
- Simplicity is an explicit decision criterion alongside metric improvement.
- The autonomous loop does not repeatedly ask the human for routine continuation.

MSTR adoption:
- Define `MSTR-RESEARCH-LOOP-v0` with frozen evaluator, verifier, hidden tasks, authority, and budget.
- Replace autoresearch's single loss metric with an MSTR multi-objective gate: DVCR primary, TTVC secondary, then Q4/laptop/security/reliability constraints.
- Do not permit a research agent to mutate the benchmark, verifier, or hidden acceptance criteria it is scored against.

Do not copy:
- Single-metric optimization as release authority.
- Assumption that one GPU/H100-class environment is the product environment.

### 2. DeepSeek Harness

Sources:
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md
- https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/core.md

Relevant observations:
- Model adapter, tool registry, session log, agent, and agent loop are separable/replaceable components.
- The session log is append-oriented and is the source from which model history is derived.
- Model-visible information is required to be reconstructable from durable events.
- Turns, steps, tool calls/results, cancellation/recovery, inbox state, and replay have explicit lifecycle semantics.
- The loop can be swapped without forcing every extension to depend on a concrete loop implementation.

MSTR adoption:
- Define typed append-oriented MSTR run events.
- Make `AgentState` a projection over durable facts rather than an opaque chat memory.
- Separate loop contract from concrete neutral/MSTR/WePLD harness implementations.
- Record every model-visible observation required for replay and training lineage.

Do not copy:
- DeepSeek Harness as a mandatory end-user dependency.
- A heavyweight all-plugin runtime if a substantially smaller MSTR implementation proves sufficient.

### 3. Cursor Composer / Composer 2 / Composer 2.5

Sources:
- https://cursor.com/blog/composer
- https://cursor.com/blog/composer-2
- https://cursor.com/blog/composer-2-5
- https://cursor.com/blog/bootstrapping-composer-with-autoinstall
- https://cursor.com/blog/real-time-rl-for-composer
- https://cursor.com/composer

Relevant observations from Cursor's public technical descriptions:
- Composer was trained for software engineering with production-like search/edit/terminal tools.
- Composer 2 uses continued code-focused pretraining followed by large-scale RL, and Cursor reports that lower code pretraining loss correlated with stronger downstream RL.
- Composer 2 RL is performed in realistic Cursor sessions using the same tools/harness class as deployment, reducing train/serve mismatch.
- Composer 2.5 emphasizes long-horizon work, instruction following, tool selection, intent understanding, reliability, and more complex RL environments.
- Autoinstall uses prior model versions to turn raw repo checkouts into runnable RL environments; setup quality is independently checked and repeatedly failing environments are rejected.
- Cursor's real-time RL discussion highlights train-test mismatch, production-derived feedback, and reward-hacking failure modes.

MSTR adoption:
- Preserve a strong code/FIM prior before agent RL.
- Generate SFT/RL trajectories inside the MSTR interaction/loop contract.
- Add environment bootstrap/admission before training.
- Preserve invalid tool calls and other failure signals instead of sanitizing them away.
- Use previous MSTR versions later to assist environment setup, task generation, run management, and research iteration.

Do not copy:
- Hidden production telemetry. MSTR telemetry remains off by default and private user repositories are excluded from training by default.
- Frontier-scale infrastructure assumptions.
- A cloud-only serving model.

### 4. Claude Loops

Source:
- https://claude.com/blog/getting-started-with-loops

Relevant observations:
- Loops become reliable when they have a clear goal, repeated action/check cycle, quantitative or mechanical verification, and explicit stop conditions.
- Goal-based loops differ from time/schedule/proactive orchestration loops.

MSTR adoption:
- Optimize MSTR weights and native harness for the **goal loop**: direction -> act -> verify -> repair -> stop.
- Leave scheduling/background/proactive orchestration primarily to WePLD or external orchestration rather than encoding it as core model behavior.

### 5. Loop Engineering

Sources:
- https://github.com/cobusgreyling/loop-engineering
- https://github.com/cobusgreyling/loop-engineering/blob/main/docs/loop-design-checklist.md

Relevant observations:
- Emphasizes designing a control loop rather than repeatedly hand-prompting an agent.
- Production loop readiness includes explicit goal/non-goals, persistent state, maker/checker separation, budgets, max attempts, escalation, observability, worktree/isolation, and kill criteria.
- The implementer should not be sole authority for declaring its own success.

MSTR adoption:
- Encode goal, non-goals, budgets, verifier set, recovery ceiling, stop/escalation, and result schema in a machine-readable loop contract.
- Keep verifier authority separate from the builder's terminal text.

Do not copy:
- A fleet/multi-agent stack as the default laptop architecture.

### 6. Karpathy-Inspired Coding Guidelines

Source:
- https://github.com/multica-ai/andrej-karpathy-skills

Relevant observations:
- Four useful behavioral targets: think before coding, simplicity first, surgical changes, and goal-driven execution.
- Typical failure modes include silent assumptions, overengineering, unrelated edits, and declaring completion without verifiable success criteria.

MSTR adoption:
- Convert these from prompt advice into measurable SFT/preference/RL behaviors: minimal diffs, assumption handling, verifier use, no drive-by refactors, and stop-after-success.

### 7. SWE-agent / mini-SWE-agent

Sources:
- https://swe-agent.com/latest/background/aci/
- https://mini-swe-agent.com/latest/
- https://mini-swe-agent.com/latest/faq/

Relevant observations:
- SWE-agent demonstrates that the agent-computer interface materially affects software-task success.
- mini-SWE-agent intentionally keeps the scaffold very small, making it attractive as a neutral baseline and reducing the risk that model training overfits a complicated orchestration layer.

MSTR adoption:
- Maintain a neutral minimal harness arm.
- Tournament richer typed MSTR/WePLD harnesses against the neutral arm.
- Do not make scaffold complexity the hidden source of the headline model score.

### 8. SWE-Gym / executable software training

Source:
- https://proceedings.mlr.press/v267/pan25g.html

Relevant observation:
- Executable software environments and verifiable repository tasks can provide high-value training signal for software-engineering agents.

MSTR adoption:
- Environment/verifier quality is a prerequisite to agent training, not merely a later RL optimization.

### 9. Qwen3-Coder-Next direction

Source:
- https://qwen.ai/blog

Relevant public direction:
- Modern coding-model work increasingly emphasizes verifiable coding tasks, executable environments, environment interaction, and agentic training signals in addition to raw code pretraining.

MSTR adoption:
- Keep code/FIM knowledge strong, then specialize behavior through executable, verifier-grounded trajectories.

### 10. Function-/Instruction-Aware FIM and Repository Context

Research references:
- Function-Aware Fill-in-the-Middle: https://arxiv.org/abs/2607.12463
- Instruction-Aware FIM: https://arxiv.org/abs/2509.24637
- Repoformer / selective retrieval: https://arxiv.org/abs/2403.10059

MSTR adoption:
- Future MSTR-001 should tournament ordinary FIM, instruction-aware FIM, function/dependency-aware FIM, and cross-file/repository FIM.
- Add an experimental action/observation continuation objective only as a measured arm, not a preselected truth.
- Teach/select `NO_RETRIEVAL` and minimal-context-first behavior.

### 11. Whole-program / long-horizon evaluation

References:
- ProgramBench: https://programbench.com/
- Terminal-Bench 2: https://arxiv.org/abs/2601.11868
- Multi-SWE-bench: https://arxiv.org/abs/2504.02605

MSTR adoption:
- Public patch benchmarks remain continuity evidence.
- The private/fresh MSTR Direction-to-Done Gauntlet must include build/new-feature and multi-file tasks, environment/tool work, and WePLD-spec-driven work.

### 12. Internal Half Moon source — WePLD

Canonical repository:
- `TheHalfMoon/wepld`
- Harness research/package includes explicit `ContextPolicy`, `ToolSurfacePolicy`, `PlanningPolicy`, `VerifierCadencePolicy`, `RecoveryPolicy`, `StopPolicy`, evidence finalization, effect envelopes, and recipe decision traces.

MSTR adoption:
- Define a WePLD-native adapter rather than inventing a disconnected second orchestration universe.
- Allow WePLD to consume an MSTR capability profile and select the smallest sufficient recipe.
- Preserve neutral-harness comparability so WePLD system gains are not mislabeled as raw model gains.

---

## Architecture Conclusions

### Three Loops

```text
BUILD LOOP
Direction -> bounded state graph -> independent verification -> recovery/stop

ENVIRONMENT LOOP
Checkout -> Discover health targets -> Setup -> Reset -> Independent verify -> Admit/reject

RESEARCH LOOP
Baseline -> Hypothesis -> Bounded mutation -> Run -> Evaluate -> Keep/discard/crash/invalid -> Repeat
```

The loops share typed identities/evidence but have different authority surfaces.

### Default Agent Topology

```text
ONE MSTR BUILDER
+
DETERMINISTIC/INDEPENDENT VERIFIER
```

Optional planner/checker/subagent arms must earn their extra token/RAM/latency cost.

### Corrected Pre-Training Sequence

```text
+--------------------------+   +--------------------------+   +--------------------------+
| MSTR-000                 |   | MSTR-000A EARLY_SAFE    |   | MSTR-000B EARLY_SAFE    |
| candidate Q4/runtime     |   | A001-A018 loop/harness  |   | governance/data/contracts|
+------------+-------------+   +------------+-------------+   +------------+-------------+
             |                              |                              |
             +------------------------------+------------------------------+
                                            |
                                            v
stable/equivalent product-aligned candidate pool
+ loop/verifier/data/curriculum prerequisites
                                            |
                                            v
A019-A024 cross-harness / Direction-to-Done convergence
                                            |
                                            v
separate founder weight-changing training gate
                                            |
                                            v
code/FIM continued training where evidence justifies
-> export + identity-bound Q4 qualification
-> only PROMOTED checkpoint may parent execution-grounded SFT
-> export + identity-bound Q4 qualification
-> only PROMOTED checkpoint may parent preference/recovery training
-> export + identity-bound Q4 qualification
-> only PROMOTED checkpoint may parent bounded executable agent RL
-> export + identity-bound Q4 qualification
-> same raw / neutral / MSTR / WePLD evaluation surfaces
```

The exact number/order of material stages is governed by later specs, but the invariant is fixed: **no material checkpoint becomes a later-stage parent without a successful `Q4PromotionRecord` binding source/merged/Q4 hashes, export and quantizer revisions/recipes, integrity, required regression, and applicable universal-laptop gates.**

## Open Research Questions for Implementation

These are evidence questions, not planning blockers:
- Minimal event vocabulary that preserves complete replay without unnecessary log bloat.
- Best compact `AgentState` projection for an 8K model.
- Whether anchored patch, search/replace, unified diff, or another edit grammar wins after training.
- Whether a learned verifier adds enough value over deterministic verifiers to justify runtime/training cost.
- Which environment isolation substrate is smallest and safest for the MVP.
- How much WePLD guidance helps MSTR without reducing standalone/general harness robustness.
- Which FIM/data mixture most improves agentic coding per token for the selected product-aligned backbone.
