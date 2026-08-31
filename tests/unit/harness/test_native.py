from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from mstr_qualify.harness.build_loop import LoopState
from mstr_qualify.harness.native import (
    ContextRequest,
    EditRequest,
    NativeHarness,
    NativeHarnessError,
    PrefixCacheMeasurement,
    ReadRequest,
    RecoveryCadence,
    ShellRequest,
)
from mstr_qualify.harness.neutral import CommandResult
from mstr_qualify.state import CompactionPolicy


def _contract(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "h1-native-test",
        "interaction_contract_id": "interaction.h1-native-test",
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
        "max_steps": 30,
        "max_tool_calls": 20,
        "max_repairs": 3,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.local-test-only",
        "trivial_task_fast_path": {"enabled": True},
    }
    payload.update(overrides)
    return payload


def _harness(tmp_path: Path, **kwargs: object) -> NativeHarness:
    return NativeHarness(
        tmp_path,
        _contract(),
        run_id="run-h1-test",
        required_verifier_ids=("tests",),
        **kwargs,
    )


def test_typed_read_and_context_selection_are_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("bravo\n", encoding="utf-8")
    harness = _harness(tmp_path, context_max_chars=8)
    harness.admit_goal("inspect", acceptance_criteria=("bounded context",))
    harness.transition(LoopState.LOCALIZE)

    read = harness.read_typed(ReadRequest("a.txt"))
    selected = harness.select_context(
        ContextRequest("EXPLICIT_PATHS", ("b.txt", "a.txt"), max_chars=8)
    )

    assert read.content == "alpha\n"
    assert read.content_sha256 == hashlib.sha256(b"alpha\n").hexdigest()
    assert len(read.result_identity) == 64
    assert [item.path for item in selected.files] == ["a.txt", "b.txt"]
    assert selected.files[0].content == "alpha\n"
    assert selected.files[1].content == "br"
    assert selected.truncated is True
    assert len(selected.result_identity) == 64


def test_no_retrieval_is_explicit_and_consumes_no_tool_call(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("minimal context", acceptance_criteria=("no retrieval",))
    harness.transition(LoopState.LOCALIZE)
    before = harness.snapshot().tool_calls

    selected = harness.select_context(ContextRequest("NO_RETRIEVAL"))

    assert selected.files == ()
    assert selected.truncated is False
    assert harness.snapshot().tool_calls == before
    assert harness.events[-1]["payload"]["h1_context_mode"] == "NO_RETRIEVAL"


def test_untyped_h0_tool_surface_is_not_exposed_by_h1(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("alpha", encoding="utf-8")
    harness = _harness(tmp_path)
    harness.admit_goal("typed only", acceptance_criteria=("typed read",))
    harness.transition(LoopState.LOCALIZE)

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.read_text("a.txt")

    assert excinfo.value.code == "h1.untyped_tool_forbidden"


def test_stale_safe_edit_rejects_changed_base_without_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "value.txt"
    target.write_text("alpha\n", encoding="utf-8")
    harness = _harness(tmp_path)
    harness.admit_goal("edit", acceptance_criteria=("no stale overwrite",))
    harness.transition(LoopState.LOCALIZE)
    observed = harness.read_typed(ReadRequest("value.txt"))
    harness.transition(LoopState.ACT)
    target.write_text("external\n", encoding="utf-8")

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.apply_stale_safe_edit(
            EditRequest("value.txt", "candidate\n", observed.content_sha256)
        )

    assert excinfo.value.code == "h1.edit_stale"
    assert target.read_text(encoding="utf-8") == "external\n"
    assert harness.native_snapshot().consecutive_failures == 1
    assert harness.project_state().known_failures[-1].category == "BAD_PATCH"


def test_stale_safe_edit_applies_when_expected_identity_matches(tmp_path: Path) -> None:
    target = tmp_path / "value.txt"
    target.write_text("alpha\n", encoding="utf-8")
    harness = _harness(tmp_path)
    harness.admit_goal("edit", acceptance_criteria=("exact base",))
    harness.transition(LoopState.LOCALIZE)
    observed = harness.read_typed(ReadRequest("value.txt"))
    harness.transition(LoopState.ACT)

    result = harness.apply_stale_safe_edit(
        EditRequest("value.txt", "beta\n", observed.content_sha256)
    )

    assert result.previous_sha256 == observed.content_sha256
    assert result.content_sha256 == hashlib.sha256(b"beta\n").hexdigest()
    assert target.read_text(encoding="utf-8") == "beta\n"
    assert harness.project_state().changed_files[-1].value == "value.txt"


def test_recovery_cadence_blocks_third_action_until_recovery(tmp_path: Path) -> None:
    def runner(argv: tuple[str, ...], cwd: Path, timeout: float) -> CommandResult:
        del cwd, timeout
        return CommandResult(argv, 1, "", "failed")

    harness = _harness(
        tmp_path,
        command_runner=runner,
        recovery_cadence=RecoveryCadence(max_consecutive_failures=2),
    )
    harness.admit_goal("recover", acceptance_criteria=("bounded repair",))
    harness.transition(LoopState.ACT)

    harness.run_shell_typed(ShellRequest(("false-a",)))
    harness.run_shell_typed(ShellRequest(("false-b",)))
    assert harness.recovery_required is True

    with pytest.raises(NativeHarnessError) as excinfo:
        harness.run_shell_typed(ShellRequest(("false-c",)))
    assert excinfo.value.code == "h1.recovery_required"

    snapshot = harness.recover(
        reason="two consecutive command failures",
        evidence="changed plan after inspecting stderr",
        next_state=LoopState.ACT,
    )
    assert snapshot.consecutive_failures == 0
    assert snapshot.recovery_required is False
    assert snapshot.loop.repairs == 1
    assert snapshot.loop.state is LoopState.ACT
    assert [event["event_type"] for event in harness.events[-2:]] == [
        "recovery.started",
        "recovery.result",
    ] or harness.events[-3]["event_type"] == "recovery.started"


def test_compact_state_uses_a004_fail_closed_compaction(tmp_path: Path) -> None:
    for index in range(3):
        (tmp_path / f"f{index}.txt").write_text(str(index), encoding="utf-8")
    harness = _harness(
        tmp_path,
        compaction_policy=CompactionPolicy(max_context_items=1),
    )
    harness.admit_goal("compact", acceptance_criteria=("retain bounded state",))
    harness.transition(LoopState.LOCALIZE)
    for index in range(3):
        harness.read_typed(ReadRequest(f"f{index}.txt"))

    compacted = harness.compact_state()

    assert len(compacted.files_inspected) == 1
    assert compacted.files_inspected[0].value == "f2.txt"
    assert {record.field for record in compacted.compaction_records} == {
        "files_inspected"
    }


def test_prefix_cache_is_unmeasured_until_runtime_observation(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    assert harness.prefix_cache_state == "UNMEASURED"

    measurement = harness.record_prefix_cache_measurement(
        PrefixCacheMeasurement(
            input_tokens=100,
            shared_prefix_tokens=40,
            cache_read_tokens=25,
        )
    )

    assert harness.prefix_cache_state == "MEASURED"
    assert measurement.prefix_reuse_ratio == 0.4
    assert harness.events[-1]["event_type"] == "context.compacted"
    assert harness.events[-1]["model_visible"] is False


def test_invalid_prefix_cache_claim_fails_closed() -> None:
    with pytest.raises(NativeHarnessError) as excinfo:
        PrefixCacheMeasurement(input_tokens=10, shared_prefix_tokens=11)

    assert excinfo.value.code == "h1.prefix_measurement_invalid"
