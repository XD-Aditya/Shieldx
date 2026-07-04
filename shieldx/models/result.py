from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ValidationResult:
    passed: bool
    validator: str
    message: str = ""
    code: str = ""
    value: Any = None
    fixed_value: Any = None
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RetryRecord:
    attempt: int
    output: Any
    passed: bool
    errors: List[str] = field(default_factory=list)


@dataclass
class ShieldResult:
    passed: bool
    original_output: Any
    final_output: Any
    validations: List[ValidationResult] = field(default_factory=list)
    retries: int = 0
    history: List[RetryRecord] = field(default_factory=list)

    def failed_validations(self, include_resolved: bool = True) -> List[ValidationResult]:
        if include_resolved:
            return [v for v in self.validations if not v.passed]
        return [v for v in self.validations if not v.passed and not v.resolved]

    def unresolved_failures(self) -> List[ValidationResult]:
        return [v for v in self.validations if not v.passed and not v.resolved]

    def error_messages(self) -> List[str]:
        return [v.message for v in self.unresolved_failures() if v.message]

    def summary(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "retries": self.retries,
            "original_output": self.original_output,
            "final_output": self.final_output,
            "validations": [
                {
                    "validator": v.validator,
                    "passed": v.passed,
                    "resolved": v.resolved,
                    "message": v.message,
                    "code": v.code,
                    "metadata": v.metadata,
                }
                for v in self.validations
            ],
        }