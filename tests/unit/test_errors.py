from __future__ import annotations

import pytest

from mstr_qualify.errors import IdentityError, QualificationError, SchemaValidationError


def test_typed_errors_remain_value_errors_for_t004_compatibility() -> None:
    assert issubclass(SchemaValidationError, QualificationError)
    assert issubclass(QualificationError, ValueError)


def test_error_string_is_deterministic_and_details_sorted() -> None:
    error = IdentityError("bad identity", details={"z": 2, "a": 1})
    assert str(error) == "identity.invalid: bad identity (a=1, z=2)"


def test_error_allows_specific_stable_code() -> None:
    error = SchemaValidationError("bad schema", code="schema.external_ref")
    assert error.code == "schema.external_ref"
    assert str(error) == "schema.external_ref: bad schema"


@pytest.mark.parametrize("code", ["", "has space", "has\ttab"])
def test_error_rejects_invalid_codes(code: str) -> None:
    with pytest.raises(ValueError, match="code"):
        QualificationError("message", code=code)


def test_error_rejects_empty_message() -> None:
    with pytest.raises(ValueError, match="message"):
        QualificationError("")
