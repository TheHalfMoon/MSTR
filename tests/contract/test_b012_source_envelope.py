from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLAB = ROOT / "colab"
if str(COLAB) not in sys.path:
    sys.path.insert(0, str(COLAB))

from mstr_b012_source import _candidate_envelope  # noqa: E402


def test_candidate_envelope_is_read_from_bound_b010_manifest() -> None:
    mellum = _candidate_envelope(ROOT, "mellum-4b")
    qwen = _candidate_envelope(ROOT, "qwen3.5-0.8b-control")

    assert mellum["candidate_id"] == "mellum-4b"
    assert mellum["upstream_id"] == "JetBrains/Mellum-4b-base"
    assert mellum["exact_revision"] == "83cce2605fbdf6a3868627e9b0a5924e0072b94d"
    assert mellum["expected_required_download_bytes"] == 8048099065

    assert qwen["candidate_id"] == "qwen3.5-0.8b-control"
    assert qwen["upstream_id"] == "Qwen/Qwen3.5-0.8B-Base"
    assert qwen["exact_revision"] == "dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68"
    assert qwen["expected_required_download_bytes"] == 1769897109
