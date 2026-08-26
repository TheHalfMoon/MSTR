# A003 — Event Log + Deterministic Replay

**Task:** MSTR-000A / A003
**Module:** `src/mstr_qualify/harness/event_log.py`

## Result

The append-oriented event log is implemented with full integrity verification:

- **Canonical hashing**: SHA-256 over the event's canonical UTF-8 serialization (sha256 + prev_event_sha256 fields removed, keys sorted, compact separators, ensure_ascii=True).
- **Predecessor chain**: `prev_event_sha256` binds each event to its immediate predecessor; seq=0 uses the all-zeros sentinel.
- **Replay validation**: rejects missing hashes, duplicate sequences, gaps, reordered events, substituted hashes, and broken predecessor chains.
- **Model-visible reconstruction**: `model_visible_history()` extracts only the subset visible to the model.

## Tests

14 unit tests covering: schema compliance, hash determinism, genesis sentinel, chain links, model-visible filtering, clean replay, missing-hash failure, substituted-hash failure, gap detection, duplicate detection, reordering detection, predecessor-chain breakage, and append-to-empty/append-chain behavior.

All 372 repository tests pass; ruff/mypy/validate clean.
