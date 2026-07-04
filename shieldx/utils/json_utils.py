from __future__ import annotations

import json
from typing import Any


def load_json(value: str) -> Any:
    return json.loads(value)


def dump_json(value: Any, indent: int = 2) -> str:
    return json.dumps(value, indent=indent, ensure_ascii=False, default=str)