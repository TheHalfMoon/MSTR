#!/usr/bin/env python3
"""B012 deterministic conversion, Q4 generation, and llama.cpp tool preparation."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from mstr_b012_governance import ExecutionError, _run
from mstr_executor_toolchain import clone_exact_commit, sanitized_runtime_environment, sha256_file


def _fim_tokens(tokenizer_path: Path) -> list[str]:
    payload = json.loads(tokenizer_path.read_text(encoding="utf-8"))
    found: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, str) and "fim" in value.lower():
            found.add(value)
        elif isinstance(value, dict):
            for key, child in value.items():
                if isinstance(key, str) and "fim" in key.lower():
                    found.add(key)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return sorted(found)


def _contains_bytes(path: Path, needle: bytes) -> bool:
    if not needle:
        return True
    overlap = max(0, len(needle) - 1)
    carry = b""
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            data = carry + chunk
            if needle in data:
                return True
            carry = data[-overlap:] if overlap else b""
    return False


def prepare_tools(*, lock: dict[str, object], workdir: Path) -> tuple[Path, Path, Path, Path, dict[str, object]]:
    llama = lock.get("llama_cpp")
    if not isinstance(llama, dict):
        raise ExecutionError("B012 llama.cpp lock is missing")
    repository = llama.get("repository")
    conversion_commit = llama.get("conversion_quantization_commit")
    runtime_commit = llama.get("runtime_commit")
    build_flags = llama.get("build_flags")
    if not isinstance(repository, str) or not isinstance(conversion_commit, str) or not isinstance(runtime_commit, str):
        raise ExecutionError("B012 llama.cpp identity is invalid")
    if not isinstance(build_flags, list) or not all(isinstance(item, str) for item in build_flags):
        raise ExecutionError("B012 llama.cpp build flags are invalid")

    conversion_dir = workdir / "llama-convert"
    quantizer = clone_exact_commit(
        repository=repository,
        commit=conversion_commit,
        destination=conversion_dir,
        build_flags=build_flags,
        target="llama-quantize",
    )
    tools = workdir / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    quantizer_copy = tools / "llama-quantize"
    shutil.copy2(quantizer, quantizer_copy)
    shutil.rmtree(conversion_dir / "build", ignore_errors=True)
    shutil.rmtree(conversion_dir / ".git", ignore_errors=True)

    runtime_dir = workdir / "llama-runtime"
    bench = clone_exact_commit(
        repository=repository,
        commit=runtime_commit,
        destination=runtime_dir,
        build_flags=build_flags,
        target="llama-bench",
    )
    _run(
        ["cmake", "--build", str(runtime_dir / "build"), "--target", "llama-cli", "-j", "4"],
        timeout=1200,
        env=sanitized_runtime_environment(),
    )
    cli = runtime_dir / "build" / "bin" / "llama-cli"
    if not cli.is_file():
        raise ExecutionError("llama-cli build output is missing")
    bench_copy = tools / "llama-bench"
    cli_copy = tools / "llama-cli"
    shutil.copy2(bench, bench_copy)
    shutil.copy2(cli, cli_copy)
    shutil.rmtree(runtime_dir, ignore_errors=True)
    return conversion_dir, quantizer_copy, bench_copy, cli_copy, {
        "repository": repository,
        "conversion_quantization_commit": conversion_commit,
        "runtime_commit": runtime_commit,
        "build_flags": build_flags,
    }


def convert_quantize(*, python_exe: Path, conversion_dir: Path, quantize_bin: Path, source_dir: Path, candidate_id: str, workdir: Path) -> tuple[Path, dict[str, object]]:
    tokenizer = source_dir / "tokenizer.json"
    if not tokenizer.is_file():
        raise ExecutionError("source tokenizer.json is missing")
    fim_tokens = _fim_tokens(tokenizer)
    f16 = workdir / f"{candidate_id}-f16.gguf"
    started = time.monotonic()
    _run(
        [str(python_exe), str(conversion_dir / "convert_hf_to_gguf.py"), str(source_dir), "--outfile", str(f16), "--outtype", "f16"],
        timeout=3600,
        env=sanitized_runtime_environment(),
    )
    conversion_seconds = time.monotonic() - started
    if not f16.is_file() or f16.stat().st_size <= 0:
        raise ExecutionError("B012 F16 conversion produced no artifact")
    f16_sha = sha256_file(f16)
    f16_size = f16.stat().st_size
    shutil.rmtree(source_dir, ignore_errors=True)

    arms: dict[str, object] = {}
    retained: Path | None = None
    for arm in ("Q4_K_M", "Q4_K_S"):
        output = workdir / f"{candidate_id}-{arm.lower()}.gguf"
        started = time.monotonic()
        _run([str(quantize_bin), str(f16), str(output), arm], timeout=2400, env=sanitized_runtime_environment())
        if not output.is_file() or output.stat().st_size <= 0:
            raise ExecutionError(f"B012 {arm} quantization produced no artifact")
        record = {
            "sha256": sha256_file(output),
            "size_bytes": output.stat().st_size,
            "regeneration_seconds": time.monotonic() - started,
        }
        arms[arm] = record
        if arm == "Q4_K_M":
            retained = output
        else:
            output.unlink(missing_ok=True)
    f16.unlink(missing_ok=True)
    if retained is None:
        raise ExecutionError("B012 Q4_K_M primary artifact is missing")

    fim_observed = {token: _contains_bytes(retained, token.encode("utf-8")) for token in fim_tokens}
    if candidate_id == "mellum-4b":
        if not fim_tokens:
            raise ExecutionError("Mellum source tokenizer exposed no FIM token identity")
        if not all(fim_observed.values()):
            raise ExecutionError("Mellum FIM token export preservation failed")
    return retained, {
        "f16_sha256": f16_sha,
        "f16_size_bytes": f16_size,
        "conversion_seconds": conversion_seconds,
        "quantization_arms": arms,
        "source_fim_tokens": fim_tokens,
        "q4_k_m_fim_token_presence": fim_observed,
        "fim_export_required": candidate_id == "mellum-4b",
    }
