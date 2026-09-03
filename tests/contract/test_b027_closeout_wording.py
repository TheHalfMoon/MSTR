import re
from pathlib import Path

_ENTITY_RE = re.compile(r"\b(?:b027|closeout|terminal|complete_canonical)\b", re.IGNORECASE)
_STATUS_RE = re.compile(
    r"\b(?:"
    r"accepted|acceptance|"
    r"is(?:\s+now)?\s+canonical(?:\s+now)?|"
    r"becomes?(?:\s+now)?\s+canonical(?:\s+now)?|"
    r"(?:has|holds)\s+canonical\s+status|"
    r"canonical\s+status|"
    r"(?:state|status)\s+(?:is|=)\s+`?complete_canonical`?"
    r")\b",
    re.IGNORECASE,
)
_SENTENCE_BOUNDARY_RE = re.compile(r"[.;](?:\s+|$)")
_ASSERTION_CONJUNCTION_RE = re.compile(r"(?:,\s*|\s+)(?:and|but)\s+", re.IGNORECASE)


def _terminal_closeout_status_assertions(text: str) -> list[str]:
    normalized = " ".join(text.split())
    sentences = [
        sentence.strip()
        for sentence in _SENTENCE_BOUNDARY_RE.split(normalized)
        if sentence.strip()
    ]
    assertions: list[str] = []
    for sentence in sentences:
        status_matches = list(_STATUS_RE.finditer(sentence))
        if not status_matches or not _ENTITY_RE.search(sentence):
            continue
        parts = (
            [sentence]
            if len(status_matches) == 1
            else [
                part.strip()
                for part in _ASSERTION_CONJUNCTION_RE.split(sentence)
                if part.strip()
            ]
        )
        assertions.extend(part for part in parts if _STATUS_RE.search(part))
    return assertions


def _is_guarded_expected_head_merge_conditional(assertion: str) -> bool:
    lowered = assertion.lower()
    return (
        "merge" in lowered
        and "exact closeout head" in lowered
        and "expected-head" in lowered
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
    normalized_lower = normalized.lower()

    assert (
        "b027 becomes canonical only when this exact closeout head is merged into canonical `main` "
        "through the required expected-head guard"
        in normalized_lower
    )
    assert (
        "terminal b027 closeout acceptance is recorded only when this exact closeout head is "
        "merged into canonical `main` through the required expected-head guard"
        in normalized_lower
    )

    assertions = _terminal_closeout_status_assertions(closeout)
    assert assertions
    for assertion in assertions:
        assert _is_guarded_expected_head_merge_conditional(assertion), assertion


def test_b027_closeout_detector_rejects_semantic_premature_acceptance_variants() -> None:
    premature_assertions = [
        "B027 is accepted on canonical `main`.",
        "The terminal closeout is accepted on canonical `main`.",
        "B027 is now canonical.",
        "B027 is canonical now.",
        "The closeout has canonical status now.",
        "The closeout state is COMPLETE_CANONICAL.",
    ]

    for assertion in premature_assertions:
        detected = _terminal_closeout_status_assertions(assertion)
        assert detected == [assertion.removesuffix(".")]
        assert not _is_guarded_expected_head_merge_conditional(detected[0])


def test_b027_closeout_detector_binds_guard_to_each_status_assertion() -> None:
    mixed = (
        "B027 is accepted on canonical main, and B027 becomes canonical only when this exact "
        "closeout head is merged into canonical `main` through the required expected-head guard."
    )

    assertions = _terminal_closeout_status_assertions(mixed)

    assert len(assertions) == 2
    assert assertions[0] == "B027 is accepted on canonical main"
    assert not _is_guarded_expected_head_merge_conditional(assertions[0])
    assert _is_guarded_expected_head_merge_conditional(assertions[1])


def test_b027_closeout_detector_rejects_generic_guarded_merge_without_exact_head() -> None:
    generic = (
        "B027 becomes canonical only when it is merged into canonical `main` through the required "
        "expected-head guard."
    )

    detected = _terminal_closeout_status_assertions(generic)

    assert detected == [generic.removesuffix(".")]
    assert not _is_guarded_expected_head_merge_conditional(detected[0])


def test_b027_closeout_detector_accepts_independently_guarded_status_assertions() -> None:
    guarded_assertions = [
        (
            "B027 becomes canonical only when this exact closeout head is merged into canonical "
            "`main` through the required expected-head guard."
        ),
        (
            "Terminal B027 closeout acceptance is recorded only when this exact closeout head is "
            "merged into canonical `main` through the required expected-head guard."
        ),
    ]

    for assertion in guarded_assertions:
        detected = _terminal_closeout_status_assertions(assertion)
        assert detected == [assertion.removesuffix(".")]
        assert _is_guarded_expected_head_merge_conditional(detected[0])
