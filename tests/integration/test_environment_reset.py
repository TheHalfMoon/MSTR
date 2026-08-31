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
    (repo / "app.txt").write_text("canonical\n", encoding="utf-8")
    (repo / "protected.txt").write_text("protected\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "fixture")
    return repo, _git(repo, "rev-parse", "HEAD"), _git(repo, "rev-parse", "HEAD^{tree}")


def _effect(*, network: str = "NONE", authority_id: str | None = None) -> dict[str, object]:
    return {
        "network_access": network,
        "allowed_hosts": [] if network == "NONE" else ["packages.example.invalid"],
        "secret_access": False,
        "allowed_secret_ids": [],
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
    setup_environment_id: str = "fixture.repo.v0",
    reset_mode: str = "HARD_RESET_CLEAN",
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
    exit_code: int = 0
    touch_protected: bool = False

    def run(self, argv: tuple[str, ...], *, cwd: Path, timeout_seconds: int) -> CommandResult:
        assert argv == ("fixture-setup",)
        assert timeout_seconds <= 10
        if self.touch_protected:
            (cwd / "protected.txt").write_text("tampered\n", encoding="utf-8")
        else:
            (cwd / "generated.txt").write_text("ready\n", encoding="utf-8")
        return CommandResult(
            exit_code=self.exit_code,
            stderr="fixture failure" if self.exit_code else "",
        )


def _envelope(effect: dict[str, object] | None = None) -> ExecutorEnvelope:
    policy = effect or _effect()
    return ExecutorEnvelope(
        effects=EffectEnvelope.from_mapping(policy),
        resources=ResourceEnvelope.from_mapping(_resources()),
    )


def test_hard_reset_restores_exact_checkout_then_runs_setup(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree)
    (repo / "app.txt").write_text("dirty\n", encoding="utf-8")
    (repo / "junk.txt").write_text("junk\n", encoding="utf-8")

    record = prepare_environment(
        repo,
        env_path,
        setup_path,
        executor=FixtureExecutor(_envelope()),
    )

    assert (repo / "app.txt").read_text(encoding="utf-8") == "canonical\n"
    assert not (repo / "junk.txt").exists()
    assert (repo / "generated.txt").read_text(encoding="utf-8") == "ready\n"
    assert record.repository_revision == revision
    assert record.repository_tree == tree
    assert record.reset_mode == "HARD_RESET_CLEAN"
    assert record.health_target_ids == ("health.tests",)
    assert record.independent_checker_ids == ("checker.tests",)
    assert record.admission_status == "NOT_EVALUATED_A013"
    assert record.setup_steps[0].step_id == "fixture-setup"


def test_manifest_cross_binding_fails_closed(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(
        tmp_path,
        revision,
        tree,
        setup_environment_id="other.environment",
    )

    with pytest.raises(EnvironmentResetError, match="manifest binding mismatch"):
        prepare_environment(repo, env_path, setup_path, executor=FixtureExecutor(_envelope()))


def test_wrong_tree_identity_fails_after_reset(tmp_path: Path) -> None:
    repo, revision, _tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, "f" * 40)

    with pytest.raises(EnvironmentResetError, match="tree does not match"):
        prepare_environment(repo, env_path, setup_path, executor=FixtureExecutor(_envelope()))


def test_setup_failure_is_not_admitted(tmp_path: Path) -> None:
    repo, revision, tree = _repo(tmp_path)
    env_path, setup_path = _write_manifests(tmp_path, revision, tree)

    with pytest.raises(EnvironmentResetError, match="setup step failed"):
        prepare_environment(
            repo,
            env_path,
            setup_path,
            executor=FixtureExecutor(_envelope(), exit_code=7),
        )
