from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIRST_FAILURE = ROOT / (
    "artifacts/results/local/T031/failures/T031-granite-4.1-3b-run-33999224131.json"
)
REPLAY_FAILURE = ROOT / (
    "artifacts/results/local/T031/failures/T031-granite-4.1-3b-run-34067212730.json"
)
EVIDENCE = ROOT / "evidence/T031-59-wheel-replay-equivalence-failure.md"

EXPECTED_T029_F16 = "b76f61cdf1a11375c734431f661fabe937b7214a54d6defda5f6683bd3473d4d"
OBSERVED_F16 = "b86ef357954d1b1e5b982cc76a830e8305cc86049ca1bc4e9fcc22c7ab91a5d7"


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_59_wheel_replay_failed_closed_on_exact_t029_f16_gate() -> None:
    failure = _read_json(REPLAY_FAILURE)

    assert failure["task_id"] == "T031"
    assert failure["candidate_id"] == "granite-4.1-3b"
    assert failure["canonical_main_at_start"] == ("610bf7dacc5ee921d99a4fa2eb9023553021e84c")
    assert failure["result_classification"] == "T031_EXECUTION_FAILED_CLOSED"
    assert failure["error_type"] == "ToolchainError"
    error = str(failure["error"])
    assert EXPECTED_T029_F16 in error
    assert OBSERVED_F16 in error
    assert failure["paid_cost_usd"] == 0.0
    assert failure["training"] is False

    replay = failure["producer_replay"]
    assert isinstance(replay, dict)
    assert replay["overlay_id"] == "T031_T029_HISTORICAL_59_WHEEL_REPLAY_2026_09_06"
    assert replay["python_version"] == "3.11.16"
    assert replay["package_count"] == 59
    assert replay["historical_transitive_identity_claim"] is False
    assert replay["equivalence_gate"] == "EXACT_T029_F16_AND_Q4_SHA256_MUST_MATCH"


def test_repaired_replay_reproduced_the_same_wrong_f16_as_first_execution() -> None:
    first = _read_json(FIRST_FAILURE)
    replay = _read_json(REPLAY_FAILURE)

    assert OBSERVED_F16 in str(first["error"])
    assert OBSERVED_F16 in str(replay["error"])
    assert EXPECTED_T029_F16 in str(first["error"])
    assert EXPECTED_T029_F16 in str(replay["error"])


def test_failure_evidence_does_not_rewrite_t029_or_claim_downstream_authority() -> None:
    text = EVIDENCE.read_text(encoding="utf-8")

    assert "T029_EXPECTED_HASH_REWRITTEN=false" in text
    assert "MODEL_QUALITY_VERDICT=NONE" in text
    assert "RUNTIME_MEASUREMENT_ACCEPTED=false" in text
    assert "TRAINING=false" in text
    assert "PAID_COST_USD=0.0" in text
    assert "T032_EXECUTION=false" in text
    assert "T033_EXECUTION=false" in text
    assert "T034_ADMISSION_DECISION=false" in text
    assert "CANDIDATE_EXPANSION=false" in text
    assert "No same-action Granite retry is authorized by this evidence." in text
