from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.harness.build_loop import LoopState
from mstr_qualify.harness.neutral import VerifierOutcome
from mstr_qualify.harness.wepld import (
    WePLDAdapterError,
    WePLDNativeHarness,
    work_item_from_mapping,
)


def _contract() -> dict[str, object]:
    return {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "h2-wepld-test",
        "interaction_contract_id": "interaction.h2-wepld-test",
        "goal_policy": {
            "ambiguity_behavior": "bounded_inference",
            "require_acceptance_criteria": True,
        },
        "tool_surface_id": "h2-wepld-over-h1",
        "context_policy_id": "h1-explicit-selective",
        "edit_policy_id": "h1-stale-safe-whole-file",
        "verifier_policy_id": "h2-wepld-required-verifier-callback",
        "stop_policy": {
            "success_requires_independent_verifier": True,
            "success_terminal_classes": ["VERIFIED_SUCCESS", "RECOVERED_SUCCESS"],
            "allow_escalation": True,
        },
        "recovery_policy": {
            "retry_same_failed_action_without_new_evidence": False,
            "require_failure_classification": True,
        },
        "max_steps": 30,
        "max_tool_calls": 20,
        "max_repairs": 3,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.local-repository-only",
        "trivial_task_fast_path": {"enabled": True},
    }


def _fixture() -> dict[str, object]:
    path = Path(__file__).resolve().parents[2] / "fixtures" / "harness" / "a009-wepld-state.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _harness(tmp_path: Path) -> WePLDNativeHarness:
    return WePLDNativeHarness(
        tmp_path,
        _contract(),
        run_id="run-h2-test",
        required_verifier_ids=("tests", "types"),
    )


def test_fixture_maps_wepld_state_into_canonical_goal_and_binding(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    item = work_item_from_mapping(_fixture())

    binding = harness.admit_wepld(item)
    state = harness.project_state()

    assert binding.profile_id == "mstr.harness.h2-wepld-native.v0"
    assert binding.contract_id == "mstr.wepld-adapter.v0"
    assert binding.spec_identity == "SPEC-42@rev-7"
    assert binding.task_identity == "TASK-9@rev-3"
    assert binding.effect_envelope_id == "effects.local-repository-only"
    assert binding.required_verifier_ids == ("tests", "types")
    assert len(binding.binding_sha256) == 64
    assert state.goal is not None
    assert state.goal.value == "Implement the bounded import command."
    assert tuple(item.goal.acceptance_criteria) == ("Import validates before write.",)
    assert "Spec behavior remains backwards compatible." in {
        record.value for record in state.acceptance_criteria
    }
    assert "WePLD prohibited effect: NETWORK" in {
        record.value for record in state.constraints
    }
    assert harness.events[-1]["payload"]["h2_wepld_binding"]["binding_sha256"] == (
        binding.binding_sha256
    )


def test_adapter_is_deterministic_for_equivalent_state(tmp_path: Path) -> None:
    item = work_item_from_mapping(_fixture())
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = _harness(tmp_path / "a")
    second = _harness(tmp_path / "b")

    first_binding = first.admit_wepld(item)
    second_binding = second.admit_wepld(item)

    assert first_binding.binding_sha256 == second_binding.binding_sha256


def test_effect_envelope_cannot_expand_mstr_authority(tmp_path: Path) -> None:
    payload = _fixture()
    payload["effects"]["effect_envelope_id"] = "effects.network-and-repository"
    item = work_item_from_mapping(payload)

    with pytest.raises(WePLDAdapterError) as excinfo:
        _harness(tmp_path).admit_wepld(item)

    assert excinfo.value.code == "h2.effect_envelope_expansion_forbidden"


def test_conflicting_effect_allow_and_deny_sets_fail_closed(tmp_path: Path) -> None:
    payload = _fixture()
    payload["effects"]["allowed_effects"] = ["NETWORK"]
    payload["effects"]["prohibited_effects"] = ["NETWORK"]
    item = work_item_from_mapping(payload)

    with pytest.raises(WePLDAdapterError) as excinfo:
        _harness(tmp_path).admit_wepld(item)

    assert excinfo.value.code == "h2.effect_policy_conflict"


def test_verifier_set_must_exactly_match_mstr_required_set(tmp_path: Path) -> None:
    payload = _fixture()
    payload["verifier"]["required_verifier_ids"] = ["tests"]
    item = work_item_from_mapping(payload)

    with pytest.raises(WePLDAdapterError) as excinfo:
        _harness(tmp_path).admit_wepld(item)

    assert excinfo.value.code == "h2.verifier_set_mismatch"


def test_unknown_success_authority_field_is_rejected() -> None:
    payload = _fixture()
    payload["canonical_success"] = True

    with pytest.raises(WePLDAdapterError) as excinfo:
        work_item_from_mapping(payload)

    assert excinfo.value.code == "h2.wepld_state_invalid"


def test_h2_still_requires_a006_finalizer_for_success(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_wepld(work_item_from_mapping(_fixture()))
    harness.transition(LoopState.VERIFY)

    def passing(workspace: Path) -> VerifierOutcome:
        del workspace
        return VerifierOutcome("PASS", "verifier-result-1", "ok")

    harness.observe_verifier("tests", passing)
    harness.observe_verifier("types", passing)
    proposal = harness.propose_stop("required verifiers observed")

    assert proposal.canonical_success is False

    decision = harness.finalize({"tests": passing, "types": passing})

    assert decision.terminal_class == "VERIFIED_SUCCESS"
    assert harness.events[-1]["event_type"] == "run.completed"


def test_adapter_module_has_no_wepld_runtime_dependency() -> None:
    import mstr_qualify.harness.wepld as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "import wepld" not in source
    assert "from wepld" not in source


def test_profile_config_records_portable_non_authoritative_boundary() -> None:
    path = (
        Path(__file__).resolve().parents[3]
        / "configs"
        / "harness"
        / "wepld-native-v0.json"
    )
    profile = json.loads(path.read_text(encoding="utf-8"))

    assert profile["profile_id"] == "mstr.harness.h2-wepld-native.v0"
    assert profile["extends"] == "mstr.harness.h1-native.v0"
    assert profile["wepld_runtime_dependency"] is False
    assert profile["authority_policy"]["wepld_can_expand_effect_envelope"] is False
    assert profile["authority_policy"]["wepld_can_author_canonical_success"] is False
