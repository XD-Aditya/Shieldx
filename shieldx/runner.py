from __future__ import annotations

from shieldx.prompt.template import build_prompt
from shieldx.retry.engine import RetryEngine


class ShieldRunner:
    def __init__(self, shield, client, retry_engine: RetryEngine | None = None):
        self.shield = shield
        self.client = client
        self.retry_engine = retry_engine or RetryEngine(max_retries=0)

    def run(
        self,
        *,
        prompt: str,
        system_prompt: str | None = None,
        contract=None,
        max_retries: int = 0,
        **kwargs,
    ):
        final_prompt = build_prompt(prompt, contract=contract)

        if contract is not None:
            self.shield.apply_contract(contract)

        if max_retries > 0:
            return self.retry_engine.run(
                client=self.client,
                shield=self.shield,
                prompt=final_prompt,
                original_prompt=prompt,
                system_prompt=system_prompt,
                contract=contract,
                **kwargs,
            )

        output = self.client.generate(final_prompt, system_prompt=system_prompt, **kwargs)
        return self.shield.validate(output)