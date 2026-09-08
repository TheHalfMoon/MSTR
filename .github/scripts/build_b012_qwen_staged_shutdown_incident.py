#!/usr/bin/env python3
"""Build the repository-only B012 staged Qwen shutdown incident subject."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BASE_MAIN = "98feee7765cbf64428f149f885519cef76800caf"
RUN_ID = 34231845282
JOB_ID = 102079676195
BLOCKED_STATUS = "BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR"
FAILURE_CLASS = "B012_INFRASTRUCTURE_RUNNER_SHUTDOWN_PARTIAL_DURABLE_RECOVERY"
FAILURE_REL = Path(
    "artifacts/results/equivalent/B012/failures/"
    "B012-qwen3.5-0.8b-control-raw-code-staged-recovery-run-34231845282.json"
)
EVIDENCE_REL = Path(
    "evidence/mstr-000b/B012-qwen-staged-recovery-runner-shutdown-34231845282.md"
)
BINDING_REL = Path("artifacts/manifests/B012-executor-toolchain-binding.json")
TEST_FILES = (
    Path("tests/contract/test_b012_executor_binding.py"),
    Path("tests/contract/test_b012_qwen_raw_code_recovery.py"),
    Path("tests/contract/test_b012_runner_shutdown_evidence.py"),
    Path("tests/contract/test_b012_stage_checkpoint_topology.py"),
    Path("tests/contract/test_b012_qwen_staged_recovery_topology.py"),
)
ACTIVE_STATUS = "SATISFIES_DISPATCH_PRECONDITION_WHEN_CANONICAL"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_incident() -> dict[str, object]:
    return {
        "schema_version": "mstr.b012-infrastructure-cancellation.v1",
        "task_id": "B012",
        "candidate_id": "qwen3.5-0.8b-control",
        "run_id": RUN_ID,
        "job_id": JOB_ID,
        "workflow_name": "B012 Qwen raw-code staged recovery",
        "workflow_event": "issue_comment",
        "workflow_conclusion": "failure",
        "workflow_head_sha": BASE_MAIN,
        "canonical_main_at_start": BASE_MAIN,
        "run_created_utc": "2026-09-08T13:25:14Z",
        "run_updated_utc": "2026-09-08T13:44:57Z",
        "raw_code_stage_started_utc": "2026-09-08T13:35:05Z",
        "runner_shutdown_utc": "2026-09-08T13:44:52.5488705Z",
        "runner_diagnostic": (
            "The runner has received a shutdown signal. This can happen when the runner "
            "service is stopped, or a manually started runner is canceled. The operation was "
            "canceled."
        ),
        "infrastructure_root_cause": "UNKNOWN_BEYOND_RUNNER_SHUTDOWN_SIGNAL",
        "workflow_timeout_minutes": 45,
        "shutdown_occurred_before_workflow_timeout_budget": True,
        "failure_classification": FAILURE_CLASS,
        "executor_authored_failure_json": False,
        "durable_stage_count": 3,
        "durable_stages": ["init", "source", "quantize"],
        "durable_artifact_count": 3,
        "durable_artifacts": [
            {
                "stage": "init",
                "artifact_id": 10058420119,
                "digest": "sha256:fe42fd594f5a5501f25ce2fe2f9449031e1760eec90d71bf2983f6965aa297fc",
            },
            {
                "stage": "source",
                "artifact_id": 10058479985,
                "digest": "sha256:1884986d415cacfc7d51b072dd87124cd6c0577e33585a3ec199019883f4e71b",
            },
            {
                "stage": "quantize",
                "artifact_id": 10058522893,
                "digest": "sha256:ff094686270f646371a9b218ce0fbc8378d5b2b0cbc4d9f8794b5bfcb6c86f68",
            },
        ],
        "source_verification": {
            "status": "EXACT_B010_QWEN_FILES_REACQUIRED_AND_VERIFIED",
            "file_count": 9,
            "total_download_bytes": 1769897109,
            "weight_sha256": "c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c",
            "weight_size_bytes": 1746942600,
            "tokenizer_sha256": "fe000e3ed39ed12b8d2481d527d44f93c65d37e87645d2dcc80d1bf9d50d2927",
            "tokenizer_size_bytes": 12807196,
        },
        "regenerated_q4": {
            "status": "EXACT_PRIOR_Q4_IDENTITY_REPRODUCED",
            "matches_prior_stage03": True,
            "f16_sha256": "60e1e6f04a2a0053fedc184407deaad3d51f4f8cc7b0e54f85a67451b706bc27",
            "f16_size_bytes": 1744371200,
            "q4_k_m_sha256": "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa",
            "q4_k_m_size_bytes": 541903296,
        },
        "raw_code_stage_conclusion": "cancelled",
        "raw_code_result": "NONE_DURABLY_PROVEN",
        "raw_code_checkpoint_artifact": "NONE",
        "finalize_stage_conclusion": "skipped",
        "final_evidence_artifact": "NONE",
        "explicit_cleanup_step_conclusion": "skipped",
        "ephemeral_cleanup_completion": "NOT_PROVEN",
        "candidate_execution_completion": "NOT_PROVEN",
        "candidate_admission_decision": "NONE",
        "model_quality_verdict": "NONE",
        "model_access_before_shutdown": "MODEL_ARTIFACT_BODIES_ACCESSED",
        "durable_binary_artifacts": False,
        "training": False,
        "paid_cost_usd": 0.0,
        "paid_model_api": False,
        "candidate_expansion": False,
        "revision_or_file_expansion": False,
        "retry_authority_created": False,
        "external_dispatch_authority_created": False,
        "same_staged_topology_redispatch_authorized_by_this_evidence": False,
        "separate_topology_repair_required": True,
        "prior_qualification_run_id": 34155931982,
    }


def build_markdown() -> str:
    return f"""# B012 Qwen Staged Recovery Infrastructure Cancellation — Run {RUN_ID}

## Classification

Run `{RUN_ID}` preserved durable checkpoints through `init`, `source`, and `quantize`, then the GitHub-hosted runner received a shutdown signal while the frozen raw-code proxy was executing. The raw-code stage was cancelled; Stage 04 upload, Stage 05 finalization, final JSON upload, and the explicit cleanup step did not run to completion.

The canonical classification for this attempt is:

`{FAILURE_CLASS}`

This is not a model-quality verdict. It is also not the earlier `NO_DURABLE_RECOVERY_RESULT` class because this staged topology successfully preserved three JSON checkpoint artifacts before the interruption.

## Exact live evidence

- workflow: `B012 Qwen raw-code staged recovery`
- run: `{RUN_ID}`
- job: `{JOB_ID}`
- candidate: `qwen3.5-0.8b-control`
- canonical main at dispatch: `{BASE_MAIN}`
- run created: `2026-09-08T13:25:14Z`
- raw-code stage began: `2026-09-08T13:35:05Z`
- runner shutdown signal: `2026-09-08T13:44:52.5488705Z`
- run final update: `2026-09-08T13:44:57Z`
- workflow conclusion: `failure`
- raw-code-stage conclusion: `cancelled`
- finalize-stage conclusion: `skipped`
- explicit cleanup conclusion: `skipped`
- workflow timeout budget: `45` minutes

The shutdown occurred before the configured workflow timeout budget. The available log proves a runner shutdown signal and cancellation, but it does not prove a more specific platform root cause. The incident therefore remains infrastructure-classified without attributing an unproven cancellation source.

## Durable progress preserved

Exactly three JSON checkpoint artifacts are durable:

1. Stage 01 `init`: artifact `10058420119`, digest `sha256:fe42fd594f5a5501f25ce2fe2f9449031e1760eec90d71bf2983f6965aa297fc`.
2. Stage 02 `source`: artifact `10058479985`, digest `sha256:1884986d415cacfc7d51b072dd87124cd6c0577e33585a3ec199019883f4e71b`.
3. Stage 03 `quantize`: artifact `10058522893`, digest `sha256:ff094686270f646371a9b218ce0fbc8378d5b2b0cbc4d9f8794b5bfcb6c86f68`.

Stage 02 durably proves all nine exact B010 Qwen files were reacquired and hash/size verified, totaling `1769897109` bytes. The canonical weight body remained SHA-256 `c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c` at `1746942600` bytes.

Stage 03 durably proves exact Q4 regeneration matched the previously qualified identity: Q4_K_M SHA-256 `177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa`, size `541903296` bytes, with `matches_prior_stage03=true`.

These checkpoints prove source and Q4 equivalence only. They do not prove a raw-code result or candidate admission.

## Unproven surfaces

No Stage 04 or Stage 05 artifact exists. Therefore the repository must not infer:

- any completed raw-code case or score;
- any raw-code success/failure verdict;
- any candidate admission decision;
- any model-quality verdict;
- completion of final recovery evidence;
- completion of the explicit ephemeral cleanup step.

The hosted runner terminated the orphan `llama-cli` process after the shutdown. No durable model/GGUF artifact was uploaded. Explicit cleanup completion remains `NOT_PROVEN` because the workflow cleanup step itself was skipped.

## Governance consequence

B012 remains `PENDING`; B013 remains blocked by B012. The executor binding must fail closed as `BLOCKED_PENDING_QWEN_RAW_CODE_RECOVERY_TOPOLOGY_REPAIR` until a genuinely different recovery topology is separately reviewed and activated.

This evidence creates no retry authority, external dispatch authority, candidate expansion, revision/file expansion, training authority, paid-compute authority, paid-model-API authority, production-release authority, Git model binaries, or founder-machine model binaries.

The unchanged staged command must not be reissued from this incident. A later dispatch is only eligible after a new topology repair and separate canonical activation lifecycle re-prove the existing B012 authority and exact-main eligibility.

## Required next action

Design a new repository-only durability repair that preserves the frozen candidate, Q4 identity, raw-code prompts, sampling parameters, runtime identities, and zero-cost boundary while materially reducing the amount of uncheckpointed work before and within raw-code execution. The repair itself must perform no model access and must pass exact-head qualification, independent semantic review, mandatory premerge verification, guarded merge, and exact-main postmerge verification before any later dispatch.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()

    failure_path = root / FAILURE_REL
    if failure_path.exists():
        raise SystemExit(f"incident path unexpectedly exists: {FAILURE_REL}")
    incident = build_incident()
    write_json(failure_path, incident)
    failure_sha = sha256(failure_path)

    binding_path = root / BINDING_REL
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    if binding.get("status") != ACTIVE_STATUS:
        raise SystemExit(f"unexpected binding status: {binding.get('status')}")
    if "qwen_raw_code_staged_recovery_runner_shutdown" in binding:
        raise SystemExit("staged shutdown incident already recorded")
    binding["status"] = BLOCKED_STATUS
    binding["qwen_raw_code_staged_recovery_runner_shutdown"] = {
        "run_id": RUN_ID,
        "job_id": JOB_ID,
        "candidate_id": "qwen3.5-0.8b-control",
        "canonical_main_at_start": BASE_MAIN,
        "runner_shutdown_utc": "2026-09-08T13:44:52.5488705Z",
        "failure_classification": FAILURE_CLASS,
        "failure_evidence_path": FAILURE_REL.as_posix(),
        "failure_evidence_sha256": failure_sha,
        "prior_qualification_run_id": 34155931982,
        "durable_stage_count": 3,
        "durable_stages": ["init", "source", "quantize"],
        "durable_artifact_count": 3,
        "source_reacquisition_verified": True,
        "regenerated_q4_identity": (
            "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"
        ),
        "regenerated_q4_size_bytes": 541903296,
        "raw_code_result": "NONE_DURABLY_PROVEN",
        "model_quality_verdict": "NONE",
        "model_access_before_shutdown": "MODEL_ARTIFACT_BODIES_ACCESSED",
        "candidate_execution_completion": "NOT_PROVEN",
        "ephemeral_cleanup_completion": "NOT_PROVEN",
        "same_staged_topology_redispatch_authorized_by_this_evidence": False,
        "retry_authority_created": False,
        "external_dispatch_authority_created": False,
        "training": False,
        "paid_model_api": False,
        "candidate_expansion": False,
        "revision_or_file_expansion": False,
    }
    write_json(binding_path, binding)

    evidence_path = root / EVIDENCE_REL
    if evidence_path.exists():
        raise SystemExit(f"evidence path unexpectedly exists: {EVIDENCE_REL}")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(build_markdown(), encoding="utf-8")

    replacement_count = 0
    for relative in TEST_FILES:
        path = root / relative
        text = path.read_text(encoding="utf-8")
        count = text.count(f'assert binding["status"] == "{ACTIVE_STATUS}"')
        if count < 1:
            raise SystemExit(f"expected active binding assertion missing: {relative}")
        text = text.replace(
            f'assert binding["status"] == "{ACTIVE_STATUS}"',
            f'assert binding["status"] == "{BLOCKED_STATUS}"',
        )
        path.write_text(text, encoding="utf-8")
        replacement_count += count

    runner_test = root / "tests/contract/test_b012_runner_shutdown_evidence.py"
    runner_text = runner_test.read_text(encoding="utf-8")
    marker = "STAGED_QWEN_EVIDENCE = ROOT / ("
    if marker in runner_text:
        raise SystemExit("staged incident test already present")
    runner_text += f'''\n\nSTAGED_QWEN_EVIDENCE = ROOT / (\n    "artifacts/results/equivalent/B012/failures/"\n    "B012-qwen3.5-0.8b-control-raw-code-staged-recovery-run-{RUN_ID}.json"\n)\nSTAGED_QWEN_EVIDENCE_SHA256 = "{failure_sha}"\nSTAGED_QWEN_FAILURE_CLASS = "{FAILURE_CLASS}"\n\n\ndef test_qwen_staged_shutdown_preserves_partial_progress_without_quality_claim() -> None:\n    evidence = _read_json(STAGED_QWEN_EVIDENCE)\n    binding = _read_json(BINDING)\n    staged = binding["qwen_raw_code_staged_recovery_runner_shutdown"]\n    assert isinstance(staged, dict)\n\n    assert _sha256(STAGED_QWEN_EVIDENCE) == STAGED_QWEN_EVIDENCE_SHA256\n    assert evidence["run_id"] == {RUN_ID}\n    assert evidence["job_id"] == {JOB_ID}\n    assert evidence["canonical_main_at_start"] == "{BASE_MAIN}"\n    assert evidence["failure_classification"] == STAGED_QWEN_FAILURE_CLASS\n    assert evidence["durable_stages"] == ["init", "source", "quantize"]\n    assert evidence["durable_artifact_count"] == 3\n    assert evidence["source_verification"]["file_count"] == 9\n    assert evidence["regenerated_q4"]["matches_prior_stage03"] is True\n    assert evidence["regenerated_q4"]["q4_k_m_sha256"] == (\n        "177a8435373b58e09910ee68e6643f656b5d93b6d64e03ee4c37be4a86c995fa"\n    )\n    assert evidence["raw_code_stage_conclusion"] == "cancelled"\n    assert evidence["raw_code_result"] == "NONE_DURABLY_PROVEN"\n    assert evidence["model_quality_verdict"] == "NONE"\n    assert evidence["candidate_admission_decision"] == "NONE"\n    assert evidence["ephemeral_cleanup_completion"] == "NOT_PROVEN"\n    assert evidence["retry_authority_created"] is False\n    assert evidence["external_dispatch_authority_created"] is False\n    assert evidence["same_staged_topology_redispatch_authorized_by_this_evidence"] is False\n\n    assert binding["status"] == BLOCKED_STATUS\n    assert staged["run_id"] == {RUN_ID}\n    assert staged["failure_evidence_sha256"] == _sha256(STAGED_QWEN_EVIDENCE)\n    assert staged["durable_stages"] == ["init", "source", "quantize"]\n    assert staged["raw_code_result"] == "NONE_DURABLY_PROVEN"\n    assert staged["model_quality_verdict"] == "NONE"\n    assert staged["retry_authority_created"] is False\n    assert staged["external_dispatch_authority_created"] is False\n''' 
    runner_test.write_text(runner_text, encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "BUILT",
                "incident_sha256": failure_sha,
                "status_assertions_updated": replacement_count,
                "changed_files_expected": 8,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
