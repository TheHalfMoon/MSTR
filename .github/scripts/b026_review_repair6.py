from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path.cwd()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one occurrence, found {count}")
    return text.replace(old, new, 1)


def replace_regex(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one replacement, found {count}")
    return updated


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected object")
    return value


def save_json(path: str, value: dict) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Semantic validator: bind verifier observations to underlying canonical
# content-addressed artifacts and treat positive network bytes as governed
# network evidence.
# ---------------------------------------------------------------------------
py_path = ROOT / "src/mstr_qualify/schemas.py"
text = py_path.read_text(encoding="utf-8")

helper_anchor = '''def _b026_compare_gate_value(operator: Any, observed: Any, expected: Any) -> str | None:
'''
helper = '''def _b026_research_artifact_path(
    task_id: object,
    registry: str,
    identity: object,
) -> tuple[Path, str] | None:
    """Derive one content-addressed B026 research-artifact path."""

    digest = _b026_sha256_identity(identity)
    if not isinstance(task_id, str) or not _b026_binding_id(task_id) or digest is None:
        return None
    return (
        Path("artifacts")
        / "results"
        / "research"
        / task_id
        / registry
        / f"{digest}.json",
        digest,
    )


'''
text = replace_once(text, helper_anchor, helper + helper_anchor, "research artifact helper")

old_source_pattern = r'''        expected_source_keys = \{.*?        observed_value = source_record\.get\("observed_value"\)'''
new_source_block = '''        expected_source_keys = {
            "schema_version",
            "governing_task_id",
            "campaign_id",
            "experiment_id",
            "gate_id",
            "frozen_evaluation_identity",
            "verifier_manifest_identity",
            "verifier_health_identity",
            "subject_identity",
            "subject_evidence_identity",
            "verifier_result_identity",
            "verifier_result_json_pointer",
        }
        if set(source_record) != expected_source_keys:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier evidence fields are not canonical"
            )
        if source_record.get("schema_version") != "mstr.research-verifier-evidence.v0":
            errors.append(
                f"$.hard_gate_results[{index}]: unsupported verifier evidence schema_version"
            )
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
        subject_identity = source_record.get("subject_identity")
        if _is_ambiguous_identity(subject_identity) or subject_identity in {None, "N/A"}:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier evidence subject_identity must be concrete"
            )

        manifest_spec = _b026_research_artifact_path(
            task_id,
            "verifier-manifests",
            source_record.get("verifier_manifest_identity"),
        )
        manifest_record: dict[str, Any] | None = None
        if manifest_spec is None:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier manifest identity must be content-addressed"
            )
        else:
            manifest_path, manifest_digest = manifest_spec
            loaded_manifest = _b026_repository_json(
                repository_root,
                manifest_path,
                canonical_commit_sha=evidence_commit_sha,
            )
            if loaded_manifest is None:
                errors.append(f"$.hard_gate_results[{index}]: canonical verifier manifest missing")
            else:
                manifest_record, observed_manifest_sha = loaded_manifest
                if observed_manifest_sha != manifest_digest:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier manifest content address mismatch"
                    )
                expected_manifest_keys = {
                    "schema_version",
                    "verifier_manifest_id",
                    "gate_id",
                    "frozen_evaluation_identity",
                }
                if set(manifest_record) != expected_manifest_keys:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier manifest fields are not canonical"
                    )
                if manifest_record.get("schema_version") != "mstr.research-verifier-manifest.v0":
                    errors.append(
                        f"$.hard_gate_results[{index}]: unsupported verifier manifest schema_version"
                    )
                if manifest_record.get("gate_id") != gate_id:
                    errors.append(f"$.hard_gate_results[{index}]: verifier manifest gate_id mismatch")
                if manifest_record.get("frozen_evaluation_identity") != evaluation_id:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier manifest evaluation identity mismatch"
                    )
                manifest_id = manifest_record.get("verifier_manifest_id")
                if _is_ambiguous_identity(manifest_id) or manifest_id in {None, "N/A"}:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier manifest id must be concrete"
                    )

        health_spec = _b026_research_artifact_path(
            task_id,
            "verifier-health",
            source_record.get("verifier_health_identity"),
        )
        if health_spec is None:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier health identity must be content-addressed"
            )
        else:
            health_path, health_digest = health_spec
            loaded_health = _b026_repository_json(
                repository_root,
                health_path,
                canonical_commit_sha=evidence_commit_sha,
            )
            if loaded_health is None:
                errors.append(f"$.hard_gate_results[{index}]: canonical verifier health missing")
            else:
                health_record, observed_health_sha = loaded_health
                if observed_health_sha != health_digest:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier health content address mismatch"
                    )
                expected_health_keys = {
                    "schema_version",
                    "verifier_health_id",
                    "verifier_manifest_identity",
                    "frozen_evaluation_identity",
                    "status",
                }
                if set(health_record) != expected_health_keys:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier health fields are not canonical"
                    )
                if health_record.get("schema_version") != "mstr.research-verifier-health.v0":
                    errors.append(
                        f"$.hard_gate_results[{index}]: unsupported verifier health schema_version"
                    )
                if health_record.get("verifier_manifest_identity") != source_record.get(
                    "verifier_manifest_identity"
                ):
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier health must bind resolved manifest"
                    )
                if health_record.get("frozen_evaluation_identity") != evaluation_id:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier health evaluation identity mismatch"
                    )
                if health_record.get("status") != "HEALTHY":
                    errors.append(f"$.hard_gate_results[{index}]: verifier health must be HEALTHY")
                health_id = health_record.get("verifier_health_id")
                if _is_ambiguous_identity(health_id) or health_id in {None, "N/A"}:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier health id must be concrete"
                    )

        subject_spec = _b026_research_artifact_path(
            task_id,
            "subject-evidence",
            source_record.get("subject_evidence_identity"),
        )
        if subject_spec is None:
            errors.append(
                f"$.hard_gate_results[{index}]: subject evidence identity must be content-addressed"
            )
        else:
            subject_path, subject_digest = subject_spec
            loaded_subject = _b026_repository_json(
                repository_root,
                subject_path,
                canonical_commit_sha=evidence_commit_sha,
            )
            if loaded_subject is None:
                errors.append(f"$.hard_gate_results[{index}]: canonical subject evidence missing")
            else:
                subject_record, observed_subject_sha = loaded_subject
                if observed_subject_sha != subject_digest:
                    errors.append(
                        f"$.hard_gate_results[{index}]: subject evidence content address mismatch"
                    )
                expected_subject_keys = {
                    "schema_version",
                    "governing_task_id",
                    "campaign_id",
                    "experiment_id",
                    "subject_identity",
                    "material_result",
                }
                if set(subject_record) != expected_subject_keys:
                    errors.append(
                        f"$.hard_gate_results[{index}]: subject evidence fields are not canonical"
                    )
                if subject_record.get("schema_version") != "mstr.research-subject-evidence.v0":
                    errors.append(
                        f"$.hard_gate_results[{index}]: unsupported subject evidence schema_version"
                    )
                for field, expected_subject_value in (
                    ("governing_task_id", task_id),
                    ("campaign_id", campaign_id),
                    ("experiment_id", experiment_id),
                    ("subject_identity", subject_identity),
                ):
                    if subject_record.get(field) != expected_subject_value:
                        errors.append(
                            f"$.hard_gate_results[{index}]: subject evidence {field} mismatch"
                        )
                material_results = instance.get("material_results")
                material_result = subject_record.get("material_result")
                matching_subject = False
                if isinstance(material_results, list) and isinstance(material_result, dict):
                    matching_subject = any(
                        isinstance(candidate, dict)
                        and candidate.get("result_id") == subject_identity
                        and candidate == material_result
                        for candidate in material_results
                    )
                if not matching_subject:
                    errors.append(
                        f"$.hard_gate_results[{index}]: subject material evidence must exactly "
                        "match one experiment material result"
                    )

        result_spec = _b026_research_artifact_path(
            task_id,
            "verifier-results",
            source_record.get("verifier_result_identity"),
        )
        verifier_result: dict[str, Any] | None = None
        if result_spec is None:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier result identity must be content-addressed"
            )
        else:
            result_path, result_digest = result_spec
            loaded_result = _b026_repository_json(
                repository_root,
                result_path,
                canonical_commit_sha=evidence_commit_sha,
            )
            if loaded_result is None:
                errors.append(f"$.hard_gate_results[{index}]: canonical verifier result missing")
            else:
                verifier_result, observed_result_sha = loaded_result
                if observed_result_sha != result_digest:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier result content address mismatch"
                    )
                expected_result_keys = {
                    "schema_version",
                    "governing_task_id",
                    "campaign_id",
                    "experiment_id",
                    "gate_id",
                    "frozen_evaluation_identity",
                    "verifier_manifest_identity",
                    "verifier_health_identity",
                    "subject_identity",
                    "subject_evidence_identity",
                    "observed_value",
                }
                if set(verifier_result) != expected_result_keys:
                    errors.append(
                        f"$.hard_gate_results[{index}]: verifier result fields are not canonical"
                    )
                if verifier_result.get("schema_version") != "mstr.research-verifier-result.v0":
                    errors.append(
                        f"$.hard_gate_results[{index}]: unsupported verifier result schema_version"
                    )
                for field, expected_result_value in (
                    ("governing_task_id", task_id),
                    ("campaign_id", campaign_id),
                    ("experiment_id", experiment_id),
                    ("gate_id", gate_id),
                    ("frozen_evaluation_identity", evaluation_id),
                    ("verifier_manifest_identity", source_record.get("verifier_manifest_identity")),
                    ("verifier_health_identity", source_record.get("verifier_health_identity")),
                    ("subject_identity", subject_identity),
                    ("subject_evidence_identity", source_record.get("subject_evidence_identity")),
                ):
                    if verifier_result.get(field) != expected_result_value:
                        errors.append(
                            f"$.hard_gate_results[{index}]: verifier result {field} mismatch"
                        )

        if evidence_record.get("source_json_pointer") != "/observed_value":
            errors.append(f"$.hard_gate_results[{index}]: unsupported source_json_pointer")
            continue
        if source_record.get("verifier_result_json_pointer") != "/observed_value":
            errors.append(f"$.hard_gate_results[{index}]: unsupported verifier_result_json_pointer")
            continue
        if verifier_result is None or "observed_value" not in verifier_result:
            errors.append(
                f"$.hard_gate_results[{index}]: verifier result lacks observed value"
            )
            continue
        observed_value = verifier_result.get("observed_value")'''
text = replace_regex(text, old_source_pattern, new_source_block, "underlying verifier evidence block")

text = replace_once(
    text,
    '''    model_execution_total = 0
    network_model_call_total = 0
''',
    '''    model_execution_total = 0
    network_model_call_total = 0
    network_byte_total = 0
''',
    "network byte total initialization",
)

resource_anchor = '''            resource_cost = result.get("resource_cost")
            if isinstance(resource_cost, dict) and (
                resource_cost.get("cost_class") == "AUTHORIZED_REMOTE_COMPUTE"
                and "RENTED_COMPUTE" not in declared_effects
            ):
                errors.append(
                    "$.governed_effects.RENTED_COMPUTE: "
                    "AUTHORIZED_REMOTE_COMPUTE requires explicit true declaration"
                )
'''
resource_replacement = resource_anchor + '''            if isinstance(resource_cost, dict):
                network_bytes = resource_cost.get("network_bytes_or_na")
                if isinstance(network_bytes, int) and not isinstance(network_bytes, bool):
                    network_byte_total += network_bytes
                    if network_bytes > 0 and "NETWORK_MODEL_OR_TEACHER_CALL" not in declared_effects:
                        errors.append(
                            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: positive network "
                            "byte evidence requires explicit true declaration"
                        )
'''
text = replace_once(text, resource_anchor, resource_replacement, "positive network byte effect")
text = replace_once(
    text,
    '''    if "NETWORK_MODEL_OR_TEACHER_CALL" in declared_effects and network_model_call_total <= 0:
        errors.append(
            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration "
            "requires positive call evidence"
        )
''',
    '''    if (
        "NETWORK_MODEL_OR_TEACHER_CALL" in declared_effects
        and network_model_call_total <= 0
        and network_byte_total <= 0
    ):
        errors.append(
            "$.governed_effects.NETWORK_MODEL_OR_TEACHER_CALL: true declaration "
            "requires positive call or network-byte evidence"
        )
''',
    "network effect positive evidence",
)
py_path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------------
# Contract tests: construct a fully content-addressed verifier chain and add
# adversarial coverage for both fresh review findings.
# ---------------------------------------------------------------------------
test_path = ROOT / "tests/contract/test_research_ladder_contract.py"
tests = test_path.read_text(encoding="utf-8")
old_source_fixture = '''        source = {
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
'''
new_source_fixture = '''        material_results = record["material_results"]
        promoted_id = record["promoted_result_id_or_na"]
        assert isinstance(material_results, list)
        subject_material = next(
            result
            for result in material_results
            if isinstance(result, dict) and result.get("result_id") == promoted_id
        )
        subject_identity = str(promoted_id)
        subject_evidence_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "subject-evidence",
            {
                "schema_version": "mstr.research-subject-evidence.v0",
                "governing_task_id": task_id,
                "campaign_id": campaign_id,
                "experiment_id": experiment_id,
                "subject_identity": subject_identity,
                "material_result": json.loads(json.dumps(subject_material)),
            },
        )
        verifier_manifest_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-manifests",
            {
                "schema_version": "mstr.research-verifier-manifest.v0",
                "verifier_manifest_id": f"fixture-verifier-manifest:{gate_id}",
                "gate_id": gate_id,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            },
        )
        verifier_health_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-health",
            {
                "schema_version": "mstr.research-verifier-health.v0",
                "verifier_health_id": f"fixture-verifier-health:{gate_id}",
                "verifier_manifest_identity": verifier_manifest_identity,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
                "status": "HEALTHY",
            },
        )
        verifier_result_identity = _write_content_addressed(
            root / "artifacts/results/research" / task_id / "verifier-results",
            {
                "schema_version": "mstr.research-verifier-result.v0",
                "governing_task_id": task_id,
                "campaign_id": campaign_id,
                "experiment_id": experiment_id,
                "gate_id": gate_id,
                "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
                "verifier_manifest_identity": verifier_manifest_identity,
                "verifier_health_identity": verifier_health_identity,
                "subject_identity": subject_identity,
                "subject_evidence_identity": subject_evidence_identity,
                "observed_value": observed_value,
            },
        )
        source = {
            "schema_version": "mstr.research-verifier-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "frozen_evaluation_identity": str(record["frozen_evaluation_identity"]),
            "verifier_manifest_identity": verifier_manifest_identity,
            "verifier_health_identity": verifier_health_identity,
            "subject_identity": subject_identity,
            "subject_evidence_identity": subject_evidence_identity,
            "verifier_result_identity": verifier_result_identity,
            "verifier_result_json_pointer": "/observed_value",
        }
'''
tests = replace_once(tests, old_source_fixture, new_source_fixture, "verifier fixture chain")

old_tamper = '''    source = _json(source_path)
    source["observed_value"] = False
    replacement_source = _write_content_addressed(source_path.parent, source)
    gate_evidence["source_evidence_identity"] = replacement_source
'''
new_tamper = '''    source = _json(source_path)
    result_digest = str(source["verifier_result_identity"]).removeprefix("sha256:")
    result_path = (
        tmp_path / "artifacts/results/research/B027/verifier-results" / f"{result_digest}.json"
    )
    verifier_result = _json(result_path)
    verifier_result["observed_value"] = False
    source["verifier_result_identity"] = _write_content_addressed(
        result_path.parent,
        verifier_result,
    )
    replacement_source = _write_content_addressed(source_path.parent, source)
    gate_evidence["source_evidence_identity"] = replacement_source
'''
tests = replace_once(tests, old_tamper, new_tamper, "tamper underlying verifier result")

insert_before = '''def test_l4_enforces_exact_universal_laptop_envelope(tmp_path: Path) -> None:
'''
new_tests = '''def test_positive_network_bytes_require_network_effect_declaration(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="network-bytes-fixture")
    results = record["material_results"]
    assert isinstance(results, list) and isinstance(results[0], dict)
    resource_cost = results[0]["resource_cost"]
    assert isinstance(resource_cost, dict)
    resource_cost["network_bytes_or_na"] = 1
    results[0]["network_model_or_teacher_call_count_or_na"] = 0
    _prepare_policy_and_gate_evidence(tmp_path, record)

    with pytest.raises(ValueError, match="positive network byte evidence"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_verifier_evidence_rejects_unresolvable_underlying_result(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="verifier-result-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
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
    source["verifier_result_identity"] = "sha256:" + "f" * 64
    gate_evidence["source_evidence_identity"] = _write_content_addressed(
        source_path.parent,
        source,
    )
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path,
        "point verifier evidence at missing underlying result",
    )

    with pytest.raises(ValueError, match="canonical verifier result missing"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


def test_verifier_subject_evidence_must_match_material_result(tmp_path: Path) -> None:
    record = _make_level_record(0, task_id="B027", campaign_id="subject-evidence-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, record)
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
    subject_digest = str(source["subject_evidence_identity"]).removeprefix("sha256:")
    subject_path = (
        tmp_path / "artifacts/results/research/B027/subject-evidence" / f"{subject_digest}.json"
    )
    subject = _json(subject_path)
    material_result = subject["material_result"]
    assert isinstance(material_result, dict)
    material_result["decision_reason"] = "not-part-of-material-result"
    replacement_subject = _write_content_addressed(subject_path.parent, subject)
    source["subject_evidence_identity"] = replacement_subject
    result_digest = str(source["verifier_result_identity"]).removeprefix("sha256:")
    result_path = (
        tmp_path / "artifacts/results/research/B027/verifier-results" / f"{result_digest}.json"
    )
    verifier_result = _json(result_path)
    verifier_result["subject_evidence_identity"] = replacement_subject
    source["verifier_result_identity"] = _write_content_addressed(
        result_path.parent,
        verifier_result,
    )
    gate_evidence["source_evidence_identity"] = _write_content_addressed(
        source_path.parent,
        source,
    )
    gate["evidence_identity"] = _write_content_addressed(gate_path.parent, gate_evidence)
    record["canonical_evidence_commit_sha_or_na"] = _commit_all(
        tmp_path,
        "replace subject material evidence with a mismatch",
    )

    with pytest.raises(ValueError, match="subject material evidence must exactly match"):
        validate_instance("mstr-research-experiment-v2", record, repository_root=tmp_path)


'''
tests = replace_once(tests, insert_before, new_tests + insert_before, "fresh review regression tests")
test_path.write_text(tests, encoding="utf-8")


# ---------------------------------------------------------------------------
# Frozen config: make the two new fail-closed boundaries explicit.
# ---------------------------------------------------------------------------
config_path = "configs/research/mstr-research-ladder-v0.json"
config = load_json(config_path)
promotion = config["promotion_policy"]
promotion["network_resource_evidence_authority_required"] = True
promotion["verifier_underlying_artifact_resolution_required"] = True
resolution = config["canonical_resolution"]
resolution["promotion_policy_binding"] = (
    "promotion_policy_identity resolves from the strict ancestor campaign-freeze commit; "
    "gate evidence resolves from the later canonical evidence commit and derives its observed "
    "value only from a content-addressed verifier result bound to content-addressed verifier "
    "manifest, verifier-health, and subject material evidence"
)
resolution["verifier_manifest_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/verifier-manifests/{sha256}.json"
)
resolution["verifier_health_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/verifier-health/{sha256}.json"
)
resolution["subject_evidence_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/subject-evidence/{sha256}.json"
)
resolution["verifier_result_registry_template"] = (
    "artifacts/results/research/{governing_task_id}/verifier-results/{sha256}.json"
)
resolution["verifier_evidence_record_contract"] = {
    "schema_version": "mstr.research-verifier-evidence.v0",
    "required_fields": [
        "governing_task_id",
        "campaign_id",
        "experiment_id",
        "gate_id",
        "frozen_evaluation_identity",
        "verifier_manifest_identity",
        "verifier_health_identity",
        "subject_identity",
        "subject_evidence_identity",
        "verifier_result_identity",
        "verifier_result_json_pointer",
    ],
    "observed_value_is_forbidden_in_wrapper": True,
    "underlying_artifacts_must_resolve_from_canonical_evidence_commit": True,
}
resolution["verifier_manifest_record_contract"] = {
    "schema_version": "mstr.research-verifier-manifest.v0",
    "content_addressed": True,
}
resolution["verifier_health_record_contract"] = {
    "schema_version": "mstr.research-verifier-health.v0",
    "content_addressed": True,
    "required_status": "HEALTHY",
}
resolution["subject_evidence_record_contract"] = {
    "schema_version": "mstr.research-subject-evidence.v0",
    "content_addressed": True,
    "must_exactly_match_experiment_material_result": True,
}
resolution["verifier_result_record_contract"] = {
    "schema_version": "mstr.research-verifier-result.v0",
    "content_addressed": True,
    "observed_value_pointer": "/observed_value",
    "must_bind_manifest_health_and_subject": True,
}
save_json(config_path, config)


# ---------------------------------------------------------------------------
# Canonical design/evidence prose: record only the bounded repair and keep all
# execution authority explicitly absent.
# ---------------------------------------------------------------------------
data_path = ROOT / "specs/002-code-model-supremacy-foundation/data-model.md"
data = data_path.read_text(encoding="utf-8")
data = replace_once(
    data,
    "Gate evidence does not carry a self-declared observed value. It content-addresses canonical verifier evidence, binds the frozen evaluator/verifier identity, and validation derives the observed value from that underlying record. L4 additionally enforces RAM <= 8 GiB, CPU execution, context = 8192, a positive thread count, Q4 artifact size <= 3 GiB, positive model-execution evidence, and an immutable candidate/Q4 binding that ties model id/revision and source checkpoint to the resolved Q4 record.",
    "Gate evidence does not carry a self-declared observed value. It content-addresses canonical verifier evidence, and that wrapper carries no observed value of its own. Instead it content-addresses the verifier manifest, verifier-health record, subject material evidence, and verifier execution result from the canonical evidence commit. Validation verifies every digest and cross-binding, requires healthy verifier evidence, requires the subject artifact to exactly match one material result in the experiment, and reads the observed value only from the content-addressed verifier result at the frozen `/observed_value` pointer. Positive `resource_cost.network_bytes_or_na` is governed network evidence even when the model/teacher call counter is zero; it therefore requires `NETWORK_MODEL_OR_TEACHER_CALL=true` and the separately canonical authority binding required by that effect. L4 additionally enforces RAM <= 8 GiB, CPU execution, context = 8192, a positive thread count, Q4 artifact size <= 3 GiB, positive model-execution evidence, and an immutable candidate/Q4 binding that ties model id/revision and source checkpoint to the resolved Q4 record.",
    "data-model verifier evidence paragraph",
)
data_path.write_text(data, encoding="utf-8")

evidence_path = ROOT / "evidence/mstr-000b/B026-research-ladder.md"
evidence = evidence_path.read_text(encoding="utf-8")
append = '''

## Exact-head CodeRabbit review repair — network evidence and verifier derivation

Fresh independent CodeRabbit issue review comment `5514766559` reviewed exact head `d2950bb1f254beedbac64268347c735f21e500c9` against canonical base `823cd7ec3b4c537876a0795d0f0f8d4bd75acd85`, resolved tree `0817e9fc29c40557e46765b8db72d60cf74f9283`, and reported two High actionable findings:

1. positive `resource_cost.network_bytes_or_na` could be accepted with zero model/teacher call count, all governed effects false, and no authority binding;
2. `mstr.research-verifier-evidence.v0` still carried a self-authored observed value without content-addressed bindings to the verifier manifest, verifier-health record, subject material evidence, and underlying verifier execution result.

This bounded repair derives the network effect from both the call counter and positive network-byte evidence. Any positive network bytes require `NETWORK_MODEL_OR_TEACHER_CALL=true`; any true governed effect continues to require a separately canonical authority record resolved from the campaign-freeze commit. No authority artifact or task ledger state is changed.

The verifier-evidence wrapper no longer carries `observed_value`. It binds content-addressed canonical verifier-manifest, verifier-health, subject-evidence, and verifier-result records from the canonical evidence commit. Validation verifies every digest and cross-binding, requires the health record to be `HEALTHY`, requires subject material evidence to exactly equal a material result in the experiment, and computes the gate observation only from the resolved verifier result at `/observed_value`. Adversarial tests cover positive network bytes with no effect declaration, a missing underlying verifier result, and mismatched subject material evidence.

These findings are not considered resolved by this text or by a local patch. Resolution requires a successful guarded repair publication, fresh exact-head qualification, a fresh independent substantive review of the newly published head, zero unresolved actionable review findings, and the mandatory exact-head premerge gate.

The authority boundary remains unchanged: B026 grants no model execution, network model/teacher call, paid compute/API, model-weight access, dataset ingestion, training/RL, research-campaign execution, or production-release authority. B027 remains separate and B011 remains blocked on its separately required external authority.
'''
if "5514766559" in evidence:
    raise RuntimeError("review repair section already present")
evidence_path.write_text(evidence.rstrip() + append + "\n", encoding="utf-8")
