from __future__ import annotations

import json
from typing import Any

from shieldx.models.result import ValidationResult
from shieldx.validators.base import BaseValidator


class ValidJSONValidator(BaseValidator):
    def validate(self, value: Any) -> ValidationResult:
        if isinstance(value, (dict, list)):
            return ValidationResult(
                passed=True,
                validator=self.name,
                value=value,
            )

        if not isinstance(value, str):
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="Value must be a JSON string, dict, or list.",
                code="type_error",
                value=value,
            )

        try:
            parsed = json.loads(value)
            return ValidationResult(
                passed=True,
                validator=self.name,
                value=parsed,
            )
        except json.JSONDecodeError as exc:
            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"Invalid JSON: {exc}",
                code="invalid_json",
                value=value,
            )


class RequiredKeysValidator(BaseValidator):
    def __init__(self, required_keys: list[str], name: str | None = None):
        super().__init__(name)
        self.required_keys = required_keys

    def validate(self, value: Any) -> ValidationResult:
        data = value

        if isinstance(value, str):
            try:
                data = json.loads(value)
            except json.JSONDecodeError as exc:
                return ValidationResult(
                    passed=False,
                    validator=self.name,
                    message=f"Invalid JSON: {exc}",
                    code="invalid_json",
                    value=value,
                )

        if not isinstance(data, dict):
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="JSON root must be an object.",
                code="json_not_object",
                value=value,
            )

        missing = [key for key in self.required_keys if key not in data]
        if missing:
            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"Missing required keys: {missing}",
                code="missing_keys",
                value=data,
                metadata={"missing": missing},
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=data,
        )