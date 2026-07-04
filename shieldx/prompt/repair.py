from __future__ import annotations

from shieldx.prompt.schema import build_schema_instructions
from shieldx.schema.contract import Contract


def build_repair_prompt(
    original_prompt: str,
    bad_output: str,
    errors: list[str],
    contract: Contract | None = None,
) -> str:
    error_block = "\n".join(f"- {error}" for error in errors) if errors else "- Unknown validation error"
    schema_block = build_schema_instructions(contract) if contract else ""

    return f"""
You previously generated an invalid response.

Original task:
{original_prompt}

Invalid output:
{bad_output}

Validation errors:
{error_block}

Fix the response and return only the corrected final output.

{schema_block}
""".strip()