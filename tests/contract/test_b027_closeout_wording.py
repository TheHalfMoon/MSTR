import re
from pathlib import Path

_ENTITY_RE = re.compile(r"\b(?:b027|closeout|terminal|complete_canonical)\b", re.IGNORECASE)
_STATUS_RE = re.compile(
    r"\b(?:accepted|acceptance|complete_canonical|is\s+canonical|becomes\s+canonical|canonical\s+status)\b",
    re.IGNORECASE,
)


def _terminal_closeout_status_claims(text: str) -> list[str]:
    normalized = " ".join(text.split())
    clauses = [
        clause.strip()
        for clause in re.split(r"[.;](?:\s+|$)", normalized)
        if clause.strip()
    ]
    return [clause for clause in clauses if _ENTITY_RE.search(clause) and _STATUS_RE.search(clause)]


def _is_guarded_merge_conditional(claim: str) -> bool:
    lowered = claim.lower()
    return (
        "merge" in lowered
        and "guard" in lowered
        and ("only when" in lowered or "only by" in lowered)
    )


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

    claims = _terminal_closeout_status_claims(closeout)
    assert claims
    for claim in claims:
        assert _is_guarded_merge_conditional(claim), claim


def test_b027_closeout_detector_rejects_semantic_premature_acceptance_variants() -> None:
    premature_claims = [
        "B027 is accepted on canonical `main`.",
        "The terminal closeout is accepted on canonical `main`.",
        "B027 is canonical now.",
        "The closeout has canonical status now.",
        "The closeout state is COMPLETE_CANONICAL.",
    ]

    for claim in premature_claims:
        detected = _terminal_closeout_status_claims(claim)
        assert detected == [claim.removesuffix(".")]
        assert not _is_guarded_merge_conditional(detected[0])
