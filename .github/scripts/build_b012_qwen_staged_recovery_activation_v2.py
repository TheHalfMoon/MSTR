#!/usr/bin/env python3
"""Run the staged Qwen activation builder while honoring the exact-main task-gate contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).with_name("build_b012_qwen_staged_recovery_activation.py")


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("b012_activation_builder", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load activation builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    builder = load_builder()

    def exact_main_eligibility() -> None:
        builder.run("git", "checkout", "-B", "main", "origin/main")
        if builder.output("git", "rev-parse", "HEAD") != builder.BASE:
            raise RuntimeError("exact-main eligibility checkout identity mismatch")
        if builder.output("git", "rev-parse", "refs/heads/main") != builder.BASE:
            raise RuntimeError("local main identity mismatch before eligibility")
        if builder.output("git", "rev-parse", "refs/remotes/origin/main") != builder.BASE:
            raise RuntimeError("remote main identity mismatch before eligibility")
        if builder.output("git", "status", "--porcelain"):
            raise RuntimeError("exact-main eligibility checkout is not clean")

        result = builder.run(
            "python",
            "-m",
            "mstr_qualify",
            "task",
            "eligible",
            "B012",
            check=False,
            capture=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "B012 exact-main eligibility failed closed: "
                f"exit={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        data = json.loads(result.stdout)
        assert data["task_id"] == "B012"
        assert data["canonical_main"] == builder.BASE
        assert data["eligible"] is True
        assert data["authority_result"]["satisfied"] is True
        assert data["state_consistency_result"]["observed_state"] == "PENDING"
        assert data["supersession_result"]["superseded"] is False
        assert all(item["satisfied"] for item in data["prerequisite_results"])

        builder.run("git", "checkout", "-B", builder.TARGET, f"origin/{builder.TARGET}")
        if builder.output("git", "rev-parse", "HEAD") != builder.BASE:
            raise RuntimeError("activation branch identity drift after exact-main eligibility")

    builder.assert_exact_main_b012_eligibility = exact_main_eligibility
    builder.main()


if __name__ == "__main__":
    main()
