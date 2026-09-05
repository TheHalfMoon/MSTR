from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / (
    "artifacts/authorities/T031_FOUNDER_AUTHORITY_FOR_LOCAL_MEASUREMENT_REGENERATION.json"
)
ENVELOPE = ROOT / "artifacts/manifests/T031-local-measurement-execution-envelope.json"
LOCK = ROOT / "artifacts/manifests/T031-executor-toolchain-lock.json"
BINDING = ROOT / "artifacts/manifests/T031-executor-toolchain-binding.json"
HELPER = ROOT / "colab/mstr_executor_toolchain.py"
GOVERNANCE = ROOT / "colab/mstr_t031_governance.py"
SOURCE = ROOT / "colab/mstr_t031_source.py"
ARTIFACTS = ROOT / "colab/mstr_t031_artifacts.py"
MEASURE = ROOT / "colab/mstr_t031_measure.py"
EXECUTOR = ROOT / "colab/mstr_t031_execute.py"
WORKFLOW = ROOT / ".github/workflows/t031-measure.yml"

CANDIDATES = [
    "granite-4.1-3b",
    "ministral-3-3b",
    "qwen2.5-coder-1.5b",
    "qwen3-4b",
    "qwen3.5-2b",
    "qwen3.5-4b",
    "smollm3-3b",
    "yi-coder-1.5b",
]


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_binding_is_exactly_bound_to_canonical_t031_authority() -> None:
    authority = _read_json(AUTHORITY)
    envelope = _read_json(ENVELOPE)
    binding = _read_json(BINDING)

    assert authority["status"] == "AUTHORIZED_CANONICAL"
    assert binding["status"] == "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"
    assert binding["authority_sha256"] == _sha256(AUTHORITY)
    assert binding["envelope_sha256"] == _sha256(ENVELOPE)
    assert binding["candidate_ids"] == CANDIDATES
    assert envelope["candidate_ids"] == CANDIDATES
    assert binding["contexts"] == [4096, 8192, 16384]

    scope = authority["scope"]
    assert isinstance(scope, dict)
    bounded = scope["bounded_execution_envelope"]
    assert isinstance(bounded, dict)
    assert bounded["dispatch_state"] == "BLOCKED_PENDING_CANONICAL_EXECUTOR_TOOLCHAIN_BINDING"
    assert bounded["sha256"] == binding["envelope_sha256"]


def test_binding_hashes_every_execution_component() -> None:
    binding = _read_json(BINDING)
    expected = {
        LOCK: binding["toolchain_lock_sha256"],
        HELPER: binding["toolchain_helper_sha256"],
        GOVERNANCE: binding["governance_script_sha256"],
        SOURCE: binding["source_script_sha256"],
        ARTIFACTS: binding["artifact_script_sha256"],
        MEASURE: binding["measurement_script_sha256"],
        EXECUTOR: binding["executor_script_sha256"],
        WORKFLOW: binding["workflow_sha256"],
    }
    for path, digest in expected.items():
        assert isinstance(digest, str)
        assert _sha256(path) == digest


def test_toolchain_and_measurement_surface_are_frozen() -> None:
    lock = _read_json(LOCK)
    binding = _read_json(BINDING)
    llama_cpp = lock["llama_cpp"]
    task = lock["task_binding"]
    runner = lock["runner"]
    python_toolchain = lock["python_toolchain"]
    assert isinstance(llama_cpp, dict)
    assert isinstance(task, dict)
    assert isinstance(runner, dict)
    assert isinstance(python_toolchain, dict)

    assert llama_cpp["conversion_quantization_commit"] == (
        "fc35562ba46fbbf8e30cac85edbb39642c37d248"
    )
    assert llama_cpp["runtime_commit"] == "3173a56471c1753650cd806694145ffd6dcace67"
    assert task["candidate_ids"] == CANDIDATES
    assert task["contexts"] == [4096, 8192, 16384]
    assert task["warmups_excluded"] == 2
    assert task["measured_repetitions"] == 10
    assert task["threads"] == 2
    assert task["decode_tokens"] == 128
    assert task["decode_semantics"] == ("T030_ISOLATED_DECODE_COMPANION_NOT_POST_PREFILL_KV_CACHE")
    assert set(task["prohibited_authority_transfer"]) == {
        "B012",
        "T032",
        "T033",
        "T034",
        "TRAINING",
    }
    assert runner["runs_on"] == "ubuntu-24.04"
    assert runner["python_version"] == "3.11.9"
    assert set(python_toolchain["hosts"]) == {
        "files.pythonhosted.org",
        "download.pytorch.org",
        "download-r2.pytorch.org",
    }

    protocol = binding["measurement_protocol"]
    assert isinstance(protocol, dict)
    assert protocol["primary_measurement_arm"] == "Q4_K_M"
    assert protocol["q4_k_s_scope"] == "IDENTITY_REGENERATION_ONLY"
    assert protocol["hosted_lane_claim"] == (
        "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM"
    )
    assert "ESTIMATED" in str(protocol["load_behavior_semantics"])


def test_execution_boundary_does_not_transfer_later_authority() -> None:
    authority = _read_json(AUTHORITY)
    binding = _read_json(BINDING)
    scope = authority["scope"]
    boundary = binding["execution_boundary"]
    assert isinstance(scope, dict)
    assert isinstance(boundary, dict)

    for key in (
        "b010_b012_candidates",
        "t032_execution",
        "t033_execution",
        "t034_admission_decision",
        "training",
        "weight_changing_training",
    ):
        assert scope[key] is False
    assert boundary["authority_transfer"] is False
    assert boundary["b012_execution"] is False
    assert boundary["t032_execution"] is False
    assert boundary["t033_execution"] is False
    assert boundary["t034_admission_decision"] is False
    assert boundary["training"] is False
    assert boundary["paid_cost_usd"] == 0.0
    assert boundary["git_model_binaries"] == 0
    assert boundary["founder_machine_model_binaries"] == 0
    assert boundary["durable_outputs"] == ["JSON", "JSONL"]


def test_workflow_dispatch_is_canonical_and_branch_creation_only() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = _read_json(BINDING)

    assert "workflow_dispatch:" in workflow
    assert '"execute/t031-*"' in workflow
    assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in workflow
    assert '[[ "$created" == "True" && "$deleted" != "True" ]]' in workflow
    assert 'candidate="${GITHUB_REF_NAME#execute/t031-}"' in workflow
    assert "ref: main" in workflow
    assert "persist-credentials: false" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "group: t031-governed-model-execution" in workflow
    assert "cancel-in-progress: false" in workflow
    for candidate in CANDIDATES:
        assert candidate in workflow

    dispatch = binding["dispatch_boundary"]
    assert isinstance(dispatch, dict)
    assert dispatch["canonicalization_required"] is True
    assert dispatch["connector_dispatch_event"] == "BRANCH_CREATION_ONLY"
    assert dispatch["checkout_ref"] == "main"
    assert dispatch["max_parallel_candidates"] == 1
    assert dispatch["max_job_minutes"] == 120


def test_executor_contains_fail_closed_network_and_runtime_boundaries() -> None:
    helper = HELPER.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")
    measure = MEASURE.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")

    assert 'frozenset({"huggingface.co", "us.aws.cdn.hf.co"})' in source
    assert 'any(part in {"", ".", ".."} for part in path.parts)' in source
    assert 'or "\\\\" in filename' in source
    assert '"-ngl",\n        "0"' in measure
    assert '"--device",\n        "none"' in measure
    assert "require_file_sha256(q4_k_m, q4_k_m_sha)" in executor
    assert "T030_ISOLATED_DECODE_COMPANION_NOT_POST_PREFILL_KV_CACHE" in executor
    assert "AUTHORIZED_EPHEMERAL_REFERENCE_NOT_U1_8GB_HARDWARE_CLAIM" in executor
    assert "estimated_load_and_process_startup_seconds" in measure
    assert "unquote(Path(urlparse(url).path).name)" in helper
    assert 'blocked_prefixes = ("LLAMA_ARG_", "HF_", "HUGGINGFACE_", "CUDA_", "NVIDIA_")' in helper
