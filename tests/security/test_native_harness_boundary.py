from __future__ import annotations

from pathlib import Path

import pytest

from mstr_qualify.harness.build_loop import LoopState
from mstr_qualify.harness.native import (
    ContextRequest,
    EditRequest,
    NativeHarness,
    NativeHarnessError,
    PrefixCacheMeasurement,
)


def _contract() -> dict[str, object]:
    return {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "h1-security",
        "interaction_contract_id": "interaction.h1-security",
        "goal_policy": {
            "ambiguity_behavior": "bounded_inference",
            "require_acceptance_criteria": True,
        },
        "tool_surface_id": "h1-mstr-native",
        "context_policy_id": "h1-explicit-selective",
        "edit_policy_id": "h1-stale-safe-whole-file",
        "verifier_policy_id": "h1-required-verifier-callback",
        "stop_policy": {
            "success_requires_independent_verifier": True,
            "success_terminal_classes": ["VERIFIED_SUCCESS", "RECOVERED_SUCCESS"],
            "allow_escalation": True,
        },
        "recovery_policy": {
            "retry_same_failed_action_without_new_evidence": False,
            "require_failure_classification": True,
        },
        "max_steps": 20,
        "max_tool_calls": 10,
        "max_repairs": 2,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.local-test-only",
        "trivial_task_fast_path": {"enabled": True},
    }


def _harness(tmp_path: Path) -> NativeHarness:
    return NativeHarness(
        tmp_path,
        _contract(),
        run_id="run-h1-security",
        required_verifier_ids=("tests",),
    )


def test_context_decision_is_rejected_outside_context_states(tmp_path: Path) -> None:
    harness = _harness(tmp_path)

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.select_context(ContextRequest("NO_RETRIEVAL"))

    assert excinfo.value.code == "h0.operation_state_invalid"


def test_unchecked_h0_apply_cannot_bypass_stale_safe_h1(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("edit", acceptance_criteria=("stale safe",))
    harness.transition(LoopState.ACT)

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.apply_file("value.txt", "unsafe")

    assert excinfo.value.code == "h1.unsafe_edit_forbidden"
    assert not (tmp_path / "value.txt").exists()


def test_noncanonical_edit_path_cannot_alias_one_file(tmp_path: Path) -> None:
    (tmp_path / "value.txt").write_text("alpha", encoding="utf-8")
    harness = _harness(tmp_path)
    harness.admit_goal("edit", acceptance_criteria=("canonical identity",))
    harness.transition(LoopState.ACT)

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.apply_stale_safe_edit(
            EditRequest(
                "nested/../value.txt",
                "beta",
                "8ed3f6ad685b959ead7022518e1af76cd816f8e8ec7ccdda1ed4018e8f2223f8",
            )
        )

    assert excinfo.value.code == "h0.path_not_canonical"
    assert (tmp_path / "value.txt").read_text(encoding="utf-8") == "alpha"


def test_edit_expected_identity_must_be_exact_sha_or_absent(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("edit", acceptance_criteria=("exact identity",))
    harness.transition(LoopState.ACT)

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.apply_stale_safe_edit(EditRequest("new.txt", "value", "latest"))

    assert excinfo.value.code == "h1.edit_expected_identity_invalid"
    assert not (tmp_path / "new.txt").exists()


def test_prefix_cache_estimate_cannot_masquerade_as_measurement() -> None:
    with pytest.raises(NativeHarnessError) as excinfo:
        PrefixCacheMeasurement(
            input_tokens=10,
            shared_prefix_tokens=5,
            measurement_source="ESTIMATE",  # type: ignore[arg-type]
        )

    assert excinfo.value.code == "h1.prefix_measurement_invalid"


def test_h1_does_not_add_external_effect_authority(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    assert harness.prefix_cache_state == "UNMEASURED"
    assert all(event["event_type"] != "run.completed" for event in harness.events)
