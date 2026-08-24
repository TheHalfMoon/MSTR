# MSTR Constitution

<!--
Sync Impact Report
- Version: 1.0.0
- Ratified: 2026-08-24
- Scope: First formal Spec Kit constitution for MSTR.
- Governs: all specifications, plans, tasks, implementation, experiments, training, evaluation, releases, and claims.
-->

MSTR is an independent, open-weight, local-first software-engineering model and runtime project. The primary product exists to deliver the highest practical verified software-engineering utility possible on ordinary laptops while remaining reproducible, distributable, private by default, and scientifically defensible.

## Core Principles

### I. Universal Laptop Is the Primary Product

The primary MSTR release MUST remain useful on ordinary contemporary laptops without a discrete GPU.

The reference qualification tier is:

```text
TOTAL_RAM = 8_GB
CPU_ONLY = REQUIRED
REFERENCE_CONTEXT = 8K
PRIMARY_Q4_ARTIFACT_TARGET <= 3_GB
WHOLE_LAPTOP_USABILITY = REQUIRED
```

Optional larger or accelerated editions MAY exist, but they MUST NOT silently redefine the primary product. Any change to the universal-laptop floor requires measured evidence, an explicit specification amendment, and founder approval.

### II. Local, Accountless, Offline, and Private by Default

The primary MSTR release MUST provide at least one official acquisition path that does not require a provider account or gated model-access acceptance, provided redistribution rights permit it.

After required artifacts are local:

- no provider account, API key, subscription, or activation server may be required;
- basic coding assistance MUST work without a network connection;
- remote-model fallback is prohibited by default;
- telemetry and outbound network access MUST be off by default;
- user repository contents MUST NOT be uploaded or used for training by default;
- basic launch MUST NOT require Docker, Python, Node.js, or building MSTR from source.

Optional networked features require explicit user opt-in and clear data-flow disclosure.

### III. Evidence Before Selection, Claims, or Scale

No model, runtime, retriever, quantization, training recipe, or benchmark result becomes project truth because it is popular, vendor-reported, or produced by an agent.

```text
MODEL_OUTPUT != PROJECT_AUTHORITY
BENCHMARK_SCORE != BACKBONE_SELECTION
PUBLIC_LEADERBOARD != MSTR_TRUTH
HARNESS_GAIN != MODEL_GAIN
```

Material decisions MUST be bound to exact evidence identities: source revision, artifact hash, tokenizer, quantizer, runtime build, hardware, context/cache settings, interaction-contract version, task manifest, seed, and cost where applicable.

MSTR MUST report raw model, neutral-harness, and full-system results separately.

### IV. Rights and Provenance Fail Closed

Any primary backbone MUST permit the intended MSTR use and distribution chain, including personal and commercial use, modification/fine-tuning, quantization/conversion, and redistribution of derivative artifacts.

Dataset, teacher/API-output, runtime, quantizer, and other dependency rights MUST be evaluated independently. A permissive backbone does not make the whole pipeline permissive.

Ambiguous, research-only, non-commercial-only, field-restricted, scale-restricted, or redistribution-incompatible components MUST fail closed for primary-product admission until the ambiguity or restriction is resolved.

### V. Freeze Coupled Contracts Before Expensive Training

MSTR MUST not begin expensive long-horizon training while the serving/training interface is still fluid.

Before agent SFT/RL at material scale, the project MUST version and freeze the coupled Interaction Contract covering at minimum:

- tokenizer/backbone family;
- prompt/chat template and stable prefix layout;
- FIM control semantics;
- tool-call grammar;
- tool-result serialization;
- edit grammar and stale-write behavior;
- task-state/context ordering;
- privacy/network semantics visible to the model;
- baseline serving/cache semantics.

A material post-freeze change requires migration evidence and regression testing.

### VI. TTVC and Verified Utility Are the Product Metrics

Raw tokens/second is not the north star.

```text
NORTH_STAR_SPEED = TTVC
TTVC = TIME_TO_VERIFIED_COMPLETION
```

MSTR MUST optimize and report end-to-end verified software-engineering utility: solve rate, TTVC, first correct edit, laptop responsiveness, memory pressure, sustained thermal behavior, and artifact/install burden.

Faster decoding that worsens verified completion, reliability, or whole-laptop usability is not a product improvement.

### VII. Smallest Sufficient Architecture Wins

Every runtime component consumes latency, RAM, disk, complexity, maintenance, and attack surface.

The default MSTR runtime MUST begin with the smallest sufficient architecture. Heavy graph databases, vector systems, subagent swarms, learned apply models, cloud dependencies, or other complex components may enter only through comparative evidence showing enough verified solve-rate/TTVC value to justify their cost.

The default shipped system MUST be on the measured Pareto frontier for quality, latency, RAM, disk, and operational complexity.

### VIII. Evaluation Integrity Is a First-Class Feature

Training contamination and runtime answer leakage are separate hazards and MUST be controlled separately.

Public benchmarks are supporting evidence only. MSTR MUST maintain a private/fresh evaluation surface before major training decisions and release claims.

Benchmark runs MUST prevent future-git-history retrieval, public-solution lookup, hidden evaluator tampering, and other answer-leakage channels.

Verifier design MUST include adversarial reward-shortcut testing such as deleting tests, weakening assertions, hardcoding outputs, modifying evaluators, reading future fixes, recovering cached solutions, or spoofing command output.

### IX. Reproducibility and Failure Evidence Are Mandatory

Failed experiments, timeouts, OOMs, verifier failures, and negative findings are evidence and MUST NOT be silently discarded.

Every material experiment MUST be reproducible from a versioned manifest. Any excluded/invalid run requires a pre-recorded or clearly auditable invalidation reason.

Performance comparisons MUST match cache states, verifier requirements, context, hardware class, timeouts, and seeds.

### X. Bounded Authority and Exact-Head Governance

GitHub `main` is canonical. Branches, PRs, local experiments, consultations, and model outputs are evidence candidates until merged through the governed workflow.

Actions with meaningful external effect—model-weight acquisition, paid API use, rented compute, large data ingestion, long training, large-scale RL, or release publication—MUST be explicitly authorized by a canonical task with a stated scope and cost/resource ceiling when relevant.

No generic continuation instruction silently expands a narrower canonical authority boundary.

## Engineering and Program Rules

### Spec-Driven Development

Every buildable MSTR workstream MUST follow the Spec Kit lifecycle:

```text
constitution
-> specification
-> clarification closeout
-> research
-> plan
-> data model / contracts / quickstart
-> tasks
-> analyze/review
-> implement
-> converge/closeout
```

The active specification is authoritative for scope; the plan is authoritative for technical execution; `tasks.md` is the executable work queue.

### Testing

Code that implements a contract MUST include automated tests for that contract.

Evidence-producing code MUST test serialization stability, identity completeness, error/failure paths, and deterministic behavior where the protocol requires it.

Runtime security, stale-write protection, offline behavior, and evaluator-integrity boundaries require explicit tests rather than prose-only assertions.

### Simplicity and Dependencies

New dependencies MUST have a documented reason. A dependency that is optional for one experiment MUST NOT become a mandatory end-user dependency unless separately admitted.

The primary user-facing runtime should favor self-contained, portable binaries and stable file formats.

### Training and Model Development

Long training, large corpus ingestion, and large-scale RL remain blocked until the governing spec explicitly authorizes them.

FIM/code-completion capability, tool reliability, and quantized behavior MUST be regression-tested through post-training. The project MUST not optimize agentic behavior by silently destroying core coding capability.

## Governance

This constitution supersedes ad-hoc convention when they conflict.

- **Authority:** MUST-level principles are blocking gates for plans, tasks, PRs, experiments, and release claims.
- **Constitution Check:** every `plan.md` MUST include an explicit Constitution Check before implementation begins and re-check it after design artifacts are complete.
- **Amendments:** changing a MUST principle requires a dedicated PR, rationale, impact analysis, and semantic version bump.
- **Versioning:** MAJOR = incompatible governance change or removed/redefined principle; MINOR = new principle or materially expanded mandatory policy; PATCH = non-semantic clarification.
- **Compliance:** unresolved constitution conflicts block implementation or merge.
- **Founder gates:** where a task explicitly requires founder acceptance, that acceptance is a project gate and cannot be inferred from unrelated activity.

Version: 1.0.0 | Ratified: 2026-08-24 | Last Amended: 2026-08-24
