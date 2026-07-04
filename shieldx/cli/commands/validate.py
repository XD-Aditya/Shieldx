from __future__ import annotations

from pathlib import Path
from typing import Optional, List

from shieldx.shield import Shield
from shieldx.validators.json import ValidJSONValidator, RequiredKeysValidator
from shieldx.validators.pii import PIIRedactionValidator
from shieldx.validators.text import (
    MinLengthValidator,
    MaxLengthValidator,
    BlockedWordsValidator,
)
from shieldx.cli.ui import render_report, print_banner, print_error


def _read_input(text: Optional[str], file: Optional[str]) -> str:
    if text is not None:
        return text
    if file is not None:
        return Path(file).read_text(encoding="utf-8")
    raise ValueError("Provide either text or file input.")


def validate_command(
    text: Optional[str] = None,
    file: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    block_words: Optional[List[str]] = None,
    require_json: bool = False,
    required_keys: Optional[List[str]] = None,
    redact_pii: bool = False,
    stop_on_fail: bool = False,
    no_auto_fix: bool = False,
) -> int:
    try:
        value = _read_input(text, file)
    except Exception as exc:
        print_error(str(exc))
        return 1

    shield = Shield(
        name="shieldx-cli",
        auto_fix=not no_auto_fix,
        stop_on_fail=stop_on_fail,
    )

    if min_length is not None:
        shield.use(MinLengthValidator(min_length))

    if max_length is not None:
        shield.use(MaxLengthValidator(max_length))

    if block_words:
        shield.use(BlockedWordsValidator(block_words))

    if redact_pii:
        shield.use(PIIRedactionValidator())

    if require_json:
        shield.use(ValidJSONValidator())

    if required_keys:
        shield.use(RequiredKeysValidator(required_keys))

    report = shield.validate(value)

    print_banner()
    render_report(report)

    return 0 if report.passed else 1