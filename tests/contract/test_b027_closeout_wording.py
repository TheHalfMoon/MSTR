import re
from pathlib import Path


def test_b027_closeout_evidence_uses_guarded_merge_conditional_canonicality() -> None:
    evidence = (
        Path(__file__).resolve().parents[2]
        / "evidence"
        / "mstr-000b"
        / "B027-ladder-pilot.md"
    ).read_text(encoding="utf-8")
    closeout = evidence.split("## Canonical Implementation Closeout", maxsplit=1)[1]
    normalized = " ".join(closeout.split())

    assert (
        "becomes canonical only when this exact closeout head is merged into canonical `main`"
        in normalized
    )
    assert (
        "terminal B027 closeout acceptance is recorded only by the guarded merge of this exact "
        "closeout head into canonical `main`"
        in normalized
    )

    clauses = [
        clause.strip()
        for clause in re.split(r"[.;](?:\s+|$)", normalized)
        if clause.strip()
    ]
    terminal_canonicality_claims = [
        clause
        for clause in clauses
        if re.search(r"\b(?:b027|closeout|terminal|complete_canonical)\b", clause, re.IGNORECASE)
        and re.search(r"\b(?:accepted|acceptance|canonical)\b", clause, re.IGNORECASE)
    ]

    assert terminal_canonicality_claims
    for claim in terminal_canonicality_claims:
        lowered = claim.lower()
        assert "merge" in lowered, claim
        assert "guard" in lowered, claim
        assert "only when" in lowered or "only by" in lowered, claim
