# T027 — Weight-Access / Acquisition Preflight (Preparation Only)

**Task:** MSTR-000 / T027
**Branch:** task/000-t027-weight-access-preflight
**Canonical base:** `6b5ce9599e4985182113c98f53e8c9566f3b1864` (main after PR #29)
**Frozen manifest:** `artifacts/manifests/T027-weight-access.json` (`mstr.weight-access-manifest.v1`)
**Scope:** preflight only. NO weight bodies downloaded, NO execution, NO quantization, NO Colab, NO Unsloth, NO gated-term acceptance, NO paid access.

## 1. Exact canonical base

Live GitHub truth was re-verified before mutation: local HEAD == `origin/main == 6b5ce95…` (PR #29 merge, canonical state T023–T026 complete). No open PRs, no pending reviews, no CI runs (CI is deliberately absent per T011). A partial prior draft of the manifest schema existed locally on the task branch and was finalized in place.

## 2. T022 source decision

`artifacts/decisions/T022-static-candidate-admission.json` admits exactly eight records into the bounded weight-eligible set — five foundations (qwen3.5-2b, qwen3.5-4b, ministral-3-3b, granite-4.1-3b, smollm3-3b) and three controls (qwen3-4b architecture control; qwen2.5-coder-1.5b, yi-coder-1.5b code controls) — with mandatory license re-verification for Ministral-3-3B, Granite-4.1-3B, SmolLM3-3B. This set was NOT modified: the frozen manifest covers exactly these eight candidates (enforced by contract test against the T022 decision record).

## 3–4. Candidate-by-candidate preflight + live license re-verification

All eight pinned revisions were re-resolved live via metadata-only HTTPS GET to `https://huggingface.co/api/models/<id>/revision/<sha>?blobs=true` (no weight bodies; API + raw README text only). Every revision still resolves exactly; every repository reports `gated=false`, `private=false`.

| candidate | role | pinned revision | revision live | gated | license re-verification | outcome |
|---|---|---|---|---|---|---|
| qwen3.5-2b | foundation | `b1485b2f…52d7c` | ✅ exact | no | Apache-2.0 confirmed: tag + front matter + verbatim LICENSE file | READY_FOR_T028 |
| qwen3.5-4b | foundation | `1001bb4d…7b741b` | ✅ exact | no | same as above | READY_FOR_T028 |
| ministral-3-3b | foundation | `6f9c4b12…23735` | ✅ exact | no | **Re-verified**: tag `license:apache-2.0` + README front matter + explicit card statement "usage and modification for both commercial and non-commercial purposes". No standalone LICENSE file at this revision → notice satisfied by preserving README. `extra_gated_description` is a privacy disclosure only, not an access gate | READY_FOR_T028 |
| qwen3-4b | arch control | `906bfd4b…ff8539` | ✅ exact | no | Apache-2.0 confirmed (tag + front matter + LICENSE file) | READY_FOR_T028 |
| granite-4.1-3b | foundation | `dacb9cb9…05c96` | ✅ exact | no | **Re-verified**: tag + front matter + card body "License: Apache 2.0" linking apache.org. No standalone LICENSE file → README is the notice artifact | READY_FOR_T028 |
| smollm3-3b | foundation | `d78a42f7…c2b940` | ✅ exact | no | **Re-verified**: tag + front matter + dedicated card License section. No standalone LICENSE file → README is the notice artifact | READY_FOR_T028 |
| qwen2.5-coder-1.5b | coder control | `df3ce67c…eb73b` | ✅ exact | no | Apache-2.0 confirmed (tag + front matter + LICENSE file) | READY_FOR_T028 |
| yi-coder-1.5b | coder control | `00e59e64…e8109` | ✅ exact | no | **Re-verified**: tag `license:apache-2.0` + README front matter only; **no standalone LICENSE file** at this revision → README is the notice artifact, recorded as residual risk | READY_FOR_T028 |

Fail-closed discipline: rights were resolved from the exact pinned revision using two independent declaration surfaces (machine-readable HF tag AND repository README text), never from a badge alone or a related model's license. No candidate required rescue-by-interpretation; the three caveated candidates passed because their declarations are consistent across surfaces at the identical revision. Rights dimensions per candidate (personal/commercial use, modification, fine-tuning, quantization/conversion, derivative redistribution): all YES under Apache-2.0. No field-of-use restriction, no MAU/revenue threshold, no account requirement, no click-through, no separate commercial license, attribution/notice satisfied by Apache-2.0 §4 with README preservation where no standalone LICENSE exists. Yi-Coder-1.5B was found to share the missing-LICENSE-text situation of the three caveated candidates (caught during review of this PR) and is now recorded identically: tag + README declarations at the pinned revision, README-as-notice mitigation, explicit residual-risk entry. Tokenizer/processor components ship inside each pinned tree under the same declared license.

## 5–6. Acquisition file set + source/revision identity

Per candidate the manifest pins: exact model id, full 40-hex revision (schema-enforced pattern `^[0-9a-f]{40}$` — moving refs are structurally impossible), per-file list with exact byte sizes, and per-file upstream LFS OID SHA-256 for every weight file (`expected_file_integrity`). Redundant precision variants are excluded from acquisition without dropping any candidate:

- **smollm3-3b**: the upstream ONNX export suite (~32.6 GiB of redundant pre-quantized variants incl. `model_q4.onnx_data`) is excluded; only bf16 safetensors shards + metadata are acquired.
- **ministral-3-3b**: `consolidated.safetensors` (~7.17 GiB duplicate full-precision variant) is excluded; the sharded set bound by `model.safetensors.index.json` is authoritative.
- `.gitattributes` excluded everywhere; tiny optional files (`model.sig`, Qwen3.5 vision preprocessor configs) marked optional.

This trimming is justified against T022: each candidate remains complete in its canonical bf16 safetensors form; nothing that the qualification runtime would need is omitted.

## 7. Integrity plan

Every weight file carries an upstream SHA-256 (LFS OID) plus exact byte size captured from the provider at the pinned revision. T028 must hash-verify each download against this identity before emitting its artifact manifest, then verify offline through the T024 machinery (`mstr_qualify.artifacts.verify_artifact`, `mstr.artifact.v1` manifests). Mismatch quarantines the file and fails that candidate closed with EXCLUDED_ARTIFACT_UNRESOLVED; no silent retry-with-substitute.

## 8. Storage budget

Direct-to-final streaming downloads keep peak storage equal to final storage (temporary expected = 0; ceiling per candidate = its own download size).

| candidate | download = final bytes | GiB |
|---|---:|---:|
| qwen3.5-2b | 4,571,203,846 | 4.26 |
| qwen3.5-4b | 9,342,822,405 | 8.70 |
| ministral-3-3b | 7,732,479,067 | 7.20 |
| qwen3-4b | 8,056,519,973 | 7.50 |
| granite-4.1-3b | 6,815,474,820 | 6.35 |
| smollm3-3b | 6,167,852,190 | 5.74 |
| qwen2.5-coder-1.5b | 3,098,970,942 | 2.89 |
| yi-coder-1.5b | 2,957,617,051 | 2.75 |
| **TOTAL** | **48,742,940,294** | **45.40 GiB** |

Aggregate math is enforced by contract tests (sum-of-parts == aggregate; per-candidate budget == sum of declared file sizes).

## 9. Network allowlist proposal

```text
METHOD = HTTPS_GET_ONLY
ALLOWLIST_HOSTS   = huggingface.co, cdn-lfs.huggingface.co,
                    cdn-lfs-us-1.huggingface.co, cas-bridge.xethub.hf.co,
                    transfer.xethub.hf.co, transfer.xethub.hf.com
REDIRECT POLICY   = every documented redirect/CDN target is a member of the
                    allowlist (contract-tested subset), so an allowlist-enforcing
                    downloader can follow the full redirect chain
UNAUTHORIZED      = arbitrary browsing, package indexes (pypi/npm), provider inference APIs,
                    telemetry endpoints, unrelated CDNs, git protocol endpoints
```

No git-lfs clone; HTTPS range GETs only. T028 must pin observed redirect hosts in its own evidence.

## 10. Account / gating status

ALL EIGHT candidates: `authentication_required=false`, `account_required=false`, `gated_access=false`, `clickthrough_required=false`, `terms_acceptance_required=false`. Enforced by contract test — any true flag would require founder authorization before T028. No credentials, tokens, or session values exist anywhere in this branch.

## 11. Runtime / quantizer candidates (NOT selections)

Runtime candidates: llama.cpp-GGUF-class CPU runtime, llamafile-portable-class runner. Quantizer candidates: llama.cpp convert_hf_to_gguf + llama-quantize Q4-class recipe. Status on every candidate: `CANDIDATE_ONLY_NEEDS_T029_T030`. No CANONICAL_RUNTIME or FINAL_QUANTIZER claim appears anywhere (contract-tested).

Per constitution IV, runtime/quantizer dependency rights are recorded independently per candidate (`runtime_quantizer_license_notes`, schema-required): llama.cpp tooling identified as MIT and llamafile as Apache-2.0 project-licensed (only its llama.cpp and whisper.cpp derived components are MIT), both with unrestricted commercial use as a *preliminary* record, with binding evaluation explicitly deferred to T029/T030 when exact builds are pinned.

## 12–13. Retention / cleanup / cost

Retention: artifacts persist in the external acquisition directory through T028→T034; post-T034 rejects are deletable on founder approval. Cleanup: partial/integrity-failed downloads deleted immediately; verified artifacts immutable. Cache: no provider cache population. Location: binaries under gitignored `artifacts/external/<candidate_id>/`; only manifests/hashes/evidence enter Git. Git exclusion verified against existing `.gitignore` coverage (`*.safetensors`, `*.gguf`, `models/`, `artifacts/external/`, …); T028 must assert zero untracked weight files post-acquisition. Cost: `EXPECTED_ACQUISITION_COST = USD 0.00`; any payment requirement aborts with PAID_ACCESS_REQUIRES_NEW_FOUNDER_DECISION.

## 14. Exclusions preserved

Qwen2.5-Coder-3B remains REFERENCE_ONLY (research license fails closed); AFM-4.5B-Base remains REFERENCE_ONLY (post-trained SFT+RL artifact); comparison-* points remain out of foundation admission. None enter the T028 authority surface. No evidence was rewritten; supersession would go through T007 if upstream terms ever change.

## 15. Unresolved risks

1. Four candidates (Ministral-3-3B, Granite-4.1-3B, SmolLM3-3B, Yi-Coder-1.5B) lack a standalone LICENSE text file at their pinned revisions; rights rest on consistent tag+README declarations (documented above). Mitigation: preserve README as notice artifact; re-check before redistribution.
2. Aggregate 45.4 GiB may exceed a founder-approved comfort zone; the manifest explicitly permits a bounded subset authorization at T028 without editing candidate entries.
3. Qwen3.5 vision-encoder weights ship inside shared shards; text-only serving validation defers to T030.
4. CDN redirect hosts may evolve upstream; T028 must pin observed redirects.

## 16. Proposed T028 authority envelope

T028 stays blocked until separate explicit founder authorization naming `T027-weight-access-preflight-frozen` and the approved subset. Authorized scope: stream-download exactly the listed files over the allowlist, SHA-256-verify, emit `artifacts/manifests/T028-acquired-artifacts.json` + `evidence/T028-weight-acquisition.md`. Prohibited: execution, quantization, Unsloth/Colab, unlisted revisions, granting backbone/finalist/local_qualified status. Completing T028 opens nothing automatically.

## Gates on exact head

```text
pytest -q                        → 342 passed (was 302; +40 T027 contract/fixture tests incl. review-driven hardening)
ruff check src tests             → All checks passed!
mypy                             → Success: no issues found in 19 source files
python -m mstr_qualify validate  → exit 0; 5 schemas checked; 5 valid fixtures passed; 5 invalid rejected
manifest schema validation       → PASS (offline CLI also validates artifacts/manifests/T027-weight-access.json)
```

## Result candidate

```text
T027_RESULT = COMPLETE_CANONICAL_PENDING_REVIEW
ACTIVE_TASK_AFTER_MERGE = NONE
NEXT_TASK = T028_EXPLICIT_WEIGHT_ACCESS_GATE
MODEL_WEIGHT_ACCESS = NOT_YET_AUTHORIZED
```
