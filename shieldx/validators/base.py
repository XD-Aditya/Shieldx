from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from shieldx.models.result import ValidationResult


class BaseValidator(ABC):
    def __init__(self, name: str | None = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    def validate(self, value: Any) -> ValidationResult:
        raise NotImplementedError

    def __call__(self, value: Any) -> ValidationResult:
        return self.validate(value)