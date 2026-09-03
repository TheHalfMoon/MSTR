from pathlib import Path


def test_b027_closeout_evidence_uses_guarded_merge_conditional_canonicality() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B027-ladder-pilot.md"
    ).read_text(encoding="utf-8")
    normalized = " ".join(evidence.split())

    assert (
        "becomes canonical only when this exact closeout head is merged into canonical `main`"
        in normalized
    )
    assert (
        "terminal B027 closeout acceptance is recorded only by the guarded merge of this exact "
        "closeout head into canonical `main`"
        in normalized
    )
    assert "is now accepted on canonical main" not in evidence
