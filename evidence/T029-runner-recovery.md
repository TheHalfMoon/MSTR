# T029 Runner Recovery Evidence

**Task:** `T029`
**Scope:** runner hardening and historical result reconciliation only
**Canonical base:** `97904ac5ad17e7142e88944ee83dbb304ecb197f`
**State:** `REPAIR_CANDIDATE / NOT_T029_COMPLETE_CANONICAL`

## Why This Repair Exists

The T029 execution surface was merged by PR #35, but T029 was never closed canonical. Historical GitHub Actions evidence shows three execution generations.

### Generation 1 — dependency-invalid batch

Head: `e46699d1892046bed8a1fc5090320f71e3c3bf06`

Eight candidate runs failed before valid conversion because `convert_hf_to_gguf.py` could not import NumPy. Those reports were infrastructure/runner failures and are not Q4 compatibility evidence.

```text
ROOT_CAUSE = ModuleNotFoundError: No module named 'numpy'
SCIENTIFIC_Q4_FAILURE = NOT_PROVEN
```

Commit `c937df457cdbf241f519e39e1585e9ad947a22c5` added the required conversion dependencies and corrected missing-dependency classification.

### Generation 2 — dependency repair

Head: `c937df457cdbf241f519e39e1585e9ad947a22c5`

This generation reran the eight-candidate batch after installing conversion dependencies. It remained superseded by the later compatibility repair below and is not used as final T029 evidence.

### Generation 3 — final historical batch

Head: `406de41d132fa6d24d55814f3f6dd4fced5f12bd`

Commit `406de41d132fa6d24d55814f3f6dd4fced5f12bd` added `safetensors`/`transformers` and moved the T029 llama.cpp execution pin to:

```text
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
```

Seven of eight final candidate runs produced durable `Q4_PROFILE_READY` reports with both `Q4_K_M` and `Q4_K_S` arms `OK`:

| Candidate | Run | Artifact | Result |
| --- | ---: | ---: | --- |
| `qwen3.5-2b` | `32959707029` | `9603552151` | `Q4_PROFILE_READY` |
| `qwen3.5-4b` | `32959712851` | `9603766969` | `Q4_PROFILE_READY` |
| `qwen3-4b` | `32959723760` | `9603722432` | `Q4_PROFILE_READY` |
| `granite-4.1-3b` | `32959729068` | `9603875247` | `Q4_PROFILE_READY` |
| `smollm3-3b` | `32959733977` | `9603684909` | `Q4_PROFILE_READY` |
| `qwen2.5-coder-1.5b` | `32959739245` | `9603602508` | `Q4_PROFILE_READY` |
| `yi-coder-1.5b` | `32959744422` | `9603583604` | `Q4_PROFILE_READY` |

Every successful report binds:

- the exact model revision;
- source-file acquisition/integrity checks;
- llama.cpp commit `fc35562ba46fbbf8e30cac85edbb39642c37d248`;
- conversion recipe `convert_hf_to_gguf.py --outtype f16`;
- F16 GGUF SHA-256 and byte size;
- Q4_K_M SHA-256 and byte size;
- Q4_K_S SHA-256 and byte size;
- execution environment identity;
- `USD 0.00` resource cost.

## Ministral Run #19 Is Not a Q4 Rejection

Final historical Ministral run:

```text
RUN = 32959718688
JOB = 98149160350
CANDIDATE = ministral-3-3b
LLAMA_CPP = fc35562ba46fbbf8e30cac85edbb39642c37d248
```

The job successfully completed checkout, Python setup, build-toolchain installation, and conversion dependency installation. The runner proceeded through HF -> GGUF conversion and entered `llama-quantize` execution.

The Python wrapper then failed while decoding quantizer stderr:

```text
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc4 in position 4034: invalid continuation byte
```

The failure occurred inside `subprocess.run(..., text=True)` while translating captured stderr. It is therefore a runner output-decoding failure, not evidence that Ministral conversion or Q4 quantization is unsupported.

The report upload then failed because the unexpected exception occurred before the report was written. Cleanup succeeded.

Canonical interpretation:

```text
MINISTRAL_Q4_STATUS = PENDING_RETRY_AFTER_RUNNER_FIX
MINISTRAL_Q4_UNSUPPORTED = NOT_PROVEN
MINISTRAL_Q4_INTEGRITY_FAILURE = NOT_PROVEN
```

## Repair

`run()` now requests deterministic UTF-8 decoding with replacement for invalid subprocess bytes:

```python
subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    ...,
)
```

This preserves bounded diagnostic text without allowing arbitrary quantizer byte sequences to crash the evidence runner.

A regression executes a child Python process that writes invalid UTF-8 bytes directly to stderr and requires:

```text
RETURN_CODE = 0
DIAGNOSTIC_TEXT_PRESERVED = TRUE
INVALID_BYTES_REPLACED = TRUE
UNEXPECTED_UNICODE_DECODE_EXCEPTION = FALSE
```

A second regression proves ordinary UTF-8 output is unchanged.

## Authority Boundary

This repair itself performs no model access, inference, quantization, paid compute, large dataset ingestion, or release action.

```text
MODEL_WEIGHT_ACCESS_BY_REPAIR = NONE
MODEL_EXECUTION_BY_REPAIR = NONE
QUANTIZATION_EXECUTION_BY_REPAIR = NONE
PAID_COMPUTE_BY_REPAIR = NONE
LARGE_DATASET_INGESTION_BY_REPAIR = NONE
```

The historical seven successful reports were produced under the already-authorized T027/T028 candidate envelope. Re-running Ministral remains an execution action and must use the same canonical T029/T028 authority and exact pinned inputs; this document does not manufacture new authority.

## Completion Boundary

This repair does not mark T029 complete. T029 remains open until:

1. the repair candidate passes required repository gates and governance;
2. Ministral is rerun or receives an evidence-backed explicit rejection under the T029 contract;
3. durable quantization manifests are committed under `artifacts/manifests/quantization/` for the final admitted/rejected T029 cells;
4. `evidence/T029-q4-profiles.md` is complete;
5. T029 closeout is canonical through repository governance.
