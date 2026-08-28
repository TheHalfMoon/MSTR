# B008 Tokenizer Economics Measurement

**Task:** `B008`
**State:** COMPLETE_CANONICAL
**Implementation PR:** `#61`
**Final implementation head:** `895983470f72128ad698023b3578553ed1cfe7c4`
**Canonical implementation merge:** `07762204ab126c0fccf9ca55a8b572bd6368d8bc`
**Canonical entry main:** `7f2fe43797db4b94103ca07c172de5672806f624`

## Entry and execution evidence

```text
ENTRY_GATE_RUN = 33151438249
ENTRY_GATE_JOB = 98784106816
ENTRY_GATE_TASK = B008
ENTRY_GATE_CANONICAL_MAIN = 7f2fe43797db4b94103ca07c172de5672806f624
ENTRY_GATE_ELIGIBLE = true
TOKENIZER_JSON_LOADABILITY_RUN = 33151738043
TOKENIZER_JSON_LOADABILITY_JOB = 98785061204
MEASUREMENT_RUN = 33153206993
MEASUREMENT_EXECUTOR = GitHub-hosted ubuntu-24.04 / Python 3.11 / tokenizers 0.22.0
REMOTE_FILE_PER_CANDIDATE = tokenizer.json only
MODEL_INFERENCE = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

## Candidate set

The measured set is derived from canonical candidate records with `status=static_qualified`, `rights.decision=pass_permissive`, and no account/clickthrough gate. Exactly 10 candidates satisfy that rule on the entry main.

## Results

Higher weighted bytes/token means denser payload under this fixed synthetic corpus. The 8192-token payload is a corpus-ratio estimate, not a context-window claim.

| Candidate | Bytes/token | Total tokens | 8K payload bytes | Diff tokens | Stacktrace tokens | Tool JSON tokens | Path tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| `smollm3-3b` | 3.247748 | 1110 | 26605 | 75 | 76 | 85 | 76 |
| `granite-4.1-3b` | 3.102410 | 1162 | 25414 | 78 | 81 | 90 | 80 |
| `qwen2.5-coder-1.5b` | 3.102410 | 1162 | 25414 | 77 | 84 | 92 | 78 |
| `qwen3-4b` | 3.102410 | 1162 | 25414 | 77 | 84 | 92 | 78 |
| `qwen3.5-0.8b-control` | 2.991701 | 1205 | 24508 | 80 | 87 | 93 | 78 |
| `qwen3.5-2b` | 2.991701 | 1205 | 24508 | 80 | 87 | 93 | 78 |
| `qwen3.5-4b` | 2.991701 | 1205 | 24508 | 80 | 87 | 93 | 78 |
| `ministral-3-3b` | 2.976879 | 1211 | 24386 | 80 | 85 | 97 | 78 |
| `mellum-4b` | 2.739362 | 1316 | 22440 | 93 | 89 | 93 | 93 |
| `yi-coder-1.5b` | 2.342430 | 1539 | 19189 | 98 | 102 | 133 | 109 |

## Measurement contract

- Corpus integrity is checked against the frozen B007 manifest before any tokenizer is used.
- Only pinned `tokenizer.json` is acquired for each candidate; that exact file is SHA-256 inventoried and is the only tokenizer artifact loaded.
- `tokenizers.Tokenizer.from_file` is used with `add_special_tokens=false`; chat templates, padding, truncation, pre-normalization, BOS and EOS injection are not used.
- Identifier-like spans use the frozen ASCII regex and are encoded in isolation. p50/p95 use deterministic nearest-rank percentiles.
- Structural observations are recorded for diff, file paths, stack traces and tool JSON fixtures.
- All temporary tokenizer files are deleted in the ephemeral runner before completion.

## Claim boundary

These results compare tokenizer economics on the deterministic B007 synthetic fixture only. They do not establish population-level code efficiency, model quality, inference quality, trainability, or production fitness.

This task does not perform model inference, accept gated terms, use paid compute, or place tokenizer artifacts on the founder machine.

## Canonical closeout evidence

B008 is canonicalized only after exact-main entry proof, tokenizer-only measurement, exact-head qualification, independent adversarial review, expected-head implementation merge, and post-implementation verification on canonical main. The task catalog now enumerates all 10 measured serious-candidate result files as required outputs before B009 can satisfy its B008 prerequisite.

```text
ENTRY_GATE_RUN = 33151438249
ENTRY_GATE_JOB = 98784106816
IMPLEMENTATION_BUILDER_RUN = 33153206993
IMPLEMENTATION_BUILDER_JOB = 98789818808
IMPLEMENTATION_PR = #61
FINAL_IMPLEMENTATION_HEAD = 895983470f72128ad698023b3578553ed1cfe7c4
CANONICAL_IMPLEMENTATION_MERGE = 07762204ab126c0fccf9ca55a8b572bd6368d8bc
EXACT_HEAD_QUALIFICATION_RUN = 33153394825
EXACT_HEAD_QUALIFICATION_JOB = 98790425624
INDEPENDENT_REVIEW_RUN = 33153850333
INDEPENDENT_REVIEW_JOB = 98791884940
POST_IMPLEMENTATION_VERIFY_RUN = 33154074016
POST_IMPLEMENTATION_VERIFY_JOB = 98792580522
POST_IMPLEMENTATION_MAIN = 07762204ab126c0fccf9ca55a8b572bd6368d8bc
POST_IMPLEMENTATION_B008_ELIGIBLE = true
POST_IMPLEMENTATION_B009_ELIGIBLE = false
POST_IMPLEMENTATION_B009_REASON = prerequisite.unsatisfied:B008
POST_IMPLEMENTATION_DRIFT = clean
CLOSEOUT_BUILDER_RUN = 33155512527
REQUIRED_RESULT_COUNT = 10
MODEL_INFERENCE = NONE
MODEL_WEIGHT_ACCESS = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_COMPUTE = NONE
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B009 eligibility after this state transition is scheduling eligibility only. B009 remains metadata/code/docs validation unless already-authorized artifacts are sufficient; this closeout creates no model-weight access, model inference, paid compute, training, or new external authority.
