from __future__ import annotations

import subprocess

from mstr_qualify.runtimes import benchmark_cli

_BLOCKED_ENV = {
    "LLAMA_ARG_MODEL_URL": "https://example.invalid/model.gguf",
    "LLAMA_ARG_DOCKER_REPO": "example/model:latest",
    "LLAMA_ARG_HF_REPO": "owner/model",
    "LLAMA_ARG_HF_FILE": "model.gguf",
    "LLAMA_ARG_RPC": "127.0.0.1:50052",
    "LLAMA_ARG_DEVICE": "CUDA0",
    "LLAMA_ARG_N_GPU_LAYERS": "99",
    "LLAMA_ARG_UNEXPECTED_FUTURE_OPTION": "unsafe",
    "HF_TOKEN": "secret",
    "HF_ENDPOINT": "https://example.invalid",
}


def test_subprocess_runner_sanitizes_upstream_option_environment(monkeypatch) -> None:
    for key, value in _BLOCKED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("MSTR_SAFE_SENTINEL", "preserved")

    captured_env: dict[str, str] | None = None

    def fake_run(argv, **kwargs):
        nonlocal captured_env
        captured_env = kwargs["env"]
        return subprocess.CompletedProcess(argv, 0, "[]", "")

    monkeypatch.setattr(benchmark_cli.subprocess, "run", fake_run)

    result = benchmark_cli._subprocess_runner(("llama-bench", "--version"), 1.0)

    assert result.returncode == 0
    assert captured_env is not None
    assert captured_env["MSTR_SAFE_SENTINEL"] == "preserved"
    assert not any(key.startswith("LLAMA_ARG_") for key in captured_env)
    assert not any(key.startswith("HF_") for key in captured_env)
    for key in _BLOCKED_ENV:
        assert key not in captured_env
