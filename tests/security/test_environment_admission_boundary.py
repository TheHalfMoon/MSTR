from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from mstr_qualify.environment import (
    CommandResult,
    EffectEnvelope,
    EnvironmentAdmissionError,
    EnvironmentSetupRecord,
    ExecutorEnvelope,
    HealthCheckResult,
    ResourceEnvelope,
    admit_environment,
)


def _effect(
    *,
    network_access: str = "NONE",
    filesystem_writes: str = "WORKTREE_AND_TEMP",
    authority_id: str | None = None,
) -> dict[str, object]:
    return {
        "network_access": network_access,
        "allowed_hosts": [] if network_access == "NONE" else ["packages.example.invalid"],
        "secret_access": False,
        "allowed_secret_ids": [],
        "filesystem_writes": filesystem_writes,
        "subprocess_execution": True,
        "authority_id": authority_id,
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
    *,
    environment_effect: dict[str, object] | None = None,
    setup_effect: dict[str, object] | None = None,
    setup_environment_id: str = "fixture.repo.v0",
) -> tuple[Path, Path]:
    env_effect = environment_effect or _effect()
    set_effect = setup_effect or env_effect
    environment = {
        "schema_version": "mstr.environment-manifest.v0",
        "environment_id": "fixture.repo.v0",
        "repository_identity": {
            "repository_url": "https://github.com/example/repository",
            "revision_sha": "a" * 40,
            "tree_sha": "b" * 40,
        },
        "setup_manifest_id": "fixture.setup.v0",
        "verifier_manifest_id": "fixture.verifier.v0",
        "reset_policy": {
            "clean_checkout_required": True,
            "mode": "HARD_RESET_CLEAN",
            "max_reset_seconds": 30,
        },
        "health_target_ids": ["health.tests"],
        "resource_limits": _resources(),
        "effect_policy": env_effect,
        "protected_paths": ["protected.txt"],
    }
    setup = {
        "schema_version": "mstr.setup-manifest.v0",
        "setup_manifest_id": "fixture.setup.v0",
        "environment_id": setup_environment_id,
        "clean_state_required": True,
        "max_attempts": 2,
        "steps": [
            {
                "step_id": "fixture-setup",
                "argv": ["fixture-setup"],
                "working_directory": ".",
                "timeout_seconds": 10,
            }
        ],
        "health_target_ids": ["health.tests"],
        "independent_checker_ids": ["checker.tests"],
        "resource_limits": _resources(),
        "effect_policy": set_effect,
    }
    env_path = tmp_path / "environment.json"
    setup_path = tmp_path / "setup.json"
    env_path.write_text(json.dumps(environment), encoding="utf-8")
    setup_path.write_text(json.dumps(setup), encoding="utf-8")
    return env_path, setup_path


def _executor_envelope() -> ExecutorEnvelope:
    return ExecutorEnvelope(
        effects=EffectEnvelope.from_mapping(_effect()),
        resources=ResourceEnvelope.from_mapping(_resources()),
    )


def _checker_effects(
    *,
    network_access: str = "NONE",
    filesystem_writes: str = "NONE",
    authority_id: str | None = None,
) -> EffectEnvelope:
    return EffectEnvelope(
        network_access=network_access,
        allowed_hosts=() if network_access == "NONE" else ("packages.example.invalid",),
        secret_access=False,
        allowed_secret_ids=(),
        filesystem_writes=filesystem_writes,
        subprocess_execution=False,
        authority_id=authority_id,
    )


@dataclass
class CountingExecutor:
    envelope: ExecutorEnvelope
    calls: int = 0

    def run(self, argv: tuple[str, ...], *, cwd: Path, timeout_seconds: int) -> CommandResult:
        self.calls += 1
        return CommandResult(exit_code=0)


@dataclass
class StaticChecker:
    checker_id: str = "checker.tests"
    target_id: str = "health.tests"
    effects: EffectEnvelope = _checker_effects()

    def check(
        self,
        *,
        workspace: Path,
        setup_record: EnvironmentSetupRecord,
    ) -> HealthCheckResult:
        return HealthCheckResult(
            checker_id=self.checker_id,
            target_id=self.target_id,
            passed=True,
        )


def test_missing_checker_fails_before_setup_execution(tmp_path: Path) -> None:
    env_path, setup_path = _write_manifests(tmp_path)
    executor = CountingExecutor(_executor_envelope())

    with pytest.raises(EnvironmentAdmissionError, match="checker ids do not match"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(),
        )

    assert executor.calls == 0


def test_undeclared_checker_target_fails_before_setup_execution(tmp_path: Path) -> None:
    env_path, setup_path = _write_manifests(tmp_path)
    executor = CountingExecutor(_executor_envelope())
    checker = StaticChecker(target_id="health.undeclared")

    with pytest.raises(EnvironmentAdmissionError, match="undeclared health targets"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(checker,),
        )

    assert executor.calls == 0


def test_checker_network_effects_are_rejected_before_setup(tmp_path: Path) -> None:
    env_path, setup_path = _write_manifests(tmp_path)
    executor = CountingExecutor(_executor_envelope())
    checker = StaticChecker(effects=_checker_effects(network_access="ALLOWLIST"))

    with pytest.raises(EnvironmentAdmissionError, match="network-isolated"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(checker,),
        )

    assert executor.calls == 0


def test_checker_worktree_write_effects_are_rejected_before_setup(tmp_path: Path) -> None:
    env_path, setup_path = _write_manifests(tmp_path)
    executor = CountingExecutor(_executor_envelope())
    checker = StaticChecker(effects=_checker_effects(filesystem_writes="WORKTREE_AND_TEMP"))

    with pytest.raises(EnvironmentAdmissionError, match="worktree read-only"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(checker,),
        )

    assert executor.calls == 0


def test_network_bearing_environment_is_rejected_before_setup(tmp_path: Path) -> None:
    network_effect = _effect(network_access="ALLOWLIST", authority_id="AUTH-NET-TEST")
    env_path, setup_path = _write_manifests(
        tmp_path,
        environment_effect=network_effect,
        setup_effect=network_effect,
    )
    executor = CountingExecutor(
        ExecutorEnvelope(
            effects=EffectEnvelope.from_mapping(network_effect),
            resources=ResourceEnvelope.from_mapping(_resources()),
        )
    )

    with pytest.raises(EnvironmentAdmissionError, match="does not authorize network"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(StaticChecker(),),
        )

    assert executor.calls == 0


def test_manifest_binding_mismatch_fails_before_setup(tmp_path: Path) -> None:
    env_path, setup_path = _write_manifests(
        tmp_path,
        setup_environment_id="other.environment",
    )
    executor = CountingExecutor(_executor_envelope())

    with pytest.raises(EnvironmentAdmissionError, match="admission binding mismatch"):
        admit_environment(
            tmp_path / "unused",
            env_path,
            setup_path,
            executor=executor,
            checkers=(StaticChecker(),),
        )

    assert executor.calls == 0
