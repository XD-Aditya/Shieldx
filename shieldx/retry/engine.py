from __future__ import annotations

from shieldx.models.result import RetryRecord, ShieldResult
from shieldx.prompt.repair import build_repair_prompt
from shieldx.schema.contract import Contract


class RetryEngine:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries

    def run(
        self,
        *,
        client,
        shield,
        prompt: str,
        original_prompt: str,
        system_prompt: str | None = None,
        contract: Contract | None = None,
        **kwargs,
    ) -> ShieldResult:
        history: list[RetryRecord] = []
        current_prompt = prompt
        last_report: ShieldResult | None = None

        for attempt in range(self.max_retries + 1):
            output = client.generate(current_prompt, system_prompt=system_prompt, **kwargs)
            report = shield.validate(output)

            history.append(
                RetryRecord(
                    attempt=attempt + 1,
                    output=output,
                    passed=report.passed,
                    errors=report.error_messages(),
                )
            )

            if report.passed:
                report.retries = attempt
                report.history = history
                return report

            last_report = report
            current_prompt = build_repair_prompt(
                original_prompt=original_prompt,
                bad_output=str(output),
                errors=report.error_messages(),
                contract=contract,
            )

        assert last_report is not None
        last_report.retries = self.max_retries
        last_report.history = history
        return last_report