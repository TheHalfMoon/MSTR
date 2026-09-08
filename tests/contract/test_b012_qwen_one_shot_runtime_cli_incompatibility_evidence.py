from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
INCIDENT = (
    ROOT
    / "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-one-shot-runtime-cli-incompatibility-run-34288154926.json"
)
CHECKPOINT_DIR = ROOT / "artifacts/results/equivalent/B012/checkpoints/34288154926"
FAILURE = (
    CHECKPOINT_DIR / "B012-qwen3.5-0.8b-control-raw-code-recovery-case-failure.json"
)
STATE = CHECKPOINT_DIR / "B012-qwen3.5-0.8b-control-raw-code-recovery-case-state.json"
CP1 = (
    CHECKPOINT_DIR
    / "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-01-init.json"
)
CP2 = (
    CHECKPOINT_DIR
    / "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-02-source.json"
)
CP3 = (
    CHECKPOINT_DIR
    / "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-03-quantize.json"
)
RAW_HELPER = ROOT / "colab/mstr_b012_raw_code.py"
TOOLCHAIN_LOCK = ROOT / "artifacts/manifests/B012-executor-toolchain-lock.json"
RAW_MANIFEST = ROOT / "benchmarks/manifests/B012-raw-code-proxy.json"


def _read(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_one_shot_cli_incompatibility_is_canonical_and_fail_closed() -> None:
    binding = _read(BINDING)
    incident = _read(INCIDENT)
    failure = _read(FAILURE)
    state = _read(STATE)

    assert _sha256(INCIDENT) == (
        "20e30ef5382189dc22407df0caaab171668c91863cdf972a66bfd90e4615f03d"
    )
    assert binding["status"] == "BLOCKED_PENDING_QWEN_RAW_CODE_RUNTIME_CONTRACT_REPAIR"
    bound = binding["qwen_raw_code_one_shot_runtime_cli_incompatibility"]
    assert isinstance(bound, dict)
    assert bound["run_id"] == 34288154926
    assert bound["run_attempt"] == 1
    assert bound["job_id"] == 102268410928
    assert bound["failure_evidence_sha256"] == _sha256(INCIDENT)
    assert bound["runtime_contract_repair_required"] is True
    assert bound["runtime_migration_requires_equivalence_review"] is True
    assert bound["same_topology_redispatch_authorized"] is False
    assert bound["retry_authority_created"] is False
    assert bound["external_dispatch_authority_created"] is False
    assert bound["cross_run_resume_authority_created"] is False

    assert incident["failure_classification"] == (
        "B012_EXECUTOR_RUNTIME_CLI_INCOMPATIBILITY_RAW_CODE_UNEXECUTED"
    )
    root_cause = incident["root_cause"]
    assert isinstance(root_cause, dict)
    assert root_cause["runtime_commit"] == (
        "3173a56471c1753650cd806694145ffd6dcace67"
    )
    assert root_cause["runtime_binary"] == "llama-cli"
    assert root_cause["parser_example"] == "LLAMA_EXAMPLE_CLI"
    assert root_cause["rejected_argument"] == "--no-conversation"
    assert root_cause["argument_scope"] == "LLAMA_EXAMPLE_COMPLETION_ONLY"
    assert root_cause["runner_shutdown_observed"] is False
    assert root_cause["timeout_observed"] is False

    execution = incident["execution"]
    assert isinstance(execution, dict)
    assert execution["durable_raw_code_cases"] == []
    assert execution["raw_code_result"] == "NONE_DURABLY_PROVEN"
    assert execution["model_quality_verdict"] == "NONE"
    assert execution["candidate_admission_decision"] == "NONE"
    assert execution["candidate_execution_completion"] == "NOT_PROVEN"
    assert execution["cleanup"] == "PROVEN_WORKFLOW_SUCCESS"

    canonical_effect = incident["canonical_effect"]
    assert isinstance(canonical_effect, dict)
    assert canonical_effect["b012_state"] == "PENDING"
    assert canonical_effect["b013_opening_authorized"] is False

    assert failure["completed_raw_code_cases"] == []
    assert failure["model_quality_verdict"] == "NONE"
    assert failure["candidate_admission_decision"] == "NONE"
    assert "error: invalid argument: --no-conversation" in str(failure["error"])
    assert state["completed_stages"] == ["init", "source", "quantize"]
    assert state["raw_code_case_results"] == {}
    assert not (
        CHECKPOINT_DIR
        / "B012-qwen3.5-0.8b-control-raw-code-recovery-checkpoint-04a-raw-code-python-clamp.json"
    ).exists()


def test_one_shot_cli_incident_preserves_exact_durable_sources() -> None:
    assert _sha256(FAILURE) == (
        "b0aff98dabafd1335b27a771cd74e4cffa9364da3a7d22154db618a7173743ef"
    )
    assert _sha256(STATE) == (
        "4c5c6521180b17949d77bdedf2d18c04dfb7f3345dde40db14527ff3b407e3b8"
    )
    assert _sha256(CP1) == (
        "fb6b5165037691699a36ed53a5d239d500a2818ed230f06932743bfc6072f14f"
    )
    assert _sha256(CP2) == (
        "d95e154bb519cd89359483f49566ad7bcda05127991bd8b1116d8a250e7e5b58"
    )
    assert _sha256(CP3) == (
        "0f09abec985a3bb26987f529d86a9d9b1ed6dd2859250700520a81be733322e7"
    )

    cp2 = _read(CP2)
    cp3 = _read(CP3)
    cp2_payload = cp2["checkpoint_payload"]
    cp3_payload = cp3["checkpoint_payload"]
    assert isinstance(cp2_payload, dict)
    assert isinstance(cp3_payload, dict)
    assert cp2_payload["verified_file_count"] == 9
    assert cp2_payload["verified_download_bytes"] == 1769897109
    assert cp3_payload["q4_k_m_sha256"] == (
        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
    )
    assert cp3_payload["q4_k_m_size_bytes"] == 541903296


def test_failed_executor_is_preserved_until_separate_runtime_contract_repair() -> None:
    helper = RAW_HELPER.read_text(encoding="utf-8")
    assert helper.count('"--no-conversation"') == 1

    lock = _read(TOOLCHAIN_LOCK)
    llama_cpp = lock["llama_cpp"]
    assert isinstance(llama_cpp, dict)
    assert llama_cpp["runtime_commit"] == "3173a56471c1753650cd806694145ffd6dcace67"

    raw = _read(RAW_MANIFEST)
    assert raw["execution"] == {
        "runtime": "llama.cpp-llama-cli-cpu",
        "context_tokens": 2048,
        "generated_tokens": 96,
        "threads": 2,
        "gpu_layers": 0,
        "temperature": 0.0,
        "seed": 42,
        "network_model_calls": 0,
    }
