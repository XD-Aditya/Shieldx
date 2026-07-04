from __future__ import annotations

import re

from shieldx.models.result import ValidationResult
from shieldx.validators.base import BaseValidator


class RefusalDetectorValidator(BaseValidator):
    """
    Detects when an LLM refuses to answer.
    """

    REFUSAL_PATTERNS = [
        r"i can't help",
        r"i cannot help",
        r"i'm sorry",
        r"i am sorry",
        r"cannot assist",
        r"unable to help",
        r"not able to help",
        r"cannot provide",
        r"can't provide",
        r"unable to comply",
        r"cannot comply",
        r"that's not something",
        r"that request",
        r"won't be able to",
        r"harmful",
        r"inappropriate",
        r"against my guidelines",
        r"cannot fulfill",
    ]

    def __init__(
        self,
        patterns: list[str] | None = None,
        name: str | None = None,
    ):
        super().__init__(name)
        self.patterns = patterns or self.REFUSAL_PATTERNS
        self._regex = re.compile(
            "|".join(re.escape(p) for p in self.patterns),
            re.IGNORECASE,
        )

    def validate(self, value) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                passed=True,
                validator=self.name,
                value=value,
            )

        match = self._regex.search(value)

        if match:
            return ValidationResult(
                passed=False,
                validator=self.name,
                message=f"LLM refusal detected: '{match.group()}'",
                code="llm_refusal",
                value=value,
                metadata={"refusal_text": match.group()},
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )