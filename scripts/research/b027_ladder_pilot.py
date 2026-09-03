from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from mstr_qualify.schemas import load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "B027"
CAMPAIGN_ID = "b027-offline-ladder-pilot-v0"
CANONICAL_ENTRY_MAIN = "312d40eee8400a0dab94633f891b206f66a82855"
_CANONICAL_REFS = ("refs/heads/main", "refs/remotes/origin/main")
RESULT_ROOT = ROOT / "artifacts" / "results" / "research" / TASK_ID
CONFIG = ROOT / "configs" / "research" / "mstr-research-ladder-v0.json"
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-research-experiment-v2.json"
)
L0 = "L0_CONTRACT_SMOKE"
L1 = "L1_CODE_PROXY"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"expected object: {path}")
    return value


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _commit_all(message: str) -> str:
    _git("add", "-A")
    if not _git("status", "--porcelain"):
        raise RuntimeError(f"expected changes before commit: {message}")
    _git("commit", "-m", message)
    return _git("rev-parse", "HEAD")


def _write_json(path: Path, value: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def _write_content_addressed(directory: Path, value: dict[str, Any]) -> str:
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{digest}.json").write_bytes(raw)
    return f"sha256:{digest}"


def _required_gate_ids(level: str) -> list[str]:
    config = _json(CONFIG)
    levels = config["levels"]
    if not isinstance(levels, list):
        raise TypeError("levels must be a list")
    for row in levels:
        if isinstance(row, dict) and row.get("level") == level:
            gate_ids = row.get("required_gate_ids")
            if not isinstance(gate_ids, list):
                raise TypeError(f"required_gate_ids missing for {level}")
            return [str(value) for value in gate_ids]
    raise KeyError(level)


def _governed_effects() -> dict[str, bool]:
    return {
        "MODEL_WEIGHT_ACCESS": False,
        "GATED_TERMS_ACCEPTANCE": False,
        "PAID_MODEL_API_EXECUTION": False,
        "PAID_COMPUTE": False,
        "RENTED_COMPUTE": False,
        "LARGE_DATASET_INGESTION": False,
        "WEIGHT_CHANGING_TRAINING": False,
        "LONG_TRAINING": False,
        "LARGE_SCALE_RL": False,
        "PRODUCTION_RELEASE": False,
        "MODEL_EXECUTION": False,
        "NETWORK_MODEL_OR_TEACHER_CALL": False,
    }


def _material_result(level: str, *, result_id: str, passed: bool) -> dict[str, Any]:
    fixture = _json(FIXTURE)
    results = fixture["material_results"]
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise TypeError("fixture material result missing")
    result = copy.deepcopy(results[0])
    result.update(
        {
            "result_id": result_id,
            "model_id_or_na": "N/A",
            "model_revision_or_na": "N/A",
            "model_artifact_sha256_or_na": "N/A",
            "model_artifact_size_bytes_or_na": "N/A",
            "model_execution_count_or_na": 0,
            "network_model_or_teacher_call_count_or_na": 0,
            "tokenizer_id_or_na": "N/A",
            "tokenizer_revision_or_na": "N/A",
            "quantization_method_or_na": "N/A",
            "quantizer_tool_revision_or_na": "N/A",
            "runtime_id_or_na": "python",
            "runtime_version_or_commit_or_na": "3.11",
            "runtime_build_flags_or_na": "N/A",
            "os_identity_or_na": "ubuntu-24.04",
            "cpu_identity_or_na": "N/A",
            "total_ram_bytes_or_na": "N/A",
            "thread_count_or_na": "N/A",
            "acceleration_backend_or_na": "N/A",
            "context_length_or_na": "N/A",
            "cache_state_or_na": "N/A",
            "interaction_contract_version_or_na": "N/A",
            "loop_contract_version_or_na": "N/A",
            "harness_profile_id_or_na": "b027-offline-ladder-pilot-v0",
            "task_manifest_id": "B027-bounded-offline-ladder-pilot",
            "verifier_manifest_id": "b027-content-addressed-offline-evaluator-v0",
            "verifier_health_id_or_na": "N/A",
            "sampling_config_id_or_na": (
                "N/A" if level == L0 else "b027-deterministic-zero-sampling-v0"
            ),
            "seed_or_na": 0,
            "result_classification": "PASS" if passed else "FAIL",
            "metrics": {
                "checks_total": 5,
                "checks_passed": 5 if passed else 4,
                "controlled_regression_detected": 0 if passed else 1,
            },
            "wall_time_seconds_or_na": 0.01,
            "resource_cost": {
                "cost_class": "NO_EXTERNAL_EFFECT",
                "cpu_seconds_or_na": 0.01,
                "accelerator_seconds_or_na": "N/A",
                "network_bytes_or_na": 0,
                "peak_ram_bytes_or_na": "N/A",
            },
            "paid_cost_usd": 0,
            "invalidation_reason_or_na": "N/A",
            "evidence_kind": "CONTRACT_ONLY",
            "data_identity_or_na": "N/A",
            "difficulty_identity_or_na": "N/A",
        }
    )
    return result


def _policy(level: str, evaluator_identity: str) -> dict[str, Any]:
    return {
        "schema_version": "mstr.research-promotion-policy.v0",
        "governing_task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "fidelity_level": level,
        "frozen_evaluation_identity": evaluator_identity,
        "criteria": [
            {
                "gate_id": gate_id,
                "operator": "EQ",
                "expected_value": True,
            }
            for gate_id in _required_gate_ids(level)
        ],
    }


def _record(
    level: str,
    *,
    evaluator_identity: str,
    policy_identity: str,
    freeze_sha: str,
    predecessor: dict[str, str] | None,
) -> dict[str, Any]:
    fixture = _json(FIXTURE)
    passed = level == L0
    result_id = (
        "b027-l0-contract-smoke-result"
        if passed
        else "b027-l1-controlled-stop-result"
    )
    record = copy.deepcopy(fixture)
    record.update(
        {
            "experiment_id": (
                "b027-l0-contract-smoke" if passed else "b027-l1-controlled-stop"
            ),
            "campaign_id": CAMPAIGN_ID,
            "parent_identity": (
                "repository:312d40eee8400a0dab94633f891b206f66a82855"
                if passed
                else str(predecessor["promoted_result_id"])
            ),
            "hypothesis": (
                "The frozen ladder promotes a clean offline L0 contract smoke."
                if passed
                else "A controlled L1 code-proxy regression is discarded before L2."
            ),
            "mutable_surface": (
                "repository-owned contract/config smoke"
                if passed
                else "repository-owned controlled code-proxy config mutation"
            ),
            "mutation_identity": (
                "b027-mutation:none"
                if passed
                else "b027-mutation:controlled-code-proxy-regression-v0"
            ),
            "frozen_evaluation_identity": evaluator_identity,
            "fidelity_level": level,
            "predecessor_promotion": (
                None
                if passed
                else {
                    "experiment_id": predecessor["experiment_id"],
                    "experiment_record_sha256": predecessor["record_sha256"],
                }
            ),
            "budget": {
                "budget_id": "b027-offline-zero-cost-v0",
                "max_wall_time_seconds": 120,
                "max_material_results": 2,
                "max_paid_cost_usd": 0,
                "resource_class": "CONTRACT_ONLY",
            },
            "material_results": [
                _material_result(level, result_id=result_id, passed=passed)
            ],
            "hard_gate_results": [],
            "promotion_decision": "PROMOTE" if passed else "STOP",
            "decision_reason": (
                "All required L0 gates passed under the frozen offline evaluator."
                if passed
                else (
                    "Controlled code-proxy threshold regression triggered "
                    "early discard before L2."
                )
            ),
            "aggregate_resource_cost": {
                "wall_time_seconds": 0.01,
                "material_result_count": 1,
                "paid_cost_usd": 0,
                "resource_class": "CONTRACT_ONLY",
            },
            "external_effect_authority": None,
            "governing_task_id": TASK_ID,
            "promoted_result_id_or_na": result_id if passed else "N/A",
            "q4_promotion_record_identity_or_na": "N/A",
            "governed_effects": _governed_effects(),
            "promotion_policy_identity": policy_identity,
            "record_mode": "CAMPAIGN_RESULT",
            "campaign_freeze_commit_sha_or_na": freeze_sha,
            "canonical_evidence_commit_sha_or_na": "N/A",
            "q4_candidate_binding_identity_or_na": "N/A",
        }
    )
    failing_gate = "code_proxy_thresholds" if level == L1 else None
    record["hard_gate_results"] = [
        {
            "gate_id": gate_id,
            "status": "FAIL" if gate_id == failing_gate else "PASS",
            "evidence_identity": "sha256:" + "0" * 64,
            "reason": (
                "Controlled threshold regression observed."
                if gate_id == failing_gate
                else "Required gate passed under frozen evaluator."
            ),
        }
        for gate_id in _required_gate_ids(level)
    ]
    return record


def _write_evidence(
    record: dict[str, Any],
    *,
    freeze_sha: str,
    failing_gate: str | None,
) -> None:
    results = record["material_results"]
    gates = record["hard_gate_results"]
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise TypeError("material result missing")
    if not isinstance(gates, list):
        raise TypeError("hard gates missing")
    subject = results[0]
    subject_identity = str(subject["result_id"])
    experiment_id = str(record["experiment_id"])
    evaluator_identity = str(record["frozen_evaluation_identity"])

    for gate in gates:
        if not isinstance(gate, dict):
            raise TypeError("gate must be an object")
        gate_id = str(gate["gate_id"])
        observed = gate_id != failing_gate
        subject_evidence_identity = _write_content_addressed(
            RESULT_ROOT / "subject-evidence",
            {
                "schema_version": "mstr.research-subject-evidence.v0",
                "governing_task_id": TASK_ID,
                "campaign_id": CAMPAIGN_ID,
                "experiment_id": experiment_id,
                "subject_identity": subject_identity,
                "material_result": copy.deepcopy(subject),
            },
        )
        verifier_manifest_identity = _write_content_addressed(
            RESULT_ROOT / "verifier-manifests",
            {
                "schema_version": "mstr.research-verifier-manifest.v0",
                "verifier_manifest_id": f"b027-offline-verifier:{gate_id}",
                "gate_id": gate_id,
                "frozen_evaluation_identity": evaluator_identity,
            },
        )
        verifier_health_identity = _write_content_addressed(
            RESULT_ROOT / "verifier-health",
            {
                "schema_version": "mstr.research-verifier-health.v0",
                "verifier_health_id": f"b027-offline-health:{gate_id}",
                "verifier_manifest_identity": verifier_manifest_identity,
                "frozen_evaluation_identity": evaluator_identity,
                "status": "HEALTHY",
            },
        )
        verifier_result_identity = _write_content_addressed(
            RESULT_ROOT / "verifier-results",
            {
                "schema_version": "mstr.research-verifier-result.v0",
                "governing_task_id": TASK_ID,
                "campaign_id": CAMPAIGN_ID,
                "experiment_id": experiment_id,
                "gate_id": gate_id,
                "frozen_evaluation_identity": evaluator_identity,
                "verifier_manifest_identity": verifier_manifest_identity,
                "verifier_health_identity": verifier_health_identity,
                "subject_identity": subject_identity,
                "subject_evidence_identity": subject_evidence_identity,
                "observed_value": observed,
            },
        )
        verifier_evidence_identity = _write_content_addressed(
            RESULT_ROOT / "verifier-evidence",
            {
                "schema_version": "mstr.research-verifier-evidence.v0",
                "governing_task_id": TASK_ID,
                "campaign_id": CAMPAIGN_ID,
                "experiment_id": experiment_id,
                "gate_id": gate_id,
                "frozen_evaluation_identity": evaluator_identity,
                "verifier_manifest_identity": verifier_manifest_identity,
                "verifier_health_identity": verifier_health_identity,
                "subject_identity": subject_identity,
                "subject_evidence_identity": subject_evidence_identity,
                "verifier_result_identity": verifier_result_identity,
                "verifier_result_json_pointer": "/observed_value",
            },
        )
        gate["evidence_identity"] = _write_content_addressed(
            RESULT_ROOT / "gate-evidence",
            {
                "schema_version": "mstr.research-gate-evidence.v1",
                "governing_task_id": TASK_ID,
                "campaign_id": CAMPAIGN_ID,
                "experiment_id": experiment_id,
                "gate_id": gate_id,
                "frozen_evaluation_identity": evaluator_identity,
                "campaign_freeze_commit_sha": freeze_sha,
                "source_evidence_identity": verifier_evidence_identity,
                "source_json_pointer": "/observed_value",
            },
        )


def _registry_write(record: dict[str, Any]) -> tuple[Path, str]:
    path = RESULT_ROOT / "registry" / f"{record['experiment_id']}.json"
    return path, _write_json(path, record)


def _resolve_ref(ref: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    value = completed.stdout.strip()
    return value if completed.returncode == 0 and value else None


def _canonical_ref_snapshot() -> dict[str, str | None]:
    return {ref: _resolve_ref(ref) for ref in _CANONICAL_REFS}


def _require_trusted_canonical_entry(
    expected_sha: str = CANONICAL_ENTRY_MAIN,
) -> dict[str, str | None]:
    snapshot = _canonical_ref_snapshot()
    origin_main = snapshot["refs/remotes/origin/main"]
    local_main = snapshot["refs/heads/main"]
    if origin_main != expected_sha:
        raise RuntimeError(
            f"origin/main is not the trusted B027 canonical entry: {origin_main!r}"
        )
    if local_main is not None and local_main != expected_sha:
        raise RuntimeError(
            f"local main disagrees with the trusted B027 canonical entry: {local_main!r}"
        )
    return snapshot


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    completed = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode not in {0, 1}:
        raise RuntimeError(
            f"unable to compare Git ancestry: {ancestor} -> {descendant}: "
            f"{completed.stderr.strip()}"
        )
    return completed.returncode == 0


def _is_strict_ancestor(ancestor: str, descendant: str) -> bool:
    return ancestor != descendant and _is_ancestor(ancestor, descendant)


def _validate_schema_shape(record: dict[str, Any]) -> None:
    schema = load_schema("mstr-research-experiment-v2")
    errors = sorted(
        Draft202012Validator(schema).iter_errors(record),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        joined = "; ".join(error.message for error in errors)
        raise RuntimeError(f"B027 candidate record schema validation failed: {joined}")


def _validate_record_candidate(record: dict[str, Any], head_sha: str) -> None:
    before = _require_trusted_canonical_entry()
    try:
        _validate_schema_shape(record)
        if not _is_ancestor(CANONICAL_ENTRY_MAIN, head_sha):
            raise RuntimeError("candidate head does not descend from canonical B027 entry")
        freeze_sha = record.get("campaign_freeze_commit_sha_or_na")
        evidence_sha = record.get("canonical_evidence_commit_sha_or_na")
        if not isinstance(freeze_sha, str) or len(freeze_sha) != 40:
            raise RuntimeError("candidate campaign freeze commit is not concrete")
        if not isinstance(evidence_sha, str) or len(evidence_sha) != 40:
            raise RuntimeError("candidate evidence commit is not concrete")
        if not _is_strict_ancestor(freeze_sha, evidence_sha):
            raise RuntimeError("candidate freeze must strictly precede evidence")
        if not _is_ancestor(evidence_sha, head_sha):
            raise RuntimeError("candidate evidence is not visible at candidate head")

        predecessor = record.get("predecessor_promotion")
        if isinstance(predecessor, dict):
            experiment_id = predecessor.get("experiment_id")
            expected_digest = predecessor.get("experiment_record_sha256")
            if not isinstance(experiment_id, str) or not isinstance(expected_digest, str):
                raise RuntimeError("candidate predecessor binding is incomplete")
            predecessor_path = RESULT_ROOT / "registry" / f"{experiment_id}.json"
            raw = predecessor_path.read_bytes()
            actual_digest = hashlib.sha256(raw).hexdigest()
            if actual_digest != expected_digest:
                raise RuntimeError("candidate predecessor registry digest mismatch")
            predecessor_record = json.loads(raw)
            predecessor_evidence = predecessor_record.get(
                "canonical_evidence_commit_sha_or_na"
            )
            if not isinstance(predecessor_evidence, str) or len(predecessor_evidence) != 40:
                raise RuntimeError("candidate predecessor evidence commit is not concrete")
            if not _is_strict_ancestor(predecessor_evidence, freeze_sha):
                raise RuntimeError(
                    "candidate predecessor evidence must precede successor freeze"
                )
    finally:
        after = _canonical_ref_snapshot()
        if after != before:
            raise RuntimeError("B027 candidate validation mutated canonical Git refs")


def _require_current_canonical_main() -> tuple[str, dict[str, str | None]]:
    snapshot = _canonical_ref_snapshot()
    origin_main = snapshot["refs/remotes/origin/main"]
    local_main = snapshot["refs/heads/main"]
    if origin_main is None:
        raise RuntimeError("origin/main is unavailable for canonical validation")
    if local_main is not None and local_main != origin_main:
        raise RuntimeError("local main disagrees with origin/main")
    if not _is_ancestor(CANONICAL_ENTRY_MAIN, origin_main):
        raise RuntimeError("canonical main no longer descends from the B027 entry commit")
    return origin_main, snapshot


def _validate_record_canonical(record: dict[str, Any]) -> None:
    _canonical_main, before = _require_current_canonical_main()
    try:
        validate_instance("mstr-research-experiment-v2", record, repository_root=ROOT)
    finally:
        after = _canonical_ref_snapshot()
        if after != before:
            raise RuntimeError("B027 canonical validation mutated canonical Git refs")


def _write_final_docs(
    *,
    evaluator_identity: str,
    l0: dict[str, Any],
    l0_digest: str,
    l1: dict[str, Any],
    l1_digest: str,
    commits: dict[str, str],
) -> None:
    ledger = {
        "schema_version": "mstr.b027-ladder-pilot-ledger.v0",
        "task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "canonical_entry_main": CANONICAL_ENTRY_MAIN,
        "canonical_history_status": "PENDING_POST_MERGE_VALIDATION",
        "candidate_validation_kind": "PROSPECTIVE_NO_CANONICAL_REF_REWRITE",
        "frozen_evaluation_identity": evaluator_identity,
        "external_effect_authority_required": False,
        "governed_effects": _governed_effects(),
        "paid_cost_usd": 0,
        "model_execution_count": 0,
        "network_model_or_teacher_call_count": 0,
        "large_dataset_ingestion": False,
        "weight_changing_training": False,
        "sequence": [
            {
                "level": L0,
                "experiment_id": l0["experiment_id"],
                "record_sha256": l0_digest,
                "decision": l0["promotion_decision"],
                "promoted_result_id": l0["promoted_result_id_or_na"],
                "freeze_commit": commits["l0_freeze"],
                "evidence_commit": commits["l0_evidence"],
                "registry_commit": commits["l0_registry"],
            },
            {
                "level": L1,
                "experiment_id": l1["experiment_id"],
                "record_sha256": l1_digest,
                "decision": l1["promotion_decision"],
                "promoted_result_id": l1["promoted_result_id_or_na"],
                "freeze_commit": commits["l1_freeze"],
                "evidence_commit": commits["l1_evidence"],
                "registry_commit": commits["l1_registry"],
                "early_discard_gate": "code_proxy_thresholds",
            },
        ],
        "levels_not_executed": [
            "L2_EXECUTABLE_REPO",
            "L3_DIRECTION_TO_DONE",
            "L4_Q4_UNIVERSAL_LAPTOP",
        ],
        "campaign_result": "QUALIFIED_PROMOTION_AND_EARLY_DISCARD",
    }
    _write_json(RESULT_ROOT / "campaign-ledger.json", ledger)

    evidence = f"""# B027 — Research Ladder Pilot Evidence

**Task:** `B027`
**State:** `IMPLEMENTATION_ACTIVE`
**Canonical entry main:** `312d40eee8400a0dab94633f891b206f66a82855`
**Campaign:** `{CAMPAIGN_ID}`

## Entry gate

```text
TASK = B027
CANONICAL_MAIN = 312d40eee8400a0dab94633f891b206f66a82855
B026_STATE = COMPLETE_CANONICAL
B027_STATE = PENDING
B027_ELIGIBLE = true
EXTERNAL_AUTHORITY_REQUIRED = false
POST_B026_CLOSEOUT_PROOF = 33690094117
```

## Pilot result

The bounded repository-owned campaign exercised the frozen B026 ladder without model inference,
weight access, network model/teacher calls, paid compute, dataset ingestion, training, RL, Q4
execution, or release activity.

- L0 `{l0["experiment_id"]}`: `PROMOTE`
- L1 `{l1["experiment_id"]}`: `STOP`
- early-discard gate: `code_proxy_thresholds`
- L2/L3/L4: not executed after the L1 hard reject
- frozen evaluator: `{evaluator_identity}`
- full ledger: `artifacts/results/research/B027/campaign-ledger.json`
- premerge canonical-history status: `PENDING_POST_MERGE_VALIDATION`
- premerge validation kind: `PROSPECTIVE_NO_CANONICAL_REF_REWRITE`
- L0 registry SHA-256: `{l0_digest}`
- L1 registry SHA-256: `{l1_digest}`

The L1 record consumes the exact L0 promoted result through the immutable predecessor registry
binding. Promotion policies precede their evidence commits, gate observations are derived from
content-addressed verifier results, and the same frozen evaluator identity is used across both
levels.

Premerge candidate validation never rewrites `refs/heads/main` or
`refs/remotes/origin/main` and does not claim that feature-only campaign commits are
already canonical. Full `mstr.research-experiment.v2` canonical-history semantic
validation is intentionally deferred to mandatory post-merge verification on real
`main`, where the campaign commits must actually be canonical ancestors.

## Campaign commit ledger

```text
L0_POLICY_FREEZE = {commits["l0_freeze"]}
L0_EVIDENCE = {commits["l0_evidence"]}
L0_REGISTRY = {commits["l0_registry"]}
L1_POLICY_FREEZE = {commits["l1_freeze"]}
L1_EVIDENCE = {commits["l1_evidence"]}
L1_REGISTRY = {commits["l1_registry"]}
```

## Authority boundary

```text
MODEL_WEIGHT_ACCESS = NONE
MODEL_EXECUTION = NONE
RESEARCH_CAMPAIGN_EXTERNAL_EFFECT = NONE
VERIFIER_EXTERNAL_EFFECT = NONE
TEACHER_API_EXECUTION = NONE
PAID_MODEL_API = NONE
PAID_COMPUTE = NONE
NETWORK_MODEL_OR_TEACHER_CALL = NONE
LARGE_DATASET_INGESTION = NONE
PRIVATE_USER_DATA_INGESTION = NONE
PRODUCTION_TRACE_INGESTION = NONE
WEIGHT_CHANGING_TRAINING = NONE
LARGE_SCALE_RL = NONE
Q4_EXECUTION = NONE
PRODUCTION_RELEASE = NONE
```

B027 remains `PENDING` in the canonical task ledger until this implementation is independently
qualified, reviewed, merged, post-merge verified, and separately closed out.
"""
    evidence_path = ROOT / "evidence" / "mstr-000b" / "B027-ladder-pilot.md"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(evidence, encoding="utf-8")


def run() -> None:
    _require_trusted_canonical_entry()
    script_digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    evaluator_identity = f"sha256:{script_digest}"
    RESULT_ROOT.mkdir(parents=True, exist_ok=True)

    entry_path = RESULT_ROOT / "entry-eligibility.json"
    if not entry_path.exists():
        raise FileNotFoundError(entry_path)

    manifest = {
        "schema_version": "mstr.b027-ladder-pilot-manifest.v0",
        "task_id": TASK_ID,
        "campaign_id": CAMPAIGN_ID,
        "canonical_entry_main": CANONICAL_ENTRY_MAIN,
        "canonical_history_status": "PENDING_POST_MERGE_VALIDATION",
        "candidate_validation_kind": "PROSPECTIVE_NO_CANONICAL_REF_REWRITE",
        "harness_path": "scripts/research/b027_ladder_pilot.py",
        "harness_sha256": script_digest,
        "frozen_evaluation_identity": evaluator_identity,
        "planned_levels": [L0, L1],
        "early_discard_before": "L2_EXECUTABLE_REPO",
        "max_paid_cost_usd": 0,
        "model_execution_authorized": False,
        "network_model_or_teacher_call_authorized": False,
        "weight_changing_training_authorized": False,
        "large_dataset_ingestion_authorized": False,
    }
    _write_json(RESULT_ROOT / "campaign-manifest.json", manifest)

    l0_policy_identity = _write_content_addressed(
        RESULT_ROOT / "promotion-policies",
        _policy(L0, evaluator_identity),
    )
    l0_freeze = _commit_all("feat(mstr-000b): freeze B027 L0 pilot policy")

    l0 = _record(
        L0,
        evaluator_identity=evaluator_identity,
        policy_identity=l0_policy_identity,
        freeze_sha=l0_freeze,
        predecessor=None,
    )
    _write_evidence(l0, freeze_sha=l0_freeze, failing_gate=None)
    l0_evidence = _commit_all("evidence(mstr-000b): record B027 L0 gate evidence")
    l0["canonical_evidence_commit_sha_or_na"] = l0_evidence
    _, l0_digest = _registry_write(l0)
    l0_registry = _commit_all("evidence(mstr-000b): record B027 L0 promotion")
    _validate_record_candidate(l0, l0_registry)

    l1_policy_identity = _write_content_addressed(
        RESULT_ROOT / "promotion-policies",
        _policy(L1, evaluator_identity),
    )
    l1_freeze = _commit_all("feat(mstr-000b): freeze B027 L1 early-discard policy")

    l1 = _record(
        L1,
        evaluator_identity=evaluator_identity,
        policy_identity=l1_policy_identity,
        freeze_sha=l1_freeze,
        predecessor={
            "experiment_id": str(l0["experiment_id"]),
            "record_sha256": l0_digest,
            "promoted_result_id": str(l0["promoted_result_id_or_na"]),
        },
    )
    _write_evidence(l1, freeze_sha=l1_freeze, failing_gate="code_proxy_thresholds")
    l1_evidence = _commit_all("evidence(mstr-000b): record B027 L1 gate evidence")
    l1["canonical_evidence_commit_sha_or_na"] = l1_evidence
    _, l1_digest = _registry_write(l1)
    l1_registry = _commit_all("evidence(mstr-000b): record B027 L1 early discard")
    _validate_record_candidate(l1, l1_registry)

    commits = {
        "l0_freeze": l0_freeze,
        "l0_evidence": l0_evidence,
        "l0_registry": l0_registry,
        "l1_freeze": l1_freeze,
        "l1_evidence": l1_evidence,
        "l1_registry": l1_registry,
    }
    _write_final_docs(
        evaluator_identity=evaluator_identity,
        l0=l0,
        l0_digest=l0_digest,
        l1=l1,
        l1_digest=l1_digest,
        commits=commits,
    )
    final = _commit_all("feat(mstr-000b): qualify B027 research ladder pilot")
    _validate_record_candidate(l0, final)
    _validate_record_candidate(l1, final)
    print(
        json.dumps(
            {
                "campaign_id": CAMPAIGN_ID,
                "final_head": final,
                "l0_record_sha256": l0_digest,
                "l1_record_sha256": l1_digest,
                "frozen_evaluation_identity": evaluator_identity,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    run()
