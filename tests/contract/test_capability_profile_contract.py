from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mstr_qualify.schemas import validate_instance

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests" / "fixtures" / "schemas" / "valid" / "mstr-capability-profile-v0.json"
INVALID = ROOT / "tests" / "fixtures" / "schemas" / "invalid" / "mstr-capability-profile-v0.json"

def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data

def test_valid_capability_profile_passes() -> None:
    validate_instance("mstr-capability-profile-v0", _load(VALID))

def test_vendor_claim_only_evidence_fails_closed() -> None:
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-capability-profile-v0", _load(INVALID))

def test_measured_capability_requires_evidence() -> None:
    profile = copy.deepcopy(_load(VALID))
    profile["shell_reliability"]["evidence_refs"] = []
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-capability-profile-v0", profile)

def test_unmeasured_capability_cannot_publish_value() -> None:
    profile = copy.deepcopy(_load(VALID))
    profile["fim_strength"]["value"] = 0.5
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-capability-profile-v0", profile)

def test_reliability_ratio_is_bounded() -> None:
    profile = copy.deepcopy(_load(VALID))
    profile["tool_call_reliability"]["value"] = 1.01
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-capability-profile-v0", profile)

def test_context_budget_must_be_positive_when_measured() -> None:
    profile = copy.deepcopy(_load(VALID))
    profile["reliable_context_budget"]["value"] = 0
    with pytest.raises(ValueError, match="validation failed"):
        validate_instance("mstr-capability-profile-v0", profile)
