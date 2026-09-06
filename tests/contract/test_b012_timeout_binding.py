from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BINDING = ROOT / "artifacts/manifests/B012-executor-toolchain-binding.json"
MEASURE = ROOT / "colab/mstr_b012_measure.py"


def test_timeout_recovery_binding_is_exact_and_non_authorizing() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    recovery = binding["timeout_budget_recovery"]

    assert binding["b012_measurement_helper_sha256"] == hashlib.sha256(MEASURE.read_bytes()).hexdigest()
    assert recovery["prior_failed_run_id"] == 34046125440
    assert recovery["prior_failure_classification"] == "B012_EXECUTION_FAILED_CLOSED"
    assert recovery["prior_failure_reason"] == "llama-bench timed out after 900s"
    assert recovery["model_quality_verdict"] == "NONE"
    assert recovery["diagnostic_run_id"] == 34057608647
    assert recovery["diagnostic_head"] == "0ea2da5976ed95109efc49cbc632a57b55360a14"
    assert recovery["focused_tests_passed"] == 5
    assert recovery["model_access"] == "NONE"
    assert recovery["training"] is False
    assert recovery["paid_cost_usd"] == 0.0
    assert recovery["retry_authority_created"] is False
    assert recovery["shared_t031_measurement_helper_modified"] is False
