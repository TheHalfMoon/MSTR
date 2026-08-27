from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: b005_closeout_apply.py <repo-root>")

    root = Path(sys.argv[1]).resolve()
    catalog_path = root / "configs/task-gate/mstr-000b.json"
    tasks_path = root / "specs/002-code-model-supremacy-foundation/tasks.md"
    evidence_path = root / "evidence/mstr-000b/B005-code-backbone-rescan.md"

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert catalog["tasks"]["B005"]["canonical_state"] == "PENDING"
    assert catalog["tasks"]["B006"]["canonical_state"] == "PENDING"
    assert catalog["tasks"]["B006"]["prerequisites"] == ["B005"]
    catalog["tasks"]["B005"]["canonical_state"] = "COMPLETE_CANONICAL"
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tasks = tasks_path.read_text(encoding="utf-8")
    old_start = "- [ ] **B005 Run mission-aligned compact backbone metadata rescan.**"
    new_start = "- [x] **B005 Run mission-aligned compact backbone metadata rescan.**"
    assert tasks.count(old_start) == 1
    assert tasks.count(new_start) == 0
    tasks = tasks.replace(old_start, new_start, 1)
    b006_marker = "\n\n- [ ] **B006 Create/reconcile candidate records for newly relevant code-specialized models.**"
    assert tasks.count(b006_marker) == 1
    before_b006, after_b006 = tasks.split(b006_marker, 1)
    canonical_line = (
        "  Canonical implementation: PR #54 / final head "
        "`0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a` / merge "
        "`1e096f4d1f270b2803da6a6306e9e7f0cf8fb81b`."
    )
    assert canonical_line not in before_b006
    before_b006 = before_b006.rstrip() + "\n" + canonical_line + "\n"
    tasks_path.write_text(before_b006 + b006_marker + after_b006, encoding="utf-8")

    evidence = evidence_path.read_text(encoding="utf-8")
    old_state = "**State:** IMPLEMENTATION_COMPLETE / NOT_COMPLETE_CANONICAL"
    assert old_state in evidence
    evidence = evidence.replace(old_state, "**State:** COMPLETE_CANONICAL", 1)
    marker = "## Closeout state\n"
    assert evidence.count(marker) == 1
    prefix = evidence.split(marker, 1)[0]
    closeout = """## Closeout state

B005 is prospectively marked `COMPLETE_CANONICAL` by this closeout branch only after the metadata-only implementation was independently reviewed, merged, and verified on canonical `main`. The marker becomes canonical only if this exact closeout head is qualified, reviewed, and merged with an expected-head guard. Post-closeout verification must then prove B005 terminal, B006 `eligible=true`, canonical drift clean, and all frozen gates green before B006 material mutation begins.

### Canonical implementation identity

```text
HISTORICAL_IMPLEMENTATION_PR = #41 / retained as non-canonical historical evidence
REFRESH_ENTRY_CANONICAL_MAIN = 986b174b2bf79ce53a3e67b9b02c55cbe6981303
REFRESH_ENTRY_GATE_RUN = 33103275261
REFRESH_ENTRY_GATE_JOB = 98626338825
FINAL_IMPLEMENTATION_PR = #54
FINAL_IMPLEMENTATION_HEAD = 0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a
IMPLEMENTATION_MERGE = 1e096f4d1f270b2803da6a6306e9e7f0cf8fb81b
```

### Exact qualification and review evidence

```text
REFRESH_QUALIFICATION_RUN = 33104689614
REFRESH_QUALIFICATION_JOB = 98631243460
REFRESH_DISCOVERY_ROWS = 19
REFRESH_PYTEST = 500 passed
REFRESH_RUFF = PASS
REFRESH_MYPY = PASS / 26 source files
REFRESH_VALIDATE = PASS / 10 valid / 10 invalid rejected

REVIEW_REPAIR_RUN = 33105382922
REVIEW_REPAIR_JOB = 98633709499
REVIEW_REPAIR_HEAD = 0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a
REVIEW_REPAIR_SEMANTICS = PASS
REVIEW_REPAIR_PYTEST = 500 passed
REVIEW_REPAIR_RUFF = PASS
REVIEW_REPAIR_MYPY = PASS / 26 source files
REVIEW_REPAIR_VALIDATE = PASS / 10 valid / 10 invalid rejected

FINAL_PREMERGE_RUN = 33105612342
FINAL_PREMERGE_JOB = 98634521533
FINAL_PREMERGE_HEAD = 0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a
FINAL_PREMERGE_B005_ELIGIBLE = true
FINAL_PREMERGE_DRIFT = clean
FINAL_PREMERGE_CHANGED_FILES = 4 exact B005 implementation surfaces
FINAL_PREMERGE_PYTEST = 500 passed
FINAL_PREMERGE_RUFF = PASS
FINAL_PREMERGE_MYPY = PASS / 26 source files
FINAL_PREMERGE_VALIDATE = PASS / 10 valid / 10 invalid rejected
FINAL_REVIEW = QODO_NO_FURTHER_REVIEW_FINDINGS_ON_EXACT_REPAIRED_HEAD
FINAL_REVIEW_THREADS = RESOLVED
```

Qodo's initial exact-head review found one material correctness issue: CodeGemma and LFM2.5-2.6B retained stale unresolved/pinning or revision-drift semantics after exact revision identity became known. Exact repaired head `0a7ee7e392d827fb08c8cc9f3b2d9ec45c8cca1a` removed those contradictions, preserved CodeGemma's manual access gate without accepting terms, and kept BitNet as the actual upstream revision-drift row. Fresh Qodo review of the repaired head explicitly reported no further review findings.

### Post-implementation-merge canonical verification

```text
POST_MERGE_CANONICAL_MAIN = 1e096f4d1f270b2803da6a6306e9e7f0cf8fb81b
POST_MERGE_RUN = 33106252706
POST_MERGE_JOB = 98636776061
POST_MERGE_B005_ELIGIBLE = true / expected pre-closeout
POST_MERGE_B005_STATE = PENDING / expected pre-closeout
POST_MERGE_CANONICAL_DRIFT = clean / 34 tasks
POST_MERGE_OUTPUTS = PASS
POST_MERGE_AUTHORITY_BOUNDARY = PASS
POST_MERGE_PYTEST = 500 passed in 16.81s
POST_MERGE_RUFF = PASS
POST_MERGE_MYPY = PASS / 26 source files
POST_MERGE_VALIDATE = PASS / 10 valid / 10 invalid rejected
POST_MERGE_FINAL_MAIN_IMMUTABLE = PASS
```

### Authority boundary

```text
PUBLIC_METADATA_ONLY = YES
MODEL_WEIGHT_ACCESS = NONE
MODEL_FILE_RESOLVE_OR_DOWNLOAD = NONE
TOKENIZER_ARTIFACT_DOWNLOAD = NONE
MODEL_EXECUTION = NONE
GATED_TERMS_ACCEPTANCE = NONE
PAID_MODEL_API_EXECUTION = NONE
PAID_COMPUTE = NONE
RENTED_COMPUTE = NONE
LARGE_DATASET_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LONG_TRAINING = NONE
LARGE_SCALE_RL = NONE
PRODUCTION_RELEASE = NONE
NEW_AUTHORITY_CREATED = NO
FOUNDER_MACHINE_LARGE_ARTIFACTS = ZERO
```

```text
B005_IMPLEMENTATION = MERGED_AND_POST_MERGE_VERIFIED
B005_CLOSEOUT_STATE = PROSPECTIVE_COMPLETE_CANONICAL_UNTIL_CLOSEOUT_MERGE
B005_COMPLETE_CANONICAL = ONLY_AFTER_CLOSEOUT_MERGE_AND_POST_CLOSEOUT_PROOF
B006_STATE = PENDING
NEXT_DEPENDENT_TASK = B006_AFTER_PRODUCTION_ELIGIBLE_TRUE
```
"""
    evidence_path.write_text(prefix + closeout, encoding="utf-8")

    print("B005_CLOSEOUT_TRANSITION=APPLIED")


if __name__ == "__main__":
    main()
