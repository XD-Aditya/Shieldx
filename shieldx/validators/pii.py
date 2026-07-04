from __future__ import annotations

import re
from typing import Any

from shieldx.models.result import ValidationResult
from shieldx.validators.base import BaseValidator


class PIIRedactionValidator(BaseValidator):
    EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b")
    CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")

    def _redact_string(self, text: str) -> tuple[str, dict]:
        found = {
            "emails": self.EMAIL_RE.findall(text),
            "phones": self.PHONE_RE.findall(text),
            "cards": self.CARD_RE.findall(text),
        }

        redacted = self.EMAIL_RE.sub("[email_redacted]", text)
        redacted = self.PHONE_RE.sub("[phone_redacted]", redacted)
        redacted = self.CARD_RE.sub("[card_redacted]", redacted)

        changed = redacted != text
        metadata = {k: v for k, v in found.items() if v}
        return redacted, {"changed": changed, **metadata}

    def _walk(self, value: Any) -> tuple[Any, bool, dict]:
        if isinstance(value, str):
            redacted, metadata = self._redact_string(value)
            return redacted, metadata.get("changed", False), metadata

        if isinstance(value, list):
            changed = False
            all_meta = []
            new_list = []
            for item in value:
                new_item, item_changed, item_meta = self._walk(item)
                changed = changed or item_changed
                if item_meta:
                    all_meta.append(item_meta)
                new_list.append(new_item)
            return new_list, changed, {"items": all_meta} if all_meta else {}

        if isinstance(value, dict):
            changed = False
            all_meta = {}
            new_dict = {}
            for key, item in value.items():
                new_item, item_changed, item_meta = self._walk(item)
                changed = changed or item_changed
                if item_meta:
                    all_meta[key] = item_meta
                new_dict[key] = new_item
            return new_dict, changed, all_meta

        return value, False, {}

    def validate(self, value: Any) -> ValidationResult:
        cleaned, changed, metadata = self._walk(value)

        if changed:
            return ValidationResult(
                passed=False,
                validator=self.name,
                message="PII detected in output.",
                code="pii_detected",
                value=value,
                fixed_value=cleaned,
                metadata=metadata,
            )

        return ValidationResult(
            passed=True,
            validator=self.name,
            value=value,
        )