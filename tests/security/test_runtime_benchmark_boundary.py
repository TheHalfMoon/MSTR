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
        "devices": argv[argv.index("--device") + 1],
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


@pytest.mark.parametrize(
    "network_flag",
    [
        "--model-url=https://example.invalid/model.gguf",
        "-mu=https://example.invalid/model.gguf",
        "--docker-repo=example/model:latest",
        "-dr=example/model:latest",
        "--hf-repo=owner/model",
        "--hf-file=model.gguf",
        "--hf-token=secret",
        "-hfr=owner/model",
        "-hff=model.gguf",
        "-hft=secret",
        "--rpc=127.0.0.1:50052",
        "-rpc=127.0.0.1:50052",
    ],
)
def test_profile_rejects_network_flags_with_equals_syntax(network_flag: str) -> None:
    with pytest.raises(BenchmarkCliError) as exc_info:
        BenchmarkCliProfile(
            runtime_id="unsafe",
            executable="llama-bench",
            upstream_repository="https://github.com/ggml-org/llama.cpp",
            upstream_revision="3173a56471c1753650cd806694145ffd6dcace67",
            output_args=("--device", "none", "-o", "json", network_flag),
        )

    assert exc_info.value.code == "runtime.benchmark_profile_network_flag"


@pytest.mark.parametrize(
    "output_args",
    [
        ("-o", "json"),
        ("--device", "CUDA0", "-o", "json"),
        ("--device", "none", "--device", "none", "-o", "json"),
    ],
)
def test_profile_requires_exactly_one_none_device_selector(
    output_args: tuple[str, ...],
) -> None:
    with pytest.raises(BenchmarkCliError) as exc_info:
        BenchmarkCliProfile(
            runtime_id="unsafe-device",
            executable="llama-bench",
            upstream_repository="https://github.com/ggml-org/llama.cpp",
            upstream_revision="3173a56471c1753650cd806694145ffd6dcace67",
            output_args=output_args,
        )

    assert exc_info.value.code == "runtime.benchmark_profile_cpu_device"


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


def test_runtime_device_identity_mismatch_is_rejected(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def runner(argv: tuple[str, ...], _: float) -> CommandResult:
        return CommandResult(0, json.dumps([_row(argv, devices="CUDA0")]), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.prefill(4)
    assert exc_info.value.code == "runtime.output_device_identity"


def test_artifact_mutation_after_load_fails_before_process(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)
    called = False

    def runner(_: tuple[str, ...], __: float) -> CommandResult:
        nonlocal called
        called = True
        raise AssertionError("mutated artifact must fail before runtime execution")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))
    artifact.write_bytes(b"mutated-after-load")

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.prefill(4)

    assert exc_info.value.code == "runtime.artifact_hash_changed_after_load"
    assert called is False


@pytest.mark.parametrize("nonfinite", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_benchmark_rate_fails_closed(
    tmp_path: Path,
    nonfinite: float,
) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def runner(argv: tuple[str, ...], _: float) -> CommandResult:
        return CommandResult(0, json.dumps([_row(argv, avg_ts=nonfinite)]), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=runner,
    )
    adapter.load(_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.prefill(4)
    assert exc_info.value.code == "runtime.output_nonfinite"


def test_zero_measurement_fails_closed(tmp_path: Path) -> None:
    artifact = tmp_path / "model.gguf"
    artifact.write_bytes(b"fixture")
    profile = load_benchmark_profile(PROFILE_PATH)

    def zero_time(argv: tuple[str, ...], _: float) -> CommandResult:
        return CommandResult(0, json.dumps([_row(argv, avg_ns=0)]), "")

    adapter = BenchmarkCliRuntimeAdapter(
        profile=profile,
        artifact_path=artifact,
        threads=1,
        command_runner=zero_time,
    )
    adapter.load(_request(artifact))

    with pytest.raises(BenchmarkCliError) as exc_info:
        adapter.decode(4)
    assert exc_info.value.code == "runtime.benchmark_observation_measurement"


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
