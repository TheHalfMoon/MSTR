from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.errors import RightsEvaluationError
from mstr_qualify.rights import evaluate_component_rights, evaluate_primary_rights

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "rights" / "fixtures.json"


def permissive() -> dict[str, object]:
    return copy.deepcopy(json.loads(FIXTURE.read_text(encoding="utf-8"))["permissive"])


def test_permissive_component_passes() -> None:
    result = evaluate_component_rights("backbone", permissive())
    assert result.eligible_for_primary is True
    assert result.computed_decision == "pass_permissive"
    assert result.reason_codes == ()


@pytest.mark.parametrize(
    "field",
    [
        "personal_use",
        "commercial_use",
        "modification",
        "fine_tuning",
        "quantization",
        "derivative_redistribution",
    ],
)
def test_unknown_required_right_fails_closed(field: str) -> None:
    rights = permissive()
    rights[field] = "unknown"
    result = evaluate_component_rights("backbone", rights)
    assert result.eligible_for_primary is False
    assert f"backbone:{field}_unknown" in result.reason_codes


def test_explicit_denial_fails_closed() -> None:
    rights = permissive()
    rights["commercial_use"] = "no"
    assert (
        "backbone:commercial_use_denied"
        in evaluate_component_rights("backbone", rights).reason_codes
    )


@pytest.mark.parametrize(
    "gate",
    ["account_gate_required", "clickthrough_gate_required", "end_user_separate_license_required"],
)
def test_end_user_gate_fails_primary_admission(gate: str) -> None:
    rights = permissive()
    rights[gate] = True
    assert f"backbone:{gate}" in evaluate_component_rights("backbone", rights).reason_codes


def test_field_or_scale_restriction_fails_primary_admission() -> None:
    rights = permissive()
    rights["field_or_scale_restrictions"] = ["non-commercial"]
    assert (
        "backbone:field_or_scale_restriction_present"
        in evaluate_component_rights("backbone", rights).reason_codes
    )


def test_declared_pass_cannot_override_unresolved_condition() -> None:
    rights = permissive()
    rights["decision"] = "pass_conditional"
    result = evaluate_component_rights("backbone", rights)
    assert result.computed_decision == "fail"
    assert "backbone:declared_pass_conditional" in result.reason_codes


def test_missing_terms_evidence_fails_closed() -> None:
    rights = permissive()
    rights["terms_urls"] = []
    result = evaluate_component_rights("backbone", rights)
    assert "backbone:terms_evidence_missing" in result.reason_codes


def test_component_failure_blocks_whole_candidate() -> None:
    backbone = permissive()
    tokenizer = permissive()
    tokenizer["derivative_redistribution"] = "unknown"
    result = evaluate_primary_rights({"backbone": backbone, "tokenizer": tokenizer})
    assert result.eligible_for_primary is False
    assert result.components[0].component_id == "backbone"
    assert result.components[1].component_id == "tokenizer"
    assert "tokenizer:derivative_redistribution_unknown" in result.reason_codes


def test_all_required_components_must_pass() -> None:
    result = evaluate_primary_rights({"tokenizer": permissive(), "backbone": permissive()})
    assert result.eligible_for_primary is True
    assert [component.component_id for component in result.components] == ["backbone", "tokenizer"]


def test_empty_component_set_is_rejected() -> None:
    with pytest.raises(RightsEvaluationError, match="at least one"):
        evaluate_primary_rights({})
