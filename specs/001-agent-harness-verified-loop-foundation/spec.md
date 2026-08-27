# Feature Specification: MSTR-000A Verified Agent Harness + Direction-to-Done Foundation

**Feature Branch:** `docs/001-agent-harness-verified-loop-foundation`  
**Created:** 2026-08-26  
**Status:** CANONICAL FOUNDATION / implementation may proceed under exact early-safe dependencies; convergence is MSTR-000B gated  
**Input:** Reframe MSTR around the smallest code-specialized model that can turn a terse software direction into verified working software, while preserving the universal-laptop product envelope and preventing harness-only gains from being misreported as model gains.

> MSTR-000A is an interposed pre-training workstream. It does not replace existing MSTR-000 candidate qualification. Model-independent A001-A018 work may proceed when exact prerequisites are satisfied and no unauthorized candidate/external-effect input is consumed. Candidate-dependent A019-A024 convergence requires equivalent candidate qualification and the MSTR-000B stable-candidate/verifier/research prerequisites. MSTR-000A grants no weight-changing training authority.

## Product Thesis

MSTR is not optimized to be a general-purpose assistant. Its primary job is software construction.

```text
PRIMARY_PURPOSE = TURN_SOFTWARE_DIRECTION_INTO_VERIFIED_WORKING_CODE
PRIMARY_QUALITY_METRIC = DIRECTION_TO_VERIFIED_COMPLETION_RATE
PRIMARY_SPEED_METRIC = TTVC
PRIMARY_DEPLOYMENT = UNIVERSAL_LAPTOP
REFERENCE_RAM = 8_GB
REFERENCE_CONTEXT = 8K
CPU_ONLY_BASIC_OPERATION = REQUIRED
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
```

General reasoning is retained only insofar as it materially improves software engineering, planning, debugging, and safe execution.

## Sequence Semantics

The original blanket rule that MSTR-000A starts only after T034 is superseded by exact dependency classes:

```text
EARLY_SAFE = A001-A018
  may proceed when exact prerequisites are satisfied,
  the task is model-independent,
  and no unqualified candidate result/external authority is consumed

CONVERGENCE = A019-A024
  requires equivalent/stable candidate qualification
  + MSTR-000B required candidate/verifier/research outputs
```

Existing MSTR-000 T030-T034 work continues according to live canonical state and is neither reopened nor blocked by this specification.

## User Scenarios & Testing

### User Story 1 — Developer Gives Direction, MSTR Finishes the Work (P1)

A developer can give a short software direction rather than a fully decomposed implementation script. MSTR must orient to the repository, infer or surface acceptance criteria, localize relevant code, plan only as much as the task warrants, edit surgically, execute tools, verify outcomes, repair failures, and stop only when the work is mechanically verified or a real escalation condition is reached.

**Independent test:** Run fresh direction-to-done tasks where the initial prompt is intentionally terse and the completion condition is hidden from the model but available to an independent verifier.

**Acceptance scenarios:**
1. Given a clear direction with a runnable repository, MSTR completes the required change and the independent verifier passes.
2. Given an ambiguity whose interpretations materially change behavior, MSTR surfaces the ambiguity or uses explicitly authorized bounded inference rather than silently inventing requirements.
3. Given a failed build/test/typecheck after an edit, MSTR diagnoses and repairs within the bounded recovery budget.
4. Given all required verifiers pass, MSTR stops without speculative extra refactoring.
5. Given no valid path to completion within authority/budget, MSTR escalates with evidence rather than claiming success.
6. Given a trivial task, MSTR may use a fast path and must not be forced through unnecessary planning/retrieval states.

### User Story 2 — Harness Engineer Can Swap the Loop Without Rewriting the Model Interface (P1)

The model-facing interaction, tool, state, verifier, and stop contracts are versioned separately from any concrete harness implementation. A neutral minimal harness, MSTR-native harness, and WePLD-native harness adapter can execute equivalent tasks under comparable conditions.

**Independent test:** Replay the same eligible task through at least two harness arms with identical model, sampling, verifier, timeout, and artifact identity, and produce separate comparable score surfaces.

**Acceptance scenarios:**
1. Harness-only gains are labeled harness gains, not model gains.
2. The agent loop is replaceable behind a stable contract.
3. All model-visible facts are reconstructable from an append-oriented event log.
4. A task success verdict cannot be authored by the same model turn that proposed the solution.
5. Candidate-dependent comparisons use the MSTR-000B stable product-aligned candidate pool or an explicit governed supersession.

### User Story 3 — Training Engineer Gets Executable, High-Signal Trajectories Before Weight Changes (P1)

Before material SFT/RL, the project can produce training-ready software trajectories from admitted executable environments with exact repo state, goal, model-visible observations, actions, tool results, edits, verifier outcomes, recovery events, and terminal result.

**Independent test:** Serialize and deterministically replay one successful and one failed/recovered trajectory from immutable manifests without relying on chat history.

**Acceptance scenarios:**
1. Successful trajectories contain independent verifier proof.
2. Failed trajectories remain first-class evidence and are not silently dropped.
3. Invalid tool calls, bad edits, timeouts, verifier failures, and recovery attempts remain visible.
4. Training trajectory acceptance can reject contaminated, unverifiable, leaked, malformed, or authority-violating runs.
5. Clean training admission consumes the verifier-health state required by MSTR-000B.

### User Story 4 — Environment Engineer Can Admit Runnable Repositories Before Training (P1)

The project can convert an eligible repository checkout into a reproducibly runnable task environment before using it for SFT/RL, so training compute is not wasted debugging broken setup.

**Independent test:** From a clean checkout, produce a bounded setup recipe, rebuild/reset the environment, prove selected health commands, prove no-op/broken-state failure where relevant, and bind the result to exact repo/environment identities.

**Acceptance scenarios:**
1. A setup agent cannot declare its own environment valid; an independent verifier checks the target commands.
2. Repeated setup failure beyond the configured attempt ceiling rejects the environment.
3. The setup recipe is replayable from a clean state.
4. Network, secrets, mounts, and dependency effects remain bounded by explicit policy.

### User Story 5 — Researcher Can Improve MSTR With Bounded Keep/Discard Experiments (P1)

The project can run autonomous or semi-autonomous research loops in which evaluation, budgets, and product constraints are frozen while one bounded experimental surface changes at a time. A result is kept only when it improves the predeclared multi-objective score without unacceptable regression.

**Independent test:** Run a baseline plus candidate experiments and reproduce keep/discard/crash/invalid decisions from the experiment ledger using the MSTR-000B multi-fidelity research ladder.

**Acceptance scenarios:**
1. The research agent cannot edit the evaluation harness or hidden acceptance criteria.
2. Every run has a fixed budget and exact code/config identity.
3. Negative experiments and crashes remain in the ledger.
4. Simpler equal-performing variants are preferred over unnecessary complexity.
5. Weak experiments can be discarded before expensive Direction-to-Done/Q4 laptop evaluation.

### User Story 6 — WePLD Can Use MSTR as Its Native Small Builder (P1)

WePLD can drive MSTR through a bounded adapter that maps WePLD task/spec state into the same MSTR loop contract without granting WePLD-only results to the raw model score.

**Independent test:** Run the same eligible task through neutral and WePLD-native harness arms and regenerate raw/neutral/full-system reporting.

**Acceptance scenarios:**
1. WePLD may improve context, planning, verification cadence, and recovery, but those gains remain a separate full-system surface.
2. MSTR exposes a capability profile that WePLD can use to choose the smallest suitable recipe.
3. MSTR remains usable without WePLD as a standalone local code model/runtime.

## Functional Requirements

### Direction-to-Done and Loop

- **FR-A001:** MSTR-000A MUST define and version `MSTR-BUILD-LOOP-v0` as a bounded state graph containing at least ORIENT, GOAL, LOCALIZE, PLAN, ACT, OBSERVE, VERIFY, RECOVER, and STOP semantics.
- **FR-A002:** STOP success MUST require independent verifier evidence; a model-authored `done` statement is not sufficient.
- **FR-A003:** The loop MUST expose bounded step/tool/repair/time budgets and explicit escalation conditions.
- **FR-A004:** The loop MUST support trivial-task fast paths without forcing heavyweight planning/retrieval for obvious edits.
- **FR-A005:** The loop MUST encode simplicity-first and surgical-change behavior as measurable outcomes, not prompt-only advice.

### Event Log, State, and Replay

- **FR-A006:** Every model-visible input, model output, tool call/result, edit/apply result, verifier observation, recovery action, state compaction, and terminal verdict MUST be represented by a typed append-oriented event.
- **FR-A007:** Model history MUST be derivable from durable events rather than maintained as a separate untraceable authority surface.
- **FR-A008:** `AgentState` MUST include goal, acceptance criteria, constraints, plan, inspected context, changed files, command/verifier history, known failures, remaining work, and next action where applicable.
- **FR-A009:** State compaction MUST preserve decision-relevant facts and MUST NOT silently convert uncertain observations into facts.

### Harness Tournament and Train/Serve Consistency

- **FR-A010:** MSTR-000A MUST implement/define at least a neutral-minimal harness arm, an MSTR-native typed harness arm, and a WePLD-native adapter arm.
- **FR-A011:** The same model-facing loop/tool/edit/result semantics selected for training MUST be available in serving/evaluation, or a migration contract with regression evidence is required.
- **FR-A012:** Harness comparisons MUST pin model/artifact, interaction/loop version, task, verifier + verifier-health identity, sampling, timeout, cache, and hardware class.
- **FR-A013:** Harness gains MUST remain separately reported from raw model gains.

### Environment and Verifier Factory

- **FR-A014:** Runnable environment admission MUST precede use of an environment for agent training.
- **FR-A015:** Environment setup MUST be verified from a fresh/reset state by an independent checker and bounded attempt count.
- **FR-A016:** Verifiers MUST prove known-good pass and known-bad/no-op fail where the task supports those checks.
- **FR-A017:** Reward-shortcut testing MUST cover evaluator/test tamper, assertion weakening, hardcoding, spoofing, cached/future solution leakage, and prohibited network paths.
- **FR-A018:** Environment and verifier identities MUST be immutable inputs to training/evaluation manifests.

### Direction-to-Done Evaluation

- **FR-A019:** MSTR MUST maintain a private/fresh `Direction-to-Done` task surface whose prompts resemble realistic terse software directions, including feature building and multi-file construction rather than only issue patches.
- **FR-A020:** The primary quality metric MUST be DVCR, paired with TTVC and failure-inclusive reporting.
- **FR-A021:** Additional mandatory diagnostics MUST include first-pass accept rate, edit-survival rate, repair success rate, tool-error rate, tokens/tool calls per verified completion, and Q4 regression where applicable. Repository Health Delta is added for long-horizon claims by MSTR-000B.
- **FR-A022:** Public benchmarks remain continuity/supporting evidence and MUST NOT be the sole release or training-selection authority.

### Trajectory Factory

- **FR-A023:** Training trajectories MUST preserve success and failure, exact event ordering, verifier identity/health, repo/environment identity, and authority/effect boundaries.
- **FR-A024:** The project MUST define an explicit failure taxonomy including wrong localization, bad assumption, stale edit, syntax/type/build/test failure, dependency/tool failure, timeout, incomplete implementation, over-edit, regression, and fake completion.
- **FR-A025:** Successful SFT candidates MUST be independently verified and satisfy downstream verifier-health/admission requirements; preference/recovery data MAY use failed attempts when provenance and labels are explicit.
- **FR-A026:** No private user repository trace becomes training data by default. Future production trace learning requires explicit opt-in and separate policy.

### Context and Retrieval

- **FR-A027:** The harness MUST support explicit no-extra-context behavior so retrieval is selective rather than mandatory.
- **FR-A028:** Context policy MUST prefer the smallest relevant slice first and expand only when evidence requires it. MSTR-000B may add typed context intents such as `NEED_FILE`/`NEED_SYMBOL`/`NO_MORE_CONTEXT` through the frozen interaction contract.
- **FR-A029:** Context compaction/retrieval quality MUST be evaluated by verified completion and TTVC, not retrieval recall alone.

### Autoresearch

- **FR-A030:** MSTR-000A MUST define `MSTR-RESEARCH-LOOP-v0`: BASELINE -> HYPOTHESIS -> BOUNDED MUTATION -> RUN -> EVALUATE -> KEEP/DISCARD/CRASH/INVALID -> NEXT.
- **FR-A031:** Evaluation code, hidden task answers, verifier policy, product/rights/contamination constraints, and resource ceilings MUST be immutable during one research campaign.
- **FR-A032:** Research decisions MUST use a declared multi-objective score with DVCR primary and reject regressions that violate universal-laptop, rights, security, verifier-health, or Q4 gates.
- **FR-A033:** The research loop MAY tune training/data/harness parameters later, but MSTR-000A itself grants no weight-changing training authority.

### Sequence and Convergence Gate

- **FR-A034:** Existing MSTR-000 candidate/Q4/runtime qualification tasks continue according to live canonical state and are not reopened or blocked by model-independent MSTR-000A work.
- **FR-A035:** A001-A018 MAY execute before T034 only when their exact dependencies are satisfied, they consume no unqualified candidate result, and they require no unauthorized external effect.
- **FR-A036:** A019-A024 MUST NOT execute as convergence/headline evidence until equivalent candidate qualification and the exact MSTR-000B stable-candidate, verifier-health, and research-ladder prerequisites are canonical.
- **FR-A037:** Existing later interaction/environment/verifier/tournament tasks MUST be reconciled against MSTR-000A + MSTR-000B to avoid duplicate or contradictory implementation.
- **FR-A038:** MSTR-001/MSTR-002/MSTR-003 MUST consume MSTR-000A event/environment/verifier/harness/trajectory contracts and the relevant MSTR-000B data/curriculum/verifier-health/Q4 contracts rather than redefine incompatible ones.
- **FR-A039:** Any weight-changing adaptation/training gate, including T053 or a canonical successor, remains separately founder-authorized after all convergence prerequisites close.

## Success Metrics

```text
DVCR = verified successful eligible direction tasks / all eligible direction attempts
TTVC = time from admitted direction to independent verified completion
FPAR = tasks completing with the first implementation attempt accepted by verifier
ESR = proposed edit content surviving through final verified solution
RSR = failed-attempt recoveries that reach verified success within the repair budget
TER = invalid/failed tool actions / all tool actions
TVC = tokens or tool calls per verified completion
```

DVCR and TTVC MUST always be reported together. A fast failed task is not a successful TTVC result.

## Non-Goals

MSTR-000A does NOT:
- train or modify model weights;
- select the final MSTR backbone;
- make WePLD mandatory for standalone MSTR;
- adopt research donors as dependencies by default;
- enable hidden telemetry or production-trace training;
- introduce default multi-agent swarms;
- weaken the 8 GB / CPU / 8K / Q4 <= 3 GB primary product envelope;
- authorize new model weight access, paid APIs, paid Colab, rented GPUs, large dataset ingest, long training, or large-scale RL.

## Exit Gate

MSTR-000A closes only when repository evidence proves:

```text
BUILD_LOOP_V0 = FROZEN
LOOP_CONTRACT = FROZEN
EVENT_LOG_REPLAY = PASS
AGENT_STATE_COMPACTION = QUALIFIED
NEUTRAL_HARNESS = QUALIFIED
MSTR_NATIVE_HARNESS = QUALIFIED
WEPLD_ADAPTER = QUALIFIED_OR_EXPLICITLY_DEFERRED_WITH_REASON
ENVIRONMENT_ADMISSION_MVP = PASS
VERIFIER_MVP = PASS
DIRECTION_TO_DONE_V0 = FROZEN_PRIVATE/FRESH
TRAJECTORY_CONTRACT = TRAINING_READY
FAILURE_TAXONOMY = FROZEN
RESEARCH_LOOP_V0 = QUALIFIED_USING_MSTR_000B_LADDER
HARNESS_GAIN_SEPARATION = PASS
MSTR_000B_CONVERGENCE = SATISFIED_OR_EXPLICITLY_RECONCILED
TRAINING_GATE_SEQUENCE = RECONCILED
WEIGHT_CHANGING_TRAINING = STILL_SEPARATELY_GATED
```
