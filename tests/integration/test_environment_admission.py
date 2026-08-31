from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from mstr_qualify.environment import (
    CommandResult,
    EffectEnvelope,
    EnvironmentHealthCheckError,
    EnvironmentSetupRecord,
    ExecutorEnvelope,
    HealthCheckResult,
    ResourceEnvelope,
    admit_environment,
)


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ("git", "-C", str(repo), *args),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "fixture@example.invalid")
    _git(repo, "config", "user.name", "A013 Fixture")
    _git(repo, "remote", "add", "origin", "https://github.com/example/repository")
    (repo / "app.txt").write_text("canonical\n", encoding="utf-8")
    (repo / "protected.txt").write_text("protected\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")


def _effect() -> dict[str, object]:
    return {
        "network_access": "NONE",
        "allowed_hosts": [],
        "secret_access": False,
        "allowed_secret_ids": [],
        "filesystem_writes": "WORKTREE_AND_TEMP",
        "subprocess_execution": True,
        "authority_id": None,
    }


def _resources() -> dict[str, int]:
    return {
        "wall_clock_seconds": 60,
        "memory_mib": 512,
        "disk_mib": 512,
        "process_count": 8,
    }


def _write_manifests(
    tmp_path: Path,
    revision: str,
    tree: str,
    *,
    max_attempts: int = 2,
    health_target_ids: tuple[str, ...] = ("health.tests",),
    checker_ids: tuple[str, ...] = ("checker.tests",),
    effect: dict[str, object] | None = None,
) -> tuple[Path, Path]:
    policy = effect or _effect()
    environment = {
        "schema_version": "mstr.environment-manifest.v0",
        "environment_id": "fixture.repo.v0",
        "repository_identity": {
            "repository_url": "https://github.com/example/repository",
            "revision_sha": revision,
            "tree_sha": tree,
        },
        "setup_manifest_id": "fixture.setup.v0",
        "verifier_manifest_id": "fixture.verifier.v0",
        "reset_policy": {
            "clean_checkout_required": True,
            "mode": "HARD_RESET_CLEAN",
            "max_reset_seconds": 30,
        },
        "health_target_ids": list(health_target_ids),
        "resource_limits": _resources(),
        "effect_policy": policy,
        "protected_paths": ["protected.txt"],
    }
    setup = {
        "schema_version": "mstr.setup-manifest.v0",
        "setup_manifest_id": "fixture.setup.v0",
        "environment_id": "fixture.repo.v0",
        "clean_state_required": True,
        "max_attempts": max_attempts,
        "steps": [
            {
                "step_id": "fixture-setup",
                "argv": ["fixture-setup"],
                "working_directory": ".",
                "timeout_seconds": 10,
            }
        ],
        "health_target_ids": list(health_target_ids),
        "independent_checker_ids": list(checker_ids),
        "resource_limits": _resources(),
        "effect_policy": policy,
    }
    env_path = tmp_path / "environment.json"
    setup_path = tmp_path / "setup.json"
    env_path.write_text(json.dumps(environment), encoding="utf-8")
    setup_path.write_text(json.dumps(setup), encoding="utf-8")
    return env_path, setup_path


def _executor_envelope(effect: dict[str, object] | None = None) -> ExecutorEnvelope:
    policy = effect or _effect()
    return ExecutorEnvelope(
        effects=EffectEnvelope.from_mapping(policy),
        resources=ResourceEnvelope.from_mapping(_resources()),
    )


def _checker_effects() -> EffectEnvelope:
    return EffectEnvelope(
        network_access="NONE",
        allowed_hosts=(),
        secret_access=False,
        allowed_secret_ids=(),
        filesystem_writes="NONE",
        subprocess_execution=False,
        authority_id=None,
    )


@dataclass
class SequenceExecutor:
    envelope: ExecutorEnvelope
    exit_codes: tuple[int, ...] = (0,)
    calls: int = 0
    clean_retry_observed: bool = False

    def run(self, argv: tuple[str, ...], *, cwd: Path, timeout_seconds: int) -> CommandResult:
        assert argv == ("fixture-setup",)
        assert timeout_seconds <= 10
        self.calls += 1
        if self.calls > 1:
            assert not (cwd / "attempt-1.marker").exists()
            self.clean_retry_observed = True
        (cwd / f"attempt-{self.calls}.marker").write_text("setup\n", encoding="utf-8")
        index = min(self.calls - 1, len(self.exit_codes) - 1)
        exit_code = self.exit_codes[index]
        return CommandResult(
            exit_code=exit_code,
            stderr="fixture setup failure" if exit_code else "",
        )


@dataclass
class SequenceChecker:
    checker_id: str
    target_id: str
    outcomes: tuple[bool, ...]
    effects: EffectEnvelope = field(default_factory=_checker_effects)
    calls: int = 0
    raise_on_calls: tuple[int, ...] = ()

    def check(
        self,
        *,
        workspace: Path,
        setup_record: EnvironmentSetupRecord,
    ) -> HealthCheckResult:
        self.calls += 1
        assert setup_record.admission_status == "NOT_EVALUATED_A013"
        assert workspace.exists()
        if self.calls in self.raise_on_calls:
            raise EnvironmentHealthCheckError(
                "fixture checker execution failed",
                code="fixture.checker_failure",
            )
        index = min(self.calls - 1, len(self.outcomes) - 1)
        passed = self.outcomes[index]
        return HealthCheckResult(
            checker_id=self.checker_id,
            target_id=self.target_id,
            passed=passed,
            detail="fixture pass" if passed else "fixture fail",
        )


def _fixture_cases() -> dict[str, dict[str, object]]:
    path = Path(__file__).parents[1] / "fixtures" / "environment" / "admission-cases.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


@pytest.mark.parametrize("case_name", sorted(_fixture_cases()))
def test_bounded_admission_fixture_matrix(tmp_path: Path, case_name: str) -> None:
    case = _fixture_cases()[case_name]
    repo, revision, tree = _repo(tmp_path)
    max_attempts = int(case["max_attempts"])
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        max_attempts=max_attempts,
    )
    executor = SequenceExecutor(_executor_envelope())
    checker = SequenceChecker(
        "checker.tests",
        "health.tests",
        tuple(bool(item) for item in case["checker_outcomes"]),
    )

    record = admit_environment(
        repo,
        env_path,
        setup_path,
        executor=executor,
        checkers=(checker,),
    )

    expected_attempts = int(case["expected_attempts"])
    expected_status = str(case["expected_status"])
    assert record.status == expected_status
    assert len(record.attempts) == expected_attempts
    assert executor.calls == expected_attempts
    assert checker.calls == expected_attempts
    assert record.max_attempts == max_attempts
    assert record.repository_revision == revision
    assert record.repository_tree == tree
    assert record.verifier_manifest_id == "fixture.verifier.v0"
    if expected_status == "ADMITTED":
        assert record.admitted_attempt == expected_attempts
        assert record.attempts[-1].passed is True
    else:
        assert record.admitted_attempt is None
        assert all(attempt.passed is False for attempt in record.attempts)
    if expected_attempts > 1:
        assert executor.clean_retry_observed is True


def test_setup_failure_is_recorded_then_retried_from_clean_state(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree, max_attempts=2)
    executor = SequenceExecutor(_executor_envelope(), exit_codes=(7, 0))
    checker = SequenceChecker("checker.tests", "health.tests", (True,))

    record = admit_environment(
        repo,
        env_path,
        setup_path,
        executor=executor,
        checkers=(checker,),
    )

    assert record.status == "ADMITTED"
    assert record.admitted_attempt == 2
    assert len(record.attempts) == 2
    assert record.attempts[0].setup_record is None
    assert record.attempts[0].failure_code is not None
    assert record.attempts[0].checks == ()
    assert record.attempts[1].passed is True
    assert executor.calls == 2
    assert checker.calls == 1
    assert executor.clean_retry_observed is True


def test_every_declared_health_target_must_pass_in_same_attempt(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        max_attempts=2,
        health_target_ids=("health.tests", "health.lint"),
        checker_ids=("checker.tests", "checker.lint"),
    )
    executor = SequenceExecutor(_executor_envelope())
    test_checker = SequenceChecker("checker.tests", "health.tests", (True, True))
    lint_checker = SequenceChecker("checker.lint", "health.lint", (False, False))

    record = admit_environment(
        repo,
        env_path,
        setup_path,
        executor=executor,
        checkers=(test_checker, lint_checker),
    )

    assert record.status == "REJECTED"
    assert record.admitted_attempt is None
    assert len(record.attempts) == 2
    assert all(len(attempt.checks) == 2 for attempt in record.attempts)
    assert all(attempt.failure_code == "environment.health_target_failed" for attempt in record.attempts)
    assert executor.clean_retry_observed is True


def test_typed_checker_failure_is_evidence_and_can_recover(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree, max_attempts=2)
    executor = SequenceExecutor(_executor_envelope())
    checker = SequenceChecker(
        "checker.tests",
        "health.tests",
        (True, True),
        raise_on_calls=(1,),
    )

    record = admit_environment(
        repo,
        env_path,
        setup_path,
        executor=executor,
        checkers=(checker,),
    )

    assert record.status == "ADMITTED"
    assert record.admitted_attempt == 2
    first_result = record.attempts[0].checks[0]
    assert first_result.passed is False
    assert first_result.error_code == "fixture.checker_failure"
    assert record.attempts[1].passed is True
    assert executor.clean_retry_observed is True
