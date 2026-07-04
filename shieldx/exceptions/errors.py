class ShieldXError(Exception):
    """Base exception for ShieldX."""


class ValidationFailedError(ShieldXError):
    """Raised when validation fails."""


class RetryLimitReachedError(ShieldXError):
    """Raised when retry limit is reached."""


class LLMProviderError(ShieldXError):
    """Raised when an LLM provider call fails."""