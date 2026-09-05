# B011 — Exact B010 Candidate Acquisition

**Task:** `MSTR-000B / B011`  
**Evidence state:** `COMPLETE_CANONICAL`
**Canonical execution base:** `dd547bb768598f92ad203764ce32be6e1fc710d6`  
**B010 manifest SHA-256:** `4c2fd1469cdcf728063ab8f5b6a603191ffdc9e1a4d4c2d794abd2a24950c3ef`  
**Founder authority:** `B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED`  
**Founder decision:** `FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE`

**State:** `COMPLETE_CANONICAL`
ENTRY_GATE_TASK=B011
ENTRY_GATE_CANONICAL_MAIN=dd547bb768598f92ad203764ce32be6e1fc710d6
ENTRY_GATE_ELIGIBLE=true
**Closeout entry canonical main:** `a788f55f5251f0be92b33e0765d0436cb321eb8b`
**Implementation PR:** `#157`
**Final implementation head:** `450d9b5b9b3c6aca27222a553dc6230f6eef6783`
**Canonical implementation merge:** `b9aa4f7de8b924d283d09fa8d93dbaceb0f6b4cd`
**Successful acquisition run:** `33865617854`
**Exact-head qualification:** `33867186224`
**Independent substantive semantic review:** `33867564924`
**Mandatory premerge verification:** `33867838434`
**Post-implementation verification:** `33927258696`
**Frontier-planning postmerge verification:** `33926866711`

## Scope

B011 accessed only the two candidates named by the exact canonical B010 envelope:

| Candidate | Upstream | Immutable revision | Verified bytes | Result |
|---|---|---|---:|---|
| `mellum-4b` | `JetBrains/Mellum-4b-base` | `83cce2605fbdf6a3868627e9b0a5924e0072b94d` | `8048099065` | `ACQUIRED_VERIFIED` |
| `qwen3.5-0.8b-control` | `Qwen/Qwen3.5-0.8B-Base` | `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68` | `1769897109` | `ACQUIRED_VERIFIED` |

Total verified bytes: `9817996174`, exactly equal to the authorized aggregate ceiling. Paid cost: `USD 0.00`.

## Fail-Closed Harness Evidence

The first attempt, Actions run `33865467059`, failed before acquisition because the evidence checkout did not expose the canonical commit through local `refs/heads/main`. The machine gate returned `task_gate.main_ref_invalid`. Both acquisition steps were skipped; no model-weight download started. Cleanup still executed.

The evidence harness was repaired without changing `main` or widening authority. The corrected execution branch head was `86609c656e20ac959c206d15fc21eda1f633b6ec`.

## Successful Execution

Actions run `33865617854` independently executed one ephemeral job per candidate. Both jobs:

1. proved the evidence branch contained only the B011 runner/workflow surface;
2. verified remote `main` was exactly `dd547bb768598f92ad203764ce32be6e1fc710d6`;
3. exposed that exact commit through local canonical refs;
4. verified the exact B010 manifest byte identity;
5. obtained exact-main `mstr-qualify task eligible B011` with authority satisfied and canonical B011 state `PENDING`;
6. fetched only required files from pinned Hugging Face revisions;
7. enforced HTTPS and the exact B010 redirect host allowlist;
8. streamed exact byte counts and SHA-256 identities;
9. uploaded JSON reports only;
10. deleted model bodies from the ephemeral runner;
11. rechecked canonical `main` for drift.

## Independent Report Reconciliation

The durable repository copies intentionally use deterministic minified JSON, while the source Actions reports use the runner's indented serialization. They are semantically identical but not byte-identical. Both identities are preserved explicitly; no formatting transformation is represented as byte identity.

### Mellum

Canonical report: `evidence/mstr-000b/B011-runner-reports/mellum-4b.json`  
Canonical report SHA-256: `8e07bffeeb657eef35c294183c1af77ab3f3ffaa9ec87bd12fc5895cba76010d`  
Source Actions report SHA-256: `e03f48e3a5744ef87ad39558c20ca96b61c47d8296e6f877795dac2dbfe0c9f9`  
Actions artifact ID: `9933928427`  
Actions artifact ZIP SHA-256: `985136da92696ac76440adea05b43472367e099ff9a96c78908a9a5a8f3d9915`

- observed bytes: `8048099065` = authorized bytes;
- weight shard `model-00001-of-00002.safetensors`: `04bf4f574526ebecd75283af1f7ed0a412362388ddd28360c1581706cb3a00d2`;
- weight shard `model-00002-of-00002.safetensors`: `8fa0269d11332e13874280dbf5a15d5d6086d038656832c16e984544caf4b21b`;
- observed serving hosts: `huggingface.co`, `us.aws.cdn.hf.co`, both authorized.

### Qwen control

Canonical report: `evidence/mstr-000b/B011-runner-reports/qwen3.5-0.8b-control.json`  
Canonical report SHA-256: `0ca35318cf3ed37ce5c93eb2b2da5a83c50b0b692209c72cdf5a4d2c311ce691`  
Source Actions report SHA-256: `c4174fc784ea0ca43dae61a81665716d476a27b943e973923e18eb6eb6ab3ad7`  
Actions artifact ID: `9933865616`  
Actions artifact ZIP SHA-256: `1a69e8df4c44cb90185495aee677582561dd835285dda9028af08f69fbf81abf`

- observed bytes: `1769897109` = authorized bytes;
- model weight SHA-256: `c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c`;
- pinned tokenizer SHA-256: `fe000e3ed39ed12b8d2481d527d44f93c65d37e87645d2dcc80d1bf9d50d2927`;
- observed serving hosts: `huggingface.co`, `us.aws.cdn.hf.co`, both authorized.

The T024-compatible manifests preserve SHA-256 and exact size for every acquired file:

- `artifacts/manifests/B011-artifact-mellum-4b.json`
- `artifacts/manifests/B011-artifact-qwen3.5-0.8b-control.json`

Aggregate acquisition binding:

- `artifacts/manifests/B011-acquired-candidates.json`

## Authority Boundary

This execution performed model-weight access only. It performed no model inference, conversion, quantization, training, large-dataset ingestion, gated-terms acceptance, paid compute/API use, production release, or Git/founder-machine model-binary persistence.

Successful binaries were intentionally not retained. Canonical storage policy requires downstream B012 qualification runners to re-acquire the same pinned inputs when B012 becomes independently eligible.

## Canonical Closeout

The B011 acquisition/verification implementation is complete and all required lifecycle evidence is bound above. The earlier fail-closed run `33865467059` remains preserved as negative evidence: no model-weight download started in that attempt.

This closeout changes only the canonical lifecycle state of B011. It does not re-acquire any model body, does not perform model execution, conversion, quantization, training, large-dataset ingestion, gated-terms acceptance, paid compute/API use, production release, or model-binary persistence.

The historical authority `B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED` remains an execution record scoped only to B011 and the exact B010 envelope. It does not transfer to, authorize, or widen B012 or any later task. In particular, it does not authorize K2 Horizon or any newly discovered candidate.

`COMPLETE_CANONICAL` is valid only after this closeout candidate is merged to canonical `main` and the required post-closeout exact-main verification succeeds. Until then, canonical `main` remains authoritative.
