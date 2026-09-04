from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path.cwd()
B010_PATH = ROOT / "artifacts/manifests/B010-new-candidate-weight-access.json"
AUTH_PATH = ROOT / "artifacts/authorities/B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED.json"
CATALOG_PATH = ROOT / "configs/task-gate/mstr-000b.json"
TASK_GATE_TEST = ROOT / "tests/contract/test_task_gate.py"
CONVERGENCE_TEST = ROOT / "tests/contract/test_convergence_external_bindings.py"

EXPECTED_CANDIDATES = ["mellum-4b", "qwen3.5-0.8b-control"]
EXPECTED_AUTHORITY_ID = "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"
EXPECTED_DECISION = "FOUNDER_B011_MODEL_WEIGHT_ACCESS_DECISION=AUTHORIZE_EXACT_B010_ENVELOPE"
EXPECTED_ISSUE = 153
EXPECTED_COMMENT_ID = 5538049681


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    b010_bytes = B010_PATH.read_bytes()
    b010 = json.loads(b010_bytes)
    decision = b010["decision"]
    if decision["new_weight_access_required_candidates"] != EXPECTED_CANDIDATES:
        raise RuntimeError("B010 access-required candidate set changed")
    if decision["qualification_candidates"] != EXPECTED_CANDIDATES:
        raise RuntimeError("B010 qualification candidate set changed")

    envelopes = b010["candidate_access_envelopes"]
    by_id = {row["candidate_id"]: row for row in envelopes}
    if sorted(by_id) != sorted(EXPECTED_CANDIDATES):
        raise RuntimeError("B010 envelope candidate identities changed")
    for candidate_id in EXPECTED_CANDIDATES:
        row = by_id[candidate_id]
        if row["new_weight_access_required"] is not True:
            raise RuntimeError(f"{candidate_id}: access no longer required")
        if row["usd_ceiling"] != 0.0:
            raise RuntimeError(f"{candidate_id}: non-zero USD ceiling")
        if row["rights_status"]["gated_terms_acceptance_required"] is not False:
            raise RuntimeError(f"{candidate_id}: gated terms unexpectedly required")

    authority = {
        "authority_id": EXPECTED_AUTHORITY_ID,
        "task_id": "B011",
        "external_effect_class": "MODEL_WEIGHT_ACCESS",
        "status": "AUTHORIZED_CANONICAL",
        "scope": {
            "decision": EXPECTED_DECISION,
            "decision_surface": {
                "issue": EXPECTED_ISSUE,
                "comment_id": EXPECTED_COMMENT_ID,
            },
            "b010_manifest": {
                "path": "artifacts/manifests/B010-new-candidate-weight-access.json",
                "sha256": hashlib.sha256(b010_bytes).hexdigest(),
                "schema_version": b010["schema_version"],
            },
            "candidate_ids": EXPECTED_CANDIDATES,
            "candidate_access_envelopes": envelopes,
            "executor": "B011_APPROVED_EPHEMERAL_CLOUD_RUNNER_AFTER_EXACT_FOUNDER_AUTHORIZATION",
            "founder_machine_large_artifacts": 0,
            "git_model_binaries": False,
            "paid_compute": False,
            "paid_model_api": False,
            "gated_terms_acceptance": False,
            "weight_changing_training": False,
            "quantization_execution": False,
            "production_release": False,
            "large_dataset_ingestion": False,
        },
    }
    AUTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    AUTH_PATH.write_text(json.dumps(authority, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    b011 = catalog["tasks"]["B011"]
    if b011["canonical_state"] != "BLOCKED":
        raise RuntimeError("B011 canonical state changed before authority capture")
    if b011["required_authority_id"] != EXPECTED_AUTHORITY_ID:
        raise RuntimeError("B011 required authority identity changed")
    unresolved = catalog["unresolved_bindings"]
    if "B011" not in unresolved:
        raise RuntimeError("B011 unresolved binding unexpectedly absent")
    b011["canonical_state"] = "PENDING"
    del unresolved["B011"]
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    task_gate_text = TASK_GATE_TEST.read_text(encoding="utf-8")
    old = '''def test_b011_remains_blocked_after_b010_closeout() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is False\n    assert result["state_consistency_result"]["observed_state"] == "BLOCKED"\n    assert "task.blocked" in result["reasons"]\n    assert "task.unresolved_binding" in result["reasons"]\n    predecessor = next(row for row in result["prerequisite_results"] if row["task_id"] == "B010")\n    assert predecessor["satisfied"] is True\n    assert result["authority_result"]["required"] is True\n    assert result["authority_result"]["satisfied"] is False\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    new = '''def test_b011_is_eligible_after_exact_founder_authority_capture() -> None:\n    result = evaluate_task_snapshot("B011", canonical_main=_CANONICAL_MAIN)\n\n    assert result["eligible"] is True\n    assert result["state_consistency_result"]["observed_state"] == "PENDING"\n    assert "task.blocked" not in result["reasons"]\n    assert "task.unresolved_binding" not in result["reasons"]\n    predecessor = next(row for row in result["prerequisite_results"] if row["task_id"] == "B010")\n    assert predecessor["satisfied"] is True\n    assert result["authority_result"] == {\n        "required": True,\n        "authority_id": "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED",\n        "satisfied": True,\n        "reasons": [],\n    }\n    validate_instance("mstr-task-eligibility-v0", result)\n'''
    task_gate_text = replace_once(task_gate_text, old, new, label="B011 task-gate regression")
    TASK_GATE_TEST.write_text(task_gate_text, encoding="utf-8")

    convergence_text = CONVERGENCE_TEST.read_text(encoding="utf-8")
    convergence_text = replace_once(
        convergence_text,
        '    assert set(unresolved) == {"B011", "B013"}\n',
        '    assert set(unresolved) == {"B013"}\n',
        label="unresolved binding set",
    )
    convergence_text = replace_once(
        convergence_text,
        '    assert tasks["B011"]["canonical_state"] == "BLOCKED"\n',
        '    assert tasks["B011"]["canonical_state"] == "PENDING"\n    assert tasks["B011"]["required_authority_id"] == "B011_FOUNDER_AUTHORITY_IF_ACCESS_REQUIRED"\n',
        label="B011 convergence state",
    )
    CONVERGENCE_TEST.write_text(convergence_text, encoding="utf-8")


if __name__ == "__main__":
    main()
