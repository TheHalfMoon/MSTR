#!/usr/bin/env python3
"""Run the staged-shutdown incident builder with live durable-artifact corrections."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

FAILURE_CLASS = (
    "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_PROGRESS_RAW_CODE_UNPROVEN"
)
F16_SHA256 = "198297c5988d7420ef3939911c5a8e1a018a7404e7bf6fb5e6965c3cc9a04045"
F16_SIZE_BYTES = 1557662144


def _load_builder(script: Path):
    spec = importlib.util.spec_from_file_location("b012_staged_shutdown_builder", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load builder: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--builder-script", required=True)
    args = parser.parse_args()

    module = _load_builder(Path(args.builder_script).resolve())
    module.FAILURE_CLASS = FAILURE_CLASS
    original_build_incident = module.build_incident

    def build_incident() -> dict[str, object]:
        incident = original_build_incident()
        regenerated = incident["regenerated_q4"]
        if not isinstance(regenerated, dict):
            raise RuntimeError("regenerated_q4 must be an object")
        regenerated["f16_sha256"] = F16_SHA256
        regenerated["f16_size_bytes"] = F16_SIZE_BYTES
        return incident

    module.build_incident = build_incident
    sys.argv = [
        str(Path(args.builder_script).resolve()),
        "--repo-root",
        str(Path(args.repo_root).resolve()),
    ]
    module.main()


if __name__ == "__main__":
    main()
