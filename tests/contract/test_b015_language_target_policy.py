import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "artifacts" / "decisions" / "B015-language-target-policy.json"
EVIDENCE_PATH = ROOT / "evidence" / "mstr-000b" / "B015-language-mix.md"
DATA_CONSTITUTION_PATH = ROOT / "docs" / "data" / "MSTR_DATA_CONSTITUTION.md"


def _policy() -> dict[str, object]:
    decoded = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def test_b015_policy_identity_and_exact_entry_gate() -> None:
    policy = _policy()
    assert policy["artifact_version"] == "mstr.b015.language-target-policy.v1"
    assert policy["policy_id"] == "MSTR-LANGUAGE-TARGET-POLICY-v0"
    assert policy["task_id"] == "B015"
    assert policy["state"] == "IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT"
    assert (
        policy["canonical_main_at_entry"]
        == "205df4be5f2e25bd28b697816eac3ea6ce361aed"
    )
    entry = policy["entry_gate"]
    assert isinstance(entry, dict)
    assert entry == {
        "canonical_main": "205df4be5f2e25bd28b697816eac3ea6ce361aed",
        "drift": "clean",
        "eligible": True,
        "external_effect_class": "NO_EXTERNAL_EFFECT",
        "job_id": 98834411321,
        "run_id": 33166914253,
        "task_id": "B015",
    }


def test_b015_language_tiers_are_disjoint_and_product_bounded() -> None:
    policy = _policy()
    tiers = policy["tiers"]
    assert isinstance(tiers, dict)
    core = {item["id"] for item in tiers["core"]}
    secondary = {item["id"] for item in tiers["secondary"]}
    long_tail = set(tiers["long_tail"]["initial_targets"])
    assert core == {
        "typescript",
        "python",
        "javascript",
        "java",
        "csharp",
        "c",
        "cpp",
    }
    assert secondary == {"go", "rust", "php", "kotlin", "swift"}
    assert core.isdisjoint(secondary)
    assert core.isdisjoint(long_tail)
    assert secondary.isdisjoint(long_tail)
    assert tiers["long_tail"]["per_language_minimum_percent"] == 0
    assert "Marketing completeness is not evidence" in tiers["long_tail"][
        "admission_rule"
    ]


def test_b015_replay_floors_are_coherent_and_leave_flexible_capacity() -> None:
    policy = _policy()
    replay = policy["replay_policy"]
    aggregate = replay["aggregate_minimum_percent"]
    assert aggregate == {
        "core_programming": 55,
        "secondary_programming": 15,
        "tooling_config": 15,
    }
    assert replay["long_tail_maximum_percent"] == 15
    assert sum(aggregate.values()) == 85
    assert sum(replay["core_language_minimum_percent"].values()) == 41
    assert sum(replay["secondary_language_minimum_percent"].values()) == 12
    assert sum(replay["tooling_group_minimum_percent"].values()) == 15
    assert (
        sum(replay["core_language_minimum_percent"].values())
        <= aggregate["core_programming"]
    )
    assert (
        sum(replay["secondary_language_minimum_percent"].values())
        <= aggregate["secondary_programming"]
    )
    assert replay["denominator"] == "LANGUAGE_TOOLING_SLICE"


def test_b015_tooling_covers_cross_platform_build_config_shell_and_sql() -> None:
    policy = _policy()
    channels = policy["tooling_channels"]
    ids = {item["id"] for item in channels}
    assert {
        "shell_posix",
        "powershell",
        "sql",
        "structured_config",
        "package_build_manifests",
        "build_systems",
        "ci_workflows",
        "infra_config",
    } <= ids
    groups = {item["group"] for item in channels}
    assert {"shell", "sql", "structured_config", "build_ci", "infra_config"} <= groups


def test_b015_stage_specific_policy_does_not_steal_role_mix_authority() -> None:
    policy = _policy()
    scope = policy["scope"]
    assert scope["stage_specific_manifest_required"] is True
    assert scope["fixed_final_percentages"] is False
    rules = policy["stage_manifest_rules"]
    assert any("sum to 100 percent" in rule for rule in rules)
    assert any("Do not infer software-role" in rule for rule in rules)
    constitution = DATA_CONSTITUTION_PATH.read_text(encoding="utf-8")
    assert "REQUIRED_POLICY_TASK = B015" in constitution
    assert "FIXED_PERCENTAGES_IN_B014 = FALSE" in constitution


def test_b015_external_sources_and_non_authority_are_explicit() -> None:
    policy = _policy()
    sources = policy["decision_basis"]["external_evidence"]
    assert {source["source_id"] for source in sources} == {
        "github_octoverse_2025",
        "stackoverflow_2025_technology",
        "jetbrains_developer_ecosystem_2025",
    }
    assert all(source["observed_at"] == "2026-08-28" for source in sources)
    boundary = policy["authority_boundary"]
    assert boundary
    assert all(value is False for value in boundary.values())
    evidence = EVIDENCE_PATH.read_text(encoding="utf-8")
    assert "IMPLEMENTED_PENDING_CANONICAL_CLOSEOUT" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
