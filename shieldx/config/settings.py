from dataclasses import dataclass

from shieldx.config.defaults import DEFAULT_AUTO_FIX, DEFAULT_MAX_RETRIES, DEFAULT_STOP_ON_FAIL


@dataclass
class Settings:
    auto_fix: bool = DEFAULT_AUTO_FIX
    max_retries: int = DEFAULT_MAX_RETRIES
    stop_on_fail: bool = DEFAULT_STOP_ON_FAIL