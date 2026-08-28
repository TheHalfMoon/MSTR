# B007 — Tokenizer Economics Corpus / Protocol

**Workstream:** MSTR-000B
**Task:** B007
**State:** COMPLETE_CANONICAL
**Implementation PR:** `#59`
**Final implementation head:** `965fbdbf152272397ae6ef721260e806be5d251c`
**Canonical implementation merge:** `b9b0a8ca7b9b7528f5da518baa83b23e2348c6f6`
**Canonical main at execution:** `9b4e885f215fd922ecf79ff9e15bdb1479396668`
**Protocol:** `MSTR-TOKENIZER-ECONOMICS-v0`

B007 freezes deterministic corpus bytes and tokenizer-measurement semantics only. It does not acquire or execute a tokenizer, run model inference, access model weights, use paid compute, ingest a large dataset, or authorize B008 execution.

## Current execution binding

Production exact-main entry run `33147997037` (job `98773224654`) proved B007 `eligible=true`, observed state `PENDING`, and clean canonical drift on `9b4e885f215fd922ecf79ff9e15bdb1479396668` immediately before fresh material branch creation.

The seven-file protocol/corpus package was imported from historical donor head `6f9161632e327b0048ec68bf79627c0e69ba1c60` only as source material. No donor review result, validation result, merge-readiness state, or canonical-state claim is inherited by this execution.

## Exact corpus identity

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
```

The compact UTF-8 serializer used for the committed corpus independently reproduces exactly `10951` bytes, the SHA-256 above, and Git object identity `af4cf20b...`. Each decoded `content_utf8` entry also carries its own byte count and SHA-256.

## Stratified bounded corpus

The first draft used one small fixture per required category. Review correctly classified that as category-complete smoke coverage rather than representative tokenizer economics.

The current corpus has exactly two fixtures for each of the 17 required categories:

```text
PROFILES = baseline + adversarial
CATEGORIES = python, typescript, javascript, rust, go, java, c, cpp,
             sql, shell, json, yaml, toml, diff, stack_trace,
             file_paths, tool_json
CLAIM_SCOPE = DETERMINISTIC_STRATIFIED_V0_FIXTURE_NOT_A_POPULATION_REPRESENTATIVE_SAMPLE
```

Adversarial surfaces include mixed-script Unicode, long identifiers, regex/generics/macros/operators, shell heredoc/quoting, nested JSON, YAML anchors and multiline scalars, TOML arrays/timestamps, rename/binary diff markers, multiple runtime trace styles, Windows/UNC/Unicode paths, and nested tool errors.

B007 therefore freezes a small deterministic comparison surface; it makes no population-wide representativeness claim.

## Current contract and test identities

```text
MANIFEST_BLOB = abc7e7216f3aa7ad2c4c46bbc57d97ddd4e82968
CORPUS_SCHEMA_BLOB = f11394e87d6d569feb58616dc8b7a90dbbd2d549
PROTOCOL_SCHEMA_BLOB = 821306ce86c67a1030dbef0ee9b483192632b1ec
BASE_INTEGRITY_TEST_BLOB = c68302f6d34f97263861b4119d59808c54bcede1
NESTED_FAIL_CLOSED_TEST_BLOB = 70898568cab23c502431cddf221c50aaf6a90157
```

Task-local schemas use JSON Schema Draft 2020-12. They do not register a shared runtime schema or create a new external-effect surface.

## Integrity enforcement

The B007 test sources are designed to fail closed on:

- duplicate JSON keys;
- corpus file SHA-256, byte-count, or Git-blob mismatch;
- duplicate fixture IDs;
- category/profile drift;
- decoded entry byte-count or SHA-256 mismatch;
- aggregate decoded-byte mismatch;
- manifest/corpus entry-pin mismatch;
- external-source-content drift;
- population-representative claim widening;
- special-token policy weakening;
- model/tokenizer authority widening.

After Qodo identified that the initial protocol schema left several nested surfaces too generic, the protocol schema was hardened so these are no longer open objects:

```text
TOKENIZER_IDENTITY = FAIL_CLOSED
COMPARABILITY = FAIL_CLOSED
CATEGORY_SUMMARY_ITEM_SHAPE = FAIL_CLOSED
ENTRY_PIN_ITEM_SHAPE = FAIL_CLOSED
STRUCTURAL_OBSERVATION_DEFINITIONS = FAIL_CLOSED
B008_OUTPUT_REQUIREMENTS = FROZEN
ENCODING_CONTRACT = FAIL_CLOSED
AUTHORITY_FALSE_FLAGS = FROZEN
```

Dedicated negative tests now mutate each of those nested surfaces and require schema rejection.

## B008 measurement semantics frozen

B008 must tokenize the exact decoded Unicode strings with:

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

Every measurement must capture effective runtime settings and token-count API identity, plus:

- exact tokenizer repository/id;
- immutable tokenizer revision;
- SHA-256 inventory for every tokenizer artifact actually loaded;
- tokenizer implementation identity/version/class;
- Python and tokenizer-library identity/version;
- executor identity;
- platform identity where behavior can differ;
- acquisition source/provenance.

## Metrics

Weighted totals are frozen as:

```text
WEIGHTED_BYTES_PER_TOKEN = SUM(byte_count) / SUM(token_count)
WEIGHTED_CHARACTERS_PER_TOKEN = SUM(character_count) / SUM(token_count)
ESTIMATED_EFFECTIVE_PAYLOAD_BYTES_AT_8192_TOKENS = FLOOR((SUM(byte_count) / SUM(token_count)) * 8192)
ZERO_TOTAL_TOKENS = INVALID_MEASUREMENT
```

The 8192-token field is a corpus-ratio estimate, not an exact model context maximum. Numerator/denominator totals and per-category totals must be retained.

Identifier fragmentation is explicitly a lexical approximation:

```text
REGEX = [A-Za-z_][A-Za-z0-9_]*
SEMANTICS = IDENTIFIER-LIKE ASCII LEXICAL SPANS, NOT LANGUAGE-AWARE IDENTIFIERS
COUNTING = OCCURRENCES WITHOUT DEDUPLICATION
ZERO_MATCH = COUNT 0 + NULL RATIO/DISTRIBUTION FIELDS
```

Mean, p50, p95, max, and multi-token fraction are required. Structural observations are separately required for diff, paths, stack traces, and tool JSON.

## Donor review history (historical, non-authoritative)

Qodo review at `c086fdf29706ccaeb58809221ee90cfe7563eec9` found:

1. under-stratified/category-only coverage;
2. documented-only integrity enforcement.

Both were explicitly closed by Qodo on re-review of `e47700a1043cd2f025fe66d1a91e45e748410c74`.

That re-review found one new material defect: nested protocol sections were insufficiently constrained. The current protocol schema and `test_b007_protocol_fail_closed.py` address that defect. A fresh exact-current-head review is required before treating review as clean.

## Current validation truth

Fresh validation was executed on the current canonical-main-derived B007 worktree. Historical donor validation and review results are not current authority.

```text
ENTRY_ELIGIBILITY_RUN = 33147997037
ENTRY_ELIGIBILITY_JOB = 98773224654
BUILDER_RUN = 33148397634
CANONICAL_MAIN = 9b4e885f215fd922ecf79ff9e15bdb1479396668
DONOR_HEAD_SOURCE_ONLY = 6f9161632e327b0048ec68bf79627c0e69ba1c60
B007_TARGETED_TESTS = 14 passed in 0.59s
FULL_PYTEST = 519 passed in 23.16s
RUFF = PASS
MYPY = PASS / 26 source files
VALIDATE = PASS / 10 valid / 10 invalid rejected
```

Exact-head qualification run `33148508447` (job `98774836633`) and independent adversarial review run `33148717463` (job `98775495939`) both passed on final implementation head `965fbdbf152272397ae6ef721260e806be5d251c` before merge. Post-implementation verification run `33148856216` (job `98775927107`) then passed on canonical main `b9b0a8ca7b9b7528f5da518baa83b23e2348c6f6`.

## Canonical closeout evidence

B007 becomes canonical only after the frozen corpus/protocol package was exact-head qualified, independently reviewed, merged with expected-head protection, and re-verified on canonical main. The task catalog now requires both the protocol manifest and the pinned corpus bytes before B008 can satisfy its B007 prerequisite.

```text
ENTRY_RUN = 33147997037
ENTRY_JOB = 98773224654
IMPLEMENTATION_BUILDER_RUN = 33148397634
IMPLEMENTATION_BUILDER_JOB = 98774487926
IMPLEMENTATION_PR = #59
FINAL_IMPLEMENTATION_HEAD = 965fbdbf152272397ae6ef721260e806be5d251c
CANONICAL_IMPLEMENTATION_MERGE = b9b0a8ca7b9b7528f5da518baa83b23e2348c6f6
EXACT_HEAD_QUALIFICATION_RUN = 33148508447
EXACT_HEAD_QUALIFICATION_JOB = 98774836633
INDEPENDENT_REVIEW_RUN = 33148717463
INDEPENDENT_REVIEW_JOB = 98775495939
POST_IMPLEMENTATION_VERIFY_RUN = 33148856216
POST_IMPLEMENTATION_VERIFY_JOB = 98775927107
POST_IMPLEMENTATION_MAIN = b9b0a8ca7b9b7528f5da518baa83b23e2348c6f6
POST_IMPLEMENTATION_B007_ELIGIBLE = true
POST_IMPLEMENTATION_B008_ELIGIBLE = false
POST_IMPLEMENTATION_B008_REASON = prerequisite.unsatisfied:B007
POST_IMPLEMENTATION_DRIFT = clean
ENTRY_GATE_TASK = B007
ENTRY_GATE_CANONICAL_MAIN = 9b4e885f215fd922ecf79ff9e15bdb1479396668
ENTRY_GATE_ELIGIBLE = true
CLOSEOUT_BUILDER_RUN = 33150163308
CLOSEOUT_TARGETED_GOVERNANCE = TBD
CLOSEOUT_FULL_PYTEST = TBD
CLOSEOUT_RUFF = PASS
CLOSEOUT_MYPY = PASS / 26 source files
CLOSEOUT_VALIDATE = PASS / 10 valid / 10 invalid rejected
```

The corpus manifest and exact corpus fixture are both required closeout outputs. Deleting either must fail B008 closed. B008 eligibility after this state transition is only machine scheduling eligibility; it is not tokenizer acquisition or measurement authority.

## Authority boundary

```text
MODEL_INFERENCE = NOT_AUTHORIZED
MODEL_WEIGHT_ACCESS = NOT_AUTHORIZED
TOKENIZER_ARTIFACT_DOWNLOAD = NOT_AUTHORIZED_BY_B007
TOKENIZER_MEASUREMENT = NOT_EXECUTED_BY_B007
PAID_COMPUTE = NOT_AUTHORIZED
LARGE_DATASET_INGESTION = NOT_AUTHORIZED
B008_EXECUTION_AUTHORITY = NOT_CREATED
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

This separate closeout canonicalizes B007 only after implementation merge and exact-main post-implementation verification. It does not create tokenizer acquisition/measurement, model access/execution, compute, training, or B008 external authority.
