from __future__ import annotations

from shieldx.prompt.schema import build_schema_instructions
from shieldx.schema.contract import Contract


def build_prompt(user_prompt: str, contract: Contract | None = None) -> str:
    if contract is None:
        return user_prompt

    schema_text = build_schema_instructions(contract)
    return f"{user_prompt}\n\n{schema_text}".strip()