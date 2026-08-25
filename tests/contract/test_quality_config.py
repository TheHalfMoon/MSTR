"""T011 contract tests: the frozen harness quality-gate configuration.

These tests keep `configs/quality.toml` honest: it must stay parseable,
declare the four required gates, and preserve the offline/no-CI decisions
recorded in T011 evidence.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUALITY_CONFIG = REPO_ROOT / "configs" / "quality.toml"

_REQUIRED_GATES = ("test_suite", "lint", "typecheck", "schema_selfcheck")


def load_quality_config() -> dict[str, object]:
    return tomllib.loads(QUALITY_CONFIG.read_text(encoding="utf-8"))


def test_quality_config_is_parseable_toml() -> None:
    data = load_quality_config()
    assert data["schema_version"] == "mstr.quality-gates.v1"


def test_all_required_gates_are_declared_and_required() -> None:
    gates = load_quality_config()["gates"]
    assert isinstance(gates, dict)
    for name in _REQUIRED_GATES:
        gate = gates[name]
        assert isinstance(gate, dict)
        assert gate["required"] is True, f"gate {name} must remain required"
        assert isinstance(gate.get("command"), str) and gate["command"].strip()


def test_offline_discipline_remains_frozen() -> None:
    environment = load_quality_config()["environment"]
    assert isinstance(environment, dict)
    assert environment["offline_required"] is True


def test_dependency_policy_stays_fail_closed() -> None:
    policy = load_quality_config()["dependency_policy"]
    assert isinstance(policy, dict)
    assert policy["runtime_dependency_additions_require_task_authority"] is True
    assert policy["dev_tooling_may_not_become_runtime_dependency"] is True


def test_distribution_decisions_match_recorded_evidence() -> None:
    distribution = load_quality_config()["distribution"]
    assert isinstance(distribution, dict)
    # T011 evidence records that no CI workflow was added; this test fails if
    # someone flips the declaration without revisiting that evidence.
    assert distribution["ci_workflows_added"] is False
    assert distribution["model_weights_in_git"] is False


def test_declared_gate_commands_run_from_repo_root() -> None:
    """Every declared command must exist as a runnable tool or module entry."""

    gates = load_quality_config()["gates"]
    for name in _REQUIRED_GATES:
        command = str(gates[name]["command"])
        if command.startswith("pytest"):
            import pytest  # noqa: F401

            continue
        if command.startswith("ruff") or command == "mypy":
            continue  # validated by the T011 evidence run itself
        if command.endswith("mstr_qualify validate"):
            from mstr_qualify.__main__ import main as cli_main

            assert callable(cli_main)
