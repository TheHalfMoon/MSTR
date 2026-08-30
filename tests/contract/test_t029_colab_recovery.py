from __future__ import annotations

import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = REPOSITORY_ROOT / "colab" / "MSTR_T029_ministral_recovery.ipynb"


def _notebook_text() -> str:
    data = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert data["nbformat"] == 4
    return "".join(
        part
        for cell in data["cells"]
        for part in cell.get("source", [])
        if isinstance(part, str)
    )


def test_t029_colab_recovery_is_pinned_to_ministral_and_canonical_inputs() -> None:
    text = _notebook_text()

    assert "CANDIDATE = 'ministral-3-3b'" in text
    assert "6f9c4b12a95b139af68670a6713616b757923735" in text
    assert "fc35562ba46fbbf8e30cac85edbb39642c37d248" in text
    assert "63c81229d0c797ea0347255f0916d0b7ed9a9514" in text
    assert "ef73095e2e9c5bdcca7147d4bdeb92a5aa9a6d0f" in text
    assert "authentication_required'] is False" in text
    assert "gated_access'] is False" in text
    assert "expected_monetary_cost'] == 'USD 0.00'" in text


def test_t029_colab_recovery_does_not_expand_to_b011_candidates() -> None:
    text = _notebook_text().lower()

    assert "mellum-4b" not in text
    assert "qwen3.5-0.8b" not in text
    assert "--candidate', candidate" in text
    assert "shutil.rmtree(workdir, ignore_errors=true)" in text
