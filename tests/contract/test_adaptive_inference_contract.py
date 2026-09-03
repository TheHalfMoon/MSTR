from __future__ import annotations

import copy
import json
from pathlib import Path

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"


def _fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / "valid" / f"{name}.json").read_text(encoding="utf-8"))


def test_b029_adaptive_policy_freezes_one_attempt_and_evidence_gated_escalation() -> None:
    value = _fixture("mstr-adaptive-inference-policy-v0")
    validate_instance("mstr-adaptive-inference-policy-v0", value)
    assert value["default_attempt_count"] == 1
    assert set(value["escalation_triggers"]) == {"VERIFIER_FAILURE", "UNCERTAINTY"}
    assert value["new_evidence_required_before_retry"] is True
    assert value["protected_finalizer_required"] is True
    assert value["builder_success_authority"] is False
    assert value["authority_effect"] == "NONE"


def test_b029_bounded_branching_and_marginal_value_fail_closed() -> None:
    value = _fixture("mstr-adaptive-inference-policy-v0")
    assert value["branching_mode"] == "BOUNDED"
    assert value["hard_caps"]["max_branch_width"] == 2
    assert value["marginal_value_rule"]["decision_rule"] == "POSITIVE_EXPECTED_DVCR_GAIN_REQUIRED"

    bad = copy.deepcopy(value)
    bad["hard_caps"]["max_branch_width"] = 1
    assert validation_errors("mstr-adaptive-inference-policy-v0", bad)

    disabled = copy.deepcopy(value)
    disabled["branching_mode"] = "DISABLED"
    disabled["hard_caps"]["max_branch_width"] = 1
    validate_instance("mstr-adaptive-inference-policy-v0", disabled)


def test_b029_capability_and_difficulty_bindings_are_exact() -> None:
    value = _fixture("mstr-adaptive-inference-policy-v0")
    assert value["capability_profile_bindings"] == {
        "context_budget_field": "reliable_context_budget",
        "repair_depth_field": "max_repair_depth",
        "verifier_cadence_field": "recommended_verifier_cadence",
    }
    assert value["difficulty_calibration_schema_version"] == "mstr.difficulty-calibration.v0"
    assert value["difficulty_evidence_required_for_nontrivial_escalation"] is True


def test_b029_selective_context_freezes_exact_intent_set_without_implicit_retrieval() -> None:
    value = _fixture("mstr-selective-context-config-v0")
    validate_instance("mstr-selective-context-config-v0", value)
    assert set(value["intent_rules"]) == {
        "NO_RETRIEVAL",
        "NEED_FILE",
        "NEED_SYMBOL",
        "NEED_HISTORY",
        "NEED_TEST",
        "NEED_CONFIG",
        "NO_MORE_CONTEXT",
    }
    assert value["implicit_retrieval_allowed"] is False
    assert value["intent_rules"]["NO_RETRIEVAL"]["max_repository_calls"] == 0
    assert value["intent_rules"]["NO_MORE_CONTEXT"]["terminal"] is True
    assert value["intent_rules"]["NEED_HISTORY"]["status"] == "UNSUPPORTED_BY_ACTIVE_CONTRACT"
    assert value["intent_rules"]["NEED_HISTORY"]["resolution_mode"] == "CONTRACT_DEPENDENT"


def test_b029_context_and_attempt_shortcuts_are_rejected() -> None:
    adaptive = _fixture("mstr-adaptive-inference-policy-v0")
    adaptive["default_attempt_count"] = 2
    assert validation_errors("mstr-adaptive-inference-policy-v0", adaptive)

    context = _fixture("mstr-selective-context-config-v0")
    context["implicit_retrieval_allowed"] = True
    assert validation_errors("mstr-selective-context-config-v0", context)


def test_b029_evidence_preserves_non_execution_authority_boundary() -> None:
    evidence = (
        ROOT / "evidence" / "mstr-000b" / "B029-adaptive-inference.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "ENTRY_GATE_V2 = 33792125789 / SUCCESS",
        "DEFAULT_ATTEMPTS = 1",
        "MODEL_WEIGHT_ACCESS = NONE",
        "MODEL_EXECUTION = NONE",
        "PAID_COMPUTE = NONE",
        "WEIGHT_CHANGING_TRAINING = NONE",
        "B029_AUTHORITY = CONTRACT_POLICY_ONLY",
    ):
        assert marker in evidence
