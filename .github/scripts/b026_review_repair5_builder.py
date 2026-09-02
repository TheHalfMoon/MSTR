from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd()


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected object")
    return value


def save_json(path: str, value: dict) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def replace_regex(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one regex replacement, found {count}")
    return updated


def int_or_na() -> dict:
    return {
        "oneOf": [
            {"type": "integer", "minimum": 0},
            {"const": "N/A"},
        ]
    }


def sha_or_na() -> dict:
    return {
        "oneOf": [
            {"const": "N/A"},
            {"type": "string", "pattern": "^[0-9a-f]{40}$"},
        ]
    }


def content_sha_or_na() -> dict:
    return {
        "oneOf": [
            {"const": "N/A"},
            {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        ]
    }


# ---------------------------------------------------------------------------
# JSON contracts
# ---------------------------------------------------------------------------
material_schema_paths = [
    "schemas/mstr-material-result-identity-v0.schema.json",
    "specs/002-code-model-supremacy-foundation/contracts/mstr-material-result-identity-v0.schema.json",
]
research_schema_paths = [
    "schemas/mstr-research-experiment-v2.schema.json",
    "specs/002-code-model-supremacy-foundation/contracts/mstr-research-experiment-v2.schema.json",
]

for path in material_schema_paths:
    schema = load_json(path)
    props = schema["properties"]
    required = schema["required"]
    props["model_execution_count_or_na"] = int_or_na()
    props["network_model_or_teacher_call_count_or_na"] = int_or_na()
    props["model_artifact_size_bytes_or_na"] = int_or_na()
    for field in (
        "model_execution_count_or_na",
        "network_model_or_teacher_call_count_or_na",
        "model_artifact_size_bytes_or_na",
    ):
        if field not in required:
            required.append(field)
    save_json(path, schema)

for path in research_schema_paths:
    schema = load_json(path)
    material = schema["$defs"]["material_result_identity"]
    props = material["properties"]
    required = material["required"]
    props["model_execution_count_or_na"] = int_or_na()
    props["network_model_or_teacher_call_count_or_na"] = int_or_na()
    props["model_artifact_size_bytes_or_na"] = int_or_na()
    for field in (
        "model_execution_count_or_na",
        "network_model_or_teacher_call_count_or_na",
        "model_artifact_size_bytes_or_na",
    ):
        if field not in required:
            required.append(field)

    effects = schema["$defs"]["governed_effects"]
    effect_props = effects["properties"]
    effect_required = effects["required"]
    for field in ("MODEL_EXECUTION", "NETWORK_MODEL_OR_TEACHER_CALL"):
        effect_props[field] = {"type": "boolean"}
        if field not in effect_required:
            effect_required.append(field)

    root_props = schema["properties"]
    root_required = schema["required"]
    root_props["record_mode"] = {"enum": ["CONTRACT_FIXTURE", "CAMPAIGN_RESULT"]}
    root_props["campaign_freeze_commit_sha_or_na"] = sha_or_na()
    root_props["canonical_evidence_commit_sha_or_na"] = sha_or_na()
    root_props["q4_candidate_binding_identity_or_na"] = content_sha_or_na()
    root_props["promotion_policy_identity"] = content_sha_or_na()
    for field in (
        "record_mode",
        "campaign_freeze_commit_sha_or_na",
        "canonical_evidence_commit_sha_or_na",
        "q4_candidate_binding_identity_or_na",
    ):
        if field not in root_required:
            root_required.append(field)
    save_json(path, schema)

# ---------------------------------------------------------------------------
# Fixtures: contract-only fixtures are explicitly non-campaign evidence.
# ---------------------------------------------------------------------------
for path in (
    "tests/fixtures/schemas/valid/mstr-material-result-identity-v0.json",
    "tests/fixtures/schemas/invalid/mstr-material-result-identity-v0.json",
):
    value = load_json(path)
    value["model_execution_count_or_na"] = 0
    value["network_model_or_teacher_call_count_or_na"] = 0
    value["model_artifact_size_bytes_or_na"] = "N/A"
    save_json(path, value)

for path in (
    "tests/fixtures/schemas/valid/mstr-research-experiment-v2.json",
    "tests/fixtures/schemas/invalid/mstr-research-experiment-v2.json",
):
    value = load_json(path)
    for result in value.get("material_results", []):
        if isinstance(result, dict):
            result["model_execution_count_or_na"] = 0
            result["network_model_or_teacher_call_count_or_na"] = 0
            result["model_artifact_size_bytes_or_na"] = "N/A"
    effects = value["governed_effects"]
    effects["MODEL_EXECUTION"] = False
    effects["NETWORK_MODEL_OR_TEACHER_CALL"] = False
    value["record_mode"] = "CONTRACT_FIXTURE"
    value["campaign_freeze_commit_sha_or_na"] = "N/A"
    value["canonical_evidence_commit_sha_or_na"] = "N/A"
    value["q4_candidate_binding_identity_or_na"] = "N/A"
    value["promotion_policy_identity"] = "N/A"
    if path.startswith("tests/fixtures/schemas/valid/"):
        value["promotion_decision"] = "STOP"
        value["decision_reason"] = "Contract fixture validates the frozen shape without claiming campaign execution."
        value["promoted_result_id_or_na"] = "N/A"
    save_json(path, value)

# Old content-addressed B026 examples lived only on the feature branch and must
# not masquerade as already-canonical campaign evidence.
for directory in (
    ROOT / "artifacts/results/research/B026/gate-evidence",
    ROOT / "artifacts/results/research/B026/promotion-policies",
):
    if directory.exists():
        for child in directory.glob("*.json"):
            child.unlink()

# ---------------------------------------------------------------------------
# Research ladder config
# ---------------------------------------------------------------------------
config_path = "configs/research/mstr-research-ladder-v0.json"
config = load_json(config_path)
promotion = config["promotion_policy"]
promotion.update(
    {
        "canonical_git_history_resolution_required": True,
        "promotion_policy_must_precede_evidence_commit": True,
        "gate_observation_underlying_evidence_resolution_required": True,
        "model_execution_authority_required": True,
        "network_model_or_teacher_call_authority_required": True,
        "l4_reference_envelope_semantically_enforced": True,
        "q4_candidate_lineage_binding_required": True,
    }
)
resolution = config["canonical_resolution"]
resolution["record_integrity"] = (
    "SHA-256 over exact Git blob bytes resolved from an explicit canonical-main-ancestor commit"
)
resolution["campaign_freeze_commit_field"] = "campaign_freeze_commit_sha_or_na"
resolution["canonical_evidence_commit_field"] = "canonical_evidence_commit_sha_or_na"
resolution["canonical_history_rule"] = (
    "campaign freeze and evidence commits must both be ancestors of canonical main; "
    "freeze must be a strict ancestor of evidence"
)
for effect in ("MODEL_EXECUTION", "NETWORK_MODEL_OR_TEACHER_CALL"):
    if effect not in resolution["governed_effects"]:
        resolution["governed_effects"].append(effect)
resolution["verifier_evidence_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/verifier-evidence/{sha256}.json"
)
resolution["q4_candidate_binding_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/q4-bindings/{sha256}.json"
)
resolution["promotion_policy_binding"] = (
    "promotion_policy_identity resolves from the strict ancestor campaign-freeze commit; "
    "gate evidence resolves from the later canonical evidence commit and derives its observed value "
    "from separately content-addressed verifier evidence"
)
resolution["gate_evidence_record_contract"] = {
    "schema_version": "mstr.research-gate-evidence.v1",
    "required_fields": [
        "governing_task_id",
        "campaign_id",
        "experiment_id",
        "gate_id",
        "frozen_evaluation_identity",
        "campaign_freeze_commit_sha",
        "source_evidence_identity",
        "source_json_pointer",
    ],
    "status_is_computed_from_predeclared_policy": True,
    "observed_value_must_be_derived_from_source_evidence": True,
}
resolution["verifier_evidence_record_contract"] = {
    "schema_version": "mstr.research-verifier-evidence.v0",
    "required_fields": [
        "governing_task_id",
        "campaign_id",
        "experiment_id",
        "gate_id",
        "frozen_evaluation_identity",
        "verifier_manifest_id",
        "verifier_health_identity",
        "subject_identity",
        "observed_value",
    ],
}
resolution["q4_candidate_binding_record_contract"] = {
    "schema_version": "mstr.research-q4-candidate-binding.v0",
    "required_fields": [
        "q4_promotion_record_identity",
        "model_id",
        "model_revision",
        "source_checkpoint_sha256",
        "canonical_q4_artifact_sha256",
    ],
}
save_json(config_path, config)

# ---------------------------------------------------------------------------
# Python semantic validator
# ---------------------------------------------------------------------------
py_path = ROOT / "src/mstr_qualify/schemas.py"
text = py_path.read_text(encoding="utf-8")
text = replace_once(text, "import math\n", "import math\nimport subprocess\n", "subprocess import")

new_material_semantics = r'''def _material_result_identity_semantic_errors(instance: Any) -> tuple[str, ...]:
    """Reject opaque or causally incomplete B026 material-result identities."""

    if not isinstance(instance, dict):
        return ()

    errors: list[str] = []
    for field in _B026_IDENTITY_OR_NA_FIELDS:
        value = instance.get(field)
        if _is_ambiguous_identity(value):
            errors.append(f"$.{field}: must be exact identity text or the literal 'N/A'")

    for field in ("task_manifest_id", "verifier_manifest_id"):
        value = instance.get(field)
        if _is_ambiguous_identity(value) or value == "N/A":
            errors.append(f"$.{field}: must be a concrete non-ambiguous identity")

    evidence_kind = instance.get("evidence_kind")
    model_id = instance.get("model_id_or_na")
    execution_count = instance.get("model_execution_count_or_na")
    if evidence_kind in {"EVALUATION", "TRAINING_EVIDENCE"} and model_id != "N/A":
        if (
            isinstance(execution_count, bool)
            or not isinstance(execution_count, int)
            or execution_count <= 0
        ):
            errors.append(
                "$.model_execution_count_or_na: model evaluation/training evidence requires "
                "a positive execution count"
            )

    return tuple(sorted(errors))
'''
text = replace_regex(
    text,
    r"def _material_result_identity_semantic_errors\(instance: Any\) -> tuple\[str, \.\.\.\]:.*?(?=\n\n_B026_GOVERNED_EFFECTS =)",
    new_material_semantics.rstrip(),
    "material result semantic function",
)

new_governed_block = r'''_B026_GOVERNED_EFFECTS = (
    "MODEL_EXECUTION",
    "MODEL_WEIGHT_ACCESS",
    "GATED_TERMS_ACCEPTANCE",
    "PAID_MODEL_API_EXECUTION",
    "PAID_COMPUTE",
    "RENTED_COMPUTE",
    "NETWORK_MODEL_OR_TEACHER_CALL",
    "LARGE_DATASET_INGESTION",
    "WEIGHT_CHANGING_TRAINING",
    "LONG_TRAINING",
    "LARGE_SCALE_RL",
    "PRODUCTION_RELEASE",
)
_B026_LEVEL_CONCRETE_FIELDS: Mapping[str, tuple[str, ...]] = {
    "L1_CODE_PROXY": (
        "sampling_config_id_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
    ),
    "L2_EXECUTABLE_REPO": (
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "verifier_health_id_or_na",
    ),
    "L3_DIRECTION_TO_DONE": (
        "interaction_contract_version_or_na",
        "loop_contract_version_or_na",
        "harness_profile_id_or_na",
        "verifier_health_id_or_na",
    ),
    "L4_Q4_UNIVERSAL_LAPTOP": (
        "model_id_or_na",
        "model_revision_or_na",
        "model_artifact_sha256_or_na",
        "model_artifact_size_bytes_or_na",
        "model_execution_count_or_na",
        "tokenizer_id_or_na",
        "tokenizer_revision_or_na",
        "quantization_method_or_na",
        "quantizer_tool_revision_or_na",
        "runtime_id_or_na",
        "runtime_version_or_commit_or_na",
        "runtime_build_flags_or_na",
        "os_identity_or_na",
        "cpu_identity_or_na",
        "acceleration_backend_or_na",
        "cache_state_or_na",
    ),
}
'''
text = replace_regex(
    text,
    r"_B026_GOVERNED_EFFECTS = \(.*?(?=\n\ndef _b026_binding_id)",
    new_governed_block.rstrip(),
    "governed effects/constants",
)

new_repository_loader = r'''def _b026_git(repository_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Run one read-only Git command against the repository."""

    return subprocess.run(
        ["git", *args],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _b026_commit_sha(value: object) -> str | None:
    if not isinstance(value, str) or len(value) != 40:
        return None
    if any(character not in "0123456789abcdef" for character in value):
        return None
    return value


def _b026_canonical_main_sha(repository_root: Path) -> str | None:
    """Resolve canonical main without trusting a feature branch or dirty worktree."""

    for ref in ("refs/remotes/origin/main", "refs/heads/main"):
        result = _b026_git(repository_root, "rev-parse", "--verify", f"{ref}^{{commit}}")
        candidate = result.stdout.strip() if result.returncode == 0 else ""
        if _b026_commit_sha(candidate) is not None:
            return candidate
    return None


def _b026_is_canonical_commit(repository_root: Path, commit_sha: object) -> bool:
    candidate = _b026_commit_sha(commit_sha)
    main_sha = _b026_canonical_main_sha(repository_root)
    if candidate is None or main_sha is None:
        return False
    exists = _b026_git(repository_root, "cat-file", "-e", f"{candidate}^{{commit}}")
    if exists.returncode != 0:
        return False
    ancestry = _b026_git(repository_root, "merge-base", "--is-ancestor", candidate, main_sha)
    return ancestry.returncode == 0


def _b026_strictly_precedes(repository_root: Path, older: object, newer: object) -> bool:
    old_sha = _b026_commit_sha(older)
    new_sha = _b026_commit_sha(newer)
    if old_sha is None or new_sha is None or old_sha == new_sha:
        return False
    if not _b026_is_canonical_commit(repository_root, old_sha):
        return False
    if not _b026_is_canonical_commit(repository_root, new_sha):
        return False
    return _b026_git(repository_root, "merge-base", "--is-ancestor", old_sha, new_sha).returncode == 0


def _b026_repository_json(
    repository_root: Path,
    relative_path: Path,
    *,
    canonical_commit_sha: object,
) -> tuple[dict[str, Any], str] | None:
    """Load JSON only from one explicit canonical-main-ancestor Git blob."""

    commit_sha = _b026_commit_sha(canonical_commit_sha)
    if commit_sha is None or not _b026_is_canonical_commit(repository_root, commit_sha):
        return None
    if relative_path.is_absolute() or ".." in relative_path.parts:
        return None
    path_text = relative_path.as_posix()
    tree = _b026_git(repository_root, "ls-tree", commit_sha, "--", path_text)
    if tree.returncode != 0:
        return None
    line = tree.stdout.strip()
    if not line or "\t" not in line:
        return None
    metadata, observed_path = line.split("\t", 1)
    fields = metadata.split()
    if observed_path != path_text or len(fields) != 3:
        return None
    mode, object_type, _object_sha = fields
    if object_type != "blob" or mode not in {"100644", "100755"}:
        return None
    blob = _b026_git(repository_root, "show", f"{commit_sha}:{path_text}")
    if blob.returncode != 0:
        return None
    try:
        raw = blob.stdout.encode("utf-8")
        decoded = json.loads(blob.stdout)
    except (UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(decoded, dict):
        return None
    return decoded, hashlib.sha256(raw).hexdigest()
'''
text = replace_regex(
    text,
    r"def _b026_repository_json\(.*?(?=\n\ndef _b026_authority_limits)",
    new_repository_loader.rstrip(),
    "canonical Git repository loader",
)

new_policy_function = r'''def _b026_promotion_policy_errors(
    instance: Mapping[str, Any],
    *,
    repository_root: Path,
    freeze_commit_sha: object,
    evidence_commit_sha: object,
) -> tuple[str, ...]:
    """Resolve predeclared policy and derive gate observations from canonical evidence."""

    errors: list[str] = []
    task_id = instance.get("governing_task_id")
    level = instance.get("fidelity_level")
    campaign_id = instance.get("campaign_id")
    experiment_id = instance.get("experiment_id")
    evaluation_id = instance.get("frozen_evaluation_identity")
    policy_identity = instance.get("promotion_policy_identity")
    digest = _b026_sha256_identity(policy_identity)
    if not isinstance(task_id, str) or digest is None:
        return ("$.promotion_policy_identity: CAMPAIGN_RESULT must bind a predeclared policy",)

    policy_path = (
        Path("artifacts")
        / "results"
        / "research"
        / task_id
        / "promotion-policies"
        / f"{digest}.json"
    )
    loaded = _b026_repository_json(
        repository_root,
        policy_path,
        canonical_commit_sha=freeze_commit_sha,
    )
    if loaded is None:
        return ("$.promotion_policy_identity: policy missing from canonical campaign-freeze commit",)
    policy, observed_sha = loaded
    if observed_sha != digest:
        errors.append("$.promotion_policy_identity: policy content address mismatch")

    expected_policy_keys = {
        "schema_version",
        "governing_task_id",
        "campaign_id",
        "fidelity_level",
        "frozen_evaluation_identity",
        "criteria",
    }
    if set(policy) != expected_policy_keys:
        errors.append("$.promotion_policy_identity: policy record fields are not canonical")
    if policy.get("schema_version") != "mstr.research-promotion-policy.v0":
        errors.append("$.promotion_policy_identity: unsupported policy schema_version")
    for field, expected_policy_value in (
        ("governing_task_id", task_id),
        ("campaign_id", campaign_id),
        ("fidelity_level", level),
        ("frozen_evaluation_identity", evaluation_id),
    ):
        if policy.get(field) != expected_policy_value:
            errors.append(f"$.promotion_policy_identity: policy {field} must match experiment")

    criteria_raw = policy.get("criteria")
    criteria: dict[str, dict[str, Any]] = {}
    if not isinstance(criteria_raw, list):
        errors.append("$.promotion_policy_identity: policy criteria must be an array")
    else:
        for criterion in criteria_raw:
            if not isinstance(criterion, dict) or set(criterion) != {
                "gate_id",
                "operator",
                "expected_value",
            }:
                errors.append("$.promotion_policy_identity: malformed policy criterion")
                continue
            gate_id = criterion.get("gate_id")
            if not isinstance(gate_id, str) or gate_id in criteria:
                errors.append("$.promotion_policy_identity: duplicate or invalid policy gate_id")
                continue
            if criterion.get("operator") not in {
                "EQ",
                "GTE",
                "LTE",
                "NOT_APPLICABLE",
                "EQ_PROMOTED_ARTIFACT",
            }:
                errors.append("$.promotion_policy_identity: unsupported policy operator")
                continue
            criteria[gate_id] = criterion

    if isinstance(level, str) and level in _B026_REQUIRED_GATE_IDS:
        required = _B026_REQUIRED_GATE_IDS[level]
        if set(criteria) != set(required) or len(criteria) != len(required):
            errors.append(
                "$.promotion_policy_identity: policy must exactly cover required gate ids"
            )

    gates = instance.get("hard_gate_results")
    if not isinstance(gates, list):
        return tuple(sorted(errors))
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            continue
        gate_id = gate.get("gate_id")
        criterion = criteria.get(gate_id) if isinstance(gate_id, str) else None
        if criterion is None:
            errors.append(f"$.hard_gate_results[{index}]: no predeclared criterion for gate")
            continue
        evidence_identity = gate.get("evidence_identity")
        evidence_digest = _b026_sha256_identity(evidence_identity)
        if evidence_digest is None:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: must be sha256 content address"
            )
            continue
        evidence_path = (
            Path("artifacts")
            / "results"
            / "research"
            / task_id
            / "gate-evidence"
            / f"{evidence_digest}.json"
        )
        loaded_evidence = _b026_repository_json(
            repository_root,
            evidence_path,
            canonical_commit_sha=evidence_commit_sha,
        )
        if loaded_evidence is None:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: canonical evidence missing"
            )
            continue
        evidence_record, evidence_sha = loaded_evidence
        if evidence_sha != evidence_digest:
            errors.append(
                f"$.hard_gate_results[{index}].evidence_identity: evidence content address mismatch"
            )
        expected_evidence_keys = {
            "schema_version",
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "frozen_evaluation_identity",
            "campaign_freeze_commit_sha",
            "source_evidence_identity",
            "source_json_pointer",
        }
        if set(evidence_record) != expected_evidence_keys:
            errors.append(f"$.hard_gate_results[{index}]: gate evidence fields are not canonical")
        if evidence_record.get("schema_version") != "mstr.research-gate-evidence.v1":
            errors.append(f"$.hard_gate_results[{index}]: unsupported gate evidence schema_version")
        for field, expected_evidence_value in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
            ("frozen_evaluation_identity", evaluation_id),
            ("campaign_freeze_commit_sha", freeze_commit_sha),
        ):
            if evidence_record.get(field) != expected_evidence_value:
                errors.append(
                    f"$.hard_gate_results[{index}]: gate evidence {field} must match experiment"
                )

        source_digest = _b026_sha256_identity(evidence_record.get("source_evidence_identity"))
        if source_digest is None:
            errors.append(f"$.hard_gate_results[{index}]: source evidence identity is invalid")
            continue
        source_path = (
            Path("artifacts")
            / "results"
            / "research"
            / task_id
            / "verifier-evidence"
            / f"{source_digest}.json"
        )
        loaded_source = _b026_repository_json(
            repository_root,
            source_path,
            canonical_commit_sha=evidence_commit_sha,
        )
        if loaded_source is None:
            errors.append(f"$.hard_gate_results[{index}]: underlying verifier evidence missing")
            continue
        source_record, source_sha = loaded_source
        if source_sha != source_digest:
            errors.append(f"$.hard_gate_results[{index}]: verifier evidence content address mismatch")
        expected_source_keys = {
            "schema_version",
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "frozen_evaluation_identity",
            "verifier_manifest_id",
            "verifier_health_identity",
            "subject_identity",
            "observed_value",
        }
        if set(source_record) != expected_source_keys:
            errors.append(f"$.hard_gate_results[{index}]: verifier evidence fields are not canonical")
        if source_record.get("schema_version") != "mstr.research-verifier-evidence.v0":
            errors.append(f"$.hard_gate_results[{index}]: unsupported verifier evidence schema_version")
        for field, expected_source_value in (
            ("governing_task_id", task_id),
            ("campaign_id", campaign_id),
            ("experiment_id", experiment_id),
            ("gate_id", gate_id),
            ("frozen_evaluation_identity", evaluation_id),
        ):
            if source_record.get(field) != expected_source_value:
                errors.append(
                    f"$.hard_gate_results[{index}]: verifier evidence {field} must match experiment"
                )
        for field in ("verifier_manifest_id", "verifier_health_identity", "subject_identity"):
            value = source_record.get(field)
            if _is_ambiguous_identity(value) or value in {None, "N/A"}:
                errors.append(f"$.hard_gate_results[{index}]: verifier evidence {field} must be concrete")
        if evidence_record.get("source_json_pointer") != "/observed_value":
            errors.append(f"$.hard_gate_results[{index}]: unsupported source_json_pointer")
            continue

        observed_value = source_record.get("observed_value")
        operator = criterion.get("operator")
        computed: str | None
        if operator == "EQ_PROMOTED_ARTIFACT":
            promoted_id = instance.get("promoted_result_id_or_na")
            material_results = instance.get("material_results")
            promoted_artifact: Any = None
            if isinstance(promoted_id, str) and isinstance(material_results, list):
                for result in material_results:
                    if isinstance(result, dict) and result.get("result_id") == promoted_id:
                        promoted_artifact = result.get("model_artifact_sha256_or_na")
                        break
            computed = (
                "PASS"
                if isinstance(promoted_artifact, str)
                and promoted_artifact != "N/A"
                and observed_value == promoted_artifact
                else "FAIL"
            )
        else:
            computed = _b026_compare_gate_value(
                operator,
                observed_value,
                criterion.get("expected_value"),
            )
        if computed is None:
            errors.append(f"$.hard_gate_results[{index}]: policy criterion cannot be evaluated")
        elif gate.get("status") != computed:
            errors.append(
                f"$.hard_gate_results[{index}].status: submitted status does not match "
                "predeclared criterion"
            )
    return tuple(sorted(errors))
'''
text = replace_regex(
    text,
    r"def _b026_promotion_policy_errors\(.*?(?=\n\ndef _research_experiment_semantic_errors)",
    new_policy_function.rstrip(),
    "promotion policy semantic function",
)

entry_old = '''    level = instance.get("fidelity_level")
    governing_task_id = instance.get("governing_task_id")
    predecessor = instance.get("predecessor_promotion")
    promotion_decision = instance.get("promotion_decision")
'''
entry_new = '''    level = instance.get("fidelity_level")
    governing_task_id = instance.get("governing_task_id")
    predecessor = instance.get("predecessor_promotion")
    promotion_decision = instance.get("promotion_decision")
    record_mode = instance.get("record_mode")
    freeze_commit_sha = instance.get("campaign_freeze_commit_sha_or_na")
    evidence_commit_sha = instance.get("canonical_evidence_commit_sha_or_na")

    if record_mode == "CONTRACT_FIXTURE":
        if governing_task_id != "B026":
            errors.append("$.record_mode: CONTRACT_FIXTURE is reserved for B026 contract proof")
        if promotion_decision == "PROMOTE":
            errors.append("$.promotion_decision: CONTRACT_FIXTURE cannot claim PROMOTE")
        for field in (
            "campaign_freeze_commit_sha_or_na",
            "canonical_evidence_commit_sha_or_na",
            "promotion_policy_identity",
            "q4_promotion_record_identity_or_na",
            "q4_candidate_binding_identity_or_na",
        ):
            if instance.get(field) != "N/A":
                errors.append(f"$.{field}: CONTRACT_FIXTURE requires literal N/A")
    elif record_mode == "CAMPAIGN_RESULT":
        if not _b026_strictly_precedes(repository_root, freeze_commit_sha, evidence_commit_sha):
            errors.append(
                "$.campaign_freeze_commit_sha_or_na: campaign freeze must be a strict "
                "canonical-main ancestor of the evidence commit"
            )
'''
text = replace_once(text, entry_old, entry_new, "research semantic entry")

text = replace_once(
    text,
    "                    loaded = _b026_repository_json(repository_root, relative)\n",
    "                    loaded = _b026_repository_json(\n                        repository_root,\n                        relative,\n                        canonical_commit_sha=freeze_commit_sha,\n                    )\n",
    "predecessor canonical load",
)

text = replace_once(
    text,
    "    errors.extend(_b026_promotion_policy_errors(instance, repository_root=repository_root))\n",
    '''    if record_mode == "CAMPAIGN_RESULT":
        errors.extend(
            _b026_promotion_policy_errors(
                instance,
                repository_root=repository_root,
                freeze_commit_sha=freeze_commit_sha,
                evidence_commit_sha=evidence_commit_sha,
            )
        )
''',
    "policy call",
)

l4_block = r'''        if level == "L4_Q4_UNIVERSAL_LAPTOP":
            ram = promoted_result.get("total_ram_bytes_or_na")
            threads = promoted_result.get("thread_count_or_na")
            context = promoted_result.get("context_length_or_na")
            artifact_size = promoted_result.get("model_artifact_size_bytes_or_na")
            backend = promoted_result.get("acceleration_backend_or_na")
            execution_count = promoted_result.get("model_execution_count_or_na")
            if isinstance(ram, bool) or not isinstance(ram, int) or ram <= 0 or ram > 8 * 1024**3:
                errors.append(
                    f"$.material_results[{promoted_result_id}].total_ram_bytes_or_na: "
                    "L4 requires evidence at or below the 8 GB reference RAM envelope"
                )
            if isinstance(threads, bool) or not isinstance(threads, int) or threads <= 0:
                errors.append(
                    f"$.material_results[{promoted_result_id}].thread_count_or_na: "
                    "L4 requires a positive thread count"
                )
            if context != 8192:
                errors.append(
                    f"$.material_results[{promoted_result_id}].context_length_or_na: "
                    "L4 requires the 8K reference context"
                )
            if backend != "CPU":
                errors.append(
                    f"$.material_results[{promoted_result_id}].acceleration_backend_or_na: "
                    "L4 requires CPU-only execution evidence"
                )
            if (
                isinstance(artifact_size, bool)
                or not isinstance(artifact_size, int)
                or artifact_size <= 0
                or artifact_size > 3 * 1024**3
            ):
                errors.append(
                    f"$.material_results[{promoted_result_id}].model_artifact_size_bytes_or_na: "
                    "L4 requires a positive Q4 artifact size at or below 3 GB"
                )
            if (
                isinstance(execution_count, bool)
                or not isinstance(execution_count, int)
                or execution_count <= 0
            ):
                errors.append(
                    f"$.material_results[{promoted_result_id}].model_execution_count_or_na: "
                    "L4 requires positive model-execution evidence"
                )

            q4_record_identity = instance.get("q4_promotion_record_identity_or_na")
            q4_digest = _b026_sha256_identity(q4_record_identity)
            artifact_sha = promoted_result.get("model_artifact_sha256_or_na")
            resolved_q4_record: dict[str, Any] | None = None
            if q4_digest is None:
                errors.append(
                    "$.q4_promotion_record_identity_or_na: L4 PROMOTE requires a "
                    "sha256-bound Q4 record"
                )
            else:
                q4_path = (
                    Path("artifacts")
                    / "results"
                    / "q4-promotion"
                    / "registry"
                    / f"{q4_digest}.json"
                )
                loaded_q4 = _b026_repository_json(
                    repository_root,
                    q4_path,
                    canonical_commit_sha=evidence_commit_sha,
                )
                if loaded_q4 is None:
                    errors.append(
                        "$.q4_promotion_record_identity_or_na: immutable Q4 promotion "
                        "record missing from canonical evidence commit"
                    )
                else:
                    q4_record, observed_q4_sha = loaded_q4
                    resolved_q4_record = q4_record
                    if observed_q4_sha != q4_digest:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record content address "
                            "mismatch"
                        )
                    q4_errors = validation_errors(
                        "mstr-q4-promotion-v0",
                        q4_record,
                        schema_dir=schema_dir,
                        repository_root=repository_root,
                    )
                    if q4_errors:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 promotion record "
                            "is invalid"
                        )
                    if q4_record.get("promotion_status") != "PROMOTED":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: referenced Q4 record must be "
                            "PROMOTED"
                        )
                    if q4_record.get("canonical_q4_artifact_sha256") != artifact_sha:
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: Q4 record artifact must match "
                            "promoted result"
                        )
                    if q4_record.get("universal_laptop_gate_result") != "PASS":
                        errors.append(
                            "$.q4_promotion_record_identity_or_na: L4 requires universal-laptop "
                            "gate PASS"
                        )
                    laptop_gate = gate_by_id.get("universal_laptop_product_gates")
                    if isinstance(laptop_gate, dict) and q4_record.get(
                        "universal_laptop_gate_evidence_identity"
                    ) != laptop_gate.get("evidence_identity"):
                        errors.append(
                            "$.hard_gate_results[universal_laptop_product_gates].evidence_identity: "
                            "must match resolved Q4 universal-laptop evidence"
                        )
                    promotion_gate = gate_by_id.get("q4_promotion_record_promoted")
                    if isinstance(promotion_gate, dict) and q4_record.get(
                        "promotion_decision_evidence_identity"
                    ) != promotion_gate.get("evidence_identity"):
                        errors.append(
                            "$.hard_gate_results[q4_promotion_record_promoted].evidence_identity: "
                            "must match resolved Q4 promotion-decision evidence"
                        )

            binding_identity = instance.get("q4_candidate_binding_identity_or_na")
            binding_digest = _b026_sha256_identity(binding_identity)
            if binding_digest is None:
                errors.append(
                    "$.q4_candidate_binding_identity_or_na: L4 PROMOTE requires a "
                    "content-addressed candidate/Q4 lineage binding"
                )
            elif not isinstance(governing_task_id, str):
                errors.append("$.governing_task_id: required to resolve Q4 candidate binding")
            else:
                binding_path = (
                    Path("artifacts")
                    / "results"
                    / "research"
                    / governing_task_id
                    / "q4-bindings"
                    / f"{binding_digest}.json"
                )
                loaded_binding = _b026_repository_json(
                    repository_root,
                    binding_path,
                    canonical_commit_sha=evidence_commit_sha,
                )
                if loaded_binding is None:
                    errors.append(
                        "$.q4_candidate_binding_identity_or_na: canonical Q4 candidate binding missing"
                    )
                else:
                    binding, binding_sha = loaded_binding
                    if binding_sha != binding_digest:
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: binding content address mismatch"
                        )
                    expected_binding_keys = {
                        "schema_version",
                        "q4_promotion_record_identity",
                        "model_id",
                        "model_revision",
                        "source_checkpoint_sha256",
                        "canonical_q4_artifact_sha256",
                    }
                    if set(binding) != expected_binding_keys:
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: binding fields are not canonical"
                        )
                    if binding.get("schema_version") != "mstr.research-q4-candidate-binding.v0":
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: unsupported binding schema_version"
                        )
                    if binding.get("q4_promotion_record_identity") != q4_record_identity:
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: binding must reference resolved Q4 record"
                        )
                    if binding.get("model_id") != promoted_result.get("model_id_or_na"):
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: model_id must match promoted result"
                        )
                    if binding.get("model_revision") != promoted_result.get("model_revision_or_na"):
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: model_revision must match promoted result"
                        )
                    if isinstance(resolved_q4_record, dict) and binding.get(
                        "source_checkpoint_sha256"
                    ) != resolved_q4_record.get("source_checkpoint_sha256"):
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: source checkpoint must match Q4 record"
                        )
                    if binding.get("canonical_q4_artifact_sha256") != artifact_sha:
                        errors.append(
                            "$.q4_candidate_binding_identity_or_na: artifact must match promoted result"
                        )
'''
text = replace_regex(
    text,
    r'        if level == "L4_Q4_UNIVERSAL_LAPTOP":.*?(?=\n    if \(\n        not \()',
    l4_block.rstrip(),
    "L4 semantic block",
)

text = replace_once(
    text,
    '''    if (
        not (
            promotion_decision == "PROMOTE"
            and level == "L4_Q4_UNIVERSAL_LAPTOP"
            and promoted_result is not None
        )
        and instance.get("q4_promotion_record_identity_or_na") != "N/A"
    ):
        errors.append(
            "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"
        )
''',
    '''    if not (
        promotion_decision == "PROMOTE"
        and level == "L4_Q4_UNIVERSAL_LAPTOP"
        and promoted_result is not None
    ):
        if instance.get("q4_promotion_record_identity_or_na") != "N/A":
            errors.append(
                "$.q4_promotion_record_identity_or_na: only L4 PROMOTE may bind Q4 promotion evidence"
            )
        if instance.get("q4_candidate_binding_identity_or_na") != "N/A":
            errors.append(
                "$.q4_candidate_binding_identity_or_na: only L4 PROMOTE may bind Q4 candidate lineage"
            )
''',
    "non-L4 Q4 restrictions",
)

new_effect_inference = r'''    declared_effects = _b026_true_effects(instance)
    model_execution_total = 0
    network_model_call_total = 0
    if isinstance(material_results, list):
        for result in material_results:
            if not isinstance(result, dict):
                continue
            if (
                result.get("evidence_kind") == "TRAINING_EVIDENCE"
                and "WEIGHT_CHANGING_TRAINING" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.WEIGHT_CHANGING_TRAINING: "
                    "TRAINING_EVIDENCE requires explicit true declaration"
                )
            resource_cost = result.get("resource_cost")
            if isinstance(resource_cost, dict) and (
                resource_cost.get("cost_class") == "AUTHORIZED_REMOTE_COMPUTE"
                and "RENTED_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.RENTED_COMPUTE: "
                    "AUTHORIZED_REMOTE_COMPUTE requires explicit true declaration"
                )
            paid = result.get("paid_cost_usd")
            if (
                isinstance(paid, (int, float))
                and not isinstance(paid, bool)
                and paid > 0
                and "PAID_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.PAID_COMPUTE: positive paid cost requires "
                    "explicit true declaration"
                )
            model_executions = result.get("model_execution_count_or_na")
            if isinstance(model_executions, int) and not isinstance(model_executions, bool):
                model_execution_total += model_executions
                if model_executions > 0 and "MODEL_EXECUTION" not in declared_effects:
                    errors.append(
                        "$.governed_effects.MODEL_EXECUTION: positive model execution count "
                        "requires explicit true declaration"
                    )
            network_calls = result.get("network_model_or_teacher_call_count_or_na")
            if isinstance(network_calls, int) and not isinstance(network_calls, bool):
                network_model_call_total += network_calls
                if network_calls > 0 and "NETWORK_MODEL_OR_TEACHER_CALL" not in declared_effects:
                    errors.append(
                        "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: positive network model/teacher "
                        "call count requires explicit true declaration"
                    )
    if "MODEL_EXECUTION" in declared_effects and model_execution_total <= 0:
        errors.append(
            "$.governed_effects.MODEL_EXECUTION: true declaration requires positive execution evidence"
        )
    if "NETWORK_MODEL_OR_TEACHER_CALL" in declared_effects and network_model_call_total <= 0:
        errors.append(
            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration requires positive call evidence"
        )
    if (
        "PAID_MODEL_API_EXECUTION" in declared_effects
        and "NETWORK_MODEL_OR_TEACHER_CALL" not in declared_effects
    ):
        errors.append(
            "$.governed_effects.PAID_MODEL_API_EXECUTION: paid model API execution also requires "
            "NETWORK_MODEL_OR_TEACHER_CALL=true"
        )
'''
text = replace_regex(
    text,
    r"    declared_effects = _b026_true_effects\(instance\).*?(?=\n    external_resource_class = bool\()",
    new_effect_inference.rstrip(),
    "governed-effect inference",
)

# The separately granted authority and predecessor must already exist at freeze time.
text = replace_once(
    text,
    "                loaded = _b026_repository_json(repository_root, relative)\n",
    "                loaded = _b026_repository_json(\n                    repository_root,\n                    relative,\n                    canonical_commit_sha=freeze_commit_sha,\n                )\n",
    "authority canonical load",
)

py_path.write_text(text, encoding="utf-8")

# ---------------------------------------------------------------------------
# Test helpers and regressions
# ---------------------------------------------------------------------------
test_path = ROOT / "tests/contract/test_research_ladder_contract.py"
tests = test_path.read_text(encoding="utf-8")
tests = replace_once(tests, "import json\n", "import json\nimport subprocess\n", "test subprocess import")

new_helpers = r'''def _write_content_addressed(path: Path, value: dict[str, object]) -> str:
    path.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    (path / f"{digest}.json").write_bytes(raw)
    return f"sha256:{digest}"


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    )
    return completed.stdout.strip()


def _ensure_git_repo(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
        _git(root, "config", "user.name", "MSTR Contract Test")
        _git(root, "config", "user.email", "mstr-contract@example.invalid")


def _commit_all(root: Path, message: str) -> str:
    _ensure_git_repo(root)
    _git(root, "add", "-A")
    if not _git(root, "status", "--porcelain"):
        raise AssertionError(f"expected changes before commit: {message}")
    _git(root, "commit", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def _write_authority(
    root: Path,
    *,
    authority_id: str,
    task_id: str,
    campaign_id: str,
    effects: list[str],
    max_paid: float = 2.0,
    max_wall: float = 60.0,
    max_results: int = 4,
) -> str:
    record: dict[str, object] = {
        "authority_id": authority_id,
        "task_id": task_id,
        "external_effect_class": effects[-1],
        "status": "AUTHORIZED_CANONICAL",
        "scope": {
            "campaign_id": campaign_id,
            "research_ladder_id": "mstr-research-ladder-v0",
            "research_effects": effects,
        },
        "cost_resource_ceiling": {
            "cost_model": "fixed-cap",
            "limits": [
                {"resource": "paid_cost_usd", "max": max_paid, "unit": "USD"},
                {"resource": "wall_time_seconds", "max": max_wall, "unit": "seconds"},
                {"resource": "material_results", "max": max_results, "unit": "count"},
            ],
        },
    }
    return _write_json_with_sha(
        root / "artifacts" / "authorities" / f"{authority_id}.json",
        record,
    )


def _prepare_policy_and_gate_evidence(root: Path, record: dict[str, object]) -> None:
    _ensure_git_repo(root)
    record["record_mode"] = "CAMPAIGN_RESULT"
    record["promotion_decision"] = "PROMOTE"
    record["decision_reason"] = "Synthetic contract test campaign satisfies all required gates."
    task_id = str(record["governing_task_id"])
    campaign_id = str(record["campaign_id"])
    experiment_id = str(record["experiment_id"])
    level = str(record["fidelity_level"])
    effects = record["governed_effects"]
    assert isinstance(effects, dict)

    enabled_effects = [name for name, enabled in effects.items() if enabled is True]
    if enabled_effects and record.get("external_effect_authority") is None:
        authority_id = f"AUTH-{task_id}-{experiment_id}"
        authority_sha = _write_authority(
            root,
            authority_id=authority_id,
            task_id=task_id,
            campaign_id=campaign_id,
            effects=enabled_effects,
            max_paid=100.0,
            max_wall=3600.0,
            max_results=100,
        )
        record["external_effect_authority"] = {
            "authority_id": authority_id,
            "authority_record_sha256": authority_sha,
        }

    policy = {
        "schema_version": "mstr.research-promotion-policy.v0",
        "governing_task_id": task_id,
        "campaign_id": campaign_id,
        "fidelity_level": level,
        "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
        "criteria": [
            (
                {
                    "gate_id": gate_id,
                    "operator": "EQ_PROMOTED_ARTIFACT",
                    "expected_value": "PROMOTED_RESULT_ARTIFACT",
                }
                if gate_id == "q4_artifact_identity"
                else {"gate_id": gate_id, "operator": "EQ", "expected_value": True}
            )
            for gate_id in _required_gate_ids(level)
        ],
    }
    record["promotion_policy_identity"] = _write_content_addressed(
        root / "artifacts/results/research" / task_id / "promotion-policies",
        policy,
    )
    freeze_sha = _commit_all(root, f"freeze {experiment_id}")
    record["campaign_freeze_commit_sha_or_na"] = freeze_sha

    gates = record["hard_gate_results"]
    assert isinstance(gates, list)
    for gate in gates:
        assert isinstance(gate, dict)
        gate_id = str(gate["gate_id"])
        observed_value: object = True
        if gate_id == "q4_artifact_identity":
            results = record["material_results"]
            promoted_id = record["promoted_result_id_or_na"]
            assert isinstance(results, list)
            promoted = next(
                result
                for result in results
                if isinstance(result, dict) and result.get("result_id") == promoted_id
            )
            observed_value = promoted["model_artifact_sha256_or_na"]
        source = {
            "schema_version": "mstr.research-verifier-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            "verifier_manifest_id": "fixture-verifier-manifest",
            "verifier_health_identity": "fixture-verifier-health",
            "subject_identity": str(record["promoted_result_id_or_na"]),
            "observed_value": observed_value,
        }
        source_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-evidence",
            source,
        )
        evidence = {
            "schema_version": "mstr.research-gate-evidence.v1",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            "campaign_freeze_commit_sha": freeze_sha,
            "source_evidence_identity": source_identity,
            "source_json_pointer": "/observed_value",
        }
        gate["evidence_identity"] = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "gate-evidence",
            evidence,
        )

    record["q4_promotion_record_identity_or_na"] = "N/A"
    record["q4_candidate_binding_identity_or_na"] = "N/A"
    if level == "L4_Q4_UNIVERSAL_LAPTOP":
        results = record["material_results"]
        assert isinstance(results, list) and isinstance(results[0], dict)
        result = results[0]
        gate_map = {str(gate["gate_id"]): gate for gate in gates if isinstance(gate, dict)}
        q4_record: dict[str, object] = {
            "schema_version": "mstr.q4-promotion.v0",
            "source_training_run_id": "fixture-training-run",
            "source_checkpoint_sha256": "b" * 64,
            "merged_master_sha256": "c" * 64,
            "export_tool_id": "fixture-export",
            "export_tool_revision": "fixture-export-revision",
            "export_recipe_hash": "d" * 64,
            "quantizer_tool_id": "fixture-quantizer",
            "quantizer_tool_revision": "fixture-quantizer-revision",
            "quantization_recipe_hash": "e" * 64,
            "canonical_q4_artifact_sha256": str(result["model_artifact_sha256_or_na"]),
            "artifact_integrity_status": "PASS",
            "q4_regression_manifest_id": "fixture-q4-regression",
            "q4_regression_result": "PASS",
            "universal_laptop_gate_result": "PASS",
            "universal_laptop_gate_evidence_identity": str(
                gate_map["universal_laptop_product_gates"]["evidence_identity"]
            ),
            "universal_laptop_gate_not_required_reason": None,
            "promotion_status": "PROMOTED",
            "rejection_reasons": [],
            "promotion_decision_evidence_identity": str(
                gate_map["q4_promotion_record_promoted"]["evidence_identity"]
            ),
        }
        q4_identity = _write_content_addressed(
            root / "artifacts/results/q4-promotion/registry",
            q4_record,
        )
        record["q4_promotion_record_identity_or_na"] = q4_identity
        binding = {
            "schema_version": "mstr.research-q4-candidate-binding.v0",
            "q4_promotion_record_identity": q4_identity,
            "model_id": str(result["model_id_or_na"]),
            "model_revision": str(result["model_revision_or_na"]),
            "source_checkpoint_sha256": str(q4_record["source_checkpoint_sha256"]),
            "canonical_q4_artifact_sha256": str(result["model_artifact_sha256_or_na"]),
        }
        record["q4_candidate_binding_identity_or_na"] = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "q4-bindings",
            binding,
        )

    evidence_sha = _commit_all(root, f"evidence {experiment_id}")
    record["canonical_evidence_commit_sha_or_na"] = evidence_sha


def _registry_path(root: Path, task_id: str, experiment_id: str) -> Path:
    return (
        root / "artifacts" / "results" / "research" / task_id / "registry" / f"{experiment_id}.json"
    )


def _make_level_record(
    level_index: int,
    *,
    task_id: str,
    campaign_id: str,
    predecessor_id: str | None = None,
    predecessor_sha: str | None = None,
    predecessor_result: str | None = None,
) -> dict[str, object]:
    fixture = _valid_research_experiment()
    level = LEVELS[level_index]
    fixture["record_mode"] = "CAMPAIGN_RESULT"
    fixture["experiment_id"] = f"fixture-l{level_index}"
    fixture["governing_task_id"] = task_id
    fixture["campaign_id"] = campaign_id
    fixture["fidelity_level"] = level
    fixture["promotion_decision"] = "PROMOTE"
    fixture["decision_reason"] = "Synthetic campaign result promoted for contract testing."
    fixture["campaign_freeze_commit_sha_or_na"] = "N/A"
    fixture["canonical_evidence_commit_sha_or_na"] = "N/A"
    fixture["promotion_policy_identity"] = "N/A"
    fixture["q4_candidate_binding_identity_or_na"] = "N/A"
    fixture["governed_effects"] = _governed_effects()
    fixture["external_effect_authority"] = None
    results = fixture["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]
    result_id = f"result-l{level_index}"
    result["result_id"] = result_id
    result["model_execution_count_or_na"] = 0
    result["network_model_or_teacher_call_count_or_na"] = 0
    result["model_artifact_size_bytes_or_na"] = "N/A"
    fixture["promoted_result_id_or_na"] = result_id
    fixture["q4_promotion_record_identity_or_na"] = "N/A"
    _set_required_gates(fixture, level)

    if level_index == 0:
        fixture["predecessor_promotion"] = None
        fixture["parent_identity"] = "fixture-parent:N/A"
    else:
        assert predecessor_id is not None
        assert predecessor_sha is not None
        assert predecessor_result is not None
        fixture["predecessor_promotion"] = {
            "experiment_id": predecessor_id,
            "experiment_record_sha256": predecessor_sha,
        }
        fixture["parent_identity"] = predecessor_result

    if level == "L1_CODE_PROXY":
        result["sampling_config_id_or_na"] = "sampling:fixture-v1"
    elif level == "L2_EXECUTABLE_REPO":
        result["cpu_identity_or_na"] = "cpu:fixture"
        result["verifier_health_id_or_na"] = "verifier-health:fixture"
    elif level == "L3_DIRECTION_TO_DONE":
        result["interaction_contract_version_or_na"] = "interaction:fixture-v1"
        result["loop_contract_version_or_na"] = "loop:fixture-v1"
        result["harness_profile_id_or_na"] = "harness:fixture-v1"
        result["verifier_health_id_or_na"] = "verifier-health:fixture"
    elif level == "L4_Q4_UNIVERSAL_LAPTOP":
        effects = fixture["governed_effects"]
        assert isinstance(effects, dict)
        effects["MODEL_EXECUTION"] = True
        result.update(
            {
                "model_id_or_na": "fixture/model",
                "model_revision_or_na": "revision-1",
                "model_artifact_sha256_or_na": "a" * 64,
                "model_artifact_size_bytes_or_na": 2 * 1024**3,
                "model_execution_count_or_na": 1,
                "network_model_or_teacher_call_count_or_na": 0,
                "tokenizer_id_or_na": "fixture/tokenizer",
                "tokenizer_revision_or_na": "tokenizer-revision-1",
                "quantization_method_or_na": "Q4_K_M",
                "quantizer_tool_revision_or_na": "llama.cpp:fixture-revision",
                "runtime_id_or_na": "llama.cpp",
                "runtime_version_or_commit_or_na": "runtime-revision-1",
                "runtime_build_flags_or_na": "CPU_ONLY=1",
                "os_identity_or_na": "macOS-fixture",
                "cpu_identity_or_na": "cpu:universal-laptop-fixture",
                "total_ram_bytes_or_na": 8 * 1024**3,
                "thread_count_or_na": 8,
                "acceleration_backend_or_na": "CPU",
                "context_length_or_na": 8192,
                "cache_state_or_na": "cold",
            }
        )
    return fixture


def _write_promoted_chain(
    root: Path, through_index: int
) -> tuple[list[dict[str, object]], list[str]]:
    _ensure_git_repo(root)
    task_id = "B027"
    campaign_id = "campaign-registry-fixture"
    records: list[dict[str, object]] = []
    shas: list[str] = []
    for index in range(through_index + 1):
        predecessor = records[index - 1] if index else None
        record = _make_level_record(
            index,
            task_id=task_id,
            campaign_id=campaign_id,
            predecessor_id=str(predecessor["experiment_id"]) if predecessor else None,
            predecessor_sha=shas[index - 1] if predecessor else None,
            predecessor_result=str(predecessor["promoted_result_id_or_na"])
            if predecessor
            else None,
        )
        _prepare_policy_and_gate_evidence(root, record)
        validate_instance("mstr-research-experiment-v2", record, repository_root=root)
        sha = _write_json_with_sha(
            _registry_path(root, task_id, str(record["experiment_id"])),
            record,
        )
        records.append(record)
        shas.append(sha)
    return records, shas
'''
tests = replace_regex(
    tests,
    r"def _write_content_addressed\(.*?(?=\n\n@pytest\.mark\.parametrize)",
    new_helpers.rstrip(),
    "research test helper region",
)

old_promotion_test = r'''def test_research_experiment_promotion_requires_all_hard_gates_pass() -> None:
    fixture = _json(FIXTURES / "valid" / "mstr-research-experiment-v2.json")
    validate_instance("mstr-research-experiment-v2", fixture)
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list)
    assert isinstance(gates[0], dict)
    gates[0]["status"] = "FAIL"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture)
'''
new_promotion_test = r'''def test_research_experiment_promotion_requires_all_hard_gates_pass(tmp_path: Path) -> None:
    fixture = _make_level_record(0, task_id="B027", campaign_id="gate-status-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
    gates = fixture["hard_gate_results"]
    assert isinstance(gates, list)
    assert isinstance(gates[0], dict)
    gates[0]["status"] = "FAIL"
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
'''
tests = replace_once(tests, old_promotion_test, new_promotion_test, "promotion PASS test")

# Ensure custom-schema predecessor test has canonical freeze/evidence for the current record.
tests = replace_once(
    tests,
    '''    current = _make_level_record(
        1,
        task_id="B027",
        campaign_id=str(predecessor["campaign_id"]),
        predecessor_id=str(predecessor["experiment_id"]),
        predecessor_sha=shas[0],
        predecessor_result=str(predecessor["promoted_result_id_or_na"]),
    )

    custom_dir = tmp_path / "custom-schemas"
''',
    '''    current = _make_level_record(
        1,
        task_id="B027",
        campaign_id=str(predecessor["campaign_id"]),
        predecessor_id=str(predecessor["experiment_id"]),
        predecessor_sha=shas[0],
        predecessor_result=str(predecessor["promoted_result_id_or_na"]),
    )
    _prepare_policy_and_gate_evidence(tmp_path, current)

    custom_dir = tmp_path / "custom-schemas"
''',
    "custom schema current preparation",
)

# Canonicalize the custom authority before checking its ceiling.
tests = replace_once(
    tests,
    '''    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)


def test_paid_result_cost_must_reconcile_to_aggregate() -> None:
''',
    '''    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)


def test_paid_result_cost_must_reconcile_to_aggregate() -> None:
''',
    "authority ceiling canonicalization",
)

# Replace the old self-declared observed-value regression with a verifier-evidence regression.
tests = replace_regex(
    tests,
    r"def test_promotion_status_is_computed_from_predeclared_policy_and_content_bound_evidence\(.*?(?=\n\ndef test_promotion_policy_missing_or_tampered_fails_closed)",
    r'''def test_promotion_status_is_computed_from_predeclared_policy_and_content_bound_evidence(
    tmp_path: Path,
) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="policy-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    gates = record["hard_gate_results"]
    assert isinstance(gates, list) and isinstance(gates[0], dict)
    gate = gates[0]
    gate_digest = str(gate["evidence_identity"]).removeprefix("sha256:")
    gate_path = tmp_path / "artifacts/results/research/B027/gate-evidence" / f"{gate_digest}.json"
    gate_evidence = _json(gate_path)
    source_digest = str(gate_evidence["source_evidence_identity"]).removeprefix("sha256:")
    source_path = (
        tmp_path / "artifacts/results/research/B027/verifier-evidence" / f"{source_digest}.json"
    )
    source = _json(source_path)
    source["observed_value"] = False
    replacement_source = _write_content_addressed(source_path.parent, source)
    gate_evidence["source_evidence_identity"] = replacement_source
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path, "tamper canonical verifier observation for rejection test"
    )
    with pytest.raises(ValueError, match="submitted status does not match predeclared criterion"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)
'''.rstrip(),
    "underlying verifier observation regression",
)

# When a Q4 artifact record is replaced, commit it before asking the canonical loader to resolve it.
tests = replace_once(
    tests,
    '''    q4["canonical_q4_artifact_sha256"] = "9" * 64
    l4["q4_promotion_record_identity_or_na"] = _write_content_addressed(q4_path.parent, q4)
    with pytest.raises(ValueError, match="Q4 record artifact must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
''',
    '''    q4["canonical_q4_artifact_sha256"] = "9" * 64
    l4["q4_promotion_record_identity_or_na"] = _write_content_addressed(q4_path.parent, q4)
    l4["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path, "replace Q4 artifact for mismatch test"
    )
    with pytest.raises(ValueError, match="Q4 record artifact must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
''',
    "Q4 mismatch canonical commit",
)

append_tests = r'''


def test_campaign_registry_rejects_worktree_only_records(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="history-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    digest = str(record["promotion_policy_identity"]).removeprefix("sha256:")
    policy_path = tmp_path / "artifacts/results/research/B027/promotion-policies" / f"{digest}.json"
    policy = _json(policy_path)
    policy["criteria"][0]["expected_value"] = False
    record["promotion_policy_identity"] = _write_content_addressed(policy_path.parent, policy)
    with pytest.raises(ValueError, match="policy missing from canonical campaign-freeze commit"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_campaign_policy_freeze_must_strictly_precede_evidence(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="ordering-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
    record["campaign_freeze_commit_sha_or_na"] = record["canonical_evidence_commit_sha_or_na"]
    with pytest.raises(ValueError, match="strict canonical-main ancestor"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_model_and_network_execution_require_explicit_governed_effects(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="effects-fixture")
    results = record["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    results[0]["model_execution_count_or_na"] = 1
    results[0]["network_model_or_teacher_call_count_or_na"] = 1
    _prepare_policy_and_gate_evidence(tmp_path, record)
    with pytest.raises(ValueError, match="MODEL_EXECUTION"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)

    effects = record["governed_effects"]
    assert isinstance(effects, dict)
    effects["MODEL_EXECUTION"] = True
    with pytest.raises(ValueError, match="NETWORK_MODEL_OR_TEACHER_CALL"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_l4_enforces_exact_universal_laptop_envelope(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    results = l4["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    result = results[0]

    mutations = (
        ("total_ram_bytes_or_na", 64 * 1024**3, "8 GB reference RAM"),
        ("thread_count_or_na", 0, "positive thread count"),
        ("context_length_or_na", 32768, "8K reference context"),
        ("acceleration_backend_or_na", "CUDA", "CPU-only execution"),
        ("model_artifact_size_bytes_or_na", 4 * 1024**3, "at or below 3 GB"),
    )
    for field, bad_value, message in mutations:
        original = result[field]
        result[field] = bad_value
        with pytest.raises(ValueError, match=message):
            validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
        result[field] = original


def test_l4_q4_candidate_binding_rejects_model_identity_relabel(tmp_path: Path) -> None:
    records, _ = _write_promoted_chain(tmp_path, 4)
    l4 = records[4]
    results = l4["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    results[0]["model_id_or_na"] = "different/model"
    with pytest.raises(ValueError, match="model_id must match promoted result"):
        validate_instance("mstr-research-experiment-v2", l4, repository_root=tmp_path)
'''
tests = tests.rstrip() + append_tests + "\n"
test_path.write_text(tests, encoding="utf-8")

# ---------------------------------------------------------------------------
# Canonical documentation and evidence
# ---------------------------------------------------------------------------
data_model_path = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
data_model = data_model_path.read_text(encoding="utf-8")
data_model = replace_once(
    data_model,
    "- model_artifact_sha256_or_na\n",
    "- model_artifact_sha256_or_na\n- model_artifact_size_bytes_or_na\n- model_execution_count_or_na\n- network_model_or_teacher_call_count_or_na\n",
    "material data model fields",
)
data_model = replace_once(
    data_model,
    "- fidelity_level\n- promotion_policy_identity\n",
    "- fidelity_level\n- record_mode\n- campaign_freeze_commit_sha_or_na\n- canonical_evidence_commit_sha_or_na\n- promotion_policy_identity\n",
    "research data model commit fields",
)
data_model = replace_once(
    data_model,
    "- q4_promotion_record_identity_or_na\n- governed_effects\n",
    "- q4_promotion_record_identity_or_na\n- q4_candidate_binding_identity_or_na\n- governed_effects\n",
    "research data model Q4 binding",
)
data_model += (
    "\n\n### B026 canonical-history hardening\n\n"
    "`CAMPAIGN_RESULT` records resolve policy, predecessor, authority, gate evidence, verifier evidence, "
    "Q4 promotion, and Q4 candidate binding from explicit Git commits in canonical `main` ancestry. "
    "`campaign_freeze_commit_sha_or_na` MUST be a strict ancestor of "
    "`canonical_evidence_commit_sha_or_na`; policy/predecessor/authority are resolved at freeze time, "
    "while gate/verifier/Q4 evidence is resolved at the later evidence commit. Dirty-worktree or "
    "feature-branch-only files are never canonical evidence. `CONTRACT_FIXTURE` exists only for B026 "
    "shape validation and cannot claim `PROMOTE`.\n\n"
    "Gate evidence does not carry a self-declared observed value. It content-addresses canonical verifier "
    "evidence, binds the frozen evaluator/verifier identity, and validation derives the observed value from "
    "that underlying record. L4 additionally enforces RAM <= 8 GiB, CPU execution, context = 8192, a "
    "positive thread count, Q4 artifact size <= 3 GiB, positive model-execution evidence, and an immutable "
    "candidate/Q4 binding that ties model id/revision and source checkpoint to the resolved Q4 record.\n"
)
data_model_path.write_text(data_model, encoding="utf-8")

readme_path = ROOT / "specs/002-code-model-supremacy-foundation/contracts/README.md"
readme = readme_path.read_text(encoding="utf-8")
readme += (
    "\n\n## B026 canonical history boundary\n\n"
    "Campaign-result validation is Git-history-bound. Policy, predecessor, and external authority must "
    "already exist at an explicit canonical campaign-freeze commit. Gate/verifier/Q4 evidence must exist "
    "at a later canonical evidence commit. Both commits must be in `main` ancestry and the freeze commit "
    "must strictly precede the evidence commit. Working-tree presence is never sufficient.\n"
)
readme_path.write_text(readme, encoding="utf-8")

evidence_path = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
evidence = evidence_path.read_text(encoding="utf-8").rstrip()
evidence += r'''

## Exact-head review repair — canonical history and causal evidence

Codex review `PRR_kwDOUCYTYs8AAAABL4fRHw` on exact historical head `ffd526fd686c84572a023490c4ab69a3255b8780` identified six P1 defects: working-tree registry trust, missing model/network execution effects, missing pre-execution policy antecedence, self-declared gate observations, incomplete L4 universal-laptop enforcement, and missing Q4-to-candidate lineage binding.

This repair is contract/configuration hardening only. `CAMPAIGN_RESULT` now requires explicit Git commits in canonical-main ancestry: policy/predecessor/authority resolve from a strict ancestor campaign-freeze commit, while gate/verifier/Q4 evidence resolves from the later canonical evidence commit. Gate evidence derives observations from separately content-addressed verifier evidence instead of accepting an `observed_value` field in the gate record. Model execution and network model/teacher calls are explicit governed effects. L4 enforces the 8 GiB / CPU / 8K / Q4 <= 3 GiB envelope and a content-addressed Q4 candidate/source-checkpoint binding. B026 contract fixtures are explicitly non-campaign and cannot claim promotion.

The repair does not grant or execute model inference, model-weight access, network model/teacher calls, paid APIs or compute, dataset ingestion, training, RL, or release. Fresh exact-head qualification and fresh independent review remain required after publication of the repaired candidate.
'''
evidence_path.write_text(evidence + "\n", encoding="utf-8")

# Keep the B026 authority boundary explicit and unchanged.
for marker in (
    "MODEL_WEIGHT_ACCESS = NONE",
    "MODEL_EXECUTION = NONE",
    "RESEARCH_CAMPAIGN_EXECUTION = NONE",
    "PAID_COMPUTE = NONE",
    "NETWORK_MODEL_OR_TEACHER_CALL = NONE",
    "LARGE_DATASET_INGESTION = NONE",
    "WEIGHT_CHANGING_TRAINING = NONE",
    "LARGE_SCALE_RL = NONE",
    "PRODUCTION_RELEASE = NONE",
):
    if marker not in evidence:
        raise RuntimeError(f"authority marker missing before repair: {marker}")

# Final deterministic schema-copy identity.
if (ROOT / research_schema_paths[0]).read_bytes() != (ROOT / research_schema_paths[1]).read_bytes():
    raise RuntimeError("research schema runtime/spec copies diverged")
if (ROOT / material_schema_paths[0]).read_bytes() != (ROOT / material_schema_paths[1]).read_bytes():
    raise RuntimeError("material schema runtime/spec copies diverged")
