from __future__ import annotations

import sys
from pathlib import Path

import pytest

from mstr_qualify.harness.build_loop import LoopState
from mstr_qualify.harness.event_log import replay
from mstr_qualify.harness.neutral import (
    CommandResult,
    NeutralHarness,
    NeutralHarnessError,
    VerifierOutcome,
)


def _contract(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "mstr.loop-contract.v0",
        "loop_id": "h0-neutral-test",
        "interaction_contract_id": "interaction.h0-neutral-test",
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
        "max_steps": 20,
        "max_tool_calls": 10,
        "max_repairs": 2,
        "timeout_seconds": 30,
        "effect_envelope_id": "effects.local-test-only",
        "trivial_task_fast_path": {"enabled": True},
    }
    payload.update(overrides)
    return payload


def _harness(tmp_path: Path, **kwargs: object) -> NeutralHarness:
    return NeutralHarness(
        tmp_path,
        _contract(),
        run_id="run-h0-test",
        required_verifier_ids=("tests",),
        **kwargs,
    )


def _pass(identity: str):
    def verifier(_: Path) -> VerifierOutcome:
        return VerifierOutcome("PASS", identity, "focused checks passed")

    return verifier


def test_repository_read_and_literal_search_are_workspace_bounded(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "alpha.py").write_text(
        "first\nneedle here\nlast\n", encoding="utf-8"
    )
    harness = _harness(tmp_path)
    harness.admit_goal("inspect repository", acceptance_criteria=("find needle",))
    harness.transition(LoopState.LOCALIZE)

    assert "needle here" in harness.read_text("src/alpha.py")
    matches = harness.search_text("needle", relative_paths=("src/alpha.py",))

    assert [(match.path, match.line_number) for match in matches] == [
        ("src/alpha.py", 2)
    ]
    assert harness.snapshot().tool_calls == 2
    state = harness.project_state()
    assert state.files_inspected[-1].value == "src/alpha.py"
    assert state.repo_map[-1].value == "src/alpha.py:2:needle here"
    assert len(replay(list(harness.events))) == len(harness.events)


def test_repository_path_escape_and_symlink_read_fail_closed(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-h0.txt"
    outside.write_text("secret", encoding="utf-8")
    harness = _harness(tmp_path)
    harness.admit_goal("inspect repository", acceptance_criteria=("bounded read",))
    harness.transition(LoopState.LOCALIZE)

    with pytest.raises(NeutralHarnessError) as escape:
        harness.read_text("../outside-h0.txt")
    assert escape.value.code == "h0.path_outside_workspace"

    link = tmp_path / "link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable on this platform")
    with pytest.raises(NeutralHarnessError) as symlink:
        harness.read_text("link.txt")
    assert symlink.value.code in {"h0.path_outside_workspace", "h0.read_target_invalid"}


def test_shell_surface_uses_argv_without_shell_and_records_result(tmp_path: Path) -> None:
    observed: list[tuple[tuple[str, ...], Path, float]] = []

    def runner(argv: tuple[str, ...], cwd: Path, timeout: float) -> CommandResult:
        observed.append((argv, cwd, timeout))
        return CommandResult(argv, 0, "ok\n", "")

    harness = _harness(tmp_path, command_runner=runner)
    harness.admit_goal("run local command", acceptance_criteria=("command succeeds",))
    harness.transition(LoopState.ACT)
    result = harness.run_shell((sys.executable, "-c", "print('ok')"))

    assert result.stdout == "ok\n"
    assert observed == [
        ((sys.executable, "-c", "print('ok')"), tmp_path.resolve(), 30.0)
    ]
    assert harness.project_state().commands_run
    assert harness.events[-1]["event_type"] == "tool.result"
    assert harness.events[-1]["source"] == "tool"


def test_whole_file_apply_is_deterministic_and_not_stale_safe_h1(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("write file", acceptance_criteria=("content exact",))
    harness.transition(LoopState.ACT)

    digest = harness.apply_file("pkg/value.txt", "alpha\n")

    assert (tmp_path / "pkg" / "value.txt").read_text(encoding="utf-8") == "alpha\n"
    assert len(digest) == 64
    state = harness.project_state()
    assert state.changed_files[-1].value == "pkg/value.txt"
    assert harness.events[-1]["event_type"] == "edit.applied"


def test_trivial_verified_flow_reruns_fresh_post_stop_evidence(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("trivial verified task", acceptance_criteria=("tests pass",))
    harness.transition(LoopState.VERIFY)
    harness.observe_verifier("tests", _pass("pre-stop-proof"))

    proposal = harness.propose_stop("pre-stop verifier observed")
    assert proposal.canonical_success is False
    assert harness.snapshot().state is LoopState.STOP

    decision = harness.finalize({"tests": _pass("post-stop-proof")})

    assert decision.terminal_class == "VERIFIED_SUCCESS"
    assert decision.completion_event["event_type"] == "run.completed"
    assert decision.completion_event["source"] == "verifier"
    assert decision.completion_event["model_visible"] is False
    assert harness.events[-3]["event_type"] == "verifier.started"
    assert harness.events[-2]["payload"]["result_identity"] == "post-stop-proof"
    assert harness.events[-1] == decision.completion_event
    assert len(replay(list(harness.events))) == len(harness.events)


def test_stop_requires_real_pre_stop_observation_for_every_required_verifier(
    tmp_path: Path,
) -> None:
    harness = NeutralHarness(
        tmp_path,
        _contract(),
        run_id="run-h0-multi",
        required_verifier_ids=("lint", "tests"),
    )
    harness.admit_goal("verify", acceptance_criteria=("all required verifiers observed",))
    harness.transition(LoopState.VERIFY)
    harness.observe_verifier("tests", _pass("tests-pre"))

    with pytest.raises(NeutralHarnessError) as excinfo:
        harness.propose_stop("model says done")

    assert excinfo.value.code == "h0.pre_stop_verifier_missing"
    assert harness.snapshot().stopped is False


def test_finalize_requires_exact_post_stop_verifier_set(tmp_path: Path) -> None:
    harness = _harness(tmp_path)
    harness.admit_goal("verify", acceptance_criteria=("tests pass",))
    harness.transition(LoopState.VERIFY)
    harness.observe_verifier("tests", _pass("pre"))
    harness.propose_stop("observed")

    with pytest.raises(NeutralHarnessError) as excinfo:
        harness.finalize({})

    assert excinfo.value.code == "h0.post_stop_verifier_set_mismatch"
    assert all(event["event_type"] != "run.completed" for event in harness.events)
