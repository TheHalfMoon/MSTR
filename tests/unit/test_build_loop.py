from __future__ import annotations

import pytest

from mstr_qualify.harness.build_loop import BuildLoop, LoopControlError, LoopState


def _contract(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "mstr-build-loop-v0-test",
        "interaction_contract_id": "interaction.test",
        "goal_policy": {
            "ambiguity_behavior": "bounded_inference",
            "require_acceptance_criteria": True,
        },
        "tool_surface_id": "tools.test",
        "context_policy_id": "context.test",
        "edit_policy_id": "edit.test",
        "verifier_policy_id": "verifier.test",
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
        "max_tool_calls": 4,
        "max_repairs": 2,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.none",
        "trivial_task_fast_path": {
            "enabled": True,
            "description": "Known local edit with direct verifier.",
        },
    }
    payload.update(overrides)
    return payload


def test_trivial_task_fast_path_skips_unneeded_states() -> None:
    loop = BuildLoop(_contract())

    loop.transition(LoopState.GOAL)
    loop.transition(LoopState.ACT)
    loop.record_tool_call()
    loop.transition(LoopState.VERIFY)
    proposal = loop.propose_stop("required verifier observation recorded", verifier_observed=True)

    assert loop.state is LoopState.STOP
    assert proposal.canonical_success is False
    assert proposal.escalation is False
    assert loop.snapshot().steps == 4
    assert loop.snapshot().tool_calls == 1
    assert loop.trivial_task_fast_path_enabled is True


def test_builder_cannot_transition_directly_to_stop() -> None:
    loop = BuildLoop(_contract())
    loop.transition(LoopState.GOAL)

    with pytest.raises(LoopControlError) as excinfo:
        loop.transition(LoopState.STOP)

    assert excinfo.value.code == "loop.stop_requires_proposal"


def test_normal_stop_requires_verify_state_and_verifier_observation() -> None:
    loop = BuildLoop(_contract())
    loop.transition(LoopState.GOAL)
    loop.transition(LoopState.ACT)

    with pytest.raises(LoopControlError) as before_verify:
        loop.propose_stop("model says done", verifier_observed=True)
    assert before_verify.value.code == "loop.stop_before_verify"

    loop.transition(LoopState.VERIFY)
    with pytest.raises(LoopControlError) as no_observation:
        loop.propose_stop("model says done", verifier_observed=False)
    assert no_observation.value.code == "loop.stop_without_verifier_observation"


def test_illegal_transition_fails_closed() -> None:
    loop = BuildLoop(_contract())

    with pytest.raises(LoopControlError) as excinfo:
        loop.transition(LoopState.ACT)

    assert excinfo.value.code == "loop.illegal_transition"
    assert loop.state is LoopState.ORIENT


def test_step_tool_and_repair_budgets_are_enforced() -> None:
    step_loop = BuildLoop(_contract(max_steps=1))
    step_loop.transition(LoopState.GOAL)
    with pytest.raises(LoopControlError) as step_exc:
        step_loop.transition(LoopState.ACT)
    assert step_exc.value.code == "loop.step_budget_exhausted"

    tool_loop = BuildLoop(_contract(max_tool_calls=1))
    tool_loop.record_tool_call()
    with pytest.raises(LoopControlError) as tool_exc:
        tool_loop.record_tool_call()
    assert tool_exc.value.code == "loop.tool_budget_exhausted"

    repair_loop = BuildLoop(_contract(max_repairs=1))
    repair_loop.record_repair()
    with pytest.raises(LoopControlError) as repair_exc:
        repair_loop.record_repair()
    assert repair_exc.value.code == "loop.repair_budget_exhausted"


def test_timeout_is_fail_closed_with_injected_clock() -> None:
    now = [100.0]
    loop = BuildLoop(_contract(timeout_seconds=5), clock=lambda: now[0])
    now[0] = 106.0

    with pytest.raises(LoopControlError) as excinfo:
        loop.transition(LoopState.GOAL)

    assert excinfo.value.code == "loop.timeout_exceeded"


def test_retry_same_failed_action_requires_new_evidence() -> None:
    loop = BuildLoop(_contract())
    loop.record_action_result("apply-patch", success=False, evidence_token="test-failure-1")

    with pytest.raises(LoopControlError) as excinfo:
        loop.admit_retry("apply-patch", evidence_token="test-failure-1")
    assert excinfo.value.code == "loop.retry_without_new_evidence"

    loop.admit_retry("apply-patch", evidence_token="new-localization-evidence")


def test_escalation_is_non_successful_and_contract_bound() -> None:
    loop = BuildLoop(_contract())
    proposal = loop.escalate("authority boundary reached")

    assert loop.state is LoopState.STOP
    assert proposal.escalation is True
    assert proposal.canonical_success is False
    assert proposal.verifier_observed is False

    forbidden = BuildLoop(
        _contract(
            stop_policy={
                "success_requires_independent_verifier": True,
                "success_terminal_classes": ["VERIFIED_SUCCESS", "RECOVERED_SUCCESS"],
                "allow_escalation": False,
            }
        )
    )
    with pytest.raises(LoopControlError) as excinfo:
        forbidden.escalate("cannot continue")
    assert excinfo.value.code == "loop.escalation_forbidden"
