"""Unit tests for the runtime adapter protocol boundary (T023)."""

from __future__ import annotations

import pytest

from mstr_qualify.errors import QualificationError
from mstr_qualify.runtimes.base import (
    AdapterStateError,
    DecodeResult,
    DummyRuntimeAdapter,
    LifecycleState,
    LoadRequest,
    PrefillResult,
    PrefixCacheState,
    RuntimeCapabilities,
    UnsupportedOperationError,
)


def _request(**overrides: object) -> LoadRequest:
    base: dict[str, object] = {
        "artifact_id": "artifact-1",
        "artifact_sha256": "a" * 64,
        "format_name": "dummy-format",
        "context_length": 8192,
    }
    base.update(overrides)
    return LoadRequest(**base)  # type: ignore[arg-type]


class TestLifecycle:
    def test_initial_state_is_uninitialized_and_capabilities_discoverable(self) -> None:
        adapter = DummyRuntimeAdapter()
        assert adapter.state is LifecycleState.UNINITIALIZED
        caps = adapter.capabilities()
        assert caps.supports_format("dummy-format")
        assert not caps.supports_format("gguf")
        assert caps.supports_cpu_only is True

    def test_load_transitions_to_ready_with_empty_cache(self) -> None:
        adapter = DummyRuntimeAdapter()
        assert adapter.load(_request()) is PrefixCacheState.EMPTY
        assert adapter.state is LifecycleState.READY
        assert adapter.loaded_artifact_id == "artifact-1"
        assert adapter.cache_state() is PrefixCacheState.EMPTY

    def test_load_from_ready_is_rejected(self) -> None:
        adapter = DummyRuntimeAdapter()
        adapter.load(_request())
        with pytest.raises(AdapterStateError, match="UNINITIALIZED"):
            adapter.load(_request())

    def test_inference_requires_ready_state(self) -> None:
        adapter = DummyRuntimeAdapter()
        with pytest.raises(AdapterStateError, match="READY"):
            adapter.prefill(4)
        with pytest.raises(AdapterStateError, match="READY"):
            adapter.decode(4)
        with pytest.raises(AdapterStateError, match="READY"):
            adapter.cache_state()

    def test_terminate_is_clean_and_terminal(self) -> None:
        adapter = DummyRuntimeAdapter()
        adapter.load(_request())
        adapter.terminate()
        assert adapter.state is LifecycleState.TERMINATED
        assert adapter.loaded_artifact_id is None
        with pytest.raises(AdapterStateError, match="already terminated"):
            adapter.terminate()


class TestCapabilityGates:
    def test_unsupported_format_fails_closed_before_any_state_change(self) -> None:
        adapter = DummyRuntimeAdapter(supported_formats=("dummy-format",))
        with pytest.raises(UnsupportedOperationError, match="format"):
            adapter.load(_request(format_name="gguf"))
        assert adapter.state is LifecycleState.UNINITIALIZED

    def test_context_above_maximum_is_rejected_explicitly(self) -> None:
        adapter = DummyRuntimeAdapter(max_context_length=8192)
        with pytest.raises(UnsupportedOperationError, match="context"):
            adapter.load(_request(context_length=16384))
        assert adapter.state is LifecycleState.UNINITIALIZED


class TestDeterminism:
    def test_identical_sequences_produce_identical_structured_results(self) -> None:
        results = []
        for _ in range(2):
            adapter = DummyRuntimeAdapter()
            adapter.load(_request())
            prefill = adapter.prefill(11)
            decode = adapter.decode(5)
            results.append(
                (
                    prefill,
                    decode,
                    adapter.cache_state(),
                )
            )
        expected = (
            PrefillResult(prompt_tokens=11, cache_state_after=PrefixCacheState.POPULATED),
            DecodeResult(generated_tokens=5),
            PrefixCacheState.POPULATED,
        )
        assert results[0] == results[1] == (expected[0], expected[1], expected[2])

    def test_decode_budget_must_be_positive(self) -> None:
        adapter = DummyRuntimeAdapter()
        adapter.load(_request())
        with pytest.raises(AdapterStateError, match="max_new_tokens"):
            adapter.decode(0)


class TestRequestValidation:
    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("artifact_id", " padded"),
            ("artifact_id", ""),
            ("format_name", " "),
            ("context_length", 0),
        ],
    )
    def test_invalid_request_fields_fail_closed(self, field: str, value: object) -> None:
        kwargs: dict[str, object] = {field: value}
        request_data = {
            "artifact_id": "artifact-1",
            "artifact_sha256": "a" * 64,
            "format_name": "dummy-format",
            "context_length": 8192,
        }
        request_data.update(kwargs)
        with pytest.raises(QualificationError):
            LoadRequest(**request_data)  # type: ignore[arg-type]


class TestCapabilitiesValidation:
    def test_duplicate_formats_rejected(self) -> None:
        with pytest.raises(AdapterStateError, match="duplicates"):
            RuntimeCapabilities(
                supported_formats=("gguf", "gguf"),
                max_context_length=None,
                supports_cpu_only=None,
                supports_prefix_cache=None,
            )

    def test_invalid_max_context_rejected(self) -> None:
        with pytest.raises(AdapterStateError, match="max_context_length"):
            RuntimeCapabilities(
                supported_formats=("gguf",),
                max_context_length=0,
                supports_cpu_only=None,
                supports_prefix_cache=None,
            )
