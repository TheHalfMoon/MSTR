# MSTR-000 Research Reconciliation

## Decision context

The founder clarified that the primary MSTR model must be installable and usable by people on ordinary laptops. That constraint materially changes the preconstruction search space: larger models may remain useful as teachers or optional editions, but the primary tournament must first test compact foundations that can plausibly satisfy an 8 GB, CPU-only, offline product envelope.

## Verified current candidate observations — 2026-08-24

### Qwen3.5-2B-Base

- Upstream: `Qwen/Qwen3.5-2B-Base`.
- Apache-2.0.
- 2B language model with vision encoder.
- hybrid Gated DeltaNet/attention architecture.
- MTP trained with multiple steps.
- 262,144 native context, but MSTR must qualify at laptop-realistic 4K/8K/16K contexts rather than treating the vendor maximum as usable local context.
- upstream exposes Transformers/vLLM/SGLang use and quantization discovery for llama.cpp-compatible apps.

Source:
https://huggingface.co/Qwen/Qwen3.5-2B-Base

### Qwen3.5-4B-Base

- Upstream: `Qwen/Qwen3.5-4B-Base`.
- Apache-2.0.
- 4B-class language model with vision encoder.
- hybrid Gated DeltaNet/attention architecture.
- MTP-capable family.
- strong foundation candidate, but 8 GB whole-laptop memory, Q4 reliability, and portable CPU-runtime maturity remain unproven MSTR gates.

Source:
https://huggingface.co/Qwen/Qwen3.5-4B-Base

### Ministral-3-3B-Base-2512

- Upstream: `mistralai/Ministral-3-3B-Base-2512`.
- Apache-2.0.
- approximately 3.4B language model plus approximately 0.4B vision encoder.
- designed for edge deployment; upstream states quantized deployment below 8 GB RAM/VRAM is possible.
- 256K-class configured context, but laptop-realistic context still must be measured.
- useful architectural/deployment hedge against the Qwen3.5 hybrid family.

Source:
https://huggingface.co/mistralai/Ministral-3-3B-Base-2512

### Qwen3-4B-Base

- Upstream: `Qwen/Qwen3-4B-Base`.
- Apache-2.0.
- mature dense text-model control with broad ecosystem support.
- valuable because a simpler mature architecture may beat a newer architecture once Q4, CPU runtime, tool reliability, and whole-laptop constraints are included.

Source:
https://huggingface.co/Qwen/Qwen3-4B-Base

### Granite-4.1-3B-Base

- Upstream: `ibm-granite/granite-4.1-3b-base`.
- Apache-2.0.
- 3B base checkpoint released in 2026.
- explicitly supports Fill-in-the-Middle code completion.
- trained from a Granite 4.x foundation with an extended long-context phase.
- important omission from the first draft and now a required static-qualification candidate because it combines permissive redistribution, compact size, and native FIM relevance.

Source:
https://huggingface.co/ibm-granite/granite-4.1-3b-base

### SmolLM3-3B-Base

- Upstream: `HuggingFaceTB/SmolLM3-3B-Base`.
- Apache-2.0.
- 3B base with mature Transformers/ONNX-oriented ecosystem visibility.
- retained as an open, text-only control; it must earn any weight-download slot on static quality/runtime evidence.

Source:
https://huggingface.co/HuggingFaceTB/SmolLM3-3B-Base

### Qwen2.5-Coder-1.5B lower-bound control

- Upstream: `Qwen/Qwen2.5-Coder-1.5B`.
- Apache-2.0.
- 1.54B pretraining-stage code-specialized model.
- supports FIM use and 32,768-token context per the upstream card.
- deliberately below the nominal 2B–4B primary range: if post-training this much smaller model produces better verified laptop utility per GB/second, MSTR should know that before committing to 3B–4B.

Source:
https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B

## Candidate removed by exact license review

### Qwen2.5-Coder-3B

The first MSTR-000 draft incorrectly treated `Qwen/Qwen2.5-Coder-3B` as an eligible code-specialized control. Exact upstream review shows its current license is the **Qwen Research License**, not Apache-2.0. The license restricts granted use to non-commercial purposes and requires a separate commercial license.

That conflicts with the founder goal that MSTR be broadly usable and redistributable. Therefore:

```text
QWEN2_5_CODER_3B_PRIMARY_BACKBONE = INELIGIBLE
REASON = RESEARCH_NONCOMMERCIAL_LICENSE
```

It may be referenced academically or used only in a separately authorized research comparison consistent with its terms. It cannot become the primary MSTR backbone.

Source:
https://huggingface.co/Qwen/Qwen2.5-Coder-3B/blob/main/LICENSE

This defect demonstrates why exact license qualification must precede model-weight access.

## Other current watchlist observations

### Phi-4-mini-instruct

`microsoft/Phi-4-mini-instruct` is a 3.8B dense post-trained model under MIT and is useful as a ready-made local reference for reasoning/tool behavior. It is not automatically a clean foundation candidate because the checkpoint is post-trained; MSTR may use it as a comparison point unless a suitable base checkpoint and training rights are separately qualified.

Source:
https://huggingface.co/microsoft/Phi-4-mini-instruct

### LFM2.5-2.6B

Liquid AI publishes an on-device-oriented 2.6B family and reports strong CPU/low-memory inference characteristics. Its custom `LFM Open License v1.0` requires a separate legal-compatibility review before it can enter the primary backbone tournament. Do not equate "open" in a model card with automatic MSTR redistribution compatibility.

Source:
https://huggingface.co/LiquidAI/LFM2.5-2.6B-Base

### Large-active-vs-total caveat

A model can report very low **activated** parameters while storing far more total weights. MSTR's universal-laptop gate is based on total artifact/storage/RAM reality, not active-parameter marketing. Large-total-weight MoE models cannot enter the primary tournament merely because their active parameter count is small.

## External adversarial consultation reconciliation

An adversarial architecture review recommended several changes that remain useful after the laptop-goal clarification.

### Accepted

- freeze prompt/tool/edit/cache semantics before serious training;
- treat environment throughput as a major RL bottleneck;
- keep FIM replay during later SFT/RL to reduce forgetting;
- prefer deterministic stale-safe edit application before building a learned apply model;
- train or refresh speculative/MTP capability with the target rather than maintain a stale separate drafter;
- maintain raw-model / neutral-harness / full-system evaluation separately;
- make reward-hacking tests continuous;
- build a private fresh-task Gauntlet;
- keep heavy graph systems as tournament arms rather than dependencies;
- use TTVC rather than tokens/sec as the principal task-speed metric.

### Modified by the universal-laptop goal

The earlier ~9B primary recommendation is superseded for MSTR-000. Larger checkpoints may later serve as teachers, data generators, upper-bound controls, or optional high-memory editions. They may not silently replace the universal primary product.

## Provisional hardware and install definition

"Any laptop" cannot literally include every historical machine. MSTR-000 therefore starts from a broad contemporary floor and must validate it empirically:

```text
8 GB total RAM
modern x86_64 or ARM64 CPU
no discrete GPU
reference context = 8K tokens
4K/8K/16K context ladder measured
<=3 GB primary Q4 model artifact target
no provider account/API key
no Docker requirement for basic local assistance
offline after install
telemetry/network egress off by default
```

The model must be tested while a real editor and OS are running. A model that consumes nearly all 8 GB by itself has not satisfied the founder goal even if it technically loads.

The project should additionally characterize 4 GB and older-CPU behavior. Failure there does not automatically invalidate the primary release, but any genuinely usable lower-memory configuration is strategically valuable.

## Research risks still open

1. A 1.5B–2B model may meet universal deployment goals but miss the desired SWE quality ceiling.
2. A 4B model may offer better quality but have an uncomfortable whole-system memory/latency envelope on 8 GB systems.
3. Multimodal vision towers may add download/runtime cost that is not justified for v1.
4. Hybrid attention architectures may complicate quantization or portable local backends.
5. Q4 may disproportionately damage tool-call JSON/FIM reliability.
6. Vendor maximum-context claims are irrelevant if laptop memory makes those contexts unusable.
7. Repository/runtime intelligence may provide more practical value than adding parameters; this must be measured rather than assumed.
8. CPU-only sustained inference may cause thermal throttling, poor battery life, or make the editor unresponsive even when RAM fits.
9. Custom/open-looking licenses may still conflict with unrestricted MSTR distribution.
10. Teacher-model/API output terms can contaminate the legal status of a distillation pipeline even when the base model is permissively licensed.

## Research thesis

MSTR's best chance is not to reproduce frontier raw intelligence on a laptop. It is to maximize **verified software-engineering utility per GB and per second** through a small strong model, precise repository localization, compact context, deterministic editing, cheap verification, strong executable post-training, and a genuinely frictionless local distribution path.
