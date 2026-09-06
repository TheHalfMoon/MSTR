#!/usr/bin/env python3
"""Frozen B012 raw-code proxy execution using pinned llama-cli."""

from __future__ import annotations

import ast
import subprocess
import time
from pathlib import Path

from mstr_b012_governance import ExecutionError
from mstr_executor_toolchain import sanitized_runtime_environment


def run_raw_code_proxy(*, executable: Path, model: Path, manifest: dict[str, object]) -> dict[str, object]:
    execution = manifest.get("execution")
    tasks = manifest.get("tasks")
    if not isinstance(execution, dict) or not isinstance(tasks, list) or not tasks:
        raise ExecutionError("B012 raw-code manifest is invalid")
    context = execution.get("context_tokens")
    generated = execution.get("generated_tokens")
    threads = execution.get("threads")
    seed = execution.get("seed")
    temperature = execution.get("temperature")
    if not isinstance(context, int) or not isinstance(generated, int) or not isinstance(threads, int) or not isinstance(seed, int):
        raise ExecutionError("B012 raw-code execution integers are invalid")
    if not isinstance(temperature, (int, float)):
        raise ExecutionError("B012 raw-code temperature is invalid")

    rows: list[dict[str, object]] = []
    for task in tasks:
        if not isinstance(task, dict):
            raise ExecutionError("B012 raw-code task is invalid")
        task_id = task.get("id")
        prompt = task.get("prompt")
        required = task.get("required_substrings")
        if not isinstance(task_id, str) or not isinstance(prompt, str) or not isinstance(required, list):
            raise ExecutionError("B012 raw-code task identity is invalid")
        argv = [
            str(executable), "-m", str(model), "-p", prompt,
            "-n", str(generated), "-c", str(context), "-t", str(threads),
            "-ngl", "0", "--temp", str(float(temperature)), "--seed", str(seed),
            "--no-display-prompt", "--simple-io",
        ]
        started = time.monotonic()
        try:
            completed = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
                check=False,
                env=sanitized_runtime_environment(),
            )
        except subprocess.TimeoutExpired as exc:
            raise ExecutionError(f"raw-code task timed out: {task_id}") from exc
        if completed.returncode != 0:
            diagnostic = (completed.stdout + "\n" + completed.stderr).strip()[-4000:]
            raise ExecutionError(f"llama-cli raw-code execution failed for {task_id}: {diagnostic}")
        completion = completed.stdout
        syntax_valid = True
        syntax_error = None
        try:
            ast.parse(prompt + completion)
        except SyntaxError as exc:
            syntax_valid = False
            syntax_error = f"{exc.msg}@{exc.lineno}:{exc.offset}"
        required_results = {str(value): str(value) in completion for value in required}
        rows.append({
            "task_id": task_id,
            "completion": completion,
            "syntax_valid": syntax_valid,
            "syntax_error": syntax_error,
            "required_substrings": required_results,
            "wall_seconds": time.monotonic() - started,
        })
    syntax_passes = sum(1 for row in rows if row["syntax_valid"] is True)
    return {
        "task_count": len(rows),
        "syntax_pass_count": syntax_passes,
        "syntax_pass_rate": syntax_passes / len(rows),
        "rows": rows,
        "interpretation": "OBSERVATIONAL_RAW_CODE_PROXY_NOT_FINAL_ADMISSION",
    }
