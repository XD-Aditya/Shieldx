from __future__ import annotations

from shieldx.schema.contract import Contract


def build_schema_instructions(contract: Contract) -> str:
    lines = []

    if contract.json_only:
        lines.append("Return valid JSON only.")
        lines.append("Do not include markdown, code fences, or extra explanation.")

    if contract.required_keys:
        lines.append(f"Required keys: {', '.join(contract.required_keys)}.")

    if contract.description:
        lines.append(f"Schema description: {contract.description}")

    return "\n".join(lines)