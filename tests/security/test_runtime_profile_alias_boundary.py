from __future__ import annotations

import pytest

from mstr_qualify.runtimes.benchmark_cli import BenchmarkCliError, BenchmarkCliProfile


@pytest.mark.parametrize(
    "field",
    [
        "model_arg",
        "prompt_arg",
        "generation_arg",
        "threads_arg",
        "gpu_layers_arg",
        "repetitions_arg",
    ],
)
@pytest.mark.parametrize("device_flag", ["-dev", "--device"])
def test_profile_rejects_device_selector_in_non_output_argument_field(
    field: str,
    device_flag: str,
) -> None:
    kwargs = {field: device_flag}

    with pytest.raises(BenchmarkCliError) as exc_info:
        BenchmarkCliProfile(
            runtime_id="unsafe-device-alias",
            executable="llama-bench",
            upstream_repository="https://github.com/ggml-org/llama.cpp",
            upstream_revision="3173a56471c1753650cd806694145ffd6dcace67",
            **kwargs,
        )

    assert exc_info.value.code == "runtime.benchmark_profile_cpu_device"
