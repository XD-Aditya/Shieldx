from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Contract:
    name: str = "default"
    description: str = ""
    required_keys: list[str] = field(default_factory=list)
    json_only: bool = True

    def build_validators(self):
        from shieldx.validators.json import RequiredKeysValidator, ValidJSONValidator

        validators = []
        if self.json_only:
            validators.append(ValidJSONValidator())
        if self.required_keys:
            validators.append(RequiredKeysValidator(self.required_keys))
        return validators