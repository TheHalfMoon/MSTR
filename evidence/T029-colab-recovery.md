# T029 Ministral Colab Recovery Surface

**Task:** `T029`  
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`  
**State:** `EXECUTION_SURFACE_READY / NOT_EXECUTED / NOT_T029_COMPLETE_CANONICAL`

## Purpose

GitHub-hosted T029 recovery jobs currently fail before exposing any job steps. The canonical T028 acquisition record permits ephemeral cloud runners and explicitly records Google Colab as an available execution surface. This artifact prepares the remaining `ministral-3-3b` retry for that already-authorized executor class without performing the retry itself.

Notebook:

```text
colab/MSTR_T029_ministral_recovery.ipynb
```

## Exact Inputs

The notebook fails closed unless the repository checkout contains these exact Git blobs:

```text
T029 runner blob   = 63c81229d0c797ea0347255f0916d0b7ed9a9514
T027 manifest blob = ef73095e2e9c5bdcca7147d4bdeb92a5aa9a6d0f
```

It binds the remaining execution to:

```text
candidate          = ministral-3-3b
model revision     = 6f9c4b12a95b139af68670a6713616b757923735
llama.cpp commit   = fc35562ba46fbbf8e30cac85edbb39642c37d248
provider auth      = prohibited / not required
gated terms        = prohibited / not required
monetary ceiling   = USD 0.00
```

## Effect Boundary

The notebook performs no action merely by existing in Git. If executed in an authorized ephemeral Colab VM, it may only re-acquire the already-T028-authorized Ministral candidate under the frozen T027 identity, convert/quantize it under the pinned T029 recipe, emit one JSON report, and remove the ephemeral binary work directory.

It does not authorize or reference the MSTR-000B B011 candidates. In particular:

```text
mellum-4b             = OUT OF SCOPE
qwen3.5-0.8b-control  = OUT OF SCOPE
weight-changing train = PROHIBITED
model inference       = NOT PART OF THIS NOTEBOOK
paid compute          = PROHIBITED
production release    = PROHIBITED
```

## Hosted Runner Truth

Exact-head T029 evidence run `33262146496` has repeatedly failed before any job step. The most recent retry again produced `steps=null` for `quality`, `identity_scope`, and `ministral_retry`; therefore no checkout, test, download, conversion, or quantization occurred.

This is infrastructure evidence only. It is neither an implementation failure nor a PASS.

## Completion Boundary

This Colab surface does not complete T029. T029 remains open until the remaining Ministral cell has a durable governed result (or an evidence-backed governed rejection), the material repository gates execute successfully on the exact final implementation head, and ordinary review/premerge/merge/closeout governance is satisfied.
