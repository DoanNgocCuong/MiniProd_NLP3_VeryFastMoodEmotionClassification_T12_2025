class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


class GroqError(RuntimeError):
    """Raised when Groq client operations fail."""

