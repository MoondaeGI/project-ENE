"""Project-wide custom exceptions."""


class AppError(Exception):
    """Base exception for all application errors."""

    default_message: str = "An application error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


# ── Database ──────────────────────────────────────────────────────────────────


class DatabaseError(AppError):
    """Raised when a database operation fails."""

    default_message = "A database error occurred."


class DatabaseConnectionError(DatabaseError):
    """Raised when a database connection cannot be established."""

    default_message = "Database connection could not be established."


# ── LLM ───────────────────────────────────────────────────────────────────────


class LLMError(AppError):
    """Base exception for LLM-related errors."""

    default_message = "An LLM error occurred."


class LLMProviderNotFoundError(LLMError):
    """Raised when a requested LLM provider name is not registered."""

    default_message = "The requested LLM provider is not registered."


class LLMAllProvidersFailedError(LLMError):
    """Raised when every available provider has been tried and all failed."""

    default_message = "All LLM providers failed."


class LLMRateLimitError(LLMError):
    """Raised when the provider returns a rate-limit response."""

    default_message = "LLM provider rate limit exceeded."


class LLMContextWindowExceededError(LLMError):
    """Raised when the request exceeds the provider's context-window limit."""

    default_message = "Request exceeds the provider's context-window limit."


class LLMTimeoutError(LLMError):
    """Raised when an LLM call exceeds the configured timeout."""

    default_message = "LLM call timed out."


# ── Memory ────────────────────────────────────────────────────────────────────


class MemoryError(AppError):
    """Base exception for memory-system errors."""

    default_message = "A memory system error occurred."


class EmbeddingError(MemoryError):
    """Raised when embedding generation fails."""

    default_message = "Embedding generation failed."


# ── WebSocket ─────────────────────────────────────────────────────────────────


class WebSocketError(AppError):
    """Raised on WebSocket connection or message errors."""

    default_message = "A WebSocket error occurred."
