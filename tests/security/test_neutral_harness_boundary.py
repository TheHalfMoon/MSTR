from __future__ import annotations

from pathlib import Path

import pytest

from mstr_qualify.harness.build_loop import LoopState
from mstr_qualify.harness.neutral import NeutralHarness, NeutralHarnessError, VerifierOutcome
from mstr_qualify.verifier.finalizer import FinalizerError


def _contract() -> dict[str, object]:
    return {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "h0-security-test",
        "interaction_contract_id": "interaction.h0-security-test",
        "goal_policy": {
            "ambiguity_behavior": "bounded_inference",
            "require_acceptance_criteria": True,
        },
        "tool_surface_id": "h0-neutral-minimal",
        "context_policy_id": "h0-literal-local-context",
        "edit_policy_id": "h0-whole-file",
        "verifier_policy_id": "h0-required-verifier-callback",
        "stop_policy": {
            "success_requires_independent_verifier": True,
            "success_terminal_classes": ["VERIFIED_SUCCESS", "RECOVERED_SUCCESS"],
            "allow_escalation": True,
        },
        "recovery_policy": {
            "retry_same_failed_action_without_new_evidence": False,
            "require_failure_classification": True,
        },
        "max_steps": 12,
        "max_tool_calls": 6,
        "max_repairs": 1,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.local-test-only",
        "trivial_task_fast_path": {"enabled": True},
    }


def _outcome(status: str, identity: str):
    def verifier(_: Path) -> VerifierOutcome:
        return VerifierOutcome(status, identity)  # type: ignore[arg-type]

    return verifier


def _ready(tmp_path: Path) -> NeutralHarness:
    harness = NeutralHarness(
        tmp_path,
        _contract(),
        run_id="run-h0-security",
        required_verifier_ids=("tests",),
    )
    harness.admit_goal("secure completion", acceptance_criteria=("protected proof",))
    harness.transition(LoopState.VERIFY)
    return harness


def test_model_claim_cannot_create_terminal_event_without_verifier_evidence(
    tmp_path: Path,
) -> None:
    harness = _ready(tmp_path)

    with pytest.raises(NeutralHarnessError) as stop:
        harness.propose_stop("model text claims COMPLETE_CANONICAL")

    assert stop.value.code == "h0.pre_stop_verifier_missing"
    assert all(event["event_type"] != "run.completed" for event in harness.events)


def test_pre_stop_pass_cannot_be_reused_as_post_stop_success(tmp_path: Path) -> None:
    harness = _ready(tmp_path)
    harness.observe_verifier("tests", _outcome("PASS", "pre-pass"))
    harness.propose_stop("pre-stop observation exists")

    with pytest.raises(FinalizerError) as excinfo:
        harness.finalize({"tests": _outcome("FAIL", "post-fail")})

    assert excinfo.value.code == "finalizer.required_verifier_not_pass"
    assert all(event["event_type"] != "run.completed" for event in harness.events)


def test_verifier_identity_whitespace_is_rejected_before_terminal_authority(
    tmp_path: Path,
) -> None:
    harness = _ready(tmp_path)

    with pytest.raises(NeutralHarnessError) as excinfo:
        harness.observe_verifier("tests", _outcome("PASS", " proof "))

    assert excinfo.value.code == "h0.verifier_result_identity_invalid"
    assert all(event["event_type"] != "run.completed" for event in harness.events)


def test_required_verifier_configuration_is_canonical_or_rejected(tmp_path: Path) -> None:
    with pytest.raises(NeutralHarnessError) as whitespace:
        NeutralHarness(
            tmp_path,
            _contract(),
            run_id="run-h0-whitespace",
            required_verifier_ids=(" tests ",),
        )
    assert whitespace.value.code == "h0.required_verifier_id_invalid"

    with pytest.raises(NeutralHarnessError) as duplicate:
        NeutralHarness(
            tmp_path,
            _contract(),
            run_id="run-h0-duplicate",
            required_verifier_ids=("tests", "tests"),
        )
    assert duplicate.value.code == "h0.required_verifiers_duplicate"
