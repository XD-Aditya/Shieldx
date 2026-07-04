from __future__ import annotations

from typing import Any

from shieldx.models.result import ShieldResult, ValidationResult
from shieldx.retry.engine import RetryEngine


class Shield:
    def __init__(
        self,
        name: str = "default-shield",
        auto_fix: bool = True,
        stop_on_fail: bool = False,
    ):
        self.name = name
        self.auto_fix = auto_fix
        self.stop_on_fail = stop_on_fail
        self.validators = []

    def use(self, validator):
        self.validators.append(validator)
        return self

    def extend(self, validators: list):
        self.validators.extend(validators)
        return self

    def apply_contract(self, contract):
        self.extend(contract.build_validators())
        return self

    def validate(self, output: Any) -> ShieldResult:
        current_value = output
        validations: list[ValidationResult] = []

        for validator in self.validators:
            result = validator.validate(current_value)
            validations.append(result)

            if result.passed:
                if result.value is not None:
                    current_value = result.value
                continue

            if self.auto_fix and result.fixed_value is not None:
                result.resolved = True
                current_value = result.fixed_value
                continue

            if self.stop_on_fail:
                break

        passed = all(v.passed or v.resolved for v in validations)

        return ShieldResult(
            passed=passed,
            original_output=output,
            final_output=current_value,
            validations=validations,
        )

    def generate(
        self,
        *,
        client,
        prompt: str,
        system_prompt: str | None = None,
        contract=None,
        max_retries: int = 0,
        **kwargs,
    ):
        from shieldx.runner import ShieldRunner

        runner = ShieldRunner(
            shield=self,
            client=client,
            retry_engine=RetryEngine(max_retries=max_retries),
        )
        return runner.run(
            prompt=prompt,
            system_prompt=system_prompt,
            contract=contract,
            max_retries=max_retries,
            **kwargs,
        )