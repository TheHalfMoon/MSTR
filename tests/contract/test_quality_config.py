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


def test_schema_selfcheck_gate_requires_exit_zero() -> None:
    gates = load_quality_config()["gates"]
    gate = gates["schema_selfcheck"]
    assert isinstance(gate, dict)
    assert gate["exit_code_zero_required"] is True


def test_declared_gate_commands_run_from_repo_root() -> None:
    """Every declared gate must map to a genuinely runnable tool or CLI wiring."""

    from importlib.util import find_spec

    for tool in ("pytest", "ruff", "mypy"):
        assert find_spec(tool) is not None, f"gate tool {tool} is not runnable in this environment"

    from mstr_qualify.cli import build_parser

    parser = build_parser()
    probe = {
        "validate": ["validate"],
        "rights": ["rights", "x"],
        "candidate": ["candidate", "static", "x"],
        "manifest": ["manifest", "validate", "x"],
    }
    for subcommand, argv in probe.items():
        args = parser.parse_args(argv)
        assert getattr(args, "command", None) == subcommand
