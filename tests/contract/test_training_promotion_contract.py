from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance, validation_errors

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "schemas"


def _fixture(kind: str, name: str) -> dict[str, object]:
    return json.loads((FIXTURES / kind / f"{name}.json").read_text(encoding="utf-8"))


def test_training_method_cell_freezes_exact_four_method_semantics() -> None:
    base = _fixture("valid", "mstr-training-method-cell-v0")
    cases = (
        ("LORA_16BIT", "SIXTEEN_BIT", False, None),
        ("LORA_16BIT_RSLORA", "SIXTEEN_BIT", True, None),
        (
            "QLORA_4BIT",
            "FOUR_BIT_BASE",
            False,
            {"base_bits": 4, "scheme": "NF4", "tool_id": "bnb", "tool_revision": "fixture"},
        ),
        (
            "QLORA_4BIT_RSLORA",
            "FOUR_BIT_BASE",
            True,
            {"base_bits": 4, "scheme": "NF4", "tool_id": "bnb", "tool_revision": "fixture"},
        ),
    )
    for method, precision, rslora, quantization in cases:
        value = copy.deepcopy(base)
        value["method"] = method
        value["precision"] = precision
        value["rslora"] = rslora
        value["quantization"] = quantization
        validate_instance("mstr-training-method-cell-v0", value)


def test_training_method_cross_binding_fails_closed() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["method"] = "LORA_16BIT"
    assert validation_errors("mstr-training-method-cell-v0", value)


def test_unsupported_method_requires_exact_reason_and_terminal_status() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["support_status"] = "UNSUPPORTED"
    value["unsupported_reason"] = "exact fixture incompatibility"
    value["status"] = "UNSUPPORTED"
    validate_instance("mstr-training-method-cell-v0", value)

    value["unsupported_reason"] = None
    assert validation_errors("mstr-training-method-cell-v0", value)


def test_unsupported_status_requires_unsupported_support_and_exact_reason() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["status"] = "UNSUPPORTED"
    assert validation_errors("mstr-training-method-cell-v0", value)

    value["support_status"] = "UNSUPPORTED"
    value["unsupported_reason"] = "exact fixture incompatibility"
    validate_instance("mstr-training-method-cell-v0", value)


def test_execution_ready_requires_candidate_specific_support() -> None:
    value = _fixture("valid", "mstr-training-method-cell-v0")
    value["status"] = "READY_FOR_AUTHORIZED_EXECUTION"
    assert validation_errors("mstr-training-method-cell-v0", value)
    value["support_status"] = "SUPPORTED"
    validate_instance("mstr-training-method-cell-v0", value)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    (
        ("artifact_integrity_status", "FAIL"),
        ("q4_regression_result", "FAIL"),
        ("universal_laptop_gate_result", "FAIL"),
    ),
)
def test_q4_promotion_hard_gates_fail_closed(field: str, bad_value: str) -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value[field] = bad_value
    assert validation_errors("mstr-q4-promotion-v0", value)


def test_q4_not_required_laptop_gate_requires_reason() -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value["universal_laptop_gate_result"] = "NOT_REQUIRED"
    value["universal_laptop_gate_not_required_reason"] = "not applicable to this frozen stage"
    validate_instance("mstr-q4-promotion-v0", value)
    value["universal_laptop_gate_not_required_reason"] = None
    assert validation_errors("mstr-q4-promotion-v0", value)


def test_rejected_q4_record_requires_reason() -> None:
    value = _fixture("valid", "mstr-q4-promotion-v0")
    value["promotion_status"] = "REJECTED"
    assert validation_errors("mstr-q4-promotion-v0", value)
    value["rejection_reasons"] = ["q4.regression_failed"]
    validate_instance("mstr-q4-promotion-v0", value)


def test_b028_manifest_contains_exact_required_arms_without_selection() -> None:
    manifest = json.loads(
        (ROOT / "artifacts" / "manifests" / "B028-method-tournament-preflight.json").read_text(
            encoding="utf-8"
        )
    )
    arms = manifest["required_method_arms"]
    assert {arm["method"] for arm in arms} == {
        "LORA_16BIT",
        "LORA_16BIT_RSLORA",
        "QLORA_4BIT",
        "QLORA_4BIT_RSLORA",
    }
    assert len(arms) == 4
    assert all(arm["preflight_status"] == "REVALIDATION_REQUIRED" for arm in arms)
    assert manifest["method_selection"] == "UNSELECTED"
    assert manifest["execution_status"] == "NOT_EXECUTED"
    assert manifest["authority_boundary"]["model_weight_access"] is False
    assert manifest["authority_boundary"]["training_execution"] is False
    assert manifest["authority_boundary"]["weight_changing_training"] is False


def test_b028_guidance_snapshot_is_exact_and_not_candidate_support() -> None:
    manifest = json.loads(
        (ROOT / "artifacts" / "manifests" / "B028-method-tournament-preflight.json").read_text(
            encoding="utf-8"
        )
    )
    guidance = manifest["guidance_revalidation"]
    assert guidance["retrieved_date"] == "2026-08-29"
    assert guidance["peft"]["main_revision"] == "9c16ee66cd4c58bd9cdf2d8b4e06c1cf8e8f8efe"
    assert guidance["transformers"]["main_revision"] == "42ca97014c85d71a88ad60d55f08cb9fb4d26e2c"
    assert guidance["unsloth"]["main_revision"] == "e1653bcd1da874466da48ee5360ff60fc10d7973"
    assert manifest["candidate_support_rule"]["default"] == "REVALIDATION_REQUIRED"


def test_b028_evidence_preserves_non_execution_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B028-training-methods.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B028" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "MODEL_EXECUTION = NONE" in evidence
    assert "QUANTIZATION_EXECUTION = NONE" in evidence
    assert "TRAINING_EXECUTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "B028_AUTHORITY = CONTRACT_AND_PREFLIGHT_ONLY" in evidence
