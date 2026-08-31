from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from mstr_qualify.environment import (
    CommandResult,
    EffectEnvelope,
    EnvironmentResetError,
    ExecutorEnvelope,
    ResourceEnvelope,
    prepare_environment,
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
    _git(repo, "config", "user.name", "A012 Fixture")
    _git(repo, "remote", "add", "origin", "https://github.com/example/repository")
    (repo / ".gitignore").write_text("ignored-protected.txt\n", encoding="utf-8")
    (repo / "protected.txt").write_text("protected\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")


def _effect(
    *,
    network: str = "NONE",
    secret_access: bool = False,
    authority_id: str | None = None,
) -> dict[str, object]:
    return {
        "network_access": network,
        "allowed_hosts": [] if network == "NONE" else ["packages.example.invalid"],
        "secret_access": secret_access,
        "allowed_secret_ids": ["fixture.secret"] if secret_access else [],
        "filesystem_writes": "WORKTREE_AND_TEMP",
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
    revision: str,
    tree: str,
    *,
    effect: dict[str, object] | None = None,
    reset_mode: str = "HARD_RESET_CLEAN",
    protected_paths: tuple[str, ...] = ("protected.txt",),
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
            "mode": reset_mode,
            "max_reset_seconds": 30,
        },
        "health_target_ids": ["health.tests"],
        "resource_limits": _resources(),
        "effect_policy": policy,
        "protected_paths": list(protected_paths),
    }
    setup = {
        "schema_version": "mstr.setup-manifest.v0",
        "setup_manifest_id": "fixture.setup.v0",
        "environment_id": "fixture.repo.v0",
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
        "effect_policy": policy,
    }
    env_path = tmp_path / "environment.json"
    setup_path = tmp_path / "setup.json"
    env_path.write_text(json.dumps(environment), encoding="utf-8")
    setup_path.write_text(json.dumps(setup), encoding="utf-8")
    return env_path, setup_path


@dataclass
class FixtureExecutor:
    envelope: ExecutorEnvelope
    touch_protected: bool = False
    touch_ignored_protected: bool = False

    def run(self, argv: tuple[str, ...], *, cwd: Path, timeout_seconds: int) -> CommandResult:
        assert argv == ("fixture-setup",)
        assert timeout_seconds <= 10
        if self.touch_protected:
            (cwd / "protected.txt").write_text("tampered\n", encoding="utf-8")
        if self.touch_ignored_protected:
            (cwd / "ignored-protected.txt").write_text("tampered\n", encoding="utf-8")
        return CommandResult(exit_code=0)


@dataclass
class FixtureCloneDriver:
    envelope: ExecutorEnvelope

    def materialize(
        self,
        repository_url: str,
        revision_sha: str,
        destination: Path,
        *,
        timeout_seconds: int,
    ) -> None:
        del repository_url, revision_sha, destination, timeout_seconds
        raise AssertionError("mismatched clone driver must be rejected before materialize")


def _envelope(effect: dict[str, object] | None = None) -> ExecutorEnvelope:
    policy = effect or _effect()
    return ExecutorEnvelope(
        effects=EffectEnvelope.from_mapping(policy),
        resources=ResourceEnvelope.from_mapping(_resources()),
    )


def test_network_effects_are_rejected_by_local_a012_boundary(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    effect = _effect(network="ALLOWLIST", authority_id="AUTH-NET-1")
    env_path, setup_path = _write_manifests(tmp_path, revision, tree, effect=effect)

    with pytest.raises(EnvironmentResetError, match="does not authorize network or secret effects"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(effect)),
        )


def test_secret_effects_are_rejected_by_local_a012_boundary(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    effect = _effect(secret_access=True, authority_id="AUTH-SECRET-1")
    env_path, setup_path = _write_manifests(tmp_path, revision, tree, effect=effect)

    with pytest.raises(EnvironmentResetError, match="does not authorize network or secret effects"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(effect)),
        )


def test_executor_must_enforce_exact_effect_and_resource_envelope(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree)
    mismatched = _effect(network="ALLOWLIST", authority_id="AUTH-NET-1")

    with pytest.raises(EnvironmentResetError, match="does not enforce the exact manifest envelope"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(mismatched)),
        )


def test_setup_cannot_modify_tracked_protected_path(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree)

    with pytest.raises(EnvironmentResetError, match="modified a protected path"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(), touch_protected=True),
        )


def test_setup_cannot_create_git_ignored_protected_path(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        protected_paths=("ignored-protected.txt",),
    )

    with pytest.raises(EnvironmentResetError, match="modified a protected path"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(), touch_ignored_protected=True),
        )


def test_fresh_clone_has_no_implicit_network_driver(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        reset_mode="FRESH_CLONE",
    )

    with pytest.raises(EnvironmentResetError, match="does not open network implicitly"):
        prepare_environment(repo, env_path, setup_path, executor=FixtureExecutor(_envelope()))


def test_fresh_clone_driver_must_enforce_exact_envelope(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        reset_mode="FRESH_CLONE",
    )
    mismatched = ExecutorEnvelope(
        effects=EffectEnvelope.from_mapping(_effect()),
        resources=ResourceEnvelope(
            wall_clock_seconds=59,
            memory_mib=512,
            disk_mib=512,
            process_count=8,
        ),
    )

    with pytest.raises(EnvironmentResetError, match="clone driver does not enforce"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope()),
            fresh_clone_driver=FixtureCloneDriver(mismatched),
        )
