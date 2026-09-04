# Research Addendum — 2026-09-04 Frontier Update

**Workstream:** MSTR-000B
**Research status:** planning evidence only
**Execution authority created:** NONE
**Question:** What newly available model/training/quantization/agent-runtime evidence materially changes the pre-training plan before MSTR freezes its stable product-aligned candidate pool?

## 1. Scope and Method

This addendum supplements, but does not rewrite, `research.md` dated 2026-08-27.

Research priority was given to primary/public sources from model/tool authors and a peer-reviewed paper. Vendor benchmark and speed claims are treated as research hypotheses until reproduced under MSTR identity, hardware, evaluator, and leakage controls.

No external model, dataset, quantizer, dependency, training method, or benchmark is admitted by citation alone.

## 2. IFM K2 Horizon

Sources:

- `https://ifm.ai/k2/`
- `https://ifm.ai/blog/k2`
- `https://huggingface.co/collections/IFM/k2-horizon`

### Observations

IFM released a connected family spanning compact dense models and larger dense/sparse models, including 0.9B, 3.7B, and 7B compact variants. Public lifecycle material includes model artifacts and unusually broad training/research disclosures, including intermediate checkpoints and recipe/data material.

The release is material to MSTR because:

1. it post-dates the canonical B005/B010 scan envelope;
2. K2 Horizon 3.7B occupies approximately the size band MSTR is actively investigating for the universal-laptop primary model;
3. the family exposes checkpoint lineage that can support a future controlled substrate comparison instead of assuming the final post-trained checkpoint is the best continued-training parent;
4. IFM's own public discussion of coding-evaluation reward hacking reinforces MSTR's existing requirement for fresh/private and leakage-controlled evaluation.

### Decision

`K2 Horizon 3.7B = MANDATORY_FRONTIER_REVIEW_INPUT`, not admitted candidate.

`K2 Horizon 7B = STRETCH_LOW_BIT_UPPER_BOUND_REVIEW`, not primary candidate by size alone.

`K2 Horizon 0.9B = TINY_MODEL / DRAFT / EFFORT_CONTROL_RESEARCH_INPUT`.

K2 MoVA variants are architecture/sparse-activation references unless total-weight storage/RAM evidence can satisfy the universal-laptop product envelope.

Any weight access requires a new exact canonical envelope and separate Founder authority unless later canonical evidence proves the artifact is already covered by an existing exact authority, which is not currently claimed.

## 3. K2 Uno / Parallel Generation

Source:

- K2 Horizon public model/research surfaces linked from the K2 release and collection.

### Observation

Uno explores a conditional adapter / alternative generation path intended to improve generation speed while retaining an autoregressive base.

### Decision

Treat Uno-style parallel generation as an MSTR-004 research arm alongside ordinary autoregressive decoding and speculative decoding. Do not interpret vendor throughput as MSTR TTVC evidence. MSTR must reproduce any gain with batch-1 coding workloads, tool interruptions, exact runtime identity, CPU/laptop hardware, context/cache parity, and independent verification.

## 4. Sherry — 1.25-bit Structured Ternary Quantization

Primary source:

- `https://aclanthology.org/2026.acl-long.513/`

### Observations

Sherry uses structured ternary weights with 3:4 fine-grained sparsity and a packing scheme equivalent to 1.25 bits per weight. The paper also introduces a training mechanism to address representation-collapse/weight-trapping behavior rather than describing the method as a trivial post-hoc format conversion.

The paper reports a 1B-model CPU experiment with bit savings and a speed gain relative to its chosen ternary baseline. Those reported values are research evidence, not MSTR claims.

### Decision

Change MSTR's optimization framing from:

```text
Q4 = END OF QUANTIZATION SEARCH
```

to:

```text
Q4 = MANDATORY QUALITY / PRODUCT ANCHOR
SUB_Q4 = EVIDENCE-GATED CHALLENGER RESEARCH
```

Potential later arms include Q3, Q2, and structured-ternary/Sherry-class methods.

If a low-bit method requires QAT, sparse training, recovery training, distillation, or any other weight change, it is a governed weight-changing stage and must satisfy exact training authority plus ordinary checkpoint/Q4 promotion rules.

## 5. Tencent AngelSlim / Hy4

Primary source:

- `https://github.com/Tencent/AngelSlim`

### Observations

AngelSlim provides current research/engineering evidence around extreme compression, structured low-bit execution, speculative decoding, and large-model deployment. Hy4-scale artifacts and distributed deployment demonstrations are far outside MSTR's primary 8 GB laptop envelope.

### Decision

Do not consider Hy4 a primary MSTR backbone.

Use AngelSlim as a future source of method candidates for:

- low-bit quantization;
- CPU/runtime kernels where architecture-compatible;
- speculative decoding;
- compression-aware deployment.

Every claim must be remeasured under MSTR's hardware/runtime/evaluation identity. Optional distributed execution may be studied later but may never become a primary-release requirement without a separate product amendment.

## 6. Cursor Composer 2 / Composer 2.5

Primary sources:

- `https://prod.cursor.com/blog/composer-2-technical-report`
- `https://cursor.com/blog/composer-2-5`
- `https://cursor.com/blog/bootstrapping-composer-with-autoinstall`
- `https://cursor.com/blog/continually-improving-agent-harness`
- `https://prod.cursor.com/blog/how-cursor-router-works`
- `https://prod.cursor.com/blog/reward-hacking-coding-benchmarks`

### Composer 3 verification boundary

No official Cursor Composer 3 release/specification was verified for this research snapshot as of 2026-09-04. Community references are not used as technical authority. The addendum therefore relies only on official Composer 2/2.5 and Cursor engineering material.

### Observations

The official Composer material reinforces several MSTR theses:

1. code-focused continued pretraining before large agent RL can materially improve the later agent-training substrate;
2. realistic executable train/serve environments reduce scaffold mismatch;
3. very long trajectories create credit-assignment problems for terminal reward alone;
4. targeted textual feedback at a specific problematic action is a plausible measured training arm;
5. synthetic task/environment scaling must be paired with shortcut/reward-hacking controls;
6. a previous model generation can help bootstrap future runnable environments when independent admission remains authoritative;
7. dynamic routing/effort allocation can reduce unnecessary compute, but MSTR should adapt this to local same-model FAST/NORMAL/DEEP effort rather than a cloud multi-provider dependency;
8. public coding benchmarks can be contaminated by future Git history, public solution retrieval, cached fixes, or evaluator exploitation.

### Decision

Carry the following into B032's downstream contract amendment when B032 becomes eligible:

- MSTR-003 production-compatible executable RL;
- targeted trajectory feedback as a measured arm;
- dynamic synthetic environment/task generation;
- previous-MSTR environment bootstrap with independent admission;
- explicit reward-shortcut batteries;
- same-model adaptive effort control;
- sealed headline evaluation requirements for MSTR-006.

## 7. MSTR-Specific Synthesis

The frontier evidence does not justify copying any one external system.

The strongest MSTR direction is the intersection:

```text
K2:
  compact-model + checkpoint-lifecycle + synthetic/agentic training evidence

Composer:
  code prior + production-compatible executable RL + targeted feedback + harness discipline

Sherry / AngelSlim:
  extreme low-bit + kernel/runtime co-design

MSTR:
  8 GB CPU-only product envelope
  + DVCR / TTVC
  + independent verifier
  + software-evolution data
  + student-frontier curriculum
  + fresh/private Direction-to-Done
  + fail-closed authority/governance
```

## 8. New Planning Gaps

### P0 — Before candidate-pool freeze

1. frontier freshness snapshot at B013 entry;
2. explicit disposition for material post-B010 model releases;
3. fail closed if a plausible primary-product challenger has not received equivalent qualification or an evidence-backed rejection;
4. do not silently reopen historical tasks—create a separately governed refresh amendment when required.

### P1 — Before material training

5. checkpoint-lineage substrate comparison when upstream exposes compatible base/intermediate/final checkpoints;
6. early low-bit compatibility awareness in finalist selection;
7. preserve mandatory Q4 promotion even if sub-Q4 research is planned.

### P1 — Agent training

8. targeted trajectory-feedback research arm;
9. dynamic synthetic environment generation with independent admission;
10. previous-MSTR autoinstall/bootstrap research arm;
11. explicit anti-shortcut environment sanitation.

### P1 — Local speed

12. FAST/NORMAL/DEEP effort controller;
13. speculative/parallel generation tournament where runtime-compatible;
14. Q4/Q3/Q2/structured-ternary tournament with exact hardware/runtime identity;
15. TTVC remains primary speed evidence.

### P0 — Release claims

16. sealed public-derived evaluation;
17. future Git history isolation;
18. public-solution/network controls;
19. protected evaluator/answer surfaces;
20. negative-evidence preservation and headline correction after detected leakage.

## 9. Research Conclusion

The 2026-08-27 MSTR-000B strategy remains structurally sound. The frontier update requires three material amendments:

```text
1. B013 FRONTIER FRESHNESS GATE
2. Q4 ANCHOR + EVIDENCE-GATED EXTREME LOW-BIT RESEARCH
3. DOWNSTREAM EXECUTABLE-RL / TARGETED-FEEDBACK / SEALED-EVAL REQUIREMENTS
```

These changes strengthen MSTR without raising the product floor, preselecting a model, or granting any new external-effect authority.
