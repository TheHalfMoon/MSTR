# A002 — Run Event v0 Contract Frozen

**Task:** MSTR-000A / A002
**Schema:** `schemas/mstr-run-event-v0.schema.json` (registered, byte-identical design source in both spec packages)

## Result

The typed append-oriented run-event vocabulary and canonical serialization/hash rules are frozen:

- Every event carries a mandatory non-null SHA-256 (`sha256`, pattern `^[a-f0-9]{64}$`)
- Predecessor binding via `prev_event_sha256` (null only for seq=0)
- Sequence numbers must be contiguous within a run
- Replay MUST reject missing hashes, duplicates, gaps, reordered/substituted events, and broken predecessor chains
- Event types cover: run lifecycle, context observation/compaction, plan updates, tool request/result, edit proposal/result, verification, recovery, escalation, and terminal states

## Fixtures

- Valid: 1 instance with all identity fields populated
- Invalid: 6 fail-closed mutations (wrong schema_version, null sha256, short sha256, negative seq, unknown event_type, empty run_id)
