from __future__ import annotations

import json
from pathlib import Path

import pytest

from mstr_qualify.ids import sha256_file
from mstr_qualify.runtimes.base import LoadRequest, PrefixCacheState, UnsupportedOperationError
from mstr_qualify.runtimes.benchmark_cli import (
    BenchmarkCliError,
    BenchmarkCliRuntimeAdapter,
    CommandResult,
    load_benchmark_profile,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = REPOSITORY_ROOT / "configs" / "runtimes" / "llama-cpp-cpu.json"


def _load_request(artifact: Path, *, context_length: int = 128) -> LoadRequest:
    return LoadRequest(
        artifact_id="fixture-gguf",
        artifact_sha256=sha256_file(artifact),
        format_name="gguf",
        context_length=context_length,
    )


def _successful_runner(calls: list[tuple[str, ...]]):
    def run(argv: tuple[str, ...], timeout_seconds: float) -> CommandResult:
        assert timeout_seconds == 12.0
        calls.append(argv)
        prompt = int(argv[argv.index("-p") + 1])
        generation = int(argv[argv.index("-n") + 1])
        threads = int(argv[argv.index("-t") + 1])
        gpu_layers = int(argv[argv.index("-ngl") + 1])
        payload = [
            {
                "build_commit": "3173a564",
                "model_filename": argv[argv.index("-m") + 1],
                "n_prompt": prompt,
                "n_gen": generation,
                "n_threads": threads,
                "n_gpu_layers": gpu_layers,
                "avg_ns": 1000,
                "avg_ts": 42.5,
            }
        ]
        return CommandResult(0, json.dumps(payload), "")

    return run


def test_llama_cpp_profile_is_pinned_and_cpu_only_command_is_deterministic(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture-q4-bytes")
    profile = load_benchmark_profile(PROFILE_PATH)
    calls: list[tuple[str, ...]] = []
    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=4,
        timeout_seconds=12.0,
        command_runner=_successful_runner(calls),
    )

    assert profile.upstream_revision == "3173a56471c1753650cd806694145ffd6dcace67"
    assert adapter.platform_family() == "llama.cpp-llama-bench-cpu"
    assert adapter.capabilities().supports_cpu_only is True
    assert adapter.capabilities().supports_prefix_cache is False
    assert adapter.load(_load_request(artifact)) is PrefixCacheState.EMPTY

    prefill = adapter.prefill(32)
    assert prefill.prompt_tokens == 32
    assert prefill.cache_state_after is PrefixCacheState.EMPTY
    assert adapter.cache_state() is PrefixCacheState.EMPTY
    assert adapter.last_observation is not None
    assert adapter.last_observation.operation == "prefill"
    assert adapter.last_observation.average_tokens_per_second == 42.5

    decode = adapter.decode(8)
    assert decode.generated_tokens == 8
    assert adapter.last_observation is not None
    assert adapter.last_observation.operation == "decode"

    assert len(calls) == 2
    for command in calls:
        assert command[0] == "llama-bench"
        assert command[command.index("-m") + 1] == str(artifact)
        assert command[command.index("-t") + 1] == "4"
        assert command[command.index("-ngl") + 1] == "0"
        assert command[command.index("-r") + 1] == "1"
        assert command[-2:] == ("-o", "json")
        assert "-hf" not in command
        assert "--hf-repo" not in command
        assert "--hf-token" not in command

    adapter.terminate()


def test_artifact_identity_must_match_before_ready(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"actual")
    profile = load_benchmark_profile(PROFILE_PATH)
    adapter = BenchmarkCliRuntimeAdapter(profile=profile, artifact_path=artifact, threads=1)
    request = LoadRequest(
        artifact_id="fixture-gguf",
        artifact_sha256="0" * 64,
        format_name="gguf",
        context_length=64,
    )

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.load(request)

    assert exc_info.value.code == "runtime.artifact_hash_mismatch"


def test_context_limits_fail_closed_without_running_process(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)
    calls: list[tuple[str, ...]] = []
    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=2,
        command_runner=_successful_runner(calls),
    )
    adapter.load(_load_request(artifact, context_length=16))

    with pytest.raises(UnsupportedOperationError) as prefill_error:
        adapter.prefill(17)
    assert prefill_error.value.code == "runtime.context_unsupported"

    with pytest.raises(UnsupportedOperationError) as decode_error:
        adapter.decode(17)
    assert decode_error.value.code == "runtime.context_unsupported"
    assert calls == []


def test_nonzero_process_and_malformed_output_have_stable_errors(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def failed(_: tuple[str, ...], __: float) -> CommandResult:
        return CommandResult(7, "", "runtime failed")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=failed,
    )
    adapter.load(_load_request(artifact))
    with pytest.raises(BenchmarkCliError) as process_error:
        adapter.prefill(4)
    assert process_error.value.code == "runtime.process_failure"

    def malformed(_: tuple[str, ...], __: float) -> CommandResult:
        return CommandResult(0, "not-json", "")

    adapter2 = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=malformed,
    )
    adapter2.load(_load_request(artifact))
    with pytest.raises(BenchmarkCliError) as output_error:
        adapter2.decode(4)
    assert output_error.value.code == "runtime.output_json"


def test_reported_gpu_or_build_identity_mismatch_fails_closed(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def mismatch(argv: tuple[str, ...], _: float) -> CommandResult:
        payload = [
            {
                "build_commit": "deadbeef",
                "model_filename": argv[argv.index("-m") + 1],
                "n_prompt": int(argv[argv.index("-p") + 1]),
                "n_gen": int(argv[argv.index("-n") + 1]),
                "n_threads": int(argv[argv.index("-t") + 1]),
                "n_gpu_layers": 1,
                "avg_ns": 1000,
                "avg_ts": 1.0,
            }
        ]
        return CommandResult(0, json.dumps(payload), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=mismatch,
    )
    adapter.load(_load_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.prefill(4)
    assert exc_info.value.code in {"runtime.output_identity", "runtime.build_identity"}
