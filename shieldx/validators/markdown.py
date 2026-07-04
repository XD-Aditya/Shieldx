from __future__ import annotations

import json as _json
import re

from shieldx.models.result import ValidationResult
from shieldx.validators.base import BaseValidator


class MarkdownStripValidator(BaseValidator):
    """
    Strips markdown code blocks (```json ... ```) from text.
    Auto-repairs if markdown is found.
    """

    def validate(self, value) -> ValidationResult:
        if not isinstance(value, str):
            return ValidationResult(
                passed=True,
                validator=self.name,
                value=value,
            )

        text = value

        # Pattern for markdown code blocks: ```json ... ``` or ``` ... ```
        pattern = r"```(?:json)?\s*(.*?)```"

        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            extracted = match.group(1).strip()
            # Check if extracted content is valid JSON
            try:
                _json.loads(extracted)
                # It's valid JSON wrapped in markdown - auto-repair
                return ValidationResult(
                    passed=False,
                    validator=self.name,
                    message="Markdown code block detected and stripped",
                    code="markdown_stripped",
                    value=value,
                    resolved=True,
                    fixed_value=extracted,
                    metadata={},
                )
            except _json.JSONDecodeError:
                pass

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )