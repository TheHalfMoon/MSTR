from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DECISION = _ROOT / "artifacts" / "decisions" / "B009-training-runtime-compatibility.json"


def _load() -> dict[str, object]:
    value = json.loads(_DECISION.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_b009_decision_is_bound_to_canonical_candidates_and_framework_pins() -> None:
    decision = _load()
    assert decision["task_id"] == "B009"
    assert decision["state"] == "IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT"
    assert decision["canonical_main_at_execution"] == "dd6c7a9b163f1f34e6cc3570da234078d39f4fce"
    pins = decision["framework_source_snapshot"]
    assert isinstance(pins, dict)
    assert set(pins) == {"transformers", "unsloth", "peft", "trl", "llama_cpp"}
    for record in pins.values():
        assert isinstance(record, dict)
        revision = record["revision"]
        assert isinstance(revision, str) and len(revision) == 40
        assert all(char in "0123456789abcdef" for char in revision)

    current = {}
    for path in sorted((_ROOT / "artifacts" / "candidates").glob("*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        current[row["candidate_id"]] = row
    serious = decision["serious_candidates"]
    references = decision["reference_candidates"]
    assert isinstance(serious, list) and len(serious) == 10
    assert isinstance(references, list) and len(references) == 9
    assert set(current) == {row["candidate_id"] for row in serious + references}
    for row in serious:
        source = current[row["candidate_id"]]
        assert row["upstream_id"] == source["upstream_id"]
        assert row["upstream_revision"] == source["upstream_revision"]
        assert source["status"] == "static_qualified"
        assert source["rights"]["decision"] == "pass_permissive"
        assert row["promotion_from_b009_allowed"] is False
    for row in references:
        source = current[row["candidate_id"]]
        assert row["upstream_id"] == source["upstream_id"]
        assert row["upstream_revision"] == source["upstream_revision"]
        assert row["compatibility_scope"] == "INFORMATIONAL_REFERENCE_ONLY"
        assert row["promotion_from_b009_allowed"] is False


def test_b009_source_evidence_never_claims_execution_pass() -> None:
    decision = _load()
    policy = decision["interpretation_policy"]
    assert isinstance(policy, dict)
    assert policy == {
        "b009_can_promote_candidate": False,
        "b010_owns_qualification_and_new_access_lists": True,
        "converter_source_is_conversion_pass": False,
        "converter_source_is_quantization_pass": False,
        "generic_path_is_exact_model_pass": False,
        "source_registered_is_runtime_pass": False,
        "trainer_source_is_trainability_pass": False,
    }
    for row in decision["serious_candidates"]:
        assert row["transformers"]["exact_candidate_load_status"] == "UNEXECUTED"
        assert row["unsloth"]["exact_train_save_export_status"] == "UNEXECUTED"
        assert row["peft"]["exact_target_module_coverage_status"] == "UNEXECUTED"
        assert row["trl"]["exact_candidate_training_status"] == "UNEXECUTED"
        assert row["llama_cpp"]["conversion_status"] == "UNEXECUTED"
        assert row["llama_cpp"]["quantization_status"] == "UNEXECUTED"
        assert row["llama_cpp"]["runtime_status"] == "UNVERIFIED"


def test_b009_authority_boundary_is_zero_effect() -> None:
    decision = _load()
    authority = decision["authority_boundary"]
    assert isinstance(authority, dict)
    assert authority["founder_machine_large_artifacts"] == 0
    for key, value in authority.items():
        if key != "founder_machine_large_artifacts":
            assert value is False, key
    handoff = decision["b010_handoff"]
    assert handoff["qualification_candidates"] == "NOT_DECIDED_BY_B009"
    assert handoff["new_weight_access_required_candidates"] == "NOT_DECIDED_BY_B009"
