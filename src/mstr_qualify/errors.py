"""Typed, deterministic errors for the MSTR qualification harness."""

from __future__ import annotations

from collections.abc import Mapping


class QualificationError(ValueError):
    """Base fail-closed error with a stable machine-readable code."""

    default_code = "qualification.error"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        if not message:
            raise ValueError("qualification error message must not be empty")
        self.message = message
        self.code = self.default_code if code is None else code
        if not self.code or any(character.isspace() for character in self.code):
            raise ValueError("qualification error code must be non-empty and contain no whitespace")
        self.details = dict(sorted((details or {}).items()))
        super().__init__(message)

    def __str__(self) -> str:
        if not self.details:
            return f"{self.code}: {self.message}"
        rendered = ", ".join(f"{key}={value!r}" for key, value in self.details.items())
        return f"{self.code}: {self.message} ({rendered})"


class ConfigurationError(QualificationError):
    default_code = "configuration.invalid"


class SchemaValidationError(QualificationError):
    default_code = "schema.invalid"


class IdentityError(QualificationError):
    default_code = "identity.invalid"


class RightsEvaluationError(QualificationError):
    default_code = "rights.ineligible"


class ArtifactIntegrityError(QualificationError):
    default_code = "artifact.integrity"


class ComparisonError(QualificationError):
    default_code = "comparison.invalid"


class PolicyViolationError(QualificationError):
    default_code = "policy.violation"
