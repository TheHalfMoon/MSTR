#!/usr/bin/env python3
"""T031 exact F16/Q4 regeneration and pinned llama.cpp build identities."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

from mstr_executor_toolchain import (
    clone_exact_commit,
    require_file_sha256,
    sanitized_runtime_environment,
)
from mstr_t031_governance import ExecutionError, _run


def _quantize(
    *,
    python_exe: Path,
    conversion_dir: Path,
    quantize_bin: Path,
    source_dir: Path,
    q4_profile: dict[str, object],
    workdir: Path,
) -> tuple[Path, dict[str, object]]:
    f16 = workdir / "model-f16.gguf"
    started = time.monotonic()
    _run(
        [
            str(python_exe),
            str(conversion_dir / "convert_hf_to_gguf.py"),
            str(source_dir),
            "--outfile",
            str(f16),
            "--outtype",
            "f16",
        ],
        timeout=3600,
        env=sanitized_runtime_environment(),
    )
    conversion_seconds = time.monotonic() - started
    expected_f16_sha = q4_profile.get("f16_sha256")
    expected_f16_size = q4_profile.get("f16_size_bytes")
    if not isinstance(expected_f16_sha, str) or not isinstance(expected_f16_size, int):
        raise ExecutionError("canonical T029 F16 identity is invalid")
    require_file_sha256(f16, expected_f16_sha)
    if f16.stat().st_size != expected_f16_size:
        raise ExecutionError("regenerated F16 size does not match canonical T029 identity")

    shutil.rmtree(source_dir, ignore_errors=True)
    arms_raw = q4_profile.get("quantization_arms")
    if not isinstance(arms_raw, dict):
        raise ExecutionError("canonical T029 quantization arms are missing")

    retained: Path | None = None
    arm_records: dict[str, object] = {}
    for arm in ("Q4_K_M", "Q4_K_S"):
        expected = arms_raw.get(arm)
        if not isinstance(expected, dict):
            raise ExecutionError(f"canonical T029 arm missing: {arm}")
        expected_sha = expected.get("output_sha256")
        expected_size = expected.get("output_size_bytes")
        if not isinstance(expected_sha, str) or not isinstance(expected_size, int):
            raise ExecutionError(f"canonical T029 arm identity invalid: {arm}")
        output = workdir / f"model-{arm.lower()}.gguf"
        started = time.monotonic()
        _run(
            [str(quantize_bin), str(f16), str(output), arm],
            timeout=2400,
            env=sanitized_runtime_environment(),
        )
        duration = time.monotonic() - started
        require_file_sha256(output, expected_sha)
        if output.stat().st_size != expected_size:
            raise ExecutionError(f"regenerated {arm} size does not match canonical T029 identity")
        arm_records[arm] = {
            "sha256": expected_sha,
            "size_bytes": expected_size,
            "regeneration_seconds": duration,
            "identity_match": True,
        }
        if arm == "Q4_K_M":
            retained = output
        else:
            output.unlink(missing_ok=True)

    f16.unlink(missing_ok=True)
    if retained is None:
        raise ExecutionError("Q4_K_M primary measurement artifact was not produced")
    return retained, {
        "f16_sha256": expected_f16_sha,
        "f16_size_bytes": expected_f16_size,
        "conversion_seconds": conversion_seconds,
        "arms": arm_records,
    }


def _prepare_llama_cpp(
    *, lock: dict[str, object], workdir: Path
) -> tuple[Path, Path, Path, dict[str, object]]:
    llama_cpp = lock.get("llama_cpp")
    if not isinstance(llama_cpp, dict):
        raise ExecutionError("llama_cpp toolchain lock is missing")
    repository = llama_cpp.get("repository")
    conversion_commit = llama_cpp.get("conversion_quantization_commit")
    runtime_commit = llama_cpp.get("runtime_commit")
    build_flags = llama_cpp.get("build_flags")
    if not isinstance(repository, str) or not isinstance(conversion_commit, str):
        raise ExecutionError("conversion tool identity is invalid")
    if not isinstance(runtime_commit, str) or not isinstance(build_flags, list):
        raise ExecutionError("runtime tool identity is invalid")
    if not all(isinstance(item, str) for item in build_flags):
        raise ExecutionError("build flags must be strings")

    conversion_dir = workdir / "llama-convert"
    quantizer = clone_exact_commit(
        repository=repository,
        commit=conversion_commit,
        destination=conversion_dir,
        build_flags=build_flags,
        target="llama-quantize",
    )
    tools_dir = workdir / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    quantizer_copy = tools_dir / "llama-quantize"
    shutil.copy2(quantizer, quantizer_copy)
    shutil.rmtree(conversion_dir / "build", ignore_errors=True)
    shutil.rmtree(conversion_dir / ".git", ignore_errors=True)

    runtime_dir = workdir / "llama-runtime"
    runtime = clone_exact_commit(
        repository=repository,
        commit=runtime_commit,
        destination=runtime_dir,
        build_flags=build_flags,
        target="llama-bench",
    )
    runtime_copy = tools_dir / "llama-bench"
    shutil.copy2(runtime, runtime_copy)
    shutil.rmtree(runtime_dir, ignore_errors=True)
    return conversion_dir, quantizer_copy, runtime_copy, {
        "repository": repository,
        "conversion_quantization_commit": conversion_commit,
        "runtime_commit": runtime_commit,
        "build_flags": build_flags,
    }
