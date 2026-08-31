from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import mstr_qualify.environment.reset as reset_module
from mstr_qualify.environment import EnvironmentResetError


def test_wrong_origin_fails_before_reset_or_clean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "repo"
    (workspace / ".git").mkdir(parents=True)
    commands: list[tuple[str, ...]] = []

    def fake_git(
        _workspace: Path, *args: str, timeout_seconds: int
    ) -> str:
        del timeout_seconds
        commands.append(args)
        if args == ("remote", "get-url", "origin"):
            return "https://github.com/example/wrong-repository"
        raise AssertionError(f"destructive or unexpected git command executed: {args!r}")

    monkeypatch.setattr(reset_module, "_git", fake_git)
    environment: dict[str, Any] = {
        "repository_identity": {
            "repository_url": "https://github.com/example/expected-repository",
            "revision_sha": "a" * 40,
            "tree_sha": "b" * 40,
        },
        "reset_policy": {
            "mode": "HARD_RESET_CLEAN",
            "max_reset_seconds": 30,
        },
    }

    with pytest.raises(EnvironmentResetError, match="origin does not match"):
        reset_module._reset_workspace(
            workspace,
            environment,
            fresh_clone_driver=None,
        )

    assert commands == [("remote", "get-url", "origin")]
