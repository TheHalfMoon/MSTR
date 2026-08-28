from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from mstr_qualify.software_evolution import (
    SoftwareEvolutionProjectionError,
    canonical_projection_json,
    project_software_evolution,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "software_evolution"


def _record(name: str) -> dict[str, Any]:
    decoded = json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))
    assert isinstance(decoded, dict)
    return decoded


def _visible_event_ids(projection: dict[str, Any]) -> list[str]:
    model_input = projection["model_input"]
    assert isinstance(model_input, dict)
    events = model_input["visible_events"]
    assert isinstance(events, list)
    return [str(event["event_id"]) for event in events]


@pytest.mark.parametrize(
    ("fixture", "kind", "target_event_id", "current_revision"),
    [
        ("b017-localization.json", "LOCALIZATION", "evt-change-1", "fixture-r0"),
        ("b017-edit.json", "EDIT", "evt-change-2", "fixture-r1"),
        ("b017-review-repair.json", "REVIEW_REPAIR", "evt-recovery-1", "fixture-r1"),
    ],
)
def test_fixture_projections_are_deterministic_and_future_hidden(
    fixture: str, kind: str, target_event_id: str, current_revision: str
) -> None:
    record = _record(fixture)
    first = project_software_evolution(record, kind=kind)  # type: ignore[arg-type]
    second = project_software_evolution(copy.deepcopy(record), kind=kind)  # type: ignore[arg-type]

    assert first == second
    assert canonical_projection_json(first) == canonical_projection_json(second)
    assert first["projection_version"] == "mstr.software-evolution-projection.v0"
    assert first["projection_kind"] == kind
    assert first["audit"]["target_event_id"] == target_event_id
    assert first["audit"]["future_history_hidden"] is True
    assert first["model_input"]["current_revision"] == current_revision

    model_input_json = json.dumps(first["model_input"], sort_keys=True)
    for excluded_event_id in first["audit"]["excluded_future_event_ids"]:
        assert excluded_event_id not in model_input_json
    assert (
        record["final_revision"] not in model_input_json
        or current_revision == record["final_revision"]
    )


def test_localization_projection_has_no_prior_events_and_labels_change_identity() -> None:
    projection = project_software_evolution(_record("b017-localization.json"), kind="LOCALIZATION")

    assert _visible_event_ids(projection) == []
    assert projection["supervision_target"] == {
        "event_id": "evt-change-1",
        "event_kind": "CHANGE",
        "change_artifact_identity": "sha256:fixture-change-r0-r1",
    }


def test_edit_projection_orders_visible_history_by_sequence() -> None:
    record = _record("b017-edit.json")
    projection = project_software_evolution(record, kind="EDIT")

    assert _visible_event_ids(projection) == [
        "evt-change-1",
        "evt-test-1",
        "evt-review-1",
        "evt-recovery-1",
    ]
    assert projection["supervision_target"] == {
        "event_id": "evt-change-2",
        "event_kind": "CHANGE",
        "change_artifact_identity": "sha256:fixture-change-r1-r2",
        "before_revision": "fixture-r1",
        "after_revision": "fixture-r2",
    }

    for collection in ("change_events", "test_ci_events", "review_events", "recovery_events"):
        record[collection] = list(reversed(record[collection]))
    reordered = project_software_evolution(record, kind="EDIT")
    assert canonical_projection_json(projection) == canonical_projection_json(reordered)


def test_review_repair_projection_requires_visible_review_trigger() -> None:
    projection = project_software_evolution(
        _record("b017-review-repair.json"), kind="REVIEW_REPAIR"
    )

    assert _visible_event_ids(projection) == ["evt-change-1", "evt-test-1", "evt-review-1"]
    assert projection["supervision_target"] == {
        "event_id": "evt-recovery-1",
        "event_kind": "RECOVERY",
        "trigger_event_id": "evt-review-1",
        "action": "REPAIR",
        "resulting_revision": "fixture-r2",
    }


def test_rejects_duplicate_event_identity_across_collections() -> None:
    record = _record("b017-edit.json")
    record["review_events"][0]["event_id"] = "evt-test-1"

    with pytest.raises(SoftwareEvolutionProjectionError, match="duplicate event_id"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_duplicate_sequence_across_collections() -> None:
    record = _record("b017-edit.json")
    record["review_events"][0]["sequence"] = 20

    with pytest.raises(SoftwareEvolutionProjectionError, match="duplicate event sequence"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_non_linear_change_lineage() -> None:
    record = _record("b017-edit.json")
    record["change_events"][1]["before_revision"] = "fixture-r0"

    with pytest.raises(SoftwareEvolutionProjectionError, match="does not extend current revision"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_stale_test_revision() -> None:
    record = _record("b017-edit.json")
    record["test_ci_events"][0]["revision"] = "fixture-r0"

    with pytest.raises(
        SoftwareEvolutionProjectionError, match="does not reference current revision"
    ):
        project_software_evolution(record, kind="EDIT")


def test_rejects_non_terminal_final_revision() -> None:
    record = _record("b017-edit.json")
    record["final_revision"] = "fixture-r1"

    with pytest.raises(SoftwareEvolutionProjectionError, match="terminal fixture revision"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_target_that_is_not_first_event_after_cutoff() -> None:
    record = _record("b017-edit.json")
    record["visible_context_manifest"]["cutoff_sequence"] = 25
    record["future_history_boundary"]["cutoff_sequence"] = 25
    record["visible_context_manifest"]["visible_event_ids"] = ["evt-change-1", "evt-test-1"]
    record["visible_context_manifest"]["excluded_future_event_ids"] = [
        "evt-review-1",
        "evt-recovery-1",
        "evt-change-2",
        "evt-test-2",
    ]

    with pytest.raises(SoftwareEvolutionProjectionError, match="first chronological event"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_visible_event_set_mismatch() -> None:
    record = _record("b017-edit.json")
    record["visible_context_manifest"]["visible_event_ids"].remove("evt-review-1")

    with pytest.raises(SoftwareEvolutionProjectionError, match="visible_event_ids"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_excluded_future_event_set_mismatch() -> None:
    record = _record("b017-edit.json")
    record["visible_context_manifest"]["excluded_future_event_ids"].remove("evt-test-2")

    with pytest.raises(SoftwareEvolutionProjectionError, match="excluded_future_event_ids"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_future_event_marked_model_visible() -> None:
    record = _record("b017-edit.json")
    record["change_events"][1]["model_visibility"] = "MODEL_VISIBLE"

    with pytest.raises(
        SoftwareEvolutionProjectionError, match="target event must remain future-hidden"
    ):
        project_software_evolution(record, kind="EDIT")


def test_rejects_future_patch_artifact_in_visible_context() -> None:
    record = _record("b017-edit.json")
    record["visible_context_manifest"]["visible_artifact_ids"].append("sha256:fixture-change-r1-r2")

    with pytest.raises(SoftwareEvolutionProjectionError, match="future event artifacts"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_future_test_result_artifact_in_visible_context() -> None:
    record = _record("b017-edit.json")
    record["visible_context_manifest"]["visible_artifact_ids"].append("sha256:fixture-test-r2-pass")

    with pytest.raises(SoftwareEvolutionProjectionError, match="future event artifacts"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_public_repository_input_for_fixture_only_pilot() -> None:
    record = _record("b017-edit.json")
    record["repository_identity"]["source_class"] = "PUBLIC_OPEN_SOURCE_REPOSITORY"

    with pytest.raises(SoftwareEvolutionProjectionError, match="fixture-only"):
        project_software_evolution(record, kind="EDIT")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("contamination_status", "UNRESOLVED", "CLEAR fixture contamination"),
        (
            "rights",
            {"license_or_terms_identity": "fixture", "decision": "UNRESOLVED"},
            "compatible fixture rights",
        ),
        (
            "provenance",
            {
                "source_identity": "fixture",
                "source_revision": "fixture",
                "acquisition_or_fixture_identity": "fixture",
                "lineage_status": "UNRESOLVED",
            },
            "complete fixture lineage",
        ),
    ],
)
def test_rejects_unresolved_admission_evidence(field: str, value: Any, message: str) -> None:
    record = _record("b017-edit.json")
    record[field] = value

    with pytest.raises(SoftwareEvolutionProjectionError, match=message):
        project_software_evolution(record, kind="EDIT")


def test_rejects_retrospective_projection_mode() -> None:
    record = _record("b017-edit.json")
    boundary = record["future_history_boundary"]
    boundary["projection_mode"] = "RETROSPECTIVE_REVIEW"
    boundary["retrospective_context_reason"] = "Fixture-only B017 does not consume this mode."

    with pytest.raises(SoftwareEvolutionProjectionError, match="FORWARD_STEP only"):
        project_software_evolution(record, kind="EDIT")


def test_rejects_projection_kind_target_mismatch() -> None:
    record = _record("b017-review-repair.json")

    with pytest.raises(SoftwareEvolutionProjectionError, match="EDIT requires a CHANGE"):
        project_software_evolution(record, kind="EDIT")


def test_review_repair_rejects_hidden_trigger() -> None:
    record = _record("b017-review-repair.json")
    record["review_events"][0]["model_visibility"] = "VERIFIER_ONLY"
    record["visible_context_manifest"]["visible_event_ids"].remove("evt-review-1")

    with pytest.raises(SoftwareEvolutionProjectionError, match="trigger event to be model-visible"):
        project_software_evolution(record, kind="REVIEW_REPAIR")


def test_b017_canonical_closeout_provenance_and_authority_boundary() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B017-evolution-fixture-pilot.md").read_text(
        encoding="utf-8"
    )
    assert "**State:** COMPLETE_CANONICAL" in evidence
    assert "**Implementation PR:** #73" in evidence
    assert (
        "**Final implementation head:** "
        "`6bab90d46fca0323fe9c1d66f37a69e8b13d8ae3`" in evidence
    )
    assert (
        "**Canonical implementation merge:** "
        "`79e1b5ceca4ed39e10f53b0f85f93ffb7b02208c`" in evidence
    )
    assert "run `33179382488` — SUCCESS" in evidence
    assert "run `33179494695` / job `98876712043` — SUCCESS" in evidence
    assert "run `33180496859` — SUCCESS" in evidence
    assert "run `33182524688` — SUCCESS" in evidence
    assert "MODEL_WEIGHT_ACCESS = NONE" in evidence
    assert "LARGE_DATASET_INGESTION = NONE" in evidence
    assert "WEIGHT_CHANGING_TRAINING = NONE" in evidence


def test_b017_machine_readable_entry_gate_provenance() -> None:
    evidence = (ROOT / "evidence" / "mstr-000b" / "B017-evolution-fixture-pilot.md").read_text(
        encoding="utf-8"
    )
    assert "ENTRY_GATE_TASK = B017" in evidence
    assert (
        "ENTRY_GATE_CANONICAL_MAIN = "
        "f7a386214a1346b75dd3311390aa1e19bf354bb1" in evidence
    )
    assert "ENTRY_GATE_RUN = 33174634290" in evidence
    assert "ENTRY_GATE_JOB = 98859944051" in evidence
    assert "ENTRY_GATE_ELIGIBLE = true" in evidence
    assert "ENTRY_GATE_DRIFT = clean" in evidence
