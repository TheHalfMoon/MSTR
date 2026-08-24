# MSTR-000 Research Reconciliation

## Decision context

The founder clarified that the primary MSTR model must be installable and usable by people on ordinary laptops. That constraint changes the preconstruction search space materially: ~7–9B may remain useful as teachers or optional editions, but the primary tournament must first test dense ~2–4B foundations.

## Current primary-source observations

### Qwen3.5-2B-Base

- Apache-2.0.
- 2B-class Qwen3.5 base family.
- multimodal architecture.
- available through Transformers/vLLM/SGLang-compatible tooling.
- third-party local Q4 artifacts demonstrate that approximately 1.3 GB weight packages are technically possible on Apple Silicon; MSTR must independently qualify its own artifact/runtime path.

Source:
https://huggingface.co/Qwen/Qwen3.5-2B-Base

### Qwen3.5-4B-Base

- Apache-2.0.
- 4B language model with vision encoder.
- hybrid Gated DeltaNet / attention architecture.
- MTP trained with multiple steps.
- 262,144 native context.
- positioned as a fine-tuning/development base.

Source:
https://huggingface.co/Qwen/Qwen3.5-4B-Base

### Ministral-3-3B-Base-2512

- Apache-2.0.
- dense ~3B class candidate.
- 262,144 configured context.
- multimodal architecture.
- valuable deployment hedge because it differs architecturally from Qwen3.5.

Source:
https://huggingface.co/mistralai/Ministral-3-3B-Base-2512

### Qwen3-4B-Base

- Apache-2.0.
- mature dense-text control with broad ecosystem support.

Source:
https://huggingface.co/Qwen/Qwen3-4B-Base

### Qwen2.5-Coder-3B

- code-specialized control.
- Qwen reports a 5.5T-token coder training program across the Qwen2.5-Coder family.
- useful as a control for whether a newer general base plus MSTR post-training actually beats an older code-specialized foundation.

Source:
https://huggingface.co/Qwen/Qwen2.5-Coder-3B

### Large-active-vs-total caveat

Qwen3-Coder-Next reports 3B activated parameters but 80B total parameters. That can be attractive for server inference efficiency, but total weight storage/memory makes it a poor default candidate for a universal-laptop primary release.

Source:
https://huggingface.co/Qwen/Qwen3-Coder-Next

## External adversarial consultation reconciliation

An adversarial architecture review recommended several changes that remain useful after the laptop-goal clarification:

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
- use TTVC rather than tokens/sec as the principal product-speed metric.

### Modified by the universal-laptop goal

The earlier ~9B primary recommendation is superseded for MSTR-000. The first tournament is now ~2B–4B dense. A larger checkpoint may later serve as:

- teacher;
- data generator;
- upper-bound control;
- optional high-memory edition.

It may not silently replace the universal primary product.

## Provisional hardware definition

"Any laptop" cannot literally include every historical machine. MSTR-000 therefore starts from a broad contemporary floor and must validate it empirically:

```text
8 GB RAM
modern x86_64 or ARM64 CPU
no discrete GPU
local storage sufficient for <=3 GB primary model artifact
```

The project should additionally characterize 4 GB and older-CPU behavior, but failure there does not automatically invalidate the primary release. The final hardware floor must be explicit and measured.

## Research risks still open

1. A 2B model may meet the universal deployment goal but miss the desired SWE quality ceiling.
2. A 4B model may offer better quality but have an uncomfortable memory/latency envelope on 8 GB systems.
3. Multimodal vision towers may add download/runtime cost that is not justified for v1.
4. Hybrid attention architectures may complicate quantization or local backends.
5. Q4 may disproportionately damage tool-call JSON/FIM reliability.
6. Large context claims are irrelevant if laptop memory makes those contexts unusable.
7. Repository/runtime intelligence may provide more practical value than adding parameters; this must be measured rather than assumed.

## Research thesis

MSTR's best chance is not to reproduce frontier raw intelligence on a laptop. It is to maximize **verified software-engineering utility per GB and per second** through a small strong model, precise repository localization, compact context, deterministic editing, cheap verification, and post-training on executable software tasks.
