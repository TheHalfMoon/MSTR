from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.ids import sha256_file
from mstr_qualify.runtimes.base import LoadRequest, PrefixCacheState
from mstr_qualify.runtimes.benchmark_cli import (
    BenchmarkCliError,
    BenchmarkCliProfile,
    BenchmarkCliRuntimeAdapter,
    CommandResult,
    load_benchmark_profile,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPOSITORY_ROOT / "configs" / "runtimes" / "llama-cpp-cpu.json"


def _request(artifact: Path) -> LoadRequest:
    return LoadRequest(
        artifact_id="fixture",
        artifact_sha256=sha256_file(artifact),
        format_name="gguf",
        context_length=64,
    )


def _row(argv: tuple[str, ...], **overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "build_commit": "3173a564",
        "model_filename": argv[argv.index("-m") + 1],
        "n_prompt": int(argv[argv.index("-p") + 1]),
        "n_gen": int(argv[argv.index("-n") + 1]),
        "n_threads": int(argv[argv.index("-t") + 1]),
        "n_gpu_layers": int(argv[argv.index("-ngl") + 1]),
        "avg_ns": 10,
        "avg_ts": 2.0,
    }
    row.update(overrides)
    return row


def test_profile_rejects_provider_acquisition_flags() -> None:
    with pytest.raises(BenchmarkCliError) as exc_info:
        BenchmarkCliProfile(
            runtime_id="unsafe",
            executable="llama-bench",
            upstream_repository="https://github.com/ggml-org/llama.cpp",
            upstream_revision="3173a56471c1753650cd806694145ffd6dcace67",
            model_arg="--hf-repo",
        )

    assert exc_info.value.code == "runtime.benchmark_profile_network_flag"


def test_runtime_build_commit_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def runner(argv: tuple[str, ...], _: float) -> CommandResult:
        return CommandResult(0, json.dumps([_row(argv, build_commit="deadbeef")]), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.prefill(4)
    assert exc_info.value.code == "runtime.build_identity"


def test_runtime_model_filename_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def runner(argv: tuple[str, ...], _: float) -> CommandResult:
        return CommandResult(0, json.dumps([_row(argv, model_filename="other.gguf")]), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.decode(4)
    assert exc_info.value.code == "runtime.output_model_identity"


def test_zero_token_prefill_is_explicit_noop_with_empty_cache(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)
    called = False

    def runner(_: tuple[str, ...], __: float) -> CommandResult:
        nonlocal called
        called = True
        raise AssertionError("zero-token prefill must not execute a benchmark")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))

    result = adapter.prefill(0)
    assert result.prompt_tokens == 0
    assert result.cache_state_after is PrefixCacheState.EMPTY
    assert adapter.cache_state() is PrefixCacheState.EMPTY
    assert adapter.last_observation is None
    assert called is False
