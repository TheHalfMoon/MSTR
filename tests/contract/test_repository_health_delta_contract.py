from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "mstr-repository-health-delta-v0.schema.json"
DESIGN_SCHEMA_PATH = (
    ROOT
    / "specs"
    / "002-code-model-supremacy-foundation"
    / "contracts"
    / "mstr-repository-health-delta-v0.schema.json"
)
FIXTURE_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "schemas"
    / "valid"
    / "mstr-repository-health-delta-v0.json"
)

EXPECTED_PROFILES = {
    "RAW_MODEL": "mstr.harness.raw-model.v0",
    "H0": "mstr.harness.h0-neutral-minimal.v0",
    "H1": "mstr.harness.h1-native.v0",
    "H2": "mstr.harness.h2-wepld-native.v0",
}
EXPECTED_DIMENSIONS = {
    "duplication",
    "dead_unused_code",
    "complexity_growth",
    "dependency_growth",
    "architecture_violations",
    "lint_type_debt",
    "test_health",
    "unnecessary_refactors",
}


def _schema() -> dict[str, object]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _errors(value: dict[str, object]) -> list[str]:
    validator = Draft202012Validator(_schema())
    return [error.message for error in validator.iter_errors(value)]


def test_b030_runtime_and_design_contract_are_byte_identical() -> None:
    assert SCHEMA_PATH.read_bytes() == DESIGN_SCHEMA_PATH.read_bytes()


def test_b030_freezes_multi_round_raw_h0_h1_h2_attribution() -> None:
    value = _fixture()
    assert _errors(value) == []

    rounds = value["rounds"]
    assert isinstance(rounds, list)
    assert len(rounds) >= 2
    for round_record in rounds:
        assert isinstance(round_record, dict)
        profiles = round_record["profiles"]
        assert isinstance(profiles, dict)
        assert set(profiles) == set(EXPECTED_PROFILES)
        for attribution, profile_id in EXPECTED_PROFILES.items():
            profile = profiles[attribution]
            assert isinstance(profile, dict)
            assert profile["attribution"] == attribution
            assert profile["harness_profile_id"] == profile_id


def test_b030_freezes_repository_health_dimensions_without_score_collapse() -> None:
    value = _fixture()
    rounds = value["rounds"]
    assert isinstance(rounds, list)

    for round_record in rounds:
        assert isinstance(round_record, dict)
        profiles = round_record["profiles"]
        assert isinstance(profiles, dict)
        for profile in profiles.values():
            assert isinstance(profile, dict)
            scorecard = profile["scorecard"]
            assert isinstance(scorecard, dict)
            dimensions = scorecard["dimensions"]
            assert isinstance(dimensions, dict)
            assert set(dimensions) == EXPECTED_DIMENSIONS
            assert all(
                isinstance(record, dict)
                and record["normalization_rule_identity"]
                and record["evidence_identity"]
                for record in dimensions.values()
            )


def test_b030_blocks_claim_when_harness_lock_in_is_blocking() -> None:
    blocked = copy.deepcopy(_fixture())
    risk = blocked["risk_assessment"]
    assert isinstance(risk, dict)
    harness_lock_in = risk["harness_lock_in"]
    assert isinstance(harness_lock_in, dict)
    harness_lock_in["status"] = "BLOCKING"

    assert any("'BLOCKED' was expected" in message for message in _errors(blocked))


def test_b030_blocks_claim_when_debt_or_comparability_is_unresolved() -> None:
    for risk_name in ("technical_debt_accumulation", "cross_harness_comparability"):
        blocked = copy.deepcopy(_fixture())
        risk = blocked["risk_assessment"]
        assert isinstance(risk, dict)
        record = risk[risk_name]
        assert isinstance(record, dict)
        record["status"] = "UNRESOLVED"
        assert any("'BLOCKED' was expected" in message for message in _errors(blocked))


def test_b030_requires_all_four_attribution_surfaces() -> None:
    value = _fixture()
    rounds = value["rounds"]
    assert isinstance(rounds, list)
    first = rounds[0]
    assert isinstance(first, dict)
    profiles = first["profiles"]
    assert isinstance(profiles, dict)
    profiles.pop("H0")

    assert _errors(value)


def test_b030_no_verified_completion_cannot_fabricate_health_score() -> None:
    value = _fixture()
    rounds = value["rounds"]
    assert isinstance(rounds, list)
    first = rounds[0]
    assert isinstance(first, dict)
    profiles = first["profiles"]
    assert isinstance(profiles, dict)
    raw = profiles["RAW_MODEL"]
    assert isinstance(raw, dict)
    raw["evaluation_state"] = "NO_VERIFIED_COMPLETION"
    raw["result_revision"] = None

    assert any("is not of type 'null'" in message for message in _errors(value))


def test_b030_no_completion_can_be_represented_only_fail_closed() -> None:
    value = _fixture()
    rounds = value["rounds"]
    assert isinstance(rounds, list)
    final_round = rounds[-1]
    assert isinstance(final_round, dict)
    profiles = final_round["profiles"]
    assert isinstance(profiles, dict)
    raw = profiles["RAW_MODEL"]
    assert isinstance(raw, dict)
    raw["evaluation_state"] = "NO_VERIFIED_COMPLETION"
    raw["result_revision"] = None
    raw["scorecard"] = None

    risk = value["risk_assessment"]
    assert isinstance(risk, dict)
    comparability = risk["cross_harness_comparability"]
    assert isinstance(comparability, dict)
    comparability["status"] = "UNRESOLVED"
    risk["claim_decision"] = "BLOCKED"

    assert _errors(value) == []


def test_b030_clear_risks_do_not_force_claim_eligibility() -> None:
    value = _fixture()
    risk = value["risk_assessment"]
    assert isinstance(risk, dict)
    risk["claim_decision"] = "BLOCKED"

    assert _errors(value) == []


def test_b030_noncompletion_forces_comparability_to_fail_closed() -> None:
    value = _fixture()
    rounds = value["rounds"]
    assert isinstance(rounds, list)
    final_round = rounds[-1]
    assert isinstance(final_round, dict)
    profiles = final_round["profiles"]
    assert isinstance(profiles, dict)
    raw = profiles["RAW_MODEL"]
    assert isinstance(raw, dict)
    raw["evaluation_state"] = "NO_VERIFIED_COMPLETION"
    raw["result_revision"] = None
    raw["scorecard"] = None

    assert _errors(value)


def test_b030_evidence_preserves_contract_only_authority_boundary() -> None:
    evidence = (
        ROOT / "evidence" / "mstr-000b" / "B030-long-horizon-quality.md"
    ).read_text(encoding="utf-8")
    for marker in (
        "ENTRY_GATE_TASK = B030",
        "ENTRY_GATE_CANONICAL_MAIN = 2d19b6296d550b5b60c1b511d71c6ce86a38d195",
        "ENTRY_GATE_ELIGIBLE = true",
        "ENTRY_GATE_V2 = 33802497478 / SUCCESS",
        "MODEL_EXECUTION = NONE",
        "HARNESS_EXECUTION = NONE",
        "WEIGHT_CHANGING_TRAINING = NONE",
        "B030_AUTHORITY = METRIC_CONTRACT_AND_FIXTURES_ONLY",
    ):
        assert marker in evidence
