# B007 — Tokenizer Economics Corpus / Protocol

**Workstream:** MSTR-000B  
**Task:** B007  
**State:** IMPLEMENTATION_ACTIVE / NOT_COMPLETE_CANONICAL  
**Canonical main at execution:** `ead69ae26265b133c782ae8fd2795c126253a3b6`  
**Current branch head:** `3d5afebe69d27c7dff08e432baff0c14776572e5`  
**Protocol:** `MSTR-TOKENIZER-ECONOMICS-v0`

B007 freezes deterministic corpus bytes and measurement semantics only. It does not acquire or execute a tokenizer, run model inference, access model weights, use paid compute, ingest a large dataset, or authorize B008 execution.

## Current outputs and exact Git identities

```text
CORPUS = benchmarks/fixtures/tokenizer-economics/B007-corpus.json
CORPUS_GIT_BLOB = af4cf20b29f5884010e79565e394af41c5a42214
CORPUS_FILE_SHA256 = 425456fa39ae5dc67214b4871b1ac948c63bf9f0ae72a1407a5908d4a5c9e1d6
CORPUS_FILE_BYTES = 10951
DECODED_CONTENT_BYTES = 3605
ENTRY_COUNT = 34
ENTRY_BYTE_MIN = 61
ENTRY_BYTE_MEDIAN = 101.5
ENTRY_BYTE_MAX = 187

MANIFEST = benchmarks/manifests/B007-tokenizer-economics.json
MANIFEST_GIT_BLOB = abc7e7216f3aa7ad2c4c46bbc57d97ddd4e82968

CORPUS_SCHEMA = specs/002-code-model-supremacy-foundation/contracts/b007-tokenizer-economics-corpus-v0.schema.json
CORPUS_SCHEMA_GIT_BLOB = f11394e87d6d569feb58616dc8b7a90dbbd2d549

PROTOCOL_SCHEMA = specs/002-code-model-supremacy-foundation/contracts/b007-tokenizer-economics-protocol-v0.schema.json
PROTOCOL_SCHEMA_GIT_BLOB = 50a0725336c14687a2da393f417b7832c0261a9c

INTEGRITY_TEST = tests/contract/test_b007_tokenizer_economics.py
INTEGRITY_TEST_GIT_BLOB = c68302f6d34f97263861b4119d59808c54bcede1
```

The corpus Git blob identity equals the Git blob SHA-1 independently computed for the exact `10951` committed bytes. The manifest separately pins the corpus SHA-256, file byte count, decoded aggregate byte count, per-entry byte counts, and per-entry SHA-256 values.

## Corpus scope after review hardening

The first draft had one small entry per required category. Qodo correctly characterized that as category-complete smoke coverage rather than a representative tokenizer-economics corpus.

The hardened v0 corpus now contains **two entries for every required category**:

```text
PROFILE_1 = baseline
PROFILE_2 = adversarial
```

Categories:

```text
python
typescript
javascript
rust
go
java
c
cpp
sql
shell
json
yaml
toml
diff
stack_trace
file_paths
tool_json
```

Adversarial surfaces include Unicode and mixed scripts, long identifiers, regex/generics/macros/operators, heredocs and shell quoting, nested JSON, YAML anchors/multiline scalars, TOML arrays/timestamps, rename/binary diff markers, multiple runtime trace styles, Windows/UNC/deep/Unicode paths, and nested tool-result/error JSON.

The claim is intentionally bounded:

```text
CLAIM_SCOPE = DETERMINISTIC_STRATIFIED_V0_FIXTURE_NOT_A_POPULATION_REPRESENTATIVE_SAMPLE
```

B007 therefore freezes a small deterministic stratified comparison surface. It does not claim that 34 synthetic entries estimate population-wide code-tokenization behavior.

## Integrity contract

B007 now has task-local Draft 2020-12 schemas and an integrity test. The test is designed to fail closed on:

- duplicate JSON keys;
- corpus file SHA-256 mismatch;
- corpus file byte-count mismatch;
- Git blob identity mismatch;
- duplicate fixture IDs;
- missing baseline/adversarial profile for any required category;
- decoded entry byte-count mismatch;
- decoded entry SHA-256 mismatch;
- aggregate decoded-byte mismatch;
- manifest/corpus entry-pin mismatch;
- external-source-content drift;
- authority widening;
- special-token policy weakening;
- claim-scope widening.

The committed corpus file bytes and decoded entry hashes are authoritative. Re-serialization is not assumed equivalent unless every pinned identity matches.

## Measurement contract frozen for B008

B008 must tokenize the exact decoded Unicode strings without pre-measurement transformation:

```text
ADD_SPECIAL_TOKENS = FALSE
BOS_INJECTION = FALSE
EOS_INJECTION = FALSE
CHAT_TEMPLATE = PROHIBITED_AND_MUST_BE_ASSERTED_UNUSED
PADDING = NONE
TRUNCATION = NONE
WHITESPACE_NORMALIZATION = NONE
NEWLINE_NORMALIZATION = NONE
TOKENIZER_NATIVE_NORMALIZER = AS_PINNED_BY_TOKENIZER_REVISION
```

B008 output must record effective runtime settings and the actual token-count API identity, not merely intended configuration.

Tokenizer identity must include:

- exact tokenizer repository/id;
- immutable tokenizer revision;
- SHA-256 inventory of every tokenizer artifact actually loaded;
- tokenizer implementation identity/version/class;
- Python/runtime and tokenizer-library identity;
- executor identity;
- platform identity when behavior can differ;
- acquisition source/provenance.

## Required metrics

Corpus-level weighted metrics use numerator/denominator totals:

```text
WEIGHTED_BYTES_PER_TOKEN = SUM(byte_count) / SUM(token_count)
WEIGHTED_CHARACTERS_PER_TOKEN = SUM(character_count) / SUM(token_count)
ESTIMATED_EFFECTIVE_PAYLOAD_BYTES_AT_8192_TOKENS = FLOOR((SUM(byte_count) / SUM(token_count)) * 8192)
ZERO_TOTAL_TOKENS = INVALID_MEASUREMENT
```

The 8192-token value is explicitly a **corpus-ratio estimate**, not an exact model-context maximum.

Per-category totals are mandatory so language/config/diff/tool surfaces are not hidden inside one aggregate ratio.

Identifier fragmentation is deliberately named an **identifier-like lexical span** metric, not semantic identifier extraction:

```text
REGEX = [A-Za-z_][A-Za-z0-9_]*
COUNTING = OCCURRENCES_WITHOUT_DEDUPLICATION
ZERO_MATCH = COUNT_0_AND_NULL_RATIO_DISTRIBUTION_FIELDS
```

B008 must report mean, p50, p95, max, and multi-token fraction for isolated identifier-like spans and must record the token-piece API used.

Structural observations are separately required for diffs, file paths, stack traces, and tool JSON so tokenizer density results retain context about the measured surface.

## Review remediation

Qodo review of draft head `c086fdf29706ccaeb58809221ee90cfe7563eec9` identified two substantive gaps:

1. one tiny example per category was insufficient for a broad representativeness claim;
2. byte/hash invariants were documented but not enforced by a task-local schema/integrity test.

Both are addressed in the current branch design:

```text
ONE_ENTRY_PER_CATEGORY = REPLACED_BY_BASELINE_PLUS_ADVERSARIAL
REPRESENTATIVE_POPULATION_CLAIM = REMOVED
TASK_LOCAL_CORPUS_SCHEMA = ADDED
TASK_LOCAL_PROTOCOL_SCHEMA = ADDED
INTEGRITY_TEST = ADDED
EFFECTIVE_RUNTIME_SETTINGS_CAPTURE = REQUIRED
TOKENIZER_LOADED_ARTIFACT_HASH_INVENTORY = REQUIRED
IDENTIFIER_METRIC_SEMANTICS = NARROWED_AND_EXPLICIT
8192_PAYLOAD_FIELD = RENAMED_AS_ESTIMATE
STRUCTURAL_METRICS = ADDED
```

A fresh exact-head re-review is required after this evidence refresh.

## Validation state

The new task-local test file exists but has **not been executed on an exact full repository checkout in the available execution environment**. No result is inferred from code inspection.

```text
B007_TARGETED_TEST = NOT_RUN
pytest -q = NOT_RUN
ruff check src tests = NOT_RUN
mypy = NOT_RUN
python -m mstr_qualify validate = NOT_RUN
GITHUB_ACTIONS = NOT_CLAIMED
```

Per `configs/quality.toml`, B007 must not be marked `COMPLETE_CANONICAL` until the required repository quality gates have passed with evidence.

## Authority boundary

```text
MODEL_INFERENCE = NOT_AUTHORIZED
MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED
TOKENIZER_ARTIFACT_DOWNLOAD = NOT_AUTHORIZED_BY_B007
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
TOKENIZER_MEASUREMENT = NOT_EXECUTED_BY_B007
B008_EXECUTION_AUTHORITY = NOT_CREATED
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B007 remains unchecked and not canonical. B008 must not infer execution or acquisition authority from this protocol.
