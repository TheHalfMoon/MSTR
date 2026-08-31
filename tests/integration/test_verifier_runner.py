from __future__ import annotations

from pathlib import Path

import pytest

from mstr_qualify.verifier.runner import (
    CommandObservation,
    VerifierRunnerError,
    hash_path,
    run_verifier_manifest,
)


class StaticExecutor:
    def __init__(self, observation: CommandObservation) -> None:
        self.observation = observation

    def run(
        self,
        *,
        argv: tuple[str, ...],
        cwd: Path,
        timeout_seconds: int,
    ) -> CommandObservation:
        assert argv == ("probe",)
        assert cwd.is_dir()
        assert timeout_seconds == 10
        return self.observation


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    (workspace / "tests").mkdir(parents=True)
    (workspace / "tests" / "probe.py").write_text(
        "def test_probe():\n    assert True\n", encoding="utf-8"
    )
    (workspace / "tests" / "guard.txt").write_text("guard\n", encoding="utf-8")
    return workspace


def _manifest(workspace: Path) -> dict[str, object]:
    return {
        "schema_version": "mstr.verifier-manifest.v0",
        "verifier_manifest_id": "fixture.a014.verifier.v0",
        "environment_id": "fixture.a014.environment.v0",
        "finalizer_contract_id": "A006_PROTECTED_FINALIZER",
        "success_semantics": "VERIFIER_EVIDENCE_ONLY",
        "verifiers": [
            {
                "verifier_id": "probe",
                "argv": ["probe"],
                "working_directory": ".",
                "timeout_seconds": 10,
                "required": True,
                "expected_exit_codes": [0],
                "source_identity": {
                    "path": "tests/probe.py",
                    "sha256": hash_path(workspace / "tests" / "probe.py"),
                },
            }
        ],
        "fixture_contract": {
            "known_good": ["fixture.good"],
            "known_bad": ["fixture.bad"],
            "noop": ["fixture.noop"],
        },
        "effect_policy": {
            "network_access": "NONE",
            "allowed_hosts": [],
            "secret_access": False,
            "allowed_secret_ids": [],
            "filesystem_writes": "WORKTREE_AND_TEMP",
            "subprocess_execution": True,
            "authority_id": None,
        },
        "protected_paths": ["tests/probe.py", "tests/guard.txt"],
    }


def test_verifier_runner_derives_pass_from_exit_code_and_identity(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    manifest = _manifest(workspace)
    record = run_verifier_manifest(
        manifest,
        workspace=workspace,
        executor=StaticExecutor(CommandObservation(exit_code=0, stdout="ok")),
    )

    assert record.passed is True
    assert len(record.results) == 1
    assert record.results[0].status == "PASS"
    assert len(record.results[0].result_identity) == 64

    repeated = run_verifier_manifest(
        manifest,
        workspace=workspace,
        executor=StaticExecutor(CommandObservation(exit_code=0, stdout="ok")),
    )
    assert repeated.results[0].result_identity == record.results[0].result_identity


def test_stdout_spoof_cannot_override_failing_exit_code(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    record = run_verifier_manifest(
        _manifest(workspace),
        workspace=workspace,
        executor=StaticExecutor(
            CommandObservation(exit_code=1, stdout="PASS: everything is green")
        ),
    )

    assert record.passed is False
    assert record.results[0].status == "FAIL"


def test_source_identity_mismatch_fails_closed(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    manifest = _manifest(workspace)
    (workspace / "tests" / "probe.py").write_text("pass\n", encoding="utf-8")

    with pytest.raises(VerifierRunnerError) as error:
        run_verifier_manifest(
            manifest,
            workspace=workspace,
            executor=StaticExecutor(CommandObservation(exit_code=0)),
        )

    assert error.value.code == "verifier.source_identity_mismatch"


def test_incomplete_effect_observation_fails_closed(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)

    with pytest.raises(VerifierRunnerError) as error:
        run_verifier_manifest(
            _manifest(workspace),
            workspace=workspace,
            executor=StaticExecutor(
                CommandObservation(exit_code=0, effect_observation_complete=False)
            ),
        )

    assert error.value.code == "verifier.effect_observation_incomplete"
