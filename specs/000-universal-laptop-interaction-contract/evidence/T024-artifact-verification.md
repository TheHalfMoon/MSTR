# T024 — Artifact Manifest / Hash Verification

**Task:** MSTR-000 / T024 [P] [US1]
**Branch:** task/000-t024-artifact-verification
**Canonical base:** main `fece0f3382ce383ca8e68dd875b48a46d4cc7fba` (T023 canonical merge, verified live before branching)
**Scope:** verification of manifests/files supplied locally. No weight fetching, no network, no model access.

## Delivered

```text
src/mstr_qualify/artifacts.py            manifest parsing + fail-closed integrity verification
tests/unit/test_artifacts.py             30 tests
tests/fixtures/artifacts/valid/          manifest.json + alpha.txt + nested/beta.bin (real hashed bytes)
```

## Behavior contract

| Requirement | Implementation |
|---|---|
| Exact artifact identity | `ArtifactManifest` = artifact_id + format_name + deterministic sorted file set; every entry carries a canonical lowercase-hex SHA-256 (`ids.validate_sha256`). |
| SHA-256 verification | Streaming `sha256_file` per declared file; mismatch raises `artifact.hash_mismatch`. |
| Size verification | Enforced only where the manifest declares `size_bytes`; undeclared sizes are still reported from actual stat. |
| Deterministic file-set handling | Entries verified in sorted path order; on-disk discovery sorts directories/files so behavior is OS-independent. |
| Missing-file failure | `artifact.missing_file` (also covers non-regular files). |
| Unexpected-file handling | Strict completeness: any extra on-disk file → `artifact.unexpected_file` with count + sample paths. |
| Malformed manifest failure | Invalid JSON / wrong root type / wrong `schema_version` / missing fields / wrong field types each get distinct fail-closed codes. |
| Path traversal protection | Two independent layers: load-time validation (absolute paths, `..`, leading `./`, backslashes/NUL, empty components) and verify-time resolution check that the resolved file stays inside the root (`artifact.path_escape`). |
| Symlink behavior explicitly defined | Symlinks are rejected outright, never followed: declared-file symlink → `artifact.symlink_rejected`; symlinked files discovered in the tree also rejected; resolution escape via directory symlinks caught by the escape layer. |
| Duplicate identity failure | Duplicate entry paths rejected at both parse time and dataclass construction (`artifact.duplicate_entry`). |
| Fail-closed mismatch semantics | Any failure raises `ArtifactIntegrityError`; there is no code path that normalizes a bad artifact into PASS. |

## What this task does NOT do

No fetching of weights or any remote content; `verify_artifact` reads only local storage under a caller-provided root. No CLI command added (not required by T024 scope).

## Evidence of quality gates (exact head)

```text
pytest -q                      -> 235 passed   (205 after T023 fixes + 30 new)
ruff check src tests           -> All checks passed!
mypy (strict)                  -> Success: no issues found in 15 source files
python -m mstr_qualify validate -> exit 0
```

CI note: repository deliberately has no GitHub Actions workflows (`configs/quality.toml`: `ci_workflows_added = false`). Gates were run locally on the exact head; no CI claim is made.

## Authority / safety

```text
MODEL_WEIGHT_ACCESS       = NONE
MODEL_ARTIFACT_DOWNLOAD   = NONE
NETWORK                   = NONE
PAID_COMPUTE              = NONE
TRAINING                  = NONE
```

## Result

```text
T024_RESULT = COMPLETE_CANONICAL_PENDING_REVIEW
NEXT_TASKS  = T025/T026 [P] then T027 preflight
```
