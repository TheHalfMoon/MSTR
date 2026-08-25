# T020 — Post-Trained Comparison Points (Reference Context Only)

**Task:** MSTR-000 / T020
**Branch:** task/000-t012-t020-static-candidates
**Scope:** record useful compact post-trained comparison points from live public metadata. These records are context for later evaluation; they are **never** foundation winners and never enter backbone selection. No weight access, no execution, no paid API, no training.

## Recorded comparison points (live-fetched 2026-08-25)

| candidate_id | upstream | revision | params | license | why useful |
|---|---|---|---|---|---|
| `comparison-qwen2.5-coder-7b-base` | Qwen/Qwen2.5-Coder-7B | `0396a76181e127dfc13e5c5ec48a8cee09938b02` | 7.62B | Apache-2.0 (tags) | Capability ceiling of the code-specialized family that the T018 control belongs to |
| `comparison-smollm2-1.7b-instruct` | HuggingFaceTB/SmolLM2-1.7B-Instruct | `31b70e2e869a7173562077fd711b654946d38674` | 1.71B | Apache-2.0 (tags) | Instruct-tuned compact general model; predecessor lineage of the SmolLM3 arm |
| `comparison-qwen3-4b-instruct-2507` | Qwen/Qwen3-4B-Instruct-2507 | `cdbee75f17c01a7cc42f958dc650907174af0554` | 4.02B | Apache-2.0 (tags) | Post-trained counterpart of the Qwen3-4B-Base control; isolates instruct delta at identical scale |

All three: schema-valid via CLI (`validate` exit 0), status `discovered`, role `comparison`. FIM capability recorded only where verified from tokenizer.json at pinned revision (`unknown` for SmolLM2 — not fetched at token level for this reference-only purpose).

## Discipline notes

- Comparison points are excluded from foundation admission by role; T22 selection operates on foundations/controls only.
- Their rights evidence is lighter than T012–T018 because no artifact acquisition is planned; if any comparison is ever executed in a benchmark, its exact terms must first be re-verified at a fresh pinned revision.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
NETWORK_SERVICE_ACCESS = metadata-only HTTPS GETs to huggingface.co
PAID_MODEL_API_EXECUTION = NONE
RENTED_COMPUTE = NONE
TRAINING = NONE
```
