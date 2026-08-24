"""Fail-closed rights evaluation for primary MSTR backbone/component admission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping

from .errors import RightsEvaluationError

ComputedDecision = Literal["pass_permissive", "fail"]

_REQUIRED_RIGHTS = (
    "personal_use",
    "commercial_use",
    "modification",
    "fine_tuning",
    "quantization",
    "derivative_redistribution",
)
_REQUIRED_FALSE_GATES = (
    "account_gate_required",
    "clickthrough_gate_required",
    "end_user_separate_license_required",
)
_ALLOWED_DECLARED_DECISIONS = {"pass_permissive", "pass_conditional", "fail", "reference_only"}
_ALLOWED_ANSWERS = {"yes", "no", "unknown"}


@dataclass(frozen=True, slots=True)
class ComponentRightsResult:
    component_id: str
    eligible_for_primary: bool
    computed_decision: ComputedDecision
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PrimaryRightsResult:
    eligible_for_primary: bool
    computed_decision: ComputedDecision
    components: tuple[ComponentRightsResult, ...]
    reason_codes: tuple[str, ...]


def _reason(component_id: str, suffix: str) -> str:
    return f"{component_id}:{suffix}"


def evaluate_component_rights(
    component_id: str,
    rights: Mapping[str, Any],
) -> ComponentRightsResult:
    """Recompute primary eligibility from evidence facts instead of trusting `decision`."""

    if not component_id or component_id.strip() != component_id:
        raise RightsEvaluationError(
            "component_id must be non-empty and have no surrounding whitespace",
            code="rights.component_id",
        )

    reasons: set[str] = set()

    declared = rights.get("decision")
    if declared not in _ALLOWED_DECLARED_DECISIONS:
        reasons.add(_reason(component_id, "decision_missing_or_invalid"))
    elif declared != "pass_permissive":
        reasons.add(_reason(component_id, f"declared_{declared}"))

    license_name = rights.get("license_name")
    if not isinstance(license_name, str) or not license_name.strip():
        reasons.add(_reason(component_id, "license_name_missing"))

    terms_urls = rights.get("terms_urls")
    if (
        not isinstance(terms_urls, list)
        or not terms_urls
        or any(not isinstance(url, str) or not url.strip() for url in terms_urls)
    ):
        reasons.add(_reason(component_id, "terms_evidence_missing"))

    rationale = rights.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        reasons.add(_reason(component_id, "rationale_missing"))

    for field in _REQUIRED_RIGHTS:
        value = rights.get(field)
        if value not in _ALLOWED_ANSWERS:
            reasons.add(_reason(component_id, f"{field}_missing_or_invalid"))
        elif value == "no":
            reasons.add(_reason(component_id, f"{field}_denied"))
        elif value == "unknown":
            reasons.add(_reason(component_id, f"{field}_unknown"))

    for field in _REQUIRED_FALSE_GATES:
        value = rights.get(field)
        if not isinstance(value, bool):
            reasons.add(_reason(component_id, f"{field}_missing_or_invalid"))
        elif value:
            reasons.add(_reason(component_id, field))

    restrictions = rights.get("field_or_scale_restrictions")
    if not isinstance(restrictions, list):
        reasons.add(_reason(component_id, "field_or_scale_restrictions_missing_or_invalid"))
    elif restrictions:
        reasons.add(_reason(component_id, "field_or_scale_restriction_present"))

    eligible = not reasons
    return ComponentRightsResult(
        component_id=component_id,
        eligible_for_primary=eligible,
        computed_decision="pass_permissive" if eligible else "fail",
        reason_codes=tuple(sorted(reasons)),
    )


def evaluate_primary_rights(
    components: Mapping[str, Mapping[str, Any]],
) -> PrimaryRightsResult:
    """Fail closed if any required backbone/tokenizer/vision component is ineligible."""

    if not components:
        raise RightsEvaluationError(
            "at least one rights component is required",
            code="rights.components_empty",
        )

    results = tuple(
        evaluate_component_rights(component_id, rights)
        for component_id, rights in sorted(components.items())
    )
    reasons = tuple(sorted(reason for result in results for reason in result.reason_codes))
    eligible = all(result.eligible_for_primary for result in results)
    return PrimaryRightsResult(
        eligible_for_primary=eligible,
        computed_decision="pass_permissive" if eligible else "fail",
        components=results,
        reason_codes=reasons,
    )
