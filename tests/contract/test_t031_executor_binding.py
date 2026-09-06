from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY = ROOT / (
    "artifacts/authorities/T031_FOUNDER_AUTHORITY_FOR_LOCAL_MEASUREMENT_REGENERATION.json"
)
ENVELOPE = ROOT / "artifacts/manifests/T031-local-measurement-execution-envelope.json"
LOCK = ROOT / "artifacts/manifests/T031-executor-toolchain-lock.json"
REPLAY_OVERLAY = ROOT / "artifacts/manifests/T031-t029-producer-replay-overlay.json"
BINDING = ROOT / "artifacts/manifests/T031-executor-toolchain-binding.json"
HELPER = ROOT / "colab/mstr_executor_toolchain.py"
REPLAY_HELPER = ROOT / "colab/mstr_t031_replay.py"
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
DIRECT_REPLAY_PACKAGES = {
    "gguf": "0.19.0",
    "numpy": "2.4.6",
    "protobuf": "7.36.0",
    "safetensors": "0.8.0",
    "sentencepiece": "0.2.2",
    "torch": "2.13.0+cpu",
    "transformers": "5.15.1",
}


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
        REPLAY_OVERLAY: binding["producer_replay_overlay_sha256"],
        HELPER: binding["toolchain_helper_sha256"],
        REPLAY_HELPER: binding["producer_replay_helper_sha256"],
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


def test_toolchain_measurement_and_replay_surface_are_frozen() -> None:
    lock = _read_json(LOCK)
    overlay = _read_json(REPLAY_OVERLAY)
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

    assert overlay["schema_version"] == "mstr.t031-t029-producer-replay-overlay.v2"
    assert overlay["status"] == "EVIDENCE_BOUNDED_REPLAY"
    assert overlay["python_version"] == "3.11.16"
    assert overlay["package_count"] == 40
    assert set(overlay["direct_package_names"]) == set(DIRECT_REPLAY_PACKAGES)
    assert set(overlay["hosts"]) == {
        "files.pythonhosted.org",
        "download.pytorch.org",
        "download-r2.pytorch.org",
    }
    packages = overlay["packages"]
    assert isinstance(packages, list)
    assert len(packages) == 40
    versions = {item["name"]: item["version"] for item in packages if isinstance(item, dict)}
    for name, version in DIRECT_REPLAY_PACKAGES.items():
        assert versions[name] == version
    assert versions["huggingface-hub"] == "1.30.0"
    assert versions["typer"] == "0.27.2"
    assert versions["tokenizers"] == "0.22.2"
    assert versions["requests"] == "2.34.2"
    assert versions["jinja2"] == "3.1.6"
    resolution = overlay["resolution_evidence"]
    assert isinstance(resolution, dict)
    assert resolution["run_id"] == 34031883766
    assert resolution["artifact_id"] == 9988881418
    assert resolution["model_access"] == "NONE"
    assert resolution["training"] is False
    assert resolution["paid_cost_usd"] == 0.0
    reconstruction = overlay["reconstruction_basis"]
    assert isinstance(reconstruction, dict)
    assert reconstruction["historical_transitive_identity_claim"] is False
    assert reconstruction["equivalence_gate"] == "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH"
    for item in packages:
        assert isinstance(item, dict)
        assert isinstance(item["url"], str) and item["url"].startswith("https://")
        assert isinstance(item["sha256"], str) and len(item["sha256"]) == 64

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
    overlay = _read_json(REPLAY_OVERLAY)
    scope = authority["scope"]
    boundary = binding["execution_boundary"]
    replay_boundary = overlay["execution_boundary"]
    assert isinstance(scope, dict)
    assert isinstance(boundary, dict)
    assert isinstance(replay_boundary, dict)

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

    for key in (
        "model_access_authority_expansion",
        "candidate_revision_or_file_expansion",
        "b012_execution",
        "t032_execution",
        "t033_execution",
        "t034_admission_decision",
        "training",
    ):
        assert replay_boundary[key] is False
    assert replay_boundary["paid_cost_usd"] == 0.0
    assert replay_boundary["git_model_binaries"] == 0
    assert replay_boundary["founder_machine_model_binaries"] == 0


def test_issue_comment_dispatch_is_canonical_owner_scoped_and_branch_trigger_free() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    binding = _read_json(BINDING)

    assert "issue_comment:" in workflow
    assert "workflow_dispatch:" not in workflow
    assert "\n  push:" not in workflow
    assert "execute/t031-" not in workflow
    assert "github.event.issue.number == 167" in workflow
    assert "github.actor == 'TheHalfMoon'" in workflow
    assert "github.event.comment.user.login == 'TheHalfMoon'" in workflow
    assert "github.event.comment.author_association == 'OWNER'" in workflow
    assert '[[ "$GITHUB_EVENT_NAME" == "issue_comment" ]]' in workflow
    assert '[[ "$GITHUB_REF" == "refs/heads/main" ]]' in workflow
    assert '[[ "$ISSUE_NUMBER" == "167" ]]' in workflow
    assert "ref: main" in workflow
    assert "persist-credentials: false" in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "group: t031-governed-model-execution" in workflow
    assert "cancel-in-progress: false" in workflow
    assert 'python-version: "3.11.16"' in workflow
    for candidate in CANDIDATES:
        assert f"T031_RUN {candidate}" in workflow

    dispatch = binding["dispatch_boundary"]
    assert isinstance(dispatch, dict)
    assert dispatch["canonicalization_required"] is True
    assert dispatch["connector_dispatch_surface"] == "ISSUE_COMMENT_CANONICAL_MAIN"
    assert dispatch["connector_dispatch_issue"] == 167
    assert dispatch["connector_dispatch_author"] == "TheHalfMoon"
    assert dispatch["connector_dispatch_author_association"] == "OWNER"
    assert dispatch["connector_dispatch_command"] == "T031_RUN <authorized-candidate>"
    assert dispatch["checkout_ref"] == "main"
    assert dispatch["max_parallel_candidates"] == 1
    assert dispatch["max_job_minutes"] == 120


def test_executor_contains_fail_closed_network_runtime_and_replay_boundaries() -> None:
    helper = HELPER.read_text(encoding="utf-8")
    replay = REPLAY_HELPER.read_text(encoding="utf-8")
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
    assert "install_replay_toolchain(" in executor
    assert '"--no-index"' in replay
    assert '"--no-deps"' in replay
    assert '"pip", "check"' in replay
    assert "producer replay direct package set drift detected" in replay
    assert "producer replay package-count binding drift detected" in replay
    assert "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH" in replay


def test_toolchain_subprocesses_are_bounded_and_workdir_setup_fails_closed() -> None:
    helper = HELPER.read_text(encoding="utf-8")
    replay = REPLAY_HELPER.read_text(encoding="utf-8")
    executor = EXECUTOR.read_text(encoding="utf-8")
    for source in (helper, replay):
        tree = ast.parse(source)
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_run_checked"
        ]
        assert calls
        for call in calls:
            assert any(keyword.arg == "timeout" for keyword in call.keywords)
    assert "timeout=timeout" in helper
    assert "except subprocess.TimeoutExpired as exc:" in helper
    assert executor.index("    try:\n") < executor.index("        if workdir.exists():")
    assert executor.index("    try:\n") < executor.index("        workdir.mkdir(parents=True)")
