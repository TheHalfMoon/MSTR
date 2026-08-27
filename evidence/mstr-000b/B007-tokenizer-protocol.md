# B007 — Tokenizer Economics Corpus / Protocol

**Workstream:** MSTR-000B  
**Task:** B007  
**State:** IMPLEMENTATION_COMPLETE_ON_BRANCH / NOT_COMPLETE_CANONICAL  
**Canonical main at execution:** `ead69ae26265b133c782ae8fd2795c126253a3b6`  
**Protocol:** `MSTR-TOKENIZER-ECONOMICS-v0`

B007 freezes corpus bytes and measurement semantics only. It does not acquire a tokenizer, run model inference, access model weights, use paid compute, or authorize B008 execution.

## Outputs

```text
MANIFEST = benchmarks/manifests/B007-tokenizer-economics.json
MANIFEST_GIT_BLOB = ded18f8672a9a6ffab8d0da46ad880b73c4deebe

CORPUS = benchmarks/fixtures/tokenizer-economics/B007-corpus.json
CORPUS_GIT_BLOB = c29d7cca25ea581daf1dc33bf23b8802bdbdda76
CORPUS_FILE_SHA256 = bf7cf5f12d43910863ceb03667972f5dfa2581285aae6ed70a608f5533257f7c
CORPUS_FILE_BYTES = 8130
DECODED_CONTENT_BYTES = 3617
ENTRY_COUNT = 17
```

## Corpus provenance

The corpus is repository-authored synthetic fixture content created specifically for tokenizer-economics measurement. It contains no copied external source content.

```text
SOURCE_CLASS = REPOSITORY_AUTHORED_SYNTHETIC_FIXTURE
EXTERNAL_SOURCE_CONTENT = NO
ENCODING = UTF-8
NEWLINE = LF
PRE_TOKENIZATION_CONTENT_TRANSFORMATION = NONE
```

The required surfaces are all present:

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

This covers the B007 task minimum: Python, TypeScript/JavaScript, Rust, Go, Java, C/C++, SQL, shell, JSON/YAML/TOML, diffs, stack traces, file paths, and tool JSON.

## Byte and source-hash pinning

Each decoded fixture entry records its exact UTF-8 byte count and SHA-256. The aggregate decoded byte count is the sum of those pinned entry counts.

```text
python       213  59311de128f93bade6d17cfa8eb09fda5595f016b692d3a51b73bfc1be913c19
typescript   300  f32f8ae7926462aab901e6b9ce08486744b1bc7bf6159f137435969280723a33
javascript   246  6fcb751859d709e0aa825eaad4fd916836fba3f119663f31a2bd2fd7a76dc841
rust         218  6836d0527bcef155f7100182ca9973b6b9aaba2361e7c775aa85a88a5af0e7e2
go           191  4b8e768e97c44fe6a72da8fc2669a57db987f8d073129d06535fcd7d4d7e4838
java         268  8d975b70a8257c926bf8f0007001d15c5b1cea406077df45dd8281e2461cf8ba
c            229  3229a2e4d715ff02399a760076e8a58343c911041be89977956e7b4a64510e40
cpp          271  784ed873ef9d60bfff4589e46bee14fe831a29e555746a581e797a333dd8206b
sql          179  1951366e3be5075147295c7f5b89e1080fe44f612942ddb39790db54ffd49fe1
shell        157  ea9d37c88e0780b1b4af8c01c723b666056990e65c8c1537e2e77d44c7919ad1
json         108  5d70692e6251737b9c000b257328f8e1714158ce20496fbf983fc587d0d4fe7a
yaml         110  ca12c345556a851d9dea5a6bb89382c3766e0981bdef74ff3b7add4c5590fbdc
toml         118  2d371fae55e4eecd820c274e9ba9db1a24f77234e6fc9df34a86973ce68e0de5
diff         277  559e35d7a2dbb5cffb2b5cf477ff5518b8452f4971b2956612fdb0823a0a4a06
stack_trace  329  c4ce75639ee025a0081ca6e43b86b2860415b7f0de1853e43719e8a02a8578cb
file_paths   247  c470c5ea5ba8724c16c3a2ee40f2613bef3b6e5cc353d64033119f93de3065fe
tool_json    156  068fcdb1bb4d65a0df110717cb7fff1117841d926065b01eca6bc90dca92fc97
```

### Exact committed-byte proof

Before commit, the corpus serializer produced:

```text
FILE_BYTES = 8130
FILE_SHA256 = bf7cf5f12d43910863ceb03667972f5dfa2581285aae6ed70a608f5533257f7c
EXPECTED_GIT_BLOB_SHA1 = c29d7cca25ea581daf1dc33bf23b8802bdbdda76
```

GitHub reports the committed corpus blob as exactly:

```text
ACTUAL_GIT_BLOB_SHA1 = c29d7cca25ea581daf1dc33bf23b8802bdbdda76
```

Therefore the committed file is byte-identical to the bytes for which the SHA-256 and entry hashes above were calculated.

## Measurement contract frozen for B008

B008 must verify corpus integrity before tokenization and then use the exact decoded Unicode text with no pre-measurement transformation.

```text
ADD_SPECIAL_TOKENS = FALSE
BOS_INJECTION = FALSE
EOS_INJECTION = FALSE
CHAT_TEMPLATE = PROHIBITED
PADDING = NONE
TRUNCATION = NONE
WHITESPACE_NORMALIZATION = NONE
NEWLINE_NORMALIZATION = NONE
TOKENIZER_NATIVE_NORMALIZER = AS_PINNED_BY_TOKENIZER_REVISION
```

Every candidate measurement must bind exact tokenizer repository/id, immutable tokenizer revision, tokenizer-file hashes where available, tokenizer implementation identity, and implementation version.

## Required metrics

Per entry:

```text
byte_count
token_count
bytes_per_token
character_count
characters_per_token
identifier_count
identifier_token_count
mean_tokens_per_identifier
multi_token_identifier_fraction
```

Identifiers use the frozen ASCII software-identifier regex:

```text
[A-Za-z_][A-Za-z0-9_]*
```

Each identifier is encoded in isolation with `add_special_tokens=false` for the identifier-fragmentation surface.

Aggregate metrics use weighted totals, never an unweighted average of per-file ratios:

```text
WEIGHTED_BYTES_PER_TOKEN = SUM(byte_count) / SUM(token_count)
EFFECTIVE_PAYLOAD_BYTES_AT_8K = FLOOR(WEIGHTED_BYTES_PER_TOKEN * 8192)
```

Named surfaces must also report exact token counts for:

```text
DIFF = fixture_id: diff
STACKTRACE = fixture_id: stack_trace
TOOL_JSON = fixture_id: tool_json
PATHS = fixture_id: file_paths
```

## Direct-comparison validity

A B008 result is invalid for direct comparison when any of the following differs or is unresolved:

- protocol identity;
- corpus file SHA-256;
- entry hashes;
- special-token policy;
- aggregation formula;
- tokenizer immutable revision;
- tokenizer implementation identity/version.

Candidate tokenizer revisions are expected to differ; the measurement protocol and corpus may not.

## Authority boundary

```text
MODEL_INFERENCE = NOT_AUTHORIZED
MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
TOKENIZER_MEASUREMENT = NOT_EXECUTED_BY_B007
B008_EXECUTION_AUTHORITY = NOT_CREATED
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

B007 is not marked `COMPLETE_CANONICAL` by this branch. Canonical closeout still requires governed review and the repository quality-gate policy; no CI or full-suite PASS is inferred here.
