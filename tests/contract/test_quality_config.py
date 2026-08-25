"""T011 contract tests: the frozen harness quality-gate configuration.

These tests keep `configs/quality.toml` honest: it must stay parseable,
declare exactly the four required gates with their exact frozen commands,
preserve the offline / dependency-policy / no-CI decisions recorded in T011
evidence, and contain no unrecognized gate entries.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUALITY_CONFIG = REPO_ROOT / "configs" / "quality.toml"

_REQUIRED_GATES: dict[str, str] = {
    "test_suite": "pytest -q",
    "lint": "ruff check src tests",
    "typecheck": "mypy",
    "schema_selfcheck": "python -m mstr_qualify validate",
}
_EXIT_CODE_ZERO_REQUIRED_GATES = frozenset({"schema_selfcheck"})
_APPROVED_RUNTIME_DEPENDENCIES = ["jsonschema>=4.23,<5"]


def load_quality_config() -> dict[str, object]:
    return tomllib.loads(QUALITY_CONFIG.read_text(encoding="utf-8"))


def test_quality_config_is_parseable_toml() -> None:
    data = load_quality_config()
    assert data["schema_version"] == "mstr.quality-gates.v1"


def test_all_required_gates_match_their_exact_frozen_commands() -> None:
    gates = load_quality_config()["gates"]
    assert isinstance(gates, dict)
    assert set(gates) == set(_REQUIRED_GATES), "gate set must not silently change"
    for name, expected_command in _REQUIRED_GATES.items():
        gate = gates[name]
        assert isinstance(gate, dict)
        assert gate["required"] is True, f"gate {name} must remain required"
        assert gate["command"] == expected_command, f"gate {name} command drifted"
        expect_exit_zero = name in _EXIT_CODE_ZERO_REQUIRED_GATES
        assert gate.get("exit_code_zero_required", False) is expect_exit_zero, (
            f"gate {name} exit_code_zero_required must be {expect_exit_zero}"
        )


def test_offline_discipline_remains_frozen() -> None:
    environment = load_quality_config()["environment"]
    assert isinstance(environment, dict)
    assert environment["offline_required"] is True
    assert environment["minimum_python"] == "3.11"


def test_dependency_policy_stays_fail_closed() -> None:
    policy = load_quality_config()["dependency_policy"]
    assert isinstance(policy, dict)
    assert policy["runtime_dependency_additions_require_task_authority"] is True
    assert policy["dev_tooling_may_not_become_runtime_dependency"] is True
    assert policy["approved_runtime_dependencies"] == _APPROVED_RUNTIME_DEPENDENCIES


def test_distribution_decisions_match_recorded_evidence() -> None:
    distribution = load_quality_config()["distribution"]
    assert isinstance(distribution, dict)
    # T011 evidence records that no CI workflow was added; this test fails if
    # someone flips the declaration without revisiting that evidence.
    assert distribution["ci_workflows_added"] is False
    assert distribution["model_weights_in_git"] is False


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
