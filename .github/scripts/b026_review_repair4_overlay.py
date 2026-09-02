from __future__ import annotations

from pathlib import Path

ROOT = Path.cwd()
SCHEMAS = ROOT / "src/mstr_qualify/schemas.py"
TESTS = ROOT / "tests/contract/test_research_ladder_contract.py"
CONFIG = ROOT / "configs/research/mstr-research-ladder-v0.json"
EVIDENCE = ROOT / "evidence/mstr-000b/B026-research-ladder.md"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def patch_validator() -> None:
    replace_once(
        SCHEMAS,
        '''            if criterion.get("operator") not in {"EQ", "GTE", "LTE", "NOT_APPLICABLE"}:
                errors.append("$.promotion_policy_identity: unsupported policy operator")
                continue
''',
        '''            if criterion.get("operator") not in {
                "EQ",
                "GTE",
                "LTE",
                "NOT_APPLICABLE",
                "EQ_PROMOTED_ARTIFACT",
            }:
                errors.append("$.promotion_policy_identity: unsupported policy operator")
                continue
''',
    )
    replace_once(
        SCHEMAS,
        '''        computed = _b026_compare_gate_value(
            criterion.get("operator"),
            evidence_record.get("observed_value"),
            criterion.get("expected_value"),
        )
''',
        '''        operator = criterion.get("operator")
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
                and evidence_record.get("observed_value") == promoted_artifact
                else "FAIL"
            )
        else:
            computed = _b026_compare_gate_value(
                operator,
                evidence_record.get("observed_value"),
                criterion.get("expected_value"),
            )
''',
    )
    replace_once(
        SCHEMAS,
        '''            artifact_sha = promoted_result.get("model_artifact_sha256_or_na")
            artifact_gate = gate_by_id.get("q4_artifact_identity")
            if (
                isinstance(artifact_sha, str)
                and artifact_sha != "N/A"
                and isinstance(artifact_gate, dict)
                and artifact_gate.get("evidence_identity") != f"sha256:{artifact_sha.lower()}"
            ):
                errors.append(
                    "$.hard_gate_results[q4_artifact_identity].evidence_identity: "
                    "must bind the promoted Q4 artifact SHA-256"
                )
''',
        '''            artifact_sha = promoted_result.get("model_artifact_sha256_or_na")
''',
    )


def patch_tests() -> None:
    replace_once(
        TESTS,
        '''        "criteria": [
            {"gate_id": gate_id, "operator": "EQ", "expected_value": True}
            for gate_id in _required_gate_ids(level)
        ],
''',
        '''        "criteria": [
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
''',
    )
    replace_once(
        TESTS,
        '''        evidence = {
            "schema_version": "mstr.research-gate-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "observed_value": True,
        }
''',
        '''        observed_value: object = True
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
        evidence = {
            "schema_version": "mstr.research-gate-evidence.v0",
            "governing_task_id": task_id,
            "campaign_id": campaign_id,
            "experiment_id": experiment_id,
            "gate_id": gate_id,
            "observed_value": observed_value,
        }
''',
    )
    replace_once(
        TESTS,
        '''    l0 = _make_level_record(0, task_id="B027", campaign_id="campaign-registry-fixture")
    l0_sha = _write_json_with_sha(_registry_path(tmp_path, "B027", "fixture-l0"), l0)
''',
        '''    l0 = _make_level_record(0, task_id="B027", campaign_id="campaign-registry-fixture")
    _prepare_policy_and_gate_evidence(tmp_path, l0)
    l0_sha = _write_json_with_sha(_registry_path(tmp_path, "B027", "fixture-l0"), l0)
''',
    )
    replace_once(
        TESTS,
        '''    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
''',
        '''    fixture["external_effect_authority"] = {
        "authority_id": authority_id,
        "authority_record_sha256": authority_sha,
    }
    _prepare_policy_and_gate_evidence(tmp_path, fixture)
    validate_instance("mstr-research-experiment-v2", fixture, repository_root=tmp_path)
''',
    )


def patch_contract_text() -> None:
    replace_once(
        CONFIG,
        '"operators": [\n        "EQ",\n        "GTE",\n        "LTE",\n        "NOT_APPLICABLE"\n      ],',
        '"operators": [\n        "EQ",\n        "GTE",\n        "LTE",\n        "NOT_APPLICABLE",\n        "EQ_PROMOTED_ARTIFACT"\n      ],',
    )
    text = EVIDENCE.read_text(encoding="utf-8").rstrip()
    note = (
        "\n\nThe `q4_artifact_identity` gate uses a predeclared symbolic criterion "
        "`EQ_PROMOTED_ARTIFACT`: its immutable gate-evidence record carries the observed artifact "
        "SHA-256, and validation compares that value to the selected promoted material result. "
        "This preserves content-addressed gate evidence without treating the gate-evidence identity "
        "itself as the model artifact identity.\n"
    )
    if "`EQ_PROMOTED_ARTIFACT`" not in text:
        EVIDENCE.write_text(text + note, encoding="utf-8")


def main() -> None:
    patch_validator()
    patch_tests()
    patch_contract_text()
    for path in (SCHEMAS, TESTS, CONFIG, EVIDENCE):
        path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
