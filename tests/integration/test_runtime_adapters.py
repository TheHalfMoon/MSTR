"""Integration tests for the T030 portable runtime-adapter surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.ids import sha256_file
from mstr_qualify.runtimes import (
    BenchmarkCliRuntimeAdapter,
    CommandResult,
    LifecycleState,
    LoadRequest,
    PrefixCacheState,
    load_benchmark_profile,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPOSITORY_ROOT / "configs" / "runtimes" / "llama-cpp-cpu.json"


def _request(artifact: Path) -> LoadRequest:
    return LoadRequest(
        artifact_id="integration-fixture-gguf",
        artifact_sha256=sha256_file(artifact),
        format_name="gguf",
        context_length=8192,
    )


def _deterministic_llama_bench(calls: list[tuple[str, ...]]):
    def run(argv: tuple[str, ...], timeout_seconds: float) -> CommandResult:
        assert timeout_seconds == 30.0
        calls.append(argv)
        payload = [
            {
                "build_commit": "3173a564",
                "model_filename": argv[argv.index("-m") + 1],
                "n_prompt": int(argv[argv.index("-p") + 1]),
                "n_gen": int(argv[argv.index("-n") + 1]),
                "n_threads": int(argv[argv.index("-t") + 1]),
                "n_gpu_layers": int(argv[argv.index("-ngl") + 1]),
                "avg_ns": 1_000_000,
                "avg_ts": 25.0,
            }
        ]
        return CommandResult(returncode=0, stdout=json.dumps(payload), stderr="")

    return run


def test_repository_profile_drives_full_t023_lifecycle_without_network_or_weights(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "fixture.gguf"
    artifact.write_bytes(b"synthetic-integration-fixture")
    profile = load_benchmark_profile(PROFILE_PATH)
    calls: list[tuple[str, ...]] = []
    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=2,
        timeout_seconds=30.0,
        command_runner=_deterministic_llama_bench(calls),
    )

    assert adapter.state is LifecycleState.UNINITIALIZED
    assert adapter.capabilities().supports_cpu_only is True
    assert adapter.capabilities().supports_prefix_cache is False
    assert adapter.load(_request(artifact)) is PrefixCacheState.EMPTY
    assert adapter.state is LifecycleState.READY

    prefill = adapter.prefill(4096)
    decode = adapter.decode(128)

    assert prefill.prompt_tokens == 4096
    assert prefill.cache_state_after is PrefixCacheState.EMPTY
    assert decode.generated_tokens == 128
    assert adapter.cache_state() is PrefixCacheState.EMPTY
    assert len(calls) == 2

    for command in calls:
        assert command[0] == "llama-bench"
        assert command[command.index("-m") + 1] == str(artifact)
        assert command[command.index("-t") + 1] == "2"
        assert command[command.index("-ngl") + 1] == "0"
        assert command[command.index("-r") + 1] == "1"
        assert command[-2:] == ("-o", "json")
        assert not any(token.startswith("--hf-") for token in command)
        assert not any(token.startswith("-hf") for token in command)

    assert adapter.last_observation is not None
    assert adapter.last_observation.operation == "decode"
    assert adapter.last_observation.runtime_build_commit == "3173a564"
    assert adapter.last_observation.average_tokens_per_second == 25.0

    adapter.terminate()
    assert adapter.state is LifecycleState.TERMINATED


def test_repository_profile_rejects_artifact_identity_drift_before_process_execution(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "fixture.gguf"
    artifact.write_bytes(b"synthetic-integration-fixture")
    profile = load_benchmark_profile(PROFILE_PATH)
    called = False

    def runner(_: tuple[str, ...], __: float) -> CommandResult:
        nonlocal called
        called = True
        raise AssertionError("artifact identity mismatch must fail before process execution")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    request = LoadRequest(
        artifact_id="integration-fixture-gguf",
        artifact_sha256="0" * 64,
        format_name="gguf",
        context_length=8192,
    )

    with pytest.raises(Exception) as exc_info:
        adapter.load(request)

    assert getattr(exc_info.value, "code", None) == "runtime.artifact_hash_mismatch"
    assert called is False
    assert adapter.state is LifecycleState.UNINITIALIZED
