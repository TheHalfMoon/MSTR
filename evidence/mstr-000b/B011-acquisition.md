# B011 — Exact B010 Candidate Acquisition

**Task:** `MSTR-000B / B011`  
**Evidence state:** `ACQUISITION_EXECUTED_VERIFIED / CANONICAL_CLOSEOUT_PENDING`  
**Canonical execution base:** `dd547bb768598f92ad203764ce32be6e1fc710d6`  
**B010 manifest SHA-256:** `4c2fd1469cdcf728063ab8f5b6a603191ffdc9e1a4d4c2d794abd2a24950c3ef`  
**Founder authority:** `B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED`  
**Founder decision:** `FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE`

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

### Mellum

Runner report: `evidence/mstr-000b/B011-runner-reports/mellum-4b.json`  
Report SHA-256: `e03f48e3a5744ef87ad39558c20ca96b61c47d8296e6f877795dac2dbfe0c9f9`

- observed bytes: `8048099065` = authorized bytes;
- weight shard `model-00001-of-00002.safetensors`: `04bf4f574526ebecd75283af1f7ed0a412362388ddd28360c1581706cb3a00d2`;
- weight shard `model-00002-of-00002.safetensors`: `8fa0269d11332e13874280dbf5a15d5d6086d038656832c16e984544caf4b21b`;
- observed serving hosts: `huggingface.co`, `us.aws.cdn.hf.co`, both authorized.

### Qwen control

Runner report: `evidence/mstr-000b/B011-runner-reports/qwen3.5-0.8b-control.json`  
Report SHA-256: `c4174fc784ea0ca43dae61a81665716d476a27b943e973923e18eb6eb6ab3ad7`

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

## Closeout Boundary

This evidence does **not** by itself set B011 to `COMPLETE_CANONICAL`. B011 remains `PENDING` until this implementation evidence is qualified, independently reviewed, merged, and then closed by a separate governed closeout. B012 remains blocked until that canonical closeout.
