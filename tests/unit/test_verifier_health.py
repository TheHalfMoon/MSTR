"""B023 verifier-health evaluator and A018 admission integration tests."""

from __future__ import annotations

from dataclasses import replace

import pytest

from mstr_qualify.errors import SchemaValidationError
from mstr_qualify.trajectory.admission import bind_verifier_health, decide_training_admission
from mstr_qualify.verifier import (
    VerifierHealthEvaluationError,
    VerifierHealthObservation,
    classify_verifier_health,
    evaluate_verifier_health,
)

STAGES = ("MSTR-002-SFT", "MSTR-002-PREFERENCE")


def _observation() -> VerifierHealthObservation:
    return VerifierHealthObservation(
        verifier_health_id="vh-b023-controlled-001",
        task_identity="direction-task-b023-controlled",
        verifier_manifest_id="verifier-b023-controlled",
        evaluator_hashes=(
            {"path": "tests/controlled/verifier.py", "sha256": "a" * 64},
        ),
        protected_paths=("tests/controlled/verifier.py",),
        protected_path_integrity="PASS",
        reference_oracle_status="PASS",
        noop_fail_status="PASS",
        known_bad_fail_status="PASS",
        mutation_results=(
            {
                "mutation_id": "delete-tests",
                "shortcut_class": "DELETE_TESTS",
                "expected_rejection": True,
                "observed_rejection": True,
                "evidence_identity": "fixture-mutation-delete-tests",
            },
        ),
        generated_test_independence="INDEPENDENT",
        leakage_checks=(
            {
                "check_id": "future-history",
                "leakage_class": "FUTURE_HISTORY",
                "status": "CLEAR",
                "evidence_identity": "fixture-leakage-future-history",
            },
        ),
        disagreement_signals=(
            {
                "signal_id": "existing-vs-targeted",
                "left_evidence_identity": "fixture-existing-tests",
                "right_evidence_identity": "fixture-targeted-tests",
                "status": "AGREE",
            },
        ),
    )


def _with_disagreement(status: str) -> VerifierHealthObservation:
    return replace(
        _observation(),
        disagreement_signals=(
            {
                "signal_id": "existing-vs-targeted",
                "left_evidence_identity": "fixture-existing-tests",
                "right_evidence_identity": "fixture-targeted-tests",
                "status": status,
            },
        ),
    )


def _with_leakage(status: str) -> VerifierHealthObservation:
    return replace(
        _observation(),
        leakage_checks=(
            {
                "check_id": "future-history",
                "leakage_class": "FUTURE_HISTORY",
                "status": status,
                "evidence_identity": "fixture-leakage-future-history",
            },
        ),
    )


@pytest.mark.parametrize(
    ("observation", "expected"),
    [
        (_observation(), "HEALTHY"),
        (replace(_observation(), generated_test_independence="PARTIAL"), "PARTIAL"),
        (_with_disagreement("DISAGREE"), "DISAGREEMENT"),
        (replace(_observation(), known_bad_fail_status="FAIL"), "BROKEN"),
        (_with_leakage("DETECTED"), "LEAKED"),
        (replace(_observation(), protected_path_integrity="FAIL"), "TAMPERED"),
    ],
)
def test_b023_proves_all_frozen_health_classes(
    observation: VerifierHealthObservation, expected: str
) -> None:
    assert classify_verifier_health(observation) == expected
    record = evaluate_verifier_health(observation, stage_ids=STAGES)
    assert record["health_class"] == expected


@pytest.mark.parametrize(
    ("health_class", "expected_admission", "expected_reasons"),
    [
        ("HEALTHY", "CLEAN_POSITIVE_ELIGIBLE", []),
        ("PARTIAL", "RESEARCH_DIAGNOSTIC_ONLY", ["VERIFIER_HEALTH_PARTIAL"]),
        (
            "DISAGREEMENT",
            "RESEARCH_DIAGNOSTIC_ONLY",
            ["VERIFIER_HEALTH_DISAGREEMENT"],
        ),
        ("BROKEN", "BLOCKED", ["VERIFIER_HEALTH_BROKEN"]),
        ("LEAKED", "BLOCKED", ["VERIFIER_HEALTH_LEAKED"]),
        ("TAMPERED", "BLOCKED", ["VERIFIER_HEALTH_TAMPERED"]),
    ],
)
def test_b023_emits_b022_stage_posture(
    health_class: str, expected_admission: str, expected_reasons: list[str]
) -> None:
    observation = {
        "HEALTHY": _observation(),
        "PARTIAL": replace(_observation(), generated_test_independence="PARTIAL"),
        "DISAGREEMENT": _with_disagreement("DISAGREE"),
        "BROKEN": replace(_observation(), known_bad_fail_status="FAIL"),
        "LEAKED": _with_leakage("DETECTED"),
        "TAMPERED": replace(_observation(), protected_path_integrity="FAIL"),
    }[health_class]
    record = evaluate_verifier_health(observation, stage_ids=STAGES)
    for stage in record["training_stage_eligibility"]:
        assert stage["admission_class"] == expected_admission
        assert stage["reason_codes"] == expected_reasons


def test_b023_safety_precedence_prefers_tamper_then_leak_then_broken() -> None:
    broken = replace(_with_leakage("DETECTED"), known_bad_fail_status="FAIL")
    assert classify_verifier_health(broken) == "LEAKED"
    tampered = replace(broken, protected_path_integrity="FAIL")
    assert classify_verifier_health(tampered) == "TAMPERED"


def test_b023_mutation_bypass_is_broken() -> None:
    observation = replace(
        _observation(),
        mutation_results=(
            {
                "mutation_id": "weaken-assertions",
                "shortcut_class": "WEAKEN_ASSERTIONS",
                "expected_rejection": True,
                "observed_rejection": False,
                "evidence_identity": "fixture-mutation-weaken-assertions",
            },
        ),
    )
    assert classify_verifier_health(observation) == "BROKEN"


@pytest.mark.parametrize(
    "independence",
    ["PARTIAL", "NOT_INDEPENDENT", "UNRESOLVED"],
)
def test_b023_non_independent_generated_tests_are_not_clean_positive(
    independence: str,
) -> None:
    observation = replace(_observation(), generated_test_independence=independence)
    assert classify_verifier_health(observation) == "PARTIAL"


def test_b023_indeterminate_disagreement_is_partial() -> None:
    assert classify_verifier_health(_with_disagreement("INDETERMINATE")) == "PARTIAL"


def test_b023_invalid_observation_fails_schema_validation() -> None:
    observation = replace(_observation(), evaluator_hashes=())
    with pytest.raises(SchemaValidationError):
        evaluate_verifier_health(observation, stage_ids=STAGES)


def test_b023_stage_ids_must_be_nonempty_and_unique() -> None:
    with pytest.raises(VerifierHealthEvaluationError) as empty:
        evaluate_verifier_health(_observation(), stage_ids=())
    assert empty.value.code == "verifier.health_stage_invalid"

    with pytest.raises(VerifierHealthEvaluationError) as duplicate:
        evaluate_verifier_health(_observation(), stage_ids=("MSTR-002-SFT", "MSTR-002-SFT"))
    assert duplicate.value.code == "verifier.health_stage_duplicate"


def _bind(record: dict[str, object], stage_id: str = "MSTR-002-SFT"):
    return bind_verifier_health(
        record,
        task_manifest_id="direction-task-b023-controlled",
        verifier_manifest_id="verifier-b023-controlled",
        stage_id=stage_id,
    )


def _sft_decision(record: dict[str, object]):
    return decide_training_admission(
        terminal_class="VERIFIED_SUCCESS",
        requested_lane="SFT",
        provenance={
            "source_class": "REPOSITORY_OWNED_FIXTURE",
            "provenance_status": "COMPLETE",
            "rights_status": "NOT_APPLICABLE",
            "secret_scan_status": "NOT_APPLICABLE",
        },
        contamination_status="CLEAR",
        authority_violations=(),
        verifier_health_binding=_bind(record),
        verifier_proof_present=True,
    )


def test_b023_healthy_record_flows_through_existing_a018_admission_surface() -> None:
    record = evaluate_verifier_health(_observation(), stage_ids=STAGES)
    decision = _sft_decision(record)
    assert decision.training_admission == "ADMITTED_SFT"
    assert decision.training_labels == {"label_kind": "CLEAN_POSITIVE"}
    assert decision.verifier_health_binding is not None
    assert decision.verifier_health_binding.health_class == "HEALTHY"


@pytest.mark.parametrize(
    "observation",
    [
        replace(_observation(), generated_test_independence="PARTIAL"),
        _with_disagreement("DISAGREE"),
        replace(_observation(), known_bad_fail_status="FAIL"),
        _with_leakage("DETECTED"),
        replace(_observation(), protected_path_integrity="FAIL"),
    ],
)
def test_b023_nonhealthy_records_block_clean_positive_a018_sft(
    observation: VerifierHealthObservation,
) -> None:
    record = evaluate_verifier_health(observation, stage_ids=STAGES)
    decision = _sft_decision(record)
    assert decision.training_admission == "REJECTED"
    assert decision.verifier_health_binding is not None
    assert decision.verifier_health_binding.health_class == record["health_class"]


def test_b023_does_not_change_a006_terminal_success_authority() -> None:
    record = evaluate_verifier_health(_observation(), stage_ids=STAGES)
    assert "terminal_class" not in record
    assert "terminal_success" not in record
    assert "training_authorized" not in record
