from __future__ import annotations

import re
from typing import Any

from shieldx.models.result import ValidationResult
from shieldx.validators.base import BaseValidator


class MinLengthValidator(BaseValidator):
    def __init__(self, min_length: int, name: str | None = None):
        super().__init__(name)
        self.min_length = min_length

    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="Value must be a string.",
                code="type_error",
                value=value,
            )

        if len(value) < self.min_length:
            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"Text is too short: {len(value)} < {self.min_length}",
                code="min_length",
                value=value,
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )


class MaxLengthValidator(BaseValidator):
    def __init__(self, max_length: int, truncate: bool = True, name: str | None = None):
        super().__init__(name)
        self.max_length = max_length
        self.truncate = truncate

    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="Value must be a string.",
                code="type_error",
                value=value,
            )

        if len(value) > self.max_length:
            fixed_value = value[: self.max_length] if self.truncate else None
            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"Text is too long: {len(value)} > {self.max_length}",
                code="max_length",
                value=value,
                fixed_value=fixed_value,
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )


class BlockedWordsValidator(BaseValidator):
    def __init__(self, blocked_words: list[str], mask: str = "[redacted]", name: str | None = None):
        super().__init__(name)
        self.blocked_words = [w for w in blocked_words if w]
        self.mask = mask

    def validate(self, value: Any) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="Value must be a string.",
                code="type_error",
                value=value,
            )

        if not self.blocked_words:
            return ValidationResult(
                passed=True,
                validator=self.name,
                value=value,
            )

        pattern = re.compile("|".join(re.escape(word) for word in self.blocked_words), re.IGNORECASE)
        found = pattern.findall(value)

        if found:
            cleaned = pattern.sub(self.mask, value)
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="Blocked words detected.",
                code="blocked_words",
                value=value,
                fixed_value=cleaned,
                metadata={"found": list(dict.fromkeys(found))},
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )